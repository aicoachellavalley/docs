# Canonical taxonomy mapping — VGPS metacategories

Three-level mapping reported at Aggregate:

1. **Raw labels** — exactly what VGPS emits in each listing's embedded JSON.
2. **Canonical categories** — duplicate-collapsed; meaningful for analysis.
3. **Strategic buckets** — **seven** high-level buckets for the headline review cut.

The workflow's Aggregate stage uses both maps (`CANONICAL_MAP` and `STRATEGIC_MAP`) and outputs all three counts. Any raw label not in the map falls through to `(unmapped: <label>)` so new VGPS labels never silently disappear — they show up flagged for review and get added in the next iteration.

## The mapping

| Raw label (VGPS as-emitted) | Canonical category | Strategic bucket |
|---|---|---|
| STAY | Lodging | Lodging |
| PLACES TO STAY | Lodging | Lodging |
| EAT & DRINK | Dining | Dining |
| THINGS TO DO | Activities | Experiences |
| ACTIVITIES & RECREATION | Activities | Experiences |
| TOURS | Tours | Experiences |
| ARTS & CULTURE | Arts & Culture | Experiences |
| CASINOS & ENTERTAINMENT | Entertainment | Experiences |
| GOLF | Golf | Experiences |
| HIKING TRAILS | Outdoor Recreation | Experiences |
| SPAS, BEAUTY & WELLNESS | Spas & Wellness | Wellness |
| GROUP VENUES | Group Venues | Meetings & Events |
| MEETING & EVENT RESOURCES | Meeting Resources | Meetings & Events |
| WEDDINGS | Weddings | Meetings & Events |
| GETTING HERE | Transportation | Mobility |
| GETTING HERE & AROUND | Transportation | Mobility |
| VISITOR INFORMATION | Visitor Services | Mobility |
| SHOPPING | Shopping | Retail & Services |
| BUSINESS & PROFESSIONAL SERVICES | Professional Services | Retail & Services |
| RELOCATION & RESOURCES | Relocation | Retail & Services |
| FILM PRODUCTION SERVICES | Film Production | Retail & Services |
| CANNABIS | Cannabis | Retail & Services |
| DOG-FRIENDLY RESOURCES | Pet Services | Retail & Services |
| _(null / no metacategory)_ | (uncategorized) | (uncategorized) |
| _(any label not above)_ | (unmapped: \<label\>) | (unmapped) |

## The seven strategic buckets

1. **Lodging** — hospitality, retreats. Where visitors sleep.
2. **Dining** — restaurants, bars, breweries, cafes. Where visitors eat.
3. **Experiences** — activities, tours, arts venues, entertainment, golf, hiking. Why visitors come.
4. **Wellness** — spas, beauty, wellness practitioners. _Promoted from canonical to its own strategic bucket 2026-06-05 — 198 records in the scoring set, directly aligned with AICV's content-gap roadmap (memory: "Wellness & Healthcare: 3 nodes. Target 25–30. Mid-tier wellness and family-applicable healthcare missing — highest-priority content gap for SF/LA founder-relocation use case")._
5. **Meetings & Events** — group venues, meeting resources, weddings. The corporate/group business.
6. **Mobility** — transportation, visitor services, getting around. The access layer.
7. **Retail & Services** — shopping, professional services, relocation, specialty services (film production, cannabis, pet services). The supporting infrastructure for residents and longer-stay visitors.

## Regex for metacategory detection

Raw metacategory labels are uppercase strings (often with punctuation). The Inventory/Merge stage uses:

```
/^[A-Z\s&,\-']+$/
```

This allows uppercase letters, whitespace, `&`, comma, hyphen, and apostrophe. Apostrophe is insurance against future labels like `KIDS' ACTIVITIES`. Comma and hyphen recover real VGPS labels that the original strict regex `/^[A-Z &]+$/` rejected (`SPAS, BEAUTY & WELLNESS`, `DOG-FRIENDLY RESOURCES`).

## Rationale for label decisions (2026-06-05 amendments)

- **`GOLF` gets its own canonical category** (not folded into Activities). Golf is too distinctive to the Coachella Valley economy — 69+ listings in the scoring set, recognizable as a destination driver. Hiding it under "Activities" would obscure a category AICV needs to report on.
- **`HIKING TRAILS` → canonical `Outdoor Recreation`** (not "Hiking & Outdoors"). Broader and more durable — future VGPS additions like mountain biking, climbing routes, or off-road trails fit cleanly under "Outdoor Recreation" without a rename.
- **`SPAS, BEAUTY & WELLNESS` promoted to its own strategic bucket "Wellness"** rather than folded into Experiences. 198 records in scoring set; substantively distinct operator type and visitor motivation; directly addresses an AICV content-gap priority.
- **`VISITOR INFORMATION` → strategic Mobility**, not Retail & Services. These are visitor centers, official welcome resources — they sit in the access/orientation layer alongside transportation, not in the retail layer.
- **`FILM PRODUCTION SERVICES` and `CANNABIS` → Retail & Services**. Specialty service operators; small counts (18 and 16 respectively); fit the supporting-infrastructure framing.
- **`DOG-FRIENDLY RESOURCES` → canonical `Pet Services`** in Retail & Services. Practical infrastructure for residents and pet-owning visitors; sits next to professional services and shopping.

## Edge cases

- A listing can appear under multiple metacategories (same business, multiple `vgps_id`). Per-listing scoring preserved. Aggregate also reports `unique_businesses` (deduped by `weburl`) alongside `total_listings`.
- A new raw label not in the map → labeled `(unmapped: <RAW_LABEL>)` at canonical, `(unmapped)` at strategic. Flagged in `unmapped_raw_labels` and `anomalies_summary`.
- Listings with no raw `primary_category` (catname regex found no uppercase value) → `(uncategorized)` at all three levels.
- **artsGPS public-art listings** (sculptures, murals, road signs) are excluded at Inventory: Merge via the `public_art_excluded` rule (`subcategories contains 'artsGPS' AND weburl is empty`). They aren't partner businesses — segregated to `inventory-public-art-excluded.jsonl`, not lost. 308 records as of 2026-06-05.

## Coverage check, 2026-06-05

The recovery re-merge on 2026-06-05 produced this metacategory distribution within `partner-directory-clean.json` (3,333 records eligible for scoring):

| Raw label | Records |
|---|---|
| EAT & DRINK | 850 |
| SHOPPING | 270 |
| RELOCATION & RESOURCES | 263 |
| MEETING & EVENT RESOURCES | 229 |
| STAY | 218 |
| SPAS, BEAUTY & WELLNESS | 198 |
| ACTIVITIES & RECREATION | 196 |
| WEDDINGS | 159 |
| GROUP VENUES | 147 |
| PLACES TO STAY | 127 |
| THINGS TO DO | 121 |
| ARTS & CULTURE | 103 |
| BUSINESS & PROFESSIONAL SERVICES | 101 |
| GOLF | 69 |
| GETTING HERE & AROUND | 60 |
| DOG-FRIENDLY RESOURCES | 54 |
| TOURS | 39 |
| VISITOR INFORMATION | 39 |
| GETTING HERE | 20 |
| FILM PRODUCTION SERVICES | 18 |
| CASINOS & ENTERTAINMENT | 16 |
| HIKING TRAILS | 16 |
| CANNABIS | 16 |
| _(empty — 4 residual edge cases)_ | 4 |
| **Total** | **3,333** |

Every raw label that surfaced is now mapped. Aggregate's `unmapped_raw_labels` list should be empty when the standalone Wide-Scan + Aggregate workflow runs.
