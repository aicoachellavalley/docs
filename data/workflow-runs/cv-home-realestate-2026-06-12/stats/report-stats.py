#!/usr/bin/env python3
"""Report stats for "Agent-Mapped: Home & Real Estate in the Coachella Valley".

NUMERIC DISCIPLINE: every number in the published report MUST come from this
script's output (report-stats.json), computed directly from the dataset JSONs
on disk — no recalled figures, no hand-copied numbers from READMEs or prompts.

Inputs (disk is canon):
  ../cv-hre-census-final.json                       — the H&RE census dataset
  ../../cv-food-dining-enrich-2026-06-11/
      dining-segmented-v2.json                      — dining dataset (comparison)
      state-segmented-v2.json                       — dining state (census totals)

Run:  python3 report-stats.py   (writes report-stats.json beside itself)
"""
import json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
HRE = json.load(open(os.path.join(HERE, '..', 'cv-hre-census-final.json')))
_dining_doc = json.load(open(os.path.join(
    HERE, '..', '..', 'cv-food-dining-enrich-2026-06-11', 'dining-segmented-v2.json')))
DINING = _dining_doc['rows'] if isinstance(_dining_doc, dict) else _dining_doc
DINING_STATE = json.load(open(os.path.join(
    HERE, '..', '..', 'cv-food-dining-enrich-2026-06-11', 'state-segmented-v2.json')))

def pct(n, d, nd=1):
    return round(100 * n / d, nd) if d else None

def tf_counts(rows, field):
    """Counts of 'true'/'false'/other for a string-boolean field."""
    c = Counter((r.get(field) or 'unknown') for r in rows)
    t, f = c.get('true', 0), c.get('false', 0)
    return {'true': t, 'false': f, 'checkable': t + f,
            'unknown_or_other': sum(c.values()) - t - f}

def has_license(r):
    v = (r.get('license_id_displayed') or '').strip().lower()
    if v in ('', 'unknown', 'none', 'none-visible', 'n/a'):
        return False
    return bool(re.search(r'\d', v))

out = {'_provenance': {
    'script': 'stats/report-stats.py',
    'hre_dataset': 'cv-hre-census-final.json',
    'dining_dataset': '../cv-food-dining-enrich-2026-06-11/dining-segmented-v2.json',
    'generated_for': 'agent-mapped-home-realestate-coachella-valley report',
}}

# ── H&RE census structure ────────────────────────────────────────────────
enr = [r for r in HRE if r.get('enriched')]
targets = [r for r in HRE if r.get('enrich_target')]
remote = [r for r in HRE if r.get('segment') == 'remote_operator']
n = len(enr)

out['hre_census'] = {
    'rows_total': len(HRE),
    'enrich_targets': len(targets),
    'enriched': n,
    'coverage_pct': pct(n, len(targets)),
    'remote_operator_context_rows': len(remote),
    'remote_operator_names': sorted(r['name'] for r in remote),
    'by_subcategory': dict(Counter(r['subcategory'] for r in enr).most_common()),
    'by_city': dict(Counter(r['city'] for r in enr).most_common()),
    'entity_kind': dict(Counter(r.get('entity_kind') for r in enr)),
    'chain_or_independent': dict(Counter(r.get('chain_or_independent') for r in enr)),
    'currently_open': dict(Counter(r.get('currently_open') for r in enr)),
}

# brokerages&teams decomposed by entity_kind (claim-precision rule)
brk = [r for r in enr if r['subcategory'] == 'residential brokerages & teams']
out['hre_brokerages_decomposition'] = {
    'total': len(brk),
    'entity_kind': dict(Counter(r.get('entity_kind') for r in brk)),
}

# ── H&RE visibility block ────────────────────────────────────────────────
vs = Counter(r.get('agent_visibility_score') for r in enr)
gap_n = vs.get('low', 0) + vs.get('invisible', 0)
crawl = tf_counts(enr, 'agent_crawlable')   # 'false' = blocked
sd = tf_counts(enr, 'has_structured_data')  # 'true' = present
out['hre_visibility'] = {
    'score': {k: vs.get(k, 0) for k in ('high', 'medium', 'low', 'invisible')},
    'gap_low_plus_invisible': {'n': gap_n, 'of': n, 'pct': pct(gap_n, n)},
    'crawler_blocked': {'n': crawl['false'], 'checkable': crawl['checkable'],
                        'pct': pct(crawl['false'], crawl['checkable']),
                        'undetermined': crawl['unknown_or_other']},
    'structured_data_present': {'n': sd['true'], 'checkable': sd['checkable'],
                                'pct': pct(sd['true'], sd['checkable']),
                                'undetermined': sd['unknown_or_other']},
    'gap_notes_nonempty': sum(1 for r in enr if (r.get('visibility_gap_note') or '').strip()),
}

# structured-data: who are the exceptions (named in report if few)
out['hre_structured_data_present_names'] = sorted(
    f"{r['name']} ({r['city']})" for r in enr if r.get('has_structured_data') == 'true')

# ── H&RE license display ─────────────────────────────────────────────────
lic_n = sum(1 for r in enr if has_license(r))
out['hre_license'] = {
    'displayed': {'n': lic_n, 'of': n, 'pct': pct(lic_n, n)},
    'type_guess': dict(Counter(r.get('license_type_guess') for r in enr)),
}
# per-subcategory license display + visibility profile
per_sub = {}
for sub in out['hre_census']['by_subcategory']:
    rows = [r for r in enr if r['subcategory'] == sub]
    sv = Counter(r.get('agent_visibility_score') for r in rows)
    sc = tf_counts(rows, 'agent_crawlable')
    ss = tf_counts(rows, 'has_structured_data')
    sl = sum(1 for r in rows if has_license(r))
    per_sub[sub] = {
        'n': len(rows),
        'by_city_top3': dict(Counter(r['city'] for r in rows).most_common(3)),
        'chain': sum(1 for r in rows if r.get('chain_or_independent') == 'chain'),
        'independent': sum(1 for r in rows if r.get('chain_or_independent') == 'independent'),
        'score': {k: sv.get(k, 0) for k in ('high', 'medium', 'low', 'invisible')},
        'gap_n': sv.get('low', 0) + sv.get('invisible', 0),
        'crawler_blocked': {'n': sc['false'], 'checkable': sc['checkable'],
                            'pct': pct(sc['false'], sc['checkable'])},
        'structured_data': {'n': ss['true'], 'checkable': ss['checkable']},
        'license_displayed': {'n': sl, 'pct': pct(sl, len(rows))},
        'entity_kind': dict(Counter(r.get('entity_kind') for r in rows)),
    }
out['hre_per_subcategory'] = per_sub

# ── H&RE STR split (local-office vs remote) ──────────────────────────────
str_local = [r for r in enr if r['subcategory'] == 'property management — vacation rental / STR management']
out['hre_str'] = {
    'local_office_entities': len(str_local),
    'remote_operators_context': len(remote),
    'vacation_rental_flag_true_all_subcats': sum(
        1 for r in enr if r.get('vacation_rental_flag') == 'true'),
    'str_local_by_city': dict(Counter(r['city'] for r in str_local).most_common()),
}

# ── Dining comparison (computed fresh from dining disk) ──────────────────
d_enr = [r for r in DINING if r.get('enriched')]
dn = len(d_enr)
dvs = Counter(r.get('agent_visibility_score') for r in d_enr)
d_gap = dvs.get('low', 0) + dvs.get('invisible', 0)
d_crawl = tf_counts(d_enr, 'agent_crawlable')
d_sd = tf_counts(d_enr, 'has_structured_data')
d_indep = [r for r in DINING if r.get('chain_or_independent') == 'independent']
out['dining_comparison'] = {
    'census_rows_total': len(DINING),
    'independent_rows': len(d_indep),
    'inspected_independents': dn,
    'score': {k: dvs.get(k, 0) for k in ('high', 'medium', 'low', 'invisible')},
    'gap_low_plus_invisible': {'n': d_gap, 'of': dn, 'pct': pct(d_gap, dn)},
    'crawler_blocked': {'n': d_crawl['false'], 'checkable': d_crawl['checkable'],
                        'pct': pct(d_crawl['false'], d_crawl['checkable'])},
    'structured_data_present': {'n': d_sd['true'], 'checkable': d_sd['checkable'],
                                'pct': pct(d_sd['true'], d_sd['checkable'])},
    'state_enriched_new': len(DINING_STATE.get('enriched_new', [])),
    'state_mapped': len(DINING_STATE.get('mapped', [])),
}

# ── Cumulative across both censuses ──────────────────────────────────────
cum_sd_n = sd['true'] + d_sd['true']
cum_sd_check = sd['checkable'] + d_sd['checkable']
cum_blocked = crawl['false'] + d_crawl['false']
cum_blocked_check = crawl['checkable'] + d_crawl['checkable']
out['cumulative_both_censuses'] = {
    'entities_inspected': n + dn,
    'structured_data_present': {'n': cum_sd_n, 'checkable': cum_sd_check,
                                'pct': pct(cum_sd_n, cum_sd_check)},
    'crawler_blocked': {'n': cum_blocked, 'checkable': cum_blocked_check,
                        'pct': pct(cum_blocked, cum_blocked_check)},
}

with open(os.path.join(HERE, 'report-stats.json'), 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
