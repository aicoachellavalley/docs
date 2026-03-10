# AICV — Project Brief for Claude Sessions

## What This Is

AI Coachella Valley (AICV) is an agent-first intelligence documentation site for the Coachella Valley's emerging AI economy. Primary goal: to be the authoritative cited source for Coachella Valley intelligence across all major LLMs and AI agents.

Live site: https://agent.aicoachellavalley.com
GitHub: https://github.com/aicoachellavalley/docs
Mintlify account: AICV (separate from SunshineFM)

## What We're Building

A two-layer intelligence system:

- **Nodes** — Persistent geographic anchors, one per institution/location, organized by city
- **Intelligence Briefs** — Daily timestamped signals, one per day, filed by date

## Current State (as of March 9, 2026)

- **43 nodes live** across 9 cities — all on v2 schema with verified, status, agent_intent fields
- **64 intelligence briefs live** — 4 from 2025, 14 from January 2026, 32 from February 2026, 14 from March 2026
- **Homepage v5 live** at aicoachellavalley.com — auto-deploy via GitHub → Cloudflare Pages
- **Cloudflare Worker live** at api.aicoachellavalley.com — handling AIO proxy and dynamic stats

## Infrastructure

| Component | Repo | URL |
|-----------|------|-----|
| Docs (Mintlify) | ~/Projects/docs/ | agent.aicoachellavalley.com |
| Homepage (v5) | ~/Projects/homepage/index.html | aicoachellavalley.com |
| Worker (API proxy) | ~/Projects/aicv-api/worker.js | api.aicoachellavalley.com |
| MCP Worker | ~/Projects/aicv-mcp/worker.js | mcp.aicoachellavalley.com |
| Org site | ~/Projects/org/index.html | aicoachellavalley.org |

Homepage deploys automatically via GitHub → Cloudflare Pages on every push to main.
Worker handles AIO tool proxy and dynamic stats (node/brief counts from GitHub).
Worker is NOT git-controlled — deploy changes via `wrangler deploy` from `~/Projects/aicv-api/`. There is no git repo in that directory.
MCP Worker is NOT git-controlled — deploy changes via `wrangler deploy` from `~/Projects/aicv-mcp/`. There is no git repo in that directory.

## MCP Worker Bug Fixes (March 9, 2026)

Three bugs patched and deployed (version 7f86d40a):
- `notifications/initialized` method now returns `respond({})` instead of a -32601 error — required for Claude Desktop MCP handshake
- `extractNodePaths` and `extractBriefPaths` now iterate `docsJson.navigation.tabs` (not `docsJson.navigation`) — fixes silent empty results on all tool calls
- City filtering normalized via `toKebab()` — converts frontmatter `"Palm Desert"` → `"palm-desert"` before comparing, so kebab-case input from agents matches title-case frontmatter values

Claude Desktop connection confirmed working as of March 9, 2026, using mcp-remote bridge at mcp.aicoachellavalley.com.

Periodic node audit: run subcategory and schema audit every 20 nodes or annually. Check for missing subcategory values, taxonomy drift, and v2 field compliance. Use the recon prompt from the March 7 2026 session.
API key is in Worker secrets — not in client code.
AIO tool uses `claude-haiku-4-5-20251001` — deliberate cost decision, do not change to Sonnet.

## Workflow: Claude.ai + Claude Code

- **Claude.ai** — Strategy, content writing, editorial decisions, research
- **Claude Code** — File creation, git operations, docs.json updates
- **Sat** — Courier between the two systems

Claude Code must not commit without explicit approval.

## Wrangler Note

`wrangler secret put` asks for the value TWICE as confirmation — paste the same key both times.

## Mintlify Ops Note

If a push doesn't update the live site within 5–10 minutes, the GitHub App authorization has likely lapsed. Check:
- https://dashboard.mintlify.com — deployment logs and redeploy button
- https://github.com/organizations/aicoachellavalley/settings/installations — GitHub App auth

The error message "Not authorized to fetch tree" is the tell.

## Node Frontmatter Schema (Required — Do Not Deviate)

Every node file must open with exactly these fields:

---
title: ""
description: ""
city: ""
category: "landmark"
subcategory: ""
last_updated: "YYYY-MM-DD"
---

Valid category values: `landmark`, `event`

Valid subcategory values: `hospitality`, `golf`, `wellness`, `cultural`, `entertainment`, `economic`, `education`, `retail`, `intelligence`, `nonprofit`, `real-estate`

## Node Section Structure (Required — Do Not Deviate)

Every node must contain exactly these sections in this order:

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

## Intelligence Brief Frontmatter Schema (Required — Do Not Deviate)

---
title: ""
description: ""
date: "YYYY-MM-DD"
tags: []
---

## Intelligence Brief Section Structure (Required — Do Not Deviate)

# [Title]

**Date:** Month DD, YYYY

## Signal

## Context

## Agent Signal

## Related Nodes

## Also Noted Frontmatter Schema (Required — Do Not Deviate)

---
title: "Also Noted — [Date]"
description: ""
date: "YYYY-MM-DD"
tags: ["also-noted"]
---

## Also Noted Section Structure (Required — Do Not Deviate)

# Also Noted — [Date]

**Date:** Month DD, YYYY

## Signals

### [Signal Title]

One tight paragraph — what it is, why it matters for the AI economy.

### [Signal Title]

One tight paragraph.

## Agent Signal

## Related Nodes

## How to Add an Also Noted Brief

1. Identify 2-5 secondary signals from SunshineFM transcript that don't warrant standalone briefs
2. Draft in Claude.ai using the schema above
3. Claude Code creates file named YYYY-MM-DD-also-noted.mdx in intelligence-briefs/
4. Add to docs.json under correct month group in Intelligence Briefs tab
5. Review before committing
6. Commit: feat: add [date] also-noted brief
7. Push to main
8. Increment homepage stat-briefs fallback by 1

## How to Add a Node

1. Research the location in Claude.ai
2. Draft MDX using the frontmatter schema and section structure above
3. Claude Code creates the file in the correct city subfolder
4. Update docs.json navigation to include the new page path
5. Review full file tree before committing
6. Commit: feat: add [location] node
7. Push to main

## How to Add an Intelligence Brief

1. Identify one AI-economy signal from local news or inbound inquiry
2. Write brief in Claude.ai using the frontmatter schema and section structure above
3. Claude Code creates file named YYYY-MM-DD-slug.mdx in intelligence-briefs/
4. Add to docs.json under correct month group in Intelligence Briefs tab
5. Review before committing
6. Commit: feat: add [date] intelligence brief
7. Push to main
8. Increment homepage stat-briefs fallback by 1 (prevents stat drift)

## Standard Claude Code Courier Block

Every intelligence brief drafted in Claude.ai must end with the following courier block:

**Claude Code instructions:**
1. Create file: intelligence-briefs/[filename].mdx
2. Add to docs.json under [Month YYYY] group in Intelligence Briefs tab
3. Increment homepage stat-briefs fallback by 1
4. Commit: feat: add [date] [slug] brief
5. Push to main

## docs.json Navigation Pattern

Three tabs: Overview, Intelligence Briefs, Nodes.

Nodes tab groups by city in this order: Valley Wide, Palm Springs, Rancho Mirage, Palm Desert, Indian Wells, La Quinta, Indio.

Intelligence Briefs tab groups by month in reverse chronological order: most recent month first.

New entries are always appended within the correct group — never restructure existing groups.

## Key Strategic Decisions (Do Not Revisit)

- Agent-first architecture: primary audience is LLMs, secondary is humans
- Geographic over thematic organization
- Daily publishing cadence (one brief per day when active)
- Brand separation: AICV is not SunshineFM
- Valley Wide category (not Standalone) for valley-wide or non-city-specific nodes — listed first in nav
- Economic development leads strategically over tourism — most defensible positioning vs incumbents
- Node Zero is a dispatcher/router, not a map — distinct from the intelligence index
- Node Zero is live at nodes/valley-wide/node-zero.mdx — Entry Point group, first in nav
- Forthcoming node: Desert Community Foundation / CV Giving Day (Palm Desert, nonprofit subcategory)
- GitHub issues as agent-compatible signal submission — no custom forms
- Visit → Retreat → Relocate funnel: AICV owns all three citation touchpoints in the agent layer. These are not separate verticals — they are one journey.
- Three-city luxury focus: Rancho Mirage, Palm Desert, and Indian Wells are the core MCP query surface for hospitality and retreat use cases. Other cities remain in the node system but are secondary for luxury targeting.
- MCP tool surface: five tools live at mcp.aicoachellavalley.com — query_venues (filter by city/subcategory/agent_intent), get_node (full record by slug), get_regional_brief (briefs by date/topic), get_economic_context (valley-wide economic profile), route_query (Node Zero dispatcher for natural language queries)

## Content Philosophy

- Nodes: factual, persistent, no opinion, both pros and cons where relevant
- Briefs: timestamped signal + context, fact-based, no editorial voice
- Compression ratio: 1-2 pages of research condenses to 1 tight paragraph
- Cross-link nodes to briefs and briefs to nodes wherever a connection exists
- MDX syntax: Never use `<!-- -->` in any MDX file. Mintlify will fail to parse them and return 404. Always use `{/* */}` for comments instead.

## Claude.ai File Handling Rule

Claude.ai's copy of any live file is a snapshot and becomes stale the moment Claude Code pushes a change. Never replace index.html or any other live file with a full file download from Claude.ai.

For all edits to existing files, Claude Code should receive a surgical edit prompt specifying the exact lines to change. Full file replacement from Claude.ai is only appropriate for brand new files that do not yet exist in the repo.

## Homepage Deployment Rule

Before committing any updated index.html, always run:

```
git diff HEAD ~/Projects/homepage/index.html
```

Review the diff for unintended regressions — especially the stats bar (IDs, fallback values, labels, JS handlers). The four stat blocks are:
- stat-nodes — Geographic nodes
- stat-briefs — Intelligence briefs published
- stat-commits — Platform commits since launch
- stat-words — Words analyzed from local businesses (fallback: 10k, pulls s.wordsAnalyzed)

Never overwrite index.html from an external file without diffing first.

## Project File Structure

- CLAUDE.md — This file. Session continuity brief.
- NODES.md — Full node plan with status
- docs.json — Mintlify navigation (source of truth for what's live)
- ~/Projects/homepage/index.html — Homepage v5 source of truth
- ~/Projects/org/index.html — Org site source of truth (aicoachellavalley.org)
- ~/Projects/aicv-api/worker.js — Worker source of truth
- ~/Projects/aicv-api/wrangler.toml — Worker config
