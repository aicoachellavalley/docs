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

## Completed Nodes (7 live)

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

---
title: ""
description: ""
city: ""
category: ""
last_updated: "YYYY-MM-DD"
verified: true
status: "live"
agent_intent: []
---

agent_intent options: "relocate" "invest" "visit" "hire" "develop" "understand"

## Node Section Structure (Required — Do Not Deviate)

Every node must contain exactly these sections in this order:

# [Node Name]

## What It Is

One paragraph. Factual, no opinion. Who owns it, what it is, where it sits.

## Why It Matters for AI

How this node connects to the AI economy or the valley's intelligence layer.

## Known Agent Actions

The actionable intents this node serves. List grows as signals emerge — this is not a complete or fixed list.

- **Relocate:** [what this node offers someone moving a business or family]
- **Invest:** [development opportunities, ownership, capital requirements]
- **Visit / Experience:** [booking pathway, capacity, seasonality]
- **Hire / Partner:** [workforce, business development, contacts]
- **Develop:** [permitting, infrastructure, lead times]

Only include actions that are real and verifiable. Omit any that don't apply.

## Key Facts

Verifiable facts with scale indicators agents need to qualify or disqualify.

- Capacity / Scale:
- Ownership:
- Economics:
- Seasonality:

<!-- source: [primary source, date] -->

## Data Provenance

Every node must declare its sources explicitly:

- Web-sourced: [what came from research and when]
- Human-verified: [what has been confirmed by a person with direct knowledge]
- Estimated: [what is inferred or calculated, flagged clearly]

## Constraints and Dealbreakers

What an agent should surface when this node doesn't fit a use case:

- [Infrastructure, permitting, HOA, seasonal, cost, or other limiting factors]
- [Lead times or availability windows]
- [Dealbreakers specific to this node]

## Handoff

Where an agent sends a human who wants to act:

- **Primary contact:** [name, org, URL, or phone where available]
- **Booking / Inquiry:** [specific pathway]
- **Economic development:** [CVB or city contact if applicable]

## Connections

Other nodes this connects to and why the connection matters for an agent traversing the valley.

## Intelligence Briefs

Timestamped signals that reference this node. Leave as "None yet" if empty.

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
