#!/usr/bin/env python3
"""
Recalibrate the schema_present and nap_consistent dimensions across all
weburl-eligible records and recompute scores + tiers.

Background: 2026-06-05 verification spot-checks (auditor/VERIFY-FINDINGS-
2026-06-05.md) confirmed two measurement artifacts in the original chunk
scoring:

  - schema_present at 0% across 3,333 partners was implausible. Spot-check
    found 4 of 10 flagged-False records with JSON-LD using rubric-eligible
    @types. Real rate ~30-40%.
  - nap_consistent at 5% was too strict. Spot-check found 6 of 10
    flagged-False Tier B records would pass with normalized-digit + lenient
    name matching. Real rate likely 40-60%.

This script re-fetches every partner's homepage and re-derives those two
dimensions using the corrected logic from Sat's 2026-06-05 courier prompt.
The other six scored dimensions (site_loads, mobile_ready, og_metadata,
faq_present, content_fresh, citation_density) are kept as scored.

Methodology documented inline below and emitted to
auditor/RECAL-METHODOLOGY-2026-06-05.md after the run.

Implementation pattern: same fetch infrastructure as score_chunkN.py with
ThreadPoolExecutor for parallelism. ~3,100 fetches × 12 threads × ~1s
throttle = ~5-10 min wall clock.
"""
import json
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2")
CHUNKS_DIR = ROOT / "auditor" / "chunks"
CLEAN_PATH = ROOT / "scout" / "partner-directory-clean.json"
METHODOLOGY_OUT = ROOT / "auditor" / "RECAL-METHODOLOGY-2026-06-05.md"

UA = "AICV-Audit/2026Q2 (+https://aicoachellavalley.org)"
TIMEOUT = 12
THREADS = 12

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# Per-host throttle (1s minimum between hits to the same host)
host_locks = {}
host_lock_lock = threading.Lock()


def host_of(url):
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def throttled_fetch(url, max_bytes=300_000):
    """Returns (status, body, error). Throttles per host."""
    h = host_of(url)
    with host_lock_lock:
        lock = host_locks.setdefault(h, [threading.Lock(), 0.0])
    with lock[0]:
        wait = lock[1] + 1.0 - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CTX) as resp:
                body = resp.read(max_bytes)
                try:
                    text = body.decode("utf-8", errors="replace")
                except Exception:
                    text = body.decode("latin-1", errors="replace")
                return resp.status, text, None
        except urllib.error.HTTPError as e:
            return e.code, "", f"HTTPError {e.code}"
        except Exception as e:
            return None, "", f"{type(e).__name__}: {e}"
        finally:
            lock[1] = time.monotonic()


# =========================================================
# Schema recalibration
# =========================================================

ACCEPTED_LD_TYPES = {
    "LocalBusiness", "Hotel", "Restaurant", "TouristAttraction",
    "Organization", "WebSite", "Place", "LodgingBusiness",
    "FoodEstablishment", "EntertainmentBusiness", "RealEstateAgent",
    "Event", "Product", "Service",
}


def collect_ld_types(html):
    """Walk every JSON-LD block (including @graph) and collect @type values."""
    types = set()
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            t = node.get("@type")
            if t:
                if isinstance(t, list):
                    for x in t:
                        types.add(str(x))
                else:
                    types.add(str(t))
            if "@graph" in node:
                walk(node["@graph"])

    for blk in blocks:
        s = blk.strip()
        # Try strict parse first
        try:
            walk(json.loads(s))
            continue
        except Exception:
            pass
        # Try cleaned parse
        try:
            walk(json.loads(s.replace("\n", " ")))
        except Exception:
            # Unparseable — fall back to regex extraction of @type strings
            for m in re.finditer(r'"@type"\s*:\s*"([^"]+)"', s):
                types.add(m.group(1))
            for m in re.finditer(r'"@type"\s*:\s*\[([^\]]+)\]', s):
                for inner in re.finditer(r'"([^"]+)"', m.group(1)):
                    types.add(inner.group(1))
    return types


def derive_schema_present(html):
    types = collect_ld_types(html)
    matched = types & ACCEPTED_LD_TYPES
    return len(matched) > 0, sorted(types), sorted(matched)


# =========================================================
# NAP recalibration
# =========================================================


def normalize_digits(s):
    return re.sub(r"\D", "", s or "")


def check_phone(html_lower_no_punct, vgps_phone):
    digits = normalize_digits(vgps_phone)
    if not digits:
        return False
    # Take last 10 digits (the US local + area code)
    target = digits[-10:]
    if len(target) < 10:
        return False
    # Look for the digit sequence anywhere in the HTML's digit stream
    # We pre-stripped non-digits in html_digits
    return target in html_lower_no_punct


def check_city(html_lower, vgps_city):
    if not vgps_city:
        return False
    return vgps_city.lower() in html_lower


def domain_root(weburl):
    h = host_of(weburl)
    # Strip www. and TLD
    if h.startswith("www."):
        h = h[4:]
    parts = h.split(".")
    return parts[0] if parts else ""


WORD_SPLIT = re.compile(r"[^a-z0-9]+")


def check_name(html_lower, vgps_name, weburl):
    """Three-rule name match per Sat's spec:
       (a) full VGPS name substring in HTML, OR
       (b) first 2-3 significant words of VGPS name all present in HTML, OR
       (c) domain root (≥4 chars) appears as substring in normalized VGPS name
    """
    name_lower = (vgps_name or "").lower().strip()
    if not name_lower:
        return False, ""
    # (a)
    if name_lower in html_lower:
        return True, "full-substring"
    # (b)
    tokens = [t for t in WORD_SPLIT.split(name_lower) if len(t) > 2]
    sig = tokens[:3]
    if sig and all(t in html_lower for t in sig):
        return True, f"first-tokens:{','.join(sig)}"
    # (c)
    root = domain_root(weburl)
    if len(root) >= 4:
        normalized = re.sub(r"[^a-z0-9]", "", name_lower)
        if root in normalized:
            return True, f"domain-root:{root}"
    return False, ""


def derive_nap(html, vgps_name, vgps_phone, vgps_city, weburl):
    html_lower = html.lower()
    html_digits = re.sub(r"\D", "", html)
    name_ok, name_evidence = check_name(html_lower, vgps_name, weburl)
    phone_ok = check_phone(html_digits, vgps_phone)
    city_ok = check_city(html_lower, vgps_city)
    return (name_ok and phone_ok and city_ok), {
        "name": name_ok,
        "name_evidence": name_evidence,
        "phone": phone_ok,
        "city": city_ok,
    }


# =========================================================
# Tier recomputation
# =========================================================

SCORED_DIMS = [
    "site_loads",
    "nap_consistent",
    "mobile_ready",
    "schema_present",
    "og_metadata",
    "faq_present",
    "content_fresh",
    "citation_density",
]


def compute_score(checks):
    return sum(1 for d in SCORED_DIMS if checks.get(d))


def compute_tier(score):
    if score >= 7:
        return "A"
    if score >= 4:
        return "B"
    if score >= 1:
        return "C"
    return "D"


# =========================================================
# Main
# =========================================================


def process_record(rec, vgps_lookup):
    """Re-fetch homepage; re-derive schema and NAP; recompute score+tier."""
    weburl = rec.get("weburl")
    vgps_id = rec.get("vgps_id")
    if not weburl:
        return rec  # shouldn't happen — Tier Z is handled separately

    inv = vgps_lookup.get(vgps_id) or {}
    vgps_name = rec.get("name") or inv.get("name") or ""
    vgps_phone = inv.get("phone") or ""
    vgps_city = inv.get("addressLocality") or ""

    status, html, err = throttled_fetch(weburl)
    checks = dict(rec.get("checks") or {})
    notes = checks.get("notes") or ""

    if err or not html:
        # Fetch failed during recalibration. Preserve original values.
        checks["_recal_status"] = "fetch_failed"
        checks["_recal_error"] = err or "empty body"
    else:
        schema_pass, all_types, matched = derive_schema_present(html)
        nap_pass, nap_evidence = derive_nap(html, vgps_name, vgps_phone, vgps_city, weburl)

        # Update only the two dimensions; preserve others
        checks["schema_present"] = schema_pass
        checks["nap_consistent"] = nap_pass

        # Diagnostic provenance
        checks["_recal_status"] = "ok"
        checks["_recal_schema_types_found"] = all_types[:30]
        checks["_recal_schema_matched"] = matched
        checks["_recal_nap_evidence"] = nap_evidence

    # Recompute score + tier from the (possibly updated) checks
    new_score = compute_score(checks)
    new_tier = compute_tier(new_score)

    rec["checks"] = checks
    rec["score"] = new_score
    rec["tier"] = new_tier
    return rec


def main():
    # Load inventory lookup (phone, city)
    inventory = json.loads(CLEAN_PATH.read_text())
    vgps_lookup = {r["vgps_id"]: r for r in inventory}

    chunk_files = sorted(CHUNKS_DIR.glob("chunk-*.jsonl"))
    print(f"Recalibrating {len(chunk_files)} chunks across ~{sum(1 for _ in inventory)} weburl-eligible records")

    # Pre-recal tier counts (from existing chunks)
    pre_tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    pre_schema_pass = 0
    pre_nap_pass = 0
    n = 0
    for cf in chunk_files:
        for line in cf.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            t = r.get("tier")
            if t in pre_tier_counts:
                pre_tier_counts[t] += 1
            checks = r.get("checks") or {}
            if checks.get("schema_present"):
                pre_schema_pass += 1
            if checks.get("nap_consistent"):
                pre_nap_pass += 1
            n += 1

    print(f"\nPRE-RECAL state (across chunks 0-13):")
    print(f"  total: {n}")
    print(f"  tier A: {pre_tier_counts['A']}")
    print(f"  tier B: {pre_tier_counts['B']}")
    print(f"  tier C: {pre_tier_counts['C']}")
    print(f"  tier D: {pre_tier_counts['D']}")
    print(f"  schema_present pass: {pre_schema_pass} ({100*pre_schema_pass/n:.1f}%)")
    print(f"  nap_consistent pass: {pre_nap_pass} ({100*pre_nap_pass/n:.1f}%)")

    # Recalibrate
    post_records_by_chunk = {}
    processed = 0
    fetch_failed = 0
    start_t = time.monotonic()

    for cf in chunk_files:
        records = []
        for line in cf.read_text().splitlines():
            if line.strip():
                records.append(json.loads(line))
        post = [None] * len(records)
        with ThreadPoolExecutor(max_workers=THREADS) as ex:
            futures = {ex.submit(process_record, r, vgps_lookup): i for i, r in enumerate(records)}
            for fut in as_completed(futures):
                i = futures[fut]
                try:
                    post[i] = fut.result()
                except Exception as e:
                    # Preserve original on hard failure
                    post[i] = records[i]
                    post[i].setdefault("checks", {})["_recal_status"] = f"exception: {e}"
                processed += 1
                if processed % 200 == 0:
                    elapsed = time.monotonic() - start_t
                    rate = processed / elapsed if elapsed else 0
                    eta = (n - processed) / rate if rate else 0
                    print(f"  ...{processed}/{n} ({rate:.1f}/s, ETA {eta:.0f}s)")
        # Count fetch failures within this chunk
        for r in post:
            if (r.get("checks") or {}).get("_recal_status") == "fetch_failed":
                fetch_failed += 1
        post_records_by_chunk[cf.name] = post

    print(f"\nProcessed {processed} records in {time.monotonic()-start_t:.0f}s; fetch failures: {fetch_failed}")

    # Write recalibrated chunks (overwrite in place — originals are at
    # auditor/_pre-recal-2026-06-05/chunks/)
    for fname, records in post_records_by_chunk.items():
        out = CHUNKS_DIR / fname
        with out.open("w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    # Post-recal tier counts
    post_tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    post_schema_pass = 0
    post_nap_pass = 0
    score_shifts = {"up_3": 0, "up_2": 0, "up_1": 0, "no_change": 0, "down": 0}

    # For shift tracking, re-read pre and post side by side
    pre_chunks_dir = ROOT / "auditor" / "_pre-recal-2026-06-05" / "chunks"
    for cf in chunk_files:
        pre = [json.loads(l) for l in (pre_chunks_dir / cf.name).read_text().splitlines() if l.strip()]
        post_recs = post_records_by_chunk[cf.name]
        pre_by_id = {r["vgps_id"]: r for r in pre}
        for r in post_recs:
            t = r.get("tier")
            if t in post_tier_counts:
                post_tier_counts[t] += 1
            checks = r.get("checks") or {}
            if checks.get("schema_present"):
                post_schema_pass += 1
            if checks.get("nap_consistent"):
                post_nap_pass += 1
            prev = pre_by_id.get(r["vgps_id"])
            if prev:
                delta = (r.get("score") or 0) - (prev.get("score") or 0)
                if delta >= 3:
                    score_shifts["up_3"] += 1
                elif delta == 2:
                    score_shifts["up_2"] += 1
                elif delta == 1:
                    score_shifts["up_1"] += 1
                elif delta == 0:
                    score_shifts["no_change"] += 1
                else:
                    score_shifts["down"] += 1

    print(f"\nPOST-RECAL state (across chunks 0-13):")
    print(f"  total: {n}")
    print(f"  tier A: {post_tier_counts['A']}  (Δ {post_tier_counts['A']-pre_tier_counts['A']:+d})")
    print(f"  tier B: {post_tier_counts['B']}  (Δ {post_tier_counts['B']-pre_tier_counts['B']:+d})")
    print(f"  tier C: {post_tier_counts['C']}  (Δ {post_tier_counts['C']-pre_tier_counts['C']:+d})")
    print(f"  tier D: {post_tier_counts['D']}  (Δ {post_tier_counts['D']-pre_tier_counts['D']:+d})")
    print(f"  schema_present pass: {post_schema_pass} ({100*post_schema_pass/n:.1f}%)  (Δ {post_schema_pass-pre_schema_pass:+d})")
    print(f"  nap_consistent pass: {post_nap_pass} ({100*post_nap_pass/n:.1f}%)  (Δ {post_nap_pass-pre_nap_pass:+d})")
    print()
    print("Score shift distribution (post - pre):")
    for k, v in score_shifts.items():
        print(f"  {k:10}: {v}")

    # Methodology document
    METHODOLOGY_OUT.write_text(f"""# Recalibration methodology — 2026-06-05

Re-scored two dimensions of the Phase 1 rubric per Sat's directive after the
verification spot-checks confirmed measurement artifacts in the original
chunk agents' implementation.

## Inputs
- Source: `scout/partner-directory-clean.json` (3,333 weburl-eligible records)
- Pre-recal chunks: `auditor/_pre-recal-2026-06-05/chunks/` (preserved)
- Pre-recal cuts: `auditor/_pre-recal-2026-06-05/cuts/` (preserved)

## schema_present — corrected rule

Fetch partner homepage with `User-Agent: {UA}`, timeout {TIMEOUT}s, lenient SSL.
Parse for any `<script type="application/ld+json">` block. Walk every block
(including `@graph` traversal). Collect all `@type` values across all blocks.

Pass if any collected `@type` is in this accepted set (documented per Sat's
directive that the methodology be recoverable):

```
{sorted(ACCEPTED_LD_TYPES)}
```

This list reflects what actually appears on real SMB / hospitality sites.
The earlier rubric's narrower filter rejected sites emitting `WebSite`,
`Organization`, `Place`, etc. — schema that IS agent-readable, just not
strictly LocalBusiness-flavored.

## nap_consistent — corrected rule

Three sub-checks, ALL must pass:

**Phone:** Last 10 digits of VGPS phone (after stripping non-digits) appear
anywhere in the HTML's digit-only projection. Tolerant of any visual format
on the partner site — `(760) 326-1234`, `760.326.1234`, `+1-760-326-1234`,
etc. all match.

**Name:** Pass if ANY of:
- (a) Full VGPS name substring appears in lowercased HTML
- (b) First 2-3 significant words (length > 2) of VGPS name all present in HTML
- (c) Domain root (≥4 chars, e.g. "modernway" from modernway.com) appears
  as substring in alphanumeric-only VGPS name

Rule (c) is the most forgiving and reflects how operators actually brand:
businesses often appear in VGPS under their full legal name but use a
shorter brand on their website. A `modernway.com` domain matching the VGPS
listing "Modernway Vintage Furniture & Mid-Century Modern" should pass.

**City:** VGPS city (e.g. "Palm Desert") appears as substring in lowercased HTML.

## Other dimensions

Unchanged. The 6 remaining scored dimensions (site_loads, mobile_ready,
og_metadata, faq_present, content_fresh, citation_density) and the 2
unscored diagnostics (llms_txt_present, gbp_linked) carry over from the
original chunk scoring.

## Score and tier

Score = sum of 8 scored dimensions (each True = +1). Tier:
- 7-8 → A
- 4-6 → B
- 1-3 → C
- 0   → D

## Provenance fields added to each record's checks

- `_recal_status`: `"ok"` or `"fetch_failed"` or `"exception: ..."`
- `_recal_error`: error string if fetch failed
- `_recal_schema_types_found`: list of all @types collected from partner site
- `_recal_schema_matched`: subset that matched the accepted list
- `_recal_nap_evidence`: per-component name/phone/city pass results plus the
  matching rule that fired for name

These provenance fields make the methodology auditable per partner.

## Results (this run)

- Total records re-checked: {n}
- Fetch failures during recal: {fetch_failed}
- schema_present pass rate: {pre_schema_pass} ({100*pre_schema_pass/n:.1f}%) → {post_schema_pass} ({100*post_schema_pass/n:.1f}%)
- nap_consistent pass rate: {pre_nap_pass} ({100*pre_nap_pass/n:.1f}%) → {post_nap_pass} ({100*post_nap_pass/n:.1f}%)
- Tier shifts:
  - A: {pre_tier_counts['A']} → {post_tier_counts['A']} ({post_tier_counts['A']-pre_tier_counts['A']:+d})
  - B: {pre_tier_counts['B']} → {post_tier_counts['B']} ({post_tier_counts['B']-pre_tier_counts['B']:+d})
  - C: {pre_tier_counts['C']} → {post_tier_counts['C']} ({post_tier_counts['C']-pre_tier_counts['C']:+d})
  - D: {pre_tier_counts['D']} → {post_tier_counts['D']} ({post_tier_counts['D']-pre_tier_counts['D']:+d})
""")

    print(f"\nMethodology written to {METHODOLOGY_OUT}")
    print(f"Next step: run reaggregate.py to re-emit all six cuts + CSV + wide-scan.json")


if __name__ == "__main__":
    main()
