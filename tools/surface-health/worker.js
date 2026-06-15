/**
 * AICV surface-health heartbeat — Cloudflare Worker (weekly cron).
 *
 * Reuses the SAME deterministic check module as the post-deploy CLI (check.mjs) —
 * no AI in the runtime. On its cron tick it runs the surface-health checks and
 * records the Bing-indexed vs sitemap-count trend.
 *
 * Bing source (per build decision): sitemap count is computed automatically each
 * run; the Bing indexed-count is a MANUALLY-maintained field (env var BING_INDEXED,
 * baseline 237 as of 2026-06-12) until/unless the Bing Webmaster API is wired.
 *
 * Persistence: if a KV namespace is bound as HEARTBEAT, each run is appended to a
 * rolling trend list; otherwise the run is logged only. Deploy is DEFERRED — see
 * wrangler.toml for the cron, vars, and the (commented) KV binding to wire at deploy.
 *
 * NOT YET DEPLOYED. `wrangler deploy` is a separate, explicit step.
 */
import { runSurfaceHealth, AICV_CONFIG } from './check.mjs';

const TREND_KEY = 'trend';
const TREND_MAX = 104; // keep ~2 years of weekly points

async function heartbeat(env) {
  // weekly run does NOT submit to IndexNow (key-file probe only) — avoid weekly submit churn.
  const cfg = { ...AICV_CONFIG, doIndexNowSubmit: false };
  const { ok, checks, heartbeat: hb } = await runSurfaceHealth(cfg);

  const sitemap = hb.sitemap_url_count;
  const bing = env.BING_INDEXED ? Number(env.BING_INDEXED) : null; // manual field; baseline 237
  const failed = checks.filter((c) => !c.ok).map((c) => `${c.name}: ${c.detail}`);

  const record = {
    ts: new Date().toISOString(),
    ok,
    failed_checks: failed,
    sitemap_url_count: sitemap,
    bing_indexed: bing,                                   // manual; null until BING_INDEXED set
    bing_minus_sitemap: bing == null ? null : bing - sitemap, // negative = sitemap URLs not yet indexed
  };

  if (env.HEARTBEAT) {
    const prev = JSON.parse((await env.HEARTBEAT.get(TREND_KEY)) || '[]');
    prev.push(record);
    await env.HEARTBEAT.put(TREND_KEY, JSON.stringify(prev.slice(-TREND_MAX)));
  }

  // surface drift loudly in logs (alerting hook can read these / tail with `wrangler tail`)
  console.log(`[surface-health] ${ok ? 'HEALTHY' : 'DRIFT'} ${JSON.stringify(record)}`);
  if (!ok) console.error(`[surface-health] DRIFT — failed: ${failed.join(' | ')}`);

  return record;
}

export default {
  // weekly cron (see wrangler.toml [triggers])
  async scheduled(event, env, ctx) {
    ctx.waitUntil(heartbeat(env));
  },

  // manual surface: GET /run = run checks now (with submit) and return JSON;
  //                 GET /     = last heartbeat trend from KV (if bound).
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/run') {
      const result = await runSurfaceHealth(AICV_CONFIG); // includes IndexNow submit
      return Response.json(result, { status: result.ok ? 200 : 503 });
    }
    if (url.pathname === '/heartbeat' || url.pathname === '/') {
      const trend = env.HEARTBEAT ? JSON.parse((await env.HEARTBEAT.get(TREND_KEY)) || '[]') : [];
      return Response.json({ baseline_bing_indexed: 237, points: trend });
    }
    return new Response('AICV surface-health worker. GET /run or /heartbeat', { status: 404 });
  },
};
