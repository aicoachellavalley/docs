export const meta = {
  name: 'cv-family-schooling-discovery',
  description: 'CV Family & Schooling census — discovery fan-out (geo×subcategory cells, Sonnet workers)',
  phases: [
    { title: 'Discover', detail: 'one Sonnet agent per geo×subcategory scope cell — 3-4 web searches, enumerate orgs', model: 'sonnet' },
  ],
}

// ── Per-batch control: bump BATCH_INDEX (0-based) before each invocation ──
// Batch 0 = PILOT (8 mixed cells spanning the density spectrum). Batches 1-2
// = remainder (run only after GATE 1 go). Snapshot each to its own -bN.js.
const BATCH_INDEX = 0

const CITIES = ['Palm Springs','Palm Desert','La Quinta','Rancho Mirage','Cathedral City','Indio','Coachella','Desert Hot Springs','Indian Wells','Thousand Palms','Bermuda Dunes','Thermal']

// Canonical subcategories (the per-candidate `subcategory` MUST be one of these):
//  1 private K-12 schools
//  2 preschools & early-childhood programs
//  3 licensed childcare & daycare centers
//  4 tutoring, test-prep & academic enrichment
//  5 youth sports academies & programs
//  6 arts, music & performing-arts education for youth
//  7 special-needs & developmental services for children
//  8 camps & after-school programs
// NOTE: subcats 2 & 3 are swept TOGETHER (one "early childhood" cell per region)
// for discovery efficiency — the same physical universe; the worker assigns each
// entity to #2 or #3 (or notes "both"). Dedup is name+city so any overlap collapses.

// Each cell: { subcat (focus label), geo (label), cities[], queries[] }
const ALL_BATCHES = [
  // ── Batch 0 — PILOT (8 cells: 2 dense per-city, 1 moderate-regional, 5 valley-wide of varying density) ──
  [
    { subcat: 'preschools & early-childhood programs + licensed childcare & daycare centers', geo: 'Palm Springs', cities: ['Palm Springs'],
      queries: ['preschool Palm Springs CA','licensed daycare childcare center Palm Springs','Montessori preschool Palm Springs','church preschool early learning center Palm Springs CA'] },
    { subcat: 'preschools & early-childhood programs + licensed childcare & daycare centers', geo: 'Palm Desert', cities: ['Palm Desert'],
      queries: ['preschool Palm Desert CA','licensed childcare daycare center Palm Desert','Montessori preschool Palm Desert','KinderCare La Petite Goddard early learning Palm Desert CA'] },
    { subcat: 'private K-12 schools', geo: 'Mid valley (PD/RM/IW)', cities: ['Palm Desert','Rancho Mirage','Indian Wells'],
      queries: ['private school Palm Desert CA','private K-12 school Rancho Mirage','Catholic Christian private school Palm Desert Rancho Mirage','Xavier College Prep Marywood Palm Valley Sacred Heart private school'] },
    { subcat: 'tutoring, test-prep & academic enrichment', geo: 'valley-wide', cities: CITIES,
      queries: ['tutoring center Coachella Valley','Kumon Mathnasium Sylvan Huntington Palm Desert Palm Springs','SAT ACT test prep tutoring Coachella Valley','academic enrichment learning center La Quinta Indio CA'] },
    { subcat: 'youth sports academies & programs', geo: 'tennis & golf academies valley-wide', cities: CITIES,
      queries: ['junior tennis academy Coachella Valley','junior golf academy Palm Desert Indian Wells La Quinta','youth tennis program Palm Springs Rancho Mirage','kids golf academy Coachella Valley CA'] },
    { subcat: 'arts, music & performing-arts education for youth', geo: 'valley-wide', cities: CITIES,
      queries: ['youth dance studio Coachella Valley','kids music lessons school Palm Desert Palm Springs','youth theater performing arts academy Coachella Valley','children art classes studio La Quinta Indio CA'] },
    { subcat: 'special-needs & developmental services for children', geo: 'valley-wide', cities: CITIES,
      queries: ['ABA therapy autism center Coachella Valley','pediatric speech occupational therapy children Palm Desert','learning disability dyslexia center Coachella Valley','developmental services children special needs Palm Springs CA'] },
    { subcat: 'camps & after-school programs', geo: 'valley-wide', cities: CITIES,
      queries: ['after school program kids Coachella Valley','Boys and Girls Clubs Coachella Valley','kids summer camp Palm Desert Palm Springs','YMCA after school childcare enrichment Coachella Valley'] },
  ],
  // ── Batch 1 (run after GATE 1) — remaining early-childhood regions + K-12 wings + tutoring/sports fill ──
  [
    { subcat: 'preschools & early-childhood programs + licensed childcare & daycare centers', geo: 'La Quinta + Indian Wells', cities: ['La Quinta','Indian Wells'],
      queries: ['preschool La Quinta CA','licensed childcare daycare center La Quinta','Montessori preschool Indian Wells','early learning center preschool La Quinta Indian Wells CA'] },
    { subcat: 'preschools & early-childhood programs + licensed childcare & daycare centers', geo: 'Rancho Mirage + Cathedral City', cities: ['Rancho Mirage','Cathedral City'],
      queries: ['preschool Rancho Mirage CA','licensed childcare daycare center Cathedral City','Montessori preschool Rancho Mirage','early learning preschool Cathedral City Rancho Mirage CA'] },
    { subcat: 'preschools & early-childhood programs + licensed childcare & daycare centers', geo: 'Indio + Coachella + Thermal', cities: ['Indio','Coachella','Thermal'],
      queries: ['preschool Indio CA','licensed childcare daycare center Coachella','Head Start preschool Indio Coachella Thermal','early learning childcare center Indio Coachella CA'] },
    { subcat: 'preschools & early-childhood programs + licensed childcare & daycare centers', geo: 'Desert Hot Springs + Thousand Palms + Bermuda Dunes', cities: ['Desert Hot Springs','Thousand Palms','Bermuda Dunes'],
      queries: ['preschool Desert Hot Springs CA','licensed childcare daycare Bermuda Dunes Thousand Palms','Montessori preschool Desert Hot Springs','early learning childcare center Desert Hot Springs CA'] },
    { subcat: 'private K-12 schools', geo: 'West valley (PS/CC/DHS)', cities: ['Palm Springs','Cathedral City','Desert Hot Springs'],
      queries: ['private school Palm Springs CA','Catholic Christian private school Palm Springs Cathedral City','private elementary middle school Desert Hot Springs','Montessori Waldorf private school Palm Springs CA'] },
    { subcat: 'private K-12 schools', geo: 'East valley (LQ/Indio/Coachella/BD/Thermal/TP)', cities: ['La Quinta','Indio','Coachella','Bermuda Dunes','Thermal','Thousand Palms'],
      queries: ['private school La Quinta CA','private K-12 school Indio','Catholic Christian private school Indio Coachella','Desert Christian Academy private school Bermuda Dunes La Quinta'] },
    { subcat: 'tutoring, test-prep & academic enrichment', geo: 'east valley independents', cities: ['La Quinta','Indio','Coachella','Bermuda Dunes','Thermal','Thousand Palms'],
      queries: ['tutoring center La Quinta CA','tutor learning center Indio Coachella','math reading tutoring La Quinta Indio','homework help academic enrichment Indio Coachella CA'] },
    { subcat: 'youth sports academies & programs', geo: 'other youth sports valley-wide (soccer/gym/swim/baseball/cheer/martial arts)', cities: CITIES,
      queries: ['youth soccer club academy Coachella Valley','kids gymnastics swim academy Palm Desert Palm Springs','youth baseball softball academy Coachella Valley','kids martial arts cheer academy La Quinta Indio CA'] },
  ],
  // ── Batch 2 (run after GATE 1) — second sweeps for dense/fragmented thin trades ──
  [
    { subcat: 'arts, music & performing-arts education for youth', geo: 'dance & music second sweep valley-wide', cities: CITIES,
      queries: ['ballet dance academy kids La Quinta Indio Rancho Mirage','music school lessons children Coachella Valley','piano guitar voice lessons studio Palm Desert Palm Springs','childrens theater drama school Coachella Valley CA'] },
    { subcat: 'special-needs & developmental services for children', geo: 'second sweep valley-wide', cities: CITIES,
      queries: ['behavioral therapy autism services children La Quinta Indio','pediatric occupational physical therapy clinic Coachella Valley','speech language therapy children Palm Desert Rancho Mirage','tutoring learning differences dyslexia program Coachella Valley CA'] },
    // camps 2nd sweep dropped per GATE-1 approval (already dense at 24 from pilot)
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
const SUBCATS = [
  'private K-12 schools',
  'preschools & early-childhood programs',
  'licensed childcare & daycare centers',
  'tutoring, test-prep & academic enrichment',
  'youth sports academies & programs',
  'arts, music & performing-arts education for youth',
  'special-needs & developmental services for children',
  'camps & after-school programs',
].map((s, i) => `  ${i + 1}. ${s}`).join('\n')

const results = await parallel(targets.map((cell, i) => () =>
  agent(
    `AICV family & schooling census DISCOVERY agent. Enumerate ORGANIZATIONS in one scope. Light depth: run the searches below, compile a deduplicated list, return it. Do NOT visit individual websites (that is a later enrichment pass).

SCOPE
- Subcategory focus: ${cell.subcat}
- Geography: ${cell.geo}  (cities in scope: ${cell.cities.join(', ')})

ENTITY DEFINITION (the rule — do not drift):
An entity is a PRIVATE organization with a physical Coachella Valley location delivering education, childcare, or youth development as its business. ONE ROW per campus/location per city (a school or program with 3 campuses = 3 rows, one per city). A named program operating its own brand inside a larger facility counts IF it has its own web presence. Output the canonical city of the campus/location from this list only: ${CITY_LIST}. If an org has a physical location in a scope city, include it; if it only "serves the valley" from a base outside the area, still list it but put a clear note ("serves CV, based elsewhere / no confirmed local campus") so triage can flag it.

CANONICAL SUBCATEGORIES — set each candidate's "subcategory" to EXACTLY one of:
${SUBCATS}
(For an early-childhood scope: assign "preschools & early-childhood programs" for a preschool/pre-K curriculum program, or "licensed childcare & daycare centers" for a full-day licensed daycare; if clearly both, use "preschools & early-childhood programs" and note "also full-day childcare".)

HARD EXCLUSIONS (enumerate NOTHING for these):
- Public school districts and district-operated schools (PSUSD, DSUSD, CVUSD) and public charter schools. If you encounter a notable public school/district NAME, you may drop it in a candidate's note field as context, but do NOT create a row for it.
- Individual private tutors / coaches / instructors with NO business brand of their own.
- Higher education, colleges, adult education, workforce/vocational training for adults.
- Children's retail, toy stores, party venues, bounce houses, indoor playgrounds with no education program.
- Pediatric MEDICAL practices (a pediatrician's office). BUT pediatric THERAPY / developmental programs — ABA, speech, OT, learning-difference centers — ARE in scope (subcategory 7). If a place is ambiguous (a clinic that may be medical vs developmental), INCLUDE it with a note "ambiguous: medical vs developmental — verify".

SEARCHES (run these, plus light variation if a query returns thin):
${cell.queries.map((q, n) => `  ${n + 1}. "${q}"`).join('\n')}

For each distinct organization you find, return:
- name: org/school/program/brand name (canonical)
- city: one of the canonical cities above (the campus/location city)
- subcategory: EXACTLY one canonical subcategory string from the list above
- website: official URL if it appears in a search snippet — blank if not seen (do NOT fetch to find it)
- address_hint: street/area if visible in snippet — blank otherwise
- chain_or_independent: "chain" (national/regional franchise like KinderCare/Goddard/Kumon/Mathnasium) | "independent" | "unknown"
- license_hint: a CDSS / Community Care Licensing facility number, OR a WASC/NAIS/AMS accreditation claim, ONLY if it literally appears in a search snippet — blank otherwise (no DB lookups)
- source: which search/site surfaced it (e.g. "Yelp", "google", "school site", "GreatSchools")
- note: one short phrase if useful (e.g. "faith-based", "Montessori", "named program inside a resort", "serves CV based elsewhere", "ambiguous: medical vs developmental")

Dedup within your own list (same name+city = one row). Aim for COVERAGE of real organizations in scope; mark fields blank/unknown freely rather than guessing. Return scope_subcat="${cell.subcat}", scope_geo="${cell.geo}", and the candidates array.`,
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
