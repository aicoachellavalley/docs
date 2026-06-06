# Standalone scoring run — post-mortem

Workflow `wf_0393f9ec-57c` completed 2026-06-05 ~08:45 PDT. **The standalone architecture worked — chunks read disk slices, structured output stayed control-data-only.** But chunk-0 silently failed to write its output file. 239 of 3,333 scoring-eligible records dropped (7.2%). The aggregate cuts are usable but understated.

## What worked

- All 14 chunks reported `chunks_completed: 14, chunks_failed: 0`
- 13 chunk files (chunk-1 through chunk-13) wrote cleanly: 3,094 records total
- Aggregate emitted all six cuts + CSV
- `unmapped_raw_labels: []` — taxonomy coverage is complete
- No chunk parse errors during ingestion
- Tier distribution is plausible across all seven strategic buckets

## What broke

**chunk-0.jsonl is missing from disk.** The chunk-0 agent reported `scored_count` in its structured output return — making the workflow's `chunks_completed: 14` count truthful at the agent-API level — but the file at `auditor/chunks/chunk-0.jsonl` was never created.

239 records covering inventory indices [0, 239) silently dropped. Verified directly: 0 of the chunk-0 vgps_ids appear in `partners-wide-scan.json`.

### What's in the missing slice

Records are alphabetical-first (lower vgps_ids = older partners), distributed across most metacategories:

- 50 EAT & DRINK, 29 SHOPPING, 18 RELOCATION & RESOURCES, 17 STAY, 17 MEETING & EVENT RESOURCES
- 14 WEDDINGS, 13 SPAS BEAUTY & WELLNESS, 12 ARTS & CULTURE, 11 GETTING HERE & AROUND
- 10 PLACES TO STAY, 9 GROUP VENUES, 6 GETTING HERE, 6 DOG-FRIENDLY, 5 each of THINGS TO DO / BUS PROF SVC / CASINOS, 4 ACTIVITIES
- 3 VISITOR INFORMATION, 2 TOURS, 2 HIKING TRAILS, 1 GOLF

These skew toward established partners: `$5 Pizza Place`, `29 Palms Inn`, `Élan Vital Studio`, `360 Sports at Agua Caliente`, several Acrisure properties, etc. Many likely score better than the chunk-1+ averages — the missing data probably **understates** Tier A/B counts.

## Architectural lesson — second-order

The first lesson (encoded in `audit-scoring-workflow.js`) was: **large data crosses agent boundaries via disk, not structured output**. That fix held — no truncation this run.

The new failure mode is subtler: **an agent's structured-output return can still lie about disk writes that were supposed to happen**. The chunk-0 agent's `scored_count: 239, output_path: "...chunk-0.jsonl"` was accepted by the schema validator, looked successful in the parallel() result, but the file didn't exist on disk.

The next-level pattern: **post-parallel() verification step**. After `parallel(chunks.map(...))`, the workflow should add an agent that:
- Lists actual files in `chunks/`
- Compares against the reported `output_path` for each completed chunk
- Compares `scored_count` against actual file line counts
- Throws if any chunk's report doesn't match its file

This isn't improvising — it's the durable hardening. I'm flagging it for Sat to approve before adding to the workflow.

## Aggregate output — usable but understated

The cuts are real but cover 3,094 of 3,333 scoring-eligible records (92.8%) plus 294 Tier Z.

### Headline tier distribution (3,388 of expected 3,627)

| Tier | Count | % of total |
|---|---|---|
| A | 218 | 6.4% |
| B | 1,533 | 45.2% |
| C | 626 | 18.5% |
| D | 717 | 21.2% |
| Z | 294 | 8.7% |

### Strategic buckets (mean score excluding Tier Z)

| Bucket | n | unique | mean | A | B | C | D | Z |
|---|---|---|---|---|---|---|---|---|
| Lodging | 325 | 307 | 3.01 | 21 | 135 | 50 | 112 | 7 |
| Dining | 906 | 860 | 3.60 | 53 | 425 | 170 | 152 | 106 |
| Experiences | 602 | 521 | 3.33 | 42 | 243 | 116 | 128 | 73 |
| **Wellness** | 211 | 207 | **3.72** | 22 | 96 | 23 | 44 | 26 |
| Meetings & Events | 519 | 433 | 3.62 | 42 | 253 | 106 | 94 | 24 |
| Mobility | 103 | 87 | 3.48 | 5 | 52 | 25 | 17 | 4 |
| Retail & Services | 718 | 683 | 3.25 | 33 | 326 | 136 | 169 | 54 |
| (uncategorized) | 4 | 4 | 4.25 | 0 | 3 | 0 | 1 | 0 |

### Chain vs Indie

- Chains: 214 listings, mean score 2.21
- Indies: 3,174 listings, mean score 3.51

**Chains underperform on local discoverability.** Interesting and counter-intuitive — brand recognition doesn't translate to local agent-readiness on the rubric we measured.

### Cuts written

- `auditor/partners-wide-scan.json` (3,388 records)
- `auditor/partners-by-tier.csv`
- `auditor/tier-by-rawlabel.json`
- `auditor/tier-by-canonical.json`
- `auditor/tier-by-strategic.json`
- `auditor/tier-by-subcategory.json`
- `auditor/chain-vs-indie.json`
- `auditor/rubric-results-per-dimension.json`

### Anomalies surfaced

- 4 records with empty primary_category (the residual edge cases) — mean score 4.25, classified `(uncategorized)`
- Tier Z represents 8.7% (294 records) — concentrated in Dining (106), Experiences (73), Retail & Services (54), Wellness (26), Meetings & Events (24)
- Lodging has the lowest mean score (3.01) and highest Tier D share (34.5% of bucket) — short-term rentals and boutique stays without strong owned web presence
- Wellness leads on mean (3.72) — aligns with AICV content-gap priority

## Decisions needed from Sat

1. **Recovery approach for the missing 239 records.** Three options:
   - **(a) Recommended:** Single direct Agent invocation scores chunk-0's slice (indices [0,239) of `partner-directory-clean.json`), writes `chunk-0.jsonl`. Then a small re-Aggregate agent merges + re-emits all six cuts + CSV + wide-scan.json. ~10-15 min. Most efficient.
   - (b) Re-invoke the standalone workflow from scratch, deleting chunks 1-13 first. Wastes ~30 min of HTTP work; produces a clean run. Use if Option A's manual stitching is risky for downstream consumers.
   - (c) Accept the 92.8% coverage as-is and proceed with current Aggregate. Not recommended — the missing slice is alphabetical-first and biased toward established partners that likely change the Tier A/B counts.

2. **Hardening — add post-parallel() verification step?** Before the next re-run (or as a permanent change to `audit-scoring-workflow.js`), add a verification agent that lists `chunks/*.jsonl`, compares to reported `output_path` and `scored_count`, throws on mismatch. Same D2 principle — fail loudly rather than silently lose data.

3. **Cleanup of stray script files.** Three agents (chunk-8, chunk-12, chunk-13) left their Python scoring scripts at `auditor/chunks/score_chunk*.py`. Harmless but messy. Move to a `_agent-scripts/` subfolder for traceability?

## What I'm NOT doing

- Running Option A or B without direction.
- Modifying `audit-scoring-workflow.js` to add the verification step.
- Touching the existing chunk files or aggregate outputs.
- Updating TAXONOMY-CANONICAL.md (no taxonomy changes needed — `unmapped_raw_labels: []`).

Holding at Aggregate per the standing directive.
