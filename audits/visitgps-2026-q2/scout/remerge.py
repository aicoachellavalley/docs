#!/usr/bin/env python3
"""
Recovery re-merge — 2026-06-05

Re-processes inventory-progress.jsonl (4,276 records produced by the Python
fetcher) with two corrections from Sat's 2026-06-05 decisions:

  1. Relaxed metacategory regex /^[A-Z\\s&,\\-']+$/ (allows comma, hyphen,
     apostrophe) — recovers SPAS, BEAUTY & WELLNESS (224 records),
     DOG-FRIENDLY RESOURCES (61 records), and any future labels with similar
     punctuation. Earlier regex /^[A-Z &]+$/ rejected these and left 597
     records with empty primary_category.

  2. New `public_art_excluded` category: subcategories contains 'artsGPS'
     AND weburl is empty. Segregates ~309 public-art listings (sculptures,
     murals, road signs) that VGPS exposes but aren't partner businesses.
     Same D2 principle — segregated, not discarded.

Does NOT re-fetch from VGPS. Pure recovery from existing inventory data.
"""
import json
import re
import urllib.parse
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/scout")
PROGRESS = ROOT / "inventory-progress.jsonl"

OUT_CLEAN = ROOT / "partner-directory-clean.json"
OUT_NO_WEBURL = ROOT / "inventory-no-weburl.jsonl"
OUT_PLATFORM = ROOT / "inventory-platform-excluded.jsonl"
OUT_SUBCAT = ROOT / "excluded-rentals.jsonl"
OUT_PUBLIC_ART = ROOT / "inventory-public-art-excluded.jsonl"
OUT_REPORT = ROOT / "remerge-2026-06-05-report.json"

# Sat's relaxed metacategory regex (allows comma, hyphen, apostrophe in
# addition to the previous uppercase + space + ampersand). The apostrophe
# is insurance against future labels like "KIDS' ACTIVITIES".
META_RE = re.compile(r"^[A-Z\s&,\-\']+$")

RENTAL_PLATFORM_HOSTS = [
    "airbnb.com",
    "abnb.me",
    "vrbo.com",
    "homeaway.com",
    "vacasa.com",
    "smartervacation.rentals",
    "evolve.com",
]

SUBCAT_RENTAL_KEYWORDS = [
    "vacation rental",
    "vacation home",
    "vacation homes",
    "timeshare",
    "timeshares",
    "rv resort",
    "rv resorts",
    "rv park",
    "rv parks",
]


def host_match(weburl):
    if not weburl:
        return None
    try:
        host = (urllib.parse.urlparse(weburl).hostname or "").lower()
    except Exception:
        return None
    for rh in RENTAL_PLATFORM_HOSTS:
        if host == rh or host.endswith("." + rh):
            return rh
    return None


def has_rental_subcat(subcats):
    sc_lower = [s.lower() for s in subcats]
    for kw in SUBCAT_RENTAL_KEYWORDS:
        if any(kw in s for s in sc_lower):
            return kw
    return None


def derive_primary_category(subcats):
    """Returns the first subcategory matching the relaxed METACATEGORY regex."""
    for sc in subcats:
        if META_RE.match(sc):
            return sc
    return None


def is_public_art(subcats, weburl):
    return ("artsGPS" in subcats) and not weburl


def main():
    buckets = {
        "kept_for_scoring": [],
        "no_weburl": [],
        "platform_excluded": [],
        "subcategory_excluded": [],
        "public_art_excluded": [],
    }
    raw_metacategory_counter = Counter()
    recovered = 0
    still_empty = 0
    records_in = 0
    parse_failures = 0

    with open(PROGRESS) as f:
        for line in f:
            records_in += 1
            try:
                r = json.loads(line)
            except Exception:
                parse_failures += 1
                continue

            subcats = list(r.get("subcategories") or [])
            weburl = r.get("weburl")
            old_pc = r.get("primary_category")

            # IMPORTANT: only re-derive primary_category for records where it
            # was originally empty. The v1 fetcher already pulled the
            # metacategory OUT of subcategories for records where its strict
            # regex matched, so the metacategory is no longer in subcats for
            # those. Touching them would erase correctly-set values.
            if not old_pc:
                new_pc = derive_primary_category(subcats)
                if new_pc:
                    r["primary_category"] = new_pc
                    # Remove the recovered metacategory from subcategories so
                    # the data shape matches the rest of the corpus.
                    subcats = [s for s in subcats if s != new_pc]
                    r["subcategories"] = subcats
                    recovered += 1
                else:
                    still_empty += 1

            current_pc = r.get("primary_category")
            raw_metacategory_counter[current_pc or "(empty)"] += 1

            # Order matters: public_art is most specific, check first
            if is_public_art(subcats, weburl):
                buckets["public_art_excluded"].append(r)
                continue
            host_hit = host_match(weburl)
            if host_hit:
                r["_platform_host"] = host_hit
                buckets["platform_excluded"].append(r)
                continue
            subcat_hit = has_rental_subcat(subcats)
            if subcat_hit:
                r["_subcat_rental_match"] = subcat_hit
                buckets["subcategory_excluded"].append(r)
                continue
            if not weburl:
                buckets["no_weburl"].append(r)
                continue
            buckets["kept_for_scoring"].append(r)

    # Write outputs
    OUT_CLEAN.write_text(json.dumps(buckets["kept_for_scoring"], indent=2))
    for path, recs in [
        (OUT_NO_WEBURL, buckets["no_weburl"]),
        (OUT_PLATFORM, buckets["platform_excluded"]),
        (OUT_SUBCAT, buckets["subcategory_excluded"]),
        (OUT_PUBLIC_ART, buckets["public_art_excluded"]),
    ]:
        path.write_text("\n".join(json.dumps(r) for r in recs) + ("\n" if recs else ""))

    # Sanity check
    total_out = sum(len(v) for v in buckets.values())

    # Sample still-empty records for investigation
    still_empty_samples = []
    for line in PROGRESS.read_text().splitlines():
        try:
            r = json.loads(line)
            subcats = r.get("subcategories") or []
            if not derive_primary_category(subcats):
                still_empty_samples.append({
                    "vgps_id": r.get("vgps_id"),
                    "name": r.get("name"),
                    "subcategories": subcats,
                    "weburl": r.get("weburl"),
                })
                if len(still_empty_samples) >= 20:
                    break
        except Exception:
            pass

    report = {
        "records_in": records_in,
        "records_out": total_out,
        "parse_failures": parse_failures,
        "bucket_counts": {k: len(v) for k, v in buckets.items()},
        "recovered_count": recovered,
        "still_empty_primary_category": still_empty,
        "still_empty_samples": still_empty_samples,
        "raw_metacategory_counts": dict(raw_metacategory_counter.most_common()),
        "output_files": {
            "partner-directory-clean.json": len(buckets["kept_for_scoring"]),
            "inventory-no-weburl.jsonl": len(buckets["no_weburl"]),
            "inventory-platform-excluded.jsonl": len(buckets["platform_excluded"]),
            "excluded-rentals.jsonl": len(buckets["subcategory_excluded"]),
            "inventory-public-art-excluded.jsonl": len(buckets["public_art_excluded"]),
        },
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2))

    # Console summary
    print(f"records_in:  {records_in}")
    print(f"records_out: {total_out}  (parity check: {'OK' if total_out == records_in - parse_failures else 'MISMATCH'})")
    print(f"parse_failures: {parse_failures}")
    print()
    print("Bucket counts:")
    for k, v in buckets.items():
        print(f"  {k}: {len(v)}")
    print()
    print(f"Recovered (was empty primary_category, now classified): {recovered}")
    print(f"Still empty after relaxed regex: {still_empty}")
    print()
    print("Raw metacategory counts (top 25, after re-derivation):")
    for label, n in raw_metacategory_counter.most_common(25):
        print(f"  {n:5} {label!r}")
    print()
    print(f"Report written to {OUT_REPORT.name}")


if __name__ == "__main__":
    main()
