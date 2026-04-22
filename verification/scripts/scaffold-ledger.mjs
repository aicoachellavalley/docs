#!/usr/bin/env node
/**
 * scaffold-ledger.mjs
 *
 * Scaffolds one verification ledger entry per AICV content item:
 *   - com/nodes/<slug>.json     per com/src/content/nodes/*.mdx
 *   - com/briefs/<slug>.json    per com/src/content/briefs/*.mdx
 *   - com/reports/<slug>.json   per com/src/content/reports/*.mdx
 *   - com/reviews/<slug>.json   per entry in com/public/reviews.json
 *   - org/<slug>.json           per slug in VW_ORDER ∪ ZONE_MAP keys
 *                               (Shape A if com node exists, Shape B otherwise)
 *   - org/_landing.json         placeholder (type: "page")
 *
 * Pass --dry-run to print a report + sample entries without writing files.
 *
 * Reads org/index.html's static VW_ORDER / ZONE_MAP / SUB_MAP structures
 * only — does NOT execute the retired docs.json runtime fetch.
 */

import {
  readdirSync, readFileSync, writeFileSync, mkdirSync, existsSync,
} from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
// scripts/ → verification/ → aicv-playbook/ → Projects/
const playbookVerification = resolve(__dirname, '..');
const projectsRoot = resolve(playbookVerification, '..', '..');
const comRoot = resolve(projectsRoot, 'com');
const orgRoot = resolve(projectsRoot, 'org');

const TODAY = '2026-04-19';
const DRY_RUN = process.argv.includes('--dry-run');

// ─────────────────────────────────────────────────────────────
// Minimal YAML frontmatter parser
// Handles the conventions used in AICV .mdx files:
//   - scalar values (quoted or bare)
//   - inline arrays: key: ["a", "b"]
//   - multi-line lists of scalars or nested objects (for `related`)
// Not a full YAML parser — deliberately tight scope.
// ─────────────────────────────────────────────────────────────

function parseFrontmatter(source) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, body: source };
  return { frontmatter: parseYaml(match[1]), body: match[2] };
}

function stripQuotes(s) {
  if (s == null) return s;
  const t = s.trim();
  if ((t.startsWith('"') && t.endsWith('"')) ||
      (t.startsWith("'") && t.endsWith("'"))) {
    return t.slice(1, -1);
  }
  return t;
}

function coerceScalar(raw) {
  const t = raw.trim();
  if (t === 'true') return true;
  if (t === 'false') return false;
  if (t === 'null' || t === '') return null;
  return stripQuotes(t);
}

function parseYaml(text) {
  const out = {};
  const lines = text.split(/\r?\n/);
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const m = line.match(/^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/);
    if (!m) { i++; continue; }
    const key = m[1];
    const rest = m[2];

    if (rest !== '') {
      // inline value
      if (rest.startsWith('[') && rest.endsWith(']')) {
        const inner = rest.slice(1, -1).trim();
        out[key] = inner
          ? inner.split(',').map(s => stripQuotes(s.trim())).filter(Boolean)
          : [];
      } else {
        out[key] = coerceScalar(rest);
      }
      i++;
      continue;
    }

    // multi-line: peek next line for list indicator
    i++;
    if (i >= lines.length) { out[key] = null; break; }
    const peek = lines[i];
    const listMatch = peek.match(/^(\s+)-\s+(.*)$/);
    if (!listMatch) { out[key] = null; continue; }

    const listIndent = listMatch[1];
    const listRe = new RegExp(`^${listIndent}-\\s+(.*)$`);
    const items = [];

    while (i < lines.length) {
      const ln = lines[i];
      const lm = ln.match(listRe);
      if (!lm) break;
      const first = lm[1];

      // nested object: first token is "key: value"
      const objKv = first.match(/^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$/);
      if (objKv) {
        const obj = { [objKv[1]]: coerceScalar(objKv[2]) };
        i++;
        // continuation keys have deeper indent
        const contRe = new RegExp(
          `^${listIndent}\\s+([a-zA-Z_][a-zA-Z0-9_]*):\\s*(.*)$`
        );
        while (i < lines.length) {
          const cm = lines[i].match(contRe);
          if (!cm) break;
          obj[cm[1]] = coerceScalar(cm[2]);
          i++;
        }
        items.push(obj);
      } else {
        items.push(stripQuotes(first));
        i++;
      }
    }
    out[key] = items;
  }

  return out;
}

// ─────────────────────────────────────────────────────────────
// Claim extraction
// Scope: section-bounded. We look for a known set of section
// headers and extract one claim per statement-sized unit (sentence
// in prose, bullet in a list). Tables and sub-subsections skipped.
// Fallback: if nothing matched, use first prose paragraph.
// ─────────────────────────────────────────────────────────────

const CLAIM_SECTIONS = [
  'What It Is', 'Key Facts', 'Overview', 'What This Is', 'Key Details',
  'Signal', 'Context', 'What Happened', 'Summary',
];

function extractClaims(body) {
  const headerRe = new RegExp(
    `^##\\s+(${CLAIM_SECTIONS.map(escapeRe).join('|')})\\s*$`,
    'gmi'
  );
  const sections = [];
  let m;
  while ((m = headerRe.exec(body)) !== null) {
    sections.push({ title: m[1], start: m.index });
  }

  const claims = [];
  for (let s = 0; s < sections.length; s++) {
    const start = sections[s].start;
    const end = s + 1 < sections.length
      ? sections[s + 1].start
      : nextSectionStart(body, start + 3) ?? body.length;
    const sectionBody = body.slice(start, end);
    claims.push(...parseSection(sectionBody));
  }

  // fallback: no recognized sections — use first paragraph of body
  if (claims.length === 0) {
    const firstPara = firstProseParagraph(body);
    if (firstPara) claims.push(...splitSentences(firstPara).map(makeClaim).filter(Boolean));
  }

  // dedupe claim_id
  const seen = new Set();
  for (const c of claims) {
    let id = c.claim_id || 'claim';
    let suffix = 2;
    const base = id;
    while (seen.has(id)) id = `${base}-${suffix++}`;
    c.claim_id = id;
    seen.add(id);
  }
  return claims;
}

function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function nextSectionStart(body, fromIdx) {
  const rest = body.slice(fromIdx);
  const idx = rest.search(/\n##\s/);
  return idx === -1 ? null : fromIdx + idx;
}

function parseSection(sectionText) {
  // drop the header line
  const nl = sectionText.indexOf('\n');
  if (nl === -1) return [];
  const content = sectionText.slice(nl + 1).trim();

  const claims = [];
  const blocks = content.split(/\n\s*\n+/);

  for (const raw of blocks) {
    const block = raw.trim();
    if (!block) continue;
    if (block.startsWith('|')) continue;          // table — skip v1
    if (block.startsWith('###')) continue;        // sub-subsection — skip v1
    if (/^(none\.?|none yet\.?)$/i.test(block)) continue;

    if (/^[-*]\s/.test(block)) {
      // bullet list
      const bullets = block.split(/\n(?=[-*]\s)/);
      for (const b of bullets) {
        const text = cleanText(b.replace(/^[-*]\s+/, ''));
        const c = makeClaim(text, { allowShort: true });
        if (c) claims.push(c);
      }
    } else {
      // prose paragraph
      const text = cleanText(block);
      for (const s of splitSentences(text)) {
        const c = makeClaim(s);
        if (c) claims.push(c);
      }
    }
  }
  return claims;
}

function firstProseParagraph(body) {
  // skip the H1 and any blank lines
  const lines = body.split(/\r?\n/);
  let buf = [];
  for (const line of lines) {
    const t = line.trim();
    if (!t) { if (buf.length) break; else continue; }
    if (t.startsWith('#')) { if (buf.length) break; else continue; }
    if (t.startsWith('|') || t.startsWith('import ')) continue;
    if (t.startsWith('**Date:**')) continue;
    buf.push(t);
  }
  return cleanText(buf.join(' '));
}

function cleanText(text) {
  return text
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, '')       // MDX comments
    .replace(/\{[^{}]*\}/g, '')                 // JSX expressions
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')    // markdown links → label
    .replace(/\*\*([^*]+)\*\*/g, '$1')          // bold markers
    .replace(/`([^`]+)`/g, '$1')                // inline code
    .replace(/\s+/g, ' ')
    .trim();
}

function splitSentences(text) {
  if (!text) return [];
  return text
    .split(/(?<=[.!?])\s+(?=[A-Z(])/)
    .map(s => s.trim())
    .filter(Boolean);
}

function makeClaim(text, opts = {}) {
  if (!text) return null;
  const minLen = opts.allowShort ? 6 : 20;
  if (text.length < minLen) return null;
  if (text.length > 500) return null;
  if (text.startsWith('#')) return null;
  return {
    claim_id: deriveClaimId(text),
    claim_text: text,
    status: 'unverified',
    sources: [],
    date_verified: null,
  };
}

function deriveClaimId(text) {
  const words = text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter(w => w && !STOPWORDS.has(w));
  const slug = words.slice(0, 6).join('-').slice(0, 60);
  return slug || 'claim';
}

const STOPWORDS = new Set([
  'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of',
  'for', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
  'have', 'has', 'had', 'do', 'does', 'did', 'as', 'it', 'its', 'that',
  'this', 'these', 'those',
]);

// ─────────────────────────────────────────────────────────────
// Connection extraction (com/ entries)
// ─────────────────────────────────────────────────────────────

const RELATION_MAP = {
  supports: 'part_of',
  part_of: 'part_of',
  related_to: 'related_to',
  supersedes: 'supersedes',
  references: 'references',
  routes_to: 'routes_to',
};

function extractConnections(frontmatter, body, knownSlugs) {
  const conns = [];
  const seen = new Set();

  // From frontmatter.related
  if (Array.isArray(frontmatter.related)) {
    for (const rel of frontmatter.related) {
      if (!rel || typeof rel !== 'object' || !rel.slug) continue;
      const type = RELATION_MAP[rel.type] || 'references';
      const key = `${rel.slug}|${type}`;
      if (seen.has(key)) continue;
      seen.add(key);
      conns.push({
        target_id: rel.slug,
        target_surface: 'com',
        direction: 'outgoing',
        type,
        notes: `Frontmatter: related.type=${rel.type ?? 'n/a'} → ${rel.slug}`,
      });
    }
  }

  // From body markdown links to /nodes/ /briefs/ /reports/
  const linkRe = /\[[^\]]+\]\(\/(nodes|briefs|reports)\/([a-z0-9-]+)\/?\)/g;
  let m;
  while ((m = linkRe.exec(body)) !== null) {
    const slug = m[2];
    if (!knownSlugs.has(slug)) continue;
    const key = `${slug}|references`;
    if (seen.has(key)) continue;
    seen.add(key);
    conns.push({
      target_id: slug,
      target_surface: 'com',
      direction: 'outgoing',
      type: 'references',
      notes: 'Body Markdown link',
    });
  }
  return conns;
}

// ─────────────────────────────────────────────────────────────
// Per-type scaffolders
// ─────────────────────────────────────────────────────────────

function scaffoldComMdx(mdxPath, type, knownSlugs) {
  const raw = readFileSync(mdxPath, 'utf8');
  const { frontmatter, body } = parseFrontmatter(raw);
  const slug = basename(mdxPath, '.mdx');
  const title = frontmatter.title || slug;
  const pathSeg = type === 'node' ? 'nodes'
                : type === 'brief' ? 'briefs'
                : type === 'report' ? 'reports'
                : `${type}s`;
  return {
    schema_version: 'v1',
    id: slug,
    surface: 'com',
    type,
    title,
    canonical_url: `https://aicoachellavalley.com/${pathSeg}/${slug}/`,
    last_reviewed: TODAY,
    review_method: 'automated',
    claims: extractClaims(body),
    connections: extractConnections(frontmatter, body, knownSlugs),
    notes: 'Scaffolded 2026-04-19 from frontmatter + body extraction. Verification pass pending.',
  };
}

function scaffoldReview(review) {
  const slug = review.slug || 'untitled';
  const title = review.title || slug;
  const claims = [];
  if (review.grades && typeof review.grades === 'object') {
    for (const [dim, grade] of Object.entries(review.grades)) {
      claims.push({
        claim_id: `grade-${dim}`,
        claim_text: `${title} received a ${grade} grade on ${dim.replace(/_/g, ' ')} in the AICV Intelligence Council review.`,
        status: 'unverified',
        sources: [],
        date_verified: null,
      });
    }
  }
  if (review.review_date) {
    claims.push({
      claim_id: 'review-date',
      claim_text: `${title} was reviewed on ${review.review_date}.`,
      status: 'unverified',
      sources: [],
      date_verified: null,
    });
  }
  const connections = [];
  if (review.slug) {
    connections.push({
      target_id: review.slug,
      target_surface: 'com',
      direction: 'outgoing',
      type: 'references',
      notes: 'Review subject node',
    });
  }
  return {
    schema_version: 'v1',
    id: slug,
    surface: 'com',
    type: 'review',
    title,
    canonical_url: review.snapshot_url || `https://aicoachellavalley.com/reviews/${slug}/`,
    last_reviewed: TODAY,
    review_method: 'automated',
    claims,
    connections,
    notes: 'Scaffolded 2026-04-19 from public/reviews.json. Reviews not yet migrated to content collection — shallow entry. Verification pass pending.',
  };
}

function scaffoldOrgShapeA(slug, title, zoneMap, subMap) {
  return {
    schema_version: 'v1',
    id: slug,
    surface: 'org',
    type: 'visualization_of',
    title,
    canonical_ledger_entry: `entries/com/nodes/${slug}.json`,
    last_reviewed: TODAY,
    review_method: 'automated',
    connections: orgGraphConnections(slug, zoneMap, subMap),
    notes: null,
  };
}

function scaffoldOrgShapeB(slug, zoneMap, subMap) {
  return {
    schema_version: 'v1',
    id: slug,
    surface: 'org',
    type: 'node',
    title: slug,
    canonical_url: `https://aicoachellavalley.com/nodes/${slug}/`,
    last_reviewed: TODAY,
    review_method: 'unverified',
    claims: [],
    connections: orgGraphConnections(slug, zoneMap, subMap),
    notes: `Shape B — no com/src/content/nodes/${slug}.mdx found. Needs manual review: either create a com/ node to back this graph reference, or remove the reference from org/index.html.`,
  };
}

function orgGraphConnections(slug, zoneMap, subMap) {
  const conns = [];
  for (const [key, zone] of Object.entries(zoneMap)) {
    const parts = key.split('/');
    if (parts.length === 2 && parts[1] === slug) {
      conns.push({
        target_id: zone,
        target_surface: 'org',
        direction: 'outgoing',
        type: 'located_in',
        notes: `ZONE_MAP: ${key} → ${zone}`,
      });
      break;
    }
  }
  if (subMap[slug]) {
    conns.push({
      target_id: subMap[slug],
      target_surface: 'org',
      direction: 'outgoing',
      type: 'part_of',
      notes: `SUB_MAP: ${slug} → ${subMap[slug]}`,
    });
  }
  return conns;
}

function orgLandingPlaceholder() {
  return {
    schema_version: 'v1',
    id: '_landing',
    surface: 'org',
    type: 'page',
    title: 'AI Coachella Valley — Nonprofit Landing Page',
    canonical_url: 'https://aicoachellavalley.org/',
    last_reviewed: TODAY,
    review_method: 'unverified',
    claims: [],
    connections: [],
    notes: "Placeholder entry. Landing page makes aggregate claims that require dedicated Layer 2 extraction. Claims identified during Phase 4 design (pending extraction): workshop count (30+), participant count (300+), cities covered (9), pledges signed (12+), partner relationships (Cal State San Bernardino, Desert Community Foundation, College of the Desert, Palm Desert Chamber of Commerce, Journalism Innovation Fund), three programs (AI Builder Workshops, Community Build System, Workforce Bridge Marketplace), and node count claim (78 nodes live) which contradicts com/'s verified 80. Node count contradiction is caused by org/index.html fetching graph data from the retired Mintlify docs.json at github.com/aicoachellavalley/docs/main/docs.json — root architectural issue documented for Phase 6 investigation.",
  };
}

// ─────────────────────────────────────────────────────────────
// org/index.html static-structure extraction
// ─────────────────────────────────────────────────────────────

function parseOrgGraph(htmlPath) {
  const html = readFileSync(htmlPath, 'utf8');

  // VW_ORDER
  const vwMatch = html.match(/const\s+VW_ORDER\s*=\s*\[([^\]]+)\]/);
  const vwOrder = vwMatch
    ? vwMatch[1]
        .split(',')
        .map(s => s.trim().replace(/^['"]|['"]$/g, ''))
        .filter(Boolean)
    : [];

  // ZONE_MAP — non-greedy, multi-line
  const zm = html.match(/const\s+ZONE_MAP\s*=\s*\{([\s\S]*?)\};/);
  const zoneMap = {};
  if (zm) {
    for (const p of zm[1].matchAll(/'([^']+)'\s*:\s*'([^']+)'/g)) {
      zoneMap[p[1]] = p[2];
    }
  }

  // SUB_MAP
  const sm = html.match(/const\s+SUB_MAP\s*=\s*\{([\s\S]*?)\};/);
  const subMap = {};
  if (sm) {
    for (const p of sm[1].matchAll(/'([^']+)'\s*:\s*'([^']+)'/g)) {
      subMap[p[1]] = p[2];
    }
  }

  return { vwOrder, zoneMap, subMap };
}

// ─────────────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────────────

function main() {
  const nodeDir = resolve(comRoot, 'src/content/nodes');
  const briefDir = resolve(comRoot, 'src/content/briefs');
  const reportDir = resolve(comRoot, 'src/content/reports');
  const reviewsPath = resolve(comRoot, 'public/reviews.json');
  const orgIndexPath = resolve(orgRoot, 'index.html');

  const nodeFiles = readdirSync(nodeDir).filter(f => f.endsWith('.mdx'));
  const briefFiles = readdirSync(briefDir).filter(f => f.endsWith('.mdx'));
  const reportFiles = existsSync(reportDir)
    ? readdirSync(reportDir).filter(f => f.endsWith('.mdx'))
    : [];
  const reviewsData = JSON.parse(readFileSync(reviewsPath, 'utf8'));
  const reviews = Array.isArray(reviewsData.reviews) ? reviewsData.reviews : [];

  const nodeSlugs = new Set(nodeFiles.map(f => f.replace(/\.mdx$/, '')));
  const briefSlugs = new Set(briefFiles.map(f => f.replace(/\.mdx$/, '')));
  const reportSlugs = new Set(reportFiles.map(f => f.replace(/\.mdx$/, '')));
  const knownSlugs = new Set([...nodeSlugs, ...briefSlugs, ...reportSlugs]);

  const { vwOrder, zoneMap, subMap } = parseOrgGraph(orgIndexPath);

  const failures = [];
  const results = {
    com_nodes: [], com_briefs: [], com_reports: [], com_reviews: [],
    org_shape_a: [], org_shape_b: [], org_landing: [],
  };

  const runCom = (files, dir, type, bucket) => {
    for (const f of files) {
      try {
        bucket.push(scaffoldComMdx(resolve(dir, f), type, knownSlugs));
      } catch (e) {
        failures.push({ file: f, type, error: e.message });
      }
    }
  };

  runCom(nodeFiles, nodeDir, 'node', results.com_nodes);
  runCom(briefFiles, briefDir, 'brief', results.com_briefs);
  runCom(reportFiles, reportDir, 'report', results.com_reports);

  for (const r of reviews) {
    try { results.com_reviews.push(scaffoldReview(r)); }
    catch (e) { failures.push({ file: r.slug || '?', type: 'review', error: e.message }); }
  }

  // Org: union of VW_ORDER and ZONE_MAP slugs (after zone/slug split)
  const orgSlugs = new Set(vwOrder);
  for (const key of Object.keys(zoneMap)) {
    const parts = key.split('/');
    if (parts.length === 2) orgSlugs.add(parts[1]);
    else orgSlugs.add(parts[0]);
  }

  for (const slug of [...orgSlugs].sort()) {
    if (nodeSlugs.has(slug)) {
      try {
        const mdxPath = resolve(nodeDir, `${slug}.mdx`);
        const { frontmatter } = parseFrontmatter(readFileSync(mdxPath, 'utf8'));
        const title = frontmatter.title || slug;
        results.org_shape_a.push(scaffoldOrgShapeA(slug, title, zoneMap, subMap));
      } catch (e) {
        failures.push({ file: slug, type: 'org-shape-a', error: e.message });
      }
    } else {
      results.org_shape_b.push(scaffoldOrgShapeB(slug, zoneMap, subMap));
    }
  }

  results.org_landing.push(orgLandingPlaceholder());

  // Audit: com/ nodes missing from org graph (Phase 6 preview)
  const missingFromOrg = [...nodeSlugs].filter(s => !orgSlugs.has(s)).sort();

  printReport(results, failures, missingFromOrg);
  printSample(results);
  printProposedFiles(results);

  if (DRY_RUN) {
    console.log('\n[dry-run] no files written.');
    return;
  }

  writeAll(results);
  console.log('\nScaffold complete.');
}

function printReport(r, failures, missingFromOrg) {
  console.log('========== SCAFFOLD REPORT ==========');
  console.log(`com/nodes:    ${r.com_nodes.length}`);
  console.log(`com/briefs:   ${r.com_briefs.length}`);
  console.log(`com/reports:  ${r.com_reports.length}`);
  console.log(`com/reviews:  ${r.com_reviews.length}`);
  console.log(`org Shape A:  ${r.org_shape_a.length}`);
  console.log(`org Shape B:  ${r.org_shape_b.length}`);
  console.log(`org _landing: ${r.org_landing.length}`);
  const total = Object.values(r).reduce((s, a) => s + a.length, 0);
  console.log(`TOTAL:        ${total}`);

  // claim + connection totals
  const ccTotals = (arr) => arr.reduce(
    (a, e) => ({
      claims: a.claims + (e.claims?.length || 0),
      conns: a.conns + (e.connections?.length || 0),
    }),
    { claims: 0, conns: 0 },
  );
  const all = [
    ...r.com_nodes, ...r.com_briefs, ...r.com_reports,
    ...r.com_reviews, ...r.org_shape_a, ...r.org_shape_b, ...r.org_landing,
  ];
  const tot = ccTotals(all);
  console.log(`\nTotal claims extracted:      ${tot.claims}`);
  console.log(`Total connections extracted: ${tot.conns}`);

  // entries with zero claims (where claims field exists)
  const emptyClaimEntries = all.filter(e => e.claims && e.claims.length === 0)
    .map(e => `${e.surface}/${e.type}/${e.id}`);
  if (emptyClaimEntries.length) {
    console.log(`\nEntries with zero extracted claims (${emptyClaimEntries.length}):`);
    for (const s of emptyClaimEntries.slice(0, 20)) console.log(`  ${s}`);
    if (emptyClaimEntries.length > 20) console.log(`  …and ${emptyClaimEntries.length - 20} more`);
  }

  if (failures.length) {
    console.log('\n=== Extraction failures ===');
    for (const f of failures) console.log(`  ${f.type}/${f.file}: ${f.error}`);
  }

  if (r.org_shape_b.length) {
    console.log('\n=== Shape B entries (no com/ backing — flagged for manual review) ===');
    for (const e of r.org_shape_b) console.log(`  ${e.id}`);
  }

  if (missingFromOrg.length) {
    console.log(`\n=== com/ node slugs NOT in org graph (Phase 6 audit preview: ${missingFromOrg.length}) ===`);
    for (const s of missingFromOrg) console.log(`  ${s}`);
  }
}

function printSample(r) {
  console.log('\n========== SAMPLE ENTRIES (first / middle / last per category) ==========');
  const cats = [
    ['com/nodes',   r.com_nodes],
    ['com/briefs',  r.com_briefs],
    ['com/reports', r.com_reports],
    ['com/reviews', r.com_reviews],
    ['org Shape A', r.org_shape_a],
    ['org Shape B', r.org_shape_b],
    ['org _landing',r.org_landing],
  ];
  for (const [name, arr] of cats) {
    if (arr.length === 0) continue;
    console.log(`\n─── ${name} ───`);
    const idx = arr.length === 1 ? [0]
              : arr.length === 2 ? [0, 1]
              : [0, Math.floor(arr.length / 2), arr.length - 1];
    for (const i of idx) {
      console.log(`[${i}] ${arr[i].id}`);
      console.log(JSON.stringify(arr[i], null, 2));
    }
  }
}

function printProposedFiles(r) {
  console.log('\n========== PROPOSED FILES ==========');
  console.log(`entries/com/nodes/     ${r.com_nodes.length} files`);
  console.log(`entries/com/briefs/    ${r.com_briefs.length} files`);
  console.log(`entries/com/reports/   ${r.com_reports.length} files`);
  console.log(`entries/com/reviews/   ${r.com_reviews.length} files`);
  const orgCount = r.org_shape_a.length + r.org_shape_b.length + r.org_landing.length;
  console.log(`entries/org/           ${orgCount} files`);
  const total = Object.values(r).reduce((s, a) => s + a.length, 0);
  console.log(`TOTAL:                 ${total} files`);
}

function writeAll(r) {
  const base = resolve(playbookVerification, 'entries');
  const pairs = [
    ['com/nodes',   r.com_nodes],
    ['com/briefs',  r.com_briefs],
    ['com/reports', r.com_reports],
    ['com/reviews', r.com_reviews],
  ];
  for (const [sub, arr] of pairs) {
    const dir = resolve(base, sub);
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    for (const e of arr) {
      writeFileSync(resolve(dir, `${e.id}.json`), JSON.stringify(e, null, 2) + '\n');
    }
  }
  const orgDir = resolve(base, 'org');
  if (!existsSync(orgDir)) mkdirSync(orgDir, { recursive: true });
  for (const e of [...r.org_shape_a, ...r.org_shape_b, ...r.org_landing]) {
    writeFileSync(resolve(orgDir, `${e.id}.json`), JSON.stringify(e, null, 2) + '\n');
  }
}

main();
