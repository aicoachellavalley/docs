#!/usr/bin/env python3
"""
Three verification spot-checks against partners-wide-scan.json:

  1. schema_present = 0% — sample 2 A / 4 B / 4 C; manually inspect each
     partner's homepage for any JSON-LD; report @types found; conclude
     whether the rubric's filter was over-restrictive or schema is truly
     absent at meaningful rates.

  2. llms_txt_present = 23.5% — sample 10 partners flagged true; fetch
     {weburl}/llms.txt; report Content-Type, first bytes, and whether the
     response is a real llms.txt or a fallthrough-200 HTML page.

  3. NAP consistent = 5% — sample 10 Tier B partners flagged false; fetch
     homepage; check for partner name / phone / city presence; report
     whether the inconsistency is real or a measurement artifact.

Deterministic sampling (random.seed(42)).
"""
import json
import random
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path("/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2")
WIDE_SCAN = ROOT / "auditor" / "partners-wide-scan.json"

UA = "AICV-Audit/2026Q2 (+https://aicoachellavalley.org)"
TIMEOUT = 12

SSL_CTX = ssl.create_default_context()
# Be lenient on SSL — many small partner sites have expired certs
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def fetch(url, max_bytes=300_000):
    """Returns (status, content_type, body_str, error_str)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CTX) as resp:
            body = resp.read(max_bytes)
            try:
                text = body.decode("utf-8", errors="replace")
            except Exception:
                text = body.decode("latin-1", errors="replace")
            return resp.status, resp.headers.get("Content-Type", ""), text, None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", "") if e.headers else "", "", f"HTTPError {e.code}"
    except Exception as e:
        return None, "", "", f"{type(e).__name__}: {e}"


def extract_ld_types(html):
    """Return a list of @type values found in any JSON-LD block in the HTML."""
    types = []
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for blk in blocks:
        try:
            parsed = json.loads(blk.strip())
        except Exception:
            # Some sites have malformed JSON-LD; try a lax cleanup
            cleaned = blk.strip().replace("\n", " ")
            try:
                parsed = json.loads(cleaned)
            except Exception:
                types.append("(unparseable block)")
                continue

        def walk(node):
            if isinstance(node, list):
                for item in node:
                    walk(item)
            elif isinstance(node, dict):
                t = node.get("@type")
                if t:
                    if isinstance(t, list):
                        for x in t:
                            types.append(x)
                    else:
                        types.append(t)
                # @graph traversal
                graph = node.get("@graph")
                if graph:
                    walk(graph)
        walk(parsed)
    return types, len(blocks)


# Rubric's "relevant @type" list per the original prompt — broad
RUBRIC_RELEVANT = {
    "LocalBusiness", "Hotel", "Restaurant", "Event", "TouristAttraction",
    "Organization", "Service", "Product",
    # Common subtypes that should count as relevant
    "LodgingBusiness", "FoodEstablishment", "Place", "Store",
    "ShoppingCenter", "AutoDealer", "Corporation", "EducationalOrganization",
    "GovernmentOrganization", "NGO", "PerformingGroup", "SportsOrganization",
}


def check_schema(record):
    weburl = record.get("weburl")
    status, ctype, body, err = fetch(weburl)
    if err and status is None:
        return {"vgps_id": record["vgps_id"], "name": record["name"], "tier": record["tier"], "weburl": weburl, "status": None, "error": err}
    types, n_blocks = extract_ld_types(body)
    relevant_present = any(t in RUBRIC_RELEVANT for t in types)
    return {
        "vgps_id": record["vgps_id"],
        "name": record["name"],
        "tier": record["tier"],
        "weburl": weburl,
        "status": status,
        "ld_blocks": n_blocks,
        "types_found": types[:20],
        "would_rubric_pass": relevant_present,
        "error": err,
    }


def check_llms_txt(record):
    weburl = record.get("weburl", "").rstrip("/")
    url = weburl + "/llms.txt"
    status, ctype, body, err = fetch(url, max_bytes=10_000)
    sample = body[:300].replace("\n", " ⏎ ")
    # Heuristic: real llms.txt is plain text starting with markdown-ish content
    looks_real = False
    if status == 200 and body:
        first200 = body[:200].lower()
        # Real llms.txt typically starts with a markdown heading
        if first200.lstrip().startswith("#"):
            looks_real = True
        # Or has explicit llms.txt-style content
        elif "llms" in first200 or "agent" in first200 or "instructions" in first200:
            # And NOT HTML
            if "<html" not in first200 and "<!doctype" not in first200:
                looks_real = True
        # If content-type explicitly says text/plain or markdown
        if "text/plain" in (ctype or "").lower() or "markdown" in (ctype or "").lower():
            if "<html" not in first200 and "<!doctype" not in first200:
                looks_real = True
    is_html_fallthrough = "<html" in body[:500].lower() or "<!doctype" in body[:500].lower()
    return {
        "vgps_id": record["vgps_id"],
        "name": record["name"],
        "tier": record["tier"],
        "weburl": weburl,
        "url_tried": url,
        "status": status,
        "content_type": ctype,
        "looks_real": looks_real,
        "is_html_fallthrough": is_html_fallthrough,
        "sample": sample,
        "error": err,
    }


def normalize_phone(p):
    return re.sub(r"\D", "", p or "")


def check_nap(record):
    weburl = record.get("weburl")
    status, ctype, body, err = fetch(weburl)
    if err and status is None:
        return {"vgps_id": record["vgps_id"], "name": record["name"], "tier": record["tier"], "weburl": weburl, "status": None, "error": err}
    body_lower = body.lower()
    name = (record.get("name") or "").strip()
    name_lower = name.lower()
    # VGPS doesn't give us phone/city directly here, so we'll need to grab from inventory
    # Look up in inventory
    inventory_record = INVENTORY_BY_ID.get(record["vgps_id"])
    vgps_phone = (inventory_record or {}).get("phone") or ""
    vgps_phone_digits = normalize_phone(vgps_phone)
    vgps_city = (inventory_record or {}).get("addressLocality") or ""
    vgps_city_lower = vgps_city.lower()

    # Name check — substring or first significant token
    name_present = name_lower and name_lower in body_lower
    if not name_present and name_lower:
        # Try the first 2-3 significant tokens
        tokens = [t for t in re.split(r"[\s'’&]+", name_lower) if len(t) > 2][:3]
        if tokens and all(t in body_lower for t in tokens):
            name_present = True

    # Phone check — look for any subsequence of the digits in the body's digit stream
    body_digits = re.sub(r"\D", " ", body)
    phone_present = bool(vgps_phone_digits) and vgps_phone_digits[-10:] in body_digits.replace(" ", "")

    # City check
    city_present = bool(vgps_city_lower) and vgps_city_lower in body_lower

    all_three = name_present and phone_present and city_present

    return {
        "vgps_id": record["vgps_id"],
        "name": record["name"],
        "tier": record["tier"],
        "weburl": weburl,
        "status": status,
        "vgps_phone": vgps_phone,
        "vgps_city": vgps_city,
        "name_present": name_present,
        "phone_present": phone_present,
        "city_present": city_present,
        "rubric_would_pass_now": all_three,
        "error": err,
    }


def main():
    data = json.loads(WIDE_SCAN.read_text())

    # Build inventory index for NAP lookups (we need phone/city from inventory)
    global INVENTORY_BY_ID
    INVENTORY_BY_ID = {}
    inv_path = ROOT / "scout" / "partner-directory-clean.json"
    for r in json.loads(inv_path.read_text()):
        INVENTORY_BY_ID[r["vgps_id"]] = r

    random.seed(42)

    # =========================================================
    # 1. SCHEMA: 2 A / 4 B / 4 C with schema_present == False
    # =========================================================
    pool_by_tier = {"A": [], "B": [], "C": []}
    for r in data:
        if r.get("tier") in ("A", "B", "C") and r.get("weburl") and not r["checks"].get("schema_present"):
            pool_by_tier[r["tier"]].append(r)
    schema_sample = (
        random.sample(pool_by_tier["A"], min(2, len(pool_by_tier["A"]))) +
        random.sample(pool_by_tier["B"], min(4, len(pool_by_tier["B"]))) +
        random.sample(pool_by_tier["C"], min(4, len(pool_by_tier["C"])))
    )
    print("=" * 80)
    print("1. SCHEMA_PRESENT spot-check (10 partners flagged False)")
    print("=" * 80)
    schema_results = []
    for r in schema_sample:
        res = check_schema(r)
        schema_results.append(res)
        print(f"\n[{res['tier']}] {res['name']!r}")
        print(f"  weburl: {res['weburl']}")
        print(f"  status: {res.get('status')}  ld_blocks: {res.get('ld_blocks')}")
        print(f"  types_found: {res.get('types_found')}")
        print(f"  would_rubric_pass_with_broad_filter: {res.get('would_rubric_pass')}")
        if res.get("error"):
            print(f"  error: {res['error']}")

    actual_has_ld = sum(1 for r in schema_results if (r.get("ld_blocks") or 0) > 0)
    would_pass = sum(1 for r in schema_results if r.get("would_rubric_pass"))
    print(f"\n--- Schema verdict ---")
    print(f"  sampled: {len(schema_results)}")
    print(f"  have ANY ld+json block: {actual_has_ld}")
    print(f"  would pass rubric's stated relevant-@type filter: {would_pass}")

    # =========================================================
    # 2. LLMS.TXT: 10 partners with checks.llms_txt_present == True
    # =========================================================
    pool = [r for r in data if r["checks"].get("llms_txt_present") and r.get("weburl") and r.get("tier") != "Z"]
    llms_sample = random.sample(pool, min(10, len(pool)))
    print()
    print("=" * 80)
    print("2. LLMS.TXT spot-check (10 partners flagged True)")
    print("=" * 80)
    llms_results = []
    for r in llms_sample:
        res = check_llms_txt(r)
        llms_results.append(res)
        print(f"\n[{res['tier']}] {res['name']!r}")
        print(f"  url: {res['url_tried']}")
        print(f"  status: {res.get('status')}  content_type: {res.get('content_type')!r}")
        print(f"  looks_real: {res.get('looks_real')}  is_html_fallthrough: {res.get('is_html_fallthrough')}")
        print(f"  sample (first 300): {res.get('sample', '')[:300]}")
        if res.get("error"):
            print(f"  error: {res['error']}")

    real = sum(1 for r in llms_results if r.get("looks_real"))
    fallthrough = sum(1 for r in llms_results if r.get("is_html_fallthrough"))
    print(f"\n--- llms.txt verdict ---")
    print(f"  sampled: {len(llms_results)}")
    print(f"  appear to be real llms.txt: {real}")
    print(f"  HTML fallthrough (200 returning homepage): {fallthrough}")
    print(f"  other (errors, redirects, etc.): {len(llms_results) - real - fallthrough}")

    # =========================================================
    # 3. NAP: 10 Tier B partners with checks.nap_consistent == False
    # =========================================================
    pool = [r for r in data if r.get("tier") == "B" and r.get("weburl") and not r["checks"].get("nap_consistent")]
    nap_sample = random.sample(pool, min(10, len(pool)))
    print()
    print("=" * 80)
    print("3. NAP_CONSISTENT spot-check (10 Tier B flagged False)")
    print("=" * 80)
    nap_results = []
    for r in nap_sample:
        res = check_nap(r)
        nap_results.append(res)
        print(f"\n[{res['tier']}] {res['name']!r}")
        print(f"  weburl: {res['weburl']}")
        print(f"  status: {res.get('status')}")
        print(f"  vgps_phone: {res.get('vgps_phone')!r}  vgps_city: {res.get('vgps_city')!r}")
        print(f"  name_present: {res.get('name_present')}  phone_present: {res.get('phone_present')}  city_present: {res.get('city_present')}")
        print(f"  rubric_would_pass_now: {res.get('rubric_would_pass_now')}")
        if res.get("error"):
            print(f"  error: {res['error']}")

    would_pass_now = sum(1 for r in nap_results if r.get("rubric_would_pass_now"))
    print(f"\n--- NAP verdict ---")
    print(f"  sampled: {len(nap_results)} Tier B flagged inconsistent")
    print(f"  re-checked now and would pass: {would_pass_now} ({'measurement artifact suspected' if would_pass_now >= 4 else 'mostly real'})")

    # Write structured report
    report = {
        "schema_sample": schema_results,
        "llms_sample": llms_results,
        "nap_sample": nap_results,
        "verdicts": {
            "schema_sample_with_ld_blocks": actual_has_ld,
            "schema_sample_would_pass_broad_filter": would_pass,
            "llms_real_count": real,
            "llms_fallthrough_count": fallthrough,
            "nap_re_pass_count": would_pass_now,
        },
    }
    out = ROOT / "auditor" / "verify-findings-2026-06-05.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nReport written to {out}")


if __name__ == "__main__":
    main()
