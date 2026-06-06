/**
 * VisitGPS Agent-Readiness Audit — Standalone Wide-Scan + Aggregate
 *
 * Created 2026-06-05 after the full Phase 1 pipeline's Wide Scan stage failed
 * due to a structured-output truncation in the loader agent (2 MB of partner
 * records couldn't cross an agent boundary cleanly). This standalone takes
 * the existing clean inventory on disk as input and re-runs scoring against
 * it. It will be the durable artifact for re-scoring re-runs going forward.
 *
 * Architectural lesson encoded here as a pattern:
 *   "Large data crosses agent boundaries via disk, not structured output."
 * Each chunk agent reads its own slice from disk by index range, scores it,
 * and writes its output to disk. Structured output is reserved for control
 * data (counts, paths, anomalies) — not data payloads.
 *
 * Inputs:
 *   - scout/partner-directory-clean.json  (the kept_for_scoring set,
 *     produced either by audit-workflow.js's Inventory: Merge stage OR by
 *     the 2026-06-05 recovery script scout/remerge.py)
 *   - scout/inventory-no-weburl.jsonl     (records auto-assigned Tier Z)
 *
 * Invocation:
 *   Workflow({
 *     scriptPath: '/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/audit-scoring-workflow.js'
 *   })
 *
 * Optional args:
 *   - chunks: integer, override the default chunk count (default ~14)
 *
 * Phase 2 remains deferred. v0 full-pipeline archived at
 * audit-workflow-v0-archived.js; v2 full pipeline at audit-workflow.js
 * (kept current so a future quarter's audit can re-fetch from scratch).
 */

export const meta = {
  name: 'visitgps-audit-scoring',
  description: 'Standalone Wide Scan + Aggregate. Takes scout/partner-directory-clean.json as input; chunk agents read their slice from disk (no large-payload structured output). Hard hold at Aggregate.',
  phases: [
    { title: 'Load', detail: 'Count records on disk, plan chunks' },
    { title: 'Wide scan', detail: 'Parallel rubric checks; each chunk agent reads its own disk slice' },
    { title: 'Verify', detail: 'Hard gate: verify_chunks.py confirms every expected chunk file exists with the correct slice on disk' },
    { title: 'Aggregate', detail: 'Three-level taxonomy cuts, Tier Z, dedup by weburl, chain-vs-indie' },
  ],
}

// ============================================================
// Constants
// ============================================================

const AUDIT_DIR = '/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2'
const UA = 'AICV-Audit/2026Q2 (+https://aicoachellavalley.org)'
const CLEAN_PATH = `${AUDIT_DIR}/scout/partner-directory-clean.json`
const NO_WEBURL_PATH = `${AUDIT_DIR}/scout/inventory-no-weburl.jsonl`
const CHUNKS_DIR = `${AUDIT_DIR}/auditor/chunks`

// 7-bucket strategic taxonomy, locked 2026-06-05. See TAXONOMY-CANONICAL.md.
const CANONICAL_MAP = {
  'STAY': 'Lodging',
  'PLACES TO STAY': 'Lodging',
  'EAT & DRINK': 'Dining',
  'THINGS TO DO': 'Activities',
  'ACTIVITIES & RECREATION': 'Activities',
  'TOURS': 'Tours',
  'ARTS & CULTURE': 'Arts & Culture',
  'CASINOS & ENTERTAINMENT': 'Entertainment',
  'GOLF': 'Golf',
  'HIKING TRAILS': 'Outdoor Recreation',
  'SPAS, BEAUTY & WELLNESS': 'Spas & Wellness',
  'GROUP VENUES': 'Group Venues',
  'MEETING & EVENT RESOURCES': 'Meeting Resources',
  'WEDDINGS': 'Weddings',
  'GETTING HERE': 'Transportation',
  'GETTING HERE & AROUND': 'Transportation',
  'VISITOR INFORMATION': 'Visitor Services',
  'SHOPPING': 'Shopping',
  'BUSINESS & PROFESSIONAL SERVICES': 'Professional Services',
  'RELOCATION & RESOURCES': 'Relocation',
  'FILM PRODUCTION SERVICES': 'Film Production',
  'CANNABIS': 'Cannabis',
  'DOG-FRIENDLY RESOURCES': 'Pet Services',
}

const STRATEGIC_MAP = {
  'Lodging': 'Lodging',
  'Dining': 'Dining',
  'Activities': 'Experiences',
  'Tours': 'Experiences',
  'Arts & Culture': 'Experiences',
  'Entertainment': 'Experiences',
  'Golf': 'Experiences',
  'Outdoor Recreation': 'Experiences',
  'Spas & Wellness': 'Wellness',
  'Group Venues': 'Meetings & Events',
  'Meeting Resources': 'Meetings & Events',
  'Weddings': 'Meetings & Events',
  'Transportation': 'Mobility',
  'Visitor Services': 'Mobility',
  'Shopping': 'Retail & Services',
  'Professional Services': 'Retail & Services',
  'Relocation': 'Retail & Services',
  'Film Production': 'Retail & Services',
  'Cannabis': 'Retail & Services',
  'Pet Services': 'Retail & Services',
}

// ============================================================
// Schemas
// ============================================================

const LOAD_SCHEMA = {
  type: 'object',
  required: ['clean_records', 'no_weburl_records', 'clean_path'],
  properties: {
    clean_records: { type: 'integer' },
    no_weburl_records: { type: 'integer' },
    clean_path: { type: 'string' },
    no_weburl_path: { type: 'string' },
    metacategory_sample: {
      type: 'object',
      additionalProperties: { type: 'integer' },
      description: 'Quick sanity counter of raw labels in clean',
    },
  },
}

const SCORED_PARTNER_SCHEMA = {
  type: 'object',
  required: ['vgps_id', 'name', 'score', 'tier', 'chain_brand', 'checks'],
  properties: {
    vgps_id: { type: 'string' },
    name: { type: 'string' },
    primary_category: { type: ['string', 'null'] },
    subcategories: { type: 'array', items: { type: 'string' } },
    weburl: { type: ['string', 'null'] },
    chain_brand: { type: 'boolean' },
    chain_brand_evidence: { type: ['string', 'null'] },
    score: { type: 'integer', minimum: 0, maximum: 8 },
    tier: { type: 'string', enum: ['A', 'B', 'C', 'D', 'Z'] },
    checks: {
      type: 'object',
      required: ['site_loads', 'nap_consistent', 'mobile_ready', 'schema_present', 'og_metadata', 'faq_present', 'content_fresh', 'citation_density'],
      properties: {
        site_loads: { type: 'boolean' },
        nap_consistent: { type: 'boolean' },
        mobile_ready: { type: 'boolean' },
        schema_present: { type: 'boolean' },
        og_metadata: { type: 'boolean' },
        faq_present: { type: 'boolean' },
        content_fresh: { type: 'boolean' },
        citation_density: { type: 'boolean' },
        llms_txt_present: { type: 'boolean' },
        gbp_linked: { type: 'boolean' },
        notes: { type: 'string' },
      },
    },
  },
}

// Chunks return CONTROL DATA only — counts, anomalies, the path they wrote.
// The actual scored records are written to chunks/chunk-N.jsonl on disk.
// This is the architectural lesson: large data does NOT cross agent boundaries.
const CHUNK_RESULT_SCHEMA = {
  type: 'object',
  required: ['chunk_index', 'start', 'end', 'scored_count', 'output_path'],
  properties: {
    chunk_index: { type: 'integer' },
    start: { type: 'integer' },       // inclusive
    end: { type: 'integer' },         // exclusive
    scored_count: { type: 'integer' }, // number of records this chunk scored and wrote
    output_path: { type: 'string' },
    errors: { type: 'array', items: { type: 'string' } },
    tier_distribution: {
      type: 'object',
      description: 'Quick tier histogram for this chunk',
      properties: {
        A: { type: 'integer' }, B: { type: 'integer' },
        C: { type: 'integer' }, D: { type: 'integer' },
      },
    },
  },
}

const AGGREGATE_SCHEMA = {
  type: 'object',
  required: ['total_listings', 'unique_businesses', 'tier_counts', 'tier_by_rawlabel_path', 'tier_by_canonical_path', 'tier_by_strategic_path', 'tier_by_subcategory_path', 'chain_vs_indie_path', 'rubric_stats_path', 'csv_path'],
  properties: {
    total_listings: { type: 'integer' },
    unique_businesses: { type: 'integer' },
    tier_counts: {
      type: 'object',
      properties: {
        A: { type: 'integer' }, B: { type: 'integer' },
        C: { type: 'integer' }, D: { type: 'integer' }, Z: { type: 'integer' },
      },
    },
    strategic_summary: {
      type: 'object',
      additionalProperties: {
        type: 'object',
        properties: {
          total: { type: 'integer' },
          unique_businesses: { type: 'integer' },
          mean_score_excluding_Z: { type: 'number' },
          tier_A: { type: 'integer' }, tier_B: { type: 'integer' },
          tier_C: { type: 'integer' }, tier_D: { type: 'integer' }, tier_Z: { type: 'integer' },
        },
      },
    },
    chain_vs_indie: {
      type: 'object',
      properties: {
        chain: { type: 'object', properties: { total: { type: 'integer' }, mean_score: { type: 'number' } } },
        indie: { type: 'object', properties: { total: { type: 'integer' }, mean_score: { type: 'number' } } },
      },
    },
    unmapped_raw_labels: { type: 'array', items: { type: 'string' } },
    tier_by_rawlabel_path: { type: 'string' },
    tier_by_canonical_path: { type: 'string' },
    tier_by_strategic_path: { type: 'string' },
    tier_by_subcategory_path: { type: 'string' },
    chain_vs_indie_path: { type: 'string' },
    rubric_stats_path: { type: 'string' },
    csv_path: { type: 'string' },
    anomalies_summary: { type: 'array', items: { type: 'string' } },
  },
}

// ============================================================
// Helpers
// ============================================================

function chunkRanges(total, nChunks) {
  const ranges = []
  const size = Math.ceil(total / nChunks)
  for (let i = 0; i < nChunks; i++) {
    const start = i * size
    const end = Math.min(total, start + size)
    if (start >= total) break
    ranges.push({ index: i, start, end })
  }
  return ranges
}

// ============================================================
// PHASE: Load — count and plan, no payload transfer
// ============================================================

phase('Load')

const loadResult = await agent(`
You are the LOAD agent for the standalone scoring workflow.

Two source files:
- ${CLEAN_PATH} — JSON array of partners with weburl, ready to score
- ${NO_WEBURL_PATH} — JSONL of partners with no weburl, will be auto Tier Z

Your task is purely accounting — DO NOT load or return record bodies. Just:

1. Read ${CLEAN_PATH} as JSON and count its length.
2. Read ${NO_WEBURL_PATH} and count its lines (each line is one JSON record).
3. Compute a quick metacategory_sample: a dict of primary_category → count
   for the clean records, to confirm the recovery worked and surface any
   surprises before chunking.
4. Ensure ${CHUNKS_DIR}/ exists and is empty (mkdir -p; rm any stale
   chunk-*.jsonl files — those are from earlier broken runs).

Return per LOAD_SCHEMA. Keep the metacategory_sample dict small (every
distinct value, just the counts — no per-record data).
`.trim(), {
  label: 'load:count-and-plan',
  phase: 'Load',
  schema: LOAD_SCHEMA,
})

if (!loadResult) throw new Error('Load returned null — aborting.')
log(`Load: ${loadResult.clean_records} records to score; ${loadResult.no_weburl_records} no-weburl → Tier Z`)

const total = loadResult.clean_records
const N_CHUNKS = Math.max(1, Math.min(14, (args && args.chunks) || 14))
const ranges = chunkRanges(total, N_CHUNKS)
log(`Plan: ${ranges.length} parallel chunks, sizes ${ranges.map(r => r.end - r.start).join(', ')}`)

// ============================================================
// PHASE: Wide scan — chunks read their own slice from disk
// ============================================================

phase('Wide scan')

const chunkResults = await parallel(ranges.map((range) => () =>
  agent(`
You are AUDITOR chunk ${range.index} of ${ranges.length}.

Your job: score the records at indices [${range.start}, ${range.end}) (zero-based, end-exclusive) in ${CLEAN_PATH}. That's ${range.end - range.start} records.

CRITICAL — DO NOT load the full file into your structured output. The file is ~2 MB. Use this Python pattern (or equivalent) to read only your slice:

  import json, sys
  with open("${CLEAN_PATH}") as f:
      all_records = json.load(f)
  my_slice = all_records[${range.start}:${range.end}]

Then for each record in my_slice, score it against the rubric and APPEND the scored record (one JSON object per line) to ${CHUNKS_DIR}/chunk-${range.index}.jsonl.

The rubric — 8 scored dimensions:

1. **Site loads** — GET the weburl with User-Agent "${UA}", timeout 10s. Pass if 200/301/302→200, SSL valid, response time < 5s.
2. **NAP consistency** — fetch the partner's homepage; compare directory-listed name + phone + addressLocality against what's on the site. All three match (allowing trivial formatting differences) → pass.
3. **Mobile-ready** — homepage HTML contains <meta name="viewport" ...>.
4. **Schema markup** — homepage has a <script type="application/ld+json"> block of a relevant @type (LocalBusiness / Hotel / Restaurant / Event / TouristAttraction / Organization / Service / Product, etc.).
5. **OG metadata** — homepage has og:title AND og:description AND og:image.
6. **FAQ or substantive Q&A** — pass if homepage links to /faq, /questions, /help, /support returning 200, OR FAQPage schema exists, OR sitemap reveals one of those paths.
7. **Content freshness** — sitemap lastmod within 6 months (since 2025-12-05), OR visible 2026 blog post, OR JSON-LD dateModified within 6 months, OR copyright year 2026.
8. **Citation density** — partner appears on ≥3 of: Google Business, Yelp, TripAdvisor, OpenTable, Resy, official tourism boards. VGPS counts as 1. Cheap heuristic: quick web search for "{partner name} {city}" and count distinct platforms in results.

Plus two UNSCORED diagnostics:
- llms_txt_present: does {weburl}/llms.txt return 200?
- gbp_linked: does the site link to its Google Business Profile (google.com/maps, g.page)?

**chain_brand** flag:
Domain match against known national/international chain patterns. Be conservative — when in doubt, false.
Hotel families:
- Marriott: marriott.com, marriotthotels, courtyard, fairfield, residenceinn, springhill, jw-marriott, ritzcarlton, sheraton, westin, w-hotels, autograph, gaylord, le-meridien, st-regis, renaissance
- Hilton: hilton.com, doubletree, hampton, embassy-suites, conrad-hotels, waldorfastoria, canopy, curio, tapestry, homewood-suites, home2suites
- Hyatt: hyatt.com, hyattregency, hyattplace, andaz, grand-hyatt, park-hyatt, thompson-hotels, hyatt-house
- IHG: ihg.com, holidayinn, crowneplaza, intercontinental, kimptonhotels (Kimpton is IHG), candlewood, staybridge, hotelindigo
- Wyndham: wyndham, ramada, daysinn, super8, howardjohnson, lq, laquinta, microtel, travelodge, hawthorn
- Choice: choicehotels, comfortinn, qualityinn, sleep-inn, mainstay, econolodge, rodewayinn, ascend
- Best Western, Accor (sofitel, fairmont, raffles, novotel, mgallery, swissotel, mercure), HGVC, Marriott Vacations Worldwide
Restaurant/coffee/retail chains:
- starbucks, panerabread, chipotle, mcdonalds, subway, dunkin, dominos, papajohns, pizzahut, kfc, tacobell, wendys, burgerking, popeyes, chick-fil-a, raisingcanes, in-n-out, jackinthebox, carlsjr, hardees
- olive-garden, redlobster, outback, longhorn, applebees, chilis, ihop, dennys, cracker-barrel, cheesecakefactory, rubytuesday, bj's, buffalowildwings
- peets, philzcoffee, blue-bottle, joe-and-the-juice, sweetgreen, cava, qdoba
- 7-eleven, walgreens, cvs, walmart, target, costco, lowes, homedepot

When chain_brand = true, set chain_brand_evidence to the matched pattern. Otherwise null.

Score: sum of the 8 scored dimensions. Tier:
- 7-8 → A
- 4-6 → B
- 1-3 → C
- 0   → D
(Tier Z is assigned only at Aggregate to records with no weburl — they don't reach this chunk.)

Pass through these fields from input to output: vgps_id, name, primary_category, subcategories (full array), weburl. Add: chain_brand, chain_brand_evidence, score, tier, checks (object with all 10 check booleans + notes string).

Be courteous and resilient:
- 1s delay between hits to the SAME host (different hosts in parallel is fine)
- Timeouts → mark that check false, note in checks.notes
- HTTP errors → checks.notes describes; don't abort the chunk

Write each scored record as one JSON line to ${CHUNKS_DIR}/chunk-${range.index}.jsonl (append-only).

Return per CHUNK_RESULT_SCHEMA. The return value is CONTROL DATA only — counts and paths, not the records themselves.
`.trim(), {
    label: `auditor:chunk-${range.index}`,
    phase: 'Wide scan',
    schema: CHUNK_RESULT_SCHEMA,
  })
))

const completedChunks = chunkResults.filter(Boolean)
const failedChunks = chunkResults.length - completedChunks.length
const totalScored = completedChunks.reduce((s, c) => s + c.scored_count, 0)
log(`Wide scan: ${completedChunks.length}/${chunkResults.length} chunks completed, ${totalScored} records scored`)
if (failedChunks > 0) {
  log(`WARNING: ${failedChunks} chunks returned null (errored or timed out)`)
}
const chunkErrors = completedChunks.flatMap(c => c.errors || [])
if (chunkErrors.length > 0) log(`Within-chunk errors: ${chunkErrors.length}`)

if (totalScored < total * 0.5) {
  throw new Error(`Wide scan covered only ${totalScored}/${total} records (under 50%). Halting per pause-and-flag protocol.`)
}

// ============================================================
// PHASE: Verify — hard gate against silent disk-write failures
//
// Codifies the 2026-06-05 second-order lesson: agent structured-output
// returns can lie about disk side-effects. Before Aggregate trusts the
// per-chunk files, verify_chunks.py confirms every expected chunk file
// exists with the correct slice on disk. If any chunk is missing or has
// the wrong set of vgps_ids, this phase throws and the workflow halts.
//
// Reusable for any workflow with parallel chunk writes — same script,
// different --source / --chunks-dir / --n-chunks.
// ============================================================

phase('Verify')

// Build a manifest of what Wide Scan REPORTED so the verifier can cross-check
// reported vs actual.
const manifestPath = `${AUDIT_DIR}/auditor/_chunk-manifest.json`
const manifest = {
  source: CLEAN_PATH,
  chunks_dir: CHUNKS_DIR,
  n_chunks: ranges.length,
  generated_iso: 'workflow-runtime', // Date.now() is unavailable in workflow body
  chunks: completedChunks.map(c => ({
    index: c.chunk_index,
    start: c.start,
    end: c.end,
    scored_count: c.scored_count,
    output_path: c.output_path,
  })),
}

const verify = await agent(`
You are VERIFY for the standalone scoring workflow.

Wide Scan just claimed to have written ${completedChunks.length} chunk files to ${CHUNKS_DIR}. Codify trust by verifying on disk before Aggregate reads them.

Steps:

1. Write the manifest below to ${manifestPath}:
${JSON.stringify(manifest, null, 2)}

2. Run the reusable verifier:
   /usr/bin/python3 ${AUDIT_DIR}/scripts/verify_chunks.py \\
     --source ${CLEAN_PATH} \\
     --chunks-dir ${CHUNKS_DIR} \\
     --n-chunks ${ranges.length} \\
     --manifest ${manifestPath}

3. Capture stdout AND the exit code.

4. If exit code is 0: return { status: 'pass', exit_code: 0, summary: <one-line summary> }.

5. If exit code is non-zero: return { status: 'fail', exit_code: <code>, summary: <one-paragraph diagnosis>, output: <verbatim stdout/stderr of the verifier> }. Then THROW an Error with the one-line summary so the workflow halts before Aggregate runs against broken data.

This phase MUST halt the workflow on any verification failure. Silent partial data is what the architectural lesson is preventing.
`.trim(), {
  label: 'verify:chunks',
  phase: 'Verify',
  schema: {
    type: 'object',
    required: ['status', 'exit_code'],
    properties: {
      status: { type: 'string', enum: ['pass', 'fail'] },
      exit_code: { type: 'integer' },
      summary: { type: 'string' },
      output: { type: 'string' },
    },
  },
})

if (!verify || verify.status !== 'pass') {
  throw new Error(`Verification failed${verify ? ': ' + (verify.summary || 'see logs') : ' (agent returned null)'}. Halting before Aggregate.`)
}
log(`Verify: ${verify.summary || 'all chunks verified'}`)

// ============================================================
// PHASE: Aggregate — read chunks + Tier Z from disk, emit cuts
// ============================================================

phase('Aggregate')

const aggregate = await agent(`
You are AGGREGATE for the standalone scoring workflow.

Read TAXONOMY-CANONICAL.md at ${AUDIT_DIR}/TAXONOMY-CANONICAL.md for the rationale behind the 3-level taxonomy. The maps to apply are these (paste into your code as dicts):

CANONICAL_MAP:
${JSON.stringify(CANONICAL_MAP, null, 2)}

STRATEGIC_MAP:
${JSON.stringify(STRATEGIC_MAP, null, 2)}

Fallthrough rules:
- A raw label not in CANONICAL_MAP → canonical = "(unmapped: <RAW_LABEL>)", strategic = "(unmapped)". Track in unmapped_raw_labels.
- A null/empty raw primary_category → canonical = "(uncategorized)", strategic = "(uncategorized)".

Inputs on disk:
- ${CHUNKS_DIR}/chunk-*.jsonl — scored records from Wide Scan (~${totalScored} total)
- ${NO_WEBURL_PATH} — records to auto-assign Tier Z (${loadResult.no_weburl_records} records)

Your task — do all of this on disk; the return value is control data only:

1. **Merge** chunk jsonl files + Tier Z records into ${AUDIT_DIR}/auditor/partners-wide-scan.json. For Tier Z records:
   - tier = "Z"
   - score = 0 (placeholder, never scored)
   - chain_brand = false, chain_brand_evidence = null
   - checks = all false, notes = "auto Tier Z — no weburl"
   Every record carries: vgps_id, name, primary_category, subcategories, weburl, chain_brand, chain_brand_evidence, score, tier, checks.

2. **CSV** at ${AUDIT_DIR}/auditor/partners-by-tier.csv with columns:
   vgps_id, name, raw_label, canonical_category, strategic_bucket, chain_brand, score, tier, weburl, listing_url
   Sort by tier (A→B→C→D→Z), then score descending.

3. **Rubric pass rates** at ${AUDIT_DIR}/auditor/rubric-results-per-dimension.json. Compute over A/B/C/D only (Tier Z never scored, excluded from denominators).
   { dimension: { pass_count, pass_rate, n }, ... }

4. **Cut 1 — tier × RAW LABEL** at ${AUDIT_DIR}/auditor/tier-by-rawlabel.json. Every raw metacategory that appeared — no collapsing.
   { "STAY": { total, unique_businesses, mean_score_excluding_Z, tier_A..tier_Z, chain_count, indie_count }, ... }

5. **Cut 2 — tier × CANONICAL CATEGORY** at ${AUDIT_DIR}/auditor/tier-by-canonical.json. Apply CANONICAL_MAP.
   { "Lodging": { ... raw_labels_included: ["STAY", "PLACES TO STAY"] }, ... }

6. **Cut 3 — tier × STRATEGIC BUCKET** at ${AUDIT_DIR}/auditor/tier-by-strategic.json. Apply STRATEGIC_MAP. The 7 expected buckets plus overflow:
   { "Lodging": {...}, "Dining": {...}, "Experiences": {...}, "Wellness": {...}, "Meetings & Events": {...}, "Mobility": {...}, "Retail & Services": {...}, "(unmapped)": {...}, "(uncategorized)": {...} }
   This is the headline view.

7. **Cut 4 — tier × VGPS sub-category** at ${AUDIT_DIR}/auditor/tier-by-subcategory.json. A partner with multiple subcategories counts in each (note in "_note" field).
   { "Hotels|Resorts": { primary_canonical: "Lodging", total, mean_score_excluding_Z, tier_A..tier_Z }, ... }

8. **Cut 5 — chain vs indie** at ${AUDIT_DIR}/auditor/chain-vs-indie.json:
   {
     "chain": { total, unique_businesses, mean_score_excluding_Z, tier_A..tier_Z, by_strategic_bucket: {...} },
     "indie": { total, unique_businesses, mean_score_excluding_Z, tier_A..tier_Z, by_strategic_bucket: {...} }
   }

9. **Headline counts**:
   - total_listings = all scored records (including Tier Z)
   - unique_businesses = distinct weburl values (null weburls count once each)
   - tier_counts = { A, B, C, D, Z }

10. **strategic_summary** for return value — inline Cut 3 so Sat can read headline numbers without opening files.

11. **anomalies_summary** — top 10 from across the run: high counts of (uncategorized), any (unmapped: X) labels with non-trivial counts, chunk errors, etc. Include unmapped_raw_labels as its own field.

Return per AGGREGATE_SCHEMA.
`.trim(), {
  label: 'aggregate:final',
  phase: 'Aggregate',
  schema: AGGREGATE_SCHEMA,
})

if (!aggregate) throw new Error('Aggregate returned null — aborting.')

log('=== Standalone scoring complete ===')
log(`Total listings: ${aggregate.total_listings} | Unique businesses: ${aggregate.unique_businesses}`)
log(`Tier counts: A=${aggregate.tier_counts.A} B=${aggregate.tier_counts.B} C=${aggregate.tier_counts.C} D=${aggregate.tier_counts.D} Z=${aggregate.tier_counts.Z}`)
if (aggregate.strategic_summary) {
  log('Strategic buckets (seven + overflow):')
  for (const [sb, s] of Object.entries(aggregate.strategic_summary)) {
    const mean = s.mean_score_excluding_Z?.toFixed?.(2) ?? s.mean_score_excluding_Z
    log(`  ${sb}: n=${s.total} (unique=${s.unique_businesses}) mean=${mean} | A=${s.tier_A} B=${s.tier_B} C=${s.tier_C} D=${s.tier_D} Z=${s.tier_Z}`)
  }
}
if (aggregate.unmapped_raw_labels && aggregate.unmapped_raw_labels.length) {
  log(`Unmapped raw labels (should be empty after 2026-06-05 taxonomy update): ${aggregate.unmapped_raw_labels.join(', ')}`)
}

return {
  workflow: 'standalone-scoring',
  status: 'complete',
  hold_for_review: true,
  load: loadResult,
  wide_scan: {
    chunks_planned: ranges.length,
    chunks_completed: completedChunks.length,
    chunks_failed: failedChunks,
    records_scored: totalScored,
    within_chunk_errors: chunkErrors.length,
  },
  aggregate,
  next_step: 'HARD HOLD. Sat reviews partners-wide-scan.json, partners-by-tier.csv, tier-by-rawlabel.json, tier-by-canonical.json, tier-by-strategic.json, tier-by-subcategory.json, chain-vs-indie.json, rubric-results-per-dimension.json. NO synthesis, brief drafting, landing-page calibration, or outreach list work until Sat explicitly greenlights the next stage.',
}
