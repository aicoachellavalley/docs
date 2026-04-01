# IC.md — Intelligence Council Operating Manual

Read this file at the start of every Intelligence Review session.
This is the operating manual for AICV's Intelligence Council (IC) process.
It governs all three outputs: Snapshot, Intelligence Review, and Node.

---

## Session Start Protocol

1. Read STATE.md for current counts and last commit
2. Read CLAUDE.md for node schema and content rules
3. Read this file in full before beginning any review

---

## What the IC Produces

Every Intelligence Review produces exactly three outputs:

1. **The Snapshot** — public-facing HTML page at
   `~/Projects/com/snapshots/[entity-slug].html`
   Human and agent readable. Published to
   `aicoachellavalley.com/snapshots/[entity-slug]`

2. **The Intelligence Review** — private deliverable for the entity.
   Full findings, 12-month roadmap, competitive territory analysis.
   Delivered directly to the business contact. Not published publicly.

3. **The Node** — MDX file committed to the docs repo.
   Follows CLAUDE.md node schema exactly.
   Filed under the correct city folder in `nodes/`.

---

## The Three IC Queries

Every entity is scored across three dimensions. Run each as a
separate prompt through the LLM Council at llmcouncil.ai.

### Query 1 — Buyer Readiness

Measures how well the entity's documented digital presence appeals
to the target buyer: newly liquid founders, operators, and executives
deciding where to retreat, relocate, or invest. Scored 0.0–10.0.

**Prompt template:**

---
You are part of a multi-model AI intelligence council reviewing an
entity in the Coachella Valley, California for AI Coachella Valley
(AICV) — the authoritative intelligence layer for the valley's AI
economy.

IMPORTANT — SEARCH INSTRUCTION:
Before beginning your analysis, search the web to establish the full
luxury property and lifestyle ecosystem of the Coachella Valley. You
are looking for the complete picture of high-end hotels, resorts,
private clubs, golf properties, spas, restaurants, and lifestyle
destinations currently operating in the valley. Identify at least
fifteen. If you find fewer, note the gap. This context is essential
— your analysis of this entity must be calibrated against the actual
competitive density of the valley, not just the properties you
already know.

If you do not have real-time web search capability, use your existing
training knowledge and the following known Coachella Valley luxury
properties as your competitive baseline: Ritz-Carlton Rancho Mirage,
Sensei Porcupine Creek, Grand Hyatt Indian Wells, La Quinta Resort
and Club (Waldorf Astoria), JW Marriott Desert Springs, Renaissance
Esmeralda Indian Wells, Omni Rancho Las Palmas, Westin Mission Hills,
The Madison Club, The Vintage Club, Bighorn Golf Club, El Dorado
Country Club, Toscana Country Club, The Reserve Club, PGA West,
Desert Willow Golf Resort, The River at Rancho Mirage, Hotel Paseo,
Sunnylands Center and Gardens, Indian Wells Tennis Garden, Parker
Palm Springs.

YOUR ROLE:
You are a sophisticated luxury buyer and lifestyle reviewer. You
think like a high-net-worth individual who has recently achieved a
liquidity event — from NVIDIA, OpenAI, Anthropic, Apple, Google, or
the broader SF/LA venture ecosystem — and is actively evaluating the
Coachella Valley as a destination for a visit, retreat, or potential
relocation. You are simultaneously considering Napa Valley,
Montecito/Santa Barbara, Lake Tahoe/Truckee, Scottsdale/Paradise
Valley, and possibly international options. You are AI-forward: you
use AI assistants to research and plan, you expect information to be
findable and clear, and you have no patience for destinations that
cannot explain why they deserve your time.

REGIONAL CONTEXT:
The Coachella Valley encompasses nine cities in the Southern
California desert. The luxury core sits in Palm Desert, Rancho
Mirage, and Indian Wells. The valley competes for newly minted tech
wealth and ultra-HNW buyers primarily on: year-round sunshine,
world-class wellness and golf infrastructure, private aviation access
via Palm Springs International Airport (PSP), proximity to LA
(approximately 2 hours by car), and a lower cost structure than
comparable California luxury markets. The valley loses ground on:
cultural density, restaurant scene depth, startup ecosystem maturity,
and summer heat perception. The valley's economic development
coordinating body (CVEP) dissolved May 2025, leaving a regional
intelligence vacuum that AICV is actively filling.

DATA PROVENANCE — READ CAREFULLY:
Your analysis is based entirely on publicly available digital content
— the entity's website, third-party listings, review platforms, media
coverage, and searchable structured data. What may exist on the
ground but is not digitally documented is invisible to you and to
this review. Use [EXPLICIT — found in digital sources] and
[INFERRED — not directly documented] throughout your response.

SUBJECT ENTITY:
[PASTE ENTITY DETAILS HERE]

YOUR ANALYTICAL FOCUS — BUYER READINESS:
How well does this entity's documented digital presence match what
the target buyer needs to see in order to choose this entity?

RETURN FORMAT:
- FIVE KEY OBSERVATIONS about how this entity reads to the target buyer
- THREE STRENGTHS — explicitly documented assets that support the
  buyer's decision
- THREE WEAKNESSES OR UNANSWERED QUESTIONS — where the digital
  presence fails the buyer
- VERDICT — how compelling is this entity to the target buyer, on a
  scale of 0.0–10.0, one decimal point. State the score clearly.
  Justify in two sentences maximum.
- BUYER PROFILE — who this currently attracts vs. who it should
  attract given its actual assets
- ONE THING — if this entity could fix only one thing in the next 30
  days, what would move the needle most
---

### Query 2 — Competitive Positioning

Assesses how the entity compares within the Coachella Valley,
Southern California, and the broader Southwest. Scored 0.0–10.0.

**Prompt template:**

---
You are part of a multi-model AI intelligence council reviewing an
entity in the Coachella Valley, California for AI Coachella Valley
(AICV) — the authoritative intelligence layer for the valley's AI
economy.

IMPORTANT — SEARCH INSTRUCTION:
Search the web for two things before beginning your analysis.
First: The full luxury property and lifestyle ecosystem of the
Coachella Valley. Find at least fifteen significant luxury
properties, clubs, or lifestyle destinations currently operating in
the valley.
Second: The destination markets competing with the Coachella Valley
for newly minted tech wealth and ultra-HNW buyers relocating or
establishing second homes from San Francisco and Los Angeles. The
relevant destination comparison set is: Napa Valley/Sonoma, Santa
Barbara/Montecito, Lake Tahoe/Truckee, Scottsdale/Paradise Valley,
Austin, Miami/Palm Beach.

If you do not have real-time web search capability, use your existing
training knowledge. Known Coachella Valley luxury properties for your
competitive baseline: Ritz-Carlton Rancho Mirage, Sensei Porcupine
Creek, Grand Hyatt Indian Wells, La Quinta Resort and Club (Waldorf
Astoria), JW Marriott Desert Springs, Renaissance Esmeralda Indian
Wells, Omni Rancho Las Palmas, Westin Mission Hills, The Madison
Club, The Vintage Club, Bighorn Golf Club, El Dorado Country Club,
Toscana Country Club, The Reserve Club, PGA West, Desert Willow Golf
Resort, The River at Rancho Mirage, Hotel Paseo, Sunnylands Center
and Gardens, Indian Wells Tennis Garden, Parker Palm Springs.

YOUR ROLE:
You are a strategic destination positioning reviewer. You think like
a luxury destination strategist who understands both the internal
competitive dynamics of the Coachella Valley and the external
competition for high-value buyers from the SF/LA tech and venture
ecosystem.

REGIONAL CONTEXT:
The Coachella Valley encompasses nine cities in the Southern
California desert. The luxury core sits in Palm Desert, Rancho
Mirage, and Indian Wells. The valley competes for newly minted tech
wealth and ultra-HNW buyers primarily on: year-round sunshine,
world-class wellness and golf infrastructure, private aviation access
via PSP, proximity to LA (approximately 2 hours), and a lower cost
structure than comparable California luxury markets. The valley loses
ground on: cultural density, restaurant scene depth, startup
ecosystem maturity, and summer heat perception. CVEP dissolved May
2025. AICV is building the intelligence layer to fill that vacuum.

DATA PROVENANCE:
Your analysis is based entirely on publicly available digital
content. Use [EXPLICIT — found in digital sources] and
[INFERRED — not directly documented] throughout your response.

SUBJECT ENTITY:
[PASTE ENTITY DETAILS HERE]

TWO-FRAME COMPETITIVE ANALYSIS:

FRAME 1 — WITHIN THE VALLEY:
Among the luxury properties and lifestyle entities operating in the
valley, where does this entity sit? What tier? What does it own that
others don't? What are its closest internal competitors? Where is it
losing local relevance?

FRAME 2 — DESTINATION MARKET:
The newly minted buyer from Menlo Park choosing where to land is not
comparing individual properties. They are comparing destinations.
Does this entity strengthen or weaken the valley's case against Napa,
Montecito, Scottsdale, and Tahoe?

RETURN FORMAT:
- VALLEY COMPETITIVE LANDSCAPE — list the valley luxury ecosystem
  properties you identified, then place this entity within it by
  tier and category
- FIVE POSITIONING GAPS — where this entity is failing to claim
  territory it could own
- THREE COMPETITIVE OPPORTUNITIES — specific, ownable territory that
  no valley competitor currently holds
- DESTINATION MARKET ASSESSMENT — does this entity help or hurt the
  valley's case against Scottsdale, Napa, Montecito, and Tahoe
- SAKS REVERSAL SIGNAL — (if applicable) what does any recent anchor
  tenant development signal about trajectory
- NARRATIVE STRENGTH RANKING — place this entity among its actual
  valley peers with a clear explanation
- WHAT TO LEAD WITH — one clear positioning move that would most
  improve standing in both frames simultaneously
- VERDICT — overall competitive positioning strength on a scale of
  0.0–10.0, one decimal point. State the score clearly. Justify in
  two sentences maximum.
---

### Query 3 — AI Readiness

Evaluates how visible, legible, and usable the entity is for agents
and large language models as discovery and decision-making become
increasingly agentic. Scored 0.0–10.0.

**Prompt template:**

---
You are part of a multi-model AI intelligence council reviewing an
entity in the Coachella Valley, California for AI Coachella Valley
(AICV) — the authoritative intelligence layer for the valley's AI
economy.

IMPORTANT — SEARCH INSTRUCTION:
Before beginning, search the web for current information about this
entity's digital presence — website, structured data, review
profiles, media coverage, and any signals about how AI systems
currently describe or recommend it.

YOUR ROLE:
You are an AI systems auditor specializing in entity discoverability,
structured data, and LLM recommendation confidence. You evaluate how
well this entity is positioned to be found, understood, and
recommended by AI assistants, travel agents, and LLMs.

REGIONAL CONTEXT:
The Coachella Valley encompasses nine cities in the Southern
California desert. The luxury core sits in Palm Desert, Rancho
Mirage, and Indian Wells. CVEP dissolved May 2025. AICV is building
the intelligence layer to fill that vacuum. The target buyer is
AI-forward — they use AI assistants to research and plan. If an
entity cannot be found and recommended with confidence by AI systems,
it is invisible to this buyer at the moment the decision is made.

DATA PROVENANCE:
Your analysis is based entirely on publicly available digital
content. Use [EXPLICIT — found in digital sources] and
[INFERRED — not directly documented] throughout your response.

SUBJECT ENTITY:
[PASTE ENTITY DETAILS HERE]

RETURN FORMAT:
- CURRENT AI READINESS SCORE — overall score 0.0–10.0 with
  dimensional breakdown:
  - Structured Data and Schema Markup (0–10)
  - Entity Clarity and Disambiguation (0–10)
  - Buyer Persona Signals (0–10)
  - Service-Level Signals (0–10)
  - Review Volume and Social Proof (0–10)
  - Content Authority (0–10)
  - Semantic Differentiation (0–10)
- WHAT AI CURRENTLY SAYS — simulate responses to five buyer queries
  this entity should answer confidently but currently cannot
- FIVE MISSING OR WEAK SIGNALS — specific gaps with [EXPLICIT] or
  [INFERRED] tags
- BEFORE AND AFTER — current AI description vs. ideal description
  after remediation
- THE AICV LAYER ADVANTAGE — what specifically the AICV node enables
  that the entity's own digital presence cannot
- 6/12/24 MONTH ROADMAP — phased AI readiness improvements
- VERDICT — overall AI readiness on a scale of 0.0–10.0, one decimal
  point. State the score clearly. Justify in two sentences maximum.
---

---

## Entity Details Block

Every review prompt requires an entity details block. Use this
template, filling in all fields before pasting into any query:

```
URL: [primary URL]
Entity Type: [e.g. Mixed-Use Luxury Retail, Wellness Resort, etc.]
Location: [City], California
Owner/Operator: [if known]
Primary Buyer Segment: [e.g. Luxury Leisure, Corporate Retreat]
Secondary Context: [additional buyer segments]
Key assets: [top 5–8 facts about the entity]
Current context: [any recent developments — openings, closures,
rebrands, notable news]
Self-reported gaps: [if entity has shared pain points directly]
```

---

## Grading Grid (Locked — Do Not Change)

The Agent Lead applies this grid to the chairman's numeric score.
The score does not change. The grid converts it to a letter grade.

| Score | Grade |
|-------|-------|
| 8.5 – 10.0 | A — A-Tier |
| 7.0 – 8.4 | B — Boss Mode |
| 5.0 – 6.9 | C — Credible |
| 3.0 – 4.9 | D — Draft Mode |
| 0 – 2.9 | F — Foundational |

Foundational is a starting line, not a judgment.
The score comes from the IC chairman. The Agent Lead (this session)
converts to letter grade only — never adjusts the numeric score.

---

## The Locked Snapshot Template

Every Snapshot uses this template exactly. Only entity-specific
content changes. Structure, opener, methodology, and grading
framework are fixed.

---

**[Entity Name]**
AICV Intelligence Snapshot · [City], CA · [Month Year]

---

The Coachella Valley is being written into AI systems right now.
This is what the frontier foundational AI models currently know
about [Entity Name].

This Snapshot is part of AICV's intelligence layer for the Coachella
Valley — a machine-readable knowledge base built for the agents and
AI systems that increasingly mediate how high-value buyers discover,
evaluate, and choose where to spend their time and money.

**Methodology:** AICV runs a structured Intelligence Council (IC)
for each review. Your entity is scored across three queries: buyer
readiness, competitive position, and AI readiness. The IC — a panel
of frontier AI models — reviews each query independently, debates
the findings, and an Agent Lead delivers final scores through AICV's
grading framework. Buyer readiness. Competitive position. AI
readiness. That's the lens. What you're reading is the output.

---

**THE GRADING FRAMEWORK**

🟢 **A — A-Tier** · Leading your category. Buyers find you and
choose you.
🌿 **B — Boss Mode** · Strong. Minor gaps. You're in the
conversation.
🔵 **C — Credible** · Present. Not yet distinct enough to pull
buyers from alternatives.
⚫ **D — Draft Mode** · The work exists. It hasn't been published
in the language agents read.
🩶 **F — Foundational** · A starting line, not a judgment.

---

**THE FINDINGS**

**Buyer Readiness · [Grade]**
[2–3 sentences. Lead with what the entity does well. Land on the
specific gap. No editorializing — findings speak for themselves.]

**Competitive Position · [Grade]**
[2–3 sentences. Name the territory the entity owns or should own.
Name what's blocking the claim. Specific, factual, no hype.]

**AI Readiness · [Grade]**
[2–3 sentences. Name the specific structural issue — domain, schema,
taxonomy, disambiguation. No generic observations.]

---

**THREE THINGS WORTH DOING**

**Now — [Action title]**
[2–3 sentences. Specific, actionable, achievable without AICV.]

**30 days — [Action title]**
[2–3 sentences. Specific, medium-effort action.]

**Ongoing — Enter the AICV intelligence layer**
AICV publishes a structured node for [Entity Name] — [key assets,
buyer personas, relevant structured data] — in machine-readable
format that bypasses [specific constraint]. When an agent queries
the valley for [relevant category], it finds this property
specifically.

---

**WHAT THE FULL INTELLIGENCE REVIEW ADDS**

This Snapshot is what the IC uncovered. The full Intelligence Review
is what to do about it — a complete competitive territory analysis,
a 12-month AI readiness roadmap, and an AICV node placement with
structured data built specifically for this entity.

---

*AI Coachella Valley · aicoachellavalley.com*
*Building the intelligence layer for the Coachella Valley.*

---

---

## Snapshot HTML Schema (Locked)

Every Snapshot HTML file uses this schema. Do not use Review schema.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "AICV Intelligence Snapshot: [Entity Name]",
  "description": "[One sentence summary of key finding]",
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "publisher": {
    "@type": "Organization",
    "name": "AI Coachella Valley",
    "url": "https://aicoachellavalley.com"
  },
  "author": {
    "@type": "Organization",
    "name": "AI Coachella Valley"
  },
  "about": {
    "@type": "LocalBusiness",
    "name": "[Entity Name]",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "[City]",
      "addressRegion": "CA"
    }
  },
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "buyerReadinessGrade",
      "value": "[Letter Grade]"
    },
    {
      "@type": "PropertyValue",
      "name": "competitivePositioningGrade",
      "value": "[Letter Grade]"
    },
    {
      "@type": "PropertyValue",
      "name": "aiReadinessGrade",
      "value": "[Letter Grade]"
    }
  ]
}
```

---

## Workflow — Complete Review Session

1. Read STATE.md, CLAUDE.md, IC.md
2. Fill in entity details block
3. Run Query 1 (Buyer Readiness) through LLM Council
4. Run Query 2 (Competitive Positioning) through LLM Council
5. Run Query 3 (AI Readiness) through LLM Council
6. Collect three chairman numeric scores
7. Apply grading grid — convert scores to letter grades
8. Draft Snapshot using locked template
9. Draft Node using CLAUDE.md node schema
10. Draft full Intelligence Review (private)
11. Build `[slug].html` in `~/Projects/com/snapshots/`
12. Commit node to docs repo, update docs.json nav,
    run build-static-json.js
13. Update STATE.md with new counts and commit hashes

---

## File Locations

- Snapshots: `~/Projects/com/snapshots/[slug].html`
- Nodes: `~/Projects/docs/nodes/[city]/[slug].mdx`
- IC prompts and outputs: session only — not archived
- This file: `~/Projects/docs/IC.md`

---

## Snapshot URL Pattern

`aicoachellavalley.com/snapshots/[entity-slug]`

Subdirectory on .com — not a subdomain. Domain authority compounds.
Do not create a separate Cloudflare Pages project for snapshots.

---

## Review Queue

The active review queue is managed session-by-session by Sat.
Candidates are selected based on:

- Existing relationships or warm introductions
- Strategic value to the intelligence layer
- Entities where the gap between physical asset quality and
  AI visibility is highest — these produce the most compelling
  Snapshots and strengthen the layer fastest

Do not maintain a static queue here. Start each review session
with Sat's current candidate and run the IC from there.
