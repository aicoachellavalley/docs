# AICV Category Census — Template v1

Reusable harness for an AICV **practitioner-layer agent-visibility census** of a
category across the Coachella Valley. Extracted from the **Home & Real Estate**
run (2026-06-12, `aicv-playbook@f891419`; workflow runs `wf_c03c314f-397`
discovery / `wf_893630f9-12f` enrichment). Same pattern as the dining census.

> ⚠️ The `.js` scripts here carry the **H&RE embedded batch data**. They are the
> structural template, not a turnkey re-run. For a new category, **regenerate**
> the embedded data (see "What gets swapped") — never hand-edit the batch arrays.

## Files

| File | Role |
|---|---|
| `discovery.js` | Discovery workflow — one Sonnet agent per geo×subcategory **cell** enumerates businesses (3–4 web searches each). `BATCH_INDEX` selects an embedded batch. |
| `enrich.js` | Enrichment workflow — one Sonnet agent per **entity** (1 site visit + 1 search), fills the ~20-field schema. `BATCH_INDEX` selects an embedded batch of ~40. |
| `enrich-gen.py` | **Target regenerator.** Reads `enrich_target` rows from the scratch dataset, splits into batches of 40, emits `enrich.js` with embedded `ALL_BATCHES`. Run this; do not hand-edit `enrich.js`. |
| `discovery-merge.py` | Discovery merge/checkpoint: normalize + dedup (name+city), **triage** (phantom detector), `entity_kind` stamp, review-bucket disposition. Idempotent per batch. |
| `enrich-merge.py` | Enrichment merge-back: matches payloads to rows by `_src_name`/`_src_city`, sets `enriched`, writes journal, tracks usage-basis spend + the 14M guard. Idempotent per batch. |

## What generalizes (keep across categories)

- **Density-tiered geo×subcategory discovery grid.** Dense subcategories get
  per-city workers; sparse ones get one valley-wide worker. Always run **one
  pilot batch first**, measure tokens/worker, re-project before the full fan-out.
- **Dedup / triage merge with the phantom detector** (`discovery-merge.py`).
  Dedup key = normalized `name + canonical city`; a brand with offices in N
  cities = **N rows** (one per physical-office city). Triage routes
  serves-from-elsewhere / cloud-only / wrong-city rows to a **review bucket**
  (excluded from enrichment, surfaced at the gate) via: (a) address-hint city ≠
  assigned city, and (b) note red-flag phrases. Over-inclusive by design —
  review beats silently enriching a phantom.
- **`entity_kind` stamp** — orchestrator heuristic, **zero worker cost**:
  `office` (default) | `team_brand` (named team within a brokerage/firm) |
  `solo` (single-practitioner person-brand). Approximate; verify before relying.
- **`_src_` merge convention** — every worker payload is tagged `_src_name` /
  `_src_city` (discovery: `_src_subcat`/`_src_geo`) **before** filtering, so the
  merge keys off identity, never positional alignment. `parallel()` preserves
  input order as the fallback.
- **~20-field, two-block enrichment schema.** *Visibility block* (identical
  across categories): name, city, full_address, website, currently_open,
  has_structured_data, agent_crawlable, agent_visibility_score,
  visibility_gap_note. *Category block* (semantics adapt): subcategory,
  license/credential displayed + type guess, areas served, specialties,
  +category-specific flags, year established, size hint, booking/contact path,
  chain_or_independent.
- **Waves-of-2 + checkpoint-per-batch rhythm.** Snapshot each batch to its own
  `*-bN.js` (sed-bump `BATCH_INDEX`), run two workflows in parallel per wave,
  **merge each to disk as it lands** (merges are idempotent + order-free per
  `batch_index`). A clean partial beats a capped crash.
- **Budget guards.** Depth pin = **1 site visit + 1 web search per entity**, no
  field additions, no extra fetches. Check cumulative **usage-basis** spend
  against the **14M** ceiling at every batch boundary; stop + checkpoint if
  tripped. ~17.5k tokens/entity is the enrichment planning number.
- **Model split.** Orchestrate on Opus; **every** `agent()` pinned
  `model: 'sonnet'`. No Fable.
- **Gated rhythm** (the conversation session holds the gates between runs):
  STAGE 0 recon → STAGE 1 discovery plan **+ pilot** → **GATE 1** → STAGE 2
  discovery batches → STAGE 3 enrichment plan (counts, ambiguities, estimate) →
  **GATE 2** → STAGE 4 enrichment waves → STAGE 5 close + durable save + commit.
- **Standing gate items — every category, not per-run add-ons.** Three checks
  run at the gates regardless of category: (1) **pilot measurement** — one
  pilot batch before any full fan-out, measure tokens/worker, re-project (see
  the discovery-grid bullet); (2) **anchor recall** — pre-register the
  category's marquee anchors and confirm the sweep surfaced them; (3)
  **plausibility flags** — sanity-check counts and rates against prior runs
  before drafting. **Missing-anchor disposition:** a pre-registered anchor the
  sweep did *not* surface gets **one targeted check**, then resolves to exactly
  one of — **"sweep miss"** (re-run the cell) or **"confirmed absent =
  market-structure finding"** (no CV location exists; record it as a finding,
  not a recall defect). Never leave a missing anchor unadjudicated. Precedent:
  F&S confirmed Goddard / La Petite / Sylvan / Huntington absent from the CV
  (national early-childhood/tutoring franchises don't operate here) — a finding
  about the market, not a gap in the sweep.

## What gets swapped per category

- **Subcategory list** — the 8 H&RE subcats → the new category's subcats.
- **Discovery cell grid** — re-tier by *that* category's density (which subcats
  warrant per-city workers vs one valley-wide worker), and the per-cell **query
  arrays**.
- **Entity definition + exclusions** — the drift-killer prose in the discovery
  agent prompt (what counts as a business vs an individual; hard exclusions).
- **Category block fields + agent prompt** in `enrich.js` — the category-specific
  half of the schema and its fill instructions.
- **Embedded `ALL_BATCHES`** — **regenerated**: discovery cells by hand-authoring
  the grid; enrichment targets by running `enrich-gen.py` over the post-discovery
  scratch. Never hand-edit the batch arrays.
- **Geography** is **fixed** — the canonical 12-city CV list (read from a prior
  run's state; do not invent).

## Scratch + durable conventions

- Scratch lives **untracked** in `com/` as `tmp-agent-mapped-<cat>*.json` /
  `tmp-<cat>-*.js|.py` (never committed there).
- Durable save → `aicv-playbook/data/workflow-runs/cv-<category>-<date>/`:
  `*-census-final.json`, state files, `journal/` (per-entity jsonl +
  `_batch`/`_run_id`, raw per-batch results), `scripts/`, and a README with a
  provenance header (method, date, model split, depth pin, locked counts).
  Commit **path-scoped**.

## Saved commands

Mirror copies are registered for slash/`name` invocation at
`~/Workspaces/.claude/workflows/census-discovery.js` and `census-enrich.js`
(project-level, this machine).

## Changelog

**v1.3 — cv-talent-workforce (2026-06-14).** Patterns for a **SPLIT credential category**
(first in the series — a credentialed wing alongside an unregulated one), doc-only; the
reusable script lives in that run's `scripts/reconcile.py`. (1) **Subcat-level
`credential_regime` stamp** in the discovery-merge (zero worker cost) — makes the
credentialed-vs-unregulated divide computable at synthesis instead of reconstructed; stamp it
whenever a category spans both regimes. (2) **Context-segment from a worker `segment` field** —
when carve-outs are known up front, a dedicated context cell tags rows directly (`segment=
public_workforce|econ_dev|…`) rather than deriving them from note red-flags; cleaner than the
H&RE/F&S note-driven triage for known institutional carve-outs. (3) **Registry-only carve-out +
promotion bar + per-row regime override** — a population enumerable only via a state registry
(FLCs, mirrors `family_home_daycare`) is kept as context, but its **web-visible members are
promoted** into an otherwise-unregulated subcat with a **per-row `credential_regime` override**
so the split stays accurate at the row level. (4) **Explicit auditable GATE-2 reconcile** —
when N is small, an explicit (normalized-substring) action list (MERGE variant-clusters / DROP
out-of-scope / RECLASS to context / PROMOTE) beats a general fuzzy auto-merge: every action is
logged and there is no accidental over-merge. See `scripts/reconcile.py`.

**v1.2 — canonization (2026-06-13).** Folded the **standing gate-items**
framing into "What generalizes": pilot-measurement + anchor-recall +
plausibility-flags are gate checks for *every* category (not per-run add-ons),
and the **missing-anchor disposition** (one targeted check → "sweep miss" vs
"confirmed absent = market-structure finding") is now an explicit rule.
Doc-only; no script change. The NAME-only public-detector and dropped-bare-
`verify` refinements (PAYLOAD items folded earlier) remain in v1.1 below.

**v1.1 — cv-family-schooling (2026-06-12).** Triage refinements folded into
`discovery-merge.py`: (1) hard-exclusion detectors (public districts/charters, etc.)
match the row **NAME only**, never the note — a note that mentions a public partner
is not a disqualifier; (2) dropped the bare `verify` flag from `FLAG_SUBSTR` — workers
append "verify" too liberally, so it over-routed in-scope rows to review. New reusable
patterns demonstrated in that run's `scripts/` (crib as needed): a **definitional
context-segment carve-out** (family-home daycares → `segment` context, not enrich-
targets — mirrors `remote_operator`; membership not conditioned on the measured
variable), a **post-discovery cross-subcat dedup pass** (`discovery-dedup.py`: safe
same-city+same-subcat auto-merge, cross-subcat & cross-city clusters surfaced for the
gate), and a **gate-decision reconcile step** (`gate2-reconcile.py`: collapse a campus's
sub-programs to one row with a `programs_note`, drop city-phantoms, promote/flag rows).
