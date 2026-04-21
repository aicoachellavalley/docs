# AICV — Strategic State

> This is the STRATEGIC STATE file for AICV.
> Operational/technical state (deploys, session logs, git hashes)
> lives in each operational repo's own STATE.md — not here.
> Update this file weekly or on strategic milestone completion.

The pre-partition snapshot of operational content is preserved at
`STATE.md.pre-partition-2026-04-17.md` for reference.

---

## Live Counts (as of April 19, 2026)

| Metric | Count |
|--------|-------|
| Nodes live | 80 |
| Intelligence briefs live | 131 |
| Snapshots live | 3 |
| Reports live | 1 |

**Brief breakdown:** 4 (2025) · 14 (Jan 2026) · 32 (Feb 2026) · 70 (Mar 2026) · 11 (Apr 2026)

**Nodes:** 80 across nine incorporated cities and adjacent communities — all on v2 schema with `verified`, `status`, `agent_intent` fields. See `TAXONOMY.md` for canonical city/region values.

**Verification ledger:** see `verification/SCHEMA.md` for schema v1; scaffold pending.

---

## Distribution Layer

| Channel | Handle / URL | Role |
|---------|-------------|------|
| Twitter/X | @CoachellaAI | AICV distribution |
| Bluesky | @sunshinefm.bsky.social | SunshineFM human voice |
| Newsletter | Beehiiv (SunshineFM) | 85 editions since June 2024 |

---

## Repositories

Git-tracked AICV repositories. All live under
`github.com/aicoachellavalley/`. Local directory name and
GitHub remote name match EXCEPT where flagged — see each
repo's CLAUDE.md for trap details.

| Local dir | GitHub remote | Purpose |
|---|---|---|
| `aicv-playbook/` | `docs` ⚠ | Workflow brain, schemas, strategic state |
| `com/` | `homepage` ⚠ | aicoachellavalley.com Astro site |
| `org/` | `aicoachellavalley-org` | aicoachellavalley.org |
| `tools/` | `tools` | tools.aicoachellavalley.com |
| `aicv-api/` | `aicv-api` | AIO Tool worker |
| `aicv-mcp/` | `aicv-mcp` | MCP worker |
| `aicv-ic/` | `aicv-ic` | IC backend worker (NEW 2026-04-21) |
| `twitter-worker/` | `twitter-worker` | @CoachellaAI posting (NEW 2026-04-21) |
| `bluesky-worker/` | `bluesky-worker` | @sunshinefm posting (NEW 2026-04-21) |

**⚠ = local directory name diverges from GitHub remote
name.** See the repo's CLAUDE.md for details. Always verify
with `git remote -v` before hardcoding GitHub URLs.

**Not shown:** `agendalink-sync/` is an untracked CV Intel
adapter cordoned 2026-04-21 — see the CV Intel parking
README (linked in Sibling projects section below). The
CV Intel family repos (`cv-intel`, `cvintel-agent`,
`cvintel-cron`) are also under `github.com/aicoachellavalley/`
but belong to CV Intel; see parking README for their status.

---

## Sibling projects

**CV Intel status:** Parked as of 2026-04-20. Workers paused in Cloudflare dashboard (parking action in progress per parking README). `agendalink-sync` cron disabled 2026-04-21. Canonical parking state: `~/cv-intel/README.md`. Do not resume CV Intel work from AICV sessions without reading the parking README first.

---

## North Star Roadmap

_To be populated with strategic milestones and major targets._

---

## How to Update This File

After a strategic milestone or weekly review:
1. Update live counts if a scope threshold crossed
2. Add/remove channels if the distribution layer shifts
3. Record milestone completion in the North Star Roadmap
4. Do NOT add operational state (commit hashes, deploy commands,
   framework versions, script invocations). Those belong in the
   relevant operational repo's STATE.md.
