# AICV Session Log

Cross-thread record of session-level work. Append-only, dated
entries. Per-thread granularity. Detail belongs in STATE.md, IC.md,
or commit messages — this file is for at-a-glance cross-thread
visibility.

Format per entry:
## YYYY-MM-DD — [topic] (thread closed [time])
- Decisions: [strategic decisions made in this thread]
- Commits: [hashes from this thread only]
- Open questions: [in-flight, not resolved]
- Hand-off to: [what next session on this topic should know]

---

## 2026-06-11 — aicv-mcp report retrieval (already built, verified) + com/ reports.json sections drift fixed (thread closed ~18:30 PT)

- Decisions:
  - Recon-first overturned the premise. Opened on com/ STATE.md GAP 1 ("MCP exposes no report retrieval — only the tool layer is missing"). Disk + live recon of the `aicv-mcp` worker proved the tool layer was ALREADY built and deployed earlier the same day: `get_report` (browse + full-body modes), `route_query` routing report intent to it, smoke-test coverage; 6 tools live, zero disk↔live drift. Did NOT rebuild — verified the premise instead of building from it (would have rebuilt a working tool and never found the parser bug).
  - The real gaps were two hygiene items the recon surfaced: a stale GAP 1 log entry, and a parser silently emptying half the reports' `sections`.
  - `sections:[]` drift diagnosed to root: `build-static-json.cjs` `parseFrontmatter` (dependency-free, line-by-line) only handled single-line arrays; a multiline YAML block array (`sections: [` … `]`) collapsed to `[]`. Hit the two reports using block arrays (dining, visitor-economy); inline-array reports (data-centers, state-of-ai) were unaffected. Fixed at the PARSER (accumulate lines until `]`), not by inlining the two frontmatters — so it never silently empties again for any future report or multiline field. Ripple-checked: no multiline arrays in nodes/briefs, so rebuild changed only `reports.json`.
  - Verified live, not assumed: post-deploy curl of `aicoachellavalley.com/reports.json` reads 8/10/15/10; the two formerly-empty reports now serve real section titles on the edge (e.g. "The Census", "Finding 1 — Zero Structured Data…"), not just non-zero counts. Propagated ~15s.
- Commits (homepage / .com):
  - `33d579c` — docs(state): close GAP 1 — MCP report retrieval shipped
  - `a495c7e` — fix(build): parse multiline YAML block arrays in frontmatter
  - (the `aicv-mcp` desk commits `ce42b68`→`4eca8ed` were the earlier same-day build thread, not this one)
- Open questions:
  - GAP 2 (node↔report cross-links) — still open by design; its own com/ session. No existing pattern → net-new convention to design.
  - Desk v2 retrieval (`sections[]`-driven sectional fetch on `aicv-mcp`) — UNBLOCKED now that browse mode serves real sections; the data is finally there to drive it.
  - com/ scratch-file cleanup (`tmp-agent-*.json`, `tmp-*.md` in the working tree) — pending, so they don't accrue into the next recon's noise.
- Hand-off to: next com/ session — GAP 2 cross-link convention; optional desk v2 sectional retrieval (now unblocked); clear the `tmp-*` scratch files. Disk-as-canon + recon-before-build earned its keep this thread — it's what surfaced both real gaps.

---

## 2026-06-03 — Gemini-feedback triage + Lighthouse 13.3 baseline + WebMCP reference implementation (thread closed ~14:30 PT)

- Decisions:
  - Verified each of three Gemini feedback documents against actual sources before acting. Two of the four headline recommendations in the first doc were either already done (llms.txt existed) or not part of the Lighthouse audit (JSON-LD sameAs, tables).
  - Reciprocated Organization sameAs (.com had omitted .org; both now bind bidirectionally).
  - Added aria-labels to the five AIO diagnostic buttons on /get-agent-ready/.
  - Switched _headers Link relation from rel="service-doc" (semantically wrong) to rel="llms-txt" / rel="llms-full-txt" (emerging Mintlify-led convention); added llms-full.txt advertising.
  - REJECTED Gemini's GitHub-raw-data play — would have recreated the GITHUB_RAW silent-failure pattern and violated single-source-of-truth rule.
  - REJECTED .org WebMCP mirror — no interactive tool surface justifies it; static-by-design.
  - .com README rewrite (2-line stub → repo-explainer); .org README diverged from llms.txt by audience (README explains the repo, llms.txt explains the organization).
  - Lighthouse 13.3 baseline: both sites 1.0 (3/3 weighted audits pass).
  - WebMCP declarative annotation on /get-agent-ready/ analyzer — `<form toolname="analyze_agent_readiness" tooldescription="..." novalidate>` wrapping URL input with `toolparamdescription` and `name="url"`. Reference implementation; audits will not flip from `notApplicable` until Chrome 149 origin trial.
  - Discovered Cloudflare Pages silent-failure pattern: 4 commits stalled behind a broken build (HTML comments in MDX from a prior session — violated a rule already in CLAUDE.md at line 352). Fix at `90f4ac8` unblocked the queue; all 5 stuck commits deployed in one batch. New Build Verification section added to CLAUDE.md.
- Commits (homepage / .com):
  - d773772 — schema: add aicoachellavalley.org to Organization sameAs
  - 9a3d217 — a11y: add aria-labels to AIO diagnostic buttons
  - b7e1515 — headers: advertise llms.txt and llms-full.txt with rel="llms-txt"
  - d7d0cb5 — docs: replace stub README with repo-explainer
  - 90f4ac8 — fix(mdx): replace HTML comments with JSX comments to unblock build
  - b07f207 — feat(webmcp): annotate /get-agent-ready/ analyzer as declarative WebMCP tool
- Commits (aicoachellavalley-org / .org):
  - f082378 — docs: replace duplicate org-pitch with repo-explainer
  - (4 prior-session commits rode along on the same push: 4b5abff, 54d5c9b, 131cd97, a477354)
- Open questions:
  - WebMCP audits will activate when Chrome 149 ships the origin trial removing the `enable-webmcp-testing` flag gate. Passive wait; re-run Lighthouse then.
  - Cloudflare Pages build-failure notifications — worth configuring so the silent-failure pattern can't repeat. Not done in this session.
  - CATEGORIES.md still missing — flagged in earlier sessions, not yet created. No action this session.
  - WebMCP spec is still in draft. Today's annotations may need revision as the spec firms up.
- Hand-off to: next session — optional WebMCP re-audit when Chrome 149 lands; Cloudflare Pages notification setup; CATEGORIES.md decision.

---

## 2026-05-22 — Agentic web positioning + schema hardening + Lighthouse audit

2026-05-22 — Talking-points doc created. `TALKING-POINTS-AGENTIC-WEB-2026.md` added to playbook root. Vocabulary alignment for any conversation about Google I/O 2026 and AICV's position in the agentic web. Internal infrastructure, not marketing copy. To be refreshed quarterly or when significant new agentic-web announcements land.

- Decisions: Lighthouse Agentic Browsing added as fourth methodology pillar; public get-agent-ready copy updated to reflect four-pillar model; `three-part` → `multi-part proprietary` scoring model language locked
- Decisions: Schema hardening — `agent_summary`, `verified`, `status` promoted to Zod-required in `content.config.ts`; two legacy `"active"` status values corrected to `"live"` (desert-willow-golf-resort, sunnylands); cotino Related Nodes converted from display names to slugs
- Decisions: Node workflow hardened — step 7 (run build-static-json.cjs) added to "How to Add a Node" in CLAUDE.md; steps renumbered 8–12
- Commits (com): `82dfe94` (Lighthouse methodology copy), `106b39e` (schema hardening + corpus fixes), `071b8c6` (gitignore five auto-generated `public/` artifacts — `llms-full.txt`, `nodes.json`, `briefs.json`, `snapshots.json`, `reports.json` — matching existing `stats.json` convention; end-to-end verified via post-deploy fetch, Cloudflare Pages build pipeline regenerates and serves files correctly from `dist/`)
- Commits (aicv-playbook): `500d505` (MVA.md), `8b96102` (schema/prompt atomic update)
- Artifacts: Lighthouse baseline audit at `audits/lighthouse/2026-05-22/` (untracked — 8 surfaces, SUMMARY.md)
- Open questions: WebMCP not yet implemented on any AICV surface; Premium transaction handoff design still pending; node count discrepancy between `llms-full.txt` (81 nodes) and `nodes.json` (80 nodes) as of 2026-05-22 — two generators pull from same source but apply different filtering, likely deliberate (status or verified filter) but not confirmed, worth a brief investigation when corpus grows or delta widens, low urgency
- Hand-off to: STATE.md update for schema version and workflow changes; Sunshine FM handoff prompt pending; talking-points doc to be referenced in any new LLM Council or outreach session

---

## 2026-05-11 — Briefs

- 📡 Coachella data center town hall: six buildings, heated opposition, no resolution — May 11, 2026
- Commit: `c7ed43a` — full scope update from town hall (six buildings, 3M sq ft, 270–300 MW); Stronghold–Hernandez campaign finance confirmed; siting proximity documented

---

## Sunday, May 3, 2026 — STATE.md catch-up + CV Intel separation

**Scope:** Strategic STATE.md was 11 days lagging from April 22. Rolled forward against verified counts; fully separated CV Intel from AICV scope.

**Three commits:**
- `2bf9305` — archived `HANDOFF.md` to `archive/cv-intel-2026-05/` with breadcrumb README
- `e34028b` — removed CV Intel canonical path from CLAUDE.md
- `5f7f359` — STATE.md roll-forward: counts (80/142/3/2 as of May 3), five new North Star Roadmap entries, Sibling projects section deleted, Repositories footnote rewritten as scope statement

**Verification before action paid off twice:**
1. TLDR claimed 141 briefs. Build verification said 142. April was 22, not 12 (the existing STATE.md had been wrong on April count for at least 11 days, undetected).
2. Pre-existing STATE.md said 81 nodes. Build verification said 80. The phantom +1 was `src/content/nodes/CLAUDE.md` — a per-collection instruction file that naive directory-listing counts as a node. nodes.json length is authoritative; `ls | wc -l` is not.

**Five roadmap entries added:**
- Milestone: Second Report shipped — State of AI Q1 2026 (2026-04-28)
- Milestone: Sand → paper color migration shipped (2026-05-02)
- Architecture: Postcard Snapshot redesign concept locked (2026-05-02)
- Architecture: Firewall framing evolved — voice and editorial mission, not human author (2026-05-02)
- Architecture: Typography audited, no action required (2026-05-02)

**On the postcard milestone framing:** Recorded as "Architecture" not "Milestone" because the concept is locked but unshipped. Same logic for firewall and typography. Only genuinely-completed work carries "Milestone:" prefix. Worth holding the line on this distinction — it keeps strategic STATE truthful as a record of what's *done* rather than what's *planned*.

**One stray reference carried to tomorrow:** `TOMORROW.md` line 41 still references CV Intel resumption. One-line surgical delete recommended as first action of next session.

**Out of scope but worth noting:** SunshineFM aggregate counter on the website shows 143 briefs; AICV nodes.json says 142. Possible build-staleness on one surface or the other. Not blocking. Worth a check tomorrow if briefs cadence resumes.

**Session closed clean. ~30 minutes for what was scoped as 15. The extra 15 was the verification round that caught the 81→80 phantom — worth every second.**

---

## 2026-05-02 — Color swap + typography audit + IC architecture lock

- Decisions: sand → paper color migration (Option B — keep --sand names, swap values only; rename deferred); firewall framing evolved — implicit human presence permitted, explicit editorial voice not; postcard Snapshot concept locked (one-finding teaser, worker CHAIR_SYSTEM simplification)
- Shipped: 5-file background swap (tokens.css + 4 slug templates) — #E8E2D0/#F2EDE0/#D4CCBA → #FAFAF7/#FFFFFF/#E8E5DD; com STATE.md updated with grade map cleanup note; typography audit (16px/1.75/760px — no changes needed)
- Commits: 690dc4a (color swap), def53e0 (STATE.md)
- Open questions: LLM Council API reply still pending (email sent 2026-04-28)
- Hand-off to: next session — postcard Snapshot redesign first (worker CHAIR_SYSTEM, IC.md template rewrite, migrate 3 live Snapshots, schema.org cleanup, reviews.json, _schema.json, cold outreach copy); then print stylesheet; grade color map cleanup (snapshots/[slug].astro lines 57–110) after postcards ship

### Queue for next session
1. Postcard Snapshot redesign — worker CHAIR_SYSTEM simplification, IC.md template rewrite, migrate 3 live Snapshots, schema.org cleanup, reviews.json, create Snapshot _schema.json, cold outreach copy update
2. Print stylesheet — @media print rules for briefs, nodes, reports, snapshots
3. Grade color map cleanup — delete dead code at snapshots/[slug].astro lines 57–110 after postcard migration ships
4. Two-agent IC pilot — Pre-Council + Post-Council Agent specs for Rancho Mirage, awaiting LLM Council API reply (sent 2026-04-28)
5. Print test — validate paper background on actual paper after print stylesheet ships
6. Playbook update — firewall framing as voice/mission, not human author existence

### Parked
- Postcards as physical mail to registered entities
- --sand → --paper variable rename (live with current names for a session)

---

## 2026-04-29 — IC worker hygiene + grades-go-private decision (thread closed 16:25)

- Decisions: grades-go-private (six-surface migration required); two-agent IC architecture (Pre-Council + Post-Council, city-scoped memory, Rancho Mirage pilot); real-time search via Claude native not Exa
- Commits (this thread only): 06e3fdb, d1fa86a, 4c76aef, 787da8f, d2ee2e2
- Open questions: LLM Council API availability (email sent, reply pending)
- Hand-off to: next IC session — draft Pre-Council and Post-Council agent specs as IC.md additions, then begin Rancho Mirage pilot build; address grades-go-private migration across the six surfaces in STATE.md
