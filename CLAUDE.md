# AICV — Project Brief for Claude Sessions

## What This Is

AI Coachella Valley (AICV) is an agent-first intelligence documentation site for the Coachella Valley's emerging AI economy. Primary goal: first LLM citation by March 2026.

Live site: https://agent.aicoachellavalley.com
GitHub: https://github.com/aicoachellavalley/docs
Mintlify account: AICV (separate from SunshineFM)

## What We're Building

A two-layer intelligence system:

- **Nodes** — Persistent geographic anchors, one per institution/location, organized by city
- **Intelligence Briefs** — Daily timestamped signals, one per day, filed by date

## Current State (as of February 26, 2026)

- **33 nodes live** across 9 cities — all on v2 schema with verified, status, agent_intent fields
- **21 intelligence briefs live** — 4 from 2025, 17 from February 2026
- **Homepage v5 live** on `aicoachellavalley.com` via Cloudflare Pages — DNS cutover complete February 26, 2026
- **Cloudflare Worker live** at `api.aicoachellavalley.com` — rate limiting, input validation, CORS locked to production domain

## Infrastructure

| Component | Repo | URL |
|-----------|------|-----|
| Docs (Mintlify) | ~/Projects/docs/ | agent.aicoachellavalley.com |
| Homepage (v5) | ~/Projects/homepage/index.html | aicoachellavalley-homepage.pages.dev |
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

## Pending Tasks (Priority Order)

### Platform
1. GitHub issues intake form — replace `mailto:sat@aicv.co` CTA in AIO tool network CTA
2. Node Zero — action routing layer, not yet built
3. wrangler.toml — add comment noting `api.aicoachellavalley.com` custom domain

### Content
1. Palm Desert 2026 goals brief — parked, waiting on Thursday council session notes
2. Submit `aicoachellavalley.com` to Google Search Console for reindexing post-cutover

## Wrangler Note

`wrangler secret put` asks for the value TWICE as confirmation — paste the same key both times.

## AIO Tool Note

Three-layer security: input validation → rate limiting (5/day per IP via Cloudflare KV) → page fetch → Anthropic analysis. Model: `claude-haiku-4-5-20251001` — do not change to Sonnet, deliberate cost decision. Words analyzed counter in KV key `stats:words_analyzed`, seeded at 10000. CORS locked to `https://aicoachellavalley.com` and `https://www.aicoachellavalley.com`.

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
agent_intent: []
---

## Intelligence Brief Section Structure (Required — Do Not Deviate)

# [Title]

**Date:** Month DD, YYYY

## Signal

## Agent Signal

## Context

## Related Nodes

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

## Project File Structure

- CLAUDE.md — This file. Session continuity brief.
- NODES.md — Full node plan with status
- docs.json — Mintlify navigation (source of truth for what's live)
- ~/Projects/homepage/index.html — Homepage v5 source of truth
- ~/Projects/aicv-api/worker.js — Worker source of truth
- ~/Projects/aicv-api/wrangler.toml — Worker config
