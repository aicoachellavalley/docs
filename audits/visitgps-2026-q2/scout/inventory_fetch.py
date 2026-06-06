#!/usr/bin/env python3
"""
Phase 1 INVENTORY fetcher for VGPS audit.
- Reads listing-urls.json candidates.
- Skips vgps_ids already present in inventory-progress.jsonl (resume).
- Fetches each listing with 2s delay, UA "AICV-Audit/2026Q2 (+https://aicoachellavalley.org)".
- Extracts weburl, phone, tollfree, email, catnames (metacategory + subcategories),
  schema.org @type, name, address fields.
- Excludes rentals by subcategory keywords.
- Writes progress, then final clean/excluded/anomalies JSON.
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path("/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/scout")
LISTINGS = ROOT / "listing-urls.json"
PROGRESS = ROOT / "inventory-progress.jsonl"
CLEAN = ROOT / "partner-directory-clean.json"
EXCLUDED = ROOT / "excluded-rentals.json"
ANOMALIES = ROOT / "inventory-anomalies.json"
STATE = Path("/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/STATE.md")

UA = "AICV-Audit/2026Q2 (+https://aicoachellavalley.org)"
DELAY = 2.0
TIMEOUT = 30

EXCLUDE_KEYWORDS = [
    "vacation rental", "vacation home", "vacation homes",
    "timeshare", "timeshares",
    "rv resort", "rv resorts", "rv park", "rv parks",
]

META_RE = re.compile(r"^[A-Z &]+$")
WEBURL_RE = re.compile(r'"weburl"\s*:\s*"(https?://[^"]+)"')
PHONE_RE = re.compile(r'"phone"\s*:\s*"([^"]+)"')
TOLLFREE_RE = re.compile(r'"tollfree"\s*:\s*"([^"]+)"')
EMAIL_RE = re.compile(r'"email"\s*:\s*"([^"]+@[^"]+)"')
CATNAME_RE = re.compile(r'"catname"\s*:\s*"([^"]+)"')
SUBCATNAME_RE = re.compile(r'"subcatname"\s*:\s*"([^"]+)"')
LDJSON_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL,
)


def load_progress():
    seen = set()
    records = []
    if PROGRESS.exists():
        with open(PROGRESS) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    seen.add(rec.get("vgps_id"))
                    records.append(rec)
                except json.JSONDecodeError:
                    continue
    return seen, records


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def extract_ldjson(html):
    """Find the first JSON-LD block with a useful @type (LocalBusiness, Restaurant, etc)."""
    for m in LDJSON_RE.finditer(html):
        txt = m.group(1).strip()
        try:
            obj = json.loads(txt)
        except json.JSONDecodeError:
            continue
        candidates = obj if isinstance(obj, list) else [obj]
        for c in candidates:
            if not isinstance(c, dict):
                continue
            if c.get("@type"):
                return c
    return None


def extract_record(vgps_id, slug, listing_url, html):
    weburl_m = WEBURL_RE.search(html)
    phone_m = PHONE_RE.search(html)
    tollfree_m = TOLLFREE_RE.search(html)
    email_m = EMAIL_RE.search(html)

    catnames = CATNAME_RE.findall(html)
    subcatnames = SUBCATNAME_RE.findall(html)

    # dedupe preserving order
    def dedupe(seq):
        out, s = [], set()
        for x in seq:
            if x not in s:
                s.add(x); out.append(x)
        return out

    cats = dedupe(catnames)
    subs_raw = dedupe(subcatnames)

    primary_category = None
    extra_metacategories = []
    leaf_subs = []
    for c in cats:
        if META_RE.match(c):
            if primary_category is None:
                primary_category = c
            else:
                extra_metacategories.append(c)
        else:
            # a catname that isn't uppercase — treat as a subcategory leaf
            leaf_subs.append(c)
    subcategories = dedupe(subs_raw + leaf_subs)

    ld = extract_ldjson(html) or {}
    schema_type = ld.get("@type")
    name = ld.get("name")
    addr = ld.get("address") or {}
    if isinstance(addr, list):
        addr = addr[0] if addr else {}
    if not isinstance(addr, dict):
        addr = {}

    return {
        "vgps_id": vgps_id,
        "slug": slug,
        "name": name,
        "primary_category": primary_category,
        "extra_metacategories": extra_metacategories,
        "subcategories": subcategories,
        "listing_url": listing_url,
        "weburl": weburl_m.group(1) if weburl_m else None,
        "phone": phone_m.group(1) if phone_m else None,
        "tollfree": tollfree_m.group(1) if tollfree_m else None,
        "email": email_m.group(1) if email_m else None,
        "address": addr.get("streetAddress"),
        "addressLocality": addr.get("addressLocality"),
        "addressRegion": addr.get("addressRegion"),
        "schema_type": schema_type,
    }


def is_rental(rec):
    for sc in rec.get("subcategories", []):
        lower = sc.lower()
        for kw in EXCLUDE_KEYWORDS:
            if kw in lower:
                return True, kw
    return False, None


def flag_anomaly(msg):
    with open(STATE, "a") as f:
        f.write(f"\n## Anomalies\n\n- {msg}\n")
    raise SystemExit(f"ANOMALY: {msg}")


def main():
    with open(LISTINGS) as f:
        data = json.load(f)
    candidates = data["candidates"]
    total = len(candidates)

    seen, prior_records = load_progress()
    print(f"Total candidates: {total}, already in progress: {len(seen)}", flush=True)

    anomalies = []
    fetched = 0
    non200_count = 0
    parse_fail_count = 0

    progress_fh = open(PROGRESS, "a")

    early_total_checked = 0
    early_window = 100  # check anomaly rate over first 100 fresh fetches

    for i, cand in enumerate(candidates):
        vgps_id = cand["vgps_id"]
        slug = cand["slug"]
        url = cand["listing_url"]

        if vgps_id in seen:
            continue

        fetched += 1
        try:
            status, html = fetch(url)
        except urllib.error.HTTPError as e:
            non200_count += 1
            anomalies.append({
                "vgps_id": vgps_id, "slug": slug, "url": url,
                "type": "http_error", "status": e.code, "msg": str(e)
            })
            time.sleep(DELAY)
            continue
        except Exception as e:
            anomalies.append({
                "vgps_id": vgps_id, "slug": slug, "url": url,
                "type": "fetch_exception", "msg": str(e)
            })
            time.sleep(DELAY)
            continue

        if status != 200:
            non200_count += 1
            anomalies.append({
                "vgps_id": vgps_id, "slug": slug, "url": url,
                "type": "non200", "status": status
            })
            time.sleep(DELAY)
            continue

        try:
            rec = extract_record(vgps_id, slug, url, html)
        except Exception as e:
            parse_fail_count += 1
            anomalies.append({
                "vgps_id": vgps_id, "slug": slug, "url": url,
                "type": "parse_error", "msg": str(e)
            })
            time.sleep(DELAY)
            continue

        # validate that we got *something* — weburl OR catname presence indicates
        # we found the embedded config block
        if rec["primary_category"] is None and not rec["subcategories"] and rec["weburl"] is None:
            parse_fail_count += 1
            anomalies.append({
                "vgps_id": vgps_id, "slug": slug, "url": url,
                "type": "empty_extraction",
                "msg": "no weburl/catnames found — page may be a stub"
            })
            time.sleep(DELAY)
            continue

        progress_fh.write(json.dumps(rec) + "\n")
        progress_fh.flush()
        seen.add(vgps_id)

        early_total_checked += 1

        # Anomaly gate: after first 100 fresh fetches, check rates
        if early_total_checked == early_window:
            non200_pct = non200_count / max(fetched, 1) * 100
            parse_pct = parse_fail_count / max(fetched, 1) * 100
            if non200_pct > 5:
                with open(STATE, "a") as f:
                    f.write(
                        f"\n## Anomalies\n\n"
                        f"- Inventory phase: {non200_count}/{fetched} ({non200_pct:.1f}%) "
                        f"non-200 in first window — exceeds 5% threshold.\n"
                    )
                print(f"ANOMALY: non-200 rate {non200_pct:.1f}% > 5%", file=sys.stderr)
                progress_fh.close()
                raise SystemExit(2)
            if parse_pct > 50:
                with open(STATE, "a") as f:
                    f.write(
                        f"\n## Anomalies\n\n"
                        f"- Inventory phase: {parse_fail_count}/{fetched} "
                        f"({parse_pct:.1f}%) parse failures in first window — "
                        f"embedded JSON shape may have changed.\n"
                    )
                print(f"ANOMALY: parse failure rate {parse_pct:.1f}% > 50%",
                      file=sys.stderr)
                progress_fh.close()
                raise SystemExit(2)

        if fetched % 50 == 0:
            print(f"  [{fetched}] kept={len(seen)} non200={non200_count} parse_fail={parse_fail_count}",
                  flush=True)

        time.sleep(DELAY)

    progress_fh.close()

    # Write outputs
    seen, all_records = load_progress()
    clean = []
    excluded = []
    metacat_counts = {}
    weburl_missing = 0

    for rec in all_records:
        is_r, kw = is_rental(rec)
        if is_r:
            rec_copy = dict(rec)
            rec_copy["excluded_reason"] = f"subcategory matched '{kw}'"
            excluded.append(rec_copy)
        else:
            clean.append(rec)
            if rec.get("weburl") is None:
                weburl_missing += 1
            pc = rec.get("primary_category") or "(none)"
            metacat_counts[pc] = metacat_counts.get(pc, 0) + 1

    with open(CLEAN, "w") as f:
        json.dump(clean, f, indent=2)
    with open(EXCLUDED, "w") as f:
        json.dump(excluded, f, indent=2)
    with open(ANOMALIES, "w") as f:
        json.dump(anomalies, f, indent=2)

    summary = {
        "fetched": fetched,
        "kept": len(clean),
        "excluded_at_inventory": len(excluded),
        "weburl_missing": weburl_missing,
        "clean_path": str(CLEAN),
        "excluded_path": str(EXCLUDED),
        "anomalies": [
            f"{a.get('type')} {a.get('vgps_id')} {a.get('slug')}: "
            f"{a.get('msg') or a.get('status')}"
            for a in anomalies[:10]
        ],
        "metacategory_counts": metacat_counts,
    }
    print("SUMMARY_JSON=" + json.dumps(summary))


if __name__ == "__main__":
    main()
