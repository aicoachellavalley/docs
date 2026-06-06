# AICV Workflow Spec — VisitGPS Partner Portal Agent-Readiness Audit

_Drafted for Claude Code execution. Sat will courier and approve before commits._

## Purpose

Audit the publicly listed VisitGPS partner directory to produce:

1. A scored agent-readiness profile of every partner, bucketed by category and tier
2. A representative deep-dive sample with cross-AI-system visibility testing
3. A publishable insight artifact for SunshineFM and the AICV corpus
4. A calibrated outreach list — partners in the productive middle who could benefit from AICV's agent-readiness work

The audit is a real AICV intelligence product, not just internal research. It will be cited from `/get-agent-ready/visitor-economy/` and become a recurring quarterly/semi-annual brief.

## Scope and constraints

- **Public data only.** Partner directory listings, public websites, public schema markup, publicly returned AI system responses. No scraping behind logins. No private API endpoints.
- **Respect robots.txt and reasonable rate limits.** Add courtesy delays between requests to the same domain.
- **Cite all sources.** Every data point in the final brief must be traceable to a public URL with a captured timestamp.
- **No partner is publicly named in a negative light.** Public outputs reference patterns and aggregate findings only. Per-partner detail stays in internal AICV files.
- **AI query responses are snapshots.** Capture date, model, and full response text. Don't characterize a model's "permanent" view of any partner.

## Scope lock — Phase 1 only (2026-06-04, post-spike)

**This audit engagement is Phase 1 only.** Phase 2 (cross-AI visibility testing) and Phase 3 (synthesis) are held pending Sat's review of Phase 1 results. Phase 2 may end up scoped differently than the original spec assumed — possibly trimmed to 3 systems × 5 queries, possibly postponed to a future cycle. See `audit-workflow-v0-archived.js` for the original three-phase script.

## Resolved open questions (Sat, 2026-06-04)

1. **Directory source** — Sitemap is the canonical URL set. Per-listing fetch extracts everything we need (weburl, phone, email, name, address, category metadata) from embedded JSON in the listing page HTML. Category-index crawling is unnecessary and would have been broken anyway (those grids are JS-rendered). _Confirmed by 10-listing spike, 2026-06-04._
2. **Categories** — VGPS emits ~17+ raw metacategory labels, not 6. Three-level taxonomy at Aggregate: raw labels (as-emitted), canonical categories (duplicate-collapsed per `TAXONOMY-CANONICAL.md`), and six strategic buckets (Lodging, Dining, Experiences, Meetings & Events, Mobility, Retail & Services). Unmapped raw labels fall through to `(unmapped: X)` and are surfaced to Sat. _Discovered in run-1 partial output, decision applied 2026-06-04._
3. **Vacation rentals** — Excluded in three stages: (a) slug-based heuristic in Scout (`hosted-by`, `acme-house`, `vacasa`, bed-bath codes, sleeps-N, RVC prefixes, rental amenity keywords); (b) `weburl` host-based exclusion at Inventory: Merge (airbnb.com, vrbo.com, vacasa.com, smartervacation.rentals, evolve.com); (c) sub-category match at Inventory: Merge ("Vacation Rentals", "Timeshares", "RV Resorts/Parks"). Excluded records are **segregated, not discarded** — they go to `inventory-platform-excluded.jsonl` and `excluded-rentals.jsonl`.
4. **No-web-presence records** — Records with no `weburl` get **Tier Z**, not Tier D. Tier Z = "no web presence to score." Tier D = "scored zero against the rubric." Reported as a distinct bucket throughout Aggregate output.
5. **Multi-listing entities** — Same business appearing under multiple `vgps_id` values (Ace Hotel under STAY + WEDDINGS + GROUP VENUES, etc.). Per-listing scoring preserved. Aggregate also reports `unique_businesses` (deduped by `weburl`) alongside `total_listings`.
6. **Phase 2 design** — HELD. To be designed after Sat reviews Phase 1 distribution.
7. **Disk location** — `~/Projects/aicv-playbook/audits/visitgps-2026-q2/` (this directory).

## Phase 1 — Wide scan (full corpus)

**Goal:** Lightweight automated scoring across every partner in the directory. Establishes baseline, enables tier bucketing, and surfaces patterns by category.

### Steps

1. **Inventory** — fetch the VisitGPS sitemap (and any nested sitemap indexes). Extract every URL matching `/listing/{slug}/{id}/`. Crawl category index pages (`/hotels/`, `/restaurants/`, `/things-to-do/` and its sub-pages, `/events/`, top-nav discoveries) to associate each listing with its primary category. Build a unified inventory: `{ id, slug, name, primary_category, all_categories, listing_url, partner_website, address, phone, sitemap_lastmod }`. Dedupe by id.
2. **Per-partner automated checks** — for each partner with a website:
   - Site loads (200 response, reasonable load time)
   - SSL cert present and valid
   - Mobile-responsive (basic viewport check)
   - Schema markup present (`LocalBusiness`, `Hotel`, `Restaurant`, `Event`, or category-relevant types)
   - Open Graph metadata present
   - `llms.txt` present (rare but increasingly relevant)
   - NAP consistency check vs. directory listing
   - Last meaningful content update (sitemap dates, blog dates, news section)
   - FAQ page exists (any URL containing `/faq`, `/questions`, `/help`, or structural FAQ markup)
   - Google Business Profile linked and verifiable
3. **Score** — apply Phase 1 scoring rubric. 0-8 scale.
4. **Bucket** — assign each partner to one of four tiers:
   - **Tier A — Agent-ready**: 7-8. Already strong. Skip for outreach.
   - **Tier B — Productive middle**: 4-6. Visible but partial. Primary outreach targets.
   - **Tier C — Foundationally absent**: 1-3. Significant gaps. Low priority.
   - **Tier D — No web presence or broken site**: 0. Exclude from analysis.

### Phase 1 scoring rubric (0-8)

One point per dimension if present and substantive:

| # | Dimension | Pass criteria |
|---|---|---|
| 1 | Website loads cleanly | 200 response, SSL valid, loads under 5s |
| 2 | NAP consistency | Name, address, phone match VisitGPS listing |
| 3 | Mobile-ready | Responsive viewport present |
| 4 | Schema markup | At least one structured data block of relevant type |
| 5 | OG metadata | Title, description, image all present |
| 6 | FAQ or substantive Q&A content | Explicit FAQ page OR comparable depth elsewhere |
| 7 | Content freshness | Any visible update within last 6 months |
| 8 | Third-party citation density | Listed on at least 3 of: Google Business, Yelp, TripAdvisor, OpenTable, Resy, official tourism boards |

### Phase 1 output

- `auditor/partners-wide-scan.json` — array of all scored records (including auto-D for null-weburl).
- `auditor/partners-by-tier.csv` — summary CSV for human review (vgps_id, name, primary_category, score, tier, weburl, listing_url; sorted A→D, then score desc).
- `auditor/rubric-results-per-dimension.json` — pass rate per scored dimension + the two unscored dimensions (llms_txt_present, gbp_linked).
- `auditor/tier-by-metacategory.json` — the review artifact: per-metacategory totals, mean score, tier counts, top-5 and bottom-5 scorers.

## Phase 1 review gate

After Phase 1 completes, Sat reviews:

1. **Distribution** — score histogram across all ~3,500-3,800 scored businesses.
2. **Tier breakdown by strategic bucket** — `tier-by-metacategory.json` shows where the A's cluster and where the D's cluster.
3. **Patterns by category** — which rubric dimensions are universally weak (e.g. llms.txt likely 0%) and which split sharply by category (e.g. schema markup probably strong for chains, weak for indies).

Phase 2 design is informed by these findings. Possibilities include:
- Trimmed scope: 3 systems × 5 queries × ~111 stratified sample.
- Hard-pivot scope: focus only on the 2-3 metacategories where Phase 1 reveals the most actionable gaps.
- Postpone entirely if Phase 1 data alone produces a publishable brief.

## Phase 2 / Phase 3 — held

The original three-phase design is preserved in `audit-workflow-v0-archived.js`. Do not run it as-is; the assumptions about partner count, category taxonomy, and Chrome MCP availability all need revisiting.

## Workflow architecture (Phase 1 — locked)

See `audit-workflow.js`. Four sequenced groups:

- **Scout** — single agent: fetch sitemap, prune obvious vacation-rental slugs.
- **Inventory** — single agent: sequential per-listing fetch (2s crawl-delay), extract `weburl`/`phone`/`email`/`primary_category`/`subcategories`/address from embedded JSON. Drop rentals revealed at this stage by sub-category match. Resumable via `inventory-progress.jsonl`.
- **Wide scan** — ~14 parallel agents: rubric checks per chunk. Hits partner websites (not VGPS), so parallelism is safe.
- **Aggregate** — single agent: merge, CSV, tier-by-metacategory matrix, dimension pass rates.

Each step writes to disk. Workflow run is restartable: Scout and Aggregate are fast and idempotent; Inventory and Wide scan are append-only via jsonl progress files.

## Cost and time estimate

- **Scout:** seconds (one sitemap fetch + python parse).
- **Inventory:** ~3,500-3,800 sequential fetches × 2s = **~2 hours wall clock**. Dominant cost. No realistic way to parallelize without violating robots.txt crawl-delay.
- **Wide scan:** parallel across chunks, each hitting unique partner domains. Total budget per partner: ~6-10 HTTP fetches × 1s spacing. ~14 chunks × ~250 partners × ~10s each = **~40 minutes**.
- **Aggregate:** seconds.
- **Total wall clock:** ~2.5-3 hours for Phase 1. API cost: minimal (HTTP fetches dominate, ~$2-5 in tokens for the rubric scoring + aggregation).

## Deliverable structure on disk

```
aicv-playbook/audits/visitgps-2026-q2/
  SPEC.md                           # this file (Phase 1 scope-locked)
  STATE.md                          # progress tracker
  audit-workflow.js                 # Phase 1 workflow script
  audit-workflow-v0-archived.js     # original 3-phase design (do not run)
  scout/
    DRY-RUN-2026-06-04.md           # initial recon report
    spike-2026-06-04-extraction.json # 10-listing spike extraction proof
    sitemap-2026-06-04.xml          # raw sitemap snapshot
    listing-urls.json               # post-slug-prune candidate URL set
    pruned-by-slug.json             # rentals dropped at Scout
    partner-directory-clean.json    # final kept inventory
    excluded-rentals.json           # rentals dropped at Inventory
    inventory-progress.jsonl        # append-only progress for resumability
    inventory-anomalies.json        # 404s, timeouts, parse failures
  auditor/
    chunks/chunk-{0..N}.jsonl       # append-only per-chunk scoring progress
    partners-wide-scan.json         # final merged scored records
    partners-by-tier.csv            # CSV for human review
    rubric-results-per-dimension.json
    tier-by-metacategory.json       # the review artifact
```

## Invocation

```
Workflow({
  scriptPath: '/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2/audit-workflow.js'
})
```

No args. Phase 1 runs end-to-end (~2.5-3 hours wall clock). The script throws if `args.phase` is anything other than `1` — guard against accidentally invoking it as a multi-phase pipeline.
