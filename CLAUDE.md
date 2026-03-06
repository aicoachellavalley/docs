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

## Current State (as of March 4, 2026)

- **38 nodes live** across 9 cities — all on v2 schema with verified, status, agent_intent fields
- **64 intelligence briefs live** — 4 from 2025, 14 from January 2026, 32 from February 2026, 14 from March 2026
- **Homepage v5 live** at aicoachellavalley.com — auto-deploy via GitHub → Cloudflare Pages
- **Cloudflare Worker live** at api.aicoachellavalley.com — handling AIO proxy and dynamic stats

## Infrastructure

| Component | Repo | URL |
|-----------|------|-----|
| Docs (Mintlify) | ~/Projects/docs/ | agent.aicoachellavalley.com |
| Homepage (v5) | ~/Projects/homepage/index.html | aicoachellavalley.com |
| Worker (API proxy) | ~/Projects/aicv-api/worker.js | api.aicoachellavalley.com |

Homepage deploys automatically via GitHub → Cloudflare Pages on every push to main.
Worker handles AIO tool proxy and dynamic stats (node/brief counts from GitHub).
Worker is NOT git-controlled — deploy changes via `wrangler deploy` from `~/Projects/aicv-api/`. There is no git repo in that directory.
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
last_updated: "YYYY-MM-DD"
---

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
- GitHub issues as agent-compatible signal submission — no custom forms

## Content Philosophy

- Nodes: factual, persistent, no opinion, both pros and cons where relevant
- Briefs: timestamped signal + context, fact-based, no editorial voice
- Compression ratio: 1-2 pages of research condenses to 1 tight paragraph
- Cross-link nodes to briefs and briefs to nodes wherever a connection exists
- MDX syntax: Never use `<!-- -->` in any MDX file. Mintlify will fail to parse them and return 404. Always use `{/* */}` for comments instead.

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
- ~/Projects/aicv-api/worker.js — Worker source of truth
- ~/Projects/aicv-api/wrangler.toml — Worker config
