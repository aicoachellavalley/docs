#!/usr/bin/env node
/**
 * AICV surface-health check — deterministic, NO AI.
 *
 * Asserts the AICV agent surfaces are mutually coherent:
 *   1. FEEDS PARSE     — every machine feed + llms.txt + sitemap.xml fetches and parses.
 *   2. COUNT AGREEMENT — for each indexed feed, the count AGREES across
 *                        feed JSON  <->  rendered site pages (sitemap)  <->  MCP desk.
 *                        reports.json is the three-way anchor and is hard-asserted == 8
 *                        (the canon count legended in STATE.md). nodes/briefs/snapshots
 *                        are feed<->site two-way (their desk tools have no full browse —
 *                        get_node has no browse mode; get_regional_brief browse is limit-capped).
 *   3. INDEXNOW        — a validated-key submit returns HTTP 200 (NOT 202; corrected criterion,
 *                        F&S publish 2026-06-14) and the key file is live.
 *   4. SAMPLE URLS     — a sample of canonical report URLs return 200.
 *
 * Exit 0 = healthy, 1 = drift/failure. The CONFIG object is the only thing that
 * changes per surface — the Agent-Ready-Premium per-merchant watch is a different
 * CONFIG passed to runSurfaceHealth(), not a rewrite. The runtime carries no model.
 *
 * Usage: node check.mjs            (checks the AICV .com canon below)
 *        import { runSurfaceHealth, AICV_CONFIG } from './check.mjs'   (worker reuse)
 */

export const AICV_CONFIG = {
  base: 'https://aicoachellavalley.com',
  mcp: 'https://mcp.aicoachellavalley.com/mcp',
  indexNowKey: 'a0637c7110a38cb16503aceee7e1a289',
  // feeds that must fetch + parse (arrays unless noted). stats is an object.
  feeds: [
    { name: 'reports', path: '/reports.json', kind: 'array' },
    { name: 'nodes', path: '/nodes.json', kind: 'array' },
    { name: 'briefs', path: '/briefs.json', kind: 'array' },
    { name: 'snapshots', path: '/snapshots.json', kind: 'array' },
    { name: 'stats', path: '/stats.json', kind: 'object' },
  ],
  // text feeds: fetch 200 + non-empty
  textFeeds: ['/llms.txt', '/sitemap.xml', '/robots.txt'],
  // count-agreement set: feed JSON <-> sitemap page prefix <-> (optional) MCP desk browse
  agreement: [
    { key: 'reports', feed: '/reports.json', prefix: '/reports/', anchor: 8,
      desk: { tool: 'get_report', args: { limit: 10 } } }, // browse default 5 / max 10; limit:10 captures all while <= 10
    { key: 'nodes', feed: '/nodes.json', prefix: '/nodes/', desk: null },
    { key: 'briefs', feed: '/briefs.json', prefix: '/briefs/', desk: null },
    { key: 'snapshots', feed: '/snapshots.json', prefix: '/snapshots/', desk: null },
  ],
  sampleUrls: [
    '/reports/agent-mapped-talent-workforce-coachella-valley/',
    '/reports/agent-mapped-family-schooling-coachella-valley/',
    '/reports/methodology-agent-mapped-census/',
  ],
  indexNowProbeUrl: '/', // an owned, idempotent URL to ping; expect HTTP 200
  doIndexNowSubmit: true, // weekly heartbeat passes false (key-file probe only)
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// fetch with one retry on transient (network throw / non-2xx) to absorb cold-start blips.
async function fetchRetry(url, opts = {}, parse = 'text') {
  let lastErr;
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      const res = await fetch(url, opts);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return parse === 'json' ? await res.json() : await res.text();
    } catch (err) {
      lastErr = err;
      if (attempt === 1) await sleep(1500);
    }
  }
  throw lastErr;
}

// MCP desk tools/call — Streamable HTTP requires the dual Accept header. Parses
// result.content[0].text as JSON. Retries once (cold-start), mirroring aicv-mcp smoke-test.
async function callDesk(endpoint, name, args = {}) {
  const req = { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } };
  let lastErr;
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' },
        body: JSON.stringify(req),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = await res.json();
      if (body.error) throw new Error(`JSON-RPC ${body.error.code}: ${body.error.message}`);
      const text = body.result?.content?.[0]?.text;
      if (typeof text !== 'string') throw new Error('no result.content[0].text');
      return JSON.parse(text);
    } catch (err) {
      lastErr = err;
      if (attempt === 1) await sleep(1500);
    }
  }
  throw lastErr;
}

// count sitemap pages under a prefix, excluding the section index page itself
// (e.g. /reports/[slug]/ counts; the bare /reports/ index does not).
function countPrefix(locs, prefix) {
  const bare = prefix.replace(/\/$/, '');
  return locs.filter((l) => l.includes(prefix) && !l.replace(/\/$/, '').endsWith(bare)).length;
}

/**
 * Run the full surface-health check. Returns { ok, checks:[{name, ok, detail}], heartbeat }.
 * Pure (fetch only) so a Cloudflare Worker can import and run it on a cron.
 */
export async function runSurfaceHealth(cfg = AICV_CONFIG) {
  const checks = [];
  const add = (name, ok, detail) => checks.push({ name, ok, detail });

  // 1. FEEDS PARSE
  const feedData = {};
  for (const f of cfg.feeds) {
    try {
      const d = await fetchRetry(cfg.base + f.path, {}, 'json');
      const okShape = f.kind === 'array' ? Array.isArray(d) : d && typeof d === 'object';
      if (!okShape) throw new Error(`unexpected shape (${typeof d})`);
      feedData[f.name] = d;
      add(`feed:${f.name}`, true, `parsed ${Array.isArray(d) ? d.length + ' entries' : 'object'}`);
    } catch (err) {
      add(`feed:${f.name}`, false, `FETCH/PARSE FAILED: ${err.message}`);
    }
  }
  let sitemapXml = '';
  for (const t of cfg.textFeeds) {
    try {
      const txt = await fetchRetry(cfg.base + t, {}, 'text');
      if (!txt || txt.length < 10) throw new Error('empty');
      if (t === '/sitemap.xml') sitemapXml = txt;
      add(`feed:${t}`, true, `${txt.length} bytes`);
    } catch (err) {
      add(`feed:${t}`, false, `FAILED: ${err.message}`);
    }
  }

  // 2. COUNT AGREEMENT
  const locs = sitemapXml ? [...sitemapXml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim()) : [];
  for (const a of cfg.agreement) {
    try {
      const feed = feedData[a.key];
      if (!Array.isArray(feed)) throw new Error('feed missing/not array (see feed check)');
      const feedCount = feed.length;
      const siteCount = countPrefix(locs, a.prefix);
      let deskCount = null;
      if (a.desk) {
        const arr = await callDesk(cfg.mcp, a.desk.tool, a.desk.args);
        if (!Array.isArray(arr)) throw new Error(`desk ${a.desk.tool} did not return an array`);
        deskCount = arr.length;
      }
      const parts = [`feed=${feedCount}`, `site=${siteCount}`];
      if (deskCount !== null) parts.push(`desk=${deskCount}`);
      const set = [feedCount, siteCount, ...(deskCount !== null ? [deskCount] : [])];
      const agree = set.every((n) => n === set[0]);
      const anchorOk = a.anchor == null || feedCount === a.anchor;
      const ok = agree && anchorOk;
      let detail = parts.join(' ');
      if (a.anchor != null) detail += ` | anchor=${a.anchor}${anchorOk ? '' : ' MISMATCH'}`;
      if (!agree) detail += ' | COUNTS DISAGREE';
      add(`agree:${a.key}`, ok, detail);
    } catch (err) {
      add(`agree:${a.key}`, false, `FAILED: ${err.message}`);
    }
  }

  // 3. INDEXNOW (key file live + validated-key submit == 200, not 202)
  try {
    const keyUrl = `${cfg.base}/${cfg.indexNowKey}.txt`;
    const res = await fetch(keyUrl);
    add('indexnow:keyfile', res.ok, `key file HTTP ${res.status}`);
  } catch (err) {
    add('indexnow:keyfile', false, `key file FAILED: ${err.message}`);
  }
  if (cfg.doIndexNowSubmit) {
    try {
      const u = encodeURIComponent(cfg.base + cfg.indexNowProbeUrl);
      const res = await fetch(`https://api.indexnow.org/indexnow?url=${u}&key=${cfg.indexNowKey}`);
      const ok = res.status === 200; // validated key returns 200, NOT 202
      add('indexnow:submit', ok, `submit HTTP ${res.status}${res.status === 202 ? ' (202 = key NOT validated — investigate)' : ''}`);
    } catch (err) {
      add('indexnow:submit', false, `submit FAILED: ${err.message}`);
    }
  }

  // 4. SAMPLE URLS 200
  for (const path of cfg.sampleUrls) {
    try {
      const res = await fetch(cfg.base + path, { method: 'HEAD' });
      add(`url:${path}`, res.ok, `HTTP ${res.status}`);
    } catch (err) {
      add(`url:${path}`, false, `FAILED: ${err.message}`);
    }
  }

  // heartbeat datum (sitemap count auto; Bing indexed is a manually-maintained field — see worker)
  const heartbeat = { sitemap_url_count: locs.length };

  const ok = checks.every((c) => c.ok);
  return { ok, checks, heartbeat };
}

// CLI entry (skipped when imported by the Worker; guarded so `process` absence in Workers is safe)
const isCli = typeof process !== 'undefined' && Array.isArray(process.argv) && process.argv[1] && import.meta.url === `file://${process.argv[1]}`;
if (isCli) {
  const { ok, checks, heartbeat } = await runSurfaceHealth();
  for (const c of checks) console.log(`  ${c.ok ? 'PASS' : 'FAIL'}  ${c.name.padEnd(22)} ${c.detail}`);
  console.log(`\n  heartbeat: sitemap_url_count=${heartbeat.sitemap_url_count}`);
  console.log(`\n${ok ? '✅ ALL CHECKS PASS' : '❌ SURFACE-HEALTH DRIFT DETECTED'} (${checks.filter((c) => c.ok).length}/${checks.length})`);
  process.exitCode = ok ? 0 : 1;
}
