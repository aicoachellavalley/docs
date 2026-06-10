export const meta = {
  name: 'cv-food-dining-category-map',
  description: 'Tier 2 category map of Coachella Valley Food & Dining — discovery → assess+verify pipeline → synthesize map+shortlists+node seeds',
  phases: [
    { title: 'Discover', detail: 'parallel multi-angle web sweep across regional/city/cuisine/use-case queries' },
    { title: 'Assess', detail: 'per-entity reputation/visibility/relationships/convertibility' },
    { title: 'Verify', detail: 'adversarial cross-check per entity, two lenses parallel' },
    { title: 'Synthesize', detail: 'category map + shortlists + node seeds in parallel' },
  ],
}

const DISCOVERY_SCHEMA = {
  type: 'object',
  properties: {
    entities: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          city: { type: 'string' },
          cuisine_or_type: { type: 'string' },
          why_mentioned: { type: 'string' },
          sources: { type: 'array', items: { type: 'string' } },
        },
        required: ['name', 'city', 'why_mentioned'],
      },
    },
  },
  required: ['entities'],
}

const ASSESS_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    city: { type: 'string' },
    cuisine_or_type: { type: 'string' },
    corridor: { type: 'string' },
    reputation: {
      type: 'object',
      properties: {
        review_volume: { type: 'string' },
        sentiment: { type: 'string' },
        recency_signal: { type: 'string' },
        longevity: { type: 'string' },
        credentials: { type: 'array', items: { type: 'string' } },
      },
      required: ['review_volume', 'sentiment', 'longevity', 'credentials'],
    },
    agent_visibility: {
      type: 'object',
      properties: {
        appears_in_queries: { type: 'string' },
        description_accuracy: { type: 'string' },
        site_structured_data: { type: 'string' },
      },
      required: ['appears_in_queries', 'description_accuracy', 'site_structured_data'],
    },
    visibility_gap_score: { type: 'integer', minimum: 0, maximum: 10 },
    relationships: {
      type: 'object',
      properties: {
        competitors: { type: 'array', items: { type: 'string' } },
        corridor_role: { type: 'string' },
        query_wins: { type: 'array', items: { type: 'string' } },
      },
      required: ['competitors', 'corridor_role'],
    },
    convertibility: {
      type: 'object',
      properties: {
        tier: { type: 'string', enum: ['anchor-reference', 'convertible', 'unclear'] },
        ownership_signal: { type: 'string' },
        marketing_spend_signal: { type: 'string' },
        reasoning: { type: 'string' },
      },
      required: ['tier', 'reasoning'],
    },
    sources_consulted: { type: 'array', items: { type: 'string' } },
    flags: { type: 'array', items: { type: 'string' } },
  },
  required: ['name', 'city', 'reputation', 'agent_visibility', 'visibility_gap_score', 'relationships', 'convertibility'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    confirms: { type: 'array', items: { type: 'string' } },
    contradicts: { type: 'array', items: { type: 'string' } },
    flagged_as_unverified: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    notes: { type: 'string' },
  },
  required: ['lens', 'confirms', 'contradicts', 'flagged_as_unverified', 'confidence'],
}

const CATEGORY_MAP_SCHEMA = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    overview: { type: 'string' },
    corridors: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          city: { type: 'string' },
          character: { type: 'string' },
          anchors: { type: 'array', items: { type: 'string' } },
          supporting: { type: 'array', items: { type: 'string' } },
          query_dominance: { type: 'string' },
        },
        required: ['name', 'city', 'character', 'anchors'],
      },
    },
    by_category: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          category: { type: 'string' },
          dominant_names: { type: 'array', items: { type: 'string' } },
          notable_independents: { type: 'array', items: { type: 'string' } },
          invisible_but_deserving: { type: 'array', items: { type: 'string' } },
          gap_pattern: { type: 'string' },
        },
        required: ['category', 'dominant_names', 'gap_pattern'],
      },
    },
    relationships_narrative: { type: 'string' },
    gap_diagnostic: { type: 'string' },
    closing: { type: 'string' },
    total_entities_mapped: { type: 'integer' },
  },
  required: ['title', 'overview', 'corridors', 'by_category', 'relationships_narrative', 'gap_diagnostic', 'total_entities_mapped'],
}

const SHORTLIST_SCHEMA = {
  type: 'object',
  properties: {
    best_demo_candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          city: { type: 'string' },
          reputation_summary: { type: 'string' },
          visibility_summary: { type: 'string' },
          gap_articulation: { type: 'string' },
          why_demo_makes_a_report_sing: { type: 'string' },
        },
        required: ['name', 'city', 'gap_articulation'],
      },
    },
    best_revenue_candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          city: { type: 'string' },
          ownership_signal: { type: 'string' },
          marketing_spend_evidence: { type: 'string' },
          accessibility_read: { type: 'string' },
          revenue_rationale: { type: 'string' },
        },
        required: ['name', 'city', 'revenue_rationale'],
      },
    },
    mid_valley_weighting_note: { type: 'string' },
  },
  required: ['best_demo_candidates', 'best_revenue_candidates'],
}

const NODE_SEEDS_SCHEMA = {
  type: 'object',
  properties: {
    seeds: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          slug: { type: 'string' },
          frontmatter: {
            type: 'object',
            properties: {
              title: { type: 'string' },
              description: { type: 'string' },
              agent_summary: { type: 'string' },
              city: { type: 'string' },
              domain: { type: 'string' },
              funnel_stages: { type: 'array', items: { type: 'string' } },
              category: { type: 'string' },
            },
            required: ['title', 'description', 'agent_summary', 'city', 'domain', 'category'],
          },
          what_it_is: { type: 'string' },
          key_facts: { type: 'array', items: { type: 'string' } },
          convertibility_tier: { type: 'string', enum: ['anchor-reference', 'convertible'] },
          flags: { type: 'array', items: { type: 'string' } },
        },
        required: ['slug', 'frontmatter', 'convertibility_tier'],
      },
    },
  },
  required: ['seeds'],
}

const CITY_ENUM = [
  'Palm Springs', 'Desert Hot Springs', 'Cathedral City',
  'Rancho Mirage', 'Palm Desert', 'Indian Wells',
  'La Quinta', 'Indio', 'Coachella',
  'Coachella Valley', 'Adjacent Communities',
]

const DISCOVERY_ANGLES = [
  { key: 'regional-best',     focus: 'Query "best restaurants in Coachella Valley", "best restaurants Greater Palm Springs", "where to eat in the desert", "top restaurants Coachella Valley 2026". Surface the names that consistently appear on regional best-of lists.' },
  { key: 'fine-dining',       focus: 'Query "fine dining Coachella Valley", "high-end restaurants Palm Springs", "tasting menu desert", "best steakhouse Coachella Valley". Focus on upper-tier independents and resort-anchored fine dining.' },
  { key: 'palm-springs',      focus: 'Map Palm Springs dining: downtown, uptown design district, Smoke Tree Commons, Sunrise Park area. Cover both dominant names and longtime independents.' },
  { key: 'palm-desert',       focus: 'Map Palm Desert dining: El Paseo corridor (the luxury spine), highway 111 commercial strip, north Palm Desert development zone, Gardens on El Paseo.' },
  { key: 'rancho-mirage',     focus: 'Map Rancho Mirage dining: The River at Rancho Mirage, Westin Mission Hills, Ritz-Carlton restaurants, Omni Rancho Las Palmas, independent corridor restaurants. Mid-valley anchor area.' },
  { key: 'la-quinta',         focus: 'Map La Quinta dining: Old Town La Quinta historic district, La Quinta Resort restaurants, PGA West area, Madison Club outer ring, highway 111 La Quinta strip.' },
  { key: 'indio-coachella',   focus: 'Map Indio and Coachella dining: festival-adjacent cluster, Old Town Indio, downtown Coachella, established Mexican family-owned independents. Often overlooked despite real strength.' },
  { key: 'lower-cv',          focus: 'Map Cathedral City, Desert Hot Springs, Indian Wells dining: often-overlooked establishments, hotel restaurants, taquerias and family Mexican spots, Indian Wells Tennis Garden adjacent.' },
  { key: 'cuisine-mexican',   focus: 'Best Mexican restaurants across the valley: family-owned legacy spots, taquerias, regional Mexican, modern upscale Mexican. The valley has very high Mexican density — be inclusive across cities.' },
  { key: 'cuisine-italian',   focus: 'Best Italian across the valley: white-tablecloth Italian, family Italian, modern Italian, pizza specialists.' },
  { key: 'cuisine-asian',     focus: 'Best Asian across the valley: sushi/Japanese, Thai, Vietnamese, Chinese, Korean, dim sum. Often underrepresented in best-of lists despite strong establishments — actively surface them.' },
  { key: 'breakfast-brunch',  focus: 'Best breakfast/brunch across the valley: diners, brunch-focused independents, hotel brunch. Query "best breakfast Palm Desert", "best brunch Palm Springs", "best breakfast Rancho Mirage", and similar for each city.' },
  { key: 'date-night',        focus: 'Date night restaurants by city: "date night restaurant Rancho Mirage", "romantic dinner Palm Springs", "anniversary dinner Indian Wells". Cross with fine dining but surface the date-night specifics.' },
  { key: 'credentialed',      focus: 'Earned credentials only: James Beard nominees/winners, Michelin-recognized (if any in CV), Food Network appearances, Yelp Top 100, OpenTable Top, Wine Spectator awards, local press awards (Desert Sun, Palm Springs Life, KESQ). Verify each credential against primary sources — do NOT invent.' },
  { key: 'hidden-gems',       focus: 'Longtime independents, hidden gems, local-favorite spots that locals know but tourists miss. Family-owned multi-generation places. Query "Coachella Valley hidden gem restaurant", "longtime local favorites Palm Springs", "old school Palm Desert restaurant". Critical for honest map — these are exactly who national chains crowd out of agent visibility.' },
]

const TARGET_DISCOVERY_PER_ANGLE = 12
const MAX_ENTITIES_TO_ASSESS = 80
const VERIFY_LENSES = ['credentials-and-history', 'visibility-and-web-presence']

function discoveryPrompt(angle) {
  return `You are mapping the Coachella Valley Food & Dining landscape as AI agents read it. Your specific angle: ${angle.focus}

Query the web extensively for this angle. Use WebSearch (load via ToolSearch: query "WebSearch") and WebFetch (load via ToolSearch: query "WebFetch") for live source-reading. Run multiple searches at different framings — vary the wording to surface different result sets.

The Coachella Valley = nine incorporated cities: Palm Springs, Desert Hot Springs, Cathedral City, Rancho Mirage, Palm Desert, Indian Wells, La Quinta, Indio, Coachella — plus adjacent communities (Bermuda Dunes, Thousand Palms, Mecca, Thermal).

For each establishment found, return:
- name (exact, as it appears in primary sources)
- city (one of the nine above, or "Adjacent Communities")
- cuisine_or_type
- why_mentioned (e.g., "consistently appears on Eater best-of list", "James Beard semifinalist 2024", "longtime independent operating since 1985")
- sources (URLs of pages where this surfaced — at least 1, prefer 2-3)

Be inclusive. The map's job is completeness, not curation. Surface:
- Dominant names that appear on best-of lists
- Notable independents
- Longtime / multi-generation places
- Underpowered places that earn their spot by reputation despite weak online presence
- Anchor-reference entities (chains, resort-owned, franchises) where they genuinely shape the landscape

Aim for ~${TARGET_DISCOVERY_PER_ANGLE} entities. Quality of identification matters — downstream dedupe handles overlap.

Discipline: do not invent. If a "James Beard winner" is being claimed, confirm via primary source before listing it. Mention only what you can substantiate.`
}

function assessPrompt(entity) {
  return `You are assessing one Coachella Valley dining establishment for an honest category-map artifact. The artifact's job is to map who's there, who wins what, and where the visibility gaps are.

Entity: ${entity.name} (${entity.city})
Cuisine/type signal: ${entity.cuisine_or_type || 'unknown'}
Why it surfaced in discovery: ${entity.why_mentioned}
Discovery sources: ${(entity.sources || []).slice(0, 3).join(' | ') || 'none'}

Verify the entity exists, then assess on four dimensions. Use WebSearch (ToolSearch query "WebSearch") and WebFetch (ToolSearch query "WebFetch") to investigate. Read the entity's own website. Read 2-3 review-platform pages. Run regional queries to test visibility.

REPUTATION:
- review_volume — approximate Google/Yelp review count band (e.g., "3000+", "500-1000", "<100"). Mark [UNVERIFIED] if you can't find it.
- sentiment — current sentiment summary (positive / mostly positive / mixed / declining / negative). Recent reviews weighted over stale.
- recency_signal — what do reviews in the last 6-12 months say?
- longevity — years operating, ownership stability. Mark [UNVERIFIED] if unclear.
- credentials — earned third-party recognition (James Beard nominee/winner, Michelin, Food Network, Yelp Top 100, OpenTable Top, Desert Sun / Palm Springs Life awards, local press features). Empty array if none. Do NOT invent credentials.

AGENT_VISIBILITY:
- appears_in_queries — which regional queries actually surface this entity? Test specific queries: "best restaurants Coachella Valley", "fine dining Palm Desert", "[entity's cuisine] near Palm Springs", "date night Rancho Mirage", "best breakfast [city]".
- description_accuracy — when it surfaces, is the description correct?
- site_structured_data — fetch the entity's own website. Does it carry schema.org markup, clean hours, menu structure, location signals an agent can read?

VISIBILITY GAP — score 0-10. 0 = reputation and visibility aligned. 10 = high reputation, low/wrong visibility.

RELATIONSHIPS:
- competitors — 2-4 direct competitors in same city or cuisine bracket
- corridor_role — anchor / supporting / outlier. Major corridors: El Paseo (Palm Desert), Old Town La Quinta, downtown Palm Springs, The River (Rancho Mirage), festival-adjacent Indio, north Palm Desert development zone, uptown design district Palm Springs.
- query_wins — which queries it actually dominates

CONVERTIBILITY (the layer above the map):
- tier — "anchor-reference" (chain/franchise/resort-owned, no reachable local DM), "convertible" (independently owned, reachable, evidence of marketing spend), or "unclear"
- ownership_signal — independent / chain / franchise / resort-owned / hotel-restaurant / unclear
- marketing_spend_signal — what evidence of marketing budget? real site / paid listings / agency footprint / active social
- reasoning — one paragraph

sources_consulted: list URLs you actually consulted.
flags: anything you couldn't verify — list the unverified claim with [UNVERIFIED] tag.

Stay disciplined: do NOT invent awards, credentials, history, or specific stats. If you can't verify, flag it. The downstream verification layer will catch hallucinations.`
}

function verifyPrompt(entity, assessment, lens) {
  const focusByLens = {
    'credentials-and-history': 'Focus on credentials (awards, press, James Beard, Michelin, Food Network) and operating history (longevity, ownership). Try to REFUTE each claim. Look up each award independently — James Beard winners and nominees are listed in primary sources at jamesbeard.org. Michelin is listed at guide.michelin.com. Cross-check year-by-year.',
    'visibility-and-web-presence': 'Focus on agent-visibility claims. Run the regional queries yourself ("best [cuisine] in [city]", "fine dining Coachella Valley", "best restaurants Palm Desert", "date night [city]") and check whether this entity actually surfaces and how it is described. Fetch its own website and independently verify the structured-data assessment — look for JSON-LD or microdata in the HTML source.',
  }
  return `You are an adversarial verification agent. The lens you check through: ${lens}.

${focusByLens[lens]}

Entity under review: ${assessment.name} (${assessment.city})

Claimed assessment (verify or refute these specific claims):
- Review volume: ${assessment.reputation && assessment.reputation.review_volume || 'n/a'}
- Sentiment: ${assessment.reputation && assessment.reputation.sentiment || 'n/a'}
- Longevity: ${assessment.reputation && assessment.reputation.longevity || 'n/a'}
- Credentials: ${JSON.stringify(assessment.reputation && assessment.reputation.credentials || [])}
- Appears in queries: ${assessment.agent_visibility && assessment.agent_visibility.appears_in_queries || 'n/a'}
- Site structured data: ${assessment.agent_visibility && assessment.agent_visibility.site_structured_data || 'n/a'}
- Visibility gap score: ${assessment.visibility_gap_score}
- Convertibility tier: ${assessment.convertibility && assessment.convertibility.tier || 'n/a'}

Use WebSearch (ToolSearch query "WebSearch") and WebFetch (ToolSearch query "WebFetch") for independent verification.

Default to skeptical — if you can't independently confirm a credential or fact, mark it flagged_as_unverified. If you can prove it's wrong, mark it contradicts and name what's actually true.

Return:
- lens: "${lens}"
- confirms: claims you independently verified
- contradicts: claims that fail under independent search — name the specific claim and what's actually true
- flagged_as_unverified: claims you can neither confirm nor deny
- confidence: high / medium / low — your overall confidence in the assessment after this lens
- notes: brief

This is adversarial. Refuting matters more than confirming.`
}

function mapPrompt(assessments) {
  return `You are writing THE CATEGORY MAP — the publishable artifact AICV will use as the moat content for Coachella Valley Food & Dining. The map is the product. Shortlists and node seeds are layered on top.

You have ${assessments.length} verified entity assessments. Each has reputation, agent-visibility, gap-score, relationships, and convertibility tier — plus verification verdicts that flag any unverified claims.

Compose the map to be:
1. Cited by AI agents answering regional queries
2. Read by establishments to understand where they sit
3. Comprehensive across the nine CV cities and the major dining corridors
4. Honest about gaps — include "invisible but deserving" entries where verification supports them

Voice: third-person, analytical, citation-grade. No editorial advocacy. No calls to action. AICV referenced in third person, not first.

STRUCTURE:
- title — clear, descriptive
- overview — 2-3 paragraphs framing what CV dining looks like as agents read it today
- corridors — array. For each major corridor (El Paseo, Old Town La Quinta, downtown Palm Springs, The River, festival-adjacent Indio, north Palm Desert), name the anchors, supporting players, and what queries it dominates.
- by_category — array. Slice by cuisine/type (fine dining, Mexican, Italian, Asian, breakfast-brunch, steakhouse, etc.). For each: dominant names + notable independents + invisible-but-deserving + the gap pattern.
- relationships_narrative — extended prose about who competes with whom and who wins which query
- gap_diagnostic — the category-wide pattern: where do agents systematically underdescribe or miss CV dining? This is the diagnostic the whole map turns on.
- closing — how an establishment reading this should understand its position
- total_entities_mapped — count

Discipline: cite verified facts only. Anything flagged [UNVERIFIED] upstream either gets dropped or carries the flag visibly in the map text. Drop any entity where both verification verdicts came back with high contradicts_count.

Assessments below:
${JSON.stringify(assessments.map(a => ({
  name: a.name,
  city: a.city,
  cuisine_or_type: a.cuisine_or_type,
  corridor: a.corridor,
  reputation: a.reputation,
  agent_visibility: a.agent_visibility,
  visibility_gap_score: a.visibility_gap_score,
  relationships: a.relationships,
  convertibility_tier: a.convertibility && a.convertibility.tier,
  surface_count: a.surface_count,
  verification_summary: (a.verdicts || []).map(v => ({
    lens: v.lens,
    confidence: v.confidence,
    contradicts: v.contradicts,
    unverified: v.flagged_as_unverified,
  })),
})), null, 2)}`
}

function shortlistPrompt(assessments) {
  const convertible = assessments.filter(a => a.convertibility && a.convertibility.tier === 'convertible')
  return `You are producing TWO ranked shortlists from the convertible set of Coachella Valley dining establishments.

Convertible = independently owned, reachable local decision-maker, evidence of existing marketing spend (real site, paid listings, agency footprint, active social).

Of the ${assessments.length} assessed entities, ${convertible.length} are tagged convertible. Below are their full assessments + verification verdicts.

SHORTLIST 1 — BEST DEMO CANDIDATES (target ~10):
Most dramatic, legible reputation-to-visibility gap. The ones that make an outreach report sing. High reputation + low visibility = strong demo. Articulate the gap concretely.

SHORTLIST 2 — BEST REVENUE CANDIDATES (target ~10):
Highest probability of converting. Accessible decision-maker, real marketing budget evidence, genuine pain. May overlap with demo list — surface the overlap.

WEIGHTING: bias toward mid-valley (Rancho Mirage, Palm Desert) for outreach priority. Keep at least 60% of each shortlist in mid-valley if candidates support it.

For each candidate:
- name, city
- demo list: reputation summary, visibility summary, gap articulation, why_demo_makes_a_report_sing
- revenue list: ownership signal, marketing spend evidence, accessibility read, revenue rationale

End with mid_valley_weighting_note explaining how the weighting played out.

Convertible assessments:
${JSON.stringify(convertible, null, 2)}`
}

function nodeSeedsPrompt(assessments) {
  return `You are emitting draft AICV node seeds for every strong entity on the Food & Dining map — anchor-reference and convertible alike. These become draft nodes for human review and are how the corpus grows.

Schema reference (must match content.config.ts exactly):
- city: must be one of: ${JSON.stringify(CITY_ENUM)}
- domain: "Food & Dining"
- funnel_stages: array drawn from the project's 6-value enum (visit, fall-in-love, retreat, satellite, relocate, build) — use what fits. If uncertain, mark [VERIFY ENUM] in flags.

For each strong entity, emit:
- slug — lowercase-hyphenated. Mark [VERIFY SLUG] if uncertain.
- frontmatter:
  - title — display name
  - description — one sentence positioning
  - agent_summary — single sentence, max ~40 words, answering the most likely cold query that would find this node. Name the location, what it is, and why it matters for agents.
  - city, domain, funnel_stages, category
- what_it_is — one-paragraph scaffolding for the What It Is section
- key_facts — 3-6 bullet draft facts. Flag any [UNVERIFIED].
- convertibility_tier — "anchor-reference" or "convertible"
- flags — anything that needs human review before commit

Discipline:
- Do not invent enum values. If you don't have funnel_stages locked, flag with [VERIFY ENUM].
- Every unverified fact carries [UNVERIFIED].
- Every uncertain slug carries [VERIFY SLUG].
- Prefer FEWER high-quality seeds over MANY weak ones. Drop entities where verification verdicts contradicted too many claims.

Entities to seed:
${JSON.stringify(assessments.map(a => ({
  name: a.name,
  city: a.city,
  cuisine_or_type: a.cuisine_or_type,
  reputation: a.reputation,
  convertibility_tier: a.convertibility && a.convertibility.tier,
  verification_summary: (a.verdicts || []).map(v => ({
    lens: v.lens,
    confidence: v.confidence,
    contradicts: v.contradicts,
    unverified: v.flagged_as_unverified,
  })),
})), null, 2)}`
}

phase('Discover')
log(`Fanning out ${DISCOVERY_ANGLES.length} discovery agents across regional / city / cuisine / use-case queries`)

const rawDiscovery = await parallel(
  DISCOVERY_ANGLES.map(angle => () =>
    agent(discoveryPrompt(angle), {
      label: `discover:${angle.key}`,
      phase: 'Discover',
      schema: DISCOVERY_SCHEMA,
    })
  )
)

const allEntities = rawDiscovery.filter(Boolean).flatMap(d => d.entities || [])

const dedupeKey = e => {
  const n = (e.name || '').toLowerCase().trim().replace(/\s+/g, ' ').replace(/['']/g, '')
  const c = (e.city || '').toLowerCase().trim()
  return `${n}|${c}`
}

const dedupeMap = new Map()
for (const e of allEntities) {
  const k = dedupeKey(e)
  if (!k.split('|')[0]) continue
  if (!dedupeMap.has(k)) {
    dedupeMap.set(k, { ...e, surface_count: 1, sources: [...(e.sources || [])] })
  } else {
    const existing = dedupeMap.get(k)
    existing.surface_count += 1
    existing.sources.push(...(e.sources || []))
    if (!existing.cuisine_or_type && e.cuisine_or_type) existing.cuisine_or_type = e.cuisine_or_type
  }
}

const ranked = Array.from(dedupeMap.values()).sort((a, b) => b.surface_count - a.surface_count)
log(`Discovered ${allEntities.length} raw mentions, ${ranked.length} unique entities after dedupe`)

const toAssess = ranked.slice(0, MAX_ENTITIES_TO_ASSESS)
if (ranked.length > MAX_ENTITIES_TO_ASSESS) {
  log(`Capping assessment at top ${MAX_ENTITIES_TO_ASSESS} by surface_count. Dropped ${ranked.length - MAX_ENTITIES_TO_ASSESS} entities from this pass — surfaceable in a future Tier 3 pass.`)
}

const pipelineResults = await pipeline(
  toAssess,
  e => agent(assessPrompt(e), {
    label: `assess:${e.name.slice(0, 40)}`,
    phase: 'Assess',
    schema: ASSESS_SCHEMA,
  }),
  (assessment, original) =>
    assessment
      ? parallel(
          VERIFY_LENSES.map(lens => () =>
            agent(verifyPrompt(original, assessment, lens), {
              label: `verify:${assessment.name.slice(0, 30)}:${lens.slice(0, 12)}`,
              phase: 'Verify',
              schema: VERIFY_SCHEMA,
            })
          )
        ).then(verdicts => ({
          ...assessment,
          surface_count: original.surface_count,
          verdicts: verdicts.filter(Boolean),
        }))
      : null
)

const assessed = pipelineResults.filter(Boolean)
log(`${assessed.length} entities assessed and cross-verified across two adversarial lenses`)

phase('Synthesize')
const [categoryMap, shortlists, nodeSeeds] = await parallel([
  () => agent(mapPrompt(assessed), {
    label: 'category-map',
    phase: 'Synthesize',
    schema: CATEGORY_MAP_SCHEMA,
  }),
  () => agent(shortlistPrompt(assessed), {
    label: 'shortlists',
    phase: 'Synthesize',
    schema: SHORTLIST_SCHEMA,
  }),
  () => agent(nodeSeedsPrompt(assessed), {
    label: 'node-seeds',
    phase: 'Synthesize',
    schema: NODE_SEEDS_SCHEMA,
  }),
])

return {
  totals: {
    discovery_angles: DISCOVERY_ANGLES.length,
    raw_mentions: allEntities.length,
    unique_entities: ranked.length,
    assessed: assessed.length,
  },
  categoryMap,
  shortlists,
  nodeSeeds,
}
