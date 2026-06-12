export const meta = {
  name: 'cv-hre-discovery-suppl',
  description: 'CV HRE census — supplemental discovery: inspectors + appraisers split into regional cells',
  phases: [
    { title: 'Discover', detail: 'inspectors west / inspectors mid+east / appraisers west / appraisers mid+east', model: 'sonnet' },
  ],
}

const BATCH_INDEX = 3  // supplemental sweep; merges as discovery batch 3

const WEST = ['Palm Springs','Cathedral City','Desert Hot Springs']
const MIDEAST = ['Palm Desert','Rancho Mirage','Indian Wells','La Quinta','Indio','Coachella','Thousand Palms','Bermuda Dunes','Thermal']
const CANON = ['Palm Springs','Palm Desert','La Quinta','Rancho Mirage','Cathedral City','Indio','Coachella','Desert Hot Springs','Indian Wells','Thousand Palms','Bermuda Dunes','Thermal']

const targets = [
  { subcat: 'home inspectors', geo: 'West valley (PS/CC/DHS)', cities: WEST,
    queries: ['home inspector Palm Springs Cathedral City','home inspection company Desert Hot Springs','certified home inspector Palm Springs CA','InterNACHI home inspector Cathedral City Desert Hot Springs','residential property inspection Palm Springs'] },
  { subcat: 'home inspectors', geo: 'Mid+East valley (PD/RM/IW/LQ/Indio/Coachella/TP/BD/Thermal)', cities: MIDEAST,
    queries: ['home inspector Palm Desert La Quinta Indio','home inspection company Rancho Mirage Indian Wells','certified home inspector Indio Coachella','InterNACHI home inspector Palm Desert La Quinta','residential property inspection Indio Bermuda Dunes'] },
  { subcat: 'appraisers', geo: 'West valley (PS/CC/DHS)', cities: WEST,
    queries: ['real estate appraiser Palm Springs Cathedral City','residential appraisal company Desert Hot Springs','certified residential appraiser Palm Springs CA','home appraiser Cathedral City Desert Hot Springs','property appraisal services Palm Springs'] },
  { subcat: 'appraisers', geo: 'Mid+East valley (PD/RM/IW/LQ/Indio/Coachella/TP/BD/Thermal)', cities: MIDEAST,
    queries: ['real estate appraiser Palm Desert La Quinta Indio','residential appraisal company Rancho Mirage Indian Wells','certified residential appraiser Indio Coachella','home appraiser Palm Desert La Quinta','property appraisal services Indio Bermuda Dunes'] },
]

const CANDIDATE_SCHEMA = {
  type: 'object',
  required: ['scope_subcat', 'scope_geo', 'candidates'],
  properties: {
    scope_subcat: { type: 'string' }, scope_geo: { type: 'string' },
    candidates: { type: 'array', items: { type: 'object',
      required: ['name', 'city', 'subcategory'],
      properties: {
        name: { type: 'string' }, city: { type: 'string' }, subcategory: { type: 'string' },
        website: { type: 'string' }, address_hint: { type: 'string' },
        chain_or_independent: { type: 'string' }, license_hint: { type: 'string' },
        source: { type: 'string' }, note: { type: 'string' },
      } } },
  },
}

phase('Discover')
log(`Supplemental sweep (batch ${BATCH_INDEX}): ${targets.length} regional cells (inspectors + appraisers)...`)
const CITY_LIST = CANON.join(', ')

const results = await parallel(targets.map((cell) => () =>
  agent(
    `AICV real-estate census DISCOVERY agent (supplemental). Enumerate BUSINESSES in one scope. Light depth: run the searches, compile a deduped business list, return it. Do NOT visit individual websites.

SCOPE
- Subcategory: ${cell.subcat}
- Geography: ${cell.geo}  (cities in scope: ${cell.cities.join(', ')})

ENTITY DEFINITION: a BUSINESS — a firm, or a solo practitioner operating as a business brand (a named inspector/appraiser running their own practice IS an entity). NOT an employee inside a larger firm. ONE ROW per business per city of its physical office/base. Output the canonical office city from this list only: ${CITY_LIST}. Skip anyone who only "serves" the area from outside the valley.

EXCLUSIONS: general contractors, engineers doing non-RE inspection, pest-only operators, national lead-gen portals with no local presence.

SEARCHES (run these + light variation if thin):
${cell.queries.map((q, n) => `  ${n + 1}. "${q}"`).join('\n')}

For each distinct business return: name, city (one of the canonical cities = office/base city), subcategory="${cell.subcat}", website (if in a snippet — blank otherwise, do NOT fetch), address_hint, chain_or_independent ("chain"|"independent"|"unknown"), license_hint (a license # ONLY if it literally appears in a snippet — blank otherwise), source, note (short; e.g. "solo practitioner", "InterNACHI certified", "covers whole valley"). These trades are fragmented — aim for the long tail, not just the top 3. Dedup within your own list. Return scope_subcat, scope_geo, and the candidates array.`,
    { label: `disc:${cell.subcat.slice(0, 10)}/${cell.geo.slice(0, 14)}`, phase: 'Discover', schema: CANDIDATE_SCHEMA, model: 'sonnet' }
  )
))

const tagged = results.map((r, i) => r ? { ...r, _src_subcat: targets[i].subcat, _src_geo: targets[i].geo } : null)
const ok = tagged.filter(Boolean)
const totalCands = ok.reduce((s, r) => s + (r.candidates?.length || 0), 0)
log(`Supplemental complete: ${ok.length}/${targets.length} cells, ${totalCands} raw candidates. Spend: ${Math.round(budget.spent() / 1000)}k`)
return { batch_index: BATCH_INDEX, cells: ok, requested: targets.length, returned: ok.length, raw_candidates: totalCands, tokens_spent: budget.spent() }
