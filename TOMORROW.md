# Tomorrow — 2026-04-23 (Thursday)

## Primary work

### 1. SunshineFM Guide — DCF entry (editorial, you + Claude)

Core block. Desert Community Foundation will be the first Guide entry at sunshine.fm/guide/desert-community-foundation/. This establishes SunshineFM Guide voice on a real entity and validates the template/schema shape before scaling.

Subtasks:
- **Template redesign** (~30 min). The current authoring template feels like a form, not a working document. Needs structure, inline guidance, natural section ordering.
- **Decide DCF schema.org type** (~5 min). `civic-institution` currently defaults to Organization. NGO or Foundation may be more accurate.
- **Author DCF entry** (~75-90 min). First Guide entry. Sets editorial voice precedent. Output: deployed entry at sunshine.fm/guide/desert-community-foundation/.

### 2. AICV Layer 2 design session (strategy, you + Claude)

If time and energy permit after DCF. Design the "collective signal" build:
- What relationship types matter for AICV specifically? (Start from the four-layer framework and adapt.)
- What does a node page need to surface that it doesn't today? (Referenced-by briefs, adjacent entities, etc.)
- What aggregations should be queryable? ("Show me all hospitality nodes in Palm Desert with briefs in last 90 days")
- What's the minimum viable first build — which relationship type first, which aggregation first?

This is design thinking work, not implementation. Goal: a written sketch of what Layer 2 looks like before any code is written.

## Secondary work — technical housekeeping if time permits

### 3. ~/sunshine-fm/CLAUDE.md creation

The separate prompt in today's handoff doc. Captures SunshineFM operating context: three-part structure, deploy flow, newsroom cards-are-not-fallback warning, voice, related projects. Run as standalone Claude Code session. ~15 min.

### 4. Newsroom cards warning comment in sunshine-fm/index.html

Prevents a future regression where the curated cards in the .catch() block get mistaken for throwaway fallback content. ~5 min.

### 5. Mobile nav for sunshine.fm root homepage

Parked from earlier. Guide has mobile nav; root doesn't. ~30-60 min.

## Parked — don't touch unless you genuinely want to

- Automated ZONE_MAP/SUB_MAP sync on .org graph (waits for Layer 2 session to decide if this lives in nodes.json or a separate sync mechanism)
- CV Intel resumption (parked 2026-04-20, see ~/cv-intel/README.md)
- Sensei Porcupine Creek IC run
- Hotel Paseo node

## Known not-blocking but worth eyeballing

- Re-run AIO Tool on aicoachellavalley.org after yesterday's content truth commits. Grade should move from B to A (HIGH fix around program status was addressed).
- Re-run Cloudflare Agentic Readability scan on aicoachellavalley.com. Multiple dimensions should now score that were zero before: Content (Markdown for Agents), Link headers, Content Signals, API catalog, MCP Server Card.
- Paste the live api-catalog and server-card.json URLs into the browser and capture screenshots — they're pitch assets now.

## Session discipline reminders

- Verification-before-inference on any production fetch, constant, config, or URL before editing
- Recon before action — read current state first
- Claude.ai for strategy/drafting, Claude Code for file operations; Sat is the courier
