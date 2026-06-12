# CV Food & Dining — Agent-Visibility Enrichment Run (2026-06-11)

Visibility-inspection leg of the Agent-Mapped dining workflow. This run completed
the **enrichment backlog** left open after the 2026-06-09 census
(`../cv-food-dining-2026-06-09/`). It did **not** publish report V2, touch
`/reports/`, author nodes, or modify seeds/pages/cross-links.

## What ran

- **481 independents** inspected (the full `to_enrich` backlog), one Sonnet 4.6
  agent per entity, light depth: one website visit + one web search.
- Orchestrated on Opus 4.8; all inspection workers pinned to Sonnet 4.6
  (`model: 'sonnet'` per agent). No Fable.
- 13 batches of 40 (last batch = 1), checkpointed to the canonical scratch
  dataset after every batch. Zero merge failures, zero unmatched rows.
- Per-entity field set replicated exactly from the prior 377-entity pass — same
  20-field `ENRICH_SCHEMA`, no schema drift.

## Field set (per entity)

`meal_periods, reservations, booking_platform, outdoor_seating,
kid_family_friendly, group_private_dining, group_capacity, bar_cocktails,
happy_hour, dietary_vegan, dietary_vegetarian, dietary_gluten_free,
dog_friendly_patio, live_music, seasonal_operation, reopen_date,
has_structured_data, agent_crawlable, agent_visibility_score,
visibility_gap_note`

## Token spend

| Metric | Value |
|---|---|
| Subagent tokens (13 batches) | **8,385,144** |
| Agents | 481 |
| Avg / agent | 17,432 |

Run proceeded ~0.39M past the 8M soft ceiling to finish the census completely
(final batch crossed 8M; completion authorized over partial-stop for census
integrity, overage bounded and non-spilling).

## Outcome — inspection coverage

| Universe | Count |
|---|---|
| Independents enriched (this run + prior 377) | **858 / 858** (100%) |
| `to_enrich` remaining | 0 |

## Headline visibility stats (recomputed at n = 858)

| Dimension | Result |
|---|---|
| `agent_visibility_score` | high 552 · medium 263 · low 40 · invisible 3 |
| low + invisible (the "gap") | 43 / 858 = **5.0%** |
| Crawler-blocked (403/challenge) | 200 / 706 checkable = **28.3%** |
| Structured data present (JSON-LD/schema.org) | **0 / 554** checkable |
| Non-empty visibility-gap notes | 348 |

> Compare against the published V1 figures (44% sample): 0/232 structured data,
> 92/298 = 31% crawler-blocked, 176 gap notes. The full-sample numbers are
> directionally consistent — **still zero structured data**, crawler-blocking
> ~28% (vs 31%), gap notes scale to 348. **Report-only — the live V1 report was
> not edited; superseding these into V2 is a separate session.**

## ⚠ DENOMINATOR RECONCILIATION REQUIRED FOR V2

Disk now shows independent counts that do not line up with the figures used in
V1. V2 must derive **all** denominators fresh from disk with definitions stated:

| Quantity | Disk value |
|---|---|
| Independents (total, `chain_or_independent == independent`) | **971** |
| Seed-mapped (`in_dining_map == true`) | 66 |
| Enriched (`enriched == true`) | 858 |
| Neither mapped nor enriched | **47** |
| Strict non-mapped independents (971 − 66) | **905** |

- V1 milestone recorded 924 independents; the published sample used **858** as
  the non-mapped denominator (377/858 = 44%).
- This run enriched 858/858 of that defined universe = 100%, but against the
  strict non-mapped count (905) it is **94.8%**.
- The 47 uncovered independents are mostly food trucks / catering / late finds
  that never entered the `to_enrich` backlog — several are arguably
  mobile-segment, not fixed independents. V2 must decide their classification
  before fixing the denominator. List preserved in `state-final.json`
  (independents with `enriched != true` and `in_dining_map != true`).

## Files

- `dining-enriched-final.json` — full 1,423-row dataset; 858 independents carry
  the 20 enrichment fields + `enriched: true`.
- `state-final.json` — canonical state: `enriched_new` (858), `to_enrich` (0),
  `mapped` (66), `chains`, `mobile`, `unclass`.
- `journal/inspection-journal.jsonl` — 481 inspection records (this run only),
  one line per entity, tagged with `_batch` and `_run_id`.
- `journal/batch-NN-<wf-id>.json` — raw per-batch workflow results.

## Provenance

Workflow run IDs (one per batch): `wf_08eb739a-c6f`, `wf_16d05ca6-e7d`,
`wf_26951c55-594`, `wf_0166ac6a-a31`, `wf_53bf84ed-93b`, `wf_2dd30df1-4c7`,
`wf_a4389e3f-f12`, `wf_c9ca50d5-002`, `wf_a53130e4-ed7`, `wf_2104811c-283`,
`wf_58825376-42c`, `wf_21df0260-8c9`, `wf_1dce53e0-e6e`.

Source scratch files (untracked in `com/`, never committed there per `tmp-`
discipline): `tmp-agent-mapped-dining.json`, `tmp-agent-mapped-state.json`.
