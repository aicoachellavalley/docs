# Tomorrow — 2026-05-11

## Priority queue

### 1. Landing page rewrite — May 11 vocabulary

`/get-agent-ready/` was written before vocabulary was locked.
Rewrite to reflect current model:
- Customer-facing: "agent on the network" (not "node")
- LLM Council (not Intelligence Council)
- Agentic Review (not Snapshot, not Intelligence Review)
- Two-product framing: Agent on the AICV Network (base) /
  Agent Premium (LLM Council review + Agentic Review artifact)
- SF/LA newly-vested founder cohort named explicitly as the
  target audience

### 2. Rancho Mirage city-agent prototype spec

First city-scoped agent runtime. Write the spec before building:
- Entity scope: which Rancho Mirage nodes get per-entity records
- Runtime architecture: how the city-agent writes to entity records
- Output format: what an entity record looks like post-run
- Integration: how the prototype feeds the LLM Council intake flow

### 3. Founding Member outreach — HELD

Sensei Porcupine Creek, Visit Greater Palm Springs, and The
Gardens on El Paseo have public Agentic Reviews and existing
nodes. These are the natural first Founding Member targets.

**Held until the Rancho Mirage prototype produces at least one
entity record.** Need evidence before outreach.

## Cleanup queue (small, non-blocking)

- **Brief count reconciliation:** 143 files on disk; `stats.json`
  reports 142; Index node says 131. ~15 min to identify and
  resolve.
- **`tokens.css` fork:** `com` and `guide-builder` have diverged.
  Variable names (`--sand`, etc.) inconsistent. Low priority.
- **`snapshots.json` grades artifact:** All three entries have
  `grades: {}` (empty object). Cosmetic; not user-facing.
- **Comprehensive snapshot→agentic-review rename:** IC.md
  template, `aicv-ic/worker.js` CHAIR_SYSTEM prompt, and
  remaining playbook docs still use "Snapshot" terminology.
  Do not rename piecemeal — defer until full IC.md update pass.

## Parked

- IC.md: Intelligence Council → LLM Council rename. Deferred
  until IC.md update session.
- Search Console health review (Q2 baseline) — see STATE.md
  entry dated 2026-04-29.
- User journey + waypoint naming — see STATE.md. Deferred until
  landing page ships.
- `aicv-mcp` `query_venues` city enum (missing
  `desert-hot-springs`, `cathedral-city`).
