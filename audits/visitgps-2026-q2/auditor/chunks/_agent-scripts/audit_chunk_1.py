#!/usr/bin/env python3
"""Audit chunk 1 (records 239:478) for VGPS 2026 Q2 partner directory."""
import json
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from datetime import datetime, timezone
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests

INPUT = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/scout/partner-directory-clean.json"
OUTPUT = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/auditor/chunks/chunk-1.jsonl"
UA = "AICV-Audit/2026Q2 (+https://aicoachellavalley.org)"
TIMEOUT = 10
START = 239
END = 478

# Threshold: 6 months back from 2026-06-05 = 2025-12-05
FRESHNESS_CUTOFF = datetime(2025, 12, 5, tzinfo=timezone.utc)

CHAIN_PATTERNS = [
    # Marriott family
    "marriott.com", "marriotthotels", "courtyard", "fairfield", "residenceinn", "springhill",
    "jw-marriott", "ritzcarlton", "ritz-carlton", "sheraton", "westin", "w-hotels",
    "autograph", "gaylord", "le-meridien", "st-regis", "renaissance",
    # Hilton family
    "hilton.com", "doubletree", "hampton", "embassy-suites", "embassysuites", "conrad-hotels",
    "waldorfastoria", "waldorf-astoria", "canopy", "curio", "tapestry", "homewood-suites",
    "homewoodsuites", "home2suites",
    # Hyatt family
    "hyatt.com", "hyattregency", "hyattplace", "andaz", "grand-hyatt", "park-hyatt",
    "thompson-hotels", "hyatt-house",
    # IHG
    "ihg.com", "holidayinn", "holiday-inn", "crowneplaza", "crowne-plaza", "intercontinental",
    "kimptonhotels", "candlewood", "staybridge", "hotelindigo",
    # Wyndham
    "wyndham", "ramada", "daysinn", "super8", "howardjohnson", "lq.com", "laquinta",
    "microtel", "travelodge", "hawthorn",
    # Choice
    "choicehotels", "comfortinn", "qualityinn", "sleep-inn", "sleepinn", "mainstay",
    "econolodge", "rodewayinn", "ascend",
    # Other hotel
    "bestwestern", "best-western", "sofitel", "fairmont", "raffles", "novotel", "mgallery",
    "swissotel", "mercure", "accor", "hgvc", "marriottvacations",
    # Restaurant / coffee / retail chains
    "starbucks", "panerabread", "chipotle", "mcdonalds", "subway.com", "dunkin", "dominos",
    "papajohns", "pizzahut", "kfc.com", "tacobell", "wendys", "burgerking", "popeyes",
    "chick-fil-a", "raisingcanes", "in-n-out", "innout", "jackinthebox", "carlsjr", "hardees",
    "olive-garden", "olivegarden", "redlobster", "outback", "longhorn", "applebees", "chilis",
    "ihop", "dennys", "cracker-barrel", "crackerbarrel", "cheesecakefactory", "rubytuesday",
    "bjsrestaurants", "buffalowildwings",
    "peets", "philzcoffee", "bluebottle", "blue-bottle", "joeandthejuice", "joe-and-the-juice",
    "sweetgreen", "cava.com", "qdoba",
    "7-eleven", "7eleven", "walgreens", "cvs.com", "walmart", "target.com", "costco",
    "lowes.com", "homedepot",
]

# Per-host rate limiting
_host_locks = {}
_host_last = {}
_locks_lock = threading.Lock()


def host_throttle(host):
    """Ensure 1s between hits to the same host."""
    with _locks_lock:
        lock = _host_locks.setdefault(host, threading.Lock())
    with lock:
        last = _host_last.get(host, 0)
        wait = 1.0 - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        _host_last[host] = time.time()


def session():
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def fetch(s, url, allow_redirects=True):
    try:
        host = urlparse(url).netloc
        host_throttle(host)
        r = s.get(url, timeout=TIMEOUT, allow_redirects=allow_redirects, verify=False)
        return r, None
    except Exception as e:
        return None, str(e)[:120]


def head(s, url):
    try:
        host = urlparse(url).netloc
        host_throttle(host)
        r = s.head(url, timeout=TIMEOUT, allow_redirects=True, verify=False)
        return r, None
    except Exception as e:
        return None, str(e)[:120]


def check_chain(weburl):
    if not weburl:
        return False, None
    host = urlparse(weburl).netloc.lower()
    for pat in CHAIN_PATTERNS:
        if pat in host:
            return True, pat
    return False, None


def norm_phone(p):
    return re.sub(r"\D+", "", p or "")


def norm_text(t):
    return re.sub(r"\s+", " ", (t or "").lower()).strip()


def check_nap(html, name, phone, city):
    text = norm_text(html)
    name_match = bool(name) and norm_text(name).split()[0] in text if name else False
    # be more lenient: check first 2 words of name
    if name:
        nm = norm_text(name)
        # try full or significant tokens
        tokens = [t for t in re.split(r"\W+", nm) if len(t) > 3]
        name_match = any(t in text for t in tokens[:3]) if tokens else (nm in text)
    phone_match = False
    if phone:
        digits = norm_phone(phone)
        if len(digits) >= 10:
            d10 = digits[-10:]
            # find any sequence containing these digits (allowing separators)
            stripped = re.sub(r"\D+", "", html or "")
            phone_match = d10 in stripped
    city_match = False
    if city:
        city_match = norm_text(city) in text
    passed = name_match and phone_match and city_match
    return passed, {"name": name_match, "phone": phone_match, "city": city_match}


def check_viewport(html):
    return bool(re.search(r'<meta[^>]+name=["\']viewport["\']', html or "", re.I))


SCHEMA_TYPES = {
    "localbusiness", "hotel", "restaurant", "event", "touristattraction",
    "organization", "service", "product", "lodgingbusiness", "foodestablishment",
    "bar", "cafe", "barorpub", "winery", "brewery", "museum", "store",
    "shoppingcenter", "healthandbeautybusiness", "professionalservice",
    "entertainmentbusiness", "sportsactivitylocation", "place", "civicstructure",
    "amusementpark", "performingartstheater", "artgallery", "spa", "resort",
    "campground", "golfcourse", "park", "nightclub", "homeandconstructionbusiness",
}


def check_schema(html):
    if not html:
        return False
    blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                       html, re.I | re.S)
    for b in blocks:
        bl = b.lower()
        # quick scan for @type
        types = re.findall(r'"@type"\s*:\s*"([^"]+)"', bl)
        for t in types:
            tn = t.replace(" ", "").lower()
            if tn in SCHEMA_TYPES:
                return True
        # arrays
        types_arr = re.findall(r'"@type"\s*:\s*\[([^\]]+)\]', bl)
        for arr in types_arr:
            for t in re.findall(r'"([^"]+)"', arr):
                if t.replace(" ", "").lower() in SCHEMA_TYPES:
                    return True
    return False


def check_og(html):
    if not html:
        return False
    has_title = bool(re.search(r'<meta[^>]+property=["\']og:title["\']', html, re.I))
    has_desc = bool(re.search(r'<meta[^>]+property=["\']og:description["\']', html, re.I))
    has_img = bool(re.search(r'<meta[^>]+property=["\']og:image["\']', html, re.I))
    return has_title and has_desc and has_img


FAQ_PATHS = ["/faq", "/faqs", "/questions", "/help", "/support", "/faq/", "/faqs/", "/help/", "/support/"]


def check_faq(s, base, html, sitemap_text):
    # FAQPage schema?
    if html and re.search(r'"@type"\s*:\s*"FAQPage"', html, re.I):
        return True
    # link in homepage
    if html:
        for path in FAQ_PATHS:
            if re.search(r'href=["\'][^"\']*' + re.escape(path) + r'["\']', html, re.I):
                # try fetching
                try:
                    full = urljoin(base, path)
                    r, _ = head(s, full)
                    if r and r.status_code == 200:
                        return True
                except Exception:
                    pass
    # sitemap reveals
    if sitemap_text:
        sl = sitemap_text.lower()
        for path in ["/faq", "/questions", "/help", "/support"]:
            if path in sl:
                return True
    return False


def check_freshness(html, sitemap_text):
    # copyright 2026
    if html and re.search(r'(?:©|copyright|&copy;)[\s\w]*?20(2[6-9]|3\d)', html, re.I):
        return True
    if html and "2026" in html:
        # check if visible blog date / dateModified
        if re.search(r'datemodified["\']?\s*[:=]\s*["\']20(2[6-9]|3\d)', html, re.I):
            return True
        if re.search(r'datepublished["\']?\s*[:=]\s*["\']2026', html, re.I):
            return True
    # sitemap lastmod
    if sitemap_text:
        lastmods = re.findall(r'<lastmod>([^<]+)</lastmod>', sitemap_text, re.I)
        for lm in lastmods:
            try:
                # try ISO parse
                lm_clean = lm.strip().split("T")[0]
                dt = datetime.strptime(lm_clean[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if dt >= FRESHNESS_CUTOFF:
                    return True
            except Exception:
                continue
    # dateModified in JSON-LD
    if html:
        dms = re.findall(r'"dateModified"\s*:\s*"([^"]+)"', html)
        for dm in dms:
            try:
                dt = datetime.strptime(dm[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if dt >= FRESHNESS_CUTOFF:
                    return True
            except Exception:
                continue
    return False


def fetch_sitemap(s, base):
    """Try /sitemap.xml and /sitemap_index.xml."""
    for path in ["/sitemap.xml", "/sitemap_index.xml"]:
        try:
            full = urljoin(base, path)
            r, _ = fetch(s, full)
            if r and r.status_code == 200 and r.text:
                return r.text[:200000]
        except Exception:
            continue
    return ""


def check_llms_txt(s, base):
    try:
        full = urljoin(base, "/llms.txt")
        r, _ = head(s, full)
        return bool(r and r.status_code == 200)
    except Exception:
        return False


def check_gbp(html):
    if not html:
        return False
    return bool(re.search(r'(google\.com/maps|g\.page|maps\.app\.goo\.gl|maps\.google)', html, re.I))


# Citation density: heuristic — we cannot easily web-search per record at scale.
# We'll detect outbound links from homepage to known platforms + VGPS listing assumed.
PLATFORMS = [
    "google.com/maps", "g.page", "maps.google", "maps.app.goo",
    "yelp.com", "tripadvisor.com", "opentable.com", "resy.com",
    "visitgreaterpalmsprings", "visitcalifornia", "visitpalmsprings",
    "facebook.com", "instagram.com",  # social often co-listed
]


def check_citation_density(html, listing_url):
    """Heuristic: count distinct platforms referenced. VGPS counts as 1."""
    platforms_found = set()
    # VGPS listing always counts
    if listing_url:
        platforms_found.add("vgps")
    if html:
        h = html.lower()
        for p in ["google.com/maps", "g.page", "maps.google", "maps.app.goo"]:
            if p in h:
                platforms_found.add("google")
                break
        if "yelp.com" in h:
            platforms_found.add("yelp")
        if "tripadvisor" in h:
            platforms_found.add("tripadvisor")
        if "opentable" in h:
            platforms_found.add("opentable")
        if "resy.com" in h:
            platforms_found.add("resy")
        # tourism boards
        for p in ["visitcalifornia", "visitpalmsprings", "visitgreaterpalmsprings",
                  "palmspringsoasis", "discoverlosangeles"]:
            if p in h:
                platforms_found.add("tourism")
                break
    return len(platforms_found) >= 3, list(platforms_found)


def audit_record(rec):
    notes = []
    weburl = rec.get("weburl") or ""
    name = rec.get("name") or ""
    phone = rec.get("phone") or ""
    city = rec.get("addressLocality") or ""
    listing_url = rec.get("listing_url") or ""

    chain, chain_evidence = check_chain(weburl)

    checks = {
        "site_loads": False,
        "nap_consistent": False,
        "mobile_ready": False,
        "schema_markup": False,
        "og_metadata": False,
        "faq_qa": False,
        "content_fresh": False,
        "citation_density": False,
        "llms_txt_present": False,
        "gbp_linked": False,
        "notes": "",
    }

    if not weburl:
        checks["notes"] = "no weburl"
        out = {**{k: rec.get(k) for k in ("vgps_id", "name", "primary_category", "subcategories", "weburl")},
               "chain_brand": chain, "chain_brand_evidence": chain_evidence,
               "score": 0, "tier": "D", "checks": checks}
        return out

    s = session()

    # 1. Site loads
    start = time.time()
    r, err = fetch(s, weburl)
    elapsed = time.time() - start
    html = ""
    final_url = weburl
    if r is not None:
        final_url = r.url
        if r.status_code == 200 and elapsed < 5:
            checks["site_loads"] = True
        else:
            notes.append(f"http {r.status_code} t={elapsed:.1f}s")
        try:
            html = r.text or ""
        except Exception:
            html = ""
    else:
        notes.append(f"fetch err: {err}")

    # 2. NAP
    if html:
        nap_ok, nap_detail = check_nap(html, name, phone, city)
        checks["nap_consistent"] = nap_ok
        if not nap_ok:
            miss = [k for k, v in nap_detail.items() if not v]
            if miss:
                notes.append("nap miss:" + ",".join(miss))

    # 3. Mobile
    checks["mobile_ready"] = check_viewport(html)

    # 4. Schema
    checks["schema_markup"] = check_schema(html)

    # 5. OG
    checks["og_metadata"] = check_og(html)

    # Sitemap once
    sitemap_text = fetch_sitemap(s, final_url) if html else ""

    # 6. FAQ
    checks["faq_qa"] = check_faq(s, final_url, html, sitemap_text)

    # 7. Freshness
    checks["content_fresh"] = check_freshness(html, sitemap_text)

    # 8. Citation density (heuristic from homepage outbound links)
    cit_ok, plats = check_citation_density(html, listing_url)
    checks["citation_density"] = cit_ok
    if plats:
        notes.append("plats:" + ",".join(sorted(plats)))

    # Unscored
    checks["llms_txt_present"] = check_llms_txt(s, final_url) if html else False
    checks["gbp_linked"] = check_gbp(html)

    score = sum(1 for k in ["site_loads", "nap_consistent", "mobile_ready", "schema_markup",
                            "og_metadata", "faq_qa", "content_fresh", "citation_density"]
                if checks[k])
    if score >= 7:
        tier = "A"
    elif score >= 4:
        tier = "B"
    elif score >= 1:
        tier = "C"
    else:
        tier = "D"

    checks["notes"] = "; ".join(notes)[:400]

    return {
        "vgps_id": rec.get("vgps_id"),
        "name": name,
        "primary_category": rec.get("primary_category"),
        "subcategories": rec.get("subcategories", []),
        "weburl": weburl,
        "chain_brand": chain,
        "chain_brand_evidence": chain_evidence,
        "score": score,
        "tier": tier,
        "checks": checks,
    }


def main():
    with open(INPUT) as f:
        data = json.load(f)
    my_slice = data[START:END]
    print(f"Auditing {len(my_slice)} records [{START}:{END})")

    # parallelize across distinct hosts (per-host lock handles serialization)
    results = []
    errors = []
    tier_dist = {"A": 0, "B": 0, "C": 0, "D": 0}

    out_f = open(OUTPUT, "w")

    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(audit_record, rec): i for i, rec in enumerate(my_slice)}
        done = 0
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                errors.append(f"idx{i}: {e}")
                continue
            results.append((i, res))
            tier_dist[res["tier"]] = tier_dist.get(res["tier"], 0) + 1
            done += 1
            if done % 20 == 0:
                print(f"  done {done}/{len(my_slice)}")

    # write in original order
    results.sort(key=lambda x: x[0])
    for _, res in results:
        out_f.write(json.dumps(res) + "\n")
    out_f.close()

    print(f"Scored {len(results)} records")
    print(f"Tier dist: {tier_dist}")
    print(f"Errors: {len(errors)}")
    if errors:
        for e in errors[:10]:
            print("  ", e)


if __name__ == "__main__":
    main()
