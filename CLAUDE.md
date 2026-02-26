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
- **12 intelligence briefs live** — 4 from 2025, 8 from February 2026
- **Homepage v5 live** on Cloudflare Pages with auto-deploy from GitHub
- **Cloudflare Worker live** handling AIO proxy and dynamic stats

## Infrastructure

| Component | Repo | URL |
|-----------|------|-----|
| Docs (Mintlify) | ~/Projects/docs/ | agent.aicoachellavalley.com |
| Homepage (v5) | ~/Projects/homepage/index.html | aicoachellavalley-homepage.pages.dev |
| Worker (API proxy) | ~/Projects/aicv-api/worker.js | aicv-api.sunshinefm.workers.dev |

Homepage deploys automatically via GitHub → Cloudflare Pages on every push to main.
Worker handles AIO tool proxy and dynamic stats (node/brief counts from GitHub).
API key is in Worker secrets — not in client code.
AIO tool uses `claude-haiku-4-5-20251001` — deliberate cost decision, do not change to Sonnet.

## Workflow: Claude.ai + Claude Code

- **Claude.ai** — Strategy, content writing, editorial decisions, research
- **Claude Code** — File creation, git operations, docs.json updates
- **Sat** — Courier between the two systems

Claude Code must not commit without explicit approval.

## Pending Tasks (Priority Order)

1. Font weight fix — Syne section headers from 800 → 600 in homepage (prompt ready)
2. Rate limiting on AIO tool — Cloudflare KV, 5 analyses per IP per day
3. CORS lockdown — change Worker `*` to `aicoachellavalley.com` after DNS cutover
4. Input validation on Worker URL field
5. DNS cutover — point Namecheap nameservers to Cloudflare
6. Swap Worker URL from `aicv-api.sunshinefm.workers.dev` to `api.aicoachellavalley.com` (one line in WORKER_BASE constant in homepage)
7. Node Zero — confirm live status and review routing layer completeness
8. Palm Desert 2026 goals brief — parked, waiting on Thursday council session notes

## Font Fix Prompt (Ready for Claude Code)

In `~/Projects/homepage/index.html` find all instances of `font-weight: 800` where font-family is Syne, and change them to `font-weight: 600`. Apply to section headers — `.aio-title`, `.intel-title`, `.hero-headline` and similar. Do NOT change `.stat-n` (keep 800) and do NOT change nav logo mark (keep 800). Commit as `fix: lighten section header font weight to 600` and push to main.

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
