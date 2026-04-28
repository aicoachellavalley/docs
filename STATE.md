# AICV — Strategic State

> This is the STRATEGIC STATE file for AICV.
> Operational/technical state (deploys, session logs, git hashes)
> lives in each operational repo's own STATE.md — not here.
> Update this file weekly or on strategic milestone completion.

The pre-partition snapshot of operational content is preserved at
`STATE.md.pre-partition-2026-04-17.md` for reference.

---

## Live Counts (as of April 28, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 80 |
| Intelligence briefs live | 141 |
| Snapshots live | 3 |
| Reports live | 2 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 70 (Mar 2026) · 21 (Apr 2026)

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

**Not shown:** `agendalink-sync/` is an untracked CV Intel
adapter cordoned 2026-04-21 — see the CV Intel parking
README (linked in Sibling projects section below). The
CV Intel family repos (`cv-intel`, `cvintel-agent`,
`cvintel-cron`) are also under `github.com/aicoachellavalley/`
but belong to CV Intel; see parking README for their status.

---

## Sibling projects

**CV Intel status:** Parked as of 2026-04-20. Workers paused in Cloudflare dashboard (parking action in progress per parking README). `agendalink-sync` cron disabled 2026-04-21. Canonical parking state: `~/cv-intel/README.md`. Do not resume CV Intel work from AICV sessions without reading the parking README first.

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

---

## How to Update This File

After a strategic milestone or weekly review:
1. Update live counts if a scope threshold crossed
2. Add/remove channels if the distribution layer shifts
3. Record milestone completion in the North Star Roadmap
4. Do NOT add operational state (commit hashes, deploy commands,
   framework versions, script invocations). Those belong in the
   relevant operational repo's STATE.md.
