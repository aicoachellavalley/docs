#!/usr/bin/env python3
"""V2 regen stats for "Agent-Mapped: Food & Dining in the Coachella Valley".

NUMERIC DISCIPLINE: every figure in the V2 report MUST come from this script's
output (v2-report-stats.json), computed from the canonical datasets on disk.

CONSISTENCY GATE (hard): the computed dining figures MUST match the H&RE
report's published benchmark row — 859 inspected / 43 (5.0%) gap /
201 of 707 (28.4%) blocked / 0 of 554 structured data — and the cumulative
row (1,176 inspected / 3 of 780 = 0.4% / 267 of 1,000 = 26.7%). Mismatch
exits non-zero; two AICV reports may never disagree silently.

Inputs:
  ../dining-segmented-v2.json            — canonical dining dataset (1,423 rows)
  ../state-segmented-v2.json             — state buckets
  ../segments-classification-2026-06-11.json — human-gated decision record
  ../../cv-home-realestate-2026-06-12/cv-hre-census-final.json — for cumulative
"""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
doc = json.load(open(os.path.join(HERE, '..', 'dining-segmented-v2.json')))
ROWS = doc['rows'] if isinstance(doc, dict) else doc
STATE = json.load(open(os.path.join(HERE, '..', 'state-segmented-v2.json')))
SEG = json.load(open(os.path.join(HERE, '..', 'segments-classification-2026-06-11.json')))
HRE = json.load(open(os.path.join(
    HERE, '..', '..', 'cv-home-realestate-2026-06-12', 'cv-hre-census-final.json')))

def pct(n, d, nd=1):
    return round(100 * n / d, nd) if d else None

def canon_city(c):
    return (c or '').replace(', CA', '').replace(',CA', '').strip()

def tf(rows, field):
    c = Counter((r.get(field) or 'unknown') for r in rows)
    t, f = c.get('true', 0), c.get('false', 0)
    return {'true': t, 'false': f, 'checkable': t + f,
            'undetermined': sum(c.values()) - t - f}

out = {'_provenance': {
    'script': 'stats/v2-report-stats.py',
    'dataset': 'dining-segmented-v2.json',
    'decision_record': 'segments-classification-2026-06-11.json',
    'generated_for': 'agent-mapped-food-dining-coachella-valley V2 regen',
}}

# ── Census structure & locked denominators (self-proving) ────────────────
indep = [r for r in ROWS if r.get('chain_or_independent') == 'independent']
chains = [r for r in ROWS if r.get('chain_or_independent') == 'chain']
other_ci = len(ROWS) - len(indep) - len(chains)

inspected = [r for r in indep if r.get('enriched')]
mapped = [r for r in indep if r.get('in_dining_map')]
seg_counts = Counter((r.get('segment') or '') for r in indep)
mobile_seg = seg_counts.get('mobile', 0)
catering_seg = seg_counts.get('catering_only', 0)
dupdef_seg = sum(v for k, v in seg_counts.items()
                 if k and ('dup' in k or 'defunct' in k))
fixed_loc = len(mapped) + len(inspected)
identity_sum = fixed_loc + mobile_seg + catering_seg + dupdef_seg

out['census'] = {
    'rows_total': len(ROWS),
    'independent_raw': len(indep),
    'chains': len(chains),
    'neither_chain_nor_independent': other_ci,
    'locked_denominators': {
        'fixed_location_independents': fixed_loc,
        'corpus_mapped': len(mapped),
        'inspected': len(inspected),
        'mobile': mobile_seg,
        'catering_only': catering_seg,
        'duplicate_or_defunct': dupdef_seg,
        'identity_check': {
            'sum': identity_sum, 'equals_raw_independents': identity_sum == len(indep)},
        'coverage': {'inspected_plus_mapped': fixed_loc,
                     'inspected_pct_of_nonmapped_fixed': pct(len(inspected), fixed_loc - len(mapped))},
    },
    'segment_values_on_independents': dict(seg_counts),
    'by_city': dict(Counter(canon_city(r.get('city')) for r in ROWS).most_common()),
    'corroborated_2plus_sources': {
        'n': sum(1 for r in ROWS if isinstance(r.get('sources'), list) and len(r['sources']) >= 2),
        'of': len(ROWS)},
    'operating_status': dict(Counter((r.get('currently_open') or 'unknown') for r in ROWS)),
    'state_buckets': {k: len(v) for k, v in STATE.items()},
}
out['census']['corroborated_2plus_sources']['pct'] = pct(
    out['census']['corroborated_2plus_sources']['n'], len(ROWS), 0)

# ── Decision record (human gate) ─────────────────────────────────────────
out['decision_record'] = {
    'rows_classified': len(SEG['classification']),
    'human_overrides': sum(1 for r in SEG['classification']
                           if 'HUMAN OVERRIDE' in (r.get('segment_note') or '')),
}

# ── Full-universe visibility findings (n = inspected) ────────────────────
n = len(inspected)
vs = Counter(r.get('agent_visibility_score') for r in inspected)
gap_n = vs.get('low', 0) + vs.get('invisible', 0)
crawl = tf(inspected, 'agent_crawlable')
sd = tf(inspected, 'has_structured_data')
out['visibility_full'] = {
    'inspected': n,
    'score': {k: vs.get(k, 0) for k in ('high', 'medium', 'low', 'invisible')},
    'gap_low_plus_invisible': {'n': gap_n, 'of': n, 'pct': pct(gap_n, n)},
    'crawler_blocked': {'n': crawl['false'], 'checkable': crawl['checkable'],
                        'pct': pct(crawl['false'], crawl['checkable']),
                        'allow': crawl['true'], 'undetermined': crawl['undetermined']},
    'structured_data_present': {'n': sd['true'], 'checkable': sd['checkable'],
                                'pct': pct(sd['true'], sd['checkable']),
                                'undetermined': sd['undetermined']},
    'gap_notes_nonempty': sum(1 for r in inspected if (r.get('visibility_gap_note') or '').strip()),
}

# ── Cross-category (recomputed from H&RE dataset for self-containment) ───
h_enr = [r for r in HRE if r.get('enriched')]
hn = len(h_enr)
hvs = Counter(r.get('agent_visibility_score') for r in h_enr)
h_gap = hvs.get('low', 0) + hvs.get('invisible', 0)
h_crawl = tf(h_enr, 'agent_crawlable')
h_sd = tf(h_enr, 'has_structured_data')
out['hre_benchmark'] = {
    'inspected': hn,
    'gap': {'n': h_gap, 'pct': pct(h_gap, hn)},
    'crawler_blocked': {'n': h_crawl['false'], 'checkable': h_crawl['checkable'],
                        'pct': pct(h_crawl['false'], h_crawl['checkable'])},
    'structured_data_present': {'n': h_sd['true'], 'checkable': h_sd['checkable'],
                                'pct': pct(h_sd['true'], h_sd['checkable'])},
}
out['cumulative'] = {
    'inspected': n + hn,
    'structured_data_present': {'n': sd['true'] + h_sd['true'],
                                'checkable': sd['checkable'] + h_sd['checkable'],
                                'pct': pct(sd['true'] + h_sd['true'], sd['checkable'] + h_sd['checkable'])},
    'crawler_blocked': {'n': crawl['false'] + h_crawl['false'],
                        'checkable': crawl['checkable'] + h_crawl['checkable'],
                        'pct': pct(crawl['false'] + h_crawl['false'],
                                   crawl['checkable'] + h_crawl['checkable'])},
}

# ── CONSISTENCY GATE vs the published H&RE benchmark row ─────────────────
published = {
    'dining_inspected': 859,
    'dining_gap_n': 43, 'dining_gap_pct': 5.0,
    'dining_blocked_n': 201, 'dining_blocked_checkable': 707, 'dining_blocked_pct': 28.4,
    'dining_sd_n': 0, 'dining_sd_checkable': 554,
    'cumulative_inspected': 1176,
    'cumulative_sd_n': 3, 'cumulative_sd_checkable': 780, 'cumulative_sd_pct': 0.4,
    'cumulative_blocked_n': 267, 'cumulative_blocked_checkable': 1000, 'cumulative_blocked_pct': 26.7,
}
computed = {
    'dining_inspected': n,
    'dining_gap_n': gap_n, 'dining_gap_pct': pct(gap_n, n),
    'dining_blocked_n': crawl['false'], 'dining_blocked_checkable': crawl['checkable'],
    'dining_blocked_pct': pct(crawl['false'], crawl['checkable']),
    'dining_sd_n': sd['true'], 'dining_sd_checkable': sd['checkable'],
    'cumulative_inspected': out['cumulative']['inspected'],
    'cumulative_sd_n': out['cumulative']['structured_data_present']['n'],
    'cumulative_sd_checkable': out['cumulative']['structured_data_present']['checkable'],
    'cumulative_sd_pct': out['cumulative']['structured_data_present']['pct'],
    'cumulative_blocked_n': out['cumulative']['crawler_blocked']['n'],
    'cumulative_blocked_checkable': out['cumulative']['crawler_blocked']['checkable'],
    'cumulative_blocked_pct': out['cumulative']['crawler_blocked']['pct'],
}
mismatches = {k: {'published': published[k], 'computed': computed[k]}
              for k in published if published[k] != computed[k]}
out['consistency_gate'] = {
    'target': 'H&RE report Finding 3 benchmark row (live since 2026-06-12)',
    'pass': not mismatches,
    'mismatches': mismatches,
}

with open(os.path.join(HERE, 'v2-report-stats.json'), 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(json.dumps(out, indent=2, ensure_ascii=False))
if mismatches:
    print('\n*** CONSISTENCY GATE: FAIL ***', file=sys.stderr)
    sys.exit(1)
print('\nCONSISTENCY GATE: PASS')
