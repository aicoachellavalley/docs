# AICV — Current State

Read this at the start of every session before any content operation. Update at end of every session.

---

## Live Counts (as of March 20, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 49 |
| Intelligence briefs live | 103 |
| `stat-briefs` fallback (homepage) | 103 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 53 (Mar 2026)

**Nodes:** 49 across 9 cities — all on v2 schema with `verified`, `status`, `agent_intent` fields.

---

## Active Month Group (docs.json)

Current month group for new briefs: **March 2026**

New briefs append to the top of the March 2026 group in the Intelligence Briefs tab.

When April begins: add a new `April 2026` group at the top of the Intelligence Briefs tab. Do not restructure existing groups.

---

## Last Known Commit Hashes

| Repo | Hash | Notes |
|------|------|-------|
| docs (Mintlify) | `269d566` | Brief 103 — March 20 also-noted |
| homepage (aicoachellavalley.com) | `8dae7cc` | stat-briefs updated to 103 |
| org (aicoachellavalley.org) | `849e583` | CLAUDE.md graph maintenance steps + live node graph deployed |

> Always verify current hash via `git log --oneline -5` before committing. Do not rely on hashes above as current.

---

## MCP Worker

Deployed version: `7f86d40a` (March 9, 2026) — stable, no pending changes.

---

## Manual Deploy Required — aicv-tools

`tools.aicoachellavalley.com` has NO Git connection in Cloudflare Pages. GitHub pushes do nothing. Always deploy manually:

```
cd ~/Projects/tools && npx wrangler pages deploy . --project-name aicv-tools
```

GitHub integration has been attempted and fails — Cloudflare's UI loops without completing the connection. Do not attempt to debug this again until Cloudflare Pages Git integration UX is confirmed fixed.

---

## Distribution Layer (as of March 17, 2026)

| Channel | Handle / URL | Role |
|---------|-------------|------|
| Twitter/X | @CoachellaAI | Timestamped citation journal — intelligence briefs, regional AI economy |
| Bluesky | @sunshinefm.bsky.social | SunshineFM human voice — Sat's personal channel |
| Newsletter | Beehiiv (SunshineFM) | Long-form; cadence resumption pending |

---

## Pending / On the Horizon

- [ ] Forthcoming node: Desert Community Foundation / CV Giving Day (Palm Desert, nonprofit subcategory)
- [ ] March 21 — Big Brothers Big Sisters summit at Classic Club, Palm Desert (7 Principles framework deployment)
- [ ] March 23 — Follow-up brief covering summit outcomes and youth AI usage data
- [ ] Continue March intelligence brief cadence
- [ ] Monitor for first LLM citation (crawler signposting + llms.txt in place)
- [ ] SunshineFM newsletter cadence resumption on Beehiiv
- [ ] Mobile mailto test for `sat@aicv.co` CTA (desktop issue is unconfigured mail client — test on iPhone)
- [ ] DCF repo move: `git mv nodes/valley-wide/desert-community-foundation.mdx nodes/palm-desert/` + docs.json nav update (separate session)
- [ ] PSP Airport node content: add drive times table to Key Facts section

---

## How to Update This File

After every session that adds content:
1. Increment node count if nodes were added
2. Increment brief count + update monthly breakdown if briefs were added
3. Update `stat-briefs` fallback value to match
4. Update active month group if the month has rolled over
5. Update last commit hash for affected repo
6. Check off or remove completed pending items
