# CV Talent & Workforce — Agent-Visibility Census + Dataset (2026-06-14)

Census + visibility dataset for the Coachella Valley **talent & workforce services**
practitioner layer — the businesses that connect people to work, train adults for work,
or house/service the workforce. This run produced a **dataset only**. It did **not** write
report MDX, nodes, seeds, cross-links, or touch `/reports/`, and it did not start any other
category. Synthesis/report, the credential-verification leg, and prospect work are separate
later sessions. Fourth category census, after dining, H&RE, and family & schooling.

## Provenance

| | |
|---|---|
| **Method** | 2-stage agent fan-out: discovery (geo×subcategory cells enumerate orgs) → dedup/triage → GATE-2 reconcile → enrichment (one agent per entity, ~20-field schema). Dynamic workflows; the conversation session held the gates between runs. |
| **Date** | 2026-06-14 |
| **Model split** | Orchestrated on **Opus 4.8**; **every** worker pinned to **Sonnet 4.6** (`model: 'sonnet'` per `agent()` call). No Fable (disabled 2026-06-12, export-control). |
| **Depth pin** | **1 website visit + 1 web search per entity.** Unknowns marked freely. Dead/blocked site = failure state recorded (`agent_crawlable=false` / `currently_open` per observation), no retries. **No state-DB queries** (DIR FLC registry / BPPE / state boards) — credential capture is **as-displayed only**; verification is a separate deterministic pass. |
| **Entity definition** | A **private organization (for-profit OR service-delivery nonprofit) with a physical CV location** whose business is connecting people to work, training adults for work, or housing/servicing the workforce. One row per physical location per city. |
| **Geography** | Same 12-city list as dining/H&RE/F&S (read from prior runs, not invented): Palm Springs, Palm Desert, La Quinta, Rancho Mirage, Cathedral City, Indio, Coachella, Desert Hot Springs, Indian Wells, Thousand Palms, Bermuda Dunes, Thermal. |
| **Budget guard** | Session HARD guard **12M** cumulative usage-basis (overrides the template's 14M). Used **1,982,158 = 16.5%.** Never tripped. |

## Subcategories (6 enrich + 3 carve-out context segments)

**Enrich-targets:** staffing & recruiting agencies · adult vocational & trade schools / training
providers · workforce-development & job-readiness service organizations · coworking & flexible
workspace · career & professional services · HR outsourcing, PEO & payroll services.

**Carve-out context segments (Gate-1 rulings; membership NOT conditioned on web visibility, per
OPERATING-RULES §5.1):**
- `public_workforce` — Riverside County WDB / America's Job Center (Indio AJCC), EDD, College of the
  Desert / CSUSB-PD / UCR-PD workforce & continuing-ed arms, public adult-school CTE.
- `econ_dev` — CVEP (board-dissolved 2024; iHub → CSUSB-run ERC), OneFuture CV, CVWBC, SBDC, chambers.
- `farm_labor_contractor` — the family-home-daycare analog: the CA DIR-licensed FLC population is a
  state-registry population (enumerable from the registry, not a web sweep) — count is a finding, not
  a web-swept census. Web-visible FLCs operating as staffing businesses **were** promoted to enrich-targets.

**Excluded entirely (no rows):** entertainment/modeling "talent" agencies (different sense of "talent";
separately licensed under the Talent Agencies Act; a future media-entertainment category). 0 enumerated.

## 🔒 LOCKED COUNTS

```
115 dataset rows
  = 83 enrich-target entities (ALL enriched, 100%)
  + 14 review rows (no-confirmed-local-office / city-mismatch / ambiguous — surfaced for a
       supplemental/verification leg, NOT enriched, by design)
  + 18 context rows (public_workforce 11 + econ_dev 6 + farm_labor_contractor 1 — defined OUT of
       the business census by GATE-1 disposition, retained as tagged context)
0 entertainment/modeling "talent" agencies enumerated (the exclusion held).
Discovery dedup: 52 cross-cell duplicates dropped during merge (pilot 24 + b1 28).
GATE-2 reconcile: 12 same-city name-variant clusters merged to one row each; 7 drops (CVEP/ERC
   infrastructure rows already represented in context, + 1 out-of-scope HCO row kept as review);
   3 reclassified to econ_dev context (OneFuture, CVWBC, SBDC — business-dev/funder, not workforce
   businesses); 1 promotion (Zepeda Labor Contracting → enrich-target per the FLC bar); 3 FLC
   per-row credential_regime overrides (Zepeda, Agro Labor, Gutierrez Farm Labor).
Enrichment: 83/83 enriched, 0 unmatched across all 3 batches.
```

`entity_kind` (orchestrator heuristic, zero worker cost): **office 45 · branch 28 · solo 10.**
(branch = national/regional franchise local office — Labor Finders/Manpower/Robert Half/Regus/etc.;
solo = single-practitioner person-brand. Heuristic — verify before relying.)

## Entity count by subcategory (enrich-targets, n=83)

| Subcategory | Entities |
|---|---:|
| staffing & recruiting agencies | 29 |
| adult vocational & trade schools / training providers | 17 |
| coworking & flexible workspace | 14 |
| HR outsourcing, PEO & payroll services | 10 |
| workforce-development & job-readiness service organizations | 8 |
| career & professional services | 5 |
| **Total** | **83** |

> **Staffing is the largest subcategory** — the B2B core. **Career & professional services is the
> thinnest (5)**: a **market-structure finding**, not a recall defect — adjudicated with a dedicated
> deep second-sweep cell (pilot returned 2 → resweep added 3); the field is dominated by solo/remote
> practitioners excluded by the entity definition.

## Entity count by city (enrich-targets, n=83)

Palm Desert 28 · Palm Springs 23 · Indio 8 · Coachella 7 · La Quinta 5 · Rancho Mirage 5 · Cathedral
City 3 · Indian Wells 2 · Thermal 1 · Desert Hot Springs 1. *(Bermuda Dunes & Thousand Palms: 0
enrich-targets — no qualifying workforce business surfaced.)* *(recompute fresh from disk for any
published figure.)*

## Anchor recall

**4/4 grid validators hit** — Labor Finders (Palm Desert), AtWork Personnel (La Quinta), Regus (Palm
Springs), Fusion Workplaces (Palm Desert). **Express Employment Professionals**: a CV franchise expansion
was **announced late 2025 but no open CV office was confirmed** at enrichment — recorded as a review row
(timing finding, not a recall miss). National staffing chains confirmed present: Labor Finders, Manpower,
PeopleReady, Robert Half, Spherion, AtWork, Hospitality Staffing Solutions, Maxim Healthcare, Decton.

## Headline visibility stats (n = 83)

| Dimension | Result |
|---|---|
| `agent_visibility_score` | medium **40** · high **31** · low **12** · invisible **0** |
| low + invisible (the "gap") | **12 / 83 = 14.5%** |
| Crawler-blocked (403 / challenge to bots) | **8 / 78 checkable = 10.3%** |
| Structured data present (JSON-LD / schema.org) | **2 / 63 checkable = 3.2%** |
| `currently_open` | open 35 · unknown 42 · **closed 6** |
| `pricing_displayed` = yes | **16 / 73 checkable = 21.9% (78.1% do not display pricing)** |
| clientele | n/a 31 (coworking/schools) · both 24 · employers 18 · jobseekers 9 · unknown 1 |
| nonprofit / for-profit | nonprofit 8 · for-profit 69 · unknown 6 |
| chain / independent | independent 54 · chain 28 · unknown 1 |

> Structurally consistent with the series: **near-zero structured data (3.2%**, on par with F&S 3.1% /
> dining 0%) and **78.1% hide pricing** (close to F&S's 83%). The agent-visibility **gap (14.5%)** is the
> **highest in the series so far** (dining 5.0% · H&RE 11.4% · F&S 12.5%) — the CV talent/workforce layer
> is the most agent-illegible category mapped to date. Crawler-blocking (10.3%) is **lower** than dining
> (28.4%) / F&S (19.9%) — B2B service sites sit behind bot challenges less often than consumer storefronts.

## The series-first SPLIT credential category (the synthesis hook)

The agent-mapped series has traced a credential typology: **inspection regime (dining) → license-display
regime (H&RE) → no regime at all (F&S)**. Talent & Workforce is the **first SPLIT category** — a
credentialed wing alongside an unregulated one, computable at the row level via `credential_regime`:

| Wing | n | share |
|---|---:|---:|
| **unregulated** (staffing, coworking, career svcs, HR/PEO, workforce-dev) | 63 | **75.9%** |
| **credentialed** (trade schools = BPPE/state-board; FLCs = DIR LC §1684) | 20 | **24.1%** |

- **Credential displayed among the credentialed wing: 11 / 20 = 55.0%** (`credential_type_guess`: BPPE 7
  + state-board 4) — notably higher display than F&S's 20–39%. The 3 promoted FLCs displayed **no** license
  number on their sites (the DIR FLC# is registry-bound, not web-posted).
- `credential_type_guess` overall: none-visible **52** · industry-cert **20** (voluntary awards/memberships
  in the *unregulated* wing — Best-of-Staffing, PIHRA, chamber) · BPPE **7** · state-board **4**.
- **Recon-sourced provenance claim the synthesis leans on:** California has **no state license for staffing /
  employment agencies** — only a $25k surety bond filed with the Secretary of State (Harbor Compliance,
  2026-06-14). The category's heaviest subcat (staffing) is therefore structurally unregulated, while the
  credentialed wing (FLCs) is structurally web-invisible.

## Token spend (usage basis)

| Stage | Subagent tokens |
|---|---:|
| Discovery (pilot + b1) | **449,638** (343,265 + 106,373) |
| Enrichment (3 batches: 40·40·3) | **1,532,520** (735,431 + 742,878 + 54,211) |
| **Session total** | **1,982,158** (**16.5%** of the 12M guard) |
| Per entity (enrichment) | **18,464** (on the 17.5k pin) |
| Per entity (all-in disc+enrich) | 23,882 |

Guard never tripped; no priority-split needed. Zero merge failures, zero unmatched rows across all 5 batches.
*(Discovery `tokens_by_batch` in `discovery-state-final.json` records output-basis `budget.spent()`; the
usage-basis figures above — the guard-relevant ones — come from the workflow task notifications, stored in
`usage_basis_by_batch`.)*

## Files

- `cv-talent-workforce-census-final.json` — full 115-row dataset; 83 carry the ~20 enrichment fields +
  `enriched: true`; 14 carry no segment + `enrich_target: false` (review); 18 carry a `segment`. Each row also
  has `entity_kind`, `credential_regime`, discovery provenance (`_disc_batch`, `_src_subcat`, `_src_geo`), and
  where applicable `_credential_subtype` (FLC), `_flag_reason`.
- `discovery-state-final.json` / `enrich-state-final.json` — discovery & enrichment state (counts, dedup logs,
  usage-by-batch, cumulative spend, guard, review_rows).
- `journal/inspection-journal.jsonl` — 83 enrichment records, one per entity, tagged `_batch` + `_run_id` + `_src_name`.
- `journal/{discovery,enrich}-NN-<wf-id>.json` — raw per-batch workflow results.
- `scripts/` — discovery, the merge / reconcile / enrich-gen / enrich / enrich-merge scripts, for reproducibility.
- `stats/` — `stats.py` + `stats.json` (all denominators recomputed fresh from disk per OPERATING-RULES §5.2).

## Provenance — workflow run IDs

**Discovery:** `wf_bebfa2c7-b8b` (pilot/b0; b1 resumed same run). **Enrichment:** `wf_d672cb8e-d09` (b0),
`wf_7a28f69c-567` (b1), `wf_e76db42b-473` (b2).

Source scratch (untracked in `com/` per `tmp-` discipline, never committed there):
`tmp-agent-mapped-tw.json`, `tmp-agent-mapped-tw-state.json`, `tmp-agent-mapped-tw-enrich-state.json`,
`tmp-agent-mapped-tw.prereconcile.json`, `tmp-tw-*.js|.py|.json|.jsonl`.

## Open items for the synthesis/report session (NOT done here)

- Recompute all denominators fresh from disk with definitions stated; run the **cross-report consistency
  gate** (OPERATING-RULES §5.3) — deconflict the gap/SD/pricing figures and any "first/only" claims against
  the four live reports before drafting.
- **Credential-verification leg** (separate deterministic pass): the 20 credentialed-wing entities — match
  displayed BPPE approvals / state-board licenses; enumerate the FLC registry population (DIR) for the
  `farm_labor_contractor` context count (market context, not prospects).
- The 14 `review` rows: decide which (if any) are real for a supplemental enrichment vs confirmed phantoms
  (incl. the two ClearPoint rows — one plausibly an in-scope Human-Capital/HR firm with no confirmed CV office;
  Express Employment — confirm whether the announced CV branch has opened).
- Caregiver/nurse-registry staffing (Coachella Valley Health Personnel, Hope Care, CLS Caregivers) sit at the
  staffing↔home-care boundary; CA Home Care Organization (HCO) licensure would make them credentialed under a
  *healthcare* regime — reconcile category placement against the future wellness/healthcare census.
- `entity_kind` is heuristic — verify before relying on office/branch/solo splits.
- Public/nonprofit institutions (AJCC, COD/CSUSB/UCR, CVEP-dissolved/ERC, OneFuture, chambers) were **not**
  censused as businesses (concept-node material for the report); they are the 18 tagged context rows.

## Template improvements folded back into `templates/census/` (this run)

1. **Subcat-level `credential_regime` stamp** (zero worker cost) — makes a SPLIT category's credentialed-vs-
   unregulated divide computable at synthesis rather than reconstructed. First needed when a category spans
   both regimes.
2. **Context-segment from a worker `segment` field** — a dedicated context cell tags carve-out rows directly
   (vs deriving them from notes), cleaner than the H&RE/F&S note-driven approach when carve-outs are known up front.
3. **Per-row credential_regime override + promotion bar** — a registry-only carve-out population (FLCs) whose
   web-visible members are promoted into an otherwise-unregulated subcat, with a per-row regime override so the
   split stays accurate. Reusable pattern in `scripts/reconcile.py`.
