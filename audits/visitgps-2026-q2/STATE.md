# STATE — VisitGPS Agent-Readiness Audit, 2026 Q2

Authored 2026-06-04. Updated by hand between phases; the workflow appends a session log.

## Current status

**Phase 1 audit complete 2026-06-05. Strict-rule cuts canonical. 1.6% Tier A (58 of 3,627), Wellness leads at 3.29 mean, chains underperform indies by 1.15 points. Pre-recal artifacts archived under `_pre-recal-2026-06-05/`. Phase 2 held pending brief and category MVA work.**

## Preconditions checklist

- [x] Sitemap + scrapability confirmed (`scout/DRY-RUN-2026-06-04.md`)
- [x] 10-listing spike confirms per-listing extraction works (`scout/spike-2026-06-04-extraction.json`)
- [x] Vacation-rental exclusion approach: two-stage (slug + sub-category)
- [x] VGPS metacategory taxonomy confirmed via spike (STAY / EAT & DRINK / GROUP VENUES / ARTS & CULTURE / SHOPPING / etc.)
- [x] Workflow rewritten: Phase 1 standalone, v0 archived
- [x] SPEC locked to Phase 1 scope
- [ ] **Sat greenlights workflow invocation** ← gate
- [ ] Phase 1 workflow run completes
- [ ] Sat reviews Phase 1 outputs and designs Phase 2 (or postpones)

## Phase 1 progress

- [ ] Scout — sitemap fetched, slug-pruned URL set written
- [ ] Inventory — per-listing fetch + extraction complete (~2 hours)
- [ ] Wide scan — rubric checks complete across all kept partners
- [ ] Aggregate — tier × metacategory matrix, dimension stats, CSV written

## Phase 2 / Phase 3

**Held.** v0 workflow archived. Phase 2 will be redesigned after Sat reviews Phase 1 outputs.

## Session log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-06-04 | Setup | Spec drafted, recon done, workflow authored. No phases run. |
| 2026-06-04 | Scout dry-run | Sitemap + robots + category-index enumeration. Findings: 4,472 listings (~30× spec assumption); category index grids are JS-rendered; backing Simpleview API requires credentials; per-listing pages serve clean schema.org JSON-LD. Three open decisions surfaced to Sat: category labeling approach, vacation-rental inclusion, Phase 2 scope cut. See `scout/DRY-RUN-2026-06-04.md`. |
| 2026-06-04 | Sat directives | Lock Phase 1 as a complete project. Run 10-listing spike. Then full Phase 1 against ~3,800 real-business corpus (rentals excluded). Hold Phase 2 entirely. No commits. |
| 2026-06-04 | 10-listing spike | Bucket-diverse (3 hotels, 3 restaurants, 2 attractions, 2 venues). 10/10 weburl + phone + metacategory; 9/10 address + geo; 8/10 email. All extracted from embedded JSON in listing HTML. **Surprises**: VGPS uses 6 strategic metacategories not visible in sitemap path structure; some entities have multiple listing IDs (dedupe by weburl). See `scout/spike-2026-06-04-extraction.json`. |
| 2026-06-04 | Workflow rewrite | v0 archived (`audit-workflow-v0-archived.js`). New `audit-workflow.js` is Phase 1-only: Scout → Inventory (sequential, 2h) → Wide scan (parallel) → Aggregate. SPEC locked to Phase 1 scope. |
| 2026-06-04 | Courier edits | (1) Strategic buckets locked to VGPS metacategories — workflow discovers the set from data, doesn't gate-keep on a hardcoded list. (2) `chain_brand` boolean + `chain_brand_evidence` string added to every scored record; seed pattern list embedded in Wide Scan prompt. (3) Inventory captures BOTH `primary_category` (metacategory) and `subcategories` (array) per record. Aggregate now emits three cuts: tier × metacategory, tier × subcategory, chain vs indie. Hard hold at Aggregate — no synthesis work post-Aggregate. Pause-and-flag protocol embedded in Scout and Inventory agents for taxonomy/extraction anomalies. |
| 2026-06-04 | Phase 1 kickoff | Workflow invoked in background. |
| 2026-06-04 | Phase 1 run — incomplete | Workflow returned with placeholder results: Scout ✓ (4,278 candidates), Inventory partial (single agent spawned a bg Python fetcher then was forced to return early), Wide Scan zero (all 12 chunks returned null — root cause unknown), Aggregate placeholder (all in tier D). **Background fetcher pid 65360 still running** at ~22 records/min, healthy, will complete in ~3h. Multiple structural surprises surfaced: VGPS metacategory taxonomy is 17+ buckets (vs. 6 expected), with apparent label duplicates (STAY/PLACES TO STAY, GETTING HERE/GETTING HERE & AROUND); slug-prune missed direct-airbnb listings (need weburl-host filter); multi-listing entities span metacategories; ~13% of records have no weburl. Full post-mortem at `scout/POST-RUN-2026-06-04.md`. **PAUSED for Sat's review and decisions before any re-run.** |
| 2026-06-04 | Decisions locked (D1–D7) | Sat locked seven decisions covering taxonomy collapsing, host-based rental exclusion, dedup, Tier Z, fetcher disposition, three-stage Inventory rebuild, and tabling the Wide Scan zero-chunk debug. See "Decisions log" section below for full rationale. Workflow rewritten as v2: 6 phases (Scout, Inventory: Spawn, Inventory: Wait, Inventory: Merge, Wide scan, Aggregate). `TAXONOMY-CANONICAL.md` documents the canonical mapping. **Fetcher still running — DO NOT touch.** |
| 2026-06-05 | Fetcher completed | pid 65360 exited cleanly. 4,276/4,278 records (2 confirmed 404s). All Inventory output on disk and validated. |
| 2026-06-05 | v2 workflow run — Inventory ✓, Wide Scan broken | Scout/Spawn/Wait/Merge all worked exactly as designed. Disk state matches Merge's reported counts (3,333 kept_for_scoring, 118 platform_excluded, 223 subcategory_excluded, 602 no_weburl). **Wide Scan dropped 98.5% of corpus.** Root cause: `wide-scan:load` agent asked to return 3,333 records (~2 MB JSON) through structured output; silently truncated to 50. Only chunk-0.jsonl produced. Aggregate ran on 50 scored + 602 Tier Z = 652 records — headline numbers are unrepresentative, do not review as final. Full post-mortem at `scout/POST-RUN-2026-06-05.md`. **PAUSED.** Inventory output preserved; re-run requires only Wide Scan + Aggregate fix. Also surfaced: 5 unmapped raw labels (GOLF, HIKING TRAILS, VISITOR INFORMATION, FILM PRODUCTION SERVICES, CANNABIS) and 597 records with empty primary_category — both flagged for Sat. |
| 2026-06-05 | 597 empty-pc records — pattern resolved | Diagnosed without re-fetching. Three sub-causes: (a) `SPAS, BEAUTY & WELLNESS` (224 records) and `DOG-FRIENDLY RESOURCES` (61) — extractor regex `/^[A-Z &]+$/` rejected comma and hyphen, lost the metacategory; (b) `artsGPS` (308) — public-art installations (sculptures, murals, road signs), no weburl, not partner businesses; (c) 4 residual edge cases (record stubs with no recoverable metacategory). The Wellness corpus reveal aligns with AICV's documented content-gap priority. |
| 2026-06-05 | Decisions locked (D8–D11) | (D8) Relaxed metacategory regex to `/^[A-Z\\s&,\\-']+$/` — comma/hyphen/apostrophe allowed. (D9) Seven-bucket strategic taxonomy: Wellness promoted from canonical to its own strategic bucket (224 records, AICV-aligned). Plus GOLF as own canonical, HIKING TRAILS → Outdoor Recreation, three new canonical mappings for VISITOR INFORMATION / FILM PRODUCTION SERVICES / CANNABIS / DOG-FRIENDLY RESOURCES. (D10) artsGPS public-art exclusion at Inventory: Merge as 5th bucket category — segregated to `inventory-public-art-excluded.jsonl`. (D11) Build standalone Wide-Scan + Aggregate workflow; future re-scoring uses it as the durable artifact. |
| 2026-06-05 | Recovery re-merge complete | `scout/remerge.py` re-processed inventory-progress.jsonl with the new rules. Recovered 285 records from the empty-primary_category set (224 SPAS, 61 DOG-FRIENDLY). Segregated 308 public-art records. Final scoring set: 3,333 in `partner-directory-clean.json` across 23 raw metacategories (4 residual edge cases). V2-broken outputs archived to `scout/_v2-broken/` and `auditor/_stale-2026-06-05/`. TAXONOMY-CANONICAL.md and audit-workflow.js constants updated. New `audit-scoring-workflow.js` built using Option A disk-slice loader. |
| 2026-06-05 | Standalone scoring run — 12/13 chunks ✓, chunk-0 silently dropped | Disk-slice architecture worked: 13 of 14 chunks scored cleanly (chunk-1 through chunk-13, 3,094 records). **Chunk-0 silently failed.** Agent reported `scored_count: 239, output_path: "...chunk-0.jsonl"` in its structured output (which the schema validator accepted), but the file was never written to disk. 239 alphabetical-first records dropped (7.2%). Aggregate ran on 3,094 scored + 294 Tier Z = 3,388 records; cuts are usable but understated (likely undercounting Tier A/B). Headline tier dist: A=218 (6.4%), B=1533 (45.2%), C=626 (18.5%), D=717 (21.2%), Z=294 (8.7%). Strategic Wellness bucket leads on mean (3.72) — aligns with AICV content-gap priority. Chains underperform indies (2.21 vs 3.51 mean) — surprising and noteworthy. Full post-mortem at `auditor/POST-RUN-2026-06-05-scoring.md`. **PAUSED** for Sat's recovery decision. |
| 2026-06-05 | Recovery sequence executed (Option A + hardening) | Built reusable `scripts/verify_chunks.py` — verifies on-disk files match source slice by SET membership (not order; agents legitimately shuffle within their slice). Verified chunks 1-13 clean: zero duplicates, zero gaps across them; only chunk-0 missing. Spawned recovery agent → hit sandbox wall on outbound network → ran `score_chunk0.py` directly from main Bash. chunk-0 wrote 239 records cleanly (A=7, B=114, C=43, D=75). Verifier re-run on all 14 chunks: PASS. Built `scripts/reaggregate.py` (deterministic Python — no LLM) and re-emitted all six cuts + CSV + wide-scan.json. Final corpus: **3,627 records** (3,333 scored + 294 Tier Z), 3,074 unique businesses. Tier dist: A=225 B=1647 C=669 D=792 Z=294. Stray Python scripts moved to `auditor/chunks/_agent-scripts/`. `unmapped_raw_labels: []` — taxonomy coverage complete. **HOLDING at Aggregate for review.** |
| 2026-06-05 | Verification spot-checks — 2 rubric bugs surfaced | Ran `scripts/verify_findings.py` against 30 sampled records (10 per dimension). **schema_present = 0% is a measurement artifact** — 4 of 10 flagged-False have JSON-LD with rubric-eligible @types (Restaurant, LocalBusiness, Organization, TouristAttraction). Real rate likely ~30-40%. **nap_consistent = 5% is also an artifact** — 6 of 10 flagged-False would pass on re-check with normalized-digit + substring matching. Real rate likely 40-60%. **llms_txt_present = 23.5% is largely valid** — 9 of 10 sampled are real llms.txt files; 1 of 10 was an HTML fallthrough. Notable: several real llms.txt files are auto-generated by All in One SEO v4.8.5 (WordPress plugin) — plugin-driven adoption is a story in itself. Relative findings (Wellness leadership, chain vs indie gap) remain robust to rubric corrections because uniform score uplift preserves ordering. Absolute headlines need recalibration before the brief ships. Full report at `auditor/VERIFY-FINDINGS-2026-06-05.md`. **HOLDING for Sat's recalibration decision.** |
| 2026-06-05 | Recalibration ran — exposed a DEEPER scoring inconsistency | Built `scripts/recalibrate.py` per Sat's Option B spec — strict True/False derivation of `schema_present` (14 accepted @types) and `nap_consistent` (normalized phone digits + 3-rule name + city substring). Pre-recal chunks archived at `_pre-recal-2026-06-05/`. Recal completed: schema 0%→39.4%, NAP 5%→34.4% (both expected). **But tier distribution moved opposite to predicted: Tier A dropped from 225 → 58 (−167).** Diagnosis: pre-recal scoring was internally inconsistent. **schema_present was 100% None** (never measured at the per-record level), **nap_consistent was 85% None**, **content_fresh was 85% None**, **faq_present was 36% None**. Chunk agents inflated scores by inconsistently counting None values as passes — only 38.3% of pre-recal scores match strict sum-of-Trues; 15.4% match Trues+Nones; 46% match neither. The recalibration's strict scoring exposed this. Honest rigorous reading: 58 of 3,627 partners hit Tier A (1.7%), not 225 (6.2%). Full diagnosis at `auditor/RECAL-POST-MORTEM-2026-06-05.md`. **HOLDING for Sat's decision among three paths: (1) accept strict result, (2) revert and keep only corrected dimension stats, (3) full 8-dimension re-derivation.** |
| 2026-06-05 | Scenario 1 locked + strict re-aggregate complete | Sat locked the strict result as the defensible reading. Re-aggregate ran against recalibrated chunks. Final tier dist: A=58 (1.7%), B=1,388 (38.3%), C=1,128 (31.1%), D=759 (20.9%), Z=294 (8.1%). 6 of 8 scored dimensions are reliable; 2 (`content_fresh`, `faq_present`) retain measurement gap as floor estimates. **Wellness still leads** strategic buckets at 3.29 mean (gap over second-place Meetings & Events widened from 0.16 pre-recal to 0.23 post-recal). **Chains still underperform indies** 1.80 vs 2.95 (gap narrowed from 1.32 to 1.15 but persists). Headline: "1.7% of Greater Palm Springs visitor-economy businesses are agent-ready under strict measurement." Brief writes from these numbers. Methodology section acknowledges recalibration + 2 dimensions remaining at floor. |

## Architectural lesson (durable) — addendum

**Agent structured-output returns can lie about disk side-effects.**

The 2026-06-05 standalone run encoded the first lesson (large data via disk, control data via structured output). But chunk-0 showed a second failure mode: an agent reported successful completion in its structured output — including `scored_count: 239` and `output_path: "...chunk-0.jsonl"` — while the file at that path was never created. The schema validator can't verify side-effects. `parallel()` counted chunk-0 as completed. The bug only surfaced when Aggregate's downstream consumer (the disk-reading merge step) saw 13 files instead of 14.

Companion pattern to the first lesson:

- **Verify on disk after `parallel()` over disk-writing chunks.** Add an explicit verification step that lists actual files, compares to the reported paths, compares reported `scored_count` against actual file line counts, AND checks set membership (the file's record set equals the source slice's record set), throws on any mismatch.
- **Treat structured output as "what the agent says happened," not "what happened."** For any agent whose primary deliverable is a file, the workflow must verify the file exists, has the expected size, and contains the claimed content. This applies to the chunked-scoring pattern and any similar fan-out where each agent writes its own output.
- **Verify by SET MEMBERSHIP, not by ORDER.** Chunk agents are free to process records in any order within their slice — the contract is "score every record in your slice and write them," not "preserve source order." Verifying first/last positions is too strict and produces false positives. Compare the set of identity fields (e.g. vgps_id) in the file against the set in the source slice.

Implementation: `scripts/verify_chunks.py` (reusable; parameterized by `--source`, `--chunks-dir`, `--n-chunks`, optional `--manifest`). Integrated into `audit-scoring-workflow.js` as the `Verify` phase between Wide Scan and Aggregate. Hard gate — throws on failure.

## Underscore-prefix convention (durable)

Any path beginning with `_` under this audit directory is **archived/non-canonical** and safe to ignore on subsequent runs:

- `scout/_v2-broken/` — outputs from the 2026-06-05 v2 broken Merge run
- `auditor/_stale-2026-06-05/` — outputs from the v2 broken Wide Scan + Aggregate
- `auditor/chunks/_agent-scripts/` — Python scripts that chunk agents wrote during scoring (preserved for traceability, not part of the data)
- `auditor/_chunk-manifest.json` — workflow-internal manifest used by the Verify phase

Subsequent workflows, queries, and reviews can prune `_*` paths without losing canonical data. When a stage needs to be redone, the prior outputs move to a fresh `_run-YYYY-MM-DD/` directory rather than being overwritten in place. Apply this convention to all future audits.

## Architectural lesson (durable)

**Large data crosses agent boundaries via disk, not structured output.**

The Wide Scan failure on 2026-06-05 was caused by the `wide-scan:load` agent being asked to return ~3,300 partner records as JSON through its structured output. The payload (~2 MB) silently truncated to ~50 records. The schema validator accepted the truncated array (no minLength constraint), the workflow continued downstream with `chunks.length === 1`, and we lost 98.5% of the corpus to a quiet failure.

The fix encodes a pattern that applies broadly:

- **Agent return values are CONTROL DATA.** Counts, paths, anomalies, status flags. Things you'd put in a progress dashboard.
- **Record-level data stays on disk.** Each chunk agent reads its own slice from a known file at a known index range. It writes its scored records back to disk as it goes. The workflow code never sees the records themselves.
- **Index-based slicing > inline payloads.** Even when a payload looks small enough to fit, prefer file+range over structured output: it scales to any size, is restartable, and never silently truncates.

This pattern is encoded in `audit-scoring-workflow.js`. The `load:count-and-plan` agent returns counts only. Each chunk agent reads its slice from `${CLEAN_PATH}[start:end)`. The chunk's return is a `CHUNK_RESULT_SCHEMA` of counts and paths — never records. Aggregate reads the per-chunk jsonl files from disk and writes its outputs directly to disk too; its return is the summary.

Future audits and any other workflow with >100 records in flight should follow this pattern.

## Anomalies

_Resolved by decisions log below (2026-06-04). Original anomaly observations preserved here for posterity._

1. VGPS emits 17+ metacategory labels, not 6. Includes apparent duplicates (STAY ⇄ PLACES TO STAY, GETTING HERE ⇄ GETTING HERE & AROUND).
2. Vacation-rental slug-prune missed ~9+ direct airbnb.com / vrbo.com / smartervacation.rentals listings in the first 125 records.
3. Multi-listing entities (same business under multiple vgps_ids across metacategories) confirmed at scale — Ace Hotel, Acrisure Arena, 533 Viet Fusion, etc.
4. ~13% of records have no weburl.
5. Inventory architecture flaw — single-agent doing 4,278 sequential fetches can't fit in agent runtime.
6. Wide Scan zero-chunk failure — root cause TBD, likely cascade from Inventory's early return.

## Decisions log (2026-06-04, Sat)

Each decision below is applied in `audit-workflow.js` v2 and documented in `SPEC.md` and `TAXONOMY-CANONICAL.md`. Rationale preserved here so the design choices are recoverable later.

### D1. Three-level taxonomy at Aggregate

Aggregate emits **raw labels, canonical categories, and six strategic buckets**. The CANONICAL_MAP and STRATEGIC_MAP are pinned constants in `audit-workflow.js`; the full mapping with rationale lives in `TAXONOMY-CANONICAL.md`. Unmapped raw labels fall through to `(unmapped: <RAW_LABEL>)` and are surfaced in `unmapped_raw_labels` so new VGPS labels never silently disappear.

**Why:** the spike under-counted (5 labels seen, 17+ in reality). Three-level reporting lets the headline use clean strategic buckets (Lodging / Dining / Experiences / Meetings & Events / Mobility / Retail & Services) while preserving the raw-label evidence for auditability.

**Six strategic buckets:** Lodging, Dining, Experiences, Meetings & Events, Mobility, Retail & Services. See `TAXONOMY-CANONICAL.md` for which raw labels roll into each.

### D2. Host-based rental exclusion at Inventory: Merge

`weburl` host match against `RENTAL_PLATFORM_HOSTS = [airbnb.com, abnb.me, vrbo.com, homeaway.com, vacasa.com, smartervacation.rentals, evolve.com]` (matches subdomains too). Excluded records → `scout/inventory-platform-excluded.jsonl`. **Segregated, not discarded.**

**Why:** the slug-based prune missed direct airbnb.com listings VGPS imports wholesale. Aggregator hosts (booking.com, expedia.com, hotels.com) are NOT in this list — those route to Tier Z because they're "no real partner site" rather than rentals.

### D3. Dedup by weburl for unique-business counts

Per-listing scoring preserved. Aggregate emits both `total_listings` (all records, including multi-listings) and `unique_businesses` (distinct weburl values). Reported alongside tier counts in every cut.

**Why:** Ace Hotel × 3 listings shouldn't count as three businesses in the headline number. But scoring each listing separately is correct — they're different VGPS entries linking to the same homepage, all rubric checks pass/fail identically.

### D4. Tier Z for no-web-presence records

New tier in the enum. Tier Z = no `weburl` (auto-assigned at Inventory: Merge, never goes through Wide Scan). Tier D = has weburl, scored 0 against the rubric.

**Why:** previously conflating "no web presence" with "scored zero" was producing misleading Tier D counts (the v1 run dumped everyone into D). Z makes the corpus shape honest.

### D5. Let the background fetcher complete

pid 65360 left running. ~3 hours to completion. Don't kill.

**Why:** the fetcher is healthy and on-pace; killing wastes the ~125 records of progress and ~3 hours of crawl-delay budget already spent. Re-runs of the workflow's Inventory: Spawn stage are idempotent and will detect the completed progress file.

### D6. Rebuild Inventory as three explicit stages

Spawn → Wait → Merge. Each with bounded job + explicit completion criterion. Spawn checks if a fetcher is already running or already complete (idempotent). Wait polls until the fetcher process exits with full coverage (or hits timeout). Merge applies exclusions (D2, D4) and produces the clean inventory Wide Scan consumes.

**Why:** v1's single-agent Inventory was forced to return structured output before the fetcher finished, which cascaded failures to Wide Scan and Aggregate. Splitting into bounded stages with clear completion criteria fixes the root cause and makes each stage separately approvable.

### D7. Table Wide Scan zero-chunk investigation

Don't investigate the v1 silent-zero-chunk failure yet. Re-test with the clean v2 inventory first; if Wide Scan still emits zeros, then investigate.

**Why:** likely cascade from Inventory's early return. Cheaper to retest than to spelunk v1 transcripts.

## Sequence locked

1. Let fetcher complete (don't touch).
2. While it runs: workflow script updated to v2 reflecting D1–D6 ✓ (this commit-batch's work).
3. When fetcher completes: re-invoke workflow. Spawn detects `already_complete`, Wait short-circuits, Merge applies exclusions, Wide Scan reruns, Aggregate emits the 3-level cuts.
4. Hard hold at Aggregate. Surface all six stage milestones (Scout, Spawn, Wait, Merge, Wide Scan, Aggregate) plus the raw-label-vs-canonical-vs-strategic-bucket comparison.

No commits at any stage.
