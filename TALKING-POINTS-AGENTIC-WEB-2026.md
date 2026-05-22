# Talking Points: The Agentic Web, Post-Google I/O 2026

**Purpose:** Vocabulary alignment for any AICV conversation about the agentic internet, what Google announced at I/O 2026, and where AICV sits in that picture. This document is internal-facing infrastructure — it grounds anyone (Sat, an LLM Council session, a contractor, a future fresh Claude thread) in consistent language. Not marketing copy.

**Last meaningful update:** 2026-05-22

---

## Section 1 — What Google announced at I/O 2026

Google I/O 2026 was held May 19, 2026. The collective announcement was the largest single rewiring of consumer search and commerce since the original launch of Google Search. Eight pieces matter for AICV's positioning.

**Gemini Spark.** Personal agent that takes action on a user's behalf, including transactions. Runs 24/7 even when the user's device is off. Bounded by the Agent Payments Protocol (AP2) — spend caps, category caps, per-transaction approval at first. Beta launched to AI Ultra subscribers in the US the week of I/O.

**Generative UI in Search.** Search builds custom widgets, simulations, tables, graphs, and full mini-interfaces on the fly per query rather than returning a list of links. Free, available to everyone, rolling out US-first in summer 2026.

**Mini Apps in Search.** Persistent dashboards and trackers for ongoing tasks — wedding planning, fitness, relocation, home moves. Available to AI Pro and Ultra subscribers in the US, rolling out over coming months.

**Information Agents.** 24/7 background monitoring with push synthesis on user-defined topics. Available to AI Pro and Ultra subscribers in the US, summer 2026.

**Universal Cart.** Cross-merchant shopping cart spanning Search, Gemini, YouTube, and Gmail. Rolling out US summer 2026. Initial merchant partners include Nike, Sephora, Target, Ulta, Walmart, Wayfair, and Shopify merchants.

**Universal Commerce Protocol (UCP).** The open standard underneath Universal Cart. Co-developed by Google with Shopify, Etsy, Walmart, Target, and Wayfair. Endorsed by Stripe, Visa, Mastercard, American Express, Adyen, Affirm, Klarna, and others. UCP keeps the brand as merchant of record. UCP for Lodging spec is published with a partner waitlist. UCP expansion to local services, food delivery, and additional geographies announced.

**Agentic booking for local services.** Google announced agent-driven booking for home repair, beauty, and pet care, including Google calling businesses on the user's behalf. Available to everyone in the US, summer 2026.

**Lighthouse Agentic Browsing audit.** Google's deterministic agent-readiness standard, shipped with Lighthouse 13.3 on May 7, 2026, and moved into the default Lighthouse config the same day. Inherits into PageSpeed Insights and all third-party Lighthouse runners. Audits llms.txt presence and validity, accessibility tree quality, layout stability, and WebMCP support. Uses fractional pass ratios rather than 0–100 scoring.

One related-but-separate piece worth noting: the **Agent Payments Protocol (AP2)** is the payment authorization layer underneath Spark and UCP-based transactions. AP2 handles the "user pre-authorized this category and amount, the agent is acting within those bounds" assurance. Different concern from UCP; they compose.

---

## Section 2 — How to talk about the stack

Four protocols matter, and they compose rather than compete:

- **MCP (Model Context Protocol)** — how agents discover and call tools and data. AICV's `aicv-mcp` worker exposes five tools (`get_node`, `query_venues`, `get_regional_brief`, `get_economic_context`, `route_query`). Server-side, accessed by Claude, ChatGPT, Perplexity, Gemini.
- **A2A (Agent-to-Agent)** — how agents talk to other agents. Google-originated, increasingly multi-vendor. Relevant when an AICV agent (a future Premium MVA's daily monitoring agent) wants to hand off to another agent.
- **UCP (Universal Commerce Protocol)** — how agents transact with merchants. Google-led, open standard, co-developed with Shopify and others. Merchant-of-record stays with the brand.
- **AP2 (Agent Payments Protocol)** — how payments are authorized when an agent transacts on a user's behalf.

The right way to describe this in a conversation: **"MCP is how agents read. A2A is how agents talk. UCP is how agents buy. AP2 is how agents pay."**

Lighthouse Agentic Browsing is not a protocol — it's an audit of how well a site supports agent interaction across these protocols and the accessibility primitives underneath. Worth being precise about: Lighthouse measures conformance; it doesn't define the standards itself.

---

## Section 3 — Where AICV sits

AICV is the regional intermediary agent layer between the consumer-side agents (Spark, Claude, ChatGPT, Perplexity, Gemini) and the Coachella Valley businesses they ask about. The unit is the Minimum Viable Agent (MVA) — the foundational agent representation of a Coachella Valley entity on the AICV network.

The slot AICV occupies is one Google's stack does not occupy. Google built the demand side (consumer agents asking questions) and the merchant transaction layer (UCP for businesses that implement it). Google did not build the regional intermediary that knows the long-tail entities, positions them on the right axes for the relocation funnel, and routes intent to them. That's AICV.

**AICV's product line:**

- **Agent Ready Business** (\$2,500/year + \$1,000 setup). The substrate. An MVA on the AICV network, agent-readable and citable, three-axis positioned (one of 11 geographies, one of 6 funnel stages, one of 13 life domains).
- **Agent Ready Premium** (\$10,000/year + \$5,000 setup). Adds an active editorial and monitoring layer — daily monitoring agent watching public signals about the entity, periodic LLM Council reviews, a living `/reviews/[entity]` portal visible to every agent that asks, and a 12-month agent-readiness roadmap.

**What AICV does:**

- Make entities visible to agents through agent-readable structured records (the MVA)
- Position entities on three axes that map to query intent (geography, funnel stage, life domain)
- Maintain editorial weight that distinguishes a relevant result from a merely correct one
- At Premium tier, route inbound inquiry from consumer agents to the entity (form TBD — see open questions, Section 7)
- Operate the agent-readable infrastructure (MCP endpoints, well-known files, RFC 9727 linksets, MCP server cards) so individual entities don't have to

**What AICV does not do:**

- Touch the entity's website
- Implement UCP on behalf of merchants
- Become the merchant of record for any entity's transactions
- Take a commission on referrals or transactions
- Hold customer data or sales data on behalf of any entity

**When asked whether AICV is implementing UCP:** "Not for merchants. UCP requires hosting endpoints on the merchant's own domain, which conflicts with AICV's principle that we don't touch the entity's website. If AICV implements UCP at all, it's for AICV's own properties — sunshine.fm, aicoachellavalley.com itself — where AICV is the merchant. The Premium tier's transaction layer is a different design: AICV-as-intermediary routing inquiry to the entity, not AICV-as-merchant taking payment."

---

## Section 4 — Why now matters

**The 18-month horizon (through November 2027):** Spark goes from Ultra-only to GA. Information Agents go GA. Generative UI is the default search experience for a meaningful fraction of queries. Universal Cart expands globally and includes hotels, food delivery, and local services. Anthropic and OpenAI ship competing or compatible agent commerce flows. For consumer transactional intent in covered categories, a substantial slice of conversions never sees a traditional web page — the agent resolves it inside the agent surface.

**The 36-month horizon (through May 2029):** Multiple agents per consumer, embedded everywhere. UCP and AP2 (or their successors) reach the maturity of OAuth and TLS — boring, ubiquitous, assumed. Websites are deprecated for transactional discovery in covered categories. Regional intelligence networks are explicitly valuable to AI vendors that need authoritative local sources. The lag between businesses with agent presences and those without resembles the 2010s mobile-readiness gap.

The window to be the regional intermediary agent layer for the Coachella Valley before someone else takes that slot is approximately the next 12 months. After that, the slot is either filled or pre-empted by general-purpose agents that resolve regional queries acceptably (without the three-axis precision but with enough coverage to be "good enough" for most users).

---

## Section 5 — The pitch, post-I/O

Pre-I/O, AICV's value proposition was a forecast: "Agents will be how people find things; get ready early."

Post-I/O, it's a present-tense argument:

> Spark beta launched the week of I/O. Universal Cart launches this summer. Agentic booking for local services launches this summer. Generative UI in Search launches this summer. Information Agents launch this summer. Every one of these depends on entities being agent-readable, citable, and three-axis-positioned. Your existing website does not provide that. An MVA on the AICV network does, and it inherits every capability upgrade as the infrastructure matures.

**The differentiator against general-purpose agents:** AICV's three-axis positioning resolves queries that general-purpose agents can only guess at. "Private schools near Cotino for a relocating founder family" resolves precisely because the three axes narrow the answer. General agents return a list of schools with reviews and guess at relevance.

**The differentiator against UCP-equipped national merchants:** AICV is the regional long-tail layer. Walmart and Nike are well-served by UCP. The Coachella Valley's hospitality, wellness, founder infrastructure, and family-and-schooling entities are not on the Universal Cart launch list and won't be for a while. AICV is the regional answer.

---

## Section 6 — Methodology, four pillars

As of I/O 2026, AICV's diagnostic stands on four pillars:

1. **Editorial** — the AICV LLM Council, powered by Anthropic's Claude. Scores positioning, demographic fit, and editorial weight.
2. **Proprietary** — the AICV AIO tool. Scores plain-English visibility to ChatGPT, Claude, Gemini, Perplexity against AICV's regional benchmarks.
3. **Infrastructure** — Cloudflare's Agent Readiness Score (verifiable at isitagentready.com). Measures the agent-readable foundation.
4. **Standards** — Google's Lighthouse Agentic Browsing audit. Measures conformance to Google's published agent-browsing standard.

AICV's own public credibility numbers: 75/100 at Level 5 Agent-Native on Cloudflare, Grade A on AICV AIO, full pass on Lighthouse Agentic Browsing across all five audited `.com` surfaces.

---

## Section 7 — Open questions worth flagging in any deep conversation

These are honest unknowns. Surface them if the conversation goes deep enough that they matter.

**Will Information Agents cite AICV?** Information Agents will synthesize regional content. Whether they cite AICV (driving discoverability) or scrape-and-synthesize (capturing AICV's editorial work without attribution) is the structural risk worth naming. The defense is making AICV's MCP endpoints more attractive to query directly than to scrape. Active research item.

**Browser-side vs server-side agent visibility.** AICV is fully visible to server-side agents (anything that speaks MCP). AICV is not yet visible to browser-side agents (anything that lives in a Chromium tab and reads the DOM looking for actions to invoke) because WebMCP is not yet implemented. Spark in Chrome, Comet, Claude in Chrome will need WebMCP-style integration over time. Scoping work pending.

**Premium's transaction handoff.** The Premium tier currently promises that an entity is positioned to be "the answer when a founder's agent asks about the Valley" and to be "progressively transactable as the commerce layer matures." The specific design of the inquiry-to-entity handoff (lead handoff, booking request, callback request, availability check) is still being scoped.

**Standards-war risk.** UCP is Google-led but open-source. Anthropic and OpenAI may ship competing or compatible standards. AICV's bet is that whatever survives will preserve the merchant-of-record posture and the well-known-file discovery pattern, so AICV's positioning is mostly forward-compatible. Worth tracking, not worth over-investing in.

---

## Section 8 — Phrases to use, phrases to avoid

**Use these:**

- "agent on the network" (externally)
- "node" (internally, when discussing the repo and schema)
- "Minimum Viable Agent" or "MVA"
- "the regional intermediary agent layer"
- "three-axis positioned" (geography, funnel stage, life domain)
- "Agent Ready Business," "Agent Ready Premium"
- "the LLM Council"
- "the Agentic Review" (the private deliverable)
- "the AICV network"

**Avoid these:**

- "listing" or "directory entry" (the MVA is not a listing)
- "SEO" (AICV is agent-readiness, not search-engine optimization)
- "the Intelligence Council" (the locked vocabulary is LLM Council)
- "Snapshot" or "Intelligence Review" (the locked vocabulary is Agentic Review)
- "AICV takes commission" or "referral fee" (the model is retainer-based)
- "AICV implements UCP for merchants" (it doesn't; that conflicts with the no-touch principle)
