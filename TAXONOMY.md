# AICV Taxonomy Conventions

Canonical names for cities, regions, and groupings used across AICV
content. New nodes, briefs, and any surface referencing locations
MUST use these canonical values.

## Nine Incorporated Cities of the Coachella Valley

Canonical city field values (human-readable, title case):

- Palm Springs
- Desert Hot Springs
- Cathedral City
- Rancho Mirage
- Palm Desert
- Indian Wells
- La Quinta
- Indio
- Coachella

## Regional Designations

- **Coachella Valley** — valley-wide designation (use for content that
  spans the region, not specific to any city). Canonical value:
  "Coachella Valley". Do NOT use: "Valley Wide", "Valley-Wide",
  "valley-wide", "CV", or other variants in structured data.
- **Adjacent Communities** — unincorporated areas connected to the
  valley economy (Thousand Palms, Bermuda Dunes, Thermal, Mecca, Sky
  Valley, and similar). Canonical value: "Adjacent Communities" (title
  case, not slug-style).

## Shorthand

"CV" is acceptable in informal prose and conversation. Do NOT use in
content frontmatter, structured data, or any field that an agent or
consumer might parse. Structured data uses fully-spelled proper nouns.

## Data Normalization Status

As of 2026-04-19, the `city` field in com/src/content/nodes/ has known
variants from multiple sessions before this convention was established:
"Coachella Valley", "Valley Wide", "Valley-Wide", "valley-wide", and
the slug-style "adjacent-communities" alongside properly-named cities.
Normalization pass scheduled in the verification ledger queue.
Until normalized, consumers should expect drift. After normalization,
this convention is load-bearing and new entries MUST conform.
