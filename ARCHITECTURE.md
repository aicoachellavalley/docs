# AICV — Architecture Reference

Read this file when working on infrastructure, deployment, or ops. Not required for routine brief and node content operations.

---

## Infrastructure

| Component | Local Path | URL |
|-----------|-----------|-----|
| Docs (Mintlify) | `~/Projects/docs/` | agent.aicoachellavalley.com |
| Homepage (v5) | `~/Projects/homepage/index.html` | aicoachellavalley.com |
| Org site | `~/Projects/org/index.html` | aicoachellavalley.org |
| API Worker | `~/Projects/aicv-api/worker.js` | api.aicoachellavalley.com |
| MCP Worker | `~/Projects/aicv-mcp/worker.js` | mcp.aicoachellavalley.com |
| Twitter Worker | `~/Projects/twitter-worker/` | twitter.aicoachellavalley.com |
| Tools dashboard | `~/Projects/tools/index.html` | tools.aicoachellavalley.com |

**Deployment notes:**
- Docs (Mintlify) auto-deploy via GitHub → Cloudflare Pages on every push to main
- Homepage auto-deploys via GitHub → Cloudflare Pages on every push to main
- API Worker is NOT git-controlled — deploy via `wrangler deploy` from `~/Projects/aicv-api/`. No git repo in that directory.
- MCP Worker is NOT git-controlled — deploy via `wrangler deploy` from `~/Projects/aicv-mcp/`. No git repo in that directory.
- Twitter Worker is NOT git-controlled — deploy via `wrangler deploy` from `~/Projects/twitter-worker/`. No git repo in that directory.
- Tools dashboard auto-deploys via GitHub → Cloudflare Pages on push to main. Same pattern as homepage.

---

## API Worker

Live at `api.aicoachellavalley.com`. Separate from MCP Worker for independent versioning.
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
Webhook verified end-to-end — any push adding a `.mdx` file to `intelligence-briefs/` auto-tweets.
Beehiiv RSS: Sundays 5pm PT.
Manual publish (songs/reports) via MANUAL_PUBLISH_TOKEN.
Clean deploy version: `25445dbb`.

---

## Wrangler Note

For `wrangler secret put`: use `printf 'secret\n'` with a single entry — wrangler strips the trailing newline and stores exactly the right value.

Do NOT use `echo` or pipe both entries — piped input concatenates value + confirmation into a doubled secret, storing the wrong value.

---

## Mintlify Ops Note

If a push doesn't update the live site within 5–10 minutes, the GitHub App authorization has likely lapsed. Check:
- https://dashboard.mintlify.com — deployment logs and redeploy button
- https://github.com/organizations/aicoachellavalley/settings/installations — GitHub App auth

The error message "Not authorized to fetch tree" is the tell.

---

## Homepage Deployment Rule

Before committing any updated `index.html`, always run:

```
git diff HEAD ~/Projects/homepage/index.html
```

Review the diff for unintended regressions — especially the stats bar (IDs, fallback values, labels, JS handlers).

**The four stat blocks:**
- `stat-nodes` — Geographic nodes
- `stat-briefs` — Intelligence briefs published (increment fallback +1 per new brief)
- `stat-commits` — Platform commits since launch
- `stat-words` — Words analyzed from local businesses (fallback: 10k, pulls `s.wordsAnalyzed`)

Never overwrite `index.html` from an external file without diffing first.

---

## Periodic Maintenance

- Node audit: run subcategory and schema audit every 20 nodes or annually — check for missing subcategory values, taxonomy drift, and v2 field compliance. Use the recon prompt from the March 7, 2026 session.
- All nodes use v2 schema with `verified`, `status`, and `agent_intent` fields.
