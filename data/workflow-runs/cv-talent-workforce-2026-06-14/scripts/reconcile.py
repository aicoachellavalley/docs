#!/usr/bin/env python3
"""GATE-2 reconcile for the T&W discovery dataset (one-shot, auditable, idempotent).
Backs up tmp-agent-mapped-tw.json -> .prereconcile.json, then applies explicit actions:

  MERGE     same-city name-variant clusters -> one row (keep richest, union note/website)
  DROP      out-of-scope + CVEP/ERC infra rows that are ALREADY context (no dup in enrich)
  RECLASS   business-dev nonprofits -> econ_dev context (per Gate-1 ruling: convening/
            funder/business-dev orgs are context, not workforce businesses)
  PROMOTE   web-visible FLC review row -> enrich-target (Gate-1 FLC promotion bar)
  FLC-REGIME per-row credential_regime override: a promoted/surfaced FLC is CREDENTIALED
            (DIR LC §1684) even though the staffing subcat is unregulated -> keeps the
            series-first split accurate at the row level.

Match keys are NORMALIZED-substring (city, key) to avoid exact-name typos. Logs every action.
"""
import json, os, re, shutil

COM = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(COM, 'tmp-agent-mapped-tw.json')
BACKUP = os.path.join(COM, 'tmp-agent-mapped-tw.prereconcile.json')

def norm(n): return re.sub(r'[^a-z0-9]', '', (n or '').lower())
def filled(r): return sum(1 for v in r.values() if v not in ('', None, [], 'unknown'))

# (city, normalized-substring) clusters -> merge all matching enrich rows into one
MERGE = [
    ('Palm Desert', 'seekpersonnel'),
    ('Palm Desert', 'milaninstitute'),
    ('Palm Desert', 'fusionworkplaces'),
    ('Palm Desert', 'spaces'),
    ('Indian Wells', 'propersolutions'),
    ('Indian Wells', 'roberthalf'),
    ('Indio', 'boulevardworkspace'),
    ('La Quinta', 'bbsi'),
    ('Coachella', 'centerforemploymenttraining'),
    ('La Quinta', 'atworkpersonnel'),
    ('Palm Springs', 'regus'),
    ('Indio', 'coachellavalleyrescuemission'),
]
# DROP: (normalized-substring[, city]) — out-of-scope or CVEP/ERC infra already in context
# NOTE: 'clearpoint' rows are NO-LOCAL-OFFICE review rows (one plausibly an in-scope
# Human-Capital/HR firm) — left in the REVIEW bucket per §5.1, not dropped.
DROP_SUBSTR = ['ihub', 'entrepreneurialresourcecenter']
DROP_WF_CVEP = 'coachellavalleyeconomicpartnership'   # CVEP rows mis-filed as workforce-dev
# RECLASS to econ_dev context
RECLASS_ECON = ['onefuture', 'smallbusinessdevelopment', 'womensbusinesscenter']
# PROMOTE FLC review -> enrich
PROMOTE = ['zepeda']
# FLC detection -> credentialed regime override
FLC_SUBSTR = ['farmlabor', 'laborcontract', 'agrolabor']

def main():
    shutil.copy(DATA, BACKUP)
    data = json.load(open(DATA))
    log = []

    # 1) MERGE variant clusters (enrich rows only)
    for city, key in MERGE:
        grp = [r for r in data if r.get('enrich_target') and r['city'] == city and key in norm(r['name'])]
        if len(grp) < 2:
            if len(grp) == 1: continue
            log.append(f'MERGE  [{city}/{key}] -> 0 matches (skip)'); continue
        keep = max(grp, key=filled)
        for r in grp:
            if r is keep: continue
            if not keep.get('website') and r.get('website'): keep['website'] = r['website']
            if not keep.get('address_hint') and r.get('address_hint'): keep['address_hint'] = r['address_hint']
            extra = (r.get('note') or '').strip()
            if extra and extra not in (keep.get('note') or ''):
                keep['note'] = ((keep.get('note') or '') + ' | ' + extra).strip(' |')
            data.remove(r)
        log.append(f'MERGE  [{city}] {len(grp)} -> 1 : kept {keep["name"]!r}')

    # 2) DROP out-of-scope / context-dup rows
    before = len(data)
    kept = []
    for r in data:
        nn = norm(r['name'])
        if any(s in nn for s in DROP_SUBSTR):
            log.append(f'DROP   {r["name"]!r} ({r["city"]}) — out-of-scope/already-context'); continue
        if r.get('subcategory','').startswith('workforce') and nn.startswith(DROP_WF_CVEP):
            log.append(f'DROP   {r["name"]!r} ({r["city"]}) — CVEP, already econ_dev context'); continue
        kept.append(r)
    data = kept

    # 3) RECLASS business-dev nonprofits -> econ_dev context
    for r in data:
        if r.get('enrich_target') and any(s in norm(r['name']) for s in RECLASS_ECON):
            r['segment'] = 'econ_dev'; r['enrich_target'] = False
            r['_office_flag'], r['_flag_reason'] = 'context', 'econ_dev (reclass: business-dev/funder)'
            log.append(f'RECLASS {r["name"]!r} ({r["city"]}) -> econ_dev context')

    # 4) PROMOTE web-visible FLC review rows -> enrich
    for r in data:
        if (not r.get('enrich_target')) and r.get('segment','') == '' and any(s in norm(r['name']) for s in PROMOTE):
            r['enrich_target'] = True
            r['subcategory'] = 'staffing & recruiting agencies'
            r['_office_flag'], r['_flag_reason'] = 'ok', ''
            r['note'] = ((r.get('note') or '') + ' | FLC-licensed (promoted from review per Gate-1 bar)').strip(' |')
            log.append(f'PROMOTE {r["name"]!r} ({r["city"]}) -> enrich-target (FLC)')

    # 5) FLC credential_regime override (per row) + flag
    for r in data:
        if r.get('enrich_target') and any(s in norm(r['name']) for s in FLC_SUBSTR + PROMOTE):
            r['credential_regime'] = 'credentialed'
            r['_credential_subtype'] = 'FLC'
            if 'flc' not in (r.get('note') or '').lower():
                r['note'] = ((r.get('note') or '') + ' | FLC-licensed').strip(' |')
            log.append(f'FLC    {r["name"]!r} ({r["city"]}) -> credentialed (FLC override)')

    json.dump(data, open(DATA, 'w'), indent=0)

    # recompute summary
    tg = [r for r in data if r.get('enrich_target')]
    ctx = [r for r in data if r.get('segment')]
    rev = [r for r in data if r.get('segment','') == '' and not r.get('enrich_target')]
    by_sub, by_reg, by_seg = {}, {}, {}
    for r in tg:
        by_sub[r['subcategory']] = by_sub.get(r['subcategory'],0)+1
        by_reg[r['credential_regime']] = by_reg.get(r['credential_regime'],0)+1
    for r in ctx:
        by_seg[r['segment']] = by_seg.get(r['segment'],0)+1
    print('\n'.join(log))
    print('\n=== RECONCILED ===')
    print(f'rows {len(data)} = {len(tg)} enrich-targets + {len(ctx)} context + {len(rev)} review')
    print('by_subcategory:', json.dumps(by_sub, indent=0))
    print('by_credential_regime:', json.dumps(by_reg))
    print('by_context_segment:', json.dumps(by_seg))

if __name__ == '__main__':
    main()
