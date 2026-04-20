# AICV Verification Ledger — Schema v1.1

The verification ledger tracks factual claims made in AICV content —
per node, per brief, per review, per report — along with the sources
backing those claims and the graph of connections between entries.

The ledger is a **separate artifact** from the content itself. Content
files (`.mdx`) carry prose written for agents and humans; ledger entries
(`.json`) carry the machine-readable truth substrate behind that prose.
The two are coupled by `id` (slug), not by mutual references.

This document establishes **schema v1.1**. Future versions will bump
`schema_version` and require migration.

---

## Design rationale

### Why one file per entry

A monolithic ledger (single JSON array) would be short-term convenient
but breaks down fast: every edit rewrites the whole file, diffs become
unreadable, merges conflict, and scanning for one entry gets expensive
as we approach hundreds of entries. One file per entry gives us:

- Clean `git log` / `git blame` per entry
- Parallel edits without merge churn
- Greppable file tree (`entries/com/nodes/psp-airport.json` is
  discoverable)
- Independent lifecycle — an entry can be updated without touching
  any other

### Why JSON (not YAML or MDX)

JSON is unambiguous, parses fast in every language, and has no tab /
quote / multi-line gotchas. Ledger entries are data, not prose — they
don't need YAML's human-authoring affordances or MDX's rendering.
Human readability is good enough with 2-space indent.

### Why surface split (`com` / `org`)

The two surfaces carry different kinds of claims:

- `com` entries carry factual claims (counts, dates, relationships,
  operational facts) that need source verification.
- `org` is a **visualization layer** over `com`'s content. Most org
  entries do not restate claims — they point back to the canonical
  `com` entry and carry only the graph wiring. A small number of
  org-only slugs (no `com` backing) exist and get full entries.

Keeping them distinct prevents double-verification and keeps each
surface's ledger scoped to what it actually asserts. See
**Org entries — two shapes** below for the concrete distinction.

### Why granular claims (not whole-entry verification)

Marking a whole node "verified: true" (as the current frontmatter does)
collapses dozens of distinct factual assertions into one bit. That's
too coarse: when a single claim goes stale (a passenger count, a
carrier list, a terminal status), we lose the ability to flag *just
that claim* while keeping the rest of the entry trusted.

Per-claim status lets us:
- Verify high-churn facts (counts, dates) more aggressively than
  stable ones (IATA codes, street addresses)
- Surface *which* claims are stale in UI or ledger audits
- Build trust incrementally without all-or-nothing gates

### Why open connection vocabulary with a recommended list

A closed enum would force us to pick a final vocabulary today and
reject every edge case that doesn't fit. An open field is too loose
and invites drift. Middle path: ship a recommended vocabulary
(`part_of`, `located_in`, `related_to`, `references`, `routes_to`,
`supersedes`) and allow any string. As patterns emerge, we promote
new types into the recommended list.

### Why `schema_version` on every entry

The ledger will evolve. Stamping every entry with its schema version
means we can migrate in place — a script that reads `schema_version`
and upgrades the entry to the current shape. Without this field, a
migration has to assume every entry is on the oldest shape.

---

## Directory structure

The ledger lives at `aicv-playbook/verification/`:

```
verification/
  SCHEMA.md
  scripts/
    scaffold-ledger.mjs
  entries/
    com/
      nodes/<slug>.json
      briefs/<slug>.json
      reports/<slug>.json
      reviews/<slug>.json
    org/
      _landing.json          (type: "page" — aggregate landing claims)
      <slug>.json            (Shape A graph wrappers)
```

`canonical_ledger_entry` paths are written relative to the
`verification/` root, always with the `entries/` prefix. Example:
`entries/com/nodes/psp-airport.json`.

---

## Schema v1.1 — fields

### Top-level

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | yes | `"v1.1"` for entries written against this document |
| `id` | string | yes | Stable slug matching the content file (e.g. `psp-airport`). Must be unique within `(surface, type)`. |
| `surface` | enum | yes | `"com"` or `"org"` |
| `type` | enum | yes | `"node"` \| `"brief"` \| `"review"` \| `"report"` \| `"visualization_of"` (org thin wrappers — see below) \| `"page"` (aggregate surface-level entries — see below) |
| `title` | string | yes | Display title for human scanning. On `visualization_of` wrappers, denormalized (copied from the canonical `com` entry). |
| `canonical_url` | string | cond. | Full URL on the live site. Required for `com` entries, org full entries, and `page` entries. Omitted on `visualization_of` wrappers (implicit via canonical). |
| `canonical_ledger_entry` | string | cond. | **Only on `visualization_of` wrappers.** Path to the canonical `com` ledger entry, relative to `verification/` (e.g. `entries/com/nodes/psp-airport.json`). |
| `last_reviewed` | string (ISO date) | yes | Date of the most recent review pass on this entry |
| `review_method` | enum | yes | `"manual"` \| `"automated"` \| `"unverified"` |
| `claims` | array | cond. | Required on entries that make factual assertions (`node`, `brief`, `review`, `report`). **Omitted** on `visualization_of` wrappers — claims live in the canonical `com` entry. |
| `connections` | array | yes | See below. May be empty. |
| `notes` | string \| null | no | Free-text overview — why this entry exists, known quirks, etc. On `visualization_of` wrappers, defaults to `null`. |

### The `"page"` type

Most entries describe a single entity (one node, one brief). A **`page`**
entry is different: it describes a surface-level page whose claims
are *aggregate* across the surface rather than tied to one entity.

The canonical use case is `entries/org/_landing.json` — the org site's
landing page makes aggregate claims (workshop counts, partner lists,
program descriptions, aggregate node counts) that belong to the page
itself, not to any single underlying node.

`page` entries use the full schema (`title`, `canonical_url`, `claims`,
`connections`) just like `node`/`brief` entries. They are rare;
scaffolding creates placeholders and a dedicated extraction session
fills in the claims later.

### Claims

Each claim is one factual assertion the content makes. Claims should
be extracted at **statement granularity**, not paragraph granularity —
"PSP handled 2.5M passengers in 2023" is one claim; the whole Key Facts
section is not.

| Field | Type | Required | Description |
|---|---|---|---|
| `claim_id` | string | yes | Short stable identifier within the entry (e.g. `passenger-volume-2023`). Alphanumeric + hyphens. |
| `claim_text` | string | yes | The assertion in plain language. Paraphrasing is OK; preserve the factual core. |
| `status` | enum | yes | `"sourced"` \| `"dated"` \| `"unverified"` \| `"broken"` (see below) |
| `sources` | array | yes | May be empty. Each source has: `url`, `title`, `publisher`, `date_published`, `date_accessed`, `type`. |
| `date_verified` | string (ISO date) \| null | yes | When this claim was last verified against a source. `null` if `status` is `unverified` or `broken`. |

#### Claim status — definitions with examples

- **`sourced`** — The claim is backed by at least one source in the
  `sources` array, the source was checked on or after `date_verified`,
  and the source still supports the claim.
  *Example:* "PSP handles 10+ carriers" with a source link to
  flypsp.com/carriers accessed 2026-04-19 showing the carrier list.

- **`dated`** — The claim was sourced at some point but has a
  time-sensitive component (a year-over-year count, a "currently"
  statement, a development status) and enough time has passed that
  the source may no longer reflect reality. Requires re-verification
  before it can move back to `sourced`.
  *Example:* "PSP handled approximately 2.5 million passengers in
  2023" — sourced to airport reporting, but 2024 and 2025 data now
  exist; the claim is true as written but flags a stale snapshot of
  the world.

- **`unverified`** — The claim exists in content but no source has
  been attached yet. Default state for every claim at scaffold time.
  *Example:* "The airport is owned and operated by the City of Palm
  Springs" — true, but no source attached yet. Moves to `sourced`
  when a citation is added.

- **`broken`** — The claim has been actively checked against a source
  and the source contradicts it, or the source the claim relied on
  has disappeared. Requires content correction.
  *Example:* If a brief claims "CVEP announced a new AI incubator in
  March 2025" but the original source retracted or never existed, the
  claim is `broken`.

#### Source types

- **`news`** — News reporting (Desert Sun, Palm Springs Life, etc.)
- **`primary`** — The entity's own website, filings, or official
  documents (City of Palm Springs capital budget PDF, PSP's own
  route map)
- **`interview`** — Notes from direct conversation with a named
  source. Include publisher as the interviewer, date as the
  interview date.
- **`government`** — Regulatory, permitting, or agency records (FAA,
  Riverside County, state filings)
- **`self_reported`** — Claims made by AICV itself (e.g. "nearly 30
  AI workshops delivered") — lower confidence than external sources,
  but sourced to the operator with a named witness (Sat Singh).
- **`dataset`** — Structured data (census, BLS, MLS, labor market
  data, aviation statistics)

### Connections

Each connection describes a typed edge between this entry and another.
Connections are **declared per entry**, not globally — if A says it
connects to B, A's ledger holds the edge. The reverse may or may not
exist in B's ledger. A future reconciliation pass will detect missing
reciprocal edges.

| Field | Type | Required | Description |
|---|---|---|---|
| `target_id` | string | yes | Slug of the connected entry (e.g. `cotino`) |
| `target_surface` | enum | yes | `"com"` or `"org"` |
| `target_type` | enum \| null | yes | Type of the target entry. Allowed non-null values: `"node"` \| `"brief"` \| `"report"` \| `"review"` \| `"page"` \| `"visualization_of"`. `null` is a known v1.1 limitation: Shape A wrapper connections (`located_in`, `part_of`) target zone and subcategory classifications that are not ledger entries under v1.1. A dedicated taxonomy-model session (see `verification/AUDIT-2026-04-20-taxonomy.md`) will resolve whether these become first-class ledger entry types in a future SCHEMA revision, at which point `target_type` becomes required non-null. |
| `direction` | enum | yes | `"outgoing"` \| `"incoming"` \| `"bidirectional"` |
| `type` | string | yes | Recommended vocabulary (below), or any string. Track free-text types as candidates for promotion. |
| `notes` | string | no | Free-text context — why this connection exists |

#### Recommended connection vocabulary

- **`part_of`** — Structural containment. `psp-airport` is `part_of`
  `aviation-gateway`; `cotino` is `part_of` `rancho-mirage`.
- **`located_in`** — Geographic placement in a city / zone.
- **`related_to`** — Generic semantic association when nothing more
  specific fits. Try to avoid — prefer `references` or `part_of`.
- **`references`** — This entry mentions / cites the target in prose.
  Default for extracted Markdown links.
- **`routes_to`** — Node Zero's routing semantics. A query like
  "where should AI startups locate" `routes_to` `cook-street-university-row`.
- **`supersedes`** — This entry replaces the target. E.g. a new
  development-pipeline node `supersedes` a retired one.

Free-text types are legal. Track them; promote popular patterns into
the vocabulary in future schema versions.

---

## Annotated example — `entries/com/nodes/psp-airport.json`

```json
{
  "schema_version": "v1.1",
  "id": "psp-airport",
  "surface": "com",
  "type": "node",
  "title": "Palm Springs International Airport",
  "canonical_url": "https://aicoachellavalley.com/nodes/psp-airport/",
  "last_reviewed": "2026-04-19",
  "review_method": "automated",
  "claims": [
    {
      "claim_id": "iata-code",
      "claim_text": "The airport's IATA code is PSP.",
      "status": "unverified",
      "sources": [],
      "date_verified": null
    },
    {
      "claim_id": "operator-city-of-palm-springs",
      "claim_text": "The airport is owned and operated by the City of Palm Springs.",
      "status": "unverified",
      "sources": [],
      "date_verified": null
    },
    {
      "claim_id": "carrier-count",
      "claim_text": "PSP serves over 10 commercial carriers including American, Delta, Southwest, United, Alaska, and WestJet.",
      "status": "unverified",
      "sources": [],
      "date_verified": null
    },
    {
      "claim_id": "passenger-volume-2023",
      "claim_text": "The airport handled approximately 2.5 million passengers in 2023.",
      "status": "unverified",
      "sources": [],
      "date_verified": null
    },
    {
      "claim_id": "terminal-modernization-ongoing",
      "claim_text": "A terminal modernization program is ongoing, with capital improvements funded in part through federal infrastructure allocations.",
      "status": "unverified",
      "sources": [],
      "date_verified": null
    }
  ],
  "connections": [
    {
      "target_id": "aviation-gateway",
      "target_surface": "com",
      "target_type": "node",
      "direction": "outgoing",
      "type": "part_of",
      "notes": "Frontmatter: related.type=supports → aviation-gateway"
    },
    {
      "target_id": "coachella-valley-intelligence-index",
      "target_surface": "com",
      "target_type": "node",
      "direction": "outgoing",
      "type": "references",
      "notes": "Related Nodes section"
    },
    {
      "target_id": "coachella-festival",
      "target_surface": "com",
      "target_type": "node",
      "direction": "outgoing",
      "type": "references",
      "notes": "Related Nodes section"
    },
    {
      "target_id": "cotino",
      "target_surface": "com",
      "target_type": "node",
      "direction": "outgoing",
      "type": "references",
      "notes": "Related Nodes section"
    },
    {
      "target_id": "sensei-porcupine-creek",
      "target_surface": "com",
      "target_type": "node",
      "direction": "outgoing",
      "type": "references",
      "notes": "Related Nodes section"
    },
    {
      "target_id": "gardens-on-el-paseo",
      "target_surface": "com",
      "target_type": "node",
      "direction": "outgoing",
      "type": "references",
      "notes": "Related Nodes section"
    }
  ],
  "notes": "Scaffolded 2026-04-19 from frontmatter + body extraction. Claims extracted from 'What It Is' and 'Key Facts' sections. Verification pass pending."
}
```

**What this example shows:**

1. Five claims were extracted from the body — each a single factual
   assertion, not a paragraph. `claim_id` values are descriptive and
   stable; they won't change as claim text is refined.
2. All five claims start `unverified` with empty `sources[]`. The
   ledger is scaffolded before the verification pass runs.
3. Connections were extracted from two places: the `related` field
   in frontmatter (→ `aviation-gateway`, typed `part_of` because the
   source relation is `supports`) and the body's Related Nodes section
   (→ 5 targets, typed `references` by default).
4. `review_method: "automated"` because the scaffold script generated
   this — no human has reviewed yet. First manual pass flips this to
   `"manual"` and bumps `last_reviewed`.
5. The `notes` field on connections preserves the extraction
   provenance — useful when auditing where an edge came from.

---

## Org entries — two shapes

Org entries are generated from `org/index.html`'s static graph
structures: `VW_ORDER` (the 28 valley-wide anchors) and the slugs
extracted from `ZONE_MAP` keys (zone/slug pairs across all zones).
Every slug in those two sources gets a ledger entry. Shape is
selected by checking whether a corresponding
`com/src/content/nodes/<slug>.mdx` file exists. Note: the org/ graph
also currently fetches `docs.json` from a retired Mintlify repo at
runtime, which causes drift between what the graph renders and what
com/ actually contains. That's a separate architectural issue
documented for Phase 6 investigation; the scaffold reads the static
structures directly, not the runtime fetch.

### Shape A — thin navigation wrapper (`type: "visualization_of"`)

Used when the slug corresponds to an existing `com/` node (check:
does `com/src/content/nodes/<slug>.mdx` exist?). This is the common
case — most graph nodes visualize a real `com/` node.

The wrapper holds only what is org-specific: graph wiring extracted
from `ZONE_MAP`, `SUB_MAP`, and any `STATIC_LINKS` structures in
`index.html`. Factual claims about the underlying entity live in the
canonical `com/` ledger entry and are not duplicated here.

Required fields:

- `schema_version`
- `id` (matches `com/` slug exactly)
- `surface: "org"`
- `type: "visualization_of"`
- `title` — denormalized from the canonical `com` entry, for quick
  human scanning of the ledger without hopping files
- `canonical_ledger_entry` — path to the canonical `com/` entry file,
  relative to `verification/` (e.g. `entries/com/nodes/psp-airport.json`)
- `connections` — graph edges from org's visualization layer
- `last_reviewed`
- `review_method`

Omitted fields: `canonical_url`, `claims`. These are implicit through
`canonical_ledger_entry`. `notes` defaults to `null`.

### Shape B — full entry

Used when a slug exists in org's graph but has no `com/` backing —
the entity is asserted only by the visualization. This should be
**rare**. Every Shape B entry emitted during scaffold is flagged for
review: either the slug needs a `com/` node written to back it, or
the graph reference should be removed.

Shape B uses the same schema as a `com/` node entry (`type: "node"`,
full claims array, etc.) but with `surface: "org"`.

### Rationale

Org is a rendering of com, not an independent knowledge base. Treating
it as such means:

- One canonical source per claim — no drift between surfaces
- Verification effort scales with unique content, not with the number
  of surfaces that render it
- Shape B's rarity becomes a useful signal — it tells us which graph
  nodes are unmoored from the content layer

---

## Second annotated example — `entries/org/psp-airport.json`

The `psp-airport` slug appears in org's `ZONE_MAP` under the key
`palm-springs/psp-airport`. A `com/src/content/nodes/psp-airport.mdx`
file exists, so this entry takes **Shape A**.

```json
{
  "schema_version": "v1.1",
  "id": "psp-airport",
  "surface": "org",
  "type": "visualization_of",
  "title": "Palm Springs International Airport",
  "canonical_ledger_entry": "entries/com/nodes/psp-airport.json",
  "last_reviewed": "2026-04-19",
  "review_method": "automated",
  "connections": [
    {
      "target_id": "palm-springs",
      "target_surface": "org",
      "target_type": null,
      "direction": "outgoing",
      "type": "located_in",
      "notes": "ZONE_MAP: palm-springs/psp-airport → palm-springs"
    },
    {
      "target_id": "economic",
      "target_surface": "org",
      "target_type": null,
      "direction": "outgoing",
      "type": "part_of",
      "notes": "SUB_MAP: psp-airport → economic"
    }
  ],
  "notes": null
}
```

**What this example shows:**

1. No `claims` array — all factual claims about PSP live in
   `entries/com/nodes/psp-airport.json` (the Shape A wrapper points
   there via `canonical_ledger_entry`).
2. `title` is denormalized from the canonical entry for quick
   scanning; `canonical_url` is omitted (implicit via the canonical
   ledger entry).
3. No connection to the `com` canonical — the cross-surface
   relationship is encoded at the entry level through
   `canonical_ledger_entry`, not duplicated as an edge. Connections
   are reserved for **graph** relationships within a surface.
4. Two connections, both graph edges:
   - Geographic placement in a zone (`located_in palm-springs`)
     sourced from `ZONE_MAP`
   - Subcategory membership (`part_of economic`) sourced from `SUB_MAP`
5. Both connections carry `target_type: null` because their targets
   (`palm-springs`, `economic`) are taxonomy references — classifying
   concepts not modeled as ledger entries under v1.1. A dedicated
   taxonomy-model session will resolve whether these become
   first-class ledger entry types; at that point `target_type`
   becomes required non-null.
6. `review_method: "automated"` and `notes: null` — no human has
   reviewed; nothing operator-specific to record yet.

A **Shape B** example would look identical in structure to the
`com/` node example above, except with `surface: "org"`. The scaffold
script will emit these only when a slug lacks a `com/` backing, and
each one gets flagged in the scaffold report for manual review.

---

## How entries get updated

The ledger is append-friendly but not append-only. Typical operations:

### Adding a source to a claim

Move `status` from `unverified` → `sourced`, push the source object
into `sources[]`, set `date_verified` to today. Example:

```json
{
  "claim_id": "passenger-volume-2023",
  "claim_text": "The airport handled approximately 2.5 million passengers in 2023.",
  "status": "sourced",
  "sources": [
    {
      "url": "https://www.flypsp.com/about/statistics",
      "title": "PSP Passenger Statistics",
      "publisher": "City of Palm Springs Department of Aviation",
      "date_published": "2024-02-15",
      "date_accessed": "2026-04-19",
      "type": "primary"
    }
  ],
  "date_verified": "2026-04-19"
}
```

Then at the entry level: bump `last_reviewed` to today, set
`review_method` to `"manual"` if a human did the sourcing.

### Marking a claim as dated

When a time-sensitive claim is still technically true but no longer
reflects current reality, flip `status` → `"dated"` and leave the
source in place. The `date_verified` field now serves as a staleness
signal. Example: the 2023 passenger count claim moves to `dated`
when 2024 data becomes public.

### Marking a claim as broken

When a source contradicts the claim or the source disappears, flip
`status` → `"broken"`, leave the source for audit trail, and open
a content correction task. The content file should be edited and
the claim re-extracted in the next scaffold pass.

### Adding a connection

Push a new object into `connections[]`. Prefer the recommended
vocabulary; if a free-text type is needed, note it — we'll review
candidates for promotion.

### Updating `last_reviewed`

Bumped any time an entry is touched for review purposes. Not bumped
for trivial edits (fixing a typo in `claim_text`). A significant
review pass — checking the entry against current content, adding or
validating sources — bumps this.

### Removing an entry

When the underlying content file is deleted, remove the ledger entry
too. Do not leave stubs. A scaffold-diff mode (future work) will
detect this automatically.

---

## Scaffold vs verification

This document distinguishes two phases:

- **Scaffold** — One-shot script run over the content tree.
  Generates one entry per content file, populates claims at coarse
  granularity with `status: "unverified"`, extracts connections from
  frontmatter and body. No judgment calls, no sources. This phase
  establishes the structure.

- **Verification** — Human (or LLM-assisted human) pass over each
  entry. Refines claims, attaches sources, flips statuses. This is
  where the ledger earns its name. Scheduled as Layer 2 work across
  future sessions.

The scaffold is load-bearing because it creates the denominator —
without it, we can't answer "what fraction of claims are sourced?"

---

## Known limitations of v1.1

- **Coarse claim extraction.** The scaffold emits roughly one claim
  per notable sentence in the "What It Is" / "Key Facts" sections.
  Future versions may split compound claims, extract tables as
  per-row claims, or skip boilerplate.
- **No reciprocity check.** If A declares a connection to B but B
  doesn't declare one back, v1 doesn't flag it. A reconciliation
  script is planned.
- **No differential scaffold.** Re-running the scaffold overwrites
  entries. A differential mode (preserve manual edits, update only
  unverified claims and auto-extracted connections) is planned.
- **Org Shape B is under-specified.** Shape B reuses the `com` node
  schema but we haven't exercised it yet. The scaffold run will
  surface which slugs need Shape B treatment; we'll refine on
  contact.
- **No verification SLA.** No automated alert when `dated` claims
  age past a threshold. Candidate for future tooling.
- **Claim quality depends on source prose quality.** Well-structured
  content (explicit section headers, single-assertion sentences,
  factual Key Facts lists) produces clean claim extraction; looser
  prose produces looser claims. Layer 2 verification normalizes
  what the scaffold emits. Scaffold completion does **not** imply
  query-ready state — it establishes the structure that verification
  fills in.
- **`target_type: null` on taxonomy-reference connections.**
  Shape A wrapper connections (`located_in`, `part_of`) target
  zones and subcategories that are not ledger entries under v1.1.
  These connections carry `target_type: null` as a documented
  placeholder until a dedicated taxonomy-model session resolves
  whether zones and subcategories become first-class ledger entry
  types. See `verification/AUDIT-2026-04-20-taxonomy.md` for the
  corpus audit that surfaced this limitation.

---

## Revisions

**v1 (2026-04-19):** Initial schema.

**v1.1 (2026-04-20):** Adds `target_type` to connections,
disambiguating cross-type id collisions surfaced by scaffold
implementation (review entries share ids with subject nodes).
Shape A wrapper connections to taxonomy references (zones,
subcategories) carry `target_type: null`, a known limitation
awaiting a dedicated taxonomy-model session (see
`verification/AUDIT-2026-04-20-taxonomy.md`).

---

*Schema v1.1 · authored 2026-04-20 · supersedes: v1*
