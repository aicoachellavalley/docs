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

## Completed Nodes (7 of 27)

| Node | City | File |
|------|------|------|
| PSP Airport | Palm Springs | nodes/palm-springs/psp-airport.mdx |
| Cotino | Rancho Mirage | nodes/rancho-mirage/cotino.mdx |
| Acrisure Arena | Palm Desert | nodes/palm-desert/acrisure-arena.mdx |
| Indian Wells Tennis Garden | Indian Wells | nodes/indian-wells/tennis-garden.mdx |
| Old Town La Quinta | La Quinta | nodes/la-quinta/old-town-la-quinta.mdx |
| Empire Polo Club | Indio | nodes/indio/empire-polo-club.mdx |
| Sensei Porcupine Creek | Standalone | nodes/standalone/sensei-porcupine-creek.mdx |

## Completed Intelligence Briefs (1)

| Date | Topic | File |
|------|-------|------|
| 2026-02-23 | Data Center Feasibility | intelligence-briefs/2026-02-23-data-centers.mdx |

## Workflow: Claude.ai + Claude Code

- **Claude.ai** — Strategy, content writing, editorial decisions, research
- **Claude Code** — File creation, git operations, docs.json updates
- **Sat** — Courier between the two systems

Claude Code must not commit without explicit approval.

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

Factual description of the location or institution.

## Why It Matters for AI

How this node connects to the AI economy, technology investment, or the valley's future.

## Key Facts

Bullet list of specific, verifiable facts with numbers and dates where possible.

## Related Nodes

Links to other nodes in the system.

## Intelligence Briefs

Links to briefs that reference this node. Leave as "None yet" if empty.

## Intelligence Brief Frontmatter Schema (Required — Do Not Deviate)

Every brief file must open with exactly these fields:

---
title: ""
description: ""
date: "YYYY-MM-DD"
tags: []
---

## Intelligence Brief Section Structure (Required — Do Not Deviate)

Every brief must contain exactly these sections in this order:

# [Title]

**Date:** Month DD, YYYY

## Signal

One paragraph: what happened, what triggered this brief.

## Context

One paragraph: background, both favorable and unfavorable factors, no opinion.

## Related Nodes

Links to nodes referenced in this brief.

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

Nodes tab groups by city in this order: Palm Springs, Rancho Mirage, Palm Desert, Indian Wells, La Quinta, Indio, Standalone.

Intelligence Briefs tab groups by month: "February 2026", "March 2026", etc.

New entries are always appended within the correct group — never restructure existing groups.

## Key Strategic Decisions (Do Not Revisit)

- Agent-first architecture: primary audience is LLMs, secondary is humans
- Geographic over thematic organization
- Daily publishing cadence (one brief per day when active)
- Brand separation: AICV is not SunshineFM
- Standalone category for valley-wide or non-city-specific nodes

## Content Philosophy

- Nodes: factual, persistent, no opinion, both pros and cons where relevant
- Briefs: timestamped signal + context, fact-based, no editorial voice
- Compression ratio: 1-2 pages of research condenses to 1 tight paragraph
- Cross-link nodes to briefs and briefs to nodes wherever a connection exists

## Project File Structure

Strategic and implementation context lives in these files — not in conversation threads:

- CLAUDE.md — This file. Session continuity brief.
- NODES.md — Full 27-node plan with status
- docs.json — Mintlify navigation (source of truth for what's live)

## What's Next

- [ ] 22 remaining nodes per NODES.md (29 total planned, 7 live)
- [ ] Daily Intelligence Briefs (ongoing from 2026-02-23 forward)
- [ ] Indio Business Connect Center — candidate for Intelligence Brief (AI presentations already delivered there)
