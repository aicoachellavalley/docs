# AICV — Current State

Read this at the start of every session before any content operation. Update at end of every session.

---

## Live Counts (as of April 15, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 80 |
| Intelligence briefs live | 129 |
| Snapshots live | 3 |
| Reports live | 1 |
| `stat-briefs` fallback (homepage) | 129 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 70 (Mar 2026) · 9 (Apr 2026)

**Nodes:** 80 across 12 zones — all on v2 schema with `verified`, `status`, `agent_intent` fields.

---

## Active Month Group (docs.json)

Current month group for new briefs: **April 2026**

New briefs append to the top of the April 2026 group in the Intelligence Briefs tab.

When May begins: add a new `May 2026` group at the top. Do not restructure existing groups.

---

## Last Known Commit Hashes

| Repo | Hash | Notes |
|------|------|-------|
| docs (Mintlify) | `705e121` | docs: add related frontmatter schema + relationship types + graph maintenance protocol |
| com (aicoachellavalley.com) | `900f4d9` | feat: retroactive related frontmatter on 10 place-based nodes + fix jacqueline-cochran agent_intent |
| org (aicoachellavalley.org) | `b2a489e` | feat: add 8 concept nodes to graph lookup tables |
| tools (aicv-tools) | deployed April 5 | fix: IR tab plain text CTA, methodology updated |

> Always verify current hash via `git log --oneline -5` before committing. Do not rely on hashes above as current.

---

## Astro Architecture (live April 5, 2026)

**Framework:** Astro v6.1.3, static output
**Repo:** `~/Projects/com/`
**Deploy:** `git push origin main` → Cloudflare auto-builds and deploys
**Build command:** `npm run build`
**Output directory:** `dist/`

**Live routes:**
- `aicoachellavalley.com` — homepage, AIO tool live
- `aicoachellavalley.com/nodes/[slug]` — 65 node pages, Gemini-crawlable, canonical tags set
- `aicoachellavalley.com/snapshots/[slug]` — dynamic, driven by `src/data/snapshots/[slug].json`
- `aicoachellavalley.com/briefs/[slug]` — route ready, not yet populated
- `aicoachellavalley.com/reviews/[slug]` — route ready, not yet populated
- `aicoachellavalley.com/reports/[slug]` — 1 report live (`state-of-ai-q1-2026`)

**Data files:**
- `src/data/snapshots/[slug].json` — one file per snapshot (canonical)
- `src/content/briefs/[slug].mdx` — 126 brief MDX files (Astro Content Collections)
- `src/content/nodes/[slug].mdx` — 65 node MDX files (Astro Content Collections, flattened from city subdirs)
- `src/content/reports/[slug].mdx` — report MDX files (Astro Content Collections)
- `src/data/briefs/` — RETIRED (deleted April 6, 2026)
- `src/data/nodes/` — RETIRED (deleted April 6, 2026)
- Adding a new brief or node = copy MDX to the relevant `src/content/` directory, push. No code changes needed.

**Two snapshots live:**
- `aicoachellavalley.com/snapshots/visit-greater-palm-springs` — D/D/F
- `aicoachellavalley.com/snapshots/gardens-on-el-paseo` — C/D/D

**Snapshot page:** Three tabs — Snapshot (public), Intelligence Review (plain text CTA, no gate), Node (pulls from matching `src/content/nodes/[slug].mdx` via Content Collections).

**Astro v6 render API note:** Use `render(entry)` imported from `astro:content` — NOT `entry.render()`. Applies to all collection templates.

**Report frontmatter rules:**
- `sections` and `tags` must be single-line arrays — `parseFrontmatter()` in build-static-json.cjs cannot handle multi-line YAML arrays (produces `[]` in reports.json)
- Do not use `{#id}` syntax in h2 headings — MDX treats `{...}` as JSX expressions; `{#slug}` is a parse error that breaks the Cloudflare build
- Section IDs are assigned client-side by position: `sections[i]` → i-th h2 in DOM order

**Snapshot schema fields:** slug, entityName, metaTitle, metaDescription, datePublished, dateModified, snapshotLocation, snapshotPeriod, schema, grades, opener, methodology, findings, actions (nullable), top_gaps (nullable), cta, passphrase (nullable — not used)

**Methodology copy (canonical):**
"AICV runs a structured Intelligence Council (IC) for each review. The entity is scored across three dimensions: buyer readiness, competitive positioning, and AI readiness. The IC — a panel of 5 randomly selected frontier AI models (from a portfolio of 30) — reviews each dimension independently, debates the findings, and a regional chairman delivers final scores through AICV's evolving grading framework. What you're reading is the output. This is a cold review. [Entity] has not been notified."

---

## IC Chair Tool

**URL:** `tools.aicoachellavalley.com/ic-chair.html?admin=aicv2026`

**Note:** `?admin=aicv2026` required to show Save Snapshot button. This gate should be removed next session — Save button should always be visible.

**Save Snapshot workflow:**
1. Run full IC synthesis — all three chairman reports
2. Entity Name: clean canonical name only
   ✓ `Visit Greater Palm Springs`
   ✗ `Visit Greater Palm Springs (VGPS) Apr 5`
3. Hit Save Snapshot
4. Copy the JSON record
5. Claude Code: save as new file `src/data/snapshots/[slug].json`
6. `git push origin main` — auto-deploys

**Deploy tools after any change:**
```
cd ~/Projects/tools && npx wrangler pages deploy . --project-name aicv-tools
```

---

## MCP Worker

Deployed version: `72483a7c` (March 26, 2026) — queryVenues optimized: 1 fetch (nodes.json) instead of 57 sequential MDX fetches.

---

## Maintenance Scripts

After any session adding nodes or briefs:

```
node scripts/build-static-json.cjs
```

from `~/Projects/com/` — regenerates `nodes.json`, `briefs.json`, `snapshots.json`, `reports.json` in `public/`. Commit:

```
chore: regenerate static JSON (N nodes, N briefs)
```

Static endpoints (canonical — served from com repo `public/`):
- https://aicoachellavalley.com/nodes.json
- https://aicoachellavalley.com/briefs.json
- https://aicoachellavalley.com/snapshots.json
- https://aicoachellavalley.com/reports.json

---

## Deploy — Cloudflare Pages Properties

**aicoachellavalley.com** — AUTO-DEPLOYS:
```
git push origin main
```

**aicoachellavalley.org** — manual:
```
cd ~/Projects/org && npx wrangler pages deploy . --project-name aicoachellavalley-org
```

**tools.aicoachellavalley.com** — manual:
```
cd ~/Projects/tools && npx wrangler pages deploy . --project-name aicv-tools
```

**sunshine.fm** — manual:
```
cd ~/Projects/sunshine-fm && npx wrangler pages deploy . --project-name sunshine-fm
```

---

## Distribution Layer

| Channel | Handle / URL | Role |
|---------|-------------|------|
| Twitter/X | @CoachellaAI | AICV distribution |
| Bluesky | @sunshinefm.bsky.social | SunshineFM human voice |
| Newsletter | Beehiiv (SunshineFM) | 85 editions since June 2024 |

---

## Agent Discoverability Layer

- `nodes.json` — 79 nodes (frontmatter only)
- `briefs.json` — 126 briefs (frontmatter only)
- `.well-known/mcp.json` — MCP autodiscovery

Regenerate: `node scripts/build-static-json.js` from `~/Projects/docs/`

---

## How to Update This File

After every session:
1. Increment node count if nodes added
2. Increment brief count + monthly breakdown if briefs added
3. Increment snapshot count if snapshots added
4. Update last commit hash for affected repos
5. Update any architecture facts that changed

Commit and push:
```
git add -A && git commit -m "docs: update STATE.md — [date] session" && git push origin main
```
