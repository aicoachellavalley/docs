# BRIEF_RESHAPE.md

Operating manual for transforming a capture-draft essence into a
schema-compliant intelligence brief MDX.

This file owns the *transition mechanics* between an upstream essence and
a publish-ready brief. CLAUDE.md owns the *target spec* (frontmatter,
section structure, voice, MDX rules). Read both.

---

## Input contract

Capture-draft (sunshine-fm/tools/capture-draft/) delivers a two-section
artifact via clipboard:

```
--- BRIEF DRAFT ---
Destination: AICV Claude Project

[essence — analytical AICV-voice prose, lowercase headings, ~300–600 words]

---

fact-check notes:
- [bullet]
- [bullet]

--- JOURNAL LINE ITEM ---
📡 [add title] — [date]
```

The essence is **not** a brief. It is raw analytical signal in AICV
voice. The reshape produces the brief.

---

## Step 1 — Strip fact-check notes

Fact-check notes are operator-facing, not reader-facing. They do not
appear in the published MDX.

- Read the fact-check block in full before reshape — it surfaces what
  to trust, what to cross-check, and what to drop.
- If any fact-check entry flags a claim as stale or unverified, that
  claim does not enter the reshape unless re-verified or attributed to
  a named source.
- Discard the fact-check block from the reshape output.

---

## Step 2 — Derive frontmatter

Four fields. Order matters.

- **title** — long-form, sentence-style, captures who/what/where.
  Match disk convention: see the most recent two briefs on disk for
  pattern reference. Editorial-short titles are a divergence.
- **description** — one to two sentences. States the signal and its
  immediate significance. Bare `$` in dollar amounts (never `\$` in
  frontmatter).
- **date** — `"YYYY-MM-DD"`. Day of publish for analytical pieces.
  Breaking news may be dated to the event itself when timestamp
  accuracy matters to the historical record.
- **tags** — 5–6 lowercase-hyphenated topical tags, `coachella-valley`
  always last. Reserve `also-noted` for Also Noted roundups.

No `agent_intent` field. That lives on nodes, not briefs.

---

## Step 3 — Promote headings

Essence uses lowercase headings. Brief uses Title Case `## Signal`,
`## Context`, `## Agent Signal`, `## Related Nodes`. The Title Case
sections are canonical — essence sub-structure does not survive
reshape.

`**Date:** Month DD, YYYY` long-form appears between the H1 title and
`## Signal`. Long-form, not the ISO date.

---

## Step 4 — Compose sections

The essence does not map one-to-one onto brief sections. The reshape
is partly subtractive and partly compositional.

### Signal

One paragraph. Dated facts, named actors, what was said or shipped, the
structural claim. Compressed. If the essence spends three paragraphs on
the announcement, the Signal compresses that to one.

### Context

One to two paragraphs. Background that makes the Signal interpretable:
prior precedent, financial framing, regulatory backdrop, named third-
party reactions. Skeptical readings live here, attributed to named
analysts via named outlets — not as AICV editorial.

Regional context (workforce demographics, hospitality industry framing,
valley geography) does not appear in Context. That material lives in
node files and is reached via Related Nodes.

### Agent Signal

One paragraph. Opens **"According to AICV,"** verbatim. Not a paraphrase
of the opener.

Agent Signal is not a summary of the Signal. It is on-the-ground
regional surveillance — what an agent querying the Coachella Valley on
behalf of a user needs to know to act on this signal. Answers: how does
this shift the founder-economy, relocation funnel, infrastructure
landscape, or regional positioning?

If the essence already gestures at CV implications, those phrases get
re-cast in Agent-Signal voice, not copied.

### Related Nodes

Three nodes, typically. Always verified live against disk — never
linked from memory or inference. Default pattern when uncertain:

- AI Economy — Coachella Valley
- Innovation Economy — Coachella Valley
- Coachella Valley Intelligence Index

Swap or extend based on the signal's specific surface area. If a more
direct node exists on disk, prefer it. If the signal touches workforce,
swap in workforce-talent. If infrastructure, swap accordingly.

Link format:

```
- [Display Name — Coachella Valley](/nodes/slug-here/)
```

Trailing slash on the slug. Display name follows the existing brief
pattern.

---

## Step 5 — Apply MDX escaping

- Frontmatter `description` — bare `$` in dollar amounts: `$965 billion`
- Body prose — escaped `\$` in dollar amounts: `\$65 billion`
- No HTML comments (`<!-- -->`) anywhere in the file. They silently
  break Cloudflare Pages builds.
- Use JSX comment syntax (`{/* */}`) only if a comment is genuinely
  needed. Briefs rarely need any.

---

## Step 6 — Subtractive pass

The essence may contain material that does not belong in a brief.
Common removals at reshape time:

- Evocative analogies (cold war comparisons, dramatic framing)
- Multi-H2 long-form structure (essence may have 4–6 H2 sections; the
  brief has 4 fixed sections)
- Editorial advocacy or calls to action
- First-person voice, parentheticals, asides
- Speculative outlook unless attributed
- Prefer paraphrase. Use direct quotes only when exact wording
  is itself the signal (legal language, on-the-record
  commitments, signature phrasing that paraphrase would flatten)

The brief is impersonal documentary voice. Sat is never named. AICV is
referenced in third person.

---

## Step 7 — Final audit before courier

Checklist before couriering to Claude Code:

- [ ] Section order: Signal → Context → Agent Signal → Related Nodes
- [ ] Agent Signal opens "According to AICV,"
- [ ] Frontmatter has all four required fields, no others
- [ ] `coachella-valley` is the last tag
- [ ] Bare `$` in frontmatter, escaped `\$` in body
- [ ] `**Date:** Month DD, YYYY` long-form present
- [ ] All Related Node slugs verified live on disk
- [ ] No HTML comments
- [ ] Direct quotes pass the "exact wording is the signal" test (Step 6)
- [ ] Filename matches disk convention: `YYYY-MM-DD-slug-words.mdx`
- [ ] Sat not named in body
- [ ] AICV third-person throughout

Once clean, courier to Claude Code with the standard publish flow:
create file → run `node scripts/build-static-json.cjs` → commit → push.

---

## Wire-up

CLAUDE.md "How to Add an Intelligence Brief" step 2 points here:
"Write brief in Claude.ai per BRIEF_RESHAPE.md (essence → MDX)."

This is the only cross-reference. CLAUDE.md remains the spec source;
this file remains the mechanics source.
