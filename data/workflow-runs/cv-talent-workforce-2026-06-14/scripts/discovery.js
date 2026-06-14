export const meta = {
  name: 'cv-talent-workforce-discovery',
  description: 'CV Talent & Workforce census — discovery fan-out (geo×subcategory cells, Sonnet workers)',
  phases: [
    { title: 'Discover', detail: 'one Sonnet agent per scope cell — 3-5 web searches, enumerate orgs', model: 'sonnet' },
  ],
}

// ── Per-batch control: bump BATCH_INDEX (0-based) before each invocation ──
// Batch 0 = PILOT (8 cells spanning the density spectrum: 2 regional staffing,
// 5 valley-wide enrich subcats, 1 valley-wide CONTEXT cell). Remaining batches
// (if the re-projection calls for second sweeps) run only after the STOP-GATE.
// Batch 1 = 2nd wave (post stop-gate go): career-services deep + specialized staffing.
const BATCH_INDEX = 1

const CITIES = ['Palm Springs','Palm Desert','La Quinta','Rancho Mirage','Cathedral City','Indio','Coachella','Desert Hot Springs','Indian Wells','Thousand Palms','Bermuda Dunes','Thermal']

// Canonical ENRICH subcategories (the per-candidate `subcategory` MUST be one of these):
//  1 staffing & recruiting agencies
//  2 adult vocational & trade schools / training providers
//  3 workforce-development & job-readiness service organizations
//  4 coworking & flexible workspace
//  5 career & professional services
//  6 HR outsourcing, PEO & payroll services
// CONTEXT segments (NOT enrich subcats — set `segment`, leave subcategory best-effort):
//  public_workforce | econ_dev | farm_labor_contractor
// EXCLUDED entirely (no rows): entertainment/modeling "talent" agencies.

// Each cell: { subcat (focus label), geo (label), cities[], queries[], mode: 'enrich'|'context' }
const ALL_BATCHES = [
  // ── Batch 0 — PILOT ──
  [
    { mode: 'enrich', subcat: 'staffing & recruiting agencies', geo: 'mid-valley commercial core (PD/RM/PS/IW)', cities: ['Palm Desert','Rancho Mirage','Palm Springs','Indian Wells'],
      queries: ['staffing agency Palm Desert CA','employment agency recruiter Palm Springs','temp staffing light industrial Palm Desert Rancho Mirage','Express Employment AppleOne Robert Half Labor Finders Palm Desert Palm Springs','executive search recruiting firm Coachella Valley'] },
    { mode: 'enrich', subcat: 'staffing & recruiting agencies', geo: 'east valley + ag-adjacent (Indio/Coachella/LQ/CC/DHS/Thermal/BD/TP)', cities: ['Indio','Coachella','La Quinta','Cathedral City','Desert Hot Springs','Thermal','Bermuda Dunes','Thousand Palms'],
      queries: ['staffing agency Indio CA','temp employment agency Coachella La Quinta','labor staffing agency Cathedral City Desert Hot Springs','AtWork staffing Coachella Valley Indio','agricultural labor staffing hospitality staffing Coachella Indio CA'],
      flcnote: true },
    { mode: 'enrich', subcat: 'adult vocational & trade schools / training providers', geo: 'valley-wide', cities: CITIES,
      queries: ['trade school Coachella Valley','cosmetology beauty barber school Palm Springs Palm Desert','CNA medical assistant training school Indio Coachella Valley','truck driving CDL school Coachella Valley','vocational career college adult training Palm Desert Indio CA'] },
    { mode: 'enrich', subcat: 'coworking & flexible workspace', geo: 'valley-wide', cities: CITIES,
      queries: ['coworking space Palm Springs CA','shared office flexible workspace Palm Desert','Regus Spaces Fusion Workplaces Coachella Valley','coworking Rancho Mirage La Quinta Indio','executive suites office membership Palm Springs CA'] },
    { mode: 'enrich', subcat: 'career & professional services', geo: 'valley-wide', cities: CITIES,
      queries: ['career coaching Coachella Valley','resume writing service Palm Springs Palm Desert','outplacement executive coaching Coachella Valley','professional development training firm Palm Desert','job search career counselor Coachella Valley CA'] },
    { mode: 'enrich', subcat: 'HR outsourcing, PEO & payroll services', geo: 'valley-wide', cities: CITIES,
      queries: ['HR outsourcing company Coachella Valley','PEO professional employer organization Palm Desert','payroll services company Palm Springs Indio','human resources consulting firm Coachella Valley','employee benefits HR services Palm Desert CA'] },
    { mode: 'enrich', subcat: 'workforce-development & job-readiness service organizations', geo: 'valley-wide', cities: CITIES,
      queries: ['workforce development nonprofit Coachella Valley','job training program nonprofit Indio Coachella','job readiness employment services nonprofit Palm Springs','ESL workforce skills training organization Coachella Valley','reentry veterans youth employment program Coachella Valley CA'] },
    { mode: 'context', subcat: 'public/institutional workforce infrastructure', geo: 'valley-wide CONTEXT', cities: CITIES,
      queries: ["America's Job Center Riverside County Workforce Development Indio Palm Springs","College of the Desert CSUSB UCR Palm Desert workforce continuing education","OneFuture Coachella Valley CVEP economic partnership ERC Palm Desert","Coachella Valley chamber of commerce workforce program","licensed farm labor contractor Coachella Valley Thermal Mecca Indio"] },
  ],
  // ── Batch 1 — 2nd wave (post stop-gate) — career-services DEEP + specialized/niche staffing ──
  [
    { mode: 'enrich', subcat: 'career & professional services', geo: 'deep resweep valley-wide', cities: CITIES,
      queries: ['career counseling service Coachella Valley','executive leadership coaching Palm Springs Palm Desert','outplacement firm Coachella Valley CA','professional development corporate training company Palm Desert','interview prep LinkedIn personal branding coach Coachella Valley','life coach career transition Rancho Mirage La Quinta Indio CA'] },
    { mode: 'enrich', subcat: 'staffing & recruiting agencies', geo: 'specialized/niche valley-wide (healthcare/IT/hospitality/domestic/event/legal)', cities: CITIES,
      queries: ['travel nurse healthcare staffing agency Coachella Valley','IT technology staffing recruiter Palm Desert Palm Springs','hospitality casino gaming staffing Coachella Valley','domestic household staffing nanny caregiver agency Palm Springs Rancho Mirage','event festival production staffing Coachella Stagecoach Indio','legal accounting finance recruiting firm Coachella Valley CA'] },
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
          segment: { type: 'string' },          // '' for enrich-targets; public_workforce|econ_dev|farm_labor_contractor for context
          website: { type: 'string' },
          address_hint: { type: 'string' },
          chain_or_independent: { type: 'string' },
          license_hint: { type: 'string' },      // FLC license #, BPPE/board approval, etc. — ONLY if literally in a snippet
          source: { type: 'string' },
          note: { type: 'string' },
        },
      },
    },
  },
}

phase('Discover')
log(`Batch ${BATCH_INDEX}: ${targets.length} discovery cells (Sonnet 4.6 workers, ~3-5 searches each)...`)

const CITY_LIST = CITIES.join(', ')
const SUBCATS = [
  'staffing & recruiting agencies',
  'adult vocational & trade schools / training providers',
  'workforce-development & job-readiness service organizations',
  'coworking & flexible workspace',
  'career & professional services',
  'HR outsourcing, PEO & payroll services',
].map((s, i) => `  ${i + 1}. ${s}`).join('\n')

const ENRICH_DEF = `ENTITY DEFINITION (the rule — do not drift):
An entity is a PRIVATE organization (for-profit, OR a service-delivery nonprofit that operates like a business) with a physical Coachella Valley location whose BUSINESS is connecting people to work, training ADULTS for work, or housing/servicing the workforce. ONE ROW per physical location per city (a brand with offices in 2 cities = 2 rows). Output the canonical city of the location from this list only: ${CITY_LIST}. If a firm only "serves the valley" from a base outside the area, still list it but put a clear note ("serves CV, based elsewhere / no confirmed local office") so triage can flag it.

CANONICAL SUBCATEGORIES — set each candidate's "subcategory" to EXACTLY one of:
${SUBCATS}
Leave "segment" BLANK for these enrich-target rows.

HARD EXCLUSIONS (enumerate NOTHING for these — no row):
- Entertainment / modeling / acting / casting / booking "TALENT" agencies. This is a DIFFERENT sense of "talent" (a separate future category, separately licensed). If you encounter one, you MAY drop the name in a note as context, but do NOT create a row.
- Individual recruiters / coaches / trainers with NO business brand of their own.
- A single employer's IN-HOUSE HR or recruiting (we want firms that SERVE other employers or jobseekers, not one company hiring for itself).
- K-12 schools, childcare, and youth education (covered by a separate census). This census is ADULT workforce only.
- Degree-granting public institutions (College of the Desert, CSUSB, UCR) and government job centers — those are CONTEXT, captured by the dedicated context cell, NOT here.
- Plain commercial real-estate leasing / office brokers (coworking = shared/flexible MEMBERSHIP workspace specifically).`

const CONTEXT_DEF = `THIS IS A CONTEXT CELL — these orgs are the institutional backbone of the category but are NOT business enrich-targets. Enumerate them and TAG each with "segment":
- segment="public_workforce": government / public workforce infrastructure — Riverside County Workforce Development Board, America's Job Center of California (AJCC) sites (e.g. Indio 44-199 Monroe St), EDD offices, and the WORKFORCE / CONTINUING-ED / non-credit arms of College of the Desert, CSUSB Palm Desert, UCR Palm Desert, plus public adult-school CTE.
- segment="econ_dev": economic-development convening / funder / advocacy orgs — CVEP (NOTE: board-dissolved 2024), the Palm Desert ERC (now CSUSB-run), OneFuture Coachella Valley, chamber-of-commerce workforce programs.
- segment="farm_labor_contractor": the CA-licensed FARM LABOR CONTRACTOR population of the east valley (Coachella/Thermal/Mecca/Indio). Do NOT try to web-enumerate them all — they are a state-registry population counted separately. List only any that surface with a real business WEBSITE; for the population as a whole add ONE row name="(FLC registry population — count separately)" segment="farm_labor_contractor" note="DIR-licensed; enumerate from registry, not web".
For every context row set subcategory to a short descriptor (e.g. "AJCC site", "community college workforce arm", "econ-dev nonprofit", "farm labor contractor") and put segment as above. Capture license_hint only if a license/approval number literally appears.`

const results = await parallel(targets.map((cell, i) => () =>
  agent(
    `AICV Talent & Workforce census DISCOVERY agent. Enumerate ORGANIZATIONS in one scope. Light depth: run the searches below, compile a deduplicated list, return it. Do NOT visit individual websites (that is a later enrichment pass).

SCOPE
- Focus: ${cell.subcat}
- Geography: ${cell.geo}  (cities in scope: ${cell.cities.join(', ')})

${cell.mode === 'context' ? CONTEXT_DEF : ENRICH_DEF}
${cell.flcnote ? `\nFLC PROMOTION NOTE: some east-valley staffing operators are licensed farm labor contractors (FLCs). If one has a real business WEBSITE and operates like a staffing agency, INCLUDE it as subcategory="staffing & recruiting agencies", segment="" (it is an enrich-target), note="FLC-licensed", and license_hint if a license # appears in a snippet. The broader FLC registry population is counted separately by the context cell — do not enumerate it here.` : ''}

SEARCHES (run these, plus light variation if a query returns thin):
${cell.queries.map((q, n) => `  ${n + 1}. "${q}"`).join('\n')}

For each distinct organization you find, return:
- name: org/firm/brand name (canonical)
- city: one of the canonical cities above (the location city)
- subcategory: ${cell.mode === 'context' ? 'a short descriptor (see context rules)' : 'EXACTLY one canonical subcategory string from the list above'}
- segment: ${cell.mode === 'context' ? 'public_workforce | econ_dev | farm_labor_contractor (per the rules above)' : 'leave BLANK ("")'}
- website: official URL if it appears in a search snippet — blank if not seen (do NOT fetch to find it)
- address_hint: street/area if visible in snippet — blank otherwise
- chain_or_independent: "chain" (national/regional franchise/branch like Express Employment / Robert Half / Regus / ADP) | "independent" | "unknown"
- license_hint: an FLC license #, a BPPE/board approval #, or similar ONLY if it literally appears in a snippet — blank otherwise (no DB lookups)
- source: which search/site surfaced it (e.g. "Yelp", "google", "Chamber", "company site")
- note: one short phrase if useful (e.g. "light-industrial temp", "national branch", "FLC-licensed", "nonprofit service-delivery", "serves CV based elsewhere", "entertainment talent agency — excluded")

Dedup within your own list (same name+city = one row). Aim for COVERAGE of real organizations in scope; mark fields blank/unknown freely rather than guessing. Return scope_subcat="${cell.subcat}", scope_geo="${cell.geo}", and the candidates array.`,
    { label: `disc:${cell.subcat.slice(0, 16)}/${cell.geo.slice(0, 14)}`, phase: 'Discover', schema: CANDIDATE_SCHEMA, model: 'sonnet' }
  )
))

// Tag each cell's return with source scope identity before filtering (provenance;
// candidate-level dedup happens at the orchestrator on normalized name+city).
const tagged = results.map((r, i) => r ? { ...r, _src_subcat: targets[i].subcat, _src_geo: targets[i].geo, _src_mode: targets[i].mode } : null)
const ok = tagged.filter(Boolean)
const totalCands = ok.reduce((s, r) => s + (r.candidates?.length || 0), 0)
log(`Batch ${BATCH_INDEX} complete: ${ok.length}/${targets.length} cells returned, ${totalCands} raw candidates. Spend so far: ${Math.round(budget.spent() / 1000)}k tokens (output-basis)`)
return { batch_index: BATCH_INDEX, cells: ok, requested: targets.length, returned: ok.length, raw_candidates: totalCands, tokens_spent: budget.spent() }
