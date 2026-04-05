# AICV — Current State

Read this at the start of every session before any content operation. Update at end of every session.

---

## Live Counts (as of April 5, 2026)

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
| com (aicoachellavalley.com) | `f76a049` | chore: remove legacy static files superseded by Astro build |
| org (aicoachellavalley.org) | `4e65fa3` | fix: add STATIC_LINKS edges for Gardens, Hotel Paseo, Visit GPS |
| tools (aicv-tools) | deployed April 5 | fix: key passphrase unlock on entity name, not LLM-generated slug |

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

## Deploy — Cloudflare Pages Properties

**aicoachellavalley.com** (com repo) — AUTO-DEPLOYS via git push:
```
git push origin main
```
Git integration confirmed active April 5, 2026. Build command: `npm run build`. Output directory: `dist`. No manual wrangler deploy needed.

**aicoachellavalley.org** (org repo):
```
cd ~/Projects/org && npx wrangler pages deploy . --project-name aicoachellavalley-org
```

**tools.aicoachellavalley.com:**
```
cd ~/Projects/tools && npx wrangler pages deploy . --project-name aicv-tools
```

**sunshine.fm:**
```
cd ~/Projects/sunshine-fm && npx wrangler pages deploy . --project-name sunshine-fm
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

## Astro Migration — Completed April 5, 2026

- **Framework:** Astro v6.1.3, static output
- **Repo:** `~/Projects/com/` — same repo, no new remote
- **Deploy:** `git push origin main` → Cloudflare Pages git integration auto-builds
- **Five content routes ready:** `snapshots/`, `nodes/`, `briefs/`, `reviews/`, `reports/`
- **Snapshot schema locked:** `src/data/snapshots.json` — canonical contract for all IC review output
- **Two snapshots live:** `visit-greater-palm-springs` (D/D/F) and `gardens-on-el-paseo` (C/D/D)
- **Homepage:** placeholder live (`<h1>AI Coachella Valley</h1>`), full rebuild pending

---

## Priority Queue

1. IC chair Save button — next build
2. Homepage rebuild — port old index.html content to Astro
3. Static nodes directory — Gemini crawlability
4. Send the emails

---

## How to Update This File

After every session that adds content:
1. Increment node count if nodes were added
2. Increment brief count + update monthly breakdown if briefs were added
3. Update `stat-briefs` fallback value to match
4. Update active month group if the month has rolled over
5. Update last commit hash for affected repo
