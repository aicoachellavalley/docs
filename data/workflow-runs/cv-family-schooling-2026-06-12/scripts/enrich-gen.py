#!/usr/bin/env python3
"""Generate the CV Family & Schooling enrichment workflow with embedded ALL_BATCHES
(harness rule: embed batch data, not the args channel). Reads enrich_target rows
from tmp-agent-mapped-fs.json, splits into batches of 40, emits tmp-fs-enrich.js
with BATCH_INDEX=0. Snapshot copies (BATCH_INDEX 0..N) are made downstream via sed.
Do NOT hand-edit tmp-fs-enrich.js — re-run this.
"""
import json, os
COM = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(COM, 'tmp-agent-mapped-fs.json')))
targets = [r for r in data if r.get('enrich_target')]

BATCH = 40
batches = [targets[i:i+BATCH] for i in range(0, len(targets), BATCH)]
def inp(r):
    return {
        'name': r['name'], 'city': r['city'], 'subcategory': r['subcategory'],
        'full_address': r.get('address_hint',''), 'website': r.get('website',''),
        'entity_kind': r.get('entity_kind','campus'),
        'chain_hint': r.get('chain_or_independent','unknown'),
        'programs_note': r.get('programs_note',''),
        'verify_note': r.get('_verify_note',''),
    }
ALL = [[inp(r) for r in b] for b in batches]
print(f'{len(targets)} targets -> {len(batches)} batches of <= {BATCH}: sizes {[len(b) for b in batches]}')

SCRIPT = '''export const meta = {
  name: 'cv-family-schooling-enrich',
  description: 'CV Family & Schooling census — enrichment (~20-field schema, Sonnet workers, 1 site visit + 1 search)',
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
    license_or_accreditation_displayed: { type: 'string' }, credential_type_guess: { type: 'string' },
    ages_grades_served: { type: 'string' }, enrollment_or_capacity_hint: { type: 'string' },
    faith_affiliation_if_stated: { type: 'string' }, tuition_or_fees_displayed: { type: 'string' },
    admissions_or_enrollment_path: { type: 'string' },
    special_programs_if_stated: { type: 'array', items: { type: 'string' } },
    year_established_if_stated: { type: 'string' }, chain_or_independent: { type: 'string' },
  },
}

phase('Enrich')
log(`Batch ${BATCH_INDEX}: enriching ${targets.length} family/schooling entities (Sonnet 4.6, 1 site visit + 1 search)...`)

const results = await parallel(targets.map((entity, i) => () =>
  agent(
    `AICV family & schooling light-enrichment agent.

ENTITY: ${entity.name}
CITY: ${entity.city}, CA
SUBCATEGORY: ${entity.subcategory}
ADDRESS (from discovery): ${entity.full_address || 'unknown'}
WEBSITE (from discovery): ${entity.website || 'not found — locate via the step-3 search if possible'}
ENTITY KIND: ${entity.entity_kind}   (campus | program_brand | solo)
CHAIN/INDEP HINT: ${entity.chain_hint}` +
    (entity.programs_note ? `\\nABSORBED PROGRAMS (this campus also runs these — reflect in special_programs / ages if relevant): ${entity.programs_note}` : ``) +
    (entity.verify_note ? `\\nVERIFY (resolve this): ${entity.verify_note}` : ``) + `

LIGHT ENRICHMENT ONLY. One website visit + one web search = you are DONE. Mark unknowns freely; do not spiral into multi-source research. Dead/blocked site = record the failure state (unknown/false) and move on, no retries.

Do NOT query state licensing databases (CDSS / Community Care Licensing / WASC / NAIS / AMS). Capture ONLY what the organization DISPLAYS on its own site — credential VERIFICATION is a separate deterministic pass later.

If ENTITY KIND is program_brand (a named program operating inside a larger venue/facility), set "name" to the PROGRAM's own brand name, not the host venue.

STEP 1 — Visit their website (URL above; if blank, find it in the step-3 search). Fill:
- full_address: street address of the campus/location (confirm or correct the discovery value)
- currently_open: "open" | "closed" | "unknown"
- license_or_accreditation_displayed: the EXACT thing the site shows — a CDSS / Community Care Licensing facility number (childcare/preschool), OR an accreditation claim (WASC, NAIS, AMS/Montessori, Cognia, etc.) for schools. Verbatim if shown; "none-visible" if the site shows neither.
- credential_type_guess: "CDSS" (a license #) | "accreditor" (WASC/NAIS/AMS/etc.) | "none-visible"
- ages_grades_served: e.g. "infant–pre-K", "TK–8", "9–12", "ages 3–5", "grades 6–12", "youth all-ages"
- enrollment_or_capacity_hint: stated enrollment or licensed capacity if shown — blank otherwise
- faith_affiliation_if_stated: e.g. "Catholic", "Christian non-denom", "Adventist", "Jewish", "secular/none" if stated — blank if not addressed
- tuition_or_fees_displayed: "yes" if any tuition/fee/pricing is shown on the site, "no" if not (high agent-query value)
- admissions_or_enrollment_path: "form" | "phone" | "portal" | "tour" | "email" | "multiple" | "unknown"
- special_programs_if_stated: array — e.g. IB, dual/language immersion, Montessori, Waldorf, STEM/STEAM, gifted/GATE, AP, learning-differences/dyslexia support, ABA, special-needs inclusion, arts/athletics focus
- year_established_if_stated: year if the site states it — blank otherwise
- chain_or_independent: "chain" (national/regional franchise — KinderCare, Goddard, Kumon, Mathnasium, etc.) | "independent" | "unknown"

STEP 2 — Structured-data / crawlability (from the website visit):
- has_structured_data: "true" if the site has JSON-LD/schema.org markup, "false" if not, "unknown" if unreachable
- agent_crawlable: "false" if the site returns 403 / a Cloudflare challenge to bots; "true" if accessible; "unknown" if unreachable

STEP 3 — One web search: "${entity.name} ${entity.city} ${entity.subcategory}". Observe where they surface:
- agent_visibility_score: "high" (own site + 2+ authoritative sources in top results) | "medium" (present but buried, or only 1 authoritative source) | "low" (barely surfaces; aggregators like GreatSchools/Yelp/Care.com dominate) | "invisible" (not found for the obvious query)
- visibility_gap_note: ONE LINE if reputation (enrollment, years in operation, accreditation, awards, community standing) clearly exceeds online visibility. Blank if no notable gap.

Return name, city, and subcategory. (name = the canonical org/program name.) All other fields may be "unknown"/blank if not found — that is correct output.`,
    { label: `enrich:${entity.name.slice(0, 22)}`, phase: 'Enrich', schema: ENRICH_SCHEMA, model: 'sonnet' }
  )
))

const tagged = results.map((r, i) => r ? { ...r, _src_name: targets[i].name, _src_city: targets[i].city } : null)
const ok = tagged.filter(Boolean)
log(`Batch ${BATCH_INDEX} complete: ${ok.length}/${targets.length} returned. Spend: ${Math.round(budget.spent() / 1000)}k`)
return { batch_index: BATCH_INDEX, enrichment: ok, requested: targets.length, returned: ok.length, tokens_spent: budget.spent() }
''' % json.dumps(ALL, ensure_ascii=False)

open(os.path.join(COM, 'tmp-fs-enrich.js'), 'w').write(SCRIPT)
print('wrote tmp-fs-enrich.js')
