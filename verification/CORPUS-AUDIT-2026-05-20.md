# AICV Node Corpus Diagnostic Report
**Date:** 2026-05-20
**Corpus:** 80 nodes · `~/Projects/com/src/content/nodes/`
**Schema:** `~/Projects/com/src/content.config.ts`
**Status:** Read-only. No files written.

---

## Stage 1 — Corpus Size and Schema State

### Confirmed Schema Fields

| Field | Type | Required | Axis |
|---|---|---|---|
| `title` | string | ✓ | Identity |
| `description` | string | ✓ | Identity |
| `agent_summary` | string | optional | Agent summary |
| `city` | string | ✓ | **Geography** |
| `category` | string | ✓ | **Life-domain proxy (degraded — see below)** |
| `subcategory` | string | optional | Life-domain refinement |
| `last_updated` | string | optional | Temporal |

### Schema-Extra Fields (in nodes but NOT in Zod — unvalidated, not type-safe)

All 80 nodes carry four fields by convention only:

| Field | Presence | Notes |
|---|---|---|
| `status` | 80/80 | Values: `live` — not validated |
| `verified` | 80/80 | Boolean — not validated |
| `agent_intent` | 80/80 | Array of intent strings — **de facto funnel-stage field, invisible to schema** |
| `related` | 22/80 | Array of slug/type pairs — not validated |

### Structural Gaps — Three Axes

| Axis | Schema Field | Status |
|---|---|---|
| **Geography** | `city` (required string) | Formalized but not enum-constrained. Free-text; no validation against canonical city list. 59% of nodes use non-canonical values. |
| **Funnel-stage** | `agent_intent` (schema-extra) | **Not in schema.** Present on all 80 nodes as unvalidated array. Free-form values; no canonical enum. Not accessible via Astro content API. No node encodes "Build." |
| **Life-domain** | `category` (required) | **Collapsed to binary.** 77/80 nodes: `landmark`. 3/80: `event`. This is a type flag, not a life-domain taxonomy. All domain differentiation falls to `subcategory`, which is optional and free-form. |

### Playbook Context

`TAXONOMY.md` defines canonical geography but does **not** define a canonical category enum or life-domain list. `STATE.md` (2026-05-11) confirms the three-axis model was locked as architectural intent, with "formal enforcement deferred."

**Key finding: The corpus operates on a ghost schema.** The real information architecture (`agent_intent`, `related`, `status`, `verified`) lives outside the Zod-validated layer. The schema enforces almost nothing about the three-axis model.

**Corpus count confirmed: 80 nodes** (81 files in directory including one `CLAUDE.md`). Prior "75-node" session note was stale.

---

## Stage 2 — Distribution Tables

### Table A — Geography Distribution

| City Value | Count | Canonical? |
|---|---|---|
| Valley Wide | 26 | ❌ variant of "Coachella Valley" |
| Palm Desert | 14 | ✓ |
| Rancho Mirage | 10 | ✓ |
| Palm Springs | 6 | ✓ |
| Indian Wells | 6 | ✓ |
| La Quinta | 5 | ✓ |
| Indio | 5 | ✓ |
| adjacent-communities | 4 | ❌ slug-style, should be "Adjacent Communities" |
| Valley-Wide | 1 | ❌ hyphenated variant |
| valley-wide | 1 | ❌ lowercase slug variant |
| Coachella Valley | 1 | ✓ |
| Coachella | 1 | ✓ |
| **Total** | **80** | |

**47/80 nodes (59%) use non-canonical `city` values.** Three variants of "valley-wide" exist (26+1+1=28). Four adjacent-community nodes use slug-style casing.

**Zero nodes for two canonical cities: Desert Hot Springs and Cathedral City.**

### Table B — Founder-Funnel Stage Distribution

Funnel-stage is not in the schema. Distribution is inferred from `agent_intent` (schema-extra field, present on all 80 nodes) mapped to canonical stages. Values in `agent_intent` are free-form; canonical mapping required best-judgment alignment.

| Canonical Stage | Nodes (primary) | Nodes (any) | Notes |
|---|---|---|---|
| Discover | ~12 | ~40 | "research", "understand", "intelligence" intents map here |
| Visit | ~10 | ~35 | Hospitality, events, attractions |
| Return | ~5 | ~20 | Festival, seasonal, destination nodes |
| Satellite | ~8 | ~25 | Economic dev, coworking, innovation nodes |
| Relocate | ~6 | ~20 | Real estate, residential, community nodes |
| Build | **0** | **~8** | **No node encodes Build as primary.** Some Founder Infra nodes serve it implicitly. |

**Non-canonical `agent_intent` values observed (partial list):** "understand", "research", "corporate-offsite", "wellness", "golf", "executive", "fund", "sponsor", "hire", "attend", "route", "relocation" (vs. canonical "Relocate"). None map cleanly without interpretation. "Build" is entirely absent as a primary intent.

### Table C — Life-Domain Distribution

Mapped from `subcategory` values (since `category` is non-functional at the domain level):

| Life-Domain | Current Count | Subcategory(ies) used |
|---|---|---|
| Arts & Culture | 13 | cultural (9), entertainment (4) |
| Founder Infrastructure | 14 | economic (9 econ-dev nodes), innovation (4), + 1 |
| Outdoors & Recreation | 10 | golf (8), + 2 |
| Hospitality & Retreat Venues | 10 | hospitality (7), + 3 |
| Media & Story | 7 | media (6), + 1 |
| Access & Arrival | 5 | — (airport, corridor, aviation nodes) |
| Civic & Safety | 5 | nonprofit (3), + 2 |
| Talent & Workforce | 3 | education (1), workforce-talent concept, + 1 |
| Home & Real Estate | 3 | real-estate (1), + 2 development-pipeline nodes |
| Wellness & Healthcare | 3 | wellness (2), + eisenhower-health |
| Food & Dining | 2 | retail (partial — El Paseo, Gardens) |
| Service Class | 2 | retail (partial — The River, Old Town LQ) |
| **Family & Schooling** | **0** | **— entirely absent** |
| Meta/routing (no domain) | 6 | intelligence (14 total, ~6 non-assignable), node-zero, desert-season |
| **Total** | **~80** | |

**Non-canonical values surfaced:** "intelligence" (14 subcategory hits) is a functional descriptor with no canonical life-domain equivalent. "economic" (14 hits) straddles Founder Infrastructure and Civic & Safety with no clean mapping.

---

## Stage 3 — Coordinate Consistency

### Summary Counts

| Status | Count | Definition |
|---|---|---|
| Complete | 0 | All three axes explicit, canonical, unambiguous |
| Partial | ~65 | Geography explicit; life-domain inferable from subcategory; funnel-stage schema-extra only |
| Inconsistent | ~15 | Non-canonical city values AND/OR subcategory maps to no canonical domain AND/OR agent_intent uses non-canonical vocabulary |

**No node is Complete** by the strict definition — funnel-stage is off-schema for all 80, and `category` maps to a life-domain for 0/80.

### Notable Partial/Inconsistent Nodes

| Node | Issue |
|---|---|
| `ai-economy-coachella-valley` | city: "Valley Wide" (non-canonical); subcategory: "intelligence" (no domain mapping) |
| `ai-startup-activity` | city: "Valley Wide"; subcategory: "intelligence" |
| `civic-infrastructure` | city: "Valley Wide"; subcategory: "economic" (ambiguous) |
| `coachella-valley-intelligence-index` | city: "Valley Wide"; subcategory: "intelligence" — meta-node with no domain home |
| `node-zero` | city: "Valley Wide"; purpose is structural/routing, not geographic or domain-specific |
| `desert-jet-center` | city: "adjacent-communities" (non-canonical slug) |
| `jacqueline-cochran-regional-airport` | city: "adjacent-communities" (non-canonical slug) |
| `thermal-club` | city: "adjacent-communities" (non-canonical slug); subcategory: "golf" — should be La Quinta or Thermal |
| `high-desert-art-fair` | city: "adjacent-communities" (non-canonical slug) |
| `luxury-corridor` | city: "Valley Wide"; subcategory: "economic" — concept node, no clear domain |
| `retreat-economy` | city: "Valley Wide"; subcategory: "hospitality" — concept, not entity |
| `wellness-positioning` | city: "Valley Wide"; subcategory: "wellness" — concept, not entity |
| `coachella-valley-economic-development` | city: "Valley-Wide" (hyphenated variant) |
| `workforce-talent` | city: "Coachella Valley" (canonical) but subcategory straddles Founder Infra and Talent |
| `desert-season` | city: "Valley Wide"; no clear domain — seasonal concept node |

---

## Stage 4 — Gap Analysis

| Life-Domain | Current | Target | Gap to Floor | Severity |
|---|---|---|---|---|
| **Family & Schooling** | **0** | 25–30 | **−25** | 🔴 Critical |
| **Home & Real Estate** | **3** | 30–40 | **−27** | 🔴 Critical |
| **Wellness & Healthcare** | **3** | 25–30 | **−22** | 🔴 Critical |
| **Talent & Workforce** | **3** | 15–20 | **−12** | 🔴 Critical |
| **Hospitality & Retreat Venues** | **10** | 25–30 | **−15** | 🔴 Critical |
| **Founder Infrastructure** | **14** | 30–40 | **−16** | 🔴 Critical |
| **Access & Arrival** | **5** | 8–10 | **−3** | 🟡 Meaningful |
| Arts & Culture | 13 | unsized | — | unsized |
| Outdoors & Recreation | 10 | unsized | — | unsized |
| Media & Story | 7 | unsized | — | unsized |
| Civic & Safety | 5 | unsized | — | unsized |
| Food & Dining | 2 | unsized | — | unsized |
| Service Class | 2 | unsized | — | unsized |

### Top 3 Domain Gaps Most Critical for an SF/LA Founder Query

*"What's it like to live and build in the Coachella Valley?"*

**1. Family & Schooling — 0 nodes (entirely absent)**
The SF/LA tech cohort overwhelmingly relocates with school-age children. Zero nodes cover K-12 schools, childcare, family-oriented neighborhoods, or school district quality. Any founder query touching "move my family" returns silence. Desert Sands Unified (the primary K-12 system for the Palm Desert–Indian Wells–La Quinta corridor) and Palm Springs Unified have no representation. This is not thin coverage — it is a complete absence.

**2. Home & Real Estate — 3 nodes (premium end only)**
Cotino (new-construction luxury), North Palm Desert Development Zone, and Development Pipeline. The corpus can answer "is there new construction?" and nothing else. The valley's existing housing sub-markets — south Palm Springs mid-century, Rancho Mirage estates, Indian Wells country club communities, Old Town La Quinta walkable zone — are invisible. No founder can answer "where would I actually live?" from this corpus.

**3. Wellness & Healthcare — 3 nodes (one hospital, one ultra-luxury adults-only retreat, one concept)**
Eisenhower Health, Sensei Porcupine Creek (residency-required adults-only, $1,225+/night), and Wellness Positioning (concept). For "is healthcare here adequate for my family?", the corpus has one hospital node and two non-family-applicable entries. Missing: urgent care networks, specialty care referral infrastructure, mid-tier spa economy (Two Bunch Palms, Agua Caliente spa), mental health practitioners, and the daily-life wellness calendar the valley's identity rests on.

---

## Stage 5 — Editorial Layer Sample

**10 nodes sampled:** `cotino`, `sensei-porcupine-creek`, `psp-airport`, `el-paseo`, `education-corridor`, `sunshinefm-startup-studios`, `workforce-talent`, `coachella-festival`, `eisenhower-health`, `desert-sun`

**Scoring:** ✅ Full (all three: place-attached metadata + demographic-fit + visit-context) · 🟡 Partial (two of three) · ❌ Directory entry (one or zero)

| Node | Score | What's missing |
|---|---|---|
| `cotino` | ✅ Full | — Specific cross-streets, explicit founder/post-liquidity demographic, 30-day rental constraint, fall 2026 Town Center timing |
| `sensei-porcupine-creek` | ✅ Full | — Specific address + foothills context, adults-only/executive framing, package types and nightly floor |
| `psp-airport` | ✅ Full | — Drive-time table to 14+ destinations, seasonal peak noted, SF/LA direct routes flagged |
| `el-paseo` | ✅ Full | — Nine-block stretch mapped, seasonal hours/closures, monthly Art Walk + Fashion Week dates |
| `education-corridor` | 🟡 Partial | Visit-context absent — institutional facts present but no "when a founder directly engages" framing |
| `sunshinefm-startup-studios` | 🟡 Partial | Visit-context thin; one reference (Mirage app) is stale |
| `workforce-talent` | 🟡 Partial | Visit-context absent — reads as intelligence brief, not an engageable entity |
| `coachella-festival` | 🟡 Partial | No founder-specific framing; economic signal rather than visit-planning entry |
| `eisenhower-health` | 🟡 Partial | Visit-context absent; no individual/family framing — employer signal only |
| `desert-sun` | ❌ Directory entry | No sub-area context, no demographic-fit, no use-case framing |

**Pattern:** 4/10 full editorial layer · 5/10 partial · 1/10 directory entry.

Full-layer nodes are consistently **place-specific experiential nodes** (resort, airport, shopping corridor, real estate). Partial nodes are **concept/intelligence nodes** — institutional facts without "who goes there and why." The most common missing element across all partials is **visit-context/use-case framing**: the gap between "what this entity is" and "when and why a founder would engage with it in practice."

---

## What This Means for an MVP Corpus

The 80-node corpus resolves the **visit and invest** layers of the founder journey reasonably well. An agent asked "should I go to Coachella Valley for a weekend retreat?" can route confidently to Sensei Porcupine Creek, La Quinta Resort, Ritz-Carlton, the tennis garden, PSP logistics, and festival context. The hospitality and outdoor recreation layers have genuine depth. The media and economic development layers are well-covered.

An agent asked **"should I move my family and build a company here?"** is operating with severe blind spots in three load-bearing domains: no school data anywhere in the corpus, housing coverage limited to one new-construction luxury development, and healthcare reduced to a hospital node and an ultra-luxury adults-only retreat. These three gaps — Family & Schooling (0 nodes), Home & Real Estate (3 nodes), Wellness & Healthcare (3 nodes) — collectively make the corpus unable to answer the most consequential founder questions about the valley.

**The 2–3 most load-bearing additions before anything else:**

First, **6–8 Family & Schooling nodes**: Desert Sands Unified, Palm Springs Unified, 2–3 private/independent school nodes, and 1–2 childcare/early-childhood nodes. This domain is entirely absent; every other gap is a matter of depth. This one is a matter of existence.

Second, **4–6 Home & Real Estate nodes** covering distinct sub-markets: south Palm Springs mid-century, Rancho Mirage estates, Indian Wells country club enclave, Old Town La Quinta walkable zone. Cotino covers the premium new-construction end; the valley's existing residential fabric is invisible.

Third, **5–7 Wellness & Healthcare nodes** at the individual-use level: urgent care access (CV Urgent Care network), specialty referral infrastructure, Two Bunch Palms (mid-tier accessible spa), mental health practitioners, and the wellness calendar as daily life rather than resort amenity.

**Structural schema change also required before the corpus is machine-queryable:**
The three-axis model is currently addressable in zero axes. Geography is present but 59% non-canonical. Life-domain is collapsed to a binary `landmark`/`event` flag. Funnel-stage exists only as a schema-extra unvalidated array with non-canonical vocabulary and no "Build" encoding. The minimal fix: (1) add `domain` as a required enum with the 13 canonical life-domain values, (2) add `funnel_stages` as a required validated array with the 6 canonical stages, (3) normalize `city` to the 11 canonical values. These three changes transform the corpus from a well-written directory into a genuinely machine-addressable three-axis knowledge graph.
