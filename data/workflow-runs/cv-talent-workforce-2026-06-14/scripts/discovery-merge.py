#!/usr/bin/env python3
"""Talent & Workforce discovery merge/checkpoint. Reusable across discovery batches.
Usage: python3 tmp-tw-merge.py <batch_task_output_file> <batch_index>

Adapted from templates/census/discovery-merge.py (HRE). T&W specifics:
  - CONTEXT segments come from the worker's `segment` field directly
    (public_workforce | econ_dev | farm_labor_contractor) — Gate-1 carve-outs,
    membership NOT conditioned on web visibility. Context rows are kept as
    enrich_target=False; they are the institutional backbone, not business targets.
  - credential_regime is stamped at the SUBCAT level (zero worker cost) so the
    series-first SPLIT (credentialed vs unregulated wing) is computable at
    synthesis. Recon-sourced: CA has NO state staffing/employment-agency license
    (Harbor Compliance) -> staffing & the service subcats = 'unregulated'; trade
    schools (BPPE + trade boards) & FLCs (DIR LC §1684) = 'credentialed'.
  - Pilot discipline: review rows are SURFACED (not dropped) for the stop-gate.
Idempotent per batch_index.
"""
import json, sys, re, os

COM = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(COM, 'tmp-agent-mapped-tw.json')
STATE = os.path.join(COM, 'tmp-agent-mapped-tw-state.json')

CANON = ['Palm Springs','Palm Desert','La Quinta','Rancho Mirage','Cathedral City',
         'Indio','Coachella','Desert Hot Springs','Indian Wells','Thousand Palms',
         'Bermuda Dunes','Thermal']

CONTEXT_SEGMENTS = {'public_workforce', 'econ_dev', 'farm_labor_contractor'}

# credential_regime by canonical enrich subcategory (subcat-level, zero worker cost).
REGIME_BY_SUBCAT = {
    'staffing & recruiting agencies': 'unregulated',
    'adult vocational & trade schools / training providers': 'credentialed',
    'workforce-development & job-readiness service organizations': 'unregulated',
    'coworking & flexible workspace': 'unregulated',
    'career & professional services': 'unregulated',
    'HR outsourcing, PEO & payroll services': 'unregulated',
}
# context-segment regimes (for completeness in computed splits)
REGIME_BY_SEGMENT = {
    'farm_labor_contractor': 'credentialed',  # DIR FLC license, LC §1684
    'public_workforce': 'public',
    'econ_dev': 'n/a',
}

def regime(row):
    seg = row.get('segment') or ''
    if seg in REGIME_BY_SEGMENT:
        return REGIME_BY_SEGMENT[seg]
    return REGIME_BY_SUBCAT.get(row.get('subcategory','').strip(), 'unknown')

# Red flags in a note that indicate NO physical office in the scope city.
# Over-inclusive on purpose — 'review' rows are surfaced, not deleted.
# (Per F&S fix #2: no bare 'verify' flag — workers over-append it.)
FLAG_SUBSTR = [
    'no physical', 'no confirmed local office', 'no local physical office',
    'no confirmed local', 'no office address', 'no local office', 'no office',
    'cloud-based', 'operate remotely', 'remote only', 'fully remote', 'virtual only',
    'serves cv, based elsewhere', 'serves cv based elsewhere', 'based elsewhere',
    'no confirmed local presence', 'primary office in', 'primary office at',
    'headquartered', 'hq in', 'office not confirmed', 'office location unclear',
    'office presence unclear', 'presence unclear', 'no confirmed campus',
    'serves the valley from', '(not palm', '(not rancho', '(not la quinta', '(not indio',
]
# Exclusion detector matches the row NAME only (F&S fix #1), never the note.
EXCLUDE_NAME_RE = re.compile(r'\b(talent agency|modeling agency|model & talent|casting|booking agency)\b', re.I)

def office_flag(row):
    """('ok'|'review', reason). Context rows are never 'review' (handled before this)."""
    city = row.get('city',''); note = (row.get('note') or '').lower(); addr = row.get('address_hint') or ''
    addr_cities = [x for x in CANON if x.lower() in addr.lower()]
    if addr_cities:
        if city in addr_cities:
            return 'ok', ''
        return 'review', 'address in ' + addr_cities[0]
    hits = [s for s in FLAG_SUBSTR if s in note]
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

# entity_kind: orchestrator heuristic (zero worker cost). T&W variant:
#   branch (national/regional franchise local office) | solo (person-name brand) | office (default)
BRANCH_TOK = ['express employment','robert half','appleone','spherion','manpower','kelly services',
              'adecco','randstad','labor finders','atwork','remedy','volt','aerotek','adp','paychex',
              'insperity','trinet','regus','spaces','wework','office evolution','kumon','mathnasium',
              'fusion workplaces','barrett business','staffmark']
COMPANY_TOK = ['staffing','recruiting','recruit','employment','personnel','workforce','talent',
               'agency','agencies','services','solutions','group','associates','consulting','partners',
               'school','college','academy','institute','training','workplaces','coworking','payroll',
               'hr','peo','company',' co ','co.','inc','llc','corp','center','centre']
PERSON_RE = re.compile(r"^[A-Z][a-z]+\s+[A-Z][a-z\.\']+(\s+[A-Z][a-z]+)?$")

def entity_kind(row):
    name = (row.get('name') or '').strip(); nl = name.lower()
    if any(t in nl for t in BRANCH_TOK) or (row.get('chain_or_independent') == 'chain'):
        return 'branch'
    if PERSON_RE.match(name) and not any(t in nl for t in COMPANY_TOK):
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
    added = dup = excluded = 0
    for cell in res['cells']:
        for c in cell['candidates']:
            name = (c.get('name') or '').strip()
            seg = (c.get('segment') or '').strip()
            # hard-exclusion detector on NAME only (entertainment talent agencies)
            if not seg and EXCLUDE_NAME_RE.search(name):
                excluded += 1; continue
            city = canon_city(c.get('city'))
            key = (norm_name(name), city)
            if key in existing:
                dup += 1; continue
            existing.add(key)
            data.append({
                'name': name, 'city': city,
                'subcategory': (c.get('subcategory') or '').strip(),
                'segment': seg if seg in CONTEXT_SEGMENTS else '',
                'website': (c.get('website') or '').strip(),
                'address_hint': (c.get('address_hint') or '').strip(),
                'chain_or_independent': c.get('chain_or_independent','unknown'),
                'license_hint': (c.get('license_hint') or '').strip(),
                'source': (c.get('source') or '').strip(), 'note': (c.get('note') or '').strip(),
                '_disc_batch': batch_idx, '_src_subcat': cell.get('_src_subcat',''),
                '_src_geo': cell.get('_src_geo',''), '_src_mode': cell.get('_src_mode',''),
                'enriched': False,
            })
            added += 1

    # stamp regime + entity_kind on ALL rows (idempotent)
    for r in data:
        r['credential_regime'] = regime(r)
        r['entity_kind'] = entity_kind(r)

    # disposition: context rows (segment set) = enrich_target False, never triaged.
    # enrich rows: office_flag triage; review rows SURFACED (kept, flagged) for the gate.
    for r in data:
        if r.get('segment') in CONTEXT_SEGMENTS:
            r['enrich_target'] = False
            r['_office_flag'], r['_flag_reason'] = 'context', r['segment']
        else:
            r['_office_flag'], r['_flag_reason'] = office_flag(r)
            r['enrich_target'] = (r['_office_flag'] == 'ok')  # review rows excluded from target count, retained in dataset

    targets_ok   = [r for r in data if r.get('enrich_target')]
    review_rows  = [r for r in data if r.get('segment') == '' and r['_office_flag'] == 'review']
    context_rows = [r for r in data if r.get('segment') in CONTEXT_SEGMENTS]

    by_sub, by_city, kinds, by_regime, by_segment = {}, {}, {}, {}, {}
    for r in targets_ok:
        by_sub[r['subcategory']] = by_sub.get(r['subcategory'],0)+1
        by_city[r['city']] = by_city.get(r['city'],0)+1
        kinds[r['entity_kind']] = kinds.get(r['entity_kind'],0)+1
        by_regime[r['credential_regime']] = by_regime.get(r['credential_regime'],0)+1
    for r in context_rows:
        by_segment[r['segment']] = by_segment.get(r['segment'],0)+1

    state['discovery_batches_done'] = sorted(set(state.get('discovery_batches_done',[]) + [batch_idx]))
    state.setdefault('tokens_by_batch', {})[str(batch_idx)] = res.get('tokens_spent')
    state['rows_total'] = len(data)
    state['enrich_target_count'] = len(targets_ok)
    state['review_count'] = len(review_rows)
    state['context_count'] = len(context_rows)
    state['by_subcategory'] = by_sub
    state['by_city'] = by_city
    state['by_credential_regime'] = by_regime
    state['by_context_segment'] = by_segment
    state['entity_kind_counts'] = kinds
    state['excluded_talent_agencies'] = state.get('excluded_talent_agencies', 0) + excluded
    state['review_rows'] = [{'name':r['name'],'city':r['city'],'subcategory':r['subcategory'],'reason':r['_flag_reason'],'note':r['note']} for r in review_rows]

    json.dump(data, open(DATA,'w'), indent=0)
    json.dump(state, open(STATE,'w'), indent=2)
    print(f'batch {batch_idx}: +{added} new, {dup} cross-cell dups dropped, {excluded} talent-agency exclusions')
    print(f'  rows now {len(data)} = {len(targets_ok)} enrich-targets(ok) + {len(review_rows)} review(surfaced) + {len(context_rows)} context')
    print(f'  by_subcategory (enrich-targets):', json.dumps(by_sub))
    print(f'  by_credential_regime (enrich-targets):', json.dumps(by_regime))
    print(f'  by_context_segment:', json.dumps(by_segment))
    print(f'  entity_kind:', json.dumps(kinds))

if __name__ == '__main__':
    main()
