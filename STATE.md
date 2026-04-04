# AICV — Current State

Read this at the start of every session before any content operation. Update at end of every session.

---

## Live Counts (as of April 4, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 64 |
| Intelligence briefs live | 120 |
| `stat-briefs` fallback (homepage) | 120 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 70 (Mar 2026)

**Nodes:** 64 across 11 zones — all on v2 schema with `verified`, `status`, `agent_intent` fields.

---

## Active Month Group (docs.json)

Current month group for new briefs: **April 2026**

New briefs append to the top of the April 2026 group in the Intelligence Briefs tab.

When May begins: add a new `May 2026` group at the top of the Intelligence Briefs tab. Do not restructure existing groups.

---

## Last Known Commit Hashes

| Repo | Hash | Notes |
|------|------|-------|
| docs (Mintlify) | `89131eb` | docs: add STATIC_LINKS step to node addition workflow |
| com (aicoachellavalley.com) | `7ab526e` | feat: add Visit Greater Palm Springs snapshot and reviews.json record 2 |
| org (aicoachellavalley.org) | `4e65fa3` | fix: add STATIC_LINKS edges for Gardens, Hotel Paseo, Visit GPS |

> Always verify current hash via `git log --oneline -5` before committing. Do not rely on hashes above as current.

---

## MCP Worker

Deployed version: `72483a7c` (March 26, 2026) — queryVenues optimized: 1 fetch (nodes.json) instead of 57 sequential MDX fetches.

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

---

## Distribution Layer

| Channel | Handle / URL | Role |
|---------|-------------|------|
| Twitter/X | @CoachellaAI | AICV distribution — intelligence briefs, reviews, reports |
| Bluesky | @sunshinefm.bsky.social | SunshineFM human voice — Sat's personal channel |
| Newsletter | Beehiiv (SunshineFM) | Long-form blog and newsletter — 85 editions since June 2024 |

---

## Agent Discoverability Layer

Static JSON endpoints live at repo root:
- `nodes.json` — all 64 nodes (frontmatter only)
- `briefs.json` — all 120 briefs (frontmatter only)
- `.well-known/mcp.json` — MCP server autodiscovery
- `scripts/build-static-json.js` — generator script

Regenerate after adding nodes or briefs: `node scripts/build-static-json.js`

---

## How to Update This File

After every session that adds content:
1. Increment node count if nodes were added
2. Increment brief count + update monthly breakdown if briefs were added
3. Update `stat-briefs` fallback value to match
4. Update active month group if the month has rolled over
5. Update last commit hash for affected repo
