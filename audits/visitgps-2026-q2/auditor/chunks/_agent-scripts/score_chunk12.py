#!/usr/bin/env python3
"""Score chunk 12 (indices 1912..2151) of partner-directory-clean.json."""
import json
import re
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import urllib.request
import urllib.error
import ssl
import gzip
import io

INPUT = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/scout/partner-directory-clean.json"
OUTPUT = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/auditor/chunks/chunk-12.jsonl"
START, END = 2868, 3107

UA = "AICV-Audit/2026Q2 (+https://aicoachellavalley.org)"
TIMEOUT = 10

CHAIN_PATTERNS = [
    # Marriott
    "marriott.com", "marriotthotels", "courtyard", "fairfield", "residenceinn",
    "springhill", "jw-marriott", "ritzcarlton", "sheraton", "westin", "w-hotels",
    "autograph", "gaylord", "le-meridien", "st-regis", "renaissance",
    # Hilton
    "hilton.com", "doubletree", "hampton", "embassy-suites", "conrad-hotels",
    "waldorfastoria", "canopy", "curio", "tapestry", "homewood-suites", "home2suites",
    # Hyatt
    "hyatt.com", "hyattregency", "hyattplace", "andaz", "grand-hyatt", "park-hyatt",
    "thompson-hotels", "hyatt-house",
    # IHG
    "ihg.com", "holidayinn", "crowneplaza", "intercontinental", "kimptonhotels",
    "candlewood", "staybridge", "hotelindigo",
    # Wyndham
    "wyndham", "ramada", "daysinn", "super8", "howardjohnson", "lq", "laquinta",
    "microtel", "travelodge", "hawthorn",
    # Choice
    "choicehotels", "comfortinn", "qualityinn", "sleep-inn", "mainstay", "econolodge",
    "rodewayinn", "ascend",
    # Other hotels
    "bestwestern", "best-western", "sofitel", "fairmont", "raffles", "novotel",
    "mgallery", "swissotel", "mercure", "hgvc",
    # Restaurants
    "starbucks", "panerabread", "chipotle", "mcdonalds", "subway", "dunkin",
    "dominos", "papajohns", "pizzahut", "kfc", "tacobell", "wendys", "burgerking",
    "popeyes", "chick-fil-a", "raisingcanes", "in-n-out", "jackinthebox", "carlsjr",
    "hardees", "olive-garden", "redlobster", "outback", "longhorn", "applebees",
    "chilis", "ihop", "dennys", "cracker-barrel", "cheesecakefactory", "rubytuesday",
    "buffalowildwings", "peets", "philzcoffee", "blue-bottle", "joe-and-the-juice",
    "sweetgreen", "cava", "qdoba",
    # Retail
    "7-eleven", "walgreens", "cvs", "walmart", "target", "costco", "lowes", "homedepot",
]


def detect_chain(weburl):
    if not weburl:
        return False, None
    u = weburl.lower()
    for pat in CHAIN_PATTERNS:
        if pat in u:
            return True, pat
    return False, None


def fetch(url, timeout=TIMEOUT, method="GET"):
    """Fetch URL, returns (status, final_url, body_text, headers, elapsed)."""
    if not url:
        return None, None, "", {}, 0.0
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
        }, method=method)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            elapsed = time.time() - t0
            data = resp.read(2_000_000)  # cap 2MB
            headers = {k.lower(): v for k, v in resp.headers.items()}
            if headers.get("content-encoding", "").lower() == "gzip":
                try:
                    data = gzip.decompress(data)
                except Exception:
                    pass
            try:
                text = data.decode("utf-8", errors="replace")
            except Exception:
                text = ""
            return resp.status, resp.url, text, headers, elapsed
    except urllib.error.HTTPError as e:
        try:
            data = e.read(500_000)
            text = data.decode("utf-8", errors="replace")
        except Exception:
            text = ""
        return e.code, url, text, {}, 0.0
    except Exception as e:
        return None, url, str(e), {}, 0.0


def head_or_get(url, timeout=TIMEOUT):
    """Check status code only via lightweight GET (some servers reject HEAD)."""
    if not url:
        return None
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def norm_phone(s):
    return re.sub(r"\D", "", s or "")


def check_nap(html, name, phone, locality):
    if not html:
        return False
    html_l = html.lower()
    name_ok = False
    if name:
        # strip parentheticals / "at X" suffixes for a more forgiving match
        # try short form first
        short = re.split(r"\s+at\s+|\s+\-\s+|\s+–\s+|\s+—\s+|\(", name, maxsplit=1)[0].strip()
        if short and short.lower() in html_l:
            name_ok = True
        elif name.lower() in html_l:
            name_ok = True
    phone_ok = False
    if phone:
        pn = norm_phone(phone)
        if pn:
            # crude digit search: find sequences of 10 digits in html with formatting
            html_digits = re.sub(r"[^\d]", "", html)
            if pn[-10:] in html_digits:
                phone_ok = True
    loc_ok = False
    if locality:
        if locality.lower() in html_l:
            loc_ok = True
    return name_ok and phone_ok and loc_ok


def check_mobile(html):
    if not html:
        return False
    return bool(re.search(r'<meta\s+[^>]*name=["\']viewport["\']', html, re.I))


SCHEMA_TYPES = {
    "localbusiness", "hotel", "restaurant", "event", "touristattraction",
    "organization", "service", "product", "lodgingbusiness", "foodestablishment",
    "bar", "cafe", "winery", "barorpub", "nightclub", "store", "shoppingcenter",
    "museum", "park", "golfcourse", "sportsactivitylocation", "healthandbeautybusiness",
    "spa", "medicalbusiness", "professionalservice", "entertainmentbusiness",
    "performingartstheater", "movietheater", "civicstructure", "place",
    "automotivebusiness", "homeandconstructionbusiness", "financialservice",
    "realestateagent", "travelagency", "tourismattraction", "campground",
    "resort", "bedandbreakfast", "motel",
}


def check_schema(html):
    if not html:
        return False
    blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                        html, re.I | re.S)
    for b in blocks:
        try:
            data = json.loads(b.strip())
        except Exception:
            # tolerate trailing commas etc
            stripped = re.sub(r",(\s*[}\]])", r"\1", b.strip())
            try:
                data = json.loads(stripped)
            except Exception:
                # fall back to substring search
                lo = b.lower()
                for t in SCHEMA_TYPES:
                    if f'"@type"' in lo and t in lo:
                        return True
                continue

        def types_of(node):
            if isinstance(node, dict):
                t = node.get("@type")
                if t:
                    if isinstance(t, list):
                        for x in t:
                            yield str(x).lower()
                    else:
                        yield str(t).lower()
                for v in node.values():
                    yield from types_of(v)
            elif isinstance(node, list):
                for v in node:
                    yield from types_of(v)

        for t in types_of(data):
            if t in SCHEMA_TYPES:
                return True
            # also accept anything containing 'business' or 'organization'
            if "business" in t or "hotel" in t or "restaurant" in t or "event" in t:
                return True
    return False


def check_og(html):
    if not html:
        return False
    has_title = bool(re.search(r'<meta\s+[^>]*property=["\']og:title["\']', html, re.I))
    has_desc = bool(re.search(r'<meta\s+[^>]*property=["\']og:description["\']', html, re.I))
    has_image = bool(re.search(r'<meta\s+[^>]*property=["\']og:image["\']', html, re.I))
    return has_title and has_desc and has_image


def check_faq(html, base_url):
    if not html:
        return False
    # FAQPage schema
    if re.search(r'"@type"\s*:\s*"FAQPage"', html, re.I):
        return True
    # Look for links to /faq, /questions, /help, /support
    links = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
    candidates = []
    for href in links:
        h = href.lower()
        if re.search(r"/(faq|faqs|questions|help|support)(/|$|\?|#)", h):
            try:
                full = urljoin(base_url, href)
                candidates.append(full)
            except Exception:
                pass
    # de-dupe
    seen = set()
    for c in candidates[:5]:
        if c in seen:
            continue
        seen.add(c)
        st = head_or_get(c, timeout=6)
        if st and 200 <= st < 400:
            return True
    return False


def check_freshness(html, base_url, sitemap_text=None):
    if not html:
        return False
    # Copyright year 2026
    if re.search(r"(©|\(c\)|copyright)[^0-9]{0,10}2026", html, re.I):
        return True
    # 2026 blog post link visible
    if re.search(r"/2026/[0-9]{1,2}/", html):
        return True
    # dateModified within 6 months
    m = re.search(r'"dateModified"\s*:\s*"([^"]+)"', html)
    if m:
        date = m.group(1)
        if "2026" in date or "2025-12" in date or "2025-11" in date or "2025-10" in date or "2025-09" in date or "2025-08" in date or "2025-07" in date:
            # within 6 months of 2026-06-05 => after 2025-12-05
            if re.match(r"2026", date) or re.match(r"2025-1[2-9]", date):
                return True
            # be permissive - accept 2026 anything
            if "2026" in date:
                return True
    # Sitemap lastmod
    if sitemap_text:
        lastmods = re.findall(r"<lastmod>([^<]+)</lastmod>", sitemap_text)
        for lm in lastmods:
            if re.match(r"2026", lm):
                return True
            mt = re.match(r"2025-(\d{2})", lm)
            if mt and int(mt.group(1)) >= 12:
                return True
    return False


def check_llms(base_url):
    if not base_url:
        return False
    try:
        p = urlparse(base_url)
        u = f"{p.scheme}://{p.netloc}/llms.txt"
        st = head_or_get(u, timeout=6)
        return st is not None and 200 <= st < 300
    except Exception:
        return False


def check_gbp(html):
    if not html:
        return False
    return ("google.com/maps" in html.lower() or "g.page" in html.lower()
            or "maps.app.goo.gl" in html.lower() or "maps.google" in html.lower())


# Web search citation density via DuckDuckGo HTML
def citation_density(name, city):
    if not name:
        return False
    q = f"{name} {city}".strip()
    try:
        url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(q)}"
    except AttributeError:
        from urllib.parse import quote
        url = f"https://duckduckgo.com/html/?q={quote(q)}"
    status, _, html, _, _ = fetch(url, timeout=8)
    if not html:
        return False
    h = html.lower()
    platforms = 0
    for pat in ["google.com/maps", "g.page", "maps.google",
                "yelp.com", "tripadvisor.com", "opentable.com", "resy.com",
                "visitcalifornia.com", "visitgreaterpalmsprings.com",
                "visitpalmsprings.com", "visitcoachella.org"]:
        if pat in h:
            platforms += 1
            if platforms >= 3:
                return True
    return platforms >= 3


# Per-host throttling
_host_locks = defaultdict(threading.Lock)
_host_last = defaultdict(float)


def throttled_fetch(url, timeout=TIMEOUT):
    host = ""
    try:
        host = urlparse(url).netloc
    except Exception:
        pass
    if host:
        with _host_locks[host]:
            wait = 1.0 - (time.time() - _host_last[host])
            if wait > 0:
                time.sleep(wait)
            res = fetch(url, timeout=timeout)
            _host_last[host] = time.time()
            return res
    return fetch(url, timeout=timeout)


def score_record(rec):
    notes = []
    weburl = rec.get("weburl") or ""
    name = rec.get("name") or ""
    phone = rec.get("phone") or ""
    locality = rec.get("addressLocality") or ""
    chain, ev = detect_chain(weburl)

    checks = {
        "site_loads": False,
        "nap_consistency": False,
        "mobile_ready": False,
        "schema_markup": False,
        "og_metadata": False,
        "faq_present": False,
        "content_freshness": False,
        "citation_density": False,
        "llms_txt_present": False,
        "gbp_linked": False,
        "notes": "",
    }

    if not weburl:
        checks["notes"] = "no weburl"
        return build_output(rec, chain, ev, 0, "D", checks)

    status, final_url, html, headers, elapsed = throttled_fetch(weburl)
    if status and 200 <= status < 400 and elapsed < 5.0:
        checks["site_loads"] = True
    else:
        if status is None:
            notes.append(f"fetch failed: {html[:80]}")
        else:
            notes.append(f"status={status} elapsed={elapsed:.1f}s")

    base = final_url or weburl

    if html and checks["site_loads"]:
        checks["nap_consistency"] = check_nap(html, name, phone, locality)
        checks["mobile_ready"] = check_mobile(html)
        checks["schema_markup"] = check_schema(html)
        checks["og_metadata"] = check_og(html)
        checks["faq_present"] = check_faq(html, base)
        # Sitemap fetch for freshness
        sitemap_text = None
        try:
            p = urlparse(base)
            sm_url = f"{p.scheme}://{p.netloc}/sitemap.xml"
            sm_status, _, sm_text, _, _ = throttled_fetch(sm_url, timeout=6)
            if sm_status and 200 <= sm_status < 300:
                sitemap_text = sm_text
                # Also check for faq path in sitemap
                if not checks["faq_present"] and re.search(r"/(faq|faqs|questions|help|support)", sm_text or "", re.I):
                    checks["faq_present"] = True
        except Exception:
            pass
        checks["content_freshness"] = check_freshness(html, base, sitemap_text)
        checks["gbp_linked"] = check_gbp(html)
        checks["llms_txt_present"] = check_llms(base)
        try:
            checks["citation_density"] = citation_density(name, locality)
        except Exception as e:
            notes.append(f"citation err: {str(e)[:40]}")

    checks["notes"] = "; ".join(notes)[:300]

    scored_keys = ["site_loads", "nap_consistency", "mobile_ready", "schema_markup",
                   "og_metadata", "faq_present", "content_freshness", "citation_density"]
    score = sum(1 for k in scored_keys if checks[k])
    if score >= 7:
        tier = "A"
    elif score >= 4:
        tier = "B"
    elif score >= 1:
        tier = "C"
    else:
        tier = "D"

    return build_output(rec, chain, ev, score, tier, checks)


def build_output(rec, chain, ev, score, tier, checks):
    return {
        "vgps_id": rec.get("vgps_id"),
        "name": rec.get("name"),
        "primary_category": rec.get("primary_category"),
        "subcategories": rec.get("subcategories", []),
        "weburl": rec.get("weburl"),
        "chain_brand": chain,
        "chain_brand_evidence": ev,
        "score": score,
        "tier": tier,
        "checks": checks,
    }


def main():
    with open(INPUT) as f:
        data = json.load(f)
    my = data[START:END]
    print(f"Scoring {len(my)} records [{START}:{END})", file=sys.stderr)

    results = [None] * len(my)
    # Concurrency across hosts, but throttled_fetch handles per-host
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(score_record, rec): i for i, rec in enumerate(my)}
        done = 0
        for fut in as_completed(futs):
            i = futs[fut]
            try:
                results[i] = fut.result()
            except Exception as e:
                rec = my[i]
                ch, ev = detect_chain(rec.get("weburl") or "")
                results[i] = build_output(rec, ch, ev, 0, "D", {
                    "site_loads": False, "nap_consistency": False, "mobile_ready": False,
                    "schema_markup": False, "og_metadata": False, "faq_present": False,
                    "content_freshness": False, "citation_density": False,
                    "llms_txt_present": False, "gbp_linked": False,
                    "notes": f"worker exc: {str(e)[:120]}",
                })
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{len(my)}", file=sys.stderr)

    with open(OUTPUT, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Tier histogram
    hist = defaultdict(int)
    for r in results:
        hist[r["tier"]] += 1
    print(f"Tier dist: A={hist['A']} B={hist['B']} C={hist['C']} D={hist['D']}", file=sys.stderr)


if __name__ == "__main__":
    main()
