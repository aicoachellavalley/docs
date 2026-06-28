# Bot-Traffic Recon — AICV surfaces — 2026-06-28

Read-only diagnostic. Draft for review. NOT committed. No production config changed.

Surfaces: aicoachellavalley.com (Pro), aicoachellavalley.org (Free), sunshine.fm (Free).
Account `sunshinefm` / `52a9db008bc2f79a8e51e03797776476`. Auth: existing wrangler OAuth token (sat@sunshine.fm).

---

## PHASE 1 — Does any retained bot-traffic history or MCP call logging already exist?

### → CASE B — only aggregated, limited-retention analytics exist. No raw history. No custom logging. The MCP desk logs NOTHING of its own.

There is **no retained raw request history** (no Logpush, no R2 log-sink) and **no custom analytics
instrumentation anywhere** (no Analytics Engine bindings, no D1/KV/console logging in the MCP worker).
The *only* retained signal is Cloudflare's built-in aggregated analytics (`httpRequestsAdaptiveGroups`,
plan-limited retention) plus built-in Workers invocation analytics — both aggregate, both short-window.

**Prompt-3 gate consequence:** the gate fires on "CASE C, **or CASE B with the MCP worker logging
NOTHING of its own**." The MCP worker logs nothing (Finding 3). **The gate condition is therefore met —
Prompt 3 (instrumentation) would fire.**

### Finding 1 — LOGPUSH: no retained raw-log pipeline

- The Logpush jobs API endpoint (account + all three zones) returns `10000 Authentication error` — the
  current OAuth token lacks the *Logs Read* scope, so the jobs list could not be read directly. **Stated
  plainly, not hidden:** this one endpoint was not directly readable.
- Corroborated two other ways, both conclusive:
  1. **Plan tiers make it structurally impossible.** Zone HTTP-request Logpush is an **Enterprise-only**
     feature. These zones are **Pro / Free / Free** — none is Enterprise. No zone here *can* run an
     `http_requests` Logpush job.
  2. **R2 bucket scan shows no log-sink.** The account's six R2 buckets are all purpose-named content
     stores — `cvintel-code-backup`, `cvintel-raw`, `cvintel-transcripts`, `forever-frozen`,
     `mirage-music`, `sunshinefm-radio-tracks`. None is a Logpush destination receiving NDJSON request
     logs.
- **Verdict: no Logpush, no retained raw logs, no R2 log history. Confirmed.**

### Finding 2 — ANALYTICS ENGINE bindings: none

- `grep -rn "analytics_engine"` across every `wrangler.toml` / `wrangler.jsonc` / `wrangler.json` in the
  whole tree (11 config files) → **zero matches.**
- No worker — not the MCP desk, not the API worker, not IC, not the sunshine-fm workers — writes a custom
  analytics data point anywhere. **Verdict: nothing is writing custom analytics. Confirmed.**

### Finding 3 — MCP WORKER call logging: NONE

- Worker serving `mcp.aicoachellavalley.com/*` is `core/mcp/worker.js` (route confirmed in its
  `wrangler.toml`).
- Its `wrangler.toml` declares **zero storage bindings** — no D1, KV, R2, or Analytics Engine.
- The source confirms it cannot persist anything:
  - `console.` calls: **0**
  - `env` references: **0** — the handler signature is `async fetch(request)`, it does not even *receive*
    `env`, so it physically cannot write to a binding even if one existed.
  - `/mcp` POST → `handleMCP(request)` → returns the JSON-RPC response. Pure stateless request→response.
- **Verdict: the desk records no call history of any kind — not D1, not Analytics Engine, not KV, not even
  an ephemeral `console.log`. Confirmed.**
- **Aggregate fallback (Phase 2):** even though the worker logs nothing itself, Cloudflare's **built-in
  Workers invocation analytics** (`workersInvocationsAdaptive`) still gives an aggregate invocation count
  for the retained window. That is the "is the desk being called" number Phase 2 will pull. It carries no
  per-caller identity beyond what the aggregate dataset exposes.

### What this means

We are effectively blind to history. Whatever AI crawlers or MCP callers hit these surfaces over the past
six months left **no retained record we can recover** — only Cloudflare's rolling aggregate window remains.
Phase 2 can pull that live window; it cannot reconstruct the past. If an ongoing baseline is wanted, it has
to be *built* now (Phase 3 / Prompt 3) — there is nothing already in place to mine.

---

## PHASE 2 — The live window (read-only)

### DATA CONFIDENCE — read this first
- **Measured retention caps (Cloudflare rejected wider queries, stating the exact limit):**
  - **.com (Pro): 8 days** of UA-level HTTP detail (`httpRequestsAdaptiveGroups` cap = 1w1d).
  - **.org (Free): 24 hours.** **sunshine.fm (Free): 24 hours.** (cap = 1d each.)
  - **MCP / Workers invocations (account): 31 days** queried (`workersInvocationsAdaptive` cap = 4w4d/32d).
- **Windows actually pulled:** .com `2026-06-20 → 06-28` (8d) · .org/.fm `2026-06-27 17:30 → 06-28 16:30` (23h) · MCP `2026-05-28 → 06-28` (31d).
- **Two hard caveats:**
  1. **This is a live snapshot. It says NOTHING about the prior six months.** Per Phase 1 (Case B) that history was never recorded and cannot be recovered. The .org/.fm picture in particular is a **single 24-hour slice** — do not read it as a weekly or monthly rate.
  2. `httpRequestsAdaptiveGroups` is **adaptively sampled** — treat every count below as a *representative magnitude*, directionally true, not an exact tally. The surfaces' windows are **asymmetric (8d vs 24h)**, so do **not** compare raw volumes across surfaces.

### Q1 — Are named AI crawlers hitting the surfaces? → YES, clearly. The corpus is being read.

**aicoachellavalley.com — KNOWN AI/LLM crawlers (8 days, sampled):**

| Crawler | Hits (8d) | Seen on hosts |
|---|---:|---|
| Meta-ExternalAgent | 1,305 | com, www, mcp |
| Amazonbot | 1,272 | com, www, mcp |
| ChatGPT-User | 797 | com, www, mcp |
| OAI-SearchBot | 167 | com, www, tools, mcp |
| ClaudeBot | 152 | com, www, mcp |
| Bytespider | 143 | com, www, mcp |
| Applebot | 131 | com, www, mcp |
| PerplexityBot | 66 | com, www, tools, mcp |
| Perplexity-User | 58 | com, mcp |
| GPTBot | 57 | com, www, tools, mcp |
| CCBot | 30 | com, www, mcp |
| Claude-User | 19 | com, www |
| Google-Extended | 10 | com, mcp |
| cohere-ai | 3 | mcp |
| anthropic-ai | 1 | mcp |
| **AI/LLM subtotal** | **≈4,211** | **≈526/day** |

**.com — generic SEO/search (8d):** Googlebot 243 · Bingbot 179 · AhrefsBot 116 · SemrushBot 77 (subtotal ≈615).
*Context: top non-AI noise included a blank-UA bucket (≈9,025), `TLM-Audit-Scanner/1.0` (2,544), `nginx-ssl early hints` (1,540, origin infra). Host:port probe noise (:8880/:2087 etc.) — 1,544 reqs — was excluded from all counts.*

**aicoachellavalley.org — AI/LLM (24h only):** OAI-SearchBot 5 · GPTBot 1 · ChatGPT-User 1 · Meta-ExternalAgent 1 (subtotal 8). SEO: AhrefsBot 19 · Googlebot 11 · Bingbot 3.

**sunshine.fm — AI/LLM (24h only):** Meta-ExternalAgent 78 · ClaudeBot 35 · GPTBot 5 · Amazonbot 5 · Applebot 3 · OAI-SearchBot 3 · Bytespider 1 (subtotal ≈130). SEO: Googlebot 8 · Bingbot 5 · SemrushBot 4 · AhrefsBot 3.

**Read:** on .com the AI-crawler pulse is real and steady — ~500 hits/day across the major frontier crawlers (OpenAI, Anthropic, Perplexity, Meta, Amazon, Apple, Bytedance, Common Crawl, Cohere, Google-Extended all present). Even the Free surfaces show AI crawlers inside a single 24h slice (notably .fm: Meta + Claude). **The supply side of the bet is being consumed.** Prompt 3 will be instrumenting a **river, not a trickle** — at least on .com.

### Q2 — Has the MCP desk been invoked by anyone but us? → Discovered widely; transacted with barely, and only by traffic we can't distinguish from our own.

- **`aicv-mcp` worker: 1,689 total invocations over 31 days** (≈54/day; spikes — Jun 2 = 648, May 30 = 114, Jun 10 = 114, Jun 18 = 82, Jun 21 = 78; all status `success`). For scale it sits mid-pack among account workers (cvintel-web 23,446 · aicv-api 9,415 · aicv-ic 5,803 · **aicv-mcp 1,689** · twitter-worker 1,583).
- **But that 1,689 is NOT 1,689 tool calls.** `workersInvocationsAdaptive` counts *every* HTTP request to the worker. Decomposing the MCP host over the 8-day detail window (method split):
  - **GET 147 + HEAD 3** — discovery/crawler hits (the AI crawlers above were literally hitting `mcp.aicoachellavalley.com` — that's why GPTBot/ClaudeBot/Amazonbot/Meta all list `mcp` as a host).
  - **POST 84** — the *actual* `/mcp` JSON-RPC tool calls. **Every single one carried user-agent `node`.**
  - (Cross-check: the two datasets agree — 8-day invocations ≈232 ≈ httpRequests 234. Numbers are consistent.)
- **us-vs-unknown read:** the only identifiable tool-call signature is generic `node` (Node.js fetch). That is exactly what AICV's own `core/mcp/scripts/smoke-test.mjs` and dev tooling produce. There is **no positively-identifiable external agent transaction** in the data — and, because the worker logs nothing (Phase 1, Finding 3) and `node` is ambiguous, **we also cannot prove their absence.** Honest verdict: **the POST traffic is consistent with being mostly or entirely us; nothing external is provable either way.**
- **The genuinely interesting split:** agents *are discovering* the desk (frontier crawlers GET its discovery endpoint) but are **not transacting** with it. The interactive desk's demand signal is the one number still unanswerable — which is precisely the gap an MCP-call logger (Prompt 3) closes.

### Plain read
- **Is there an AI-crawler pulse this week? — YES.** ~500 frontier-crawler hits/day on .com; AI crawlers present even in a 24h slice of the Free surfaces. The machine-legible corpus is being read.
- **Is the MCP desk being called by anyone but us? — NOT PROVABLY.** It's being *discovered* by external crawlers, but the actual tool-call traffic (84 POSTs/8d, all UA `node`) cannot be distinguished from our own testing. To answer this for real, the desk has to record its own callers — which is the Prompt-3 build.

---

## PHASE 3 — Instrumentation (Stream 2 built & deployed; Stream 1 deferred)

Gate met at Phase 1 (Case B + MCP worker logs nothing). Built under five-stage discipline with human
approval at the propose-diff stop and again before deploy.

### Stream 2 — MCP caller log — DEPLOYED + VERIFIED ✅
- **What:** `core/mcp/worker.js` handler threaded to `(request, env, ctx)`; one envelope-only Analytics
  Engine data point per `/mcp` call via `MCP_LOG` → dataset `aicv_mcp_calls`. Fields: method, tool name, UA,
  cf-ray, country. **Excludes** `params.arguments` (query contents), body, IP, auth headers.
- **Failure-isolated:** write runs in `ctx.waitUntil()` inside `try/catch` behind optional-chaining — unbound
  binding / throw / AE outage all no-op; the JSON-RPC response never depends on the logger.
- **Deployed:** `wrangler deploy` from `core/mcp`, version `91883a7d`. Binding confirmed at upload
  (`env.MCP_LOG (aicv_mcp_calls) → Analytics Engine Dataset`).
- **Verified end-to-end:** posted a live `tools/call` (route_query) + `initialize` with probe UA
  `aicv-verify-probe-2026-06-28`. Desk answered correctly (result, no error). Both rows landed within ~30s
  and **read back through the AE SQL API (HTTP 200 — the 403 risk the recon flagged is cleared)**:
  ```
  initialize | tool=          | ua=aicv-verify-probe-2026-06-28 | US
  tools/call | tool=route_query | ua=aicv-verify-probe-2026-06-28 | US
  ```
  The probe UA is non-`node`, which **demonstrates the us-vs-them detector works** — a non-`node` caller
  surfaces distinctly.
- **Durable read-back:** `core/mcp/OBSERVABILITY.md` holds the SQL query + the `blob3 != 'node'` filter that
  catches the first external transaction.

### Stream 1 — .com crawler log — DEFERRED
`.com` is pure-static Astro (no handler); logging there needs a Pages Function on every request — an
architecture change for retention-only gain (built-in analytics already shows the pulse for 8 days).
Decoupled deliberately; revisit only if 8-day crawler retention proves insufficient.

### Net for the day
From blind-for-six-months to: **supply side validated** (every major AI crawler reading .com) and
**demand-side meter installed** on the desk (recording from 2026-06-28 forward). Historical bot data before
today stays unrecoverable; everything from now on is on the record.

---
*End Phase 3. Holding at the commit gate.*
