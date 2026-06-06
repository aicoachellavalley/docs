# Recalibration post-mortem — 2026-06-05

The strict recalibration ran. **The result is not what we predicted, because it exposed a deeper measurement issue than the schema/NAP bugs.**

Surfaced before re-aggregate. Recalibrated chunks are in `auditor/chunks/`; pre-recal originals preserved at `auditor/_pre-recal-2026-06-05/chunks/`. Easy revert if needed.

## What happened

The two corrected dimensions land roughly where the spot-checks predicted:

| Dimension | Pre | Post | Δ |
|---|---|---|---|
| `schema_present` | 0.0% | 39.4% | +1,314 |
| `nap_consistent` | 5.0% | 34.4% | +977 |

But tier distribution moved in the **opposite** direction from what we predicted:

| Tier | Pre | Post | Δ |
|---|---|---|---|
| A | 225 | 58 | **−167** |
| B | 1,647 | 1,388 | −259 |
| C | 669 | 1,128 | **+459** |
| D | 792 | 759 | −33 |

Score-shift distribution (post − pre):
- up_3: 0
- up_2: 15
- up_1: 132
- **no_change: 1,686**
- **down: 1,500**

**1,500 records went DOWN in score despite gaining points on schema and NAP.** That shouldn't be possible if the recalibration only updates two dimensions upward.

## Root cause: pre-recal None values inflated the original scoring

Per-dimension True / False / **None** counts in the original chunks:

| Dimension | True | False | None |
|---|---|---|---|
| site_loads | 2,429 | 904 | 0 |
| nap_consistent | 168 | 310 | **2,855** |
| mobile_ready | 2,425 | 908 | 0 |
| schema_present | 0 | 0 | **3,333** |
| og_metadata | 1,244 | 2,089 | 0 |
| faq_present | 438 | 1,700 | 1,195 |
| content_fresh | 271 | 207 | **2,855** |
| citation_density | 323 | 3,010 | 0 |

- **`schema_present` was 100% None.** It was never measured. The "0%" headline came from treating None as not-passing in aggregate stats.
- **`nap_consistent` was 85% None.** Most chunk agents didn't even attempt it.
- **`content_fresh` was 85% None.** Same.
- **`faq_present` was 36% None.**

But the original record scores weren't consistent with either strict-sum or lenient-None-as-pass:

| Score calculation | Matches pre-recal score |
|---|---|
| strict (sum of Trues only) | 38.3% |
| lenient (sum of Trues + Nones) | 15.4% |
| neither | **46.3%** |

**The original chunk agents used ad-hoc score conventions per chunk.** Some treated Nones as passes (counted toward score), some didn't, some used overall judgment. The chunks aren't measuring the same thing under the same rule.

## What the strict recalibration actually did

By recomputing every record's score as `sum(d in SCORED_DIMS if checks[d] is True)`:

1. The 3,333 None values on `schema_present` got replaced with explicit True/False from the new logic (1,314 True, 2,019 False). Most records that lost a "None-counted-as-pass" gained a "True" — net positive **for the few records where the agent had been treating None as pass**.

2. The 2,855 None values on `nap_consistent` got replaced. 995 became True, 1,860 became False (within the fetched subset). Some records where the agent counted None-as-pass now have explicit False, losing a point.

3. **The 2,855 None values on `content_fresh` were NOT touched by the recalibration.** When my strict sum hit them, they evaluated to falsy. Records that had been scoring +1 on content_fresh-as-None now lose that point.

4. **The 1,195 None values on `faq_present` were also NOT touched.** Same downgrade pattern.

So the downgrades come almost entirely from `content_fresh` and `faq_present` — dimensions we didn't touch, where the chunk agents had been giving free passes via None values.

## What this means honestly

The pre-recal "Tier A = 225 (6.2%)" headline was **inflated by ~3-4× by the chunk agents' inconsistent None handling**. A more rigorous measurement of "how many partners pass at least 7 of 8 dimensions" produces **Tier A = 58 (1.7%)**.

That's a more dramatic finding, and a more honest one. The audit's main story shifts:

| Pre-recal headline | Post-recal headline |
|---|---|
| 6.2% of partners are agent-ready (Tier A) | **1.7%** of partners are agent-ready (Tier A) |
| 5% NAP-consistent | **34%** NAP-consistent (a brief footnote, not a headline) |
| 0% schema markup | **39%** schema markup (no longer the dramatic number) |
| Chains underperform indies | _need to recompute_ |
| Wellness leads | _need to recompute_ |

**The really actionable finding shifts from "5% NAP" to "98% of Greater Palm Springs visitor-economy businesses are not yet agent-ready" (only 58 of 3,627 hit Tier A).** That's a stronger and more defensible headline.

## Three paths from here

### (1) Accept the strict result — ★ recommended

Run `reaggregate.py` against the recalibrated chunks. New tier distribution stands. Brief writes from the rigorous numbers:
- Tier A 1.7%, Tier B 38.3%, Tier C 31.1%, Tier D 21.0%, Tier Z 8.1%
- 39% have schema markup (most do)
- 34% have consistent NAP (most don't)
- The audit's main finding becomes: **the rigorous reading is that ~2% are agent-ready; the messy reading per the original (loose) scoring was ~6%. Either way it's small.**

**Pro:** Most honest. Internally consistent. Stronger story for the brief.
**Con:** Pre-recal headline numbers (Tier A 6.2%, NAP 5%, schema 0%) we've been quoting in this thread won't survive. The brief has to lead with the new numbers.

### (2) Hybrid — preserve original tier counts, use only corrected dimension stats

Revert chunks/ to the pre-recal originals (already at `_pre-recal-2026-06-05/chunks/`). Re-emit only `rubric-results-per-dimension.json` with the corrected schema and NAP rates. Tier counts stay at A=225, B=1,647, etc.

**Pro:** Tier headlines we've been describing all session survive.
**Con:** Internal inconsistency. Brief saying "Tier A = 6.2% AND schema pass rate = 39%" doesn't square — the original Tier A was computed against schema = 0%. Anyone reading carefully spots it.

### (3) Re-derive all 8 dimensions strictly

Re-fetch and re-score every dimension under a single consistent convention. Citation_density requires web searches (~$0.01-0.05 per partner × 3,333 = manageable cost but real). Faq_present, content_fresh, og_metadata are deterministic from the homepage HTML and could be done in the same pass.

**Pro:** Cleanest possible result. Everything measured under one rule.
**Con:** Most work. Probably 30-60 min more compute. Sat might find the result similar to Scenario 1 anyway (most None values likely true-False under strict measurement).

## My recommendation

**Scenario 1.** The recalibration didn't fail — it surfaced that the original scoring was conceptually broken. Accepting the strict result is the most defensible path. The audit's story actually gets sharper: "only 58 of 3,627 visitor-economy businesses in Greater Palm Springs hit the agent-ready threshold" is a stronger finding than "6.2% Tier A under a loose scoring rule."

If Sat wants the cleanest possible artifact, Scenario 3 is the formal answer. If credibility-protecting the existing tier headlines matters more than honesty, Scenario 2 keeps the numbers but at a cost.

## What I'm NOT doing

- Running `reaggregate.py` yet — waiting for direction.
- Reverting the recalibrated chunks. They're in `auditor/chunks/` ready to aggregate; originals are safely at `_pre-recal-2026-06-05/chunks/`.
- Touching the existing cuts in `auditor/`. Those still reflect the pre-recal state from yesterday's re-aggregate.

Awaiting decision on which path to commit to.
