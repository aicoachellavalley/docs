# AICV — Project Brief for Claude Sessions

## Session Start — Required

Before any content operation:
1. Read STATE.md for current counts, active month group, and last commit
2. Read ARCHITECTURE.md only if working on infrastructure, deployment, or ops

Do not create or edit any file without completing step 1.

---

## What This Is

AI Coachella Valley (AICV) is an agent-first intelligence documentation site for the Coachella Valley's emerging AI economy. Primary goal: to be the authoritative cited source for Coachella Valley intelligence across all major LLMs and AI agents.

Live site: https://agent.aicoachellavalley.com
GitHub: https://github.com/aicoachellavalley/docs
Mintlify account: AICV (separate from SunshineFM)

---

## What We're Building

A three-layer intelligence system:

- **Nodes** — Persistent geographic anchors, one per institution/location, organized by city
- **Intelligence Briefs** — Daily timestamped signals, one per day, filed by date
- **Also Noted** — Secondary signal roundups, 2–5 signals per file, filed by date

---

## Workflow

- **Claude.ai** — Strategy, content writing, editorial decisions, research
- **Claude Code** — File creation, git operations, docs.json updates
- **Sat** — Courier between the two systems

Claude Code must not commit without explicit approval.

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
---
```

Valid `category` values: `landmark`, `event`

Valid `subcategory` values: `hospitality`, `golf`, `wellness`, `cultural`, `entertainment`, `economic`, `education`, `retail`, `intelligence`, `nonprofit`, `real-estate`, `innovation`

---

## Node Section Structure (Required — Do Not Deviate)

Every node must contain exactly these sections in this order:

```
# [Node Name]

## What It Is

## Why It Matters for AI

## Key Facts

## Known Agent Actions

## Data Provenance

## Constraints and Dealbreakers

## Handoff

## Related Nodes

## Intelligence Briefs
```

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
3. Claude Code creates file named `YYYY-MM-DD-slug.mdx` in `intelligence-briefs/`
4. Add to `docs.json` under correct month group in Intelligence Briefs tab
5. Review before committing
6. Commit: `feat: add [date] intelligence brief`
7. Push to main
8. Increment `stat-briefs` fallback in homepage by 1 (prevents stat drift)
9. Update STATE.md counts and last commit hash

---

## How to Add an Also Noted Brief

1. Identify 2–5 secondary signals from SunshineFM transcript that don't warrant standalone briefs
2. Draft in Claude.ai using the schema above
3. Claude Code creates file named `YYYY-MM-DD-also-noted.mdx` in `intelligence-briefs/`
4. Add to `docs.json` under correct month group in Intelligence Briefs tab
5. Review before committing
6. Commit: `feat: add [date] also-noted brief`
7. Push to main
8. Increment `stat-briefs` fallback by 1
9. Update STATE.md counts and last commit hash

---

## How to Add a Node

1. Research the location in Claude.ai
   - Write `agent_summary` as a single sentence (max 40 words) answering the most likely cold query that would find this node — name the location, what it is, and why it matters for agents
2. Draft MDX using the frontmatter schema and section structure above
3. Claude Code creates the file in the correct city subfolder under `nodes/`
4. Update `docs.json` navigation to include the new page path
5. Review full file tree before committing
6. Commit: `feat: add [location] node`
7. Push to main
8. Update STATE.md counts and last commit hash

---

## Standard Claude Code Courier Block

Every intelligence brief drafted in Claude.ai must end with:

**Claude Code instructions:**
1. Create file: `intelligence-briefs/[filename].mdx`
2. Add to `docs.json` under [Month YYYY] group in Intelligence Briefs tab
3. Increment homepage `stat-briefs` fallback by 1
4. Commit: `feat: add [date] [slug] brief`
5. Push to main

---

## docs.json Navigation Pattern

Three tabs: Overview, Intelligence Briefs, Nodes.

**Nodes tab** — city groups in this order:
1. Entry Point (Node Zero only)
2. Valley Wide
3. Palm Springs
4. Rancho Mirage
5. Palm Desert
6. Indian Wells
7. La Quinta
8. Indio

**Intelligence Briefs tab** — month groups in reverse chronological order: most recent month first.

New entries always appended within the correct group — never restructure existing groups.

---

## Key Learnings

- **Agent-readability is not automatic.** Mintlify renders via JS — agents fetching page URLs get empty shells. The static JSON endpoints (nodes.json, briefs.json at repo root) are the actual agent-readable layer. Run build-static-json.js after every content session. The MCP worker bypasses Mintlify entirely and is the preferred access path for structured agent queries.

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

---

## Content Philosophy

- Nodes: factual, persistent, no opinion, both pros and cons where relevant
- Briefs: timestamped signal + context, fact-based, no editorial voice
- Compression ratio: 1–2 pages of research condenses to 1 tight paragraph
- Cross-link nodes to briefs and briefs to nodes wherever a connection exists
- AICV referenced in third person in all published content — Sat is not named

---

## MDX Rules (Mintlify — Do Not Violate)

- **Comments:** Never use `<!-- -->` in any MDX file — Mintlify will fail to parse and return 404. Always use `{/* */}` instead.
- **Dollar signs in body content:** Always escape as `\$` (e.g. `\$2.1 billion`) — unescaped `$` triggers LaTeX math mode and renders as italicized strings.
- **Dollar signs in YAML frontmatter** (`title`, `description`): Use bare `$` — backslash escaping in YAML is a parse error and causes a 404.
- **Node paths:** Always `nodes/valley-wide/` — never `nodes/valley-wide/` (directory was renamed; stale path causes broken nav).

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

Valid zone keys: `valley-wide`, `palm-springs`, `rancho-mirage`, `palm-desert`, `indian-wells`, `la-quinta`, `indio`

Valid subcategory values: `innovation`, `economic`, `intelligence`, `hospitality`, `golf`, `wellness`, `cultural`, `entertainment`, `education`, `retail`, `nonprofit`, `real-estate`

Commit the org homepage update separately from the docs commit:
```
git commit -m "feat: add [node-slug] to graph lookup tables"
```

If the node is valley-wide, also add its slug to the `VW_ORDER` array in the same script block, at the appropriate position.

---

## File Handling Rules

- Claude.ai's copy of any live file is a snapshot — it becomes stale the moment Claude Code pushes a change.
- Never replace `index.html` or any live file with a full download from Claude.ai.
- For all edits to existing files: give Claude Code a surgical edit prompt specifying the exact lines to change.
- Full file replacement from Claude.ai is only appropriate for brand new files that do not yet exist in the repo.

---

## Project File Structure

- `CLAUDE.md` — This file. Session brief, workflow, schemas, procedures, strategy.
- `ARCHITECTURE.md` — Infrastructure, deployment, ops notes, worker details. Read when working on infra.
- `STATE.md` — Live counts, active month group, last commit. Read at session start.
- `VOICE.md` — @CoachellaAI voice and tone brief for Twitter Worker posts.
- `NODES.md` — Full node plan with status.
- `docs.json` — Mintlify navigation (source of truth for what's live).
- `~/Projects/homepage/index.html` — Homepage v5 source of truth.
- `~/Projects/org/index.html` — Org site source of truth (aicoachellavalley.org).
- `~/Projects/aicv-api/worker.js` — API Worker source of truth.
- `~/Projects/aicv-api/wrangler.toml` — API Worker config.
