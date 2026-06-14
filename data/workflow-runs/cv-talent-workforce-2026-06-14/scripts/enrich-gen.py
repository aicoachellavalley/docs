#!/usr/bin/env python3
"""Generate the Talent & Workforce enrichment workflow with embedded ALL_BATCHES
(harness rule: embed batch data, never the args channel). Reads enrich_target rows
from tmp-agent-mapped-tw.json, splits into batches of 40, emits tmp-tw-enrich.js
with BATCH_INDEX=0. Snapshot copies (BATCH_INDEX 0..N) made downstream via sed.

T&W category block: credential-display capture (FLC#/BPPE#/board license as-DISPLAYED
only — verification is a separate pass), services/sectors, clientele (employers vs
jobseekers), pricing-transparency (the F&S '83% hide pricing' analog), nonprofit flag.
"""
import json, os

COM = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(COM, 'tmp-agent-mapped-tw.json')))
targets = [r for r in data if r.get('enrich_target')]

BATCH = 40
batches = [targets[i:i+BATCH] for i in range(0, len(targets), BATCH)]
def inp(r):
    return {
        'name': r['name'], 'city': r['city'], 'subcategory': r['subcategory'],
        'full_address': r.get('address_hint',''), 'website': r.get('website',''),
        'entity_kind': r.get('entity_kind','office'),
        'chain_hint': r.get('chain_or_independent','unknown'),
        'regime': r.get('credential_regime','unknown'),
    }
ALL = [[inp(r) for r in b] for b in batches]

print(f'{len(targets)} targets -> {len(batches)} batches of <= {BATCH}: sizes {[len(b) for b in batches]}')

SCRIPT = r'''export const meta = {
  name: 'cv-talent-workforce-enrich',
  description: 'CV Talent & Workforce census — enrichment (~20-field schema, Sonnet workers, 1 site visit + 1 search)',
  phases: [
    { title: 'Enrich', detail: 'one Sonnet agent per entity — website visit + one web search', model: 'sonnet' },
  ],
}

// ── Per-batch control: bump BATCH_INDEX (0-based) before each invocation ──
const BATCH_INDEX = 0

const ALL_BATCHES = %s

const targets = ALL_BATCHES[BATCH_INDEX] || []

const ENRICH_SCHEMA = {
  type: 'object',
  required: ['name', 'city', 'subcategory', 'agent_visibility_score'],
  properties: {
    name: { type: 'string' }, city: { type: 'string' }, subcategory: { type: 'string' },
    full_address: { type: 'string' }, website: { type: 'string' },
    currently_open: { type: 'string' },
    has_structured_data: { type: 'string' }, agent_crawlable: { type: 'string' },
    agent_visibility_score: { type: 'string' }, visibility_gap_note: { type: 'string' },
    credential_displayed: { type: 'string' }, credential_type_guess: { type: 'string' },
    services_offered: { type: 'array', items: { type: 'string' } },
    industries_or_sectors_served: { type: 'array', items: { type: 'string' } },
    areas_served: { type: 'array', items: { type: 'string' } },
    pricing_displayed: { type: 'string' }, clientele: { type: 'string' },
    nonprofit_or_forprofit: { type: 'string' },
    year_established_if_stated: { type: 'string' }, size_hint: { type: 'string' },
    booking_or_contact_path: { type: 'string' }, chain_or_independent: { type: 'string' },
  },
}

phase('Enrich')
log(`Batch ${BATCH_INDEX}: enriching ${targets.length} talent/workforce entities (Sonnet 4.6, 1 site visit + 1 search)...`)

const results = await parallel(targets.map((entity, i) => () =>
  agent(
    `AICV Talent & Workforce light-enrichment agent.

ENTITY: ${entity.name}
CITY: ${entity.city}, CA
SUBCATEGORY: ${entity.subcategory}
ADDRESS (from discovery): ${entity.full_address || 'unknown'}
WEBSITE (from discovery): ${entity.website || 'not found — locate via the step-3 search if possible'}
ENTITY KIND: ${entity.entity_kind}   (office | branch | solo)
CHAIN/INDEP HINT: ${entity.chain_hint}
CREDENTIAL REGIME for this subcategory: ${entity.regime}   (credentialed = a state license/approval may be displayed; unregulated = none expected, but capture any industry cert shown)

LIGHT ENRICHMENT ONLY. One website visit + one web search = you are DONE. Mark unknowns freely; do not spiral into multi-source research. Dead/blocked site = record the failure state (unknown/false) and move on, no retries.

Do NOT query state license databases (DIR FLC registry, BPPE, board lookups) — verification is a separate deterministic pass later. Capture ONLY what the business itself DISPLAYS.

STEP 1 — Visit their website (use the URL above; if blank, try to find it in step 3). Fill:
- full_address: street address of their CV office (confirm or correct the discovery value)
- currently_open: "open" | "closed" | "unknown"
- credential_displayed: the license/approval NUMBER the SITE ITSELF shows — a CA Farm Labor Contractor (FLC) license #, a BPPE approval #, a state-board license (Barbering & Cosmetology / DMV driving-school / CDPH CNA-program), or a named industry certification. Blank if none shown.
- credential_type_guess: "FLC" | "BPPE" | "state-board" | "industry-cert" | "none-visible"
- services_offered: array — e.g. temp staffing, direct-hire, executive search, payrolling, CNA program, CDL training, cosmetology program, hot-desk, private office, virtual office, payroll, benefits admin, PEO, career coaching, outplacement, resume writing
- industries_or_sectors_served: array — e.g. hospitality, healthcare, light-industrial, agriculture, IT, construction, gaming/casino, finance/legal (blank/n/a for coworking & trade schools)
- areas_served: array of CV cities/areas they state they serve
- pricing_displayed: "yes" if the site shows ANY rates/fees/tuition/membership pricing, "no" if none, "unknown" if unreachable  (the high-value transparency signal — most B2B services hide it)
- clientele: "employers" | "jobseekers" | "both" | "n/a"  (who the service is sold to; n/a for coworking/trade schools where it is the worker/student directly)
- nonprofit_or_forprofit: "nonprofit" | "for-profit" | "unknown"
- year_established_if_stated: year if the site states it — blank otherwise
- size_hint: e.g. "solo", "1 office", "3 CV locations", "50+ desks", "national branch" — blank if unclear
- booking_or_contact_path: "contact form" | "phone" | "online scheduler" | "application portal" | "email" | "multiple" | "unknown"
- chain_or_independent: "chain" (national/regional franchise/branch) | "independent" | "unknown"

STEP 2 — Structured-data / crawlability (from the website visit):
- has_structured_data: "true" if the site has JSON-LD/schema.org markup, "false" if not, "unknown" if unreachable
- agent_crawlable: "false" if the site returns 403 / a Cloudflare challenge to bots; "true" if accessible; "unknown" if unreachable

STEP 3 — One web search: "${entity.name} ${entity.city} ${entity.subcategory}". Observe where they surface:
- agent_visibility_score: "high" (own site + 2+ authoritative sources in top results) | "medium" (present but buried, or only 1 authoritative source) | "low" (barely surfaces; aggregators/directories dominate) | "invisible" (not found for the obvious query)
- visibility_gap_note: ONE LINE if reputation (review volume, years in business, brand recognition, placements) clearly exceeds online visibility. Blank if no notable gap.

Return name, city, and subcategory exactly as given. All other fields may be "unknown"/blank if not found — that is correct output.`,
    { label: `enrich:${entity.name.slice(0, 22)}`, phase: 'Enrich', schema: ENRICH_SCHEMA, model: 'sonnet' }
  )
))

// canonical source identity by index BEFORE filtering, so the merge never depends
// on positional alignment or agent-renamed payloads.
const tagged = results.map((r, i) => r ? { ...r, _src_name: targets[i].name, _src_city: targets[i].city } : null)
const ok = tagged.filter(Boolean)
log(`Batch ${BATCH_INDEX} complete: ${ok.length}/${targets.length} returned. Spend: ${Math.round(budget.spent() / 1000)}k`)
return { batch_index: BATCH_INDEX, enrichment: ok, requested: targets.length, returned: ok.length, tokens_spent: budget.spent() }
''' % json.dumps(ALL, ensure_ascii=False)

open(os.path.join(COM, 'tmp-tw-enrich.js'), 'w').write(SCRIPT)
print('wrote tmp-tw-enrich.js')
