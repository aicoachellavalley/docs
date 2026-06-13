#!/usr/bin/env python3
"""CV Family & Schooling — post-discovery dedup pass (GATE-1 approved), v2.

AUTO-MERGE (safe): same CITY + same SUBCATEGORY rows whose normalized names
(parens stripped, non-alnum removed) are EQUAL or one is a >=12-char PREFIX of the
other = one entity, punctuation/paren/Inc./brand-suffix variant. Survivor name:
- equal-normalized  -> the LONGER raw name (keeps the parenthetical detail)
- prefix-relationship-> the BASE (shorter-normalized) name (the canonical entity,
  not its longest sub-label). Blanks back-filled from the dropped twin.

SURFACE ONLY (judgment, NOT merged — taken to GATE 2):
- same-city CROSS-SUBCATEGORY same-stem groups (a school + its camp/preschool sub-
  program: 1 campus or N named-program rows? = entity-definition call).
- CROSS-CITY same-stem groups (legit multi-campus vs single-entity city phantom).
Idempotent; operates on tmp-agent-mapped-fs.json + state.
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

def pick(a, b):
    """Return (winner, loser) by NAME canonicality (fields back-filled separately)."""
    na, nb = norm(a['name']), norm(b['name'])
    if na == nb:
        return (a, b) if len(a['name']) >= len(b['name']) else (b, a)   # equal -> longer
    return (a, b) if len(na) <= len(nb) else (b, a)                     # prefix -> base

def main():
    data = json.load(open(DATA))
    state = json.load(open(STATE))
    targets = [r for r in data if r.get('enrich_target')]
    others = [r for r in data if not r.get('enrich_target')]

    # 1. AUTO-MERGE: same city + same subcategory
    groups = {}
    for r in targets:
        groups.setdefault((r['city'], r['subcategory']), []).append(r)
    survivors, merged_audit = [], []
    for _, rows in groups.items():
        kept = []
        for r in rows:
            rn = norm(r['name']); hit = None
            for k in kept:
                if is_dup(rn, norm(k['name'])): hit = k; break
            if hit is None:
                kept.append(r); continue
            win, lose = pick(hit, r)
            for f in ('website', 'license_hint', 'address_hint', 'source', 'note'):
                if not win.get(f) and lose.get(f): win[f] = lose[f]
            win['enrich_target'] = True
            if win is not hit: kept[kept.index(hit)] = win
            merged_audit.append({'kept': win['name'], 'dropped': lose['name'], 'city': lose['city']})
        survivors.extend(kept)

    # 2. SURFACE same-city cross-subcategory same-stem clusters (NOT merged)
    cross_sub = []
    by_city = {}
    for r in survivors:
        by_city.setdefault(r['city'], []).append(r)
    for city, rows in by_city.items():
        used = set()
        for i, a in enumerate(rows):
            if i in used: continue
            clust = [a]
            for j in range(i + 1, len(rows)):
                if j in used: continue
                if is_dup(norm(a['name']), norm(rows[j]['name'])):
                    clust.append(rows[j]); used.add(j)
            if len(clust) > 1 and len({c['subcategory'] for c in clust}) > 1:
                used.add(i)
                cross_sub.append([(c['name'], c['city'], c['subcategory']) for c in clust])

    # 3. SURFACE cross-city same-stem groups (NOT merged)
    stem = {}
    for r in survivors:
        stem.setdefault(norm(r['name'])[:16], []).append((r['name'], r['city'], r['subcategory'], r.get('chain_or_independent')))
    cross_city = [v for v in stem.values() if len({c for _, c, *_ in v}) > 1]

    data = survivors + others
    json.dump(data, open(DATA, 'w'), indent=0)
    tr = [r for r in data if r.get('enrich_target')]
    by_sub, by_city2 = {}, {}
    for r in tr:
        by_sub[r['subcategory']] = by_sub.get(r['subcategory'], 0) + 1
        by_city2[r['city']] = by_city2.get(r['city'], 0) + 1
    state['enrich_target_count'] = len(tr)
    state['by_subcategory'] = by_sub
    state['by_city'] = by_city2
    state['dedup_same_subcat_merged'] = merged_audit
    json.dump(state, open(STATE, 'w'), indent=2)

    print(f'AUTO-MERGED same-city+same-subcat: {len(merged_audit)} dups -> enrich-targets now {len(tr)}')
    for m in merged_audit:
        print(f"   kept '{m['kept']}'  |  dropped '{m['dropped']}'  ({m['city']})")
    print(f'\nSURFACE — same-city CROSS-SUBCAT clusters (GATE-2 judgment): {len(cross_sub)}')
    for g in cross_sub:
        for n, c, s in g: print(f"   {n}  [{c}]  ({s[:24]})")
        print('   --')
    print(f'\nSURFACE — CROSS-CITY same-stem groups (GATE-2 judgment): {len(cross_city)}')
    for g in cross_city:
        for n, c, s, ch in g: print(f"   {n}  [{c}]  ({s[:18]} · {ch})")
        print('   --')

if __name__ == '__main__':
    main()
