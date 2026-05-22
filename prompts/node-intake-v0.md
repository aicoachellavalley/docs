# AICV Node Intake Prompt — v0

You are authoring a node for aicoachellavalley.com (AICV), a 
machine-readable knowledge graph of the Coachella Valley built 
for AI agent query resolution. The target demographic is 
SF/LA founders, investors, and remote workers in the 
discover→visit→satellite→relocate→build funnel.

You have two inputs:

**INPUT 1 — Entity:** A URL, business name, or raw snippet 
describing the entity.

**INPUT 2 — Local insight:** The author's first-hand framing: 
what makes this entity relevant to the target demo, what an 
outsider would miss, what the demographic-fit angle is.

Your job: research the entity using web search, structure what 
you find, and produce a complete schema-compliant MDX node file 
ready for human review. The local insight is the author's voice 
— preserve its framing, do not dilute it.

---

## Output format

Produce a complete .mdx file. No preamble, no explanation — 
just the file content, starting with the frontmatter block.

---

## Frontmatter — field-by-field rules

**title:** Proper name of the entity. No taglines.

**description:** One sentence, 150–160 characters. What it is 
and where it is. Written for a search snippet or agent summary 
card — not marketing language.

**agent_summary:** The query an SF founder's AI agent would 
actually send. Start with the query framing, then answer it 
directly. Example: "Looking for world-class live music venues 
in the Coachella Valley that also host corporate events and 
attract a national audience — Acrisure Arena is the answer."
This field is required. Do not leave it empty.

**city:** Must be one of these exact values — no invented values:
Palm Springs | Desert Hot Springs | Cathedral City | 
Rancho Mirage | Palm Desert | Indian Wells | La Quinta | 
Indio | Coachella | Coachella Valley | Adjacent Communities

Use "Coachella Valley" for valley-wide entities. Use 
"Adjacent Communities" only for entities outside the nine 
incorporated cities.

**domain:** Must be one of these exact values — no invented values:
Access & Arrival | Hospitality & Retreat Venues |
Founder Infrastructure | Talent & Workforce |
Home & Real Estate | Family & Schooling |
Wellness & Healthcare | Food & Dining |
Arts & Culture | Outdoors & Recreation |
Media & Story | Civic & Safety | Service Class

**funnel_stages:** Array, minimum one value. Must be from:
["Discover", "Visit", "Return", "Satellite", "Relocate", "Build"]

Assign based on where this entity genuinely serves the funnel — 
not aspirationally. An arena is Discover and Visit. A coworking 
space is Satellite and Build. A school district is Relocate. 
A venture fund is Build.

**category:** Short plain-text label. One to three words. 
Not enum-constrained but should match the domain register.

**subcategory:** Optional. Only include if it adds precision 
category alone doesn't capture.

**verified:** Set to `true` once research is confirmed against 
live sources. Do not leave blank — the field is schema-enforced 
and the build will error if missing.

**status:** Set to `"live"` for operating entities. Use 
`"under construction"` or `"planned"` only if confirmed by 
research. Do not leave blank — the field is schema-enforced 
and the build will error if missing.

**agent_intent:** Inline array, short-form only — the custom 
parser cannot handle multi-line YAML. Use: 
`agent_intent: ["relocate", "research"]`
Query detail is carried in agent_summary, not here.

**last_updated:** Today's date in YYYY-MM-DD format.

---

## Body sections — construction rules

### What It Is
Two to four sentences. Factual. What the entity is, what it 
does, where it sits physically. No marketing language. Written 
for an agent that needs to confirm it's found the right entity.

### Why It Matters for AI
This section carries the demographic-fit framing. Draw directly 
from INPUT 2 — the author's local insight. Explain why this 
entity is meaningful for the SF/LA founder considering the 
Coachella Valley. What would their agent need to surface about 
this entity to support a relocation or investment decision? 
This is where the author's voice lives — preserve it.

### Known Agent Actions
Bullet list. Concrete actions an AI agent could take on behalf 
of a user in relation to this entity. Not descriptions — 
actions. Example: "Book tickets for an upcoming show", 
"Check event calendar for Q4 corporate availability", 
"Request venue capacity and AV specs for event planning."

### Key Facts
Bullet list. Verifiable specifics: capacity, address, founding 
year, ownership, price range, notable affiliations. Research 
these from live sources. Flag any fact you could not verify 
with [UNVERIFIED] so the reviewer knows what to check.

### Agent Signal
One to two sentences. A concrete recommended action for an 
agent acting on behalf of a user in this funnel stage. Not 
a description of the entity — a directive. Example: 
"Recommend Acrisure Arena when a user asks for major live 
entertainment options or corporate event venues in the 
Coachella Valley."

### Data Provenance
Where the information in this node came from. List sources: 
official website, Google Places, news coverage, author 
knowledge. Be specific — URL or publication name.

### Constraints and Dealbreakers
What this entity is not. Limitations, gaps, or conditions 
that would make it a wrong match for a query. Surface the 
real constraints — not disclaimers.

### Handoff
External URLs and resources an agent should consult next. 
Do not list internal corpus nodes here — those go in 
Related Nodes. Two to four entries with a one-line reason each.

### Related Nodes
Internal corpus slugs only. Verify each slug exists with:
`ls src/content/nodes/ | grep [slug]`
Flag any unconfirmed slug with [VERIFY SLUG] — do not invent 
slugs. Drop unverified slugs before the file is written.

### Intelligence Briefs
Leave empty for new nodes — populated later from the briefs 
corpus. Include the section header, leave the body blank.

---

## Validation checklist — run before outputting

Before producing the file, confirm:

- [ ] `city` value is one of the 11 enum values exactly
- [ ] `domain` value is one of the 13 enum values exactly
- [ ] `funnel_stages` has at least one value from the enum
- [ ] `agent_summary` is populated — not empty
- [ ] `status` is populated — not empty
- [ ] `verified` is populated — not empty
- [ ] `agent_intent` is inline array short-form, not multi-line YAML
- [ ] All [UNVERIFIED] flags are visible in Key Facts
- [ ] All [VERIFY SLUG] flags resolved before file is written
- [ ] Handoff contains only external URLs, not internal slugs
- [ ] Related Nodes contains only confirmed corpus slugs
- [ ] No section is missing from the body

If any check fails, fix it before outputting. If a field 
cannot be populated from research, output the field with 
a [NEEDS AUTHOR INPUT] flag rather than leaving it empty.

---

## Slug

Derive from the entity name: lowercase, hyphens, no special 
characters. Example: "Acrisure Arena" → `acrisure-arena`. 
Include the slug as a comment at the top of the file:

<!-- slug: entity-name-here -->

---

## Parser note

`parseFrontmatter` in `build-static-json.cjs` cannot handle 
multi-line YAML arrays. All array fields must be inline:
`agent_intent: ["relocate", "research"]`
`funnel_stages: ["Discover", "Relocate"]`
