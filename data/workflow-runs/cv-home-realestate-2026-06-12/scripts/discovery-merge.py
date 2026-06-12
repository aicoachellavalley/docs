#!/usr/bin/env python3
"""HRE discovery merge/checkpoint. Reusable across discovery batches.
Usage: python3 tmp-hre-merge.py <batch_task_output_file> <batch_index>

Reads the workflow task-output envelope, normalizes + dedups candidates against
the on-disk scratch (tmp-agent-mapped-hre.json), appends new rows with provenance,
then RE-TRIAGES every row by its note into office-confirmed (_office_flag='ok')
vs serves-from-elsewhere/phantom/cloud (_office_flag='review'). Counts are computed
over 'ok' rows only; 'review' rows are preserved in the dataset for GATE-2 human
review (entity-definition: one row per business per city of PHYSICAL office).
Idempotent per batch_index.
"""
import json, sys, re, os

COM = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(COM, 'tmp-agent-mapped-hre.json')
STATE = os.path.join(COM, 'tmp-agent-mapped-hre-state.json')

CANON = ['Palm Springs','Palm Desert','La Quinta','Rancho Mirage','Cathedral City',
         'Indio','Coachella','Desert Hot Springs','Indian Wells','Thousand Palms',
         'Bermuda Dunes','Thermal']

# Red flags in a candidate note that indicate NO physical office in the scope
# city (the brand serves the area from another city / is cloud-only / unverified).
# Over-inclusive on purpose — 'review' rows are surfaced for human decision, not deleted.
FLAG_SUBSTR = [
    'no physical', 'cloud-based', 'no confirmed local office', 'no local physical office',
    'no confirmed local', 'no office address', 'no local office', 'no office',
    'remotely', 'operate remotely', 'may operate remotely', 'field team',
    'national operator with local field', 'office is palm', 'office is rancho',
    'but office is', 'office city is', 'primary office in', 'primary office at',
    'primary retail office', 'primary confirmed office is', 'headquartered', 'hq in',
    'hq appears', 'office not confirmed', 'office address found', 'office presence unclear',
    'presence unclear', 'office location unclear', 'office unclear', 'needs verification',
    'agents likely operate out of', 'agents active in', 'address from search snippet',
    'serves cathedral city', '(not palm', '(not rancho', '(not la quinta', '(not indio',
    'verify — may be', 'may be palm springs', 'included because serves',
]
FLAG_RE = re.compile(r'no\s+[\w\s\-]{0,30}?(office|branch)', re.I)

def office_flag(row):
    """Return ('ok'|'review', reason). Address-confirms-in-city wins; address-in-
    other-city flags; else fall back to note red flags."""
    city = row.get('city',''); note = (row.get('note') or '').lower(); addr = row.get('address_hint') or ''
    addr_cities = [x for x in CANON if x.lower() in addr.lower()]
    if addr_cities:
        if city in addr_cities:
            return 'ok', ''                       # confirmed physical suite in the assigned city
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

# entity_kind: orchestrator heuristic (zero worker cost). office (default) |
# team_brand (named team operating within a brokerage) | solo (person-name brand).
TEAM_SIG = ['team within', 'team brand', 'operates under', 'operating team',
            'operate under', 'team is the operating', 'within bennion', 'within keller',
            'within compass', 'within coldwell', 'within berkshire', 'within bhhs',
            'group operates', 'team within keller']
COMPANY_TOK = ['realty','homes','properties','property','group','company',' co ','co.',
               'inc','llc','management','mgmt','title','escrow','mortgage','lending',
               'loans','inspection','appraisal','appraisers','rentals','vacation',
               'real estate','re/max','remax','keller williams','coldwell','compass',
               'sotheby','berkshire','windermere','century','exp realty','homesmart',
               'the agency','equity union','harcourts','associates','associa','powerstone',
               'realtors','brokers','brokerage','bank','financial','services','desert']
PERSON_RE = re.compile(r"^[A-Z][a-z]+\s+[A-Z][a-z\.\']+(\s+[A-Z][a-z]+)?$")

def entity_kind(row):
    name = (row.get('name') or '').strip()
    nl = name.lower(); note = (row.get('note') or '').lower()
    if nl.endswith(' team') or any(s in note for s in TEAM_SIG):
        return 'team_brand'
    if 'within ' in note and 'team' in note:
        return 'team_brand'
    if PERSON_RE.match(name) and not any(t in nl for t in COMPANY_TOK):
        return 'solo'
    if '& associates' in nl and re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', name):
        return 'solo'
    return 'office'

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
        r['_office_flag'], r['_flag_reason'] = office_flag(r)

    # disposition of review rows (per GATE-2 go):
    #  - STR/vacation-rental review NOT 'address in' -> keep as segment=remote_operator (context, no enrich)
    #  - everything else review (brokerage phantoms, 'address in' city-duplicates) -> DROP entirely
    survivors, dropped = [], []
    for r in data:
        if r['_office_flag'] == 'review':
            is_str = 'vacation rental' in r['subcategory'].lower()
            if is_str and not r['_flag_reason'].startswith('address in'):
                r['segment'] = 'remote_operator'; r['enrich_target'] = False
                survivors.append(r)
            else:
                dropped.append(r)
        else:
            r.setdefault('segment', ''); r['enrich_target'] = True
            survivors.append(r)
    data = survivors

    # entity_kind stamp on all surviving rows (office | team_brand | solo)
    for r in data:
        r['entity_kind'] = entity_kind(r)

    targets_rows = [r for r in data if r.get('enrich_target')]
    remote_rows = [r for r in data if r.get('segment') == 'remote_operator']
    by_sub, by_city, kinds = {}, {}, {}
    for r in targets_rows:
        by_sub[r['subcategory']] = by_sub.get(r['subcategory'],0)+1
        by_city[r['city']] = by_city.get(r['city'],0)+1
        kinds[r['entity_kind']] = kinds.get(r['entity_kind'],0)+1

    # accumulate dropped-row audit across runs (idempotent dedup by name|city)
    seen_drop = {(d['name'], d['city']) for d in state.get('dropped_rows', [])}
    acc_drop = list(state.get('dropped_rows', []))
    for r in dropped:
        if (r['name'], r['city']) not in seen_drop:
            seen_drop.add((r['name'], r['city']))
            acc_drop.append({'name':r['name'],'city':r['city'],'subcategory':r['subcategory'],'reason':r['_flag_reason']})

    state['discovery_batches_done'] = sorted(set(state.get('discovery_batches_done',[]) + [batch_idx]))
    state.setdefault('tokens_by_batch', {})[str(batch_idx)] = res.get('tokens_spent')
    state['rows_total'] = len(data)
    state['enrich_target_count'] = len(targets_rows)
    state['remote_operator_count'] = len(remote_rows)
    state['dropped_count'] = len(acc_drop)
    state['by_subcategory'] = by_sub
    state['by_city'] = by_city
    state['entity_kind_counts'] = kinds
    state['dropped_rows'] = acc_drop
    state['remote_operators'] = [{'name':r['name'],'city':r['city']} for r in remote_rows]

    json.dump(data, open(DATA,'w'), indent=0)
    json.dump(state, open(STATE,'w'), indent=2)
    print(f'batch {batch_idx}: +{added} new, {dup} cross-cell dups dropped')
    print(f'  rows now {len(data)} = {len(targets_rows)} enrich-targets + {len(remote_rows)} remote_operator (context) | {len(acc_drop)} dropped (cumulative)')
    print(f'  entity_kind: {json.dumps(kinds)}')
    print('  by_subcategory (enrich targets):', json.dumps(by_sub))

if __name__ == '__main__':
    main()
