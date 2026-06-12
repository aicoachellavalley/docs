export const meta = {
  name: 'cv-hre-discovery',
  description: 'CV Home & Real Estate census — discovery fan-out (geo×subcategory cells, Sonnet workers)',
  phases: [
    { title: 'Discover', detail: 'one Sonnet agent per geo×subcategory scope cell — 3-4 web searches, enumerate businesses', model: 'sonnet' },
  ],
}

// ── Per-batch control: bump BATCH_INDEX (0-based) before each invocation ──
// Batch 0 = PILOT (8 mixed cells). Batches 1-2 = remainder (run only after GATE 1 go).
const BATCH_INDEX = 0

const CITIES = ['Palm Springs','Palm Desert','La Quinta','Rancho Mirage','Cathedral City','Indio','Coachella','Desert Hot Springs','Indian Wells','Thousand Palms','Bermuda Dunes','Thermal']

// Each cell: { subcat (canonical), geo (label), cities[], queries[] }
const ALL_BATCHES = [
  // ── Batch 0 — PILOT ──
  [
    { subcat: 'residential brokerages & teams', geo: 'Palm Springs', cities: ['Palm Springs'],
      queries: ['real estate brokerages Palm Springs CA','top real estate agents teams Palm Springs','Compass Coldwell Banker Bennion Deville Palm Springs office','luxury real estate Palm Springs brokerage'] },
    { subcat: 'residential brokerages & teams', geo: 'Palm Desert', cities: ['Palm Desert'],
      queries: ['real estate brokerages Palm Desert CA','real estate teams Palm Desert','Bennion Deville HomeSmart Coldwell Banker Palm Desert office','luxury golf real estate Palm Desert'] },
    { subcat: 'residential brokerages & teams', geo: 'La Quinta', cities: ['La Quinta'],
      queries: ['real estate brokerages La Quinta CA','PGA West real estate teams La Quinta','real estate agents La Quinta brokerage office','luxury real estate La Quinta'] },
    { subcat: 'property management — vacation rental / STR management', geo: 'Palm Springs', cities: ['Palm Springs'],
      queries: ['vacation rental management companies Palm Springs','short term rental property management Palm Springs','Palm Springs STR management company','vacation rental managers Palm Springs CA'] },
    { subcat: 'property management — long-term residential', geo: 'West valley (PS/DHS/Cathedral City)', cities: ['Palm Springs','Desert Hot Springs','Cathedral City'],
      queries: ['long term residential property management Palm Springs','property management company Cathedral City Desert Hot Springs','residential property managers west Coachella Valley','rental property management Palm Springs CA'] },
    { subcat: 'title & escrow companies', geo: 'valley-wide franchises', cities: CITIES,
      queries: ['title escrow company Coachella Valley','First American Fidelity Chicago Title office Palm Desert Palm Springs','escrow company La Quinta Indio','title insurance office Coachella Valley CA'] },
    { subcat: 'home inspectors', geo: 'valley-wide', cities: CITIES,
      queries: ['home inspector Coachella Valley','home inspection company Palm Springs Palm Desert La Quinta','certified home inspector Indio Cathedral City','property inspection services Coachella Valley CA'] },
    { subcat: 'HOA / community association management', geo: 'big firms valley-wide', cities: CITIES,
      queries: ['HOA management company Coachella Valley','community association management Palm Desert La Quinta','Associa Desert Resort Management Powerstone Coachella Valley','homeowners association manager Palm Springs CA'] },
  ],
  // ── Batch 1 (run after GATE 1) ──
  [
    { subcat: 'residential brokerages & teams', geo: 'Rancho Mirage', cities: ['Rancho Mirage'],
      queries: ['real estate brokerages Rancho Mirage CA','real estate teams Rancho Mirage','luxury real estate Rancho Mirage office','real estate agents Rancho Mirage brokerage'] },
    { subcat: 'residential brokerages & teams', geo: 'Cathedral City', cities: ['Cathedral City'],
      queries: ['real estate brokerages Cathedral City CA','real estate agents Cathedral City','real estate office Cathedral City','homes for sale brokerage Cathedral City'] },
    { subcat: 'residential brokerages & teams', geo: 'Indio', cities: ['Indio'],
      queries: ['real estate brokerages Indio CA','real estate agents teams Indio','real estate office Indio','homes for sale brokerage Indio CA'] },
    { subcat: 'residential brokerages & teams', geo: 'Indian Wells', cities: ['Indian Wells'],
      queries: ['real estate brokerages Indian Wells CA','luxury real estate Indian Wells','real estate agents Indian Wells golf','real estate office Indian Wells'] },
    { subcat: 'residential brokerages & teams', geo: 'Coachella + Thermal', cities: ['Coachella','Thermal'],
      queries: ['real estate brokerages Coachella CA','real estate agents Thermal CA','real estate office Coachella Thermal','homes for sale brokerage Coachella'] },
    { subcat: 'residential brokerages & teams', geo: 'Desert Hot Springs', cities: ['Desert Hot Springs'],
      queries: ['real estate brokerages Desert Hot Springs CA','real estate agents Desert Hot Springs','real estate office Desert Hot Springs','homes for sale brokerage Desert Hot Springs'] },
    { subcat: 'residential brokerages & teams', geo: 'Thousand Palms + Bermuda Dunes', cities: ['Thousand Palms','Bermuda Dunes'],
      queries: ['real estate brokerages Thousand Palms CA','real estate agents Bermuda Dunes CA','real estate office Thousand Palms Bermuda Dunes','homes for sale brokerage Bermuda Dunes'] },
    { subcat: 'property management — vacation rental / STR management', geo: 'golf corridor (LQ/IW/Indio)', cities: ['La Quinta','Indian Wells','Indio'],
      queries: ['vacation rental management La Quinta PGA West','short term rental management Indian Wells','vacation rental property management Indio','STR management company La Quinta CA'] },
  ],
  // ── Batch 2 (run after GATE 1) ──
  [
    { subcat: 'property management — vacation rental / STR management', geo: 'PD/RM/rest', cities: ['Palm Desert','Rancho Mirage','Cathedral City','Desert Hot Springs'],
      queries: ['vacation rental management Palm Desert','short term rental management Rancho Mirage','vacation rental managers Cathedral City Desert Hot Springs','STR property management Palm Desert CA'] },
    { subcat: 'property management — long-term residential', geo: 'Mid valley (PD/RM/IW/Thousand Palms)', cities: ['Palm Desert','Rancho Mirage','Indian Wells','Thousand Palms'],
      queries: ['long term property management Palm Desert','residential property management Rancho Mirage','property managers Indian Wells Thousand Palms','rental management company Palm Desert CA'] },
    { subcat: 'property management — long-term residential', geo: 'East valley (LQ/Indio/Coachella/BD/Thermal)', cities: ['La Quinta','Indio','Coachella','Bermuda Dunes','Thermal'],
      queries: ['long term property management La Quinta','residential property management Indio Coachella','property managers Bermuda Dunes Thermal','rental management company La Quinta Indio CA'] },
    { subcat: 'title & escrow companies', geo: 'independents valley-wide', cities: CITIES,
      queries: ['independent escrow company Coachella Valley','local title escrow Palm Springs Palm Desert','escrow services La Quinta Indio independent','desert escrow company Coachella Valley CA'] },
    { subcat: 'mortgage lenders & brokers', geo: 'West/Mid valley offices', cities: ['Palm Springs','Cathedral City','Desert Hot Springs','Palm Desert','Rancho Mirage','Indian Wells','Thousand Palms'],
      queries: ['mortgage broker Palm Springs Palm Desert office','mortgage lender branch Coachella Valley','home loan officer Rancho Mirage Cathedral City','local mortgage company Palm Desert CA NMLS'] },
    { subcat: 'mortgage lenders & brokers', geo: 'East valley offices', cities: ['La Quinta','Indio','Coachella','Bermuda Dunes','Thermal'],
      queries: ['mortgage broker La Quinta Indio office','mortgage lender branch Indio Coachella','home loan officer La Quinta','local mortgage company Indio CA NMLS'] },
    { subcat: 'appraisers', geo: 'valley-wide', cities: CITIES,
      queries: ['real estate appraiser Coachella Valley','residential appraisal company Palm Springs Palm Desert','certified appraiser La Quinta Indio','home appraisal services Coachella Valley CA'] },
    { subcat: 'HOA / community association management', geo: 'independents valley-wide', cities: CITIES,
      queries: ['independent HOA management Coachella Valley','small community association manager Palm Desert','local HOA management company La Quinta Indio','condo association management Palm Springs CA'] },
  ],
]

const targets = ALL_BATCHES[BATCH_INDEX] || []

const CANDIDATE_SCHEMA = {
  type: 'object',
  required: ['scope_subcat', 'scope_geo', 'candidates'],
  properties: {
    scope_subcat: { type: 'string' },
    scope_geo: { type: 'string' },
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'city', 'subcategory'],
        properties: {
          name: { type: 'string' },
          city: { type: 'string' },
          subcategory: { type: 'string' },
          website: { type: 'string' },
          address_hint: { type: 'string' },
          chain_or_independent: { type: 'string' },
          license_hint: { type: 'string' },
          source: { type: 'string' },
          note: { type: 'string' },
        },
      },
    },
  },
}

phase('Discover')
log(`Batch ${BATCH_INDEX}: ${targets.length} discovery cells (Sonnet 4.6 workers, ~3-4 searches each)...`)

const CITY_LIST = CITIES.join(', ')

const results = await parallel(targets.map((cell, i) => () =>
  agent(
    `AICV real-estate census DISCOVERY agent. Enumerate BUSINESSES in one scope. Light depth: run the searches below, compile a deduplicated business list, return it. Do NOT visit individual websites (that is a later enrichment pass).

SCOPE
- Subcategory: ${cell.subcat}
- Geography: ${cell.geo}  (cities in scope: ${cell.cities.join(', ')})

ENTITY DEFINITION (the rule — do not drift):
An entity is a BUSINESS: a brokerage office, a named team with its own brand/web presence, or a solo practitioner operating as a business brand. NOT individual licensees inside a brokerage. ONE ROW per business per city of its physical office. A brand with offices in 3 cities = 3 rows (one per city). Output the canonical city of the office from this list only: ${CITY_LIST}. If a business's office sits in a scope city, include it; if it only "serves" the area from outside the valley, skip.

HARD EXCLUSIONS (enumerate NOTHING for these):
- Individual MLS listings / for-sale inventory of any kind
- Individual agents with no business brand of their own
- Architects, interior designers, landscapers, contractors, home-services, home-improvement retail
- National iBuyers / portals with no physical local office (Zillow, Opendant, Redfin HQ, etc.)
- Communities, country clubs, HOAs-as-developments themselves (note the NAME in a candidate's note field only if it owns a captive management entity — do not census the community)

SEARCHES (run these, plus light variation if a query returns thin):
${cell.queries.map((q, n) => `  ${n + 1}. "${q}"`).join('\n')}

For each distinct business you find, return:
- name: business/brand/team name (canonical, no agent personal names unless the brand IS the person, e.g. "Jane Doe Group")
- city: one of the canonical cities above (the office city)
- subcategory: "${cell.subcat}"
- website: official URL if it appears in a search snippet — blank if not seen (do NOT fetch to find it)
- address_hint: street/area if visible in snippet — blank otherwise
- chain_or_independent: "chain" (national/regional franchise office) | "independent" | "unknown"
- license_hint: a DRE# or NMLS# ONLY if it literally appears in a search snippet — blank otherwise (no DB lookups)
- source: which search/site surfaced it (e.g. "Yelp", "google", "brokerage site")
- note: one short phrase if useful (e.g. "franchise branch", "team within Compass", "also does STR")

Dedup within your own list (same name+city = one row). Aim for COVERAGE of real businesses in scope; mark fields blank/unknown freely rather than guessing. Return scope_subcat="${cell.subcat}", scope_geo="${cell.geo}", and the candidates array.`,
    { label: `disc:${cell.subcat.slice(0, 14)}/${cell.geo.slice(0, 16)}`, phase: 'Discover', schema: CANDIDATE_SCHEMA, model: 'sonnet' }
  )
))

// Tag each cell's return with source scope identity before filtering (provenance;
// candidate-level dedup happens at the orchestrator on normalized name+city).
const tagged = results.map((r, i) => r ? { ...r, _src_subcat: targets[i].subcat, _src_geo: targets[i].geo } : null)
const ok = tagged.filter(Boolean)
const totalCands = ok.reduce((s, r) => s + (r.candidates?.length || 0), 0)
log(`Batch ${BATCH_INDEX} complete: ${ok.length}/${targets.length} cells returned, ${totalCands} raw candidates. Spend so far: ${Math.round(budget.spent() / 1000)}k tokens`)
return { batch_index: BATCH_INDEX, cells: ok, requested: targets.length, returned: ok.length, raw_candidates: totalCands, tokens_spent: budget.spent() }
