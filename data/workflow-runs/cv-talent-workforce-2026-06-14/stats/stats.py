#!/usr/bin/env python3
"""CV Talent & Workforce — Stage-5 close stats. Recompute fresh from disk with
denominators stated (OPERATING-RULES §5.2). Output -> tmp-tw-stats.json + console."""
import json, os
COM = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(COM, 'tmp-agent-mapped-tw.json')))
T = [r for r in data if r.get('enrich_target') and r.get('enriched')]
review = [r for r in data if r.get('segment','') == '' and not r.get('enrich_target')]
context = [r for r in data if r.get('segment')]

ORDER = ['staffing & recruiting agencies',
         'adult vocational & trade schools / training providers',
         'workforce-development & job-readiness service organizations',
         'coworking & flexible workspace',
         'career & professional services',
         'HR outsourcing, PEO & payroll services']

def dist(rows, field):
    d = {}
    for r in rows:
        v = r.get(field)
        if isinstance(v, list): v = 'set' if v else 'blank'
        if v in (None, ''): v = 'blank'
        d[v] = d.get(v, 0) + 1
    return dict(sorted(d.items(), key=lambda kv: -kv[1]))

def pct(n, d): return round(100*n/d, 1) if d else 0.0

S = {}
S['n_enriched'] = len(T); S['n_review'] = len(review); S['n_context'] = len(context)
S['by_subcategory'] = {k: sum(1 for r in T if r['subcategory']==k) for k in ORDER}
S['by_city'] = {}
for r in T: S['by_city'][r['city']] = S['by_city'].get(r['city'],0)+1
S['by_city'] = dict(sorted(S['by_city'].items(), key=lambda kv: -kv[1]))
S['by_context_segment'] = dist(context, 'segment')

# visibility
S['agent_visibility_score'] = dist(T, 'agent_visibility_score')
gap = sum(1 for r in T if r.get('agent_visibility_score') in ('low','invisible'))
S['gap_low_plus_invisible'] = {'n': gap, 'pct': pct(gap, len(T))}
crawl = [r for r in T if r.get('agent_crawlable') in ('true','false')]
blocked = sum(1 for r in crawl if r['agent_crawlable']=='false')
S['crawler_blocked'] = {'blocked': blocked, 'checkable': len(crawl), 'pct': pct(blocked, len(crawl))}
sd = [r for r in T if r.get('has_structured_data') in ('true','false')]
sd_yes = sum(1 for r in sd if r['has_structured_data']=='true')
S['structured_data'] = {'present': sd_yes, 'checkable': len(sd), 'pct': pct(sd_yes, len(sd))}
S['currently_open'] = dist(T, 'currently_open')

# transparency: pricing_displayed (the F&S 'hide pricing' analog)
pr = [r for r in T if r.get('pricing_displayed') in ('yes','no')]
pr_yes = sum(1 for r in pr if r['pricing_displayed']=='yes')
S['pricing_displayed'] = {'shown': pr_yes, 'checkable': len(pr), 'pct_shown': pct(pr_yes, len(pr)),
                          'pct_hidden': pct(len(pr)-pr_yes, len(pr))}

# the SERIES-FIRST split: credential regime (row-level; FLC promotions overridden to credentialed)
S['by_credential_regime'] = dist(T, 'credential_regime')
cred_rows = [r for r in T if r.get('credential_regime')=='credentialed']
cred_shown = sum(1 for r in cred_rows if r.get('credential_type_guess') not in (None,'','none-visible'))
S['credential_display_among_credentialed'] = {'shown': cred_shown, 'n': len(cred_rows),
                                               'pct': pct(cred_shown, len(cred_rows))}
S['credential_type_guess'] = dist(T, 'credential_type_guess')

# category descriptives
S['clientele'] = dist(T, 'clientele')
S['nonprofit_or_forprofit'] = dist(T, 'nonprofit_or_forprofit')
S['chain_or_independent'] = dist(T, 'chain_or_independent')
S['entity_kind'] = dist(T, 'entity_kind')

json.dump(S, open(os.path.join(COM,'tmp-tw-stats.json'),'w'), indent=2)

print(f"ENRICHED: {S['n_enriched']} | review: {S['n_review']} | context: {S['n_context']} {S['by_context_segment']}")
print(f"\nby_subcategory: {json.dumps(S['by_subcategory'])}")
print(f"by_city: {json.dumps(S['by_city'])}")
print(f"\nagent_visibility_score: {S['agent_visibility_score']}")
print(f"  low+invisible GAP: {gap}/{len(T)} = {S['gap_low_plus_invisible']['pct']}%")
print(f"crawler-blocked: {blocked}/{len(crawl)} = {S['crawler_blocked']['pct']}%")
print(f"structured-data: {sd_yes}/{len(sd)} = {S['structured_data']['pct']}%")
print(f"pricing_displayed: shown {pr_yes}/{len(pr)} = {S['pricing_displayed']['pct_shown']}% (hidden {S['pricing_displayed']['pct_hidden']}%)")
print(f"currently_open: {S['currently_open']}")
print(f"\n*** SERIES-FIRST SPLIT — credential_regime: {S['by_credential_regime']}")
print(f"    credential DISPLAYED among credentialed: {cred_shown}/{len(cred_rows)} = {S['credential_display_among_credentialed']['pct']}%")
print(f"    credential_type_guess: {S['credential_type_guess']}")
print(f"\nclientele: {S['clientele']}")
print(f"nonprofit_or_forprofit: {S['nonprofit_or_forprofit']}")
print(f"chain_or_independent: {S['chain_or_independent']}")
print(f"entity_kind: {S['entity_kind']}")
