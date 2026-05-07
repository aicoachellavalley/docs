# AICV — Strategic State

> This is the STRATEGIC STATE file for AICV.
> Operational/technical state (deploys, session logs, git hashes)
> lives in each operational repo's own STATE.md — not here.
> Update this file weekly or on strategic milestone completion.

The pre-partition snapshot of operational content is preserved at
`STATE.md.pre-partition-2026-04-17.md` for reference.

---

## Live Counts (as of May 3, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 80 |
| Intelligence briefs live | 142 |
| Snapshots live | 3 |
| Reports live | 2 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 70 (Mar 2026) · 22 (Apr 2026)

**Nodes:** 80 across nine incorporated cities and adjacent communities — all on v2 schema with `verified`, `status`, `agent_intent` fields. See `TAXONOMY.md` for canonical city/region values.

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

---

## How to Update This File

After a strategic milestone or weekly review:
1. Update live counts if a scope threshold crossed
2. Add/remove channels if the distribution layer shifts
3. Record milestone completion in the North Star Roadmap
4. Do NOT add operational state (commit hashes, deploy commands,
   framework versions, script invocations). Those belong in the
   relevant operational repo's STATE.md.
