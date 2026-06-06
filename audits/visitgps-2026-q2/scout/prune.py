#!/usr/bin/env python3
import re
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import subprocess

SITEMAP = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/scout/sitemap-2026-06-04.xml"
OUT_CANDIDATES = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/scout/listing-urls.json"
OUT_PRUNED = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/scout/pruned-by-slug.json"

LISTING_RE = re.compile(r"^https://www\.visitgreaterpalmsprings\.com/listing/([^/]+)/(\d+)/?$")

CONTAINS_TOKENS = [
    "hosted-by", "acme-house", "vacasa", "airbnb", "vrbo",
    "ryson-desert", "desert-vacations",
    "pool-spa", "firepit", "fire-pit", "gameroom", "game-room",
    "casita", "guesthouse", "guest-house", "vacation-rental",
    "king-bed", "-bd-", "-ba-",
]

REGEX_PATTERNS = [
    re.compile(r"\b[0-9]bd-[0-9]", re.IGNORECASE),
    re.compile(r"\b[0-9]br-[0-9]", re.IGNORECASE),
    re.compile(r"sleeps-[0-9]", re.IGNORECASE),
    re.compile(r"\b[0-9]-bed-[0-9]", re.IGNORECASE),
    re.compile(r"^[0-9]+-rvc", re.IGNORECASE),
    re.compile(r"^[0-9]{4,}-", re.IGNORECASE),
]

def should_prune(slug: str) -> bool:
    s = slug.lower()
    for tok in CONTAINS_TOKENS:
        if tok in s:
            return True
    for pat in REGEX_PATTERNS:
        if pat.search(s):
            return True
    return False

# Parse sitemap
tree = ET.parse(SITEMAP)
root = tree.getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

locs = [el.text for el in root.findall("sm:url/sm:loc", ns)]

total_in_sitemap = 0
candidates = []
pruned = []

for url in locs:
    if not url:
        continue
    m = LISTING_RE.match(url.strip())
    if not m:
        continue
    total_in_sitemap += 1
    slug, vgps_id = m.group(1), m.group(2)
    if should_prune(slug):
        pruned.append({"vgps_id": vgps_id, "slug": slug})
    else:
        candidates.append({
            "vgps_id": vgps_id,
            "slug": slug,
            "listing_url": f"https://www.visitgreaterpalmsprings.com/listing/{slug}/{vgps_id}/",
        })

# fetched_at_iso via `date -Iseconds`
fetched_at = subprocess.check_output(["date", "-Iseconds"]).decode().strip()

result = {
    "fetched_at_iso": fetched_at,
    "total_in_sitemap": total_in_sitemap,
    "pruned_by_slug": len(pruned),
    "candidates": candidates,
}

with open(OUT_CANDIDATES, "w") as f:
    json.dump(result, f, indent=2)

with open(OUT_PRUNED, "w") as f:
    json.dump({"pruned_by_slug": len(pruned), "items": pruned}, f, indent=2)

print(json.dumps({
    "total_in_sitemap": total_in_sitemap,
    "pruned_by_slug": len(pruned),
    "candidates": len(candidates),
    "sample_pruned_slugs": [p["slug"] for p in pruned[:10]],
}, indent=2))
