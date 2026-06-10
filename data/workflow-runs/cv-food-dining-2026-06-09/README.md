# cv-food-dining-category-map — workflow run rescue

Rescued 2026-06-09 from session-scoped storage (workflow journal
`wf_72203d9c-3ce.json` under `~/.claude/projects/`) before cleanup could
destroy the only copies. Raw output of the Tier 2 Food & Dining category-map
workflow; nothing here is schema-validated site content — node seeds fail the
com Zod schema as-is (lowercase `funnel_stages`, missing `agent_intent` /
`verified` / `status`) by design, pending per-entity intake.

## Run

- Workflow: `cv-food-dining-category-map` (runId `wf_72203d9c-3ce`)
- Completed: 2026-06-09, status `completed`, 111 min
- Scale: 258 agents, 9,646,299 total tokens
- Funnel: 15 discovery angles → 211 raw mentions → 157 unique entities → 80 assessed → 68 seeds

## Files

| File | Contents |
|---|---|
| `category-map.json` | Publishable category map: overview, 18 categories, 10 corridors, gap diagnostic, relationships narrative, closing |
| `shortlists.json` | 10 best demo candidates, 10 best revenue candidates, mid-valley weighting note |
| `seeds.json` | 68 node seeds (slug, frontmatter draft, what_it_is, key_facts, convertibility_tier, flags) |
| `ranked-inventory.md` | 68 seeds ranked by reputation-to-visibility gap (was untracked `com/tmp-dining-ranked.md`) |
| `cv-food-dining-category-map-wf_72203d9c-3ce.js` | The workflow script that produced this run, for reproducibility |

## depth/ — evidence substrate (rescued 2026-06-09, second pass)

`depth/` is a verbatim byte-for-byte copy of the run's subagent directory
(`subagents/workflows/wf_72203d9c-3ce/`): `journal.jsonl` (526 lines — every
agent() call's prompt key and structured result, including the 80 per-entity
assessments and adversarial verify-lens records) plus 268 `agent-*.jsonl` full
transcripts and their 268 `agent-*.meta.json` companions. Raw, unparsed,
unfiltered — interpret downstream, never edit in place.

NOT schema-valid content. Never point the com build, a content collection, or
any loader at `depth/`. It is archival evidence only.
