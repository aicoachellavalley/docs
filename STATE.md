# AICV — Current State

Read this at the start of every session before any content operation. Update at end of every session.

---

## Live Counts (as of March 24, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 56 |
| Intelligence briefs live | 113 |
| `stat-briefs` fallback (homepage) | 113 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 63 (Mar 2026)

**Nodes:** 56 across 9 cities — all on v2 schema with `verified`, `status`, `agent_intent` fields.

---

## Active Month Group (docs.json)

Current month group for new briefs: **March 2026**

New briefs append to the top of the March 2026 group in the Intelligence Briefs tab.

When April begins: add a new `April 2026` group at the top of the Intelligence Briefs tab. Do not restructure existing groups.

---

## Last Known Commit Hashes

| Repo | Hash | Notes |
|------|------|-------|
| docs (Mintlify) | `b600e2f` | agent_summary added to all 56 nodes; nodes.json updated with agent_summary field (45.7 KB) |
| homepage (aicoachellavalley.com) | `e0a5b6b` | stat-briefs updated to 113 |
| org (aicoachellavalley.org) | `480bc80` | 5 nodes added to graph — ZONE_MAP, SUB_MAP, 13 new edges |

> Always verify current hash via `git log --oneline -5` before committing. Do not rely on hashes above as current.

---

## MCP Worker

Deployed version: `7f86d40a` (March 9, 2026) — stable, no pending changes.

---

## Maintenance Scripts

After any session adding nodes or briefs, run:

```
node scripts/build-static-json.js
```

from `~/Projects/docs/` — regenerates `nodes.json` and `briefs.json` in `public/`. Commit both files:

```
chore: regenerate static JSON (N nodes, N briefs)
```

Do not skip. Stale JSON = agents reading outdated data.

Static endpoints:
- https://agent.aicoachellavalley.com/nodes.json
- https://agent.aicoachellavalley.com/briefs.json
- https://agent.aicoachellavalley.com/.well-known/mcp.json

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

## Agent Discoverability Layer (added March 24, 2026)

Static JSON endpoints live at repo root — Mintlify serves static files from repo root, not `public/`:
- `nodes.json` — all 56 nodes (frontmatter only, 30.6 KB)
- `briefs.json` — all 113 briefs (frontmatter only, 63.3 KB)
- `.well-known/mcp.json` — MCP server autodiscovery
- `scripts/build-static-json.js` — generator script (run from docs root to regenerate)

`llms.txt` updated with static endpoint URLs and corrected counts (was: "33 nodes, 32 briefs").

Regenerate JSON files after adding new nodes or briefs: `node scripts/build-static-json.js`

---

## Pending / On the Horizon

- [ ] Forthcoming node: Desert Community Foundation / CV Giving Day (Palm Desert, nonprofit subcategory)
- [ ] March 21 — Big Brothers Big Sisters summit at Classic Club, Palm Desert (7 Principles framework deployment)
- [x] March 22 — Youth AI usage brief (BBBS session outcomes) — done
- [ ] Continue March intelligence brief cadence
- [ ] Monitor for first LLM citation (crawler signposting + llms.txt in place)
- [ ] SunshineFM newsletter cadence resumption on Beehiiv
- [ ] Mobile mailto test for `sat@aicv.co` CTA (desktop issue is unconfigured mail client — test on iPhone)
- [x] DCF repo move: `git mv nodes/valley-wide/desert-community-foundation.mdx nodes/palm-desert/` + docs.json nav update — done `7cbabef`
- [x] PSP Airport node content: add drive times table to Key Facts section — done `57d2300`

---

## How to Update This File

After every session that adds content:
1. Increment node count if nodes were added
2. Increment brief count + update monthly breakdown if briefs were added
3. Update `stat-briefs` fallback value to match
4. Update active month group if the month has rolled over
5. Update last commit hash for affected repo
6. Check off or remove completed pending items
