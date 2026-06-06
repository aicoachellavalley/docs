# Three verification spot-checks — 2026-06-05

Run by `scripts/verify_findings.py` against `auditor/partners-wide-scan.json` with deterministic sampling (`random.seed(42)`). Full per-record output at `auditor/verify-findings-2026-06-05.json`.

## TL;DR

| Finding | Original | Spot-check | Verdict |
|---|---|---|---|
| `schema_present` | **0.0%** | 4 of 10 flagged-False have JSON-LD ✓ | **Measurement artifact.** Re-derive. |
| `llms_txt_present` | **23.5%** | 9 of 10 flagged-True are real | **Largely valid** (~10% contamination). Optional sharpening. |
| `nap_consistent` | **5.0%** | 6 of 10 flagged-False would pass on re-check | **Measurement artifact.** Re-derive. |

The two strongest brief headlines — NAP 5% and schema 0% — are both wrong as measured. They're real signals, but the magnitudes need recalibration before they ship.

## Detail

### 1. schema_present = 0%

Sampled 10 partners flagged False (2 A / 4 B / 4 C). Of those:

- **4 out of 10 have JSON-LD blocks on their homepage**, with `@type` values squarely in the rubric's stated relevant list:
  - `Harcourts Luxury Real Estate` — `Organization`, `WebSite`, `RealEstateAgent` (Tier A)
  - `Soul of China` — `Restaurant`, `WebSite` (Tier A)
  - `Palm Springs Balloons` — `WebSite`, `TouristAttraction`, `LocalBusiness` (Tier B)
  - `The Wine and Cheese Shop on El Paseo` — `WebSite`, `LocalBusiness` (Tier B)
- 6 of 10 truly have no JSON-LD.

**Conclusion:** rubric implementation bug. The chunk agents' scoring code didn't detect JSON-LD even when present and emitting types from the rubric's own list (`Organization`, `Restaurant`, `LocalBusiness`, `TouristAttraction`). 0% across 3,333 partners is implausible; the real corpus rate from this sample extrapolates to **~40% have JSON-LD**, and **~30-40% would pass the rubric's stated filter**.

Root cause hypothesis: the chunk agents likely fetched the homepage with a request that returned something different from what `curl` or Python's `urllib` returns (e.g., a bot-detection page or a CDN edge cache without the dynamic SEO/schema injection), OR they applied a narrower @type filter than the prompt instructed.

### 2. llms_txt_present = 23.5%

Sampled 10 partners flagged True. Of those:

- **9 out of 10 are real llms.txt files** — text/plain or text/markdown content-type, properly formatted markdown with site descriptions and agent instructions.
- 1 of 10 (`Boomers! Palm Springs`) returned an HTML fallthrough page at /llms.txt.

**Notable finding within the verification:** several real llms.txt files are emitted by `All in One SEO v4.8.5` (a WordPress plugin), e.g., `Angel View Thrift Mart`. This suggests the 23.5% adoption rate is partly driven by plugin defaults rather than active partner awareness — itself a meta-finding worth a sentence in the brief. The agent-readiness wave is arriving via plugin auto-generation, not deliberate operator action.

**Conclusion:** the 23.5% headline is **largely valid**. With ~10% fallthrough contamination, the true rate is closer to **~21-22%**. Marginal correction; doesn't change the story.

### 3. nap_consistent = 5%

Sampled 10 Tier B partners flagged False. Of those:

- **6 out of 10 would pass on re-check** with a more lenient name + phone + city presence check (name substring present, phone digit-sequence present anywhere in HTML, city name present):
  - Katsuyama, Modernway, Palm Mountain Resort & Spa, Dive Palm Springs, The Rock Gallery, Escena Lounge & Grill — all three signals findable on the homepage now.
- 4 of 10 have genuine issues:
  - `Angel View Thrift Mart - Cathedral City` — partner site is the parent `angelview.org` which doesn't mention specific location. Multi-location measurement issue.
  - `Julian Gold Rush Hotel` — site returned HTTP 403 to our re-check (bot-blocked).
  - `Palm Springs Yacht Club at Parker Palm Springs` — name and city present, but the Yacht Club's phone isn't on the parent Parker Palm Springs homepage. Real sub-property NAP mismatch.
  - `Jessup Auto Plaza` — name and city present, phone not findable (likely different formatting on site).

**Conclusion:** rubric implementation bug. The original scoring was too strict — likely required exact-format phone match (e.g., `(760) 326-1234`) instead of normalized-digits comparison, OR didn't consider full-page text. With a more reasonable check (lenient digit-sequence + substring), **at least 60% of flagged-inconsistent records actually have consistent NAP**.

**Real corpus rate is probably 40-60% NAP-consistent, not 5%.** That's still a substantial finding — but a less dramatic headline.

## What this means for the brief

### Relative findings remain robust

Tier distributions, strategic-bucket ordering, and chain-vs-indie are computed from total scores. If the missing schema and NAP signals are restored, **every record's score rises by roughly the same amount**, preserving relative ordering. The bottom line:

- **Wellness still leads.** All buckets would shift up together; Wellness staying ahead is robust.
- **Chains still underperform indies.** The gap (2.16 vs 3.48) is wide enough to survive a +1 or +2 uniform shift in scoring. Chains may even shift LESS than indies on schema (chain corporate sites often emit `Organization` schema), so the gap might narrow but remain.
- **Tier A is understated.** Probably significantly. A meaningful number of records sitting at score 5-6 are actually 7-8 once schema and NAP are correctly counted.

### Absolute findings need recalibration

- **NAP "5%" cannot ship.** Real rate is probably 40-60%. Still useful — "more than half of Greater Palm Springs visitor-economy partners are missing consistent name/phone/city alignment between VGPS and their own site" is a legitimate headline. Just not as dramatic.
- **Schema "0%" cannot ship.** Real rate is probably 30-40%. Honest headline: "most partners have basic JSON-LD, but only ~30-40% emit the kind agents need."
- **llms.txt "23.5%" can ship** with a sentence noting plugin-driven adoption.

## Three recalibration options for Sat

### (a) Conservative: re-derive dimension pass rates only

Re-score the schema_present and nap_consistent dimensions across all 3,333 weburl-eligible records using corrected logic. Re-emit only `rubric-results-per-dimension.json`. Tier assignments stay computed against the buggy original dimensions.

**Pro:** Fast. ~15 min for the network re-fetch.
**Con:** The published dimension pass rates would diverge from the tier counts (which were computed against the buggy dimensions). Brief text has to either ignore tier counts, or note the inconsistency.

### (b) Recommended: re-score + re-aggregate

Re-score schema_present and nap_consistent per record. Recompute total scores. Re-run `reaggregate.py`. Re-emit all six cuts + CSV + wide-scan.json.

**Pro:** Self-consistent. Brief text can cite both tier counts and dimension pass rates without contradiction. Tier A count probably rises meaningfully — better story.
**Con:** ~20-30 min total. Existing chunk-N.jsonl files get updated in place (or new -corrected files written).

### (c) Skip llms.txt resharpening

10% fallthrough contamination on llms.txt — small enough that the existing 23.5% is brief-defensible. Decision: leave llms.txt as-is, or apply content-type/content-pattern check for a slightly more honest ~21%?

## My recommendation

**Option (b)** for schema + NAP. Re-score those two dimensions only (other six are presumed correct), recompute totals, re-aggregate. The tier shifts are likely to be substantial enough that the brief gets a stronger story — and shipping internally-inconsistent numbers (a la option a) creates a credibility risk if anyone audits.

**Skip llms.txt resharpening.** 23.5% is the right answer ±2 points. The plugin-driven adoption note is worth keeping in the brief regardless.

Awaiting decision.
