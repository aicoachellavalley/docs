#!/usr/bin/env python3
"""CV Family & Schooling — Stage-5 close stats. Recompute fresh from disk with
denominators stated. Output -> tmp-fs-stats.json + console summary."""
import json, os
COM = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(COM, 'tmp-agent-mapped-fs.json')))
T = [r for r in data if r.get('enrich_target') and r.get('enriched')]
review = [r for r in data if r.get('segment') == 'review']
home = [r for r in data if r.get('segment') == 'family_home_daycare']

ORDER = ['private K-12 schools','preschools & early-childhood programs',
         'licensed childcare & daycare centers','tutoring, test-prep & academic enrichment',
         'youth sports academies & programs','arts, music & performing-arts education for youth',
         'special-needs & developmental services for children','camps & after-school programs']
# subcats with a STATE credential available to display: CDSS (childcare/preschool) or
# school accreditation (K-12). The rest have NO state credential to display at all.
HAS_STATE_CRED = {'private K-12 schools','preschools & early-childhood programs',
                  'licensed childcare & daycare centers'}

def dist(rows, field, vals=None):
    d = {}
    for r in rows:
        v = (r.get(field) or 'blank')
        if isinstance(v, list): v = 'set' if v else 'blank'
        d[v] = d.get(v, 0) + 1
    return d

def low_or_invis(rows):
    return sum(1 for r in rows if (r.get('agent_visibility_score') in ('low','invisible')))

S = {}
S['n_enriched'] = len(T); S['n_review'] = len(review); S['n_family_home'] = len(home)
S['by_subcategory'] = {k: sum(1 for r in T if r['subcategory']==k) for k in ORDER}
S['by_city'] = {}
for r in T: S['by_city'][r['city']] = S['by_city'].get(r['city'],0)+1

S['agent_visibility_score'] = dist(T, 'agent_visibility_score')
S['gap_low_plus_invisible'] = {'n': low_or_invis(T), 'pct': round(100*low_or_invis(T)/len(T),1)}

crawl = [r for r in T if r.get('agent_crawlable') in ('true','false')]
blocked = sum(1 for r in crawl if r['agent_crawlable']=='false')
S['crawler_blocked'] = {'blocked': blocked, 'checkable': len(crawl),
                        'pct': round(100*blocked/len(crawl),1) if crawl else 0}
sd = [r for r in T if r.get('has_structured_data') in ('true','false')]
sd_yes = sum(1 for r in sd if r['has_structured_data']=='true')
S['structured_data'] = {'present': sd_yes, 'checkable': len(sd),
                        'pct': round(100*sd_yes/len(sd),1) if sd else 0}
S['currently_open'] = dist(T, 'currently_open')
S['tuition_displayed'] = dist(T, 'tuition_or_fees_displayed')
S['credential_type_guess'] = dist(T, 'credential_type_guess')

# credential-display capture rate by subcategory (the verification-leg teaser)
cred = {}
for k in ORDER:
    rows = [r for r in T if r['subcategory']==k]
    shown = sum(1 for r in rows if (r.get('credential_type_guess') in ('CDSS','accreditor')))
    cred[k] = {'n': len(rows), 'credential_shown': shown,
               'pct': round(100*shown/len(rows),1) if rows else 0,
               'state_credential_exists': k in HAS_STATE_CRED}
S['credential_capture_by_subcat'] = cred
# the inspectors-pattern: subcats with NO state credential to display at all
no_cred_subcats = [k for k in ORDER if k not in HAS_STATE_CRED]
S['no_state_credential_subcats'] = {'subcats': no_cred_subcats,
    'n_entities': sum(S['by_subcategory'][k] for k in no_cred_subcats)}

S['name_enriched_count'] = sum(1 for r in T if r.get('name_enriched'))
S['entity_kind'] = dist(T, 'entity_kind')

json.dump(S, open(os.path.join(COM,'tmp-fs-stats.json'),'w'), indent=2)

print(f"ENRICHED: {S['n_enriched']} | review: {S['n_review']} | family_home(context): {S['n_family_home']}")
print(f"\nagent_visibility_score: {S['agent_visibility_score']}")
print(f"  low+invisible GAP: {S['gap_low_plus_invisible']['n']}/{len(T)} = {S['gap_low_plus_invisible']['pct']}%")
print(f"crawler-blocked: {S['crawler_blocked']['blocked']}/{S['crawler_blocked']['checkable']} = {S['crawler_blocked']['pct']}%")
print(f"structured-data present: {S['structured_data']['present']}/{S['structured_data']['checkable']} = {S['structured_data']['pct']}%")
print(f"currently_open: {S['currently_open']}")
print(f"tuition_or_fees_displayed: {S['tuition_displayed']}")
print(f"credential_type_guess: {S['credential_type_guess']}")
print("\nCREDENTIAL-DISPLAY CAPTURE by subcategory (verification-leg teaser):")
for k in ORDER:
    c = cred[k]; tag = 'STATE-CRED EXISTS' if c['state_credential_exists'] else 'no state credential'
    print(f"  {c['credential_shown']:2d}/{c['n']:2d} = {c['pct']:5.1f}%  [{tag}]  {k}")
print(f"\nINSPECTORS-PATTERN: {S['no_state_credential_subcats']['n_entities']} entities in "
      f"{len(no_cred_subcats)} subcats have NO state credential to display at all.")
