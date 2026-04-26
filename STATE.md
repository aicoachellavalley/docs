# AICV — Strategic State

> This is the STRATEGIC STATE file for AICV.
> Operational/technical state (deploys, session logs, git hashes)
> lives in each operational repo's own STATE.md — not here.
> Update this file weekly or on strategic milestone completion.

The pre-partition snapshot of operational content is preserved at
`STATE.md.pre-partition-2026-04-17.md` for reference.

---

## Live Counts (as of April 26, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 80 |
| Intelligence briefs live | 133 |
| Snapshots live | 3 |
| Reports live | 1 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 70 (Mar 2026) · 13 (Apr 2026)

**Nodes:** 80 across nine incorporated cities and adjacent communities — all on v2 schema with `verified`, `status`, `agent_intent` fields. See `TAXONOMY.md` for canonical city/region values.

**Verification ledger:** see `verification/SCHEMA.md` for schema v1; scaffold pending.

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

- aicoachellavalley.com: Cloudflare 75 / Level 5 "Agent-Native" (highest tier). AICV AIO Tool: Grade A. Person schema added; entity clarity clear.
- aicoachellavalley.org: Cloudflare 50 / Level 2. AIO Tool: B. Status pills + agent discovery infrastructure deployed. Markdown for Agents + Pro upgrade deferred pending pitch traffic.

Commercial tier activated — /get-agent-ready page scoped for next build session with DCF board approval secured.

### Milestone: Commercial tier Phase 1 launched (2026-04-23)

`/get-agent-ready/` live on aicoachellavalley.com (commit `32b6981`). Standalone page separates AICV Network commercial positioning from organizational/editorial homepage narrative — resolves the Entity Clarity warning flagged in the 2026-04-23 AIO baseline. Homepage untouched. Pricing locked: AICV Ready ($1,000 + $2,500/yr), AICV Reviewed Founding ($2,500 + $5,000/yr, 10 spots), AICV Reviewed Standard ($5,000 + $7,500/yr). Founding counter 10/10. AIO grade + Cloudflare rescoring on new page deferred (worker rate limit hit on 2026-04-23); operational detail in `com/STATE.md`.

**Deferred verifications scheduled 2026-04-24:** AIO Tool grade on `/get-agent-ready/` (target A); Cloudflare agent-readiness rescan on `/get-agent-ready/` (target 75+); Google Rich Results validation on `/get-agent-ready/` JSON-LD.

---

## How to Update This File

After a strategic milestone or weekly review:
1. Update live counts if a scope threshold crossed
2. Add/remove channels if the distribution layer shifts
3. Record milestone completion in the North Star Roadmap
4. Do NOT add operational state (commit hashes, deploy commands,
   framework versions, script invocations). Those belong in the
   relevant operational repo's STATE.md.
