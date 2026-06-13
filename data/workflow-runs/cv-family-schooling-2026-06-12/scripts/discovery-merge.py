#!/usr/bin/env python3
"""CV Family & Schooling discovery merge/checkpoint. Reusable across batches.
Usage: python3 tmp-fs-discovery-merge.py <batch_task_output_file> <batch_index>

Reads the workflow task-output envelope, normalizes + dedups candidates against
the on-disk scratch (tmp-agent-mapped-fs.json), appends new rows with provenance,
then RE-TRIAGES every row into:
  - 'ok'      -> enrich_target=True  (physical CV campus confirmed/assumed in city)
  - 'review'  -> enrich_target=False, segment='review' (serves-from-elsewhere /
                 online-only / city-mismatch / ambiguous medical-vs-developmental)
                 KEPT in dataset, surfaced at GATE 2 for human decision (NOT dropped)
  - 'public'  -> DROPPED from dataset; name recorded in state['public_noted'] as
                 concept-node material (public districts/charters are out of scope)
Counts (by_subcategory/by_city/entity_kind) are computed over enrich_target rows.
Idempotent per batch_index.
"""
import json, sys, re, os

COM = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(COM, 'tmp-agent-mapped-fs.json')
STATE = os.path.join(COM, 'tmp-agent-mapped-fs-state.json')

CANON = ['Palm Springs','Palm Desert','La Quinta','Rancho Mirage','Cathedral City',
         'Indio','Coachella','Desert Hot Springs','Indian Wells','Thousand Palms',
         'Bermuda Dunes','Thermal']

# Public/out-of-scope detector: district-operated or public charter -> dropped,
# but the NAME is preserved as concept-node material for the report session.
PUBLIC_RE = re.compile(r'\b(psusd|dsusd|cvusd|unified school district|school district|'
                       r'public charter|charter school|head start)\b', re.I)

# Red flags in a candidate note that indicate NO physical campus in the scope city
# (serves the area from elsewhere / online-only / unverified / ambiguous-medical).
# Over-inclusive on purpose — 'review' rows are surfaced for human decision, not deleted.
FLAG_SUBSTR = [
    'no physical', 'no confirmed local', 'no local campus', 'no campus', 'no local location',
    'no physical location', 'no confirmed campus', 'serves cv', 'serves the valley',
    'serves coachella', 'based elsewhere', 'based outside', 'online only', 'online-only',
    'online tutoring', 'virtual only', 'virtual-only', 'mobile only', 'in-home only',
    'in home only', 'travels to', 'travelling', 'traveling program', 'operate remotely',
    'remotely', 'headquartered', 'hq in', 'hq appears', 'based in los angeles', 'based in san diego',
    'based in riverside', 'no confirmed campus', 'campus unconfirmed',
    'office not confirmed', 'campus not confirmed', 'location unclear', 'presence unclear',
    'ambiguous: medical', 'ambiguous medical', 'medical vs developmental', '(not palm',
    '(not rancho', '(not la quinta', '(not indio', '(not palm desert',
]
FLAG_RE = re.compile(r'no\s+[\w\s\-]{0,30}?(campus|location|address)', re.I)

# Licensed family child-care HOME detector (GATE-1 disposition A): residential
# operations enumerable only via the state licensing registry (CDSS), not a web
# sweep. Carved OUT of the business census as context (segment='family_home_daycare',
# mirrors H&RE remote_operator) — membership is NOT conditioned on web presence;
# the segment is defined out for a stated structural reason. Registry enumeration
# is disclosed future verification-leg work.
HOME_RE = re.compile(r'family\s+(child\s?care|day\s?care)|(child\s?care|day\s?care)\s+home|'
                     r'home\s+(child\s?care|day\s?care)|licensed\s+family\s+(child|day)', re.I)

def triage(row):
    """Return ('ok'|'review'|'public'|'family_home', reason)."""
    name = row.get('name','') or ''
    note = (row.get('note') or '').lower()
    # public detection fires on NAME ONLY — a private org whose note merely mentions
    # a district/charter partnership (e.g. "PSUSD vendor") is in scope, not public.
    if PUBLIC_RE.search(name):
        return 'public', 'public district/charter'
    # family child-care home carve-out (definitional, BEFORE address/note checks —
    # a home IS a physical location, but the segment is defined out of the census).
    if HOME_RE.search(name) or HOME_RE.search(note):
        return 'family_home', 'licensed family child-care home (CDSS-registry-enumerable, not web-sweep)'
    city = row.get('city',''); addr = row.get('address_hint') or ''
    addr_cities = [x for x in CANON if x.lower() in addr.lower()]
    if addr_cities:
        if city in addr_cities:
            return 'ok', ''                       # confirmed physical campus in assigned city
        return 'review', 'address in ' + addr_cities[0]
    hits = [s for s in FLAG_SUBSTR if s in note]
    if not hits and FLAG_RE.search(note):
        hits = [FLAG_RE.search(note).group(0)]
    if hits:
        return 'review', '; '.join(hits[:2])
    return 'ok', ''

def canon_city(c):
    c = (c or '').replace(', CA','').replace(',CA','').strip()
    for x in CANON:
        if c.lower() == x.lower():
            return x
    for x in CANON:
        if x.lower() in c.lower():
            return x
    return c

def norm_name(n):
    return re.sub(r'[^a-z0-9]', '', (n or '').lower())

# entity_kind: orchestrator heuristic (zero worker cost). campus (default) |
# program_brand (named program operating its own brand inside a larger facility —
# mirrors H&RE team_brand) | solo (single-practitioner person-brand).
PROGRAM_SIG = ['named program', 'program inside', 'inside a', 'inside the', 'within a',
               'within the', 'operates inside', 'operates within', 'at the resort',
               'at the club', 'housed in', 'hosted at', 'program at', 'academy at',
               'inside resort', 'within resort', 'brand inside']
COMPANY_TOK = ['school','academy','preschool','montessori','waldorf','learning','childcare',
               'daycare','day care','center','centre','kids','children','child','youth',
               'tutoring','kumon','mathnasium','sylvan','huntington','dance','music','arts',
               'sports','tennis','golf','gymnastics','swim','soccer','camp','christian',
               'catholic','adventist','lutheran','college prep','prep','ymca','boys','girls',
               'club','therapy','aba','institute','studio','enrichment','college','university',
               'kindercare','goddard','primrose','la petite','head start','montessori']
PERSON_RE = re.compile(r"^[A-Z][a-z]+\s+[A-Z][a-z\.\']+(\s+[A-Z][a-z]+)?$")

VENUE_SUBCATS = ('youth sports academies & programs',
                 'arts, music & performing-arts education for youth',
                 'camps & after-school programs')
VENUE_DASH = re.compile(r' [—–] ')   # spaced em/en dash: "Venue — Program"

def entity_kind(row):
    name = (row.get('name') or '').strip()
    nl = name.lower(); note = (row.get('note') or '').lower()
    sub = row.get('subcategory','')
    # GATE-1 disposition D: attraction/venue-hosted programs are the program brand.
    if any(s in note for s in PROGRAM_SIG):
        return 'program_brand'
    if sub in VENUE_SUBCATS and VENUE_DASH.search(name):
        return 'program_brand'
    if PERSON_RE.match(name) and not any(t in nl for t in COMPANY_TOK):
        return 'solo'
    return 'campus'

def load(path, default):
    return json.load(open(path)) if os.path.exists(path) else default

def extract_result(p):
    env = json.load(open(p))
    r = env['result'] if isinstance(env, dict) and 'result' in env else env
    return json.loads(r) if isinstance(r, str) else r

def main():
    out_file, batch_idx = sys.argv[1], int(sys.argv[2])
    res = extract_result(out_file)
    data = load(DATA, [])
    state = load(STATE, {'discovery_batches_done': [], 'tokens_by_batch': {}})

    if batch_idx in state.get('discovery_batches_done', []):
        print(f'batch {batch_idx} already merged — no-op'); return

    existing = {(norm_name(r['name']), r['city']) for r in data}
    added = dup = 0
    for cell in res['cells']:
        for c in cell['candidates']:
            city = canon_city(c.get('city'))
            key = (norm_name(c.get('name')), city)
            if key in existing:
                dup += 1; continue
            existing.add(key)
            data.append({
                'name': c.get('name','').strip(), 'city': city,
                'subcategory': c.get('subcategory','').strip(),
                'website': c.get('website','').strip(),
                'address_hint': c.get('address_hint','').strip(),
                'chain_or_independent': c.get('chain_or_independent','unknown'),
                'license_hint': c.get('license_hint','').strip(),
                'source': c.get('source','').strip(), 'note': c.get('note','').strip(),
                '_disc_batch': batch_idx, '_src_subcat': cell.get('_src_subcat',''),
                '_src_geo': cell.get('_src_geo',''), 'enriched': False,
            })
            added += 1

    # re-triage ALL rows (idempotent, consistent across batches)
    for r in data:
        r['_campus_flag'], r['_flag_reason'] = triage(r)

    # disposition:
    #  - public       -> DROP from dataset; record name as concept-node material
    #  - family_home  -> KEEP as context, segment='family_home_daycare', NOT a target
    #  - review       -> KEEP, enrich_target=False, segment='review' (surfaced at GATE 2)
    #  - ok           -> enrich_target=True
    survivors, public = [], []
    for r in data:
        flag = r['_campus_flag']
        if flag == 'public':
            public.append(r); continue
        if flag == 'family_home':
            r['segment'] = 'family_home_daycare'; r['enrich_target'] = False
        elif flag == 'review':
            r['segment'] = 'review'; r['enrich_target'] = False
        else:
            r.setdefault('segment', ''); r['enrich_target'] = True
        survivors.append(r)
    data = survivors

    # entity_kind stamp on all surviving rows (campus | program_brand | solo)
    for r in data:
        r['entity_kind'] = entity_kind(r)

    targets_rows = [r for r in data if r.get('enrich_target')]
    review_rows = [r for r in data if r.get('segment') == 'review']
    home_rows = [r for r in data if r.get('segment') == 'family_home_daycare']
    by_sub, by_city, kinds = {}, {}, {}
    for r in targets_rows:
        by_sub[r['subcategory']] = by_sub.get(r['subcategory'],0)+1
        by_city[r['city']] = by_city.get(r['city'],0)+1
        kinds[r['entity_kind']] = kinds.get(r['entity_kind'],0)+1

    # accumulate public-noted names across runs (idempotent dedup by name|city)
    seen_pub = {(d['name'], d['city']) for d in state.get('public_noted', [])}
    acc_pub = list(state.get('public_noted', []))
    for r in public:
        if (r['name'], r['city']) not in seen_pub:
            seen_pub.add((r['name'], r['city']))
            acc_pub.append({'name':r['name'],'city':r['city'],'subcategory':r.get('subcategory','')})

    state['discovery_batches_done'] = sorted(set(state.get('discovery_batches_done',[]) + [batch_idx]))
    state.setdefault('tokens_by_batch', {})[str(batch_idx)] = res.get('tokens_spent')
    state['rows_total'] = len(data)
    state['enrich_target_count'] = len(targets_rows)
    state['review_count'] = len(review_rows)
    state['family_home_daycare_count'] = len(home_rows)
    state['public_noted_count'] = len(acc_pub)
    state['by_subcategory'] = by_sub
    state['by_city'] = by_city
    state['entity_kind_counts'] = kinds
    state['review_rows'] = [{'name':r['name'],'city':r['city'],'subcategory':r['subcategory'],
                             'reason':r['_flag_reason'],'note':r.get('note','')} for r in review_rows]
    state['family_home_daycare_rows'] = [{'name':r['name'],'city':r['city']} for r in home_rows]
    state['public_noted'] = acc_pub

    json.dump(data, open(DATA,'w'), indent=0)
    json.dump(state, open(STATE,'w'), indent=2)
    print(f'batch {batch_idx}: +{added} new, {dup} cross-cell dups dropped')
    print(f'  rows now {len(data)} = {len(targets_rows)} enrich-targets + {len(review_rows)} review + {len(home_rows)} family_home (context) | {len(acc_pub)} public-noted (dropped)')
    print(f'  entity_kind: {json.dumps(kinds)}')
    print('  by_subcategory (enrich targets):', json.dumps(by_sub, ensure_ascii=False))
    print('  by_city (enrich targets):', json.dumps(by_city, ensure_ascii=False))

if __name__ == '__main__':
    main()
