/**
 * VisitGPS Agent-Readiness Audit — Phase 1 workflow (v2, post-run-1 revisions)
 *
 * Revised 2026-06-04 after the partial first run surfaced architectural and
 * data-shape issues. Sat's decisions log (in STATE.md "Decisions log") drives
 * these changes:
 *
 *   1. Aggregate emits THREE levels of metacategory cuts: raw labels,
 *      canonical categories (duplicate-collapsed per TAXONOMY-CANONICAL.md),
 *      and six strategic buckets. CANONICAL_MAP and STRATEGIC_MAP defined as
 *      constants below; unmapped raw labels fall through to "(unmapped: X)"
 *      so new labels never silently disappear.
 *   2. Inventory: Merge applies weburl host-based exclusion for vacation-rental
 *      platforms (airbnb.com, vrbo.com, vacasa.com, smartervacation.rentals,
 *      evolve.com). Excluded records go to inventory-platform-excluded.jsonl
 *      — segregated, not discarded.
 *   3. Aggregate dedupes by weburl for unique_businesses count. Per-listing
 *      scoring is preserved. Both total_listings and unique_businesses
 *      reported.
 *   4. New Tier Z for records with no weburl. Not conflated with Tier D
 *      (scored 0). Reported as its own bucket throughout.
 *   5. Background fetcher from run-1 (pid 65360) was allowed to complete;
 *      its output at scout/inventory-progress.jsonl is the source of truth
 *      for the re-run. Inventory: Spawn is idempotent and skips spawning
 *      if the progress file already covers all candidates.
 *   6. Inventory rebuilt as three explicit stages: Spawn → Wait → Merge.
 *      Each has a bounded job and explicit completion criteria.
 *   7. Wide Scan zero-chunk failure investigation tabled until clean inventory
 *      is available; expected to be a cascade from Inventory's early return.
 *
 * Phase 2 remains deferred. v0 script archived at audit-workflow-v0-archived.js.
 *
 * Invocation:
 *   Workflow({
 *     scriptPath: '/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/audit-workflow.js'
 *   })
 */

export const meta = {
  name: 'visitgps-audit-2026-q2-phase1',
  description: 'AICV agent-readiness audit of Visit Greater Palm Springs — Phase 1 only. v2: 3-stage Inventory (Spawn/Wait/Merge), host-based rental exclusion, dedup by weburl, Tier Z for no-web records, 3-level taxonomy reporting (raw/canonical/strategic).',
  phases: [
    { title: 'Scout', detail: 'Sitemap fetch + slug-based rental pruning' },
    { title: 'Inventory: Spawn', detail: 'Launch background fetcher if not already running/complete (idempotent)' },
    { title: 'Inventory: Wait', detail: 'Poll progress file until fetcher exits with full coverage' },
    { title: 'Inventory: Merge', detail: 'Apply weburl-host + subcategory exclusions; segregate platform-listings; emit clean inventory' },
    { title: 'Wide scan', detail: 'Parallel rubric checks against partner websites' },
    { title: 'Aggregate', detail: '3-level taxonomy cuts, Tier Z, chain-vs-indie, unique-business dedup' },
  ],
}

// ============================================================
// Constants
// ============================================================

const AUDIT_DIR = '/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2'
const BASE_URL = 'https://www.visitgreaterpalmsprings.com'
const UA = 'AICV-Audit/2026Q2 (+https://aicoachellavalley.org)'

// Vacation-rental platform hosts — Inventory: Merge excludes records whose
// weburl host matches any of these. Excluded records go to a segregated
// file (not dropped). Aggregator hosts (booking.com, expedia.com, hotels.com)
// are NOT in this list — those route to Tier Z via the "no real partner site"
// path so they don't get conflated with rentals.
const RENTAL_PLATFORM_HOSTS = [
  'airbnb.com', 'abnb.me',
  'vrbo.com', 'homeaway.com',
  'vacasa.com',
  'smartervacation.rentals',
  'evolve.com',
]

// Canonical mapping — see TAXONOMY-CANONICAL.md for full rationale.
// Updated 2026-06-05: added GOLF, HIKING TRAILS → Outdoor Recreation,
// SPAS BEAUTY & WELLNESS → Wellness (new strategic bucket), VISITOR
// INFORMATION, FILM PRODUCTION SERVICES, CANNABIS, DOG-FRIENDLY RESOURCES.
// Unmapped raw labels fall through to "(unmapped: <RAW_LABEL>)" so new
// VGPS labels never silently disappear.
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

// Strategic bucket rollup — SEVEN high-level buckets above canonical.
// Wellness promoted from canonical category to its own strategic bucket
// 2026-06-05 (224 records in inventory; aligned with AICV's documented
// content-gap priority). Same fallthrough rule: a canonical category not
// in this map → "(unmapped)".
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

// Phase 2/3 are deferred. Guard against accidental Phase 2 invocation
// against this script (the v0 script handled it; this one does not).
if (args && args.phase && args.phase !== 1) {
  throw new Error(
    'audit-workflow.js is locked to Phase 1. Phase 2 was held by Sat on 2026-06-04 ' +
    'pending review of Phase 1 results. Do not pass args.phase to this script.'
  )
}

// ============================================================
// Schemas
// ============================================================

const SCOUT_SCHEMA = {
  type: 'object',
  required: ['total_in_sitemap', 'pruned_by_slug', 'candidates', 'candidates_path'],
  properties: {
    total_in_sitemap: { type: 'integer' },
    pruned_by_slug: { type: 'integer' },
    candidates: { type: 'integer' },
    candidates_path: { type: 'string' },
    sample_pruned_slugs: { type: 'array', items: { type: 'string' } },
  },
}

const PARTNER_RECORD_SCHEMA = {
  type: 'object',
  required: ['vgps_id', 'name', 'listing_url'],
  properties: {
    vgps_id: { type: 'string' },
    slug: { type: 'string' },
    name: { type: 'string' },
    primary_category: { type: ['string', 'null'] },
    subcategories: { type: 'array', items: { type: 'string' } },
    listing_url: { type: 'string' },
    weburl: { type: ['string', 'null'] },
    phone: { type: ['string', 'null'] },
    tollfree: { type: ['string', 'null'] },
    email: { type: ['string', 'null'] },
    address: { type: ['string', 'null'] },
    addressLocality: { type: ['string', 'null'] },
    addressRegion: { type: ['string', 'null'] },
    schema_type: { type: ['string', 'null'] },
  },
}

// Three Inventory stages, each with explicit completion criteria.
const INVENTORY_SPAWN_SCHEMA = {
  type: 'object',
  required: ['status', 'candidates_total', 'progress_count_at_spawn'],
  properties: {
    // 'launched' = new fetcher started; 'already_running' = found a live pid;
    // 'already_complete' = progress file covers all candidates; 'resumed' = bg started for remainder.
    status: { type: 'string', enum: ['launched', 'already_running', 'already_complete', 'resumed'] },
    candidates_total: { type: 'integer' },
    progress_count_at_spawn: { type: 'integer' },
    fetcher_pid: { type: ['integer', 'null'] },
    log_path: { type: 'string' },
  },
}

const INVENTORY_WAIT_SCHEMA = {
  type: 'object',
  required: ['status', 'final_count', 'candidates_total', 'wait_seconds'],
  properties: {
    // 'complete' = process exited AND progress count == candidates (allowing for transient failures).
    // 'timeout' = hit hard timeout before completion. 'process_died_short' = exited early with gap.
    status: { type: 'string', enum: ['complete', 'timeout', 'process_died_short'] },
    final_count: { type: 'integer' },
    candidates_total: { type: 'integer' },
    coverage_pct: { type: 'number' },
    wait_seconds: { type: 'integer' },
    missing_sample: { type: 'array', items: { type: 'string' }, description: 'up to 10 candidate URLs not in progress' },
  },
}

const INVENTORY_MERGE_SCHEMA = {
  type: 'object',
  required: ['total_in_progress', 'kept_for_scoring', 'platform_excluded', 'subcategory_excluded', 'public_art_excluded', 'no_weburl', 'clean_path'],
  properties: {
    total_in_progress: { type: 'integer' },
    kept_for_scoring: { type: 'integer' },         // has weburl AND not a rental — feeds Wide Scan
    no_weburl: { type: 'integer' },                // routed straight to Tier Z, skip Wide Scan
    platform_excluded: { type: 'integer' },        // weburl host matches RENTAL_PLATFORM_HOSTS
    subcategory_excluded: { type: 'integer' },     // subcategory contains rental keyword
    public_art_excluded: { type: 'integer' },      // artsGPS subcategory + no weburl (public art, not businesses)
    clean_path: { type: 'string' },
    platform_excluded_path: { type: 'string' },
    subcategory_excluded_path: { type: 'string' },
    no_weburl_path: { type: 'string' },
    public_art_excluded_path: { type: 'string' },
    raw_metacategory_counts: { type: 'object', additionalProperties: { type: 'integer' } },
    anomalies: { type: 'array', items: { type: 'string' } },
  },
}

const SCORED_PARTNER_SCHEMA = {
  type: 'object',
  required: ['vgps_id', 'name', 'score', 'tier', 'chain_brand', 'checks'],
  properties: {
    vgps_id: { type: 'string' },
    name: { type: 'string' },
    primary_category: { type: ['string', 'null'] },          // VGPS raw metacategory label
    subcategories: { type: 'array', items: { type: 'string' } }, // pass-through; enables sub-category cuts at Aggregate
    weburl: { type: ['string', 'null'] },
    chain_brand: { type: 'boolean' },                        // weburl matches a known chain pattern
    chain_brand_evidence: { type: ['string', 'null'] },      // matched pattern, for auditability
    score: { type: 'integer', minimum: 0, maximum: 8 },
    // Tier Z = no weburl (auto-assigned, never scored). A/B/C/D as before.
    tier: { type: 'string', enum: ['A', 'B', 'C', 'D', 'Z'] },
    checks: {
      type: 'object',
      required: [
        'site_loads', 'nap_consistent', 'mobile_ready', 'schema_present',
        'og_metadata', 'faq_present', 'content_fresh', 'citation_density',
      ],
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

const WIDE_SCAN_CHUNK_SCHEMA = {
  type: 'object',
  required: ['chunk_index', 'partners'],
  properties: {
    chunk_index: { type: 'integer' },
    partners: { type: 'array', items: SCORED_PARTNER_SCHEMA },
    errors: { type: 'array', items: { type: 'string' } },
  },
}

const AGGREGATE_SCHEMA = {
  type: 'object',
  required: [
    'total_listings', 'unique_businesses', 'tier_counts',
    'tier_by_rawlabel_path', 'tier_by_canonical_path', 'tier_by_strategic_path',
    'tier_by_subcategory_path', 'chain_vs_indie_path', 'rubric_stats_path', 'csv_path',
  ],
  properties: {
    total_listings: { type: 'integer' },           // every record, including multi-listing same-business
    unique_businesses: { type: 'integer' },        // deduped by weburl (null-weburl counted once each)
    tier_counts: {
      type: 'object',
      properties: {
        A: { type: 'integer' }, B: { type: 'integer' },
        C: { type: 'integer' }, D: { type: 'integer' }, Z: { type: 'integer' },
      },
    },
    strategic_summary: {                           // headline inline summary for the report
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
    unmapped_raw_labels: { type: 'array', items: { type: 'string' } },  // any RAW labels not in CANONICAL_MAP
    tier_by_rawlabel_path: { type: 'string' },     // every raw label, no collapsing
    tier_by_canonical_path: { type: 'string' },    // duplicate-collapsed (STAY ⇄ PLACES TO STAY etc.)
    tier_by_strategic_path: { type: 'string' },    // six strategic buckets
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

function chunkArray(arr, size) {
  const out = []
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size))
  return out
}

// ============================================================
// PHASE: Scout
// ============================================================

phase('Scout')
log('Fetching VGPS sitemap and pruning obvious vacation-rental slugs.')

const scout = await agent(`
You are SCOUT for Phase 1 of the VGPS agent-readiness audit.

Read these for context (do not re-derive):
- ${AUDIT_DIR}/SPEC.md — full audit design
- ${AUDIT_DIR}/scout/DRY-RUN-2026-06-04.md — confirmed sitemap structure
- ${AUDIT_DIR}/scout/spike-2026-06-04-extraction.json — confirmed per-listing extraction shape

Your task:
1. curl ${BASE_URL}/sitemap.xml with User-Agent "${UA}". Save raw to ${AUDIT_DIR}/scout/sitemap-2026-06-04.xml.
2. Extract every <loc> matching the pattern /listing/{slug}/{numeric-id}/.
3. PRUNE obvious vacation-rental slugs. Apply ALL of these patterns (case-insensitive on the slug portion of the URL):
   - Contains: 'hosted-by', 'acme-house', 'vacasa', 'airbnb', 'vrbo', 'ryson-desert', 'desert-vacations'
   - Bed/bath/sleeps codes: matches /\\b[0-9]bd-[0-9]/, /\\b[0-9]br-[0-9]/, /sleeps-[0-9]/, /\\b[0-9]-bed-[0-9]/
   - Numeric/code prefixes: matches /^[0-9]+-rvc/, /^[0-9]{4,}-/
   - Rental amenity keywords: 'pool-spa', 'firepit', 'fire-pit', 'gameroom', 'game-room', 'casita', 'guesthouse', 'guest-house', 'vacation-rental', 'king-bed', '-bd-', '-ba-'
4. Save the pruned URL set to ${AUDIT_DIR}/scout/listing-urls.json as:
   {
     "fetched_at_iso": <use Bash 'date -Iseconds'>,
     "total_in_sitemap": <int>,
     "pruned_by_slug": <int>,
     "candidates": [
       { "vgps_id": "23341", "slug": "the-living-desert", "listing_url": "https://www.visitgreaterpalmsprings.com/listing/the-living-desert/23341/" },
       ...
     ]
   }
5. Save the pruned slugs (just the IDs and slugs that were dropped) to ${AUDIT_DIR}/scout/pruned-by-slug.json for auditability.

Return: { total_in_sitemap, pruned_by_slug, candidates: <count>, candidates_path, sample_pruned_slugs: <10 pruned slugs as evidence> }.

Be efficient — only one HTTP call (the sitemap). Use bash + python3 for parsing.

**Pause-and-flag protocol**: if you discover the sitemap structure has changed materially since the dry-run (e.g. it's now a sitemap index pointing to nested files, or the URL pattern has shifted, or the total listing count diverges by more than 20% from the dry-run's 4,472), DO NOT improvise — append a clear description of the anomaly to ${AUDIT_DIR}/STATE.md under a new "## Anomalies" section and throw an Error with a one-line summary. The workflow will halt and surface the issue.
`.trim(), {
  label: 'scout:filter-rentals',
  phase: 'Scout',
  schema: SCOUT_SCHEMA,
})

if (!scout) throw new Error('Scout returned null — aborting.')
log(`Scout: ${scout.total_in_sitemap} listings in sitemap, pruned ${scout.pruned_by_slug} by slug heuristics, ${scout.candidates} candidates remain`)

// ============================================================
// PHASE: Inventory — Spawn / Wait / Merge (three explicit stages)
//
// The single-agent design from v1 broke because a single agent can't sit on
// a 2-hour sequential fetch loop without being forced to return early. The
// fix is to externalize the slow work to a Python background process and
// have explicit Spawn / Wait / Merge agents around it. Each agent has a
// bounded job and an explicit completion criterion.
// ============================================================

phase('Inventory: Spawn')

const spawn = await agent(`
You are INVENTORY: SPAWN for the VGPS audit.

Read ${AUDIT_DIR}/scout/listing-urls.json to know the candidate set.

Goal: ensure a background fetcher is producing per-listing extraction records
at ${AUDIT_DIR}/scout/inventory-progress.jsonl, OR confirm the existing
progress file already covers all candidates.

Steps:

1. Count candidates: total = candidates.length from listing-urls.json.
2. Count progress: lines in ${AUDIT_DIR}/scout/inventory-progress.jsonl (file may not exist yet).
3. If progress count >= total AND each vgps_id in candidates appears in progress
   → status = 'already_complete'. Done. Return.
4. Check for a live fetcher process. The v1 run left scout/inventory_fetch.py
   in place — check for any python3 process running it with:
     pgrep -f inventory_fetch.py
   If a pid is alive → status = 'already_running'. Return its pid.
5. Otherwise we need to launch (or resume) the fetcher:
   - The fetcher script at ${AUDIT_DIR}/scout/inventory_fetch.py from v1 has
     resume support (skips vgps_ids already in inventory-progress.jsonl).
     If it exists and matches the current candidate set's path, reuse it.
   - If it doesn't exist OR has bugs, write/replace it. It must:
     - Read ${AUDIT_DIR}/scout/listing-urls.json
     - Read ${AUDIT_DIR}/scout/inventory-progress.jsonl if present and SKIP
       vgps_ids already done
     - For each remaining candidate, curl with User-Agent "${UA}", 2s delay
     - Extract from the listing HTML:
       * weburl (regex /"weburl"\\s*:\\s*"(https?:\\/\\/[^"]+)"/)
       * phone, tollfree (may be null), email (may be null)
       * ALL "catname" values; the first match for the RELAXED metacategory
         regex /^[A-Z\\s&,\\-']+$/ is primary_category; all others go to subcategories[].
         (Relaxed 2026-06-05 from /^[A-Z &]+$/ to allow comma, hyphen, and
         apostrophe — recovers SPAS, BEAUTY & WELLNESS / DOG-FRIENDLY RESOURCES
         and future labels with similar punctuation.)
       * From schema.org JSON-LD: @type, name, address fields, geo
     - Append one JSON object per line to inventory-progress.jsonl
     - Log every 100 listings to scout/inventory-fetch.log
   - Launch as: nohup python3 -u scout/inventory_fetch.py > scout/inventory-fetch.log 2>&1 &
   - Capture the pid via: echo $!
6. Set status = 'launched' (fresh start) or 'resumed' (progress file exists but incomplete).

Return: {
  status: 'launched' | 'already_running' | 'already_complete' | 'resumed',
  candidates_total: <int>,
  progress_count_at_spawn: <int>,
  fetcher_pid: <int or null if already_complete>,
  log_path: "${AUDIT_DIR}/scout/inventory-fetch.log"
}.

DO NOT block on the fetcher's progress. The Wait stage will handle polling.
This stage must complete in well under a minute regardless of fetcher state.
`.trim(), {
  label: 'inventory:spawn',
  phase: 'Inventory: Spawn',
  schema: INVENTORY_SPAWN_SCHEMA,
})

if (!spawn) throw new Error('Inventory: Spawn returned null — aborting.')
log(`Spawn: status=${spawn.status}, progress=${spawn.progress_count_at_spawn}/${spawn.candidates_total}, pid=${spawn.fetcher_pid ?? 'n/a'}`)

phase('Inventory: Wait')

const waitResult = await agent(`
You are INVENTORY: WAIT for the VGPS audit.

Inputs from prior stage:
- candidates_total: ${spawn.candidates_total}
- spawn status was: ${spawn.status}
- fetcher_pid (if known): ${spawn.fetcher_pid ?? 'unknown'}
- progress file: ${AUDIT_DIR}/scout/inventory-progress.jsonl
- log: ${spawn.log_path}

Goal: wait until the background fetcher is done (or until it's clear the run
is stuck/dead), without burning agent budget.

If spawn.status was 'already_complete', skip the wait entirely and return
status='complete' immediately.

Otherwise poll. Recommended polling strategy:

  start_time=\$(date +%s)
  HARD_TIMEOUT=14400   # 4 hours
  STABLE_CHECKS=0
  prev_count=0
  while true; do
    count=\$(wc -l < ${AUDIT_DIR}/scout/inventory-progress.jsonl 2>/dev/null || echo 0)
    pid_alive=\$(pgrep -f inventory_fetch.py | head -1)
    elapsed=\$(( \$(date +%s) - start_time ))

    # Done condition: progress meets candidates AND process exited
    if [ "\$count" -ge ${spawn.candidates_total} ] && [ -z "\$pid_alive" ]; then
      echo "COMPLETE: count=\$count pid_alive='' elapsed=\$elapsed"
      break
    fi

    # Process died but progress is short: process_died_short
    if [ -z "\$pid_alive" ] && [ "\$count" -lt ${spawn.candidates_total} ]; then
      gap=\$(( ${spawn.candidates_total} - count ))
      # Tolerate up to 1% gap (404s, parse failures recorded as anomalies)
      if [ \$gap -le \$(( ${spawn.candidates_total} / 100 )) ]; then
        echo "COMPLETE_WITH_GAP: count=\$count gap=\$gap elapsed=\$elapsed"
        break
      else
        echo "PROCESS_DIED_SHORT: count=\$count gap=\$gap elapsed=\$elapsed"
        break
      fi
    fi

    # Timeout
    if [ \$elapsed -gt \$HARD_TIMEOUT ]; then
      echo "TIMEOUT: count=\$count elapsed=\$elapsed"
      break
    fi

    # Sanity: if count hasn't moved for 10 consecutive checks (10 min total),
    # something's wrong — surface it
    if [ "\$count" = "\$prev_count" ]; then
      STABLE_CHECKS=\$(( STABLE_CHECKS + 1 ))
      if [ \$STABLE_CHECKS -ge 10 ]; then
        echo "STALLED: count stuck at \$count for 10 consecutive checks (10 min)"
        break
      fi
    else
      STABLE_CHECKS=0
    fi
    prev_count=\$count
    sleep 60
  done

Use Bash with run_in_background=false for the polling loop above (it sleeps
inside a single Bash invocation; the workflow tool tolerates long Bash calls
better than long sleep loops driven by the agent runtime).

When the loop exits, compute:
- final_count = wc -l of inventory-progress.jsonl
- coverage_pct = 100 * final_count / candidates_total
- wait_seconds = elapsed
- status:
    'complete' if final_count >= candidates_total - 1% gap (within tolerance) AND process exited
    'process_died_short' if process exited with > 1% gap
    'timeout' if HARD_TIMEOUT hit
- missing_sample: if status is 'process_died_short' or 'timeout', list up to 10 candidate URLs whose vgps_ids are NOT in inventory-progress.jsonl

Return per INVENTORY_WAIT_SCHEMA.

THROW if status != 'complete'. The workflow halts. Sat reviews and decides
whether to resume (re-invoking this workflow re-enters Spawn which will pick
up where the fetcher left off).
`.trim(), {
  label: 'inventory:wait',
  phase: 'Inventory: Wait',
  schema: INVENTORY_WAIT_SCHEMA,
})

if (!waitResult) throw new Error('Inventory: Wait returned null — aborting.')
log(`Wait: status=${waitResult.status}, ${waitResult.final_count}/${waitResult.candidates_total} (${waitResult.coverage_pct?.toFixed?.(1) ?? waitResult.coverage_pct}%), elapsed ${waitResult.wait_seconds}s`)
if (waitResult.status !== 'complete') {
  throw new Error(`Inventory fetcher did not complete cleanly (status=${waitResult.status}). See STATE.md and inventory-fetch.log. Halting per pause-and-flag protocol.`)
}

phase('Inventory: Merge')

const merge = await agent(`
You are INVENTORY: MERGE for the VGPS audit.

Inputs:
- ${AUDIT_DIR}/scout/inventory-progress.jsonl — ${waitResult.final_count} records produced by the fetcher.

Goal: apply data-shape decisions (host-based rental exclusion, subcategory
rental exclusion, no-weburl segregation) and produce the inventory files that
Wide Scan and Aggregate consume.

For each record in inventory-progress.jsonl, classify into ONE of FIVE buckets:

A. **public_art_excluded** — subcategories contains 'artsGPS' AND weburl is empty.
   VGPS lists public art (sculptures, murals, road-sign installations) as
   listings, but they aren't partner businesses. Added 2026-06-05 per Sat's
   decision. Write to ${AUDIT_DIR}/scout/inventory-public-art-excluded.jsonl.

B. **platform_excluded** — weburl host (parsed via urllib.parse.urlparse or
   regex) ends in one of these (case-insensitive):
     ${JSON.stringify(RENTAL_PLATFORM_HOSTS)}
   Host comparison should match both bare domain and any subdomain
   (e.g. www.airbnb.com, m.vrbo.com both match).
   Write to ${AUDIT_DIR}/scout/inventory-platform-excluded.jsonl.

C. **subcategory_excluded** — any subcategory value contains (case-insensitive)
   one of: "vacation rental", "vacation home", "vacation homes", "timeshare",
   "timeshares", "rv resort", "rv resorts", "rv park", "rv parks".
   Write to ${AUDIT_DIR}/scout/excluded-rentals.jsonl.

D. **no_weburl** — weburl is null/empty/missing (and not already in public_art).
   These get auto-assigned Tier Z at Aggregate (never go to Wide Scan).
   Write to ${AUDIT_DIR}/scout/inventory-no-weburl.jsonl.

E. **kept_for_scoring** — has a usable weburl AND not a rental.
   Write to ${AUDIT_DIR}/scout/partner-directory-clean.json as a JSON array
   (one of the few outputs that's an array file rather than jsonl, because
   Wide Scan reads it whole).

A record falls into the FIRST matching bucket in the order A → B → C → D → E.

Also compute raw_metacategory_counts: a dict of primary_category (raw label as emitted) → count, across ALL records in inventory-progress.jsonl. This becomes the canonical-mapping pre-flight check for Aggregate.

Anomalies to report (in the anomalies array):
- Any new raw metacategory labels not present in the v1 partial run (the v1 partial saw 17+: STAY, PLACES TO STAY, EAT & DRINK, MEETING & EVENT RESOURCES, GETTING HERE, GETTING HERE & AROUND, SHOPPING, RELOCATION & RESOURCES, THINGS TO DO, GROUP VENUES, ARTS & CULTURE, WEDDINGS, BUSINESS & PROFESSIONAL SERVICES, CASINOS & ENTERTAINMENT, ACTIVITIES & RECREATION, TOURS — flag anything beyond this list as "NEW RAW LABEL: <label>" so Sat can add it to TAXONOMY-CANONICAL.md)
- High platform_excluded count (> 5% of total)
- High no_weburl count (> 20% of total)
- Records with no primary_category AND no subcategories (likely VGPS data stubs)

Return per INVENTORY_MERGE_SCHEMA.
`.trim(), {
  label: 'inventory:merge',
  phase: 'Inventory: Merge',
  schema: INVENTORY_MERGE_SCHEMA,
})

if (!merge) throw new Error('Inventory: Merge returned null — aborting.')
log(`Merge: ${merge.kept_for_scoring} kept for scoring, ${merge.platform_excluded} platform-excluded, ${merge.subcategory_excluded} subcategory-excluded, ${merge.no_weburl} no-weburl (→ tier Z)`)
if (merge.anomalies && merge.anomalies.length) {
  log(`Merge anomalies (${merge.anomalies.length}):`)
  merge.anomalies.slice(0, 5).forEach(a => log(`  - ${a}`))
}

// ============================================================
// PHASE: Wide scan
// ============================================================

phase('Wide scan')

// partner-directory-clean.json from Merge contains ONLY records with weburl
// that are not rentals. no-weburl records (Tier Z) and platform/subcategory
// rentals are in separate files and don't get scored.
const invRead = await agent(`
Read ${AUDIT_DIR}/scout/partner-directory-clean.json (a JSON array file written by Inventory: Merge). Return { partners: [...full array...] }.

All records in this file have a non-null weburl and have already been filtered
through the platform-host and subcategory rental exclusions. Pass them through verbatim.
`.trim(), {
  label: 'wide-scan:load',
  phase: 'Wide scan',
  schema: {
    type: 'object',
    required: ['partners'],
    properties: {
      partners: { type: 'array', items: PARTNER_RECORD_SCHEMA },
    },
  },
})

if (!invRead) throw new Error('Failed to read inventory.')
const scoreable = invRead.partners
const N_CHUNKS = Math.min(14, Math.max(1, Math.ceil(scoreable.length / 50)))  // cap chunk count, aim ~250/chunk
const CHUNK_SIZE = Math.max(1, Math.ceil(scoreable.length / N_CHUNKS))
const chunks = chunkArray(scoreable, CHUNK_SIZE)
log(`Wide scan: ${scoreable.length} partners with weburl across ${chunks.length} parallel chunks (~${CHUNK_SIZE} each). ${merge.no_weburl} no-weburl records bypass Wide Scan and route to Tier Z at Aggregate.`)

const chunkResults = await parallel(chunks.map((chunkPartners, i) => () =>
  agent(`
You are AUDITOR chunk ${i} of ${chunks.length} for Phase 1 of the VGPS audit.

Read ${AUDIT_DIR}/SPEC.md section "Phase 1 scoring rubric (0-8)" for the rubric definition. Score each of these ${chunkPartners.length} partners against it.

Your partners (JSON, ${chunkPartners.length} records):
${JSON.stringify(chunkPartners, null, 2)}

For each partner:

1. **Site loads** — GET the weburl with User-Agent "${UA}", timeout 10s. Pass if 200/301/302 chain ending in 200, SSL cert valid, response time < 5s. (Be courteous: 1s delay between hits to the SAME partner host. Different hosts in parallel is fine.)
2. **NAP consistency** — compare the partner's directory-listed name + phone + address-locality against what appears on the website. Fetch the homepage; if the name, phone, and city all match (allowing trivial formatting differences) → pass.
3. **Mobile-ready** — homepage HTML contains <meta name="viewport" ...>.
4. **Schema markup** — homepage HTML contains a <script type="application/ld+json"> block of a relevant @type (LocalBusiness / Hotel / Restaurant / Event / TouristAttraction / Organization / Service / Product, etc.).
5. **OG metadata** — homepage HTML has og:title AND og:description AND og:image (all three present).
6. **FAQ or substantive Q&A** — pass if the homepage links to a /faq, /questions, /help, /support page that returns 200, OR if there's FAQPage schema in the JSON-LD, OR if a sitemap.xml on the partner site reveals one of those paths.
7. **Content freshness** — pass if any of: sitemap.xml lastmod within last 6 months (since 2025-12-04); blog or news section with a 2026 post; JSON-LD dateModified within last 6 months; visible copyright year of 2026.
8. **Citation density** — pass if the partner appears on ≥3 of: Google Business Profile, Yelp, TripAdvisor, OpenTable, Resy, official tourism boards (VGPS itself counts). Use the partner's name + city to search. Acceptable signals: VGPS listing exists (trivially yes for our corpus), + Yelp page exists + Google Maps page exists = 3.

Record these UNSCORED dimensions for analysis but don't add to score:
- llms_txt_present: does {weburl}/llms.txt return 200?
- gbp_linked: does the site link to its Google Business Profile (e.g. via a "Reviews" button to google.com/maps or g.page)?

ALSO record (per the courier directive — captured cheap now, refined in synthesis):

**chain_brand** (boolean) — does the weburl match a known national/international chain pattern? Apply these seed patterns case-insensitively against the weburl's hostname; this list is intentionally non-exhaustive — use judgment if the domain obviously belongs to a major chain even when not listed.

  Hotel families:
  - Marriott: marriott.com, marriotthotels, courtyard, fairfield, residenceinn, springhill, jw-marriott, ritzcarlton, sheraton, westin, w-hotels, autograph, gaylord, le-meridien, st-regis, renaissance
  - Hilton: hilton.com, doubletree, hampton, embassy-suites, conrad-hotels, waldorfastoria, canopy, curio, tapestry, homewood-suites, home2suites
  - Hyatt: hyatt.com, hyattregency, hyattplace, andaz, grand-hyatt, park-hyatt, thompson-hotels, hyatt-house
  - IHG: ihg.com, holidayinn, crowneplaza, intercontinental, kimptonhotels (Kimpton is IHG), candlewood, staybridge, hotelindigo
  - Wyndham: wyndham, ramada, daysinn, super8, howardjohnson, lq, laquinta, microtel, travelodge, hawthorn
  - Choice: choicehotels, comfortinn, qualityinn, sleep-inn, mainstay, econolodge, rodewayinn, ascend
  - Best Western: bestwestern.com
  - Accor: accor.com, sofitel, fairmont, raffles, novotel, mgallery, swissotel, mercure
  - Disney/Universal/timeshare brands at scale: disneyhotels, hgvc.com (Hilton Grand Vacations), marriottvacationsworldwide
  Restaurant/coffee/retail chains:
  - starbucks, panerabread, chipotle, mcdonalds, subway, dunkin, dominos, papajohns, pizzahut, kfc, tacobell, wendys, burgerking, popeyes, chick-fil-a, raisingcanes, in-n-out, jackinthebox, carlsjr, hardees
  - olive-garden, redlobster, outback, longhorn, applebees, chilis, ihop, dennys, cracker-barrel, cheesecakefactory, rubytuesday, bj's, buffalowildwings
  - Major fast-casual / coffee: peets, philzcoffee, blue-bottle, joe-and-the-juice, sweetgreen, cava, qdoba
  Other major service-chain patterns: any domain that looks like a Fortune-500 national operator.

  When chain_brand = true, set chain_brand_evidence to the matched pattern (e.g. "marriott.com" or "hilton family / doubletree") for auditability.
  When chain_brand = false, set chain_brand_evidence = null.

  Be conservative: when in doubt (small regional groups, single-brand-but-not-national, ambiguous domains), set false. Refinement happens later.

Score = sum of the 8 scored dimensions. Tier:
- 7-8 → A
- 4-6 → B
- 1-3 → C
- 0 → D

Be courteous and resilient:
- 1s delay between hits to the same host. Parallel across different hosts is fine.
- Timeouts → mark that check false, set notes accordingly.
- Append each scored record to ${AUDIT_DIR}/auditor/chunks/chunk-${i}.jsonl as you go, so partial progress survives.

In each scored record, PASS THROUGH from the input partner record: primary_category (VGPS metacategory) AND subcategories (full array). Both are needed at Aggregate for the two-axis cut Sat requested.

Return: { chunk_index: ${i}, partners: [...scored records matching the schema...], errors: [...] }.
`.trim(), {
    label: `auditor:chunk-${i}`,
    phase: 'Wide scan',
    schema: WIDE_SCAN_CHUNK_SCHEMA,
  })
))

const scoredFromChunks = chunkResults.filter(Boolean).flatMap(r => r.partners)
const chunkErrors = chunkResults.filter(Boolean).flatMap(r => r.errors || [])
log(`Wide scan: ${scoredFromChunks.length} partners scored. ${chunkErrors.length} chunk-level errors.`)

// ============================================================
// PHASE: Aggregate
// ============================================================

phase('Aggregate')

const aggregate = await agent(`
You are AGGREGATE for Phase 1 of the VGPS audit.

Read TAXONOMY-CANONICAL.md at ${AUDIT_DIR}/TAXONOMY-CANONICAL.md for the rationale behind the 3-level taxonomy you'll emit. The canonical and strategic maps to apply are exactly these (paste these into your code as dicts):

CANONICAL_MAP (raw VGPS label → canonical category):
${JSON.stringify(CANONICAL_MAP, null, 2)}

STRATEGIC_MAP (canonical category → strategic bucket):
${JSON.stringify(STRATEGIC_MAP, null, 2)}

Fallthrough rules:
- A raw label not in CANONICAL_MAP → canonical = "(unmapped: <RAW_LABEL>)", strategic = "(unmapped)". Track every unmapped raw label in unmapped_raw_labels for the return value.
- A null raw primary_category → canonical = "(uncategorized)", strategic = "(uncategorized)".

Inputs available on disk:
- ${AUDIT_DIR}/auditor/chunks/chunk-*.jsonl — per-chunk scored records from Wide Scan (${scoredFromChunks.length} records expected).
- ${AUDIT_DIR}/scout/inventory-no-weburl.jsonl — records with no weburl; auto-assigned Tier Z (NEVER tier D).
- ${AUDIT_DIR}/scout/partner-directory-clean.json — the input that Wide Scan saw (for cross-check).

Your task:

1. **Merge** chunk jsonl files + Tier Z records into a single canonical scored file at ${AUDIT_DIR}/auditor/partners-wide-scan.json. For Tier Z records:
   - tier = "Z"
   - score = 0  (still record as 0 to keep field shape consistent, but they're never SCORED)
   - chain_brand = false, chain_brand_evidence = null
   - checks = all false, notes = "auto Tier Z — no weburl"
   Every record carries: vgps_id, name, primary_category (raw), subcategories array, weburl, chain_brand, chain_brand_evidence, score, tier, checks.

2. **CSV** at ${AUDIT_DIR}/auditor/partners-by-tier.csv with columns:
   vgps_id, name, raw_label, canonical_category, strategic_bucket, chain_brand, score, tier, weburl, listing_url
   Sort by tier (A→B→C→D→Z), then score descending.

3. **Rubric pass rates** per dimension at ${AUDIT_DIR}/auditor/rubric-results-per-dimension.json. Compute over A/B/C/D only (Tier Z records are NOT counted in pass-rate denominators — they were never scored).
   { dimension: { pass_count, pass_rate, n }, ... }

4. **Cut 1 — tier × RAW LABEL** at ${AUDIT_DIR}/auditor/tier-by-rawlabel.json. Every raw metacategory string that appeared in the inventory gets its own entry — no collapsing. Shape:
   { "STAY": { total, unique_businesses, mean_score_excluding_Z, tier_A, tier_B, tier_C, tier_D, tier_Z, chain_count, indie_count }, "PLACES TO STAY": {...}, "(uncategorized)": {...}, ... }
   (unique_businesses = count of distinct weburl values within this bucket; null weburls count as 1 each.)

5. **Cut 2 — tier × CANONICAL CATEGORY** at ${AUDIT_DIR}/auditor/tier-by-canonical.json. Apply CANONICAL_MAP to collapse raw labels:
   { "Lodging": { total, unique_businesses, mean_score_excluding_Z, tier_A, tier_B, tier_C, tier_D, tier_Z, chain_count, indie_count, raw_labels_included: ["STAY", "PLACES TO STAY"] }, "Dining": {...}, "(unmapped: SOMETHING)": {...} }

6. **Cut 3 — tier × STRATEGIC BUCKET** at ${AUDIT_DIR}/auditor/tier-by-strategic.json. Apply STRATEGIC_MAP to roll canonical → strategic. The six expected buckets plus overflow:
   { "Lodging": { ... canonical_categories_included: ["Lodging"] }, "Dining": {...}, "Experiences": { ... canonical_categories_included: ["Activities","Tours","Arts & Culture","Entertainment"] }, "Meetings & Events": {...}, "Mobility": {...}, "Retail & Services": {...}, "(unmapped)": {...}, "(uncategorized)": {...} }
   This is the headline view Sat reviews first.

7. **Cut 4 — tier × VGPS sub-category** at ${AUDIT_DIR}/auditor/tier-by-subcategory.json. Leaf axis under each metacategory. A partner with multiple subcategories counts in each (note this in a "_note" field).
   { "Hotels|Resorts": { primary_canonical: "Lodging", total, mean_score_excluding_Z, tier_A, tier_B, tier_C, tier_D, tier_Z }, ... }

8. **Cut 5 — chain vs indie** at ${AUDIT_DIR}/auditor/chain-vs-indie.json:
   {
     "chain": { total, unique_businesses, mean_score_excluding_Z, tier_A, tier_B, tier_C, tier_D, tier_Z, by_strategic_bucket: {...} },
     "indie": { total, unique_businesses, mean_score_excluding_Z, tier_A, tier_B, tier_C, tier_D, tier_Z, by_strategic_bucket: {...} }
   }
   (Tier Z records have chain_brand = false by default; they sit in indie.)

9. **Headline counts**:
   - total_listings = total scored records (everything, including Tier Z)
   - unique_businesses = distinct weburl values (null weburls each count once)
   - tier_counts = { A, B, C, D, Z }

10. **strategic_summary** for the return value — inline copy of Cut 3 so Sat can read the headline numbers without opening files.

11. **Anomalies summary** — top 10 from across the run: high counts of (uncategorized), any (unmapped: X) labels with non-trivial counts, anomalies inherited from Merge, Wide Scan chunk errors. Also include unmapped_raw_labels as its own field (a list of every raw label that didn't match CANONICAL_MAP — Sat needs this to update TAXONOMY-CANONICAL.md before the next quarter's audit).

Return per AGGREGATE_SCHEMA.
`.trim(), {
  label: 'aggregate:final',
  phase: 'Aggregate',
  schema: AGGREGATE_SCHEMA,
})

if (!aggregate) throw new Error('Aggregate returned null — aborting.')

log('=== Phase 1 complete ===')
log(`Total listings: ${aggregate.total_listings} | Unique businesses (by weburl): ${aggregate.unique_businesses}`)
log(`Tier counts: A=${aggregate.tier_counts.A} B=${aggregate.tier_counts.B} C=${aggregate.tier_counts.C} D=${aggregate.tier_counts.D} Z=${aggregate.tier_counts.Z}`)
if (aggregate.strategic_summary) {
  log('Strategic buckets (the six + overflow):')
  for (const [sb, s] of Object.entries(aggregate.strategic_summary)) {
    const mean = s.mean_score_excluding_Z?.toFixed?.(2) ?? s.mean_score_excluding_Z
    log(`  ${sb}: n=${s.total} (unique=${s.unique_businesses}) mean=${mean} | A=${s.tier_A} B=${s.tier_B} C=${s.tier_C} D=${s.tier_D} Z=${s.tier_Z}`)
  }
}
if (aggregate.unmapped_raw_labels && aggregate.unmapped_raw_labels.length) {
  log(`Unmapped raw labels (update TAXONOMY-CANONICAL.md): ${aggregate.unmapped_raw_labels.join(', ')}`)
}

return {
  phase: 1,
  status: 'complete',
  hold_for_review: true,
  scout,
  inventory: { spawn, wait: waitResult, merge },
  wide_scan: {
    chunks: chunks.length,
    scored: scoredFromChunks.length,
    chunk_errors: chunkErrors.length,
  },
  aggregate,
  next_step: 'HARD HOLD. Sat reviews partners-wide-scan.json, partners-by-tier.csv, tier-by-rawlabel.json, tier-by-canonical.json, tier-by-strategic.json, tier-by-subcategory.json, chain-vs-indie.json, rubric-results-per-dimension.json. Update TAXONOMY-CANONICAL.md if any unmapped_raw_labels surfaced. NO synthesis, brief drafting, landing-page calibration, or outreach list work until Sat explicitly greenlights the next stage.',
}
