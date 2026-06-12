#!/usr/bin/env python3
"""HRE enrichment merge-back + checkpoint. Reusable per enrichment batch.
Usage: python3 tmp-hre-enrich-merge.py <output_file> <batch_index> <usage_tokens> [run_id]

Merges the ~20 enrichment fields onto scratch rows by (_src_name,_src_city),
sets enriched=True, appends journal lines, updates enrichment state with
usage-basis cumulative spend, and checks the 14M session guard at the boundary.
Idempotent per batch_index.
"""
import json, sys, os, re

COM = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(COM, 'tmp-agent-mapped-hre.json')
ESTATE = os.path.join(COM, 'tmp-agent-mapped-hre-enrich-state.json')
JOURNAL = os.path.join(COM, 'tmp-hre-inspection-journal.jsonl')

DISCOVERY_USAGE = 1_174_060   # usage-basis discovery total (304+339+352+179k, from task notifications)
GUARD = 14_000_000

ENRICH_FIELDS = ['full_address','website','currently_open','has_structured_data',
                 'agent_crawlable','agent_visibility_score','visibility_gap_note',
                 'license_id_displayed','license_type_guess','cities_served','specialties',
                 'vacation_rental_flag','year_established_if_stated','team_size_hint',
                 'booking_or_contact_path','chain_or_independent']

def norm(n): return re.sub(r'[^a-z0-9]', '', (n or '').lower())

def extract(p):
    env = json.load(open(p))
    r = env['result'] if isinstance(env, dict) and 'result' in env else env
    return json.loads(r) if isinstance(r, str) else r

def main():
    out_file, bidx = sys.argv[1], int(sys.argv[2])
    usage = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    run_id = sys.argv[4] if len(sys.argv) > 4 else ''
    res = extract(out_file)
    data = json.load(open(DATA))
    st = json.load(open(ESTATE)) if os.path.exists(ESTATE) else {
        'enriched_batches_done': [], 'usage_by_batch': {}, 'enriched_count': 0}

    if bidx in st['enriched_batches_done']:
        print(f'enrich batch {bidx} already merged — no-op'); return

    # index rows by exact (name,city) and normalized fallback
    by_exact = {(r['name'], r['city']): r for r in data}
    by_norm = {(norm(r['name']), norm(r['city'])): r for r in data}

    merged = miss = 0
    jlines = []
    for p in res['enrichment']:
        sn, sc = p.get('_src_name'), p.get('_src_city')
        row = by_exact.get((sn, sc)) or by_norm.get((norm(sn), norm(sc)))
        if not row:
            miss += 1; print(f'  UNMATCHED: {sn!r} / {sc!r}'); continue
        for f in ENRICH_FIELDS:
            if f in p:
                row[f] = p[f]
        row['enriched'] = True
        row['_enrich_batch'] = bidx
        merged += 1
        jl = {k: p.get(k) for k in (['name','city','subcategory'] + ENRICH_FIELDS)}
        jl['_batch'] = bidx; jl['_run_id'] = run_id
        jlines.append(jl)

    # journal append
    with open(JOURNAL, 'a') as jf:
        for jl in jlines:
            jf.write(json.dumps(jl, ensure_ascii=False) + '\n')

    st['enriched_batches_done'] = sorted(set(st['enriched_batches_done'] + [bidx]))
    st['usage_by_batch'][str(bidx)] = usage
    st['enriched_count'] = sum(1 for r in data if r.get('enriched'))
    enrich_usage = sum(st['usage_by_batch'].values())
    session_total = DISCOVERY_USAGE + enrich_usage
    st['enrich_usage_total'] = enrich_usage
    st['session_usage_total'] = session_total

    json.dump(data, open(DATA, 'w'), indent=0)
    json.dump(st, open(ESTATE, 'w'), indent=2)

    target_total = sum(1 for r in data if r.get('enrich_target'))
    print(f'enrich batch {bidx}: merged {merged}/{res["returned"]} returned ({miss} unmatched)')
    print(f'  enriched so far: {st["enriched_count"]}/{target_total} targets')
    print(f'  this batch usage: {usage:,} | enrichment cumulative: {enrich_usage:,} | SESSION TOTAL (disc+enrich): {session_total:,}')
    pct = 100 * session_total / GUARD
    print(f'  GUARD: {session_total:,} / {GUARD:,} = {pct:.1f}%  ' + ('*** OVER 14M — STOP ***' if session_total > GUARD else 'OK'))

if __name__ == '__main__':
    main()
