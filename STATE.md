# AICV — Strategic State

> This is the STRATEGIC STATE file for AICV.
> Operational/technical state (deploys, session logs, git hashes)
> lives in each operational repo's own STATE.md — not here.
> Update this file weekly or on strategic milestone completion.
>
> **Operating rules** for how sessions are *run* (model seating,
> budget governance, census & data-product integrity, outreach) live
> in `OPERATING-RULES.md`. **Infrastructure / Cloudflare zone posture**
> lives in `ARCHITECTURE.md`.
>
> The **Forward Queue** at the bottom of this file is the SOLE forward
> queue (the stale `TOMORROW.md` was retired 2026-06-13).

The pre-partition snapshot of operational content is preserved at
`STATE.md.pre-partition-2026-04-17.md` for reference.

---

## Live Counts (as of 2026-06-14 — disk-verified)

| Metric | Count |
|--------|-------|
| Nodes live | 81 |
| Intelligence briefs live | 162 |
| Snapshots live | 3 |
| Reports live | 7 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 70 (Mar 2026) · 22 (Apr 2026) · 7 (May 2026) · 13 (Jun 2026)

**Brief count reconciled 2026-05-19:** discrepancy flagged 2026-05-11 resolved. Disk, stats.json, and STATE.md now in sync at 145. `coachella-valley-intelligence-index` node description referencing 131 is a stale prose string, not a count field — update deferred.

**Reports count reconciled 2026-06-14 (T&W publish):** `reports.json` now serves **8** entries — seven Reports (data-centers, state-of-ai-q1, visitor-economy, dining, home & real-estate, family-schooling, **talent-workforce**) plus one evergreen methodology page (`methodology-agent-mapped-census`). Count taken from the endpoint, not from memory (per OPERATING-RULES §5.2). Node / brief / snapshot rows above carry their June-11 reconciliation and were not re-verified this session.

**Report-count legend (the counts differ by SCOPE — all correct, do not "reconcile" them to one number):**
- **4 — complete category censuses:** ground-up category maps (dining, H&RE, F&S, T&W).
- **5 — agent-readiness research series:** the 4 censuses **+ the visitor-economy audit**. This is the number each report's own text uses (T&W = "the fifth entry in the series").
- **7 — Reports shipped (roadmap milestones):** **all** report types — the 5 above **+ data-centers (civic-intelligence) + State of AI Q1 (state-of-ai)**. This is the "Nth Report shipped" milestone number (T&W = "Seventh Report shipped").
- **8 — `reports.json` endpoint entries:** the 7 Reports **+ the evergreen methodology page** (not itself a "Report"). This is the count the surface-health monitor asserts agreement on (site ↔ reports.json ↔ MCP desk).

**Nodes:** 81 live across nine incorporated cities and adjacent communities (includes valley-wide concept nodes and the `coachella-valley-intelligence-index` meta-node) — all on v2 schema with `verified`, `status`, `agent_intent` fields. See `TAXONOMY.md` for canonical city/region values.

**Verification ledger:** see `verification/SCHEMA.md` for schema v1; scaffold deferred — revisit when nodes reach 100

---

## Distribution Layer

| Channel | Handle / URL | Role |
|---------|-------------|------|
| Twitter/X | @CoachellaAI | AICV distribution |
| Bluesky | @sunshinefm.bsky.social | SunshineFM human voice |
| Newsletter | Beehiiv (SunshineFM) | 85 editions since June 2024 |

---

## Repositories

Git-tracked AICV repositories. All live under
`github.com/aicoachellavalley/`. Local directory name and
GitHub remote name match EXCEPT where flagged — see each
repo's CLAUDE.md for trap details.

| Local dir | GitHub remote | Purpose |
|---|---|---|
| `aicv-playbook/` | `docs` ⚠ | Workflow brain, schemas, strategic state |
| `com/` | `homepage` ⚠ | aicoachellavalley.com Astro site |
| `org/` | `aicoachellavalley-org` | aicoachellavalley.org |
| `tools/` | `tools` | tools.aicoachellavalley.com |
| `aicv-api/` | `aicv-api` | AIO Tool worker |
| `aicv-mcp/` | `aicv-mcp` | MCP worker |
| `aicv-ic/` | `aicv-ic` | IC backend worker (NEW 2026-04-21) |
| `twitter-worker/` | `twitter-worker` | @CoachellaAI posting (NEW 2026-04-21) |
| `bluesky-worker/` | `bluesky-worker` | @sunshinefm posting (NEW 2026-04-21) |

**⚠ = local directory name diverges from GitHub remote
name.** See the repo's CLAUDE.md for details. Always verify
with `git remote -v` before hardcoding GitHub URLs.

**Not shown:** Only AICV-scoped repositories appear in this table. Repos belonging to other projects under `github.com/aicoachellavalley/` are out of scope for this STATE file.

---

## North Star Roadmap

### Milestone: Tier 4 agent-readiness achieved (2026-04-22)

aicoachellavalley.com is now at full Tier 4 of the four-tier agent-readiness framework:
- Cloudflare Pro zone upgrade
- Markdown for Agents enabled at CDN edge (Accept: text/markdown → edge-converted response with Content-Signal header)
- Content-Signal directive live in robots.txt
- `/.well-known/api-catalog` (RFC 9727 linkset) published
- `/.well-known/mcp/server-card.json` (SEP-2127 draft shape) published
- AICV MCP server at mcp.aicoachellavalley.com publicly discoverable via standard well-known path

### Milestone: Pitch framing locked (2026-04-22)

Four-tier agent-readiness framework crystallized as a pitch asset. Network pitch: "Join the AICV network — we represent your entity at Tier 4 without you touching your website." See CLAUDE.md for the full tier definitions.

### Architecture: AICV vs SunshineFM Guide separation formalized (2026-04-22)

Strategic posture locked: **"agent-ready now, SEO-ready always."** Bridge at entity level only (aicvNodeSlug on Guide entries; future sunshineFmGuideSlug on AICV nodes). Neither system auto-feeds the other.

### Architecture: Collective signal vision defined (2026-04-22)

At ~300 AICV entities, the corpus should produce emergent regional insights. Layer 2 build path defined: enhance build-static-json.cjs with bidirectional refs, explicit relationship types, temporal structure, aggregation surfaces. Not a new platform. See CLAUDE.md for full definition.

### Milestone: Agent-readiness baselines established (2026-04-23)

Both AICV domains now have documented agent-readiness baselines with deferral rationale on disk.

- aicoachellavalley.com: Cloudflare 75 / Level 5 "Agent-Native" (highest tier). AICV AIO Tool: 86 / Grade B. Person schema added; entity clarity clear.
- aicoachellavalley.org: Cloudflare 50 / Level 2. AIO Tool: B. Status pills + agent discovery infrastructure deployed. Markdown for Agents + Pro upgrade deferred pending pitch traffic.

Commercial tier activated — /get-agent-ready page scoped for next build session with DCF board approval secured.

### Milestone: Commercial tier Phase 1 launched (2026-04-23)

`/get-agent-ready/` live on aicoachellavalley.com (commit `32b6981`). Standalone page separates AICV Network commercial positioning from organizational/editorial homepage narrative — resolves the Entity Clarity warning flagged in the 2026-04-23 AIO baseline. Homepage untouched. Pricing locked: AICV Ready ($1,000 + $2,500/yr), AICV Reviewed Founding ($2,500 + $5,000/yr, 10 spots), AICV Reviewed Standard ($5,000 + $7,500/yr). Founding counter 10/10. AIO grade + Cloudflare rescoring on new page deferred (worker rate limit hit on 2026-04-23); operational detail in `com/STATE.md`.

**Deferred verifications completed 2026-04-25** (originally scheduled 2026-04-24; delayed one day by rate-limit): AIO Tool grade on `/get-agent-ready/` (78 / Grade C, 1 warn — AIO rescan surfaced a 6k content-cap truncation bug in the worker; investigated and fixed same session, `aicv-api` commit `91a31f4`); Cloudflare agent-readiness rescan (75 / Level 5 — domain infrastructure confirmed); Google Rich Results (valid — all 4 schema types confirmed). Operational detail in `com/STATE.md`.

### Milestone: First Civic Intelligence Report published (2026-04-28)

"The Server Farm Next Door" — AICV Civic Intelligence Report No. 001 on data centers, AI infrastructure, and community negotiating power in the Coachella Valley. New report type (`civic-intelligence`) added alongside existing `state-of-ai` type. Reports live at `/reports/`. Static JSON and reports index updated; second report in `reports.json`.

### On the horizon: User journey + waypoint naming

Surfaced 2026-04-26. The four-tier framework (Tier 1–4) is the right technical taxonomy for internal use and developer-facing pitches, but numbers are the wrong shape for partner-facing communication — they read as grades and put prospects in a defensive posture.

Pending work, deferred until landing page completes:
- Build the partner-facing user journey: how a prospect goes from "never heard of AICV" to "represented in the network at the top tier"
- Identify waypoints: landing point, self-location, visible gap, on-ramp (likely Snapshot), ongoing presence (Review portal)
- Name the waypoints with descriptive, motion-implying language — not numbers, not aspirational grades. Names emerge from the journey, not before it.
- Keep Tier 1–4 as internal technical vocabulary; the named waypoints are the partner-facing layer on top.

Do not start this work until landing page (separate thread) is shipped.

### Parked: Search Console health review (Q2 baseline)

**Surfaced 2026-04-29.** While filing a Removal Request for the retired agent.* subdomain, surfaced a separate finding on aicoachellavalley.com worth a dedicated session.

**Baseline as of 2026-04-29:**

49 URLs not indexed, broken into five categories:

| Category | Count | Source | Likely status |
|---|---|---|---|
| Alternate page with proper canonical tag | 12 | Website | Correct — canonical signals working as intended |
| Page with redirect | 10 | Website | Correct — Google indexing destination URLs |
| Not found (404) | 7 | Website | Possibly actionable — worth per-URL review |
| Crawled - currently not indexed | 20 | Google systems | Normal for content-heavy site at Tier 4; trend gently rising |
| Blocked due to other 4xx issue | 0 | Website | Clean |

**Scope of the future session (60–90 min, focused):**

- Drill per-URL into each category, especially the 7 404s and 20 currently-not-indexed pages
- Decide per-URL: correct status, redirect needed, or indexing request warranted
- Pair with wider Search Console sweep — sitemap freshness, Core Web Vitals, mobile usability, structured data validation
- Establish ongoing trend monitoring cadence (monthly or quarterly check-ins)

**Why parked:** Acting well requires per-URL drill-down across 49 candidates plus context from adjacent Search Console sections. Not fragmented-day work. The indexing health is not currently degraded — this is a baseline-and-improve pass, not a fix-something-broken pass.

**Closed today (2026-04-29):**

- Search Console Removal Request filed for agent.aicoachellavalley.com (retired surface hygiene from this morning's audit). The agent subdomain finding is unrelated to the 49-URL panel above — different property, different issue.

### Strategic decision: Grades go private (2026-04-29)

AICV is not a public grading authority. This decision locks the
posture going forward and requires migration across six surfaces.

- **Public Snapshots publish analytical substance only** — no letter
  grades. The three-dimension findings, recommendations, and
  competitive framing remain public. The grade labels (A/B/C/D/F)
  do not.
- **Letter grades are reserved for the private Intelligence Review**
  delivered directly to the entity. Grades are the upsell hook —
  the full Review with grades is what cold outreach points toward.
- **Cold outreach reframe:** "Here's what the IC found about your
  entity" (public Snapshot substance) → "Here's how you scored"
  (private Review with grades) → "Here's what to do about it"
  (12-month roadmap, AICV node).

**Migration required across six surfaces:**

1. **Three existing public Snapshots** — strip letter grades from
   public-facing HTML: Sensei Porcupine Creek, Visit Greater Palm
   Springs, The Gardens on El Paseo.
2. **Worker CHAIR_SYSTEM prompt** — revise `aicv-ic/worker.js` to
   separate public Snapshot output fields from private Review output
   fields. Currently returns a single unified object. Post-migration,
   `/chair` returns a `snapshot` object (no grades) and a `review`
   object (grades included) — or separation happens in the client
   layer. Architecture TBD next session.
3. **Snapshot JSON schema** — replace `additionalProperty` grade
   entries (buyerReadinessGrade, competitivePositioningGrade,
   aiReadinessGrade) with structured finding fields that carry
   substance without letter grades.
4. **Locked Snapshot template in IC.md** — remove the grading
   framework section (A/B/C/D/F labels) from the public Snapshot
   template. Retain in the private Intelligence Review template.
5. **Cold outreach pitch language** — update pitch copy so grades are
   framed as the upsell hook, not the cold open. Cold outreach leads
   with findings; grades appear only in the private Review delivered
   after engagement.
6. **Methodology copy on public Snapshots** — verify or reframe the
   "5 randomly selected frontier AI models from a portfolio of 30"
   language on existing public Snapshots. Ensure it accurately
   reflects the current IC process and doesn't imply a grading
   authority posture that contradicts the grades-go-private decision.

**Executed on public surfaces 2026-05-11** (commit `44482c7`):
`public/reviews.json` deleted. Top-level grades and per-finding
`grade` fields removed from all three snapshot JSONs. Grade
frontmatter removed from `gardens-on-el-paseo` and
`visit-greater-palm-springs` node MDX. Snapshot template
(`[slug].astro`) guarded for grades-absent rendering — IC Grades
and Grade Key sections now conditional; per-finding badge
suppressed when grade absent. Homepage stat replaced with
snapshots-backed "Agentic Reviews" (count: 3). Verified live
at aicoachellavalley.com.

### Milestone: Second Report shipped — State of AI Q1 2026 (2026-04-28)

`state-of-ai-q1-2026` published as the second AICV Report. Joins `data-centers-ai-infrastructure-coachella-valley` ("The Server Farm Next Door") in the Report layer. Reports cadence target remains 4–6/year as the citation anchor.

### Milestone: Sand → paper color migration shipped (2026-05-02)

Background palette migrated from warm beige (`#E8E2D0`) to warm near-white (`#FAFAF7`) across five files (tokens.css + four inline `:root` blocks in slug templates). Variable names (`--sand`, `--sand-light`, `--sand-dark`) intentionally preserved — rename deferred. Brand continuity held; legibility improved without dramatic visual shift. Step 1 of three-step legibility program; Steps 2 (postcard redesign) and 3 (print stylesheet) pending.

### Architecture: Postcard Snapshot redesign concept locked (2026-05-02)

Public Snapshots will collapse from "analytical page with hidden grades" to a registration card: identity + AICV layer membership + structured data + one-finding teaser + CTA to full Review. Grades become the paywall. Migration scope spans `aicv-ic/worker.js` (CHAIR_SYSTEM JSON, ~30 lines), `IC.md` template, three live Snapshots, `reviews.json` (rename to `snapshots-index.json`), and a new `snapshots/_schema.json`. Editorial shift more than code shift — primary work is writing one factual paragraph + one teaser per live entity.

### Architecture: Firewall framing evolved — voice and editorial mission, not human author (2026-05-02)

AICV ↔ SunshineFM separation refined: the firewall protects voice and editorial mission, not the existence of a human author. Implicit human presence is acceptable on AICV surfaces; cross-contamination at the audience level is permitted. Voice and editorial mission remain strictly separate.

### Milestone: Get Agent Ready V2 desktop recalibration shipped (2026-05-07)

`/get-agent-ready/` V2 desktop recalibration live (commit `8ea075d`). Hero h1 84px, diagnostic h2 56px, section h2s unified at 44px, about at 28px. Section padding 64→96px desktop. Inner wrapper gains 48px horizontal padding. Tier price block softened to 17px DM Sans 400 (Setup/Annual labels replace Deployment jargon). Scarcity copy updated to "Limited to 10 Founding Members." 12px pine-tint strip replaced with full-width pine-mist tagline band. All changes scale proportionally on mobile via updated ≤768px breakpoint.

### Milestone: Get Agent Ready V2 shipped (2026-04-29)

`/get-agent-ready/` rebuilt from V7.7 (8-section education surface) to V2 (6-section qualification surface). Commit `624f71d` on `com/`. Key changes: split-color volt diagnostic headline, inline booking strip above tier cards, Proof of Work button → Node Zero, blueprint figures across five sections, `--pine-tint` and `--pine-mist` palette tokens added to `tokens.css`, fiscal sponsorship + email moved to footer fields inside the close section. FAQ removed from the page; booking section collapsed. Copy revised throughout for visibility metaphor consistency.

### Architecture: Typography audited, no action required (2026-05-02)

Reading-surface body type confirmed at 16px / 1.75 line-height / 760px max-width — already in publication-grade band. Three-font system (Syne display / DM Sans body / EB Garamond editorial) is deliberately designed and stays. Font weight 300 is intentional homepage marketing copy on dark backgrounds, never reading-surface body. Print legibility (the original complaint trigger) belongs to the print stylesheet, not screen typography.

### Milestone: May 11 model locked — two products, vocabulary, audience, taxonomy, architecture (2026-05-11)

**Two-product model:**
- **Agent on the AICV Network** — base product. The entity's
  structured node on the network, built and maintained by AICV.
- **Agent Premium** — upgrade tier. Includes an LLM Council
  review producing the **Agentic Review** (private deliverable)
  as the differentiating artifact.

**Vocabulary locked:**
- "Node" stays internal. Customer-facing term is "agent on the
  network."
- **LLM Council** replaces Intelligence Council internally and
  externally.
- "Snapshot" retires as a public term. **Agentic Review** is
  the artifact the Council produces.

**Audience and positioning:**
- SF/LA newly-vested founder cohort is the named primary audience
  — tech-wealth migrating from the venture and startup ecosystem.
- Positioning honest about being early — aspirational framing,
  not accomplished-scale.

**SunshineFM Guide / AICV Network:**
- ~80% candidate pool overlap. Independent selection criteria:
  Guide selects for editorial fit; network selects for
  agent-readiness and commercial intent. Shared pool, separate
  editorial gates.

**Taxonomy axes locked:**
- **Funnel-stage axis:** visit / fall-in-love / retreat /
  satellite / relocate / build. Existing `agent_intent` field
  encodes this informally; formal enforcement deferred.
- **Life-domain axis:** 14-domain target density; canonical
  domain enum deferred to a future taxonomy session. The two
  axes are orthogonal.

**Agent architecture:**
- Per-city agent runtime writes to per-entity records (hybrid
  architecture). City-scoped, not system-wide.
- **Rancho Mirage named prototype city.** Cotino — the
  1,900-home Disney-branded master-planned community currently
  building out — is AICV's primary relocation intelligence
  anchor for tech-wealthy professionals migrating from SF and
  LA, making Rancho Mirage the highest-leverage city for
  prototyping the funnel-aware agent runtime against the named
  primary audience.
- Architecture is distinct from cv-intel civic-watchdog
  inheritance; AICV agent scope is commercial and
  intelligence-layer.

### Milestone: Lighthouse 13.3 Agentic Browsing baseline + WebMCP reference implementation (2026-06-03)

Both .com and .org score 1.0 on Lighthouse 13.3 Agentic Browsing (3/3 weighted audits pass: accessibility tree, CLS, llms.txt). Declarative WebMCP annotation shipped on /get-agent-ready/ analyzer as reference implementation (`<form toolname="analyze_agent_readiness" tooldescription="...">` with `toolparamdescription` on the URL input); audits remain `notApplicable` until Chrome 149 origin trial removes the `enable-webmcp-testing` flag gate. Bidirectional Organization schema sameAs established between .com and .org. Confirmed: .com is the canonical agent surface; repos stay proof-of-work, not a parallel data API. Six commits to homepage, two to org.

### Milestone: Third Report shipped — State of CV Visitor Economy Q2 2026 (2026-06-05)

`state-cv-visitor-economy-agent-readiness-q2-2026` published as the third AICV Report. First systematic regional audit of agent-readiness across 3,627 publicly-facing visitor-economy businesses in the Coachella Valley; 58 (1.6%) currently meet the threshold. Joins `data-centers-ai-infrastructure-coachella-valley` ("The Server Farm Next Door") and `state-of-ai-q1-2026` in the Report layer. Multi-agent research workflow; first measurement-grade asset in the Network's citation anchor.

### Milestone: Fourth Report shipped — Agent-Mapped: Food & Dining in the Coachella Valley Q2 2026 (2026-06-11)

`agent-mapped-food-dining-coachella-valley` published as the fourth AICV Report and the second in the agent-readiness series. Category-complete census of 1,423 food and dining establishments across twelve communities — 971 independent rows (925 fixed-location operators), 442 chains, and 10 unclassified — produced through a multi-agent agent-mapping workflow that starts from the territory itself rather than from any directory. With the full inspection complete — all 859 non-mapped fixed-location independents individually inspected — none expose structured data across 554 checkable sites and 28.4 percent block AI crawlers. Distinct from the visitor-economy audit by scope and method rather than correction: the visitor-economy report scored a 956-business directory-sourced Dining subset against an eight-dimension rubric, while this census maps the full category including operators no directory contains. First vertical-deep, single-category, end-to-end map in the Report layer; advances the "honey-pot" thesis of holding category-complete maps that aggregators structurally cannot see. (Milestone figures updated 2026-06-14 to the V2 full-inspection numbers; V1 carried a 377-establishment sample.)

### Milestone: Fifth Report shipped — Agent-Mapped: Home & Real Estate, + shared methodology page + public supersession (2026-06-12)

`agent-mapped-home-realestate-coachella-valley` published as the fifth AICV Report and the third in the agent-readiness series, alongside a new evergreen methodology page `methodology-agent-mapped-census` — the shared, citable methodology for the whole agent-mapped census series. The same day, the dining report's **V2 regen** shipped carrying a public **supersession block** and a **Cross-Category Ledger**, consistency-gated to the digit against the live H&RE figures — the first public demonstration of AICV's supersession convention (a revised report openly supersedes its prior version rather than silently overwriting it). The `reports.json` endpoint now serves six entries (five Reports + the methodology page). The numeric and supersession conventions are now public on the methodology page; the internal operating rules that enforce them (numeric discipline, the cross-report consistency gate, the regen-draft convention) are codified in `OPERATING-RULES.md` §5.

### Milestone: Sixth Report shipped — Agent-Mapped: Family & Schooling in the Coachella Valley Q2 2026 (2026-06-14)

`agent-mapped-family-schooling-coachella-valley` published as the sixth AICV Report and the fourth in the agent-readiness series — the third complete category census, after dining and H&RE. Canonical <https://aicoachellavalley.com/reports/agent-mapped-family-schooling-coachella-valley/> (com `6ee47f0`); live, served by `get_report`, `reports.json` now at seven entries. 216 organizations across eight subcategories and twelve communities. Thesis — **"The Unregulated Category"** — completes the credential typology the series has been tracing: inspection regime (dining) → license-display regime (H&RE) → no regime at all (151/216 carry no state credential an agent can check). Headline finding: 83% hide pricing. **First synthesis published under the Opus synthesis seat** (post-Fable fold, `OPERATING-RULES.md` §1); numeric + cross-report consistency gates held to the digit (visibility gap 12.5%, on par with H&RE).

### Milestone: Seventh Report shipped — Agent-Mapped: Talent & Workforce Q2 2026 (2026-06-14)

The **fifth entry in the agent-readiness series and the fourth complete category census** (after
dining, H&RE, F&S), now **synthesized and live**: canonical
<https://aicoachellavalley.com/reports/agent-mapped-talent-workforce-coachella-valley/> (com
`4c74b7f`); served by `get_report`, IndexNow HTTP 200, **`reports.json` now at eight entries** (seven
reports + the methodology page). **Second synthesis published under the Opus-only seat.** The dataset
(aicv-playbook `0502249`) ran in one session at **~16.5% of the 12M guard**: **83 enrich-targets (100%
enriched) + 14 review + 18 context** (public_workforce 11 / econ_dev 6 / farm_labor_contractor 1).
**Series-first SPLIT credential category** — the typology now reads inspection (dining) →
license-display (H&RE) → no regime (F&S) → **split** (T&W): **unregulated 63 (75.9%) vs credentialed 20
(24.1%)**, computable row-level. Headlines: **visibility gap 14.5% — series-high, consistency-gated to
the digit (5.0 < 11.4 < 12.5 < 14.5, on the n=83 enriched-only denominator the prior three each used)**;
structured data 3.2%, 78.1% hide pricing, crawler-blocked 10.3% (series-low). Census template at **v1.3**
(split-category `credential_regime` stamp; worker-tagged context segments; registry-carve-out promotion +
per-row regime override; auditable Gate-2 reconcile). Run dir
`data/workflow-runs/cv-talent-workforce-2026-06-14/` (README has full provenance).

### Milestone: iMac HQ ignition — tree re-bootstrapped from canon (2026-06-27)

The full AICV code tree was stood up clean on the iMac from GitHub canon: **14 repos, 0
failures**, both intentional remote-name divergences intact (`com`→`homepage`,
`playbook`→`docs`), the **Mac Mini untouched**, nothing committed or pushed. New tree root is
**`~/AICV/`** (replacing `~/Projects/`): `core/{com,org,playbook,mcp,api,co,ic}`,
`aiqna/{aiqna,aiqna-agent}`, `mva`, `workers/{bluesky,twitter,tools}`, `sunshine-fm`. This is
the **disk-is-canon resilience property proven** in the realest test — the business can be
re-bootstrapped from GitHub onto a fresh machine. CV-Intel cluster intentionally **parked**
(alive-but-on-hold); clone targets documented in `_archive/README.md`. Recordings (4.8G) +
The-Archive (1.1G) backed up on the Crucial drive; R2 is the eventual home. **Scope honesty:**
this is a clean *code tree*, not yet a working deploy-and-run environment — the three steps
between "tree exists" and "I work entirely from the iMac" are tracked in the Forward Queue below.

---

## Forward Queue

> The single forward record for AICV. Reconciled 2026-06-13; the stale
> `TOMORROW.md` (dated 2026-05-11) was read item-by-item and retired into
> this section. Strategic posture and completed work stay in the North
> Star Roadmap above; near-term build/verification items live here.
> Operational mechanics (scripts, deploy commands, env) belong in the
> relevant operational repo when each item gets built — not here.

### iMac HQ — make it a working environment, not just a code store (queued 2026-06-27)

Three steps stand between the clean tree (done) and "I work entirely from the iMac." All
next-session, none done today:

1. **Cloudflare / wrangler auth** — the second handshake. Nothing deploys until `wrangler` is
   logged into the `sunshinefm` Cloudflare account on the iMac. Next browser pop-up, due on the
   first live push. (GitHub auth is already done — `gh` logged in as SunshineFM, both orgs visible.)
2. **Path-update sweep** — everything moved `~/Projects/` → `~/AICV/core/`. The playbook
   `CLAUDE.md` (Canonical paths block, every build/deploy command, file-structure map) and likely
   `OPERATING-RULES.md` + scripts still hardcode the old path. Grep the new tree and fix before a
   cold session trips on a stale path.
3. **Cold-start test** — the real proof. Point a fresh Claude Code session at
   `~/AICV/core/playbook`, have it read this STATE.md, and confirm it can find its bearings and
   resume the operating rhythm. That's when the iMac becomes a *working* HQ, not just a code store.

### Surface-health monitor — BUILT 2026-06-14 (legs 1–2 done + verified; leg 3 code-complete, deploy deferred)

**Pointer:** surfaces map → [`SURFACE-INVENTORY.md`](SURFACE-INVENTORY.md); monitor code → `tools/surface-health/`.
Deterministic, no AI. Three legs:
1. **Surface-inventory doc** — `SURFACE-INVENTORY.md` (pages, feeds, .well-known, the 6 MCP desk tools, the count-agreement graph). ✅ done.
2. **Post-deploy check script** — `tools/surface-health/check.mjs`: feeds parse; counts agree site ↔ json ↔
   desk (reports.json **= 8** is the three-way anchor; nodes/briefs/snapshots feed↔site); IndexNow returns 200 (a validated key returns 200, not 202 — F&S
   publish, 2026-06-14); sample report URLs return 200. ✅ done — verified live 17/17 on the clean state (2026-06-14).
3. **Weekly Cloudflare Worker heartbeat** — `tools/surface-health/{worker.js,wrangler.toml}`: reuses the check module; records Bing indexed-count
   vs sitemap-count trend (sitemap auto; **Bing manual field** `BING_INDEXED`, baseline 237). ⏳ code-complete, **NOT deployed** — `wrangler deploy` (+ create the KV namespace, keep BING_INDEXED current) is a separate explicit step.

Productize as **Agent Ready Premium surface-watch.** Build precondition
("after F&S census") is now met.

### Email-pilot arc

- **Step zero:** fix the **DMARC record error** Cloudflare flags on the zone.
- **Primary rail:** Cloudflare Email Service (public beta) + their skill
  and Agentic Inbox reference app. **AgentMail.to** is the fallback benchmark.
- Use a **dedicated sending subdomain** (never the root domain); slow warmup.
- **First real flow:** prospect score-delivery to census **non-winners** —
  agent-sent, honestly labeled, reply-to-human. (Division of labor: see
  `OPERATING-RULES.md` §6 — recognition emails carry no pitch.)

### Verification legs queued

- **DRE / NMLS** deterministic pass (H&RE census).
- **F&S verification pass (narrow by design):** confirm the ~65 displayed
  CDSS facility numbers + school-accreditation claims, and enumerate the 46
  `family_home_daycare` registry-only homes against the CDSS registry.
- **T&W credential-verification leg:** the **20 credentialed-wing entities**
  (BPPE/state-board trade schools + the 3 promoted FLCs) + **FLC registry
  enumeration** (CA DIR) for the `farm_labor_contractor` context count.

### Prospect-shortlist extraction (internal)

- Dining, H&RE, and F&S shortlists.

### Node candidates parked (events / wedding layer, human-endorsed)

- Kuma Catering · PS Underground · Butter Cake Studio.

### Census status

- **F&S (family & schooling):** dataset SHIPPED 2026-06-12 (216 enriched + 16
  review + 46 family-home context rows); **synthesis report PUBLISHED 2026-06-14**
  (com `6ee47f0`, live + served by `get_report`). Remaining census-cleanup legs
  (separate sessions): resolve the **2 `_verify_note` rows** (Dove's Landing city,
  Montessori PS&PD variant) and triage the **16 review rows**. (The narrow
  verification pass and the prospect shortlist are tracked in their sections above.)
- **T&W (talent & workforce):** dataset SHIPPED 2026-06-14 (aicv-playbook `0502249`) **and
  synthesis report PUBLISHED 2026-06-14** (com `4c74b7f`, live + served by `get_report` +
  IndexNow 200, `reports.json`→8). The §5.3 consistency gate held to the digit (5.0 < 11.4 <
  12.5 < 14.5, n=83 enriched-only). Remaining census-cleanup legs (separate sessions): triage
  the **14 review rows** (the two ClearPoint rows; the not-yet-open Express Employment branch;
  the rest). **Boundary note:** caregiver / nurse-registry staffing sits at the staffing↔home-care
  line — reconcile (pre-flagged dedup) against the future **Wellness/healthcare census**.
  (Credential-verification leg tracked above.)

### Migrated from the retired TOMORROW.md — still live

- **Rancho Mirage city-agent prototype spec** — first city-scoped,
  funnel-aware agent runtime (entity scope, runtime architecture, output
  record, LLM Council intake integration). Dormant since the census push;
  not dead.
- **IC.md → LLM Council rename** — comprehensive snapshot→Agentic-Review +
  Intelligence Council→LLM Council rename pass across IC.md and the
  `aicv-ic/worker.js` CHAIR_SYSTEM prompt. Do not rename piecemeal; one pass.
- **`aicv-mcp` `query_venues` city enum** — missing `cathedral-city` and
  `desert-hot-springs`. Now higher-relevance: the dining/H&RE/F&S censuses
  all use the 12-city list that includes both. (Operational fix lives in the
  `aicv-mcp` desk.)
- **`tokens.css` fork** — `com` vs `guide-builder` divergence (`--sand` etc.).
  Low priority.
- **`snapshots.json` cosmetic** — empty `grades: {}` objects left after the
  2026-05-11 grades-go-private execution. Cosmetic, not user-facing.

### Closed from the retired TOMORROW.md (2026-05-11)

- **Landing-page May-11 vocabulary rewrite** — superseded by the later
  `/get-agent-ready/` V2 work (see roadmap, 2026-04-29 / 2026-05-07); no
  longer a tracked priority.
- **Founding-Member outreach (was HELD)** — superseded by the Email-pilot
  arc + Prospect-shortlist work above.
- **Brief count reconciliation** — done (reconciled 2026-05-19; see Live
  Counts).
- **IndexNow 403** — resolved (see `ARCHITECTURE.md` → Agent Discoverability
  Layer; com `6799846`).
- **Search Console health review** and **User journey + waypoint naming** —
  already tracked in the North Star Roadmap above; not duplicated here.

---

## How to Update This File

After a strategic milestone or weekly review:
1. Update live counts if a scope threshold crossed
2. Add/remove channels if the distribution layer shifts
3. Record milestone completion in the North Star Roadmap
4. Do NOT add operational state (commit hashes, deploy commands,
   framework versions, script invocations). Those belong in the
   relevant operational repo's STATE.md.
