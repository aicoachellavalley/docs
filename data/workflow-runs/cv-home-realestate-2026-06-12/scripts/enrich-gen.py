#!/usr/bin/env python3
"""Generate the HRE enrichment workflow script with embedded ALL_BATCHES
(harness rule: embed batch data, do not use the args channel). Reads enrich_target
rows from the scratch, splits into batches of 40, emits tmp-hre-enrich.js with
BATCH_INDEX=0. Snapshot copies (BATCH_INDEX 0..N) are made downstream via sed.
"""
import json, os

COM = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(COM, 'tmp-agent-mapped-hre.json')))
targets = [r for r in data if r.get('enrich_target')]

BATCH = 40
batches = [targets[i:i+BATCH] for i in range(0, len(targets), BATCH)]
# worker input: minimal fields the enrichment agent needs as seed
def inp(r):
    return {
        'name': r['name'], 'city': r['city'], 'subcategory': r['subcategory'],
        'full_address': r.get('address_hint',''), 'website': r.get('website',''),
        'entity_kind': r.get('entity_kind','office'),
        'chain_hint': r.get('chain_or_independent','unknown'),
    }
ALL = [[inp(r) for r in b] for b in batches]

print(f'{len(targets)} targets -> {len(batches)} batches of <= {BATCH}: sizes {[len(b) for b in batches]}')

SCRIPT = '''export const meta = {
  name: 'cv-hre-enrich',
  description: 'CV Home & Real Estate census — enrichment (~20-field HRE schema, Sonnet workers, 1 site visit + 1 search)',
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
    license_id_displayed: { type: 'string' }, license_type_guess: { type: 'string' },
    cities_served: { type: 'array', items: { type: 'string' } },
    specialties: { type: 'array', items: { type: 'string' } },
    vacation_rental_flag: { type: 'string' },
    year_established_if_stated: { type: 'string' }, team_size_hint: { type: 'string' },
    booking_or_contact_path: { type: 'string' }, chain_or_independent: { type: 'string' },
  },
}

phase('Enrich')
log(`Batch ${BATCH_INDEX}: enriching ${targets.length} HRE entities (Sonnet 4.6, 1 site visit + 1 search)...`)

const results = await parallel(targets.map((entity, i) => () =>
  agent(
    `AICV real-estate light-enrichment agent.

ENTITY: ${entity.name}
CITY: ${entity.city}, CA
SUBCATEGORY: ${entity.subcategory}
ADDRESS (from discovery): ${entity.full_address || 'unknown'}
WEBSITE (from discovery): ${entity.website || 'not found — locate via the step-3 search if possible'}
ENTITY KIND: ${entity.entity_kind}   (office | team_brand | solo)
CHAIN/INDEP HINT: ${entity.chain_hint}

LIGHT ENRICHMENT ONLY. One website visit + one web search = you are DONE. Mark unknowns freely; do not spiral into multi-source research. Dead/blocked site = record the failure state (unknown/false) and move on, no retries.

Do NOT query state license databases — DRE/NMLS verification is a separate deterministic pass later. Capture ONLY what the business itself DISPLAYS.

STEP 1 — Visit their website (use the URL above; if blank, try to find it in step 3). Fill:
- full_address: street address of their office (confirm or correct the discovery value)
- currently_open: "open" | "closed" | "unknown"
- license_id_displayed: the DRE# / NMLS# / other license number the SITE ITSELF shows (CA law requires a DRE# on real-estate marketing — usually in the footer). Blank if none shown.
- license_type_guess: "DRE" | "NMLS" | "other" | "none-visible"
- year_established_if_stated: year if the site states it — blank otherwise
- team_size_hint: e.g. "solo", "5 agents", "20+ staff" if discernible — blank otherwise
- cities_served: array of CV cities/areas they state they serve
- specialties: array — e.g. luxury, golf/country-club, snowbird/seasonal, 1031 exchange, jumbo, REO/foreclosure, vacation rentals, new construction, first-time buyers
- vacation_rental_flag: "true" if they do STR / vacation-rental work, "false" if clearly not, "unknown"
- booking_or_contact_path: "contact form" | "phone" | "online scheduler" | "email" | "multiple" | "unknown"
- chain_or_independent: "chain" (national/regional franchise) | "independent" | "unknown"

STEP 2 — Structured-data / crawlability (from the website visit):
- has_structured_data: "true" if the site has JSON-LD/schema.org markup, "false" if not, "unknown" if unreachable
- agent_crawlable: "false" if the site returns 403 / a Cloudflare challenge to bots; "true" if accessible; "unknown" if unreachable

STEP 3 — One web search: "${entity.name} ${entity.city} ${entity.subcategory}". Observe where they surface:
- agent_visibility_score: "high" (own site + 2+ authoritative sources in top results) | "medium" (present but buried, or only 1 authoritative source) | "low" (barely surfaces; Zillow/aggregators/directories dominate) | "invisible" (not found for the obvious query)
- visibility_gap_note: ONE LINE if reputation (review volume, years in business, transaction volume, awards, brand recognition) clearly exceeds online visibility. Blank if no notable gap.

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

open(os.path.join(COM, 'tmp-hre-enrich.js'), 'w').write(SCRIPT)
print('wrote tmp-hre-enrich.js')
