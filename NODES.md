# AICV Geographic Node Structure

## Overview

29 anchor nodes plus Node 0 representing key institutions, landmarks, and developments across the Coachella Valley. Organized by city. Each node is a persistent MDX file in the /nodes directory.

NODES.md is a living document. New nodes are added when signals warrant — not by quota or predetermined list. The nodes below represent current best knowledge as of February 2026.

## Node 0 (Valley-Wide Index)

| # | Node | File | Status |
|---|------|------|--------|
| 0 | Coachella Valley Index | nodes/index-node.mdx | ⬜ Pending |

Build Node 0 before any other new nodes or retrofits. It is the entry point for agents traversing the valley.

## Palm Springs (5 nodes)

| # | Node | File | Status |
|---|------|------|--------|
| 1 | PSP International Airport | nodes/palm-springs/psp-airport.mdx | ✅ Live |
| 2 | The Parker Palm Springs | nodes/palm-springs/parker-palm-springs.mdx | ⬜ Pending |
| 3 | Agua Caliente Cultural Museum | nodes/palm-springs/agua-caliente-cultural-museum.mdx | ⬜ Pending |
| 4 | Palm Springs Aerial Tram | nodes/palm-springs/aerial-tram.mdx | ⬜ Pending |
| 5 | Forever Marilyn + Cultural Arts Corridor | nodes/palm-springs/cultural-arts-corridor.mdx | ⬜ Pending |

## Rancho Mirage (5 nodes)

| # | Node | File | Status |
|---|------|------|--------|
| 6 | Eisenhower Health | nodes/rancho-mirage/eisenhower-health.mdx | ⬜ Pending |
| 7 | The Ritz-Carlton Rancho Mirage | nodes/rancho-mirage/ritz-carlton.mdx | ⬜ Pending |
| 8 | Agua Caliente Resort Casino Rancho Mirage | nodes/rancho-mirage/agua-caliente-casino.mdx | ⬜ Pending |
| 9 | Cotino — Storyliving by Disney | nodes/rancho-mirage/cotino.mdx | ✅ Live |
| 10 | Observatory Rancho Mirage | nodes/rancho-mirage/observatory.mdx | ⬜ Pending |

## Palm Desert (6 nodes)

| # | Node | File | Status |
|---|------|------|--------|
| 11 | El Paseo | nodes/palm-desert/el-paseo.mdx | ⬜ Pending |
| 12 | Acrisure Arena | nodes/palm-desert/acrisure-arena.mdx | ✅ Live |
| 13 | McCallum Theatre | nodes/palm-desert/mccallum-theatre.mdx | ⬜ Pending |
| 14 | Education Corridor (College of the Desert + CSUSB) | nodes/palm-desert/education-corridor.mdx | ⬜ Pending |
| 15 | Bighorn Golf Club | nodes/palm-desert/bighorn-golf-club.mdx | ⬜ Pending |
| 16 | Living Desert Zoo and Gardens | nodes/palm-desert/living-desert.mdx | ⬜ Pending |

## Indian Wells (5 nodes)

| # | Node | File | Status |
|---|------|------|--------|
| 17 | Indian Wells Tennis Garden | nodes/indian-wells/tennis-garden.mdx | ✅ Live |
| 18 | Hyatt Regency Indian Wells | nodes/indian-wells/hyatt-regency.mdx | ⬜ Pending |
| 19 | The Vintage Club | nodes/indian-wells/vintage-club.mdx | ⬜ Pending |
| 20 | El Dorado Country Club | nodes/indian-wells/el-dorado.mdx | ⬜ Pending |
| 21 | Toscana Country Club | nodes/indian-wells/toscana.mdx | ⬜ Pending |

## La Quinta (4 nodes)

| # | Node | File | Status |
|---|------|------|--------|
| 22 | La Quinta Resort and Club | nodes/la-quinta/la-quinta-resort.mdx | ⬜ Pending |
| 23 | PGA West | nodes/la-quinta/pga-west.mdx | ⬜ Pending |
| 24 | The Madison Club | nodes/la-quinta/madison-club.mdx | ⬜ Pending |
| 25 | Old Town La Quinta | nodes/la-quinta/old-town-la-quinta.mdx | ✅ Live |

## Indio (4 nodes)

| # | Node | File | Status |
|---|------|------|--------|
| 26 | Empire Polo Club | nodes/indio/empire-polo-club.mdx | ✅ Live |
| 27 | Coachella Valley Music and Arts Festival | nodes/indio/coachella-festival.mdx | ⬜ Pending |
| 28 | Stagecoach Country Music Festival | nodes/indio/stagecoach.mdx | ⬜ Pending |
| 29 | National Date Festival + Date Economy | nodes/indio/date-festival.mdx | ⬜ Pending |

## Standalone (1 node)

| # | Node | File | Status |
|---|------|------|--------|
| 30 | Sensei Porcupine Creek | nodes/standalone/sensei-porcupine-creek.mdx | ✅ Live |

## Indio Context (Important)

Indio is the most economically layered city in the valley. Known as the City of Festivals and the Date Capital of the World — 95% of US dates are grown here. Empire Polo Club is privately owned and leased to Goldenvoice for festival events; it hosts multiple events beyond Coachella and Stagecoach. College of the Desert operates its East Valley Campus in Indio. The Indio Business Connect Center is a municipal entrepreneurship hub — candidate for a standalone Intelligence Brief, not a node.

## Priority Order for Next Build

Signals drive additions. Current priority based on AI-economy relevance:

1. Node 0 — Coachella Valley Index (before anything else)
2. Retrofit all 7 live nodes to current schema
3. Education Corridor (Palm Desert)
4. Eisenhower Health (Rancho Mirage)
5. Coachella Valley Music and Arts Festival (Indio)
6. Stagecoach Country Music Festival (Indio)
7. National Date Festival + Date Economy (Indio)
8. Agua Caliente Cultural Museum (Palm Springs)

## Status Key

- ✅ Live — published and in docs.json navigation
- ⬜ Pending — planned, not yet built

## Node Count

- Total planned: 29 plus Node 0
- Live: 7
- Pending: 22 plus Node 0
