# AICV Surface Inventory

> The canonical map of every agent-facing AICV surface — human pages, machine
> feeds, agent-discovery files, and the MCP desk — and the **count-agreement graph**
> the surface-health monitor enforces. Disk is canon; counts here are disk/endpoint-
> verified as of 2026-06-14. The deterministic monitor that checks this inventory
> lives in `tools/surface-health/` (no AI at runtime).
>
> Count vocabulary: see the **report-count legend** in `STATE.md` → Live Counts
> (4 censuses / 5 series / 7 Reports / 8 reports.json entries — scopes differ by design).

---

## 1. Human pages (aicoachellavalley.com)

254 live URLs (sitemap.xml). Route families:

| Route | Backed by | Count |
|---|---|---:|
| `/reports/[slug]/` | `src/content/reports/*.mdx` | 8 |
| `/nodes/[slug]/` | `src/content/nodes/*.mdx` | 81 |
| `/briefs/[slug]/` | `src/content/briefs/*.mdx` | 156 |
| `/snapshots/[slug]/` | `public/snapshots.json` | 3 |
| `/get-agent-ready/`, `/minimum-viable-agent/`, `/founding-111/`, section indexes, `/` | static/Astro | — |

`_`-prefixed content files are loader-ignored (the report draft convention); they do not render and do not enter these counts.

## 2. Machine feeds

Regenerated at every deploy by `com` → `scripts/build-static-json.cjs` (JSON feeds) and `scripts/generate-stats.mjs` (stats). **Not git-tracked** — they are build artifacts; the MDX/content is the source of truth.

| Feed | Shape | Count | Consumed by |
|---|---|---:|---|
| `/reports.json` | array | 8 | site `/reports/`, MCP `get_report` |
| `/nodes.json` | array | 81 | site `/nodes/`, MCP `get_node` |
| `/briefs.json` | array | 156 | site `/briefs/`, MCP `get_regional_brief` |
| `/snapshots.json` | array | 3 | site `/snapshots/` |
| `/stats.json` | object | — | homepage stats |
| `/llms.txt`, `/llms-full.txt` | text | — | LLM crawlers |
| `/sitemap.xml` | xml | 254 `<loc>` | search engines, the heartbeat trend |
| `/robots.txt` | text | — | crawlers (points to llms.txt) |
| `/<indexnow-key>.txt` | text | — | IndexNow validation (`a0637c7110a38cb16503aceee7e1a289`) |

## 3. Agent-discovery surfaces (`.well-known/`)

`security.txt` · `api-catalog` (RFC 9727 linkset) · `mcp.json` · `mcp/server-card.json` (SEP-2127 shape) · `skills/index.json` + `skills/query-coachella-valley-intelligence/SKILL.md`.

## 4. MCP desk — `mcp.aicoachellavalley.com/mcp` (6 tools)

Streamable HTTP (JSON-RPC `tools/call`; requires `Accept: application/json, text/event-stream`). The desk fetches the `.com` feeds live.

| Tool | Reads | Browse (bare call) |
|---|---|---|
| `get_report` | `/reports.json` | ✅ array — **default limit 5, max 10** (pass `limit:10` for full count while ≤ 10) |
| `get_node` | `/nodes.json` | ❌ **no browse mode** (returns `{error}`; requires a slug) |
| `get_regional_brief` | `/briefs.json` | ⚠️ array but **limit-capped** (default 5) — not a full count of 156 |
| `query_venues` | venues data | — |
| `route_query` | router | — |
| `get_economic_context` | economic data | — |

## 5. The count-agreement graph (what the monitor enforces)

A surface is healthy when the **same entity count agrees across its surfaces**:

| Entity | feed JSON | site pages (sitemap) | MCP desk | agreement |
|---|---:|---:|---:|---|
| **reports** | `/reports.json` = **8** | `/reports/[slug]/` = 8 | `get_report` (limit 10) = 8 | **three-way — the anchor (= 8, the legended canon)** |
| nodes | `/nodes.json` = 81 | `/nodes/[slug]/` = 81 | `get_node` has no browse | feed ↔ site (two-way) |
| briefs | `/briefs.json` = 156 | `/briefs/[slug]/` = 156 | `get_regional_brief` limit-capped | feed ↔ site (two-way) |
| snapshots | `/snapshots.json` = 3 | `/snapshots/[slug]/` = 3 | (no desk tool) | feed ↔ site (two-way) |

**`reports.json` = 8 is the three-way anchor** the post-deploy check hard-asserts — the same count clarified in the STATE.md report-count legend.

### Known ceilings / limitations
- **`get_report` browse maxes at 10.** Once Reports exceed 10, the three-way desk count can no longer match the feed via browse — at that point the desk needs pagination or a count endpoint, and the monitor's `agree:reports` desk leg must be revised (it will surface as a desk=10 vs feed>10 mismatch, i.e. it fails loud rather than silently). Tracked here so the failure mode is expected, not mysterious.
- **`get_node` / `get_regional_brief` have no full browse**, so their agreement is feed ↔ site only. A future desk `count`/`list-all` affordance would make them three-way.

## 6. Running the monitor (`tools/surface-health/`)

- **Post-deploy check (deterministic, no AI):** `node tools/surface-health/check.mjs` — feeds parse; counts agree (incl. the reports three-way anchor); IndexNow submit returns **200** (validated-key — *not* 202, the criterion corrected at the F&S publish); sample report URLs return 200. Exit 0 = healthy, 1 = drift.
- **Weekly heartbeat:** `tools/surface-health/worker.js` (+ `wrangler.toml`) — a Cloudflare Worker cron reusing the same check module, recording the **Bing-indexed vs sitemap-count trend** (sitemap count auto; Bing indexed is a manual field, `BING_INDEXED`, baseline **237** as of 2026-06-12). **Code-complete but NOT YET DEPLOYED** — `wrangler deploy` is a separate explicit step.

## 7. Productization (design-time note, not built)

The same monitor is scoped as an **Agent Ready Premium** per-merchant surface-watch. The check is written config-first: `runSurfaceHealth(cfg)` takes a `CONFIG` object (base URL, feeds, agreement set, sample URLs, IndexNow key). The per-merchant version is a different CONFIG passed to the same function — a parameterization, not a rewrite. The merchant version is **not** built in this internal pass.
