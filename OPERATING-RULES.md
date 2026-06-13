# AICV — Standing Operating Rules

> How AICV multi-agent census, publishing, and model-orchestration
> sessions are *run*. This is the operating layer — distinct from
> `CLAUDE.md` (content schemas + publishing workflow), from
> `templates/census/TEMPLATE-README.md` (census *mechanics*), and from
> `STATE.md` (strategic state). Where a rule below has census mechanics,
> this doc states the standing *principle* and points to the template;
> it does not duplicate it.
>
> Codified 2026-06-13 from the operating learnings of the week of
> June 9–12, 2026 (dining V2 regen, H&RE census + report, F&S census).

---

## 1. Model seating

Each model has a seat. Do not freelance the assignment.

- **Fable 5 — synthesis / editorial sessions ONLY.** It burns at **2×**
  (free through **June 22, 2026** — see §3). Use it for report drafting,
  editorial voice, and synthesis where prose quality is the product.
  Never for recon, orchestration, or fan-out.
- **Opus 4.8 — recon, orchestration, diagnostics, planning.** The
  thinking seat. Plans are **made or reviewed on Opus or better.**
- **Sonnet 4.6 — fan-out workers**, pinned per-agent via `model: 'sonnet'`
  on every `agent()` call. Sonnet **executes but never gate-approves its
  own plan** — a plan Sonnet produced is reviewed on Opus or better before
  it runs. (Census mechanics: `templates/census/TEMPLATE-README.md` →
  "Model split.")

## 2. Session model control

`/model` is set by **the human at every new session start.** Prompt-level
model declarations (in a payload, skill, or workflow header) **do not
control the session model** — they document intent only. If a session
needs a different seat than the one the human set, surface it; do not
assume the prompt overrode `/model`.

## 3. Free-window rule (the Fable window is a *publishing* window)

The Fable 5 free-through-June-22 window is a **PUBLISHING window, not a
census window.** Run census **only as fast as synthesis can also
publish.** Never strand a finished dataset unpublished across a pricing
boundary — a dataset that lands the day the window closes, with its
report still undrafted, has wasted the window. Pace census fan-out to
the publishing throughput, not the other way around.

## 4. Budget guards

- A run's token/usage guard (e.g. the census 12M–14M usage-basis ceiling)
  is **overridden only at a batch boundary, with the reasoning surfaced**
  — never silently mid-batch. Checkpoint, state the new ceiling and why,
  then continue.
- Precedent: dining enrichment, 2026-06-11.
- Census guard mechanics (per-batch checks, depth pin, checkpointing):
  `templates/census/TEMPLATE-README.md` → "Budget guards."

## 5. Census & data-product integrity

These four govern every census and every published figure.

### 5.1 Membership is never conditioned on the measured variable

A census's membership is **never** conditioned on the variable being
measured — e.g. web presence in a web-visibility census. Out-of-scope
segments are **defined out with a stated rationale** and **kept as tagged
context rows**, not silently dropped. Precedents: dining
`mobile`/`catering`; H&RE `remote_operator`; F&S `family_home_daycare`
(registry-only homes — enumerable only via the state registry, not a web
sweep, so excluded from the *business* census but retained as context).

### 5.2 Numeric discipline

**Every published figure computes from a committed stats script run
against the canonical dataset.** Recalled or hand-carried numbers never
publish — **including flattering ones.** Recompute denominators fresh from
disk, with the definition stated, for every figure. (This rule applies to
this very repo's own counts: see `STATE.md` Live Counts, reconciled
against `reports.json`, not from memory.)

### 5.3 Cross-report consistency gate

Before drafting a new or revised report, its shared figures are
**script-asserted against the already-published reports.** Two live
reports never disagree silently — neither in numbers nor in superlative
claims ("first / only" deconfliction). Precedent: dining V2 regen
consistency-gated to the digit against the live H&RE report
(2026-06-12). The public-facing convention lives on the methodology page
(`com` → `methodology-agent-mapped-census`); this is the internal gate
that enforces it.

### 5.4 Regen draft convention

A regenerated/revised report draft is written to a **`_`-prefixed file
that the loader ignores**, and **renamed on gate-approval.** The working
tree therefore never holds an unapproved-but-publishable file. (Astro
content loaders skip `_`-prefixed entries; this is the mechanical hook
that makes "drafted but not live" a filesystem fact, not a promise.)

## 6. Outreach division of labor

- **Manual human email is reserved for one-to-many and allies:**
  associations, press, and positive recognition (no ask).
- **One-to-one at scale is the agent-mail rail** (see `STATE.md` →
  email-pilot arc for the rail itself).
- **Recognition emails to exemplars carry no sales pitch** — they are
  independence evidence. An entity that scored well hears that it scored
  well, full stop; the absence of an ask is the point.

---

## Pointers

- `CLAUDE.md` — content schemas, node/brief workflow, strategic decisions.
- `STATE.md` — strategic state, live counts, forward queue.
- `templates/census/TEMPLATE-README.md` — census harness + mechanics.
- `ARCHITECTURE.md` — infrastructure, Cloudflare zone posture, agent
  discoverability.
