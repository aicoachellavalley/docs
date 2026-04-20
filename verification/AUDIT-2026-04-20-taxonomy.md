# Taxonomy Audit — 2026-04-20

Read-only corpus inspection conducted during SCHEMA v1.1 amendment
work. Findings reshape the scope of v1.1 and define the agenda for a
dedicated taxonomy-model session.

---

## TAXONOMY.md says

The canonical city list is the **nine incorporated cities**: Palm
Springs, Desert Hot Springs, Cathedral City, Rancho Mirage, Palm
Desert, Indian Wells, La Quinta, Indio, Coachella.

Regional designations are defined as a **separate tier** from cities:

- **"Coachella Valley"** is the canonical valley-wide designation
  (title case, not hyphenated-slug). Explicitly forbidden variants in
  structured data: "Valley Wide", "Valley-Wide", "valley-wide", "CV".
- **"Adjacent Communities"** is defined as unincorporated areas
  connected to the valley economy. Named examples: Thousand Palms,
  Bermuda Dunes, Thermal, Mecca, Sky Valley, "and similar". Canonical
  value: "Adjacent Communities" (title case, not slug-style).

Valley-wide and adjacent-communities are treated as **distinct**
designations, not consolidated — they live in the same "Regional
Designations" section but as separate bullets with different meanings
(cross-valley scope vs. unincorporated-adjacent geography).

No other categories (no "region", "scope", "cross-valley" as named
types). TAXONOMY.md section 4 explicitly flags current city-field
normalization drift — multiple variants coexist in the corpus and a
"normalization pass" is queued in the verification ledger.

---

## Valley-wide membership

**28 ZONE_MAP entries**, **28 com/ nodes** with `city` field matching
a Valley-Wide variant, plus 1 node (`workforce-talent`) with canonical
`city: "Coachella Valley"` also in valley-wide ZONE_MAP. Total:
**29 distinct nodes** semantically in the valley-wide bucket.

Frontmatter variant spread:

- "Valley Wide" × 26
- "Valley-Wide" × 1 (coachella-valley-economic-development)
- "valley-wide" × 1 (ai-startup-activity)
- "Coachella Valley" × 1 (workforce-talent) — **only this one conforms
  to TAXONOMY.md**

Membership by semantic subclass:

| Subclass | Count | Examples |
|---|---|---|
| **Meta/thematic aggregate concepts** (not entities — summary lenses across the valley) | 15 | innovation-economy, luxury-corridor, retreat-economy, wellness-positioning, golf-destination, desert-season, aviation-gateway, creative-economy-coachella-valley, ai-economy-coachella-valley, ai-startup-activity, development-pipeline, civic-infrastructure, nonprofit-philanthropy, workforce-talent, coachella-valley-economic-development |
| **Genuine cross-valley organizations/events** (entities with jurisdiction or mandate spanning the whole valley) | 4 | visit-greater-palm-springs, riverside-county-economic-development, cv-giving-day, coachella-valley-ai-events |
| **Media outlets** (entities with valley-wide coverage scope, but editorially based in specific cities) | 6 | desert-sun, palm-springs-life, kesq-news-channel-3, nbc-palm-springs, coachella-valley-independent, coachella-valley-weekly |
| **Platform/index/routing nodes** (AICV's own infrastructure) | 2 | coachella-valley-intelligence-index, node-zero |
| **Cross-city geographic features** | 1 | highway-111-corridor |
| **Drift case** (frontmatter says "Valley Wide" but ZONE_MAP places in palm-desert) | 1 | desert-community-foundation (valley-wide city, palm-desert zone) |

**Assessment:** The category is not semantically coherent. It mixes
five distinct kinds of things — thematic concept aggregations (15, the
dominant subclass), genuine cross-valley organizations (4, what the
user described), media outlets (6), platform infrastructure (2), and
one geographic corridor. The user's description ("entities whose
jurisdiction spans the entire Coachella Valley, CVAG, VGPS, etc.")
covers only the 4 organization nodes. The majority use of the bucket
is actually for **thematic synthesis/meta nodes** that are not
"entities" in the jurisdictional sense. Assigning these a single
`target_type: "zone"` in SCHEMA v1.1 would collapse five meaningfully
different categories into one.

---

## Adjacent-communities membership

4 ZONE_MAP entries, 4 com/ nodes with `city: "adjacent-communities"`
(slug-style, not the TAXONOMY canonical "Adjacent Communities").

| Slug | Title | Description (1-sentence) | Geographic reality |
|---|---|---|---|
| jacqueline-cochran-regional-airport | Jacqueline Cochran Regional Airport | Primary private aviation facility; UHNW/Thermal Club/festival-VIP arrival gateway | Thermal (unincorporated Riverside County, Coachella Valley proper) |
| thermal-club | Thermal Club | Ultra-private members club; aviation/motorsports/residential amenities for UHNW | Thermal (unincorporated Riverside County, Coachella Valley proper) |
| desert-jet-center | Desert Jet Center | Executive FBO at Jacqueline Cochran Regional Airport | Thermal (unincorporated Riverside County, Coachella Valley proper) |
| high-desert-art-fair | High Desert Art Fair | Annual boutique art fair at Pioneertown, adjacent to Joshua Tree National Park | Pioneertown (**high desert, San Bernardino County — not Coachella Valley**) |

ZONE_MAP entries for adjacent-communities:
`adjacent-communities/high-desert-art-fair`,
`adjacent-communities/thermal-club`,
`adjacent-communities/jacqueline-cochran-regional-airport`,
`adjacent-communities/desert-jet-center` (all 4 present).

**Assessment:** Adjacent-communities is more internally coherent than
valley-wide — all 4 are physical entities in unincorporated areas,
matching TAXONOMY.md's "unincorporated areas connected to the valley
economy" framing. However, the bucket mixes two sub-geographies:
3 nodes in **Thermal** (genuinely adjacent unincorporated Coachella
Valley, per TAXONOMY's named examples) and 1 node
(`high-desert-art-fair`) in **Pioneertown/Morongo Basin** — the high
desert across the mountains, a different county and geographic region
that TAXONOMY.md does not explicitly enumerate. Stretching "adjacent"
to mean "near but not in the valley" is a softer drift than
valley-wide's drift, but still a drift.

---

## Category coherence assessment

The three-way split (9 cities · valley-wide · adjacent-communities)
that SCHEMA v1.1 was about to encode as uniform `target_type: "zone"`
is not semantically uniform:

- **9 cities** — coherent. Each is an incorporated municipality with
  defined boundaries.
- **valley-wide (29 nodes)** — incoherent. Hosts five distinct
  semantic subclasses (thematic concepts, cross-valley orgs, media,
  platform, geographic corridors), with the dominant use
  (15/29 = ~52%) being thematic/meta aggregate nodes that aren't
  geographic entities at all.
- **adjacent-communities (4 nodes)** — mostly coherent (3/4 match
  TAXONOMY's "unincorporated near-valley" definition), with 1 node
  stretched into high-desert geography.

Key drift signals:

a. TAXONOMY.md's canonical "Coachella Valley" and "Adjacent
   Communities" values are used by only 1 and 0 nodes respectively —
   the corpus is almost entirely on non-canonical variants.
b. One node (desert-community-foundation) has inconsistent placement:
   city frontmatter says "Valley Wide", but ZONE_MAP places it in
   palm-desert.
c. The valley-wide ZONE_MAP bucket is functioning as a de facto
   "other" bin for everything that isn't a physical entity in a
   specific city.

---

## Implications for SCHEMA and TAXONOMY

A dedicated taxonomy-model session is queued to work through:

1. Whether thematic/meta aggregate nodes (innovation-economy,
   luxury-corridor, etc.) are a distinct ledger type or a misuse of
   the node type.
2. Whether valley-wide should be split into geographic-scope (CVAG,
   VGPS-type cross-valley orgs) vs thematic-lens (innovation-economy,
   luxury-corridor) categories.
3. Whether adjacent-communities should tighten to the TAXONOMY.md
   definition (unincorporated near-valley) and whether the Pioneertown
   case needs reclassification.
4. Canonicalization pass to align all 29 valley-wide and 4
   adjacent-communities node city-field values to TAXONOMY.md
   canonical forms.
