# CV Family & Schooling — Agent-Visibility Census + Dataset (2026-06-12)

Census + visibility dataset for the Coachella Valley **family education, childcare
& youth-development** practitioner layer. This run produced a **dataset only**. It
did **not** write report MDX, nodes, seeds, cross-links, or touch `/reports/`, and
it did not start any other category. Synthesis/report, the credential-verification
leg, and prospect work are separate later sessions.

## Provenance

| | |
|---|---|
| **Method** | 2-stage agent fan-out: discovery (geo×subcategory cells enumerate orgs) → dedup/triage → GATE-2 reconcile → enrichment (one agent per entity, ~20-field schema). Dynamic workflows; the conversation session held the gates between runs. |
| **Date** | 2026-06-12 |
| **Model split** | Orchestrated on **Opus 4.8**; **every** worker pinned to **Sonnet 4.6** (`model: 'sonnet'` per `agent()` call). No Fable. |
| **Depth pin** | **1 website visit + 1 web search per entity.** Unknowns marked freely. Dead/blocked site = failure state recorded (`agent_crawlable=false` / `currently_open` per observation), no retries. **No state-DB queries** (CDSS / Community Care Licensing / WASC / NAIS / AMS) — credential capture is **as-displayed only**; verification is a separate deterministic pass. |
| **Entity definition** | A **private organization with a physical CV location** delivering education, childcare, or youth development as its business. One row per **campus/location per city** (3 campuses = 3 rows). A named program operating its own brand inside a larger facility counts if it has its own web presence (`entity_kind=program_brand`). |
| **Geography** | Same 12-city list as dining/H&RE (read from the H&RE run, not invented): Palm Springs, Palm Desert, La Quinta, Rancho Mirage, Cathedral City, Indio, Coachella, Desert Hot Springs, Indian Wells, Thousand Palms, Bermuda Dunes, Thermal. |
| **Budget guard** | Session HARD guard **12M** cumulative usage-basis (overrides the template's 14M). Never tripped. |

## Subcategories (8)

private K-12 schools · preschools & early-childhood programs · licensed childcare &
daycare centers · tutoring/test-prep & academic enrichment · youth sports academies
& programs · arts/music & performing-arts education for youth · special-needs &
developmental services for children · camps & after-school programs.

## 🔒 LOCKED COUNTS

```
278 dataset rows
  = 216 enrich-target entities (campus-confirmed; ALL enriched, 100%)
  +  16 review rows (phantom / no-confirmed-campus / in-home-or-online / ambiguous —
        surfaced for the verification leg, NOT enriched, by design)
  +  46 family_home_daycare context rows (licensed family child-care HOMES — defined
        OUT of the business census by GATE-1 disposition A: residential operations
        enumerable only via the CDSS state registry, not a web sweep; membership is
        NOT conditioned on web presence. Mirrors the H&RE remote_operator pattern.)
0 public-noted/dropped (the discovery prompt's exclusions held — no district/charter
   school was ever enumerated as a row).
Discovery dedup: 33 cross-cell duplicates removed during merge (pilot 3 + b1 8 + b2 22).
Post-discovery dedup pass: 6 same-city+same-subcat variant auto-merges.
GATE-2 reconcile: 9 cross-subcat clusters collapsed to one row/campus (school + its
   own camp/preschool = facets, with a programs_note recording the absorbed programs);
   3 phantoms dropped (Xavier [Thousand Palms] city-dup; 2 Variety name-variants);
   1 promotion (Young Life Desert Cities → Cathedral City target); 2 flagged
   _verify_note for enrichment-time resolution (Dove's Landing TP; Montessori PS&PD variant).
Enrichment: 216/216 enriched, 0 unmatched across all 6 batches.
```

`entity_kind` (orchestrator heuristic, zero worker cost): **campus 168 · program_brand
32 · solo 16**. (program_brand = a named program operating inside a larger venue/
facility — resort tennis/golf academies, attraction-run camps; solo = single-
practitioner person-brand. Heuristic — refine in a later verification pass.)
**34** rows carry a `name_enriched` (Disposition D: the enrichment worker set the
program's own canonical name where discovery had named the host venue).

## Entity count by subcategory (enrich-targets, n=216)

| Subcategory | Entities |
|---|---:|
| youth sports academies & programs | 54 |
| arts, music & performing-arts education for youth | 42 |
| preschools & early-childhood programs | 30 |
| special-needs & developmental services for children | 28 |
| camps & after-school programs | 19 |
| licensed childcare & daycare centers (center-based) | 18 |
| private K-12 schools | 17 |
| tutoring, test-prep & academic enrichment | 8 |
| **Total** | **216** |

> **Youth sports is the largest subcategory** — the CV tennis/golf/swim/soccer
> signature the brief anticipated. Tutoring is the thinnest: a **market-structure
> finding**, not a recall defect (see below).

## Entity count by city (enrich-targets, n=216)

Palm Desert 71 · Palm Springs 29 · Indio 29 · La Quinta 25 · Coachella 17 · Rancho
Mirage 13 · Cathedral City 11 · Desert Hot Springs 9 · Indian Wells 5 · Thousand
Palms 3 · Thermal 2 · Bermuda Dunes 2. *(recompute fresh from disk for any published figure.)*

## Anchor recall + chain-absence (market-structure finding)

Anchor recall **15/16** marquee anchors hit. The four national franchises that did
**not** surface were each given one targeted check → **confirmed no CV location**
(not sweep misses): **Goddard** (only the GSFOA franchisee-association admin address
is in Palm Desert — not a school), **La Petite** (nearest Palmdale), **Sylvan**,
**Huntington**. → The national early-childhood & tutoring franchises are **absent
from the CV**; the market is independents + the few chains that are present
(KinderCare, Kumon, Mathnasium, First School regional). Enrichment additionally
caught the **Desert Hot Springs KinderCare as a ghost listing** (the chain's own
page shows no active center).

## Headline visibility stats (n = 216)

| Dimension | Result |
|---|---|
| `agent_visibility_score` | medium **122** · high **67** · low **26** · invisible **1** |
| low + invisible (the "gap") | **27 / 216 = 12.5%** |
| Crawler-blocked (403 / challenge to bots) | **40 / 201 checkable = 19.9%** |
| Structured data present (JSON-LD / schema.org) | **5 / 160 checkable = 3.1%** |
| `currently_open` | open 161 · unknown 43 · **closed 12** (ghost/closed centers caught) |
| `tuition_or_fees_displayed` = yes | **37 / 216 = 17.1%** (83% do not display pricing) |

> Structurally consistent with dining and H&RE: **near-zero structured data (3.1%)**
> and heavy crawler-blocking (19.9%). The agent-visibility **gap (12.5%)** sits
> between dining (5.0%) and is on par with real estate (11.4%) — the CV family/
> schooling layer is materially illegible to agents, and **83% hide pricing**, the
> single highest-value query a relocating family's agent would ask.

## Credential-display capture — the verification-leg teaser + the inspectors-pattern

| Subcategory | credential shown / n | state credential exists? |
|---|---|---|
| licensed childcare & daycare (centers) | 7 / 18 = **38.9%** | yes — CDSS license # |
| private K-12 schools | 6 / 17 = **35.3%** | yes — school accreditation |
| preschools & early-childhood | 6 / 30 = **20.0%** | yes — CDSS license # |
| special-needs & developmental | 2 / 28 = 7.1% | mostly no (a few CAC/IBCCES) |
| tutoring · youth sports · arts · camps | **0 / 123 = 0%** | **no state credential exists** |

`credential_type_guess` overall: none-visible **194** · CDSS **11** · accreditor **10** · unknown 1.

> **The inspectors-pattern, inverted.** Unlike dining (health permits) or real
> estate (DRE/NMLS), **151 of 216 entities (5 subcategories) have NO state credential
> to display at all** — youth sports, arts, tutoring, camps, and most developmental
> services are simply unregulated at the state level. The verification leg for this
> category is therefore **narrow**: only the ~65 childcare/preschool (CDSS) and
> school (accreditation) entities carry a verifiable credential — and even they
> display it only **20–39%** of the time. The same EC/childcare layer that is the
> *only* one with a credential is also the one with the most web-invisible operators
> (the 46 registry-only family homes + the low-visibility Indio center cluster).

## Token spend (usage basis)

| Stage | Subagent tokens |
|---|---:|
| Discovery (pilot + b1 + b2) | **769,778** (347,898 + 321,591 + 100,289) |
| Enrichment (6 batches: 40·40·40·40·40·16) | **3,915,446** |
| **Session total** | **4,685,224** (**39.0%** of the 12M guard) |
| Per entity (enrichment) | **18,127** (on the 17.5k pin) |
| Per entity (all-in disc+enrich) | 21,691 |

Guard never tripped; no priority-split needed. Zero merge failures, zero unmatched
rows across all 9 batches. *(Discovery `tokens_by_batch` in `discovery-state-final.json`
records output-basis `budget.spent()`; the usage-basis figures above — the
guard-relevant ones — come from the workflow task notifications.)*

## Files

- `cv-family-schooling-census-final.json` — full 278-row dataset; 216 carry the ~20
  enrichment fields + `enriched: true`; 16 carry `segment: review`; 46 carry
  `segment: family_home_daycare`. Each row also has `entity_kind`, `enrich_target`,
  discovery provenance (`_disc_batch`, `_src_subcat`, `_src_geo`), and where
  applicable `programs_note`, `name_enriched`, `_verify_note`.
- `discovery-state-final.json` / `enrich-state-final.json` — discovery & enrichment
  state (counts, dedup/reconcile logs, usage-by-batch, cumulative spend, guard).
- `journal/inspection-journal.jsonl` — 216 enrichment records, one per entity,
  tagged `_batch` + `_run_id` + `_src_name`.
- `journal/{discovery,enrich}-NN-<wf-id>.json` — raw per-batch workflow results.
- `scripts/` — discovery, enrichment, the merge / dedup / gate2-reconcile / gen
  scripts, for reproducibility.
- `stats/` — `stats.py` + `stats.json` (all denominators recomputed fresh from disk).

## Provenance — workflow run IDs

**Discovery:** `wf_ebfd3a0c-efa` (pilot/b0), `wf_abc2e3e8-a6c` (b1), `wf_c4410dc6-34e` (b2).
**Enrichment:** `wf_9dd3f60d-631` (b0), `wf_a258ab0c-45a` (b1), `wf_a2619082-b4a` (b2),
`wf_634d426a-852` (b3), `wf_7bcd2f60-6f9` (b4), `wf_c4eb1f85-724` (b5).

Source scratch (untracked in `com/` per `tmp-` discipline, never committed there):
`tmp-agent-mapped-fs.json`, `tmp-agent-mapped-fs-state.json`,
`tmp-agent-mapped-fs-enrich-state.json`, `tmp-fs-*.js|.py`.

## Open items for the synthesis/report session (NOT done here)

- Recompute all denominators fresh from disk with definitions stated.
- **Credential-verification leg** (separate deterministic pass): the ~65 CDSS/
  accreditation entities — match displayed license #s against the CDSS registry;
  decide how the 46 `family_home_daycare` registry-only homes appear (market context,
  not prospects).
- Resolve the 2 `_verify_note` rows (Dove's Landing city; Montessori PS&PD variant).
- The 16 `review` rows: decide which (if any) are real for a supplemental enrichment
  vs which are confirmed phantoms (e.g. "Rancho Mirage Children's School" — checked,
  confirmed phantom).
- `entity_kind` is heuristic — verify before relying on campus/program_brand/solo splits.
- Public districts/charters (PSUSD/DSUSD/CVUSD) were **not** censused (concept-node
  material for the report); none entered the dataset.
- Subcategory refinements observed at enrichment (e.g. Desert Adventist is TK-8 not
  K-12; The Academy PD is preschool/K) are recorded in `ages_grades_served` /
  `visibility_gap_note` — reconcile canonical subcat at synthesis.

## Template improvements folded back into `templates/census/` (this run)

1. **Public-detector reads the NAME only** — a private org whose *note* mentions a
   district/charter partnership (e.g. "PSUSD vendor") is in scope, not public.
2. **Dropped the bare `verify` triage flag** — it over-routed real in-scope therapy
   providers to review; the specific `campus not confirmed` / medical-ambiguity
   signals are retained.
