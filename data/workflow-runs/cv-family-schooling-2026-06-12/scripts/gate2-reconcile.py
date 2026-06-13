#!/usr/bin/env python3
"""CV Family & Schooling — GATE-2 reconciliation (locks the enrichment universe).
(a) promote Young Life Desert Cities review->target (Cathedral City)
(b) collapse same-city CROSS-SUBCAT clusters to one row per campus; survivor =
    highest-priority subcategory; survivor gets a programs_note recording absorbed
    programs (synthesis keeps the multi-program fact). Independent-brand programs
    would have distinct base names and are NOT caught by is_dup -> stay separate.
(c) drop phantoms: Xavier (Thousand Palms); merge the Variety name-variants per city.
    Dove's Landing (Thousand Palms) + Montessori 'PS & Palm Desert' variant -> KEEP,
    tagged _verify_note for the enrichment worker to resolve.
Operates on tmp-agent-mapped-fs.json + state. Run once.
"""
import json, re, os
COM = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(COM, 'tmp-agent-mapped-fs.json')
STATE = os.path.join(COM, 'tmp-agent-mapped-fs-state.json')

def norm(n):
    n = re.sub(r'\([^)]*\)', '', n or '')
    return re.sub(r'[^a-z0-9]', '', n.lower())

def is_dup(a, b):
    if a == b: return True
    lo, hi = sorted([a, b], key=len)
    return len(lo) >= 12 and hi.startswith(lo)

PRIORITY = {'private K-12 schools':0,'preschools & early-childhood programs':1,
            'licensed childcare & daycare centers':2,'youth sports academies & programs':3,
            'arts, music & performing-arts education for youth':4,
            'tutoring, test-prep & academic enrichment':5,
            'special-needs & developmental services for children':6,
            'camps & after-school programs':7}

data = json.load(open(DATA))
state = json.load(open(STATE))
log = []

# (a) promote Young Life -> Cathedral City target
for r in data:
    if 'young life' in r['name'].lower() and r.get('segment') == 'review':
        r['city'] = 'Cathedral City'; r['segment'] = ''; r['enrich_target'] = True
        r['_flag_reason'] = ''
        log.append(f"(a) promoted '{r['name']}' -> enrich-target (Cathedral City)")

# (c1) drop Xavier Thousand Palms phantom
before = len(data)
data = [r for r in data if not ('xavier' in r['name'].lower() and r['city'] == 'Thousand Palms')]
if len(data) < before: log.append("(c) dropped phantom: Xavier College Prep [Thousand Palms]")

# (c2) merge Variety name-variants per city (keep longer/ more-detailed name)
variety = [r for r in data if r.get('enrich_target') and 'variety' in norm(r['name']) and 'charity' in norm(r['name'])]
keep_ids = set()
by_city = {}
for r in variety: by_city.setdefault(r['city'], []).append(r)
drop_set = set()
for city, rows in by_city.items():
    rows.sort(key=lambda r: len(r['name']), reverse=True)
    for r in rows[1:]:
        drop_set.add(id(r)); log.append(f"(c) merged Variety variant -> dropped '{r['name']}' [{city}]")
data = [r for r in data if id(r) not in drop_set]

# (c3) flag Dove's Landing (Thousand Palms) + Montessori 'PS & Palm Desert' for enrichment resolve
for r in data:
    nl = r['name'].lower()
    if "dove's landing" in nl and r['city'] == 'Thousand Palms':
        r['_verify_note'] = "possible city-dup of Dove's Landing [Palm Desert] — confirm campus city, merge if same"
        log.append("(c) flagged Dove's Landing [Thousand Palms] for enrichment-resolve")
    if 'palm springs & palm desert' in nl and 'montessori' in nl:
        r['_verify_note'] = "possible variant of Montessori School of Palm Springs [PS] — confirm distinct PD campus or merge"
        log.append("(c) flagged Montessori 'PS & Palm Desert' variant for enrichment-resolve")

# (b) collapse same-city cross-subcat clusters
targets = [r for r in data if r.get('enrich_target')]
others = [r for r in data if not r.get('enrich_target')]
by_city = {}
for r in targets: by_city.setdefault(r['city'], []).append(r)
survivors, collapsed = [], 0
for city, rows in by_city.items():
    used = set(); keep = []
    for i, a in enumerate(rows):
        if i in used: continue
        clust = [a]
        for j in range(i+1, len(rows)):
            if j in used: continue
            if is_dup(norm(a['name']), norm(rows[j]['name'])):
                clust.append(rows[j]); used.add(j)
        used.add(i)
        if len(clust) > 1 and len({c['subcategory'] for c in clust}) > 1:
            clust.sort(key=lambda c: PRIORITY.get(c['subcategory'], 9))
            win = clust[0]; absorbed = clust[1:]
            notes = '; '.join(f"{c['subcategory']} ({c['name']})" for c in absorbed)
            win['programs_note'] = (win.get('programs_note','') + ' | also operates: ' + notes).strip(' |')
            for c in absorbed:
                for f in ('website','license_hint','address_hint','source'):
                    if not win.get(f) and c.get(f): win[f] = c[f]
            log.append(f"(b) collapsed [{city}] '{win['name']}' ({win['subcategory']}) <- {[c['name'] for c in absorbed]}")
            collapsed += len(absorbed)
            keep.append(win)
        else:
            keep.extend(clust)
    survivors.extend(keep)

data = survivors + others
json.dump(data, open(DATA, 'w'), indent=0)

tr = [r for r in data if r.get('enrich_target')]
rv = [r for r in data if r.get('segment') == 'review']
hm = [r for r in data if r.get('segment') == 'family_home_daycare']
by_sub, by_city2 = {}, {}
for r in tr:
    by_sub[r['subcategory']] = by_sub.get(r['subcategory'],0)+1
    by_city2[r['city']] = by_city2.get(r['city'],0)+1
state['enrich_target_count'] = len(tr); state['review_count'] = len(rv)
state['by_subcategory'] = by_sub; state['by_city'] = by_city2
state['gate2_reconcile_log'] = log
json.dump(state, open(STATE, 'w'), indent=2)

print('GATE-2 RECONCILE:')
for l in log: print('  ', l)
print(f'\nLOCKED: {len(tr)} enrich-targets | {len(rv)} review | {len(hm)} family_home (context)')
print('by_subcategory:', json.dumps(by_sub, ensure_ascii=False))
