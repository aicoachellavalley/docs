# AICV — Project Brief for Claude Sessions

## What this repo is

The canonical workflow and schema store for AICV. No live content,
no publishing. When working here, you are updating schemas, workflows,
voice rules, or strategic state — not publishing-ready content.

GitHub: https://github.com/aicoachellavalley/docs

**GitHub repo name vs local directory name.** This local directory is named `aicv-playbook/` but the GitHub remote is `aicoachellavalley/docs` — not `aicoachellavalley/aicv-playbook`. Any code or prompt that hardcodes GitHub raw URLs, clones from GitHub, or references the repo by name must use `docs`.

Verify with: `git remote -v`

Surfaced 2026-04-21 during ecosystem recon. This is the second instance of the same trap — see also com/CLAUDE.md for the trap on the homepage repo. Origin: the local directory was renamed from `docs/` to `aicv-playbook/` on 2026-04-17 (commit 627f235) for ergonomic reasons; the GitHub remote was not renamed.

## State file partition

STATE.md in this repo tracks STRATEGIC state only: North Star
roadmap, milestones, major targets. Update weekly or on milestone
completion, not per commit.

OPERATIONAL state (deploy hashes, session logs, per-task tracking)
belongs in each operational repo's own STATE.md. Do not add
operational state to this file. If a repo doesn't have its own
STATE.md yet, create one in that repo when first needed.

## Canonical paths

- Live AICV content: ~/Projects/com/src/content/
- Live .org site: ~/Projects/org/
- Live sunshine.fm: ~/sunshine-fm/
- AICV Worker API: ~/Projects/aicv-api/
- CV Intel: parked 2026-04-20, lives at ~/cv-intel/ (see README there)

---

## Session Start — Required

Before any content operation:
1. Read STATE.md for current counts, active month group, and last commit
2. Read ARCHITECTURE.md only if working on infrastructure, deployment, or ops

Do not create or edit any file without completing step 1.

---

## What We're Building

A three-layer intelligence system:

- **Nodes** — Persistent geographic anchors, one per institution/location, organized by city
- **Intelligence Briefs** — Daily timestamped signals, one per day, filed by date
- **Also Noted** — Secondary signal roundups, 2–5 signals per file, filed by date

---

## Workflow

- **Claude.ai** — Strategy, content writing, editorial decisions, research
- **Claude Code** — File creation, git operations, build script runs
- **Sat** — Courier between the two systems

Claude Code must not commit without explicit approval.

**Verify before acting on production state.** Before any action that changes a production constant, hardcoded path, configuration value, or live deployed resource, verify the target via direct inspection (`git remote -v`, `curl`, file read, etc.) rather than inferring from prior conversation or tool reports. This applies whether the action is a single-line edit, a deploy, or a schema change. Cost is seconds; cost of false precision in production is hours.

Surfaced 2026-04-20 when an aicv-mcp URL fix was written on top of a reconstructed inference about the GitHub remote, caught by the user before deploy. The actual remote was verified in 10 seconds via `git remote -v` and confirmed the fix was correct — but the cost of being wrong (deploying a worse bug on top of an existing one) would have been hours of rollback and re-triage.

---

## Node Frontmatter Schema (Required — Do Not Deviate)

Every node file must open with exactly these fields:

```
---
title: ""
description: ""
agent_summary: ""
city: ""
category: "landmark"
subcategory: ""
last_updated: "YYYY-MM-DD"
related:
  - slug: ""
    type: ""
---
```

Valid `category` values: `landmark`, `event`

Valid `subcategory` values: `hospitality`, `golf`, `wellness`, `cultural`, `entertainment`, `economic`, `education`, `retail`, `intelligence`, `nonprofit`, `real-estate`, `innovation`, `media`

Valid `related.type` values:
- `supports` — this node provides evidence or context for the linked node's narrative
- `extends` — this node deepens a concept the linked node introduces
- `see_also` — relevant but no directional relationship; agent should know both
- `same_corridor` — physical or geographic proximity matters for routing
- `competitive_set` — same category, same market; IC and agent comparison context

---

## Node Section Structure (Required — Do Not Deviate)

Every node must contain exactly these sections in this order:

```
# [Node Name]

## What It Is

## Why It Matters for AI

## Key Facts

## Known Agent Actions

## Agent Signal

## Data Provenance

## Constraints and Dealbreakers

## Handoff

## Related Nodes

## Intelligence Briefs
```

`## Agent Signal` — Opens with "For transactions —" and closes with "Updated by AICV: [Season] [Year]." Written as a direct instruction to the querying agent. AICV is the agent-to-agent concierge for tourism and economic development in the Coachella Valley.

---

## Intelligence Brief Frontmatter Schema (Required — Do Not Deviate)

```
---
title: ""
description: ""
date: "YYYY-MM-DD"
tags: []
---
```

---

## Intelligence Brief Section Structure (Required — Do Not Deviate)

```
# [Title]

**Date:** Month DD, YYYY

## Signal

## Context

## Agent Signal

Opens with "According to AICV," and reads as on-the-ground regional surveillance — not a summary of the signal above. Answers: what does an agent querying the CV need to know to act on this?

## Related Nodes
```

---

## Also Noted Frontmatter Schema (Required — Do Not Deviate)

```
---
title: "Also Noted — [Date]"
description: ""
date: "YYYY-MM-DD"
tags: ["also-noted"]
---
```

---

## Also Noted Section Structure (Required — Do Not Deviate)

```
# Also Noted — [Date]

**Date:** Month DD, YYYY

## Signals

### [Signal Title]

One tight paragraph — what it is, why it matters for the AI economy.

### [Signal Title]

One tight paragraph.

## Agent Signal

Opens with "According to AICV," and reads as on-the-ground regional surveillance — not a summary of the signal above. Answers: what does an agent querying the CV need to know to act on this?

## Related Nodes
```

---

## How to Add an Intelligence Brief

1. Identify one AI-economy signal from local news or inbound inquiry
2. Write brief in Claude.ai using the frontmatter schema and section structure above
3. Claude Code creates file: `src/content/briefs/YYYY-MM-DD-slug.mdx`
4. Run: `node scripts/build-static-json.cjs` from `~/Projects/com/`
5. Review before committing
6. Commit: `feat: add [date] intelligence brief`
7. Push to main — auto-deploys

---

## How to Add an Also Noted Brief

1. Identify 2–5 secondary signals from SunshineFM transcript that don't warrant standalone briefs
2. Draft in Claude.ai using the schema above
3. Claude Code creates file: `src/content/briefs/YYYY-MM-DD-also-noted.mdx`
4. Run: `node scripts/build-static-json.cjs` from `~/Projects/com/`
5. Review before committing
6. Commit: `feat: add [date] also-noted brief`
7. Push to main — auto-deploys

---

## How to Add a Node

1. Research the location in Claude.ai
   - Write `agent_summary` as a single sentence (max 40 words) answering the most likely cold query that would find this node — name the location, what it is, and why it matters for agents
2. Draft MDX using the frontmatter schema and section structure above
3. Claude Code creates the file at `src/content/nodes/[slug].mdx` (flat, no city subfolder)
4. Review full file tree before committing
5. Commit: `feat: add [location] node`
6. Push to main — auto-deploys
7. Update STATE.md counts and last commit hash
8. **Reciprocal links** — for every node listed in `## Related Nodes`, open that node file and add a back-link to the new node. Run before committing:
   ```bash
   grep -rn "new-node-slug" ~/Projects/com/src/content/nodes/
   ```
   Confirm every related node has a matching link back. One-way links break agent routing and the org graph edges. This step is not optional.
9. **Graph maintenance (required before commit):**
   Ask: which existing nodes does this node strengthen, extend, or contradict?
   - Update their `related` frontmatter with the appropriate slug and type
   - Update their `## Related Nodes` section to include a backlink
   - One-way `related` links break graph integrity — every relationship must be reciprocal
10. **Deploy org site** — graph changes are not visible until deployed:
    ```
    cd ~/Projects/org && npx wrangler pages deploy . --project-name aicoachellavalley-org
    ```
11. **Deploy com site:**
    ```
    cd ~/Projects/com && npx wrangler pages deploy . --project-name aicoachellavalley-homepage
    ```

---

## Standard Claude Code Courier Block

Every intelligence brief drafted in Claude.ai must end with:

**Claude Code instructions:**
1. Create file: `src/content/briefs/[filename].mdx`
2. Run: `node scripts/build-static-json.cjs` from `~/Projects/com/`
3. Commit: `feat: add [date] [slug] brief`
4. Push to main — auto-deploys

---

## Key Learnings

- **Static JSON is the agent-readable layer.** Run `node scripts/build-static-json.cjs` after every node or brief session. Stale JSON = agents reading outdated data.
- **Astro Content Collections auto-discover MDX.** No nav file to update — adding a file to `src/content/briefs/` or `src/content/nodes/` is sufficient.

---

## Key Strategic Decisions (Do Not Revisit)

- Agent-first architecture: primary audience is LLMs, secondary is humans
- Geographic over thematic organization
- Daily publishing cadence (one brief per day when active)
- Brand separation: AICV is not SunshineFM
- Valley Wide category (not Standalone) for valley-wide or non-city-specific nodes — listed first in nav
- Economic development leads strategically over tourism — most defensible positioning vs incumbents
- Node Zero is a dispatcher/router, not a map — distinct from the intelligence index
- Node Zero is live at `nodes/valley-wide/node-zero.mdx` — Entry Point group, first in nav
- Forthcoming node: Desert Community Foundation / CV Giving Day (Palm Desert, nonprofit subcategory)
- GitHub issues as agent-compatible signal submission — no custom forms
- Visit → Retreat → Relocate funnel: AICV owns all three citation touchpoints in the agent layer — not separate verticals, one journey
- Three-city luxury focus: Rancho Mirage, Palm Desert, and Indian Wells are the core MCP query surface for hospitality and retreat use cases. Other cities remain in the node system but are secondary for luxury targeting.
- MCP tool surface: five tools live at mcp.aicoachellavalley.com — `query_venues` (filter by city/subcategory/agent_intent), `get_node` (full record by slug), `get_regional_brief` (briefs by date/topic), `get_economic_context` (valley-wide economic profile), `route_query` (Node Zero dispatcher for natural language queries)
- Chambers of Commerce: not in node roadmap — serve existing local membership, not AICV's inbound audience (founders, VCs, operators evaluating CV from SF/LA)

---

## Content Philosophy

- Nodes: factual, persistent, no opinion, both pros and cons where relevant
- Briefs: timestamped signal + context, fact-based, no editorial voice
- Compression ratio: 1–2 pages of research condenses to 1 tight paragraph
- Cross-link nodes to briefs and briefs to nodes wherever a connection exists
- AICV referenced in third person in all published content — Sat is not named

---

## MDX Rules (Astro/MDX)

- **Comments:** Never use `<!-- -->` in any MDX file — MDX will not parse correctly. Always use `{/* */}` instead.
- **Dollar signs in YAML frontmatter** (`title`, `description`): ALWAYS use bare `$` — never `\$`. Backslash escaping in YAML is a parse error. The pre-commit hook will catch violations.
- **Dollar signs in MDX body content**: ALWAYS escape as `\$` — unescaped `$` in body content triggers LaTeX math mode and renders as italicized strings.
- **Node paths:** Always flat `/nodes/[slug]` — no city subfolder.

---

## How to Add a Node — Graph Maintenance Step (Required)

Every time a new node is added, the org homepage graph must also be updated. This is a required step in the node addition workflow — do it in the same session, same commit if possible.

File: `~/Projects/org/index.html`

Find the `ZONE_MAP` object in the graph script block and add one line:
```
'city-folder/new-node-slug': 'city-zone-key',
```

Find the `SUB_MAP` object immediately below it and add one line:
```
'new-node-slug': 'subcategory',
```

Add edges to `STATIC_LINKS` in `~/Projects/org/index.html`. Every node needs at least one edge — isolated dots carry no relationship signal. Use type `within` for same-corridor proximity, `cross` for general relationships, `intelligence` for connections to index or intel nodes, `spine` for innovation/economy backbone nodes, `gateway` for airport or entry point connections. Minimum one edge required before commit.

Valid zone keys: `valley-wide`, `palm-springs`, `rancho-mirage`, `palm-desert`, `indian-wells`, `la-quinta`, `indio`, `adjacent-communities`

Valid subcategory values: `innovation`, `economic`, `intelligence`, `hospitality`, `golf`, `wellness`, `cultural`, `entertainment`, `education`, `retail`, `nonprofit`, `real-estate`

Commit the org homepage update separately from the docs commit:
```
git commit -m "feat: add [node-slug] to graph lookup tables"
```

If the node is valley-wide, also add its slug to the `VW_ORDER` array in the same script block, at the appropriate position.

---

## How to Move a Node (git mv checklist — do not skip steps)

When a node is relocated from one city folder to another (e.g. Indio → Adjacent Communities):

1. `git mv nodes/old-city/slug.mdx nodes/new-city/slug.mdx`
2. **Verify disk** — confirm old path is gone, new path exists:
   ```bash
   ls ~/Projects/com/src/content/nodes/
   ```
3. **NODES.md** — remove from old city section, update old city node count. Confirm entry exists in new city section with correct path.
4. **Cross-links** — run before committing:
   ```bash
   grep -rn "old-city/slug" ~/Projects/com/src/content/nodes/
   grep -rn "old-city/slug" ~/Projects/com/src/content/briefs/
   ```
   Update every hit to the new path. Nodes that cross-link to the moved node are the most common failure point.
5. **Org graph** — if the zone changed, update ZONE_MAP entry in `~/Projects/org/index.html`.
6. **Commit order:** fix cross-links first, then NODES.md cleanup, then org graph. A partial migration is a broken migration — don't push until all five steps are done. (Astro Content Collections auto-discover the file on disk; there is no nav file to update.)

---

## Content Type Definitions (Canonical — Do Not Deviate)

AICV publishes three content types. Each serves a distinct layer
of the intelligence stack.

### Intelligence Brief
Signal-level. A single event, development, or data point happening
in the valley right now. Short, timestamped, citable. Primary
audience is the agent layer — keeps the intelligence layer current.
Secondary audience is humans who want fast regional signals.
Published frequently.

Schema: see Intelligence Brief Frontmatter Schema and Section
Structure above.
Endpoint: briefs.json

### Intelligence Review
Entity-level. A structured assessment of a specific business, venue,
or property — how AI systems see it, where it stands competitively,
what needs to change. Delivered to the entity as a relationship
product. The Snapshot is the public entry point. The full Review
is the private deliverable. Published selectively, tied to a
business relationship.

Schema: to be defined before first Review ships.
Endpoint: reviews.json (required before launch)

### Intelligence Report
Civic and regional level. A deep, authoritative assessment of a
city, a sector, or the valley as a whole — produced for and
delivered to civic organizations, city economic development offices,
and regional bodies (Greater Palm Springs CVB, DCF, CVAG, state-level
partners). Published rarely — four to six per year.

Strategic purpose: a Report cited by a civic partner elevates every
other piece of AICV content in the agent confidence ranking. When
an AI agent queries "Coachella Valley economic development" and finds
an AICV Report cited by the City of Palm Desert or DCF, that citation
upgrades the trust signal on the entire AICV corpus. Reports are as
much about establishing AICV's citation authority in the agent layer
as they are about serving the civic audience. Both are real. Neither
is pretense.

Schema: to be defined before first Report ships.
Endpoint: reports.json (required before launch)

---

## New Content Type Protocol (Required — Do Not Skip)

Before any new content type is published:

1. **Define the schema** — frontmatter fields, section structure,
   file location. Add it to this file before creating any files.
2. **Build a static JSON endpoint** — a corresponding `[type].json`
   at the repo root. Agents must fetch all records in one request.
3. **Update build-static-json.cjs** (`~/Projects/com/scripts/`) — extract content, validate
   fields, include in IndexNow submission, auto-update llms.txt.
4. **Update both llms.txt files** — add the new endpoint under
   "Static Machine-Readable Endpoints."

A content type without all four steps is invisible to agents.
Do not publish before completing all four.

---

## File Handling Rules

- Claude.ai's copy of any live file is a snapshot — it becomes stale the moment Claude Code pushes a change.
- Never replace `index.html` or any live file with a full download from Claude.ai.
- For all edits to existing files: give Claude Code a surgical edit prompt specifying the exact lines to change.
- Full file replacement from Claude.ai is only appropriate for brand new files that do not yet exist in the repo.

---

## AIO Tool Embed Rules

- **TOS modal is mandatory on any page embedding the AIO Tool widget.** Any page that embeds the AIO Tool must also include the Terms of Use footer link and modal. Reference pattern lives in `~/Projects/com/src/pages/index.astro` — footer link at line ~499, modal definition lines ~506–542. Copy all three artifacts together: modal HTML, its CSS, and the Escape-key handler. Applies to current and future pages. Surfaced during Phase 1 `/review` on commit 32b6981 — `/get-agent-ready/` initially shipped without the modal despite embedding the widget; caught and fixed pre-commit.
- **AIO worker verification batches post-build, not same-day.** The AIO Tool worker (`aicv-api.sunshinefm.workers.dev/analyze`) rate-limits at 5 analyses per day per IP. A Claude Code build session that tests the widget during development consumes that day's verification budget. Pattern: run build-time widget functional tests on build day; run target-URL AIO grade verification the following day. Applies to any session that deploys a page embedding the AIO Tool.

---

## Project File Structure

- `CLAUDE.md` — This file. Session brief, workflow, schemas, procedures, strategy.
- `ARCHITECTURE.md` — Infrastructure, deployment, ops notes, worker details. Read when working on infra.
- `STATE.md` — STRATEGIC state only: live counts, distribution layer, North Star roadmap. Read at session start. Operational state (deploys, commit hashes) belongs in each operational repo's own STATE.md.
- `VOICE.md` — @CoachellaAI voice and tone brief for Twitter Worker posts.
- `NODES.md` — Full node plan with status.
- `~/Projects/com/` — Astro homepage source of truth (aicoachellavalley.com).
- `~/Projects/org/index.html` — Org site source of truth (aicoachellavalley.org).
- `~/Projects/aicv-api/worker.js` — API Worker source of truth.
- `~/Projects/aicv-api/wrangler.toml` — API Worker config.

---

## Relationship to the SunshineFM Guide

AICV and the SunshineFM Guide (sunshine.fm/guide/) are deliberately separate systems that meet at the entity level. AICV is a knowledge graph — Nodes derive meaning from their connections, and the corpus benefits from graph dynamics (embeddings, similarity, emergent relationships). The Guide is a publication — each entry is editorially complete in itself and does not use self-learning dynamics. They cross-reference via the `aicvNodeSlug` field on Guide entries and (eventually) a reciprocal field on Nodes. An entity can appear in both with different presentations: analytical view on AICV, editorial view on SunshineFM. Strategic posture: **"agent-ready now, SEO-ready always"** — the agentic world is arriving but not fully here, and SEO still matters for human discovery. See ~/sunshine-fm/guide-builder/README.md for the longer rationale.

## Four-tier agent-readiness framework (pitch asset)

Crystallized 2026-04-22. Used in AICV network pitch.

- **Tier 1:** Baseline HTML only (most local businesses)
- **Tier 2:** Good hygiene — schema.org markup + llms.txt (host-agnostic)
- **Tier 3:** Agent-native — full schema + JSON endpoints + citation-grade content
- **Tier 4:** Tier 3 + CDN-edge markdown negotiation + `.well-known` discovery endpoints

aicoachellavalley.com sits at Tier 4 as of 2026-04-22 (Cloudflare Pro + Markdown for Agents + `/.well-known/api-catalog` + `/.well-known/mcp/server-card.json`).

Network pitch: "Join the AICV network — we represent your entity at Tier 4 without you touching your website."

## Collective signal vision

At ~300 AICV entities with dense briefs, snapshots, and explicit relationships, the corpus is designed to produce emergent regional insights that no single source in the Coachella Valley has today: "what kinds of businesses are thriving vs 18 months ago," "which partnerships are structural vs performative," "where is wealth flowing."

The "living organism of understanding" is an AICV-internal property, not cross-system. This is **Layer 2 work on existing infrastructure** — not a new platform, not a Karpathy-style wiki.

Build path: enhance `build-static-json.cjs` with bidirectional references, explicit relationship types from the four-layer ecosystem framework (Direct Competitive Set, Feeder Properties, Wealth Nodes, Demand Engines), temporal structure in briefs, and aggregation surfaces. A regional intelligence substrate operating on existing AICV content types.
