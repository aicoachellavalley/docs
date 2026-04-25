# AICV — Architecture Reference

Read this file when working on infrastructure, deployment, or ops. Not required for routine brief and node content operations.

---

## Infrastructure

| Component | Local Path | URL |
|-----------|-----------|-----|
| Homepage (Astro) | `~/Projects/com/` | aicoachellavalley.com |
| Org site | `~/Projects/org/index.html` | aicoachellavalley.org |
| API Worker | `~/Projects/aicv-api/worker.js` | api.aicoachellavalley.com |
| MCP Worker | `~/Projects/aicv-mcp/worker.js` | mcp.aicoachellavalley.com |
| Twitter Worker | `~/Projects/twitter-worker/` | twitter.aicoachellavalley.com |
| Tools dashboard | `~/Projects/tools/index.html` | tools.aicoachellavalley.com |

**Deployment notes:**
- Homepage (Astro) auto-deploys via GitHub → Cloudflare Pages on every push to main (`git push origin main`)
- Org site does NOT auto-deploy reliably. Deploy manually: `cd ~/Projects/org && npx wrangler pages deploy . --project-name aicoachellavalley-org`
- API Worker is git-controlled at https://github.com/aicoachellavalley/aicv-api — deploy via `wrangler deploy` from `~/Projects/aicv-api/`. No Cloudflare Pages connection — push to GitHub does not deploy.
- MCP Worker is NOT git-controlled — deploy via `wrangler deploy` from `~/Projects/aicv-mcp/`. No git repo in that directory.
- Twitter Worker is NOT git-controlled — deploy via `wrangler deploy` from `~/Projects/twitter-worker/`. No git repo in that directory.
- Tools dashboard does NOT auto-deploy. No Git connection. Always deploy manually: `cd ~/Projects/tools && npx wrangler pages deploy . --project-name aicv-tools`

---

## IC Workflow URLs

| Step | URL | Notes |
|------|-----|-------|
| Step 1 — Intake Form | https://tools.aicoachellavalley.com/ic-intake | Entity copy + three gap questions |
| Step 3 — IC Chair | https://tools.aicoachellavalley.com/ic-chair.html?admin=aicv2026 | Full tool; admin param required for Save Snapshot |

---

## API Worker

Live at `api.aicoachellavalley.com`. Source: https://github.com/aicoachellavalley/aicv-api
Separate from MCP Worker for independent versioning.
Handles AIO tool proxy and dynamic stats (node/brief counts from GitHub).
API key is in Worker secrets — not in client code.
AIO tool uses `claude-haiku-4-5-20251001` — deliberate cost decision, do not change to Sonnet.

---

## MCP Worker

Live at `mcp.aicoachellavalley.com`. Deployed version: `7f86d40a`.
Stateless architecture — fetches MDX node files directly from GitHub raw content.
Claude Desktop connection confirmed working as of March 9, 2026, via mcp-remote bridge.

**Five tools:**
- `query_venues` — filter by city / subcategory / agent_intent
- `get_node` — full record by slug
- `get_regional_brief` — briefs by date / topic
- `get_economic_context` — valley-wide economic profile
- `route_query` — Node Zero dispatcher for natural language queries

**Bug fixes in deployed version (do not revert):**
- `notifications/initialized` returns `respond({})` — required for Claude Desktop MCP handshake
- `extractNodePaths` / `extractBriefPaths` iterate `docsJson.navigation.tabs` (not `docsJson.navigation`) — fixes silent empty results on all tool calls
- City filtering normalized via `toKebab()` — converts frontmatter `"Palm Desert"` → `"palm-desert"` for agent query matching

---

## Twitter Worker

Live at `twitter.aicoachellavalley.com`. Account: @CoachellaAI on X.
Webhook verified end-to-end — any push adding a `.mdx` file to `src/content/briefs/` auto-tweets.
Beehiiv RSS: Sundays 5pm PT.
Manual publish (songs/reports) via MANUAL_PUBLISH_TOKEN.
Clean deploy version: `f3048d63` (April 11, 2026).
Bug fix (April 10, 2026): repo name was `com`, corrected to `homepage` on line 234. Root cause: silent 404 swallowed by try/catch — invisible until manually traced.

---

## Wrangler Note

For `wrangler secret put`: use `printf 'secret\n'` with a single entry — wrangler strips the trailing newline and stores exactly the right value.

Do NOT use `echo` or pipe both entries — piped input concatenates value + confirmation into a doubled secret, storing the wrong value.

---

## Homepage Deployment Rule

Before committing any updated `index.html`, always run:

```
git diff HEAD ~/Projects/com/index.html
```

Review the diff for unintended regressions — especially the stats bar (IDs, fallback values, labels, JS handlers).

**The four stat blocks:**
- `stat-nodes` — Geographic nodes
- `stat-briefs` — Intelligence briefs published (JSON-driven at build time — no manual increment needed)
- `stat-commits` — Platform commits since launch
- `stat-words` — Words analyzed from local businesses (fallback: 10k, pulls `s.wordsAnalyzed`)

Never overwrite `index.html` from an external file without diffing first.

---

## Pre-commit Hook — com repo

A pre-commit hook is installed at `~/Projects/com/.git/hooks/pre-commit`.
It blocks commits where briefs frontmatter (`src/content/briefs/`) contains
escaped dollar signs (`\$`) in title or description fields. The hook is not
git-tracked (lives in `.git/hooks/`, never committed). If the repo is cloned
fresh, recreate from this script:

```sh
#!/bin/sh
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep '^src/content/briefs/')
if [ -z "$STAGED" ]; then exit 0; fi
if echo "$STAGED" | xargs grep -l '^\(title\|description\):.*\\\$' 2>/dev/null | grep -q .; then
  echo "ERROR: Escaped \$ in frontmatter title/description. Use bare $ in YAML."
  exit 1
fi
```

---

## Periodic Maintenance

- Node audit: run subcategory and schema audit every 20 nodes or annually — check for missing subcategory values, taxonomy drift, and v2 field compliance. Use the recon prompt from the March 7, 2026 session.
- All nodes use v2 schema with `verified`, `status`, and `agent_intent` fields.

---

## AIO Tool Architecture Rule

Worker (`~/Projects/aicv-api/worker.js`) returns the raw Anthropic API response unchanged. Homepage (`~/Projects/com/index.html`) handles all parsing:
1. Unwrap `data.content[0].text`
2. Strip markdown fences (``` json / ```)
3. JSON.parse the cleaned string
4. Read `r.score` and derive grade client-side via `gradeFromScore()`

**Never move JSON parsing or grade logic into the worker.** This was attempted March 18, 2026 and caused a cascade of response shape mismatches that broke the tool across multiple deploys. The client-side chain is battle-tested — leave it there.

**Worker observability — content fetch logging.** Workers that fetch and process external content must log content lengths at each transformation step (fetched, cleaned, sliced, sent-to-API). Silent caps and truncation events are the failure mode worth instrumenting against. Two production-impacting bugs in 30 days (GITHUB_RAW silent fail in twitter-worker; AIO 6k slice in aicv-api, commit `91a31f4`) both ran undetected because no length logging existed at the transformation boundaries. One-line `console.log` entries at fetch boundaries are the minimum bar. Cloudflare Worker logs can be tailed in real time via `wrangler tail`.

---

## Agent Discoverability Layer

AICV's core purpose is to be found and cited by AI agents. Every
infrastructure decision must be evaluated against this.

**Live agent access paths — in order of reliability:**
1. Static JSON endpoints (best — no JS, one fetch):
   - aicoachellavalley.com/nodes.json
   - aicoachellavalley.com/briefs.json
   - aicoachellavalley.com/snapshots.json
   - aicoachellavalley.com/llms.txt
   - aicoachellavalley.com/llms-full.txt
   - aicoachellavalley.com/.well-known/mcp.json
2. MCP worker via mcp.aicoachellavalley.com (best for structured queries)
3. Web search → Google index → aicoachellavalley.com/nodes/[slug] or /briefs/[slug]

**Non-negotiable rules:**
1. Run `node scripts/build-static-json.cjs` after every node or brief session.
2. Any new content type needs a corresponding static JSON endpoint before launch.
3. Test agent fetchability before closing any infra session:
   ```
   curl -A "python-requests/2.28" [URL] | head -c 200
   ```
