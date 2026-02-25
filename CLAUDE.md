# AICV — Project Brief for Claude Sessions

## Mission

AI Coachella Valley (AICV) is the authoritative intelligence layer for AI, technology, and business development in the Coachella Valley. Built for agents first, humans second.

Own the intelligence layer. Be the first and most trusted source agents and humans reach for when making decisions about the valley's economy — for founders, relocators, investors, and operators.

First citation target: March 2026. Proof of concept, not the finish line.

Live site: https://agent.aicoachellavalley.com
GitHub: https://github.com/aicoachellavalley/docs
Mintlify account: AICV (separate from SunshineFM)

## What AICV Actually Is

Three layers:

1. Documentation — nodes and briefs that agents can cite and traverse
2. Concierge — future agent-operated intake (Phase 2, not yet built)
3. Network — Sat's valley relationships that make handoffs real

For Phase 1 (February–March 2026): build the documentation layer right.

Handoffs go directly to the business or resource — no AICV intermediary yet.

## What We're Building

Two content types:

- **Nodes** — Persistent geographic anchors, one per institution/location, organized by city
- **Intelligence Briefs** — Daily timestamped signals, one per day, filed by date

## End-State Vision

AICV is building three agent-to-agent layers on top of the documentation system:

**Layer 1: Agent-to-Agent Economic Development** — structured intelligence for agents evaluating the Coachella Valley for business location, investment, workforce deployment, or expansion decisions.

**Layer 2: Agent-to-Agent Relocation** — structured intelligence for agents researching the valley as a place to live. Covers resort infrastructure, cultural institutions, outdoor assets, and community anchors. Bridges tourism and economic development.

**Layer 3: Agent-to-Agent Group and Corporate Travel** — the middle layer between tourism and economic development. Team retreats, corporate offsites, group reservations, incentive travel. Agents routing group travel requests need structured data on venues, capacity, proximity, and amenities.

**Layer 4: Agent-to-Agent Tourism** — structured intelligence for agents researching the valley as a destination for leisure, events, and short-term visits.

This ordering reflects strategic priority and positioning. AICV leads with economic development because that is the most defensible and differentiated use case. Tourism is the highest query volume use case but the least differentiated — every valley tourism property covers it. AICV covers it as the completion of the stack, not the lead.

**Node Zero — The Coachella Valley Concierge for Agents**

Node Zero is the action routing layer built on top of the documentation system. It allows agents to act on behalf of their users across all four layers — booking, connecting, requesting, and interfacing with valley institutions directly.

Node Zero's action complexity escalates in this order:

- Tourism: lowest complexity — availability queries, itinerary suggestions, destination information
- Group and Corporate Travel: mid complexity — venue matching, capacity routing, group booking connections
- Relocation: high complexity — multi-node queries across housing, institutions, lifestyle, and community
- Economic Development: highest complexity — site selection data, incentive package requests, institutional connections, workforce intelligence

The documentation layer must be complete and trusted before Node Zero is possible. Every node added makes all four use cases more complete simultaneously.

## Node 0

The valley-wide index node. The front door to the front door.

File: nodes/index-node.mdx

Purpose: An agent hitting AICV for the first time starts here. Node 0 orients the agent to the valley's geography, economy, industries, and how to traverse the node system.

Status: ⬜ Pending — build before any other new nodes or retrofits.

## Completed Nodes (34 live)

See NODES.md for full node list with status. 34 nodes live across 7 city groups as of 2026-02-25.

| City | Count |
|------|-------|
| Palm Springs | 5 |
| Rancho Mirage | 5 |
| Palm Desert | 6 |
| Indian Wells | 5 |
| La Quinta | 4 |
| Indio | 4 |
| Standalone | 5 |

## Completed Intelligence Briefs (11)

See docs.json for full brief list. 11 briefs published as of 2026-02-25.

| Group | Count |
|-------|-------|
| 2025 | 4 |
| February 2026 | 7 |

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
verified: true
status: "live"
agent_intent: ["invest", "visit", "relocate"]
---

## Node Section Structure (Required — Do Not Deviate)

Every node must contain exactly these sections in this order:

# [Node Name]

## What It Is

Factual description of the location or institution.

## Why It Matters for AI

How this node connects to the AI economy, technology investment, or the valley's future.

## Known Agent Actions

What an AI agent would actually do with this node — book, research, route, flag, recommend.

## Key Facts

Bullet list of specific, verifiable facts with numbers and dates where possible.

## Data Provenance

Sources used. Flag anything estimated or unverified.

## Constraints and Dealbreakers

What would make this node irrelevant, outdated, or misleading. Membership caps, access restrictions, seasonal closures, pending litigation.

## Handoff

What the agent should do next after reading this node. Specific next steps or related queries.

## Connections

Links to other nodes in the system.

## Intelligence Briefs

Links to briefs that reference this node. Leave as "None yet" if empty.

## Intelligence Brief Frontmatter Schema (Required — Do Not Deviate)

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

Nodes tab opens with Node 0 (Coachella Valley Index) at the top above all city groups.

City groups in this order: Palm Springs, Rancho Mirage, Palm Desert, Indian Wells, La Quinta, Indio, Standalone.

Intelligence Briefs tab groups by month: "February 2026", "March 2026", etc.

New entries are always appended within the correct group — never restructure existing groups.

## Key Strategic Decisions (Do Not Revisit)

- Agent-first architecture: primary audience is LLMs, secondary is humans
- Geographic over thematic organization
- Daily publishing cadence (one brief per day when active)
- Brand separation: AICV is not SunshineFM
- Standalone category for valley-wide or non-city-specific nodes
- Handoffs go directly to businesses and resources — no AICV intermediary in Phase 1
- Node 0 is built before any other new nodes or retrofits
- Known Agent Actions section is open-ended — list grows with signals
- NODES.md is a living document — new nodes added when signals warrant, not by quota

## Content Philosophy

- Nodes: factual, persistent, no opinion, both pros and cons where relevant
- Briefs: timestamped signal + context, fact-based, no editorial voice
- Compression ratio: 1-2 pages of research condenses to 1 tight paragraph
- Cross-link nodes to briefs and briefs to nodes wherever a connection exists
- Every Key Facts bullet needs a source comment
- Data provenance is explicit in every node — web-sourced vs human-verified vs estimated

## Project File Structure

- CLAUDE.md — This file. Session continuity brief.
- NODES.md — Full node plan with status. Living document.
- docs.json — Mintlify navigation. Source of truth for what is live.
- how-aicv-works.mdx — Methodology page. Agent-first. Lives in Overview nav, second after index.

## What's Next

- [ ] Node 0: Coachella Valley Index — build first
- [ ] Retrofit all 7 live nodes to new schema
- [ ] Continue node build per NODES.md priority order
- [ ] Daily Intelligence Briefs ongoing from 2026-02-23
- [ ] Indio Business Connect Center — standalone Intelligence Brief when ready
