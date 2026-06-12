# CV Home & Real Estate — Agent-Visibility Census + Dataset (2026-06-12)

Census + visibility dataset for the Coachella Valley **home & real estate**
practitioner layer. This run produced a **dataset only**. It did **not** write
report MDX, nodes, seeds, cross-links, or touch `/reports/`, and it did not
start any other category. Synthesis/report is a separate later session.

## Provenance

| | |
|---|---|
| **Method** | 2-stage agent fan-out: discovery (geo×subcategory cells enumerate businesses) → enrichment (one agent per entity, ~20-field schema). Dynamic workflows; conversation session held the gates between runs. |
| **Date** | 2026-06-12 |
| **Model split** | Orchestrated on **Opus 4.8**; **every** worker pinned to **Sonnet 4.6** (`model: 'sonnet'` per `agent()` call). No Fable. |
| **Depth pin** | **1 website visit + 1 web search per entity.** Unknowns marked freely. Dead/blocked site = failure state recorded, no retries. No state-license-DB queries (DRE/NMLS verification is a separate deterministic pass). |
| **Entity definition** | A BUSINESS: a brokerage office, a named team with its own brand/web presence, or a solo practitioner operating as a business brand — **not** individual licensees inside a brokerage. One row per business per **city of physical office** (a brand with offices in N cities = N rows). |
| **Geography** | Same 12-city list as the dining census: Palm Springs, Palm Desert, La Quinta, Rancho Mirage, Cathedral City, Indio, Coachella, Desert Hot Springs, Indian Wells, Thousand Palms, Bermuda Dunes, Thermal. |

## Subcategories (all practitioner-side)

residential brokerages & teams · property management (long-term residential) ·
property management (vacation rental / STR) · title & escrow · mortgage lenders
& brokers (local offices/branches) · home inspectors · appraisers · HOA /
community association management.

## 🔒 LOCKED COUNTS

```
323 census rows
  = 317 enrich-target entities (office-confirmed; ALL enriched, 100%)
  +   6 remote_operator context rows (STR operators serving CV with no local
        office — Vacasa, AvantStay, Air Concierge, GnG Vacation, My Canadian
        Concierge, California Vacation Villas; market context, NOT prospects,
        excluded from enrichment by design)
10 rows dropped at triage (8 phantom Cathedral City brokerage entries already
   counted at their real office city; 2 city-duplicates already present in Palm
   Springs). 25 cross-cell duplicates removed during discovery merge.
Inspection coverage: 317 / 317 office-confirmed entities = 100%.
```

`entity_kind` (orchestrator heuristic, zero worker cost): **office 282 ·
team_brand 24 · solo 11**. (team_brand = named team operating within a
brokerage; solo = single-practitioner person-brand. Heuristic — refine in a
later verification pass.)

## Entity count by subcategory

| Subcategory | Entities |
|---|---:|
| residential brokerages & teams | 107 |
| title & escrow companies | 40 |
| property management — vacation rental / STR | 39 |
| home inspectors | 35 |
| mortgage lenders & brokers | 31 |
| appraisers | 29 |
| property management — long-term residential | 19 |
| HOA / community association management | 17 |
| **Total** | **317** |

> Home inspectors (15→35) and appraisers (15→29) were lifted by an approved
> supplemental sweep (2 regional cells each) after the single-cell first pass
> flagged thin coverage of these fragmented trades.

## Entity count by city (office city)

Palm Desert 86 · Palm Springs 83 · La Quinta 48 · Indio 27 · Rancho Mirage 23 ·
Indian Wells 19 · Desert Hot Springs 14 · Cathedral City 6 · Coachella 5 ·
Bermuda Dunes 4 · Thermal 1 · Thousand Palms 1. *(enrich-target rows, n=317;
recompute fresh from disk for any published figure.)*

## Headline visibility stats (n = 317)

| Dimension | Result |
|---|---|
| `agent_visibility_score` | high **168** · medium **113** · low **31** · invisible **5** |
| low + invisible (the "gap") | **36 / 317 = 11.4%** |
| Crawler-blocked (403 / challenge to bots) | **66 / 293 checkable = 22.5%** |
| Structured data present (JSON-LD / schema.org) | **3 / 226 checkable = 1.3%** |
| Non-empty visibility-gap notes | **201 / 317** |
| `currently_open` | open 87 · closed 5 · unknown 225 |
| `vacation_rental_flag` = true | 59 |

> The structural finding mirrors dining: **near-zero structured data (1.3%)** and
> heavy crawler-blocking (22.5%). The agent-visibility **gap is worse than dining**
> (11.4% low+invisible vs dining's 5.0%) — the CV real-estate practitioner layer
> is materially less legible to agents than its restaurants.

## License-display capture (the verification-leg teaser)

| | |
|---|---|
| `license_id_displayed` captured (DRE#/NMLS# the site itself shows) | **117 / 317 = 36.9%** |
| `license_type_guess` | DRE 79 · NMLS 20 · other 22 · none-visible 196 |

> CA law requires a DRE# on real-estate marketing, yet only **36.9%** display a
> license number on their own site. Captured values are **as-displayed only** —
> a deterministic DRE/NMLS verification pass is a separate future leg.

## Token spend

| Stage | Subagent tokens (usage basis) |
|---|---:|
| Discovery (4 batches: pilot + 2 + supplemental) | **1,174,060** |
| Enrichment (8 batches × ~40) | **5,572,549** |
| **Session total** | **6,746,609** (**48.2%** of the 14M guard) |
| Per entity (enrichment) | **17,579** (on the 17.5k pin) |
| Per entity (all-in disc+enrich) | 21,283 |

Guard never tripped; no priority-split needed. Zero merge failures, zero
unmatched rows across all 12 batches.

## Files

- `cv-hre-census-final.json` — full 323-row dataset; 317 carry the ~20
  enrichment fields + `enriched: true`; 6 carry `segment: remote_operator`.
  Each row also has `entity_kind`, `enrich_target`, and discovery provenance
  (`_disc_batch`, `_src_subcat`, `_src_geo`).
- `discovery-state-final.json` — discovery state: counts by subcategory/city,
  `entity_kind_counts`, `dropped_rows` (the 10, with reasons), `remote_operators`.
- `enrich-state-final.json` — enrichment state: batches done, usage by batch,
  cumulative usage-basis spend.
- `journal/inspection-journal.jsonl` — 317 enrichment records, one line per
  entity, tagged `_batch` + `_run_id`.
- `journal/{discovery,enrich}-NN-<wf-id>.json` — raw per-batch workflow results.
- `scripts/` — the discovery, supplemental, and enrichment workflow scripts plus
  the merge/generator scripts, for reproducibility.

## Provenance — workflow run IDs

**Discovery:** `wf_c03c314f-397` (pilot/b0), `wf_ed92ea7e-76b` (b1),
`wf_b9cef508-220` (b2), `wf_26c3f392-0a8` (supplemental inspectors+appraisers).

**Enrichment:** `wf_893630f9-12f`, `wf_a6e7bb04-293`, `wf_071d2363-f20`,
`wf_f897f1c4-899`, `wf_43522f4d-24f`, `wf_bc6c2287-441`, `wf_67a238bf-05c`,
`wf_3dc82300-eaf` (batches 0–7).

Source scratch (untracked in `com/`, never committed there per `tmp-`
discipline): `tmp-agent-mapped-hre.json`, `tmp-agent-mapped-hre-state.json`,
`tmp-agent-mapped-hre-enrich-state.json`.

## Open items for the synthesis/report session (NOT done here)

- Recompute all denominators fresh from disk with definitions stated.
- Decide whether the 6 `remote_operator` rows appear as market context in the
  report (they are not prospects).
- Deterministic DRE/NMLS verification leg against the 117 displayed license IDs.
- `entity_kind` is heuristic — verify before relying on office/team/solo splits.
- Country clubs / gated communities encountered in discovery were **not**
  censused (concept-node material) — names live in candidate notes if needed.
