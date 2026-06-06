#!/usr/bin/env python3
"""Score a chunk of partner records against the AICV agent-readiness rubric."""

import json
import re
import sys
import time
import threading
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = "AICV-Audit/2026Q2 (+https://aicoachellavalley.org)"
TIMEOUT = 10
SIX_MONTHS_AGO = datetime.now(timezone.utc) - timedelta(days=183)

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
    "wyndham", "ramada", "daysinn", "super8", "howardjohnson", "lq.com", "laquinta",
    "microtel", "travelodge", "hawthorn",
    # Choice
    "choicehotels", "comfortinn", "qualityinn", "sleep-inn", "mainstay",
    "econolodge", "rodewayinn", "ascend",
    # Other hotel
    "bestwestern", "accor", "sofitel", "fairmont", "raffles", "novotel", "mgallery",
    "swissotel", "mercure", "hgvc", "marriottvacations",
    # Restaurants / coffee / retail
    "starbucks", "panerabread", "chipotle", "mcdonalds", "subway", "dunkin",
    "dominos", "papajohns", "pizzahut", "kfc", "tacobell", "wendys", "burgerking",
    "popeyes", "chick-fil-a", "raisingcanes", "in-n-out", "jackinthebox", "carlsjr",
    "hardees",
    "olive-garden", "redlobster", "outback", "longhorn", "applebees", "chilis",
    "ihop", "dennys", "cracker-barrel", "cheesecakefactory", "rubytuesday",
    "buffalowildwings",
    "peets", "philzcoffee", "blue-bottle", "joe-and-the-juice", "sweetgreen",
    "cava", "qdoba",
    "7-eleven", "walgreens", "cvs", "walmart", "target", "costco", "lowes",
    "homedepot",
]

# Per-host last-hit timestamps for politeness
_host_lock = threading.Lock()
_host_last_hit = defaultdict(float)


def host_of(url):
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""


def polite_get(session, url, **kwargs):
    """GET with 1s delay between hits to same host."""
    host = host_of(url)
    with _host_lock:
        last = _host_last_hit[host]
        wait = 1.0 - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        _host_last_hit[host] = time.time()
    return session.get(url, timeout=TIMEOUT, allow_redirects=True, **kwargs)


def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    retry = Retry(total=1, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def chain_check(weburl):
    if not weburl:
        return False, None
    h = host_of(weburl)
    low = h.lower()
    for pat in CHAIN_PATTERNS:
        if pat in low:
            return True, pat
    return False, None


def norm_phone(s):
    return re.sub(r"[^0-9]", "", s or "")


def norm_text(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def check_site_loads(session, url):
    """Returns (passed, response_or_None, notes_str)."""
    notes = ""
    try:
        t0 = time.time()
        r = polite_get(session, url)
        elapsed = time.time() - t0
        if r.status_code == 200 and elapsed < 5.0:
            return True, r, ""
        notes = f"status={r.status_code} elapsed={elapsed:.1f}s"
        return False, r, notes
    except requests.exceptions.SSLError as e:
        return False, None, f"ssl_error: {str(e)[:80]}"
    except requests.exceptions.Timeout:
        return False, None, "timeout"
    except requests.exceptions.ConnectionError as e:
        return False, None, f"conn_error: {str(e)[:80]}"
    except Exception as e:
        return False, None, f"err: {str(e)[:80]}"


def check_nap(html, record):
    if not html:
        return False
    low = html.lower()
    name = (record.get("name") or "").lower()
    phone = norm_phone(record.get("phone"))
    city = (record.get("addressLocality") or "").lower()

    # Allow trivial formatting diffs by stripping html tags somewhat
    text = re.sub(r"<[^>]+>", " ", low)
    text = re.sub(r"\s+", " ", text)

    # Compare normalized phone digit sequence anywhere in raw html (handles various formats)
    digits = re.sub(r"[^0-9]", "", html)
    phone_ok = bool(phone) and phone in digits

    # Name match: try short fragments
    name_clean = re.sub(r"[^a-z0-9 ]", "", name).strip()
    name_ok = False
    if name_clean:
        # Try full name, else any 2+ char meaningful word
        if name_clean in text:
            name_ok = True
        else:
            # Try a distinctive token
            tokens = [t for t in name_clean.split() if len(t) >= 4]
            if tokens and all(t in text for t in tokens[:2]):
                name_ok = True

    city_ok = bool(city) and city in text

    return phone_ok and name_ok and city_ok


def check_mobile(html):
    if not html:
        return False
    return bool(re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I))


RELEVANT_SCHEMA_TYPES = {
    "localbusiness", "hotel", "restaurant", "event", "touristattraction",
    "organization", "service", "product", "lodgingbusiness", "foodestablishment",
    "bar", "cafe", "store", "shoppingcenter", "museum", "artgallery",
    "performingartstheater", "amusementpark", "park", "entertainmentbusiness",
    "sportsactivitylocation", "healthandbeautybusiness", "professionalservice",
    "homeandconstructionbusiness", "automotivebusiness", "financialservice",
    "medicalbusiness", "realestateagent", "travelagency", "winery", "brewery",
    "bedandbreakfast", "resort", "motel", "campground",
}


def check_schema(html):
    """Returns (passed, faqpage_present, datemodified_ok)."""
    if not html:
        return False, False, False
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S,
    )
    if not blocks:
        return False, False, False
    has_relevant = False
    has_faq = False
    date_mod_ok = False
    for b in blocks:
        try:
            # Strip CDATA wrappers
            txt = b.strip()
            txt = re.sub(r"^/\*.*?\*/", "", txt, flags=re.S).strip()
            txt = re.sub(r"^<!\[CDATA\[|\]\]>$", "", txt).strip()
            data = json.loads(txt)
        except Exception:
            # Try to find @type and dateModified textually
            tlow = b.lower()
            for t in RELEVANT_SCHEMA_TYPES:
                if f'"{t}"' in tlow or f"'{t}'" in tlow:
                    has_relevant = True
                    break
            if "faqpage" in tlow:
                has_faq = True
            m = re.search(r'"datemodified"\s*:\s*"([^"]+)"', tlow)
            if m:
                date_mod_ok = date_mod_ok or _date_within_6mo(m.group(1))
            continue

        for obj in _iter_json_objs(data):
            t = obj.get("@type")
            if isinstance(t, list):
                tlist = [str(x).lower() for x in t]
            elif t:
                tlist = [str(t).lower()]
            else:
                tlist = []
            for ty in tlist:
                if ty in RELEVANT_SCHEMA_TYPES:
                    has_relevant = True
                if ty == "faqpage":
                    has_faq = True
            dm = obj.get("dateModified")
            if isinstance(dm, str) and _date_within_6mo(dm):
                date_mod_ok = True
    return has_relevant, has_faq, date_mod_ok


def _iter_json_objs(data):
    if isinstance(data, dict):
        yield data
        for v in data.values():
            yield from _iter_json_objs(v)
    elif isinstance(data, list):
        for it in data:
            yield from _iter_json_objs(it)


def _date_within_6mo(s):
    try:
        # Strip Z and any timezone-less suffix
        s2 = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s2)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt >= SIX_MONTHS_AGO
    except Exception:
        # Try simple YYYY-MM-DD
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
        if m:
            try:
                dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
                return dt >= SIX_MONTHS_AGO
            except Exception:
                return False
        return False


def check_og(html):
    if not html:
        return False
    has_title = bool(re.search(r'<meta[^>]+property=["\']og:title["\']', html, re.I))
    has_desc = bool(re.search(r'<meta[^>]+property=["\']og:description["\']', html, re.I))
    has_img = bool(re.search(r'<meta[^>]+property=["\']og:image["\']', html, re.I))
    return has_title and has_desc and has_img


def check_faq(session, base_url, html, faqpage_in_schema):
    """FAQ: link to /faq, /questions, /help, /support returning 200, OR FAQPage schema, OR sitemap path."""
    if faqpage_in_schema:
        return True
    if not html:
        return False
    low = html.lower()
    # Look for links
    for path in ("/faq", "/questions", "/help", "/support"):
        if re.search(r'href=["\'][^"\']*' + re.escape(path) + r'[^"\']*["\']', low):
            # Try fetching that path
            test_url = urllib.parse.urljoin(base_url, path)
            try:
                r = polite_get(session, test_url)
                if r.status_code == 200:
                    return True
            except Exception:
                pass
    return False


def check_freshness(html, sitemap_text, schema_dmod_ok):
    if schema_dmod_ok:
        return True
    if html:
        # Visible 2026 in some date-ish context
        if re.search(r"\b2026\b", html):
            # Copyright year 2026 or just any 2026 = pass
            return True
    if sitemap_text:
        # Find lastmod tags
        for m in re.finditer(r"<lastmod>([^<]+)</lastmod>", sitemap_text, re.I):
            if _date_within_6mo(m.group(1).strip()):
                return True
    return False


def fetch_sitemap(session, base_url):
    """Try sitemap.xml, robots.txt -> Sitemap:."""
    try:
        sm_url = urllib.parse.urljoin(base_url, "/sitemap.xml")
        r = polite_get(session, sm_url)
        if r.status_code == 200 and "<" in r.text:
            return r.text, sm_url
    except Exception:
        pass
    try:
        rb = polite_get(session, urllib.parse.urljoin(base_url, "/robots.txt"))
        if rb.status_code == 200:
            for line in rb.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    sm_url = line.split(":", 1)[1].strip()
                    try:
                        r2 = polite_get(session, sm_url)
                        if r2.status_code == 200:
                            return r2.text, sm_url
                    except Exception:
                        pass
                    break
    except Exception:
        pass
    return "", None


def check_faq_in_sitemap(sitemap_text):
    if not sitemap_text:
        return False
    low = sitemap_text.lower()
    for p in ("/faq", "/questions", "/help", "/support"):
        if p in low:
            return True
    return False


def check_llms_txt(session, base_url):
    try:
        r = polite_get(session, urllib.parse.urljoin(base_url, "/llms.txt"))
        return r.status_code == 200
    except Exception:
        return False


def check_gbp(html):
    if not html:
        return False
    low = html.lower()
    return ("google.com/maps" in low) or ("g.page" in low) or ("maps.google" in low)


def check_citation_density(session, name, city):
    """Cheap heuristic: DuckDuckGo HTML for '{name} {city}' and count distinct platforms."""
    q = f"{name} {city}"
    platforms = set()
    try:
        url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(q)
        r = session.get(url, timeout=TIMEOUT, headers={"User-Agent": UA})
        if r.status_code == 200:
            low = r.text.lower()
            mapping = {
                "google.com/maps": "google",
                "g.page": "google",
                "google.com/search": "google",
                "yelp.com": "yelp",
                "tripadvisor.com": "tripadvisor",
                "opentable.com": "opentable",
                "resy.com": "resy",
                "visitgreaterpalmsprings.com": "vgps",
                "visitcalifornia.com": "tourism",
                "visitpalmsprings.com": "tourism",
            }
            for k, v in mapping.items():
                if k in low:
                    platforms.add(v)
    except Exception:
        pass
    return len(platforms) >= 3, platforms


def score_record(record, session):
    weburl = record.get("weburl")
    name = record.get("name")
    city = record.get("addressLocality")

    chain, chain_evidence = chain_check(weburl)

    checks = {
        "site_loads": False,
        "nap_consistency": False,
        "mobile_ready": False,
        "schema_markup": False,
        "og_metadata": False,
        "faq_qa": False,
        "content_freshness": False,
        "citation_density": False,
        "llms_txt_present": False,
        "gbp_linked": False,
        "notes": "",
    }
    notes_parts = []

    if not weburl:
        checks["notes"] = "no_weburl"
        out = {
            "vgps_id": record.get("vgps_id"),
            "name": name,
            "primary_category": record.get("primary_category"),
            "subcategories": record.get("subcategories", []),
            "weburl": weburl,
            "chain_brand": chain,
            "chain_brand_evidence": chain_evidence,
            "score": 0,
            "tier": "Z",
            "checks": checks,
        }
        return out

    # 1. Site loads
    site_ok, resp, site_notes = check_site_loads(session, weburl)
    checks["site_loads"] = site_ok
    if site_notes:
        notes_parts.append(site_notes)

    html = resp.text if (resp is not None and resp.status_code == 200) else ""
    base_url = resp.url if resp is not None else weburl

    # 2. NAP
    if html:
        checks["nap_consistency"] = check_nap(html, record)
    # 3. Mobile
    if html:
        checks["mobile_ready"] = check_mobile(html)
    # 4. Schema
    schema_ok, faqpage_in_schema, schema_dmod_ok = check_schema(html)
    checks["schema_markup"] = schema_ok
    # 5. OG
    if html:
        checks["og_metadata"] = check_og(html)

    # Sitemap (used by FAQ + freshness)
    sitemap_text = ""
    if site_ok:
        sitemap_text, _ = fetch_sitemap(session, base_url)

    # 6. FAQ
    faq_link_ok = check_faq(session, base_url, html, faqpage_in_schema)
    if not faq_link_ok and check_faq_in_sitemap(sitemap_text):
        faq_link_ok = True
    checks["faq_qa"] = faq_link_ok

    # 7. Freshness
    checks["content_freshness"] = check_freshness(html, sitemap_text, schema_dmod_ok)

    # 8. Citation density
    cit_ok, platforms = check_citation_density(session, name or "", city or "")
    checks["citation_density"] = cit_ok
    if platforms:
        notes_parts.append("cites=" + ",".join(sorted(platforms)))

    # Diagnostics
    if site_ok:
        checks["llms_txt_present"] = check_llms_txt(session, base_url)
        checks["gbp_linked"] = check_gbp(html)

    checks["notes"] = "; ".join(notes_parts) if notes_parts else ""

    # Score
    scored_keys = [
        "site_loads", "nap_consistency", "mobile_ready", "schema_markup",
        "og_metadata", "faq_qa", "content_freshness", "citation_density",
    ]
    score = sum(1 for k in scored_keys if checks[k])
    if score >= 7:
        tier = "A"
    elif score >= 4:
        tier = "B"
    elif score >= 1:
        tier = "C"
    else:
        tier = "D"

    return {
        "vgps_id": record.get("vgps_id"),
        "name": name,
        "primary_category": record.get("primary_category"),
        "subcategories": record.get("subcategories", []),
        "weburl": weburl,
        "chain_brand": chain,
        "chain_brand_evidence": chain_evidence,
        "score": score,
        "tier": tier,
        "checks": checks,
    }


def main():
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])
    workers = int(sys.argv[5]) if len(sys.argv) > 5 else 12

    with open(in_path) as f:
        data = json.load(f)
    my_slice = data[start:end]

    # Each thread gets its own session
    local = threading.local()

    def get_session():
        if not hasattr(local, "s"):
            local.s = make_session()
        return local.s

    def work(idx_record):
        idx, rec = idx_record
        try:
            return idx, score_record(rec, get_session())
        except Exception as e:
            return idx, {
                "vgps_id": rec.get("vgps_id"),
                "name": rec.get("name"),
                "primary_category": rec.get("primary_category"),
                "subcategories": rec.get("subcategories", []),
                "weburl": rec.get("weburl"),
                "chain_brand": False,
                "chain_brand_evidence": None,
                "score": 0,
                "tier": "D",
                "checks": {
                    "site_loads": False, "nap_consistency": False,
                    "mobile_ready": False, "schema_markup": False,
                    "og_metadata": False, "faq_qa": False,
                    "content_freshness": False, "citation_density": False,
                    "llms_txt_present": False, "gbp_linked": False,
                    "notes": f"worker_exception: {str(e)[:120]}",
                },
            }

    results = [None] * len(my_slice)
    indexed = list(enumerate(my_slice))
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(work, ir) for ir in indexed]
        for fut in as_completed(futs):
            idx, scored = fut.result()
            results[idx] = scored
            done += 1
            if done % 20 == 0:
                print(f"  progress: {done}/{len(my_slice)}", file=sys.stderr, flush=True)

    # Append-write JSONL
    with open(out_path, "a") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Tier histogram
    hist = {"A": 0, "B": 0, "C": 0, "D": 0, "Z": 0}
    for r in results:
        hist[r["tier"]] = hist.get(r["tier"], 0) + 1
    print(json.dumps({"scored": len(results), "tiers": hist}))


if __name__ == "__main__":
    main()
