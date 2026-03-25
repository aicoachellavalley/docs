#!/usr/bin/env node
// build-static-json.js
// Generates public/nodes.json and public/briefs.json from MDX frontmatter
// Run from ~/Projects/docs: node scripts/build-static-json.js

const fs = require('fs');
const path = require('path');

const DOCS_ROOT = path.resolve(__dirname, '..');
const NODES_DIR = path.join(DOCS_ROOT, 'nodes');
const BRIEFS_DIR = path.join(DOCS_ROOT, 'intelligence-briefs');
const PUBLIC_DIR = DOCS_ROOT; // Mintlify serves static files from repo root, not public/

// --- Frontmatter parser (no external deps) ---
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const yaml = match[1];
  const result = {};

  for (const line of yaml.split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;

    const key = line.slice(0, colonIdx).trim();
    let value = line.slice(colonIdx + 1).trim();

    if (!key) continue;

    // Array: ["a", "b"] or [a, b]
    if (value.startsWith('[')) {
      try {
        // Convert YAML array to JSON array
        const jsonLike = value
          .replace(/'/g, '"')
          .replace(/(\w[\w-]*)(?=[,\]])/g, '"$1"')  // unquoted words
          .replace(/""(\w)/g, '"$1');                // fix double-quote artifacts
        result[key] = JSON.parse(jsonLike);
      } catch {
        // fallback: strip brackets and split
        result[key] = value.replace(/[\[\]"']/g, '').split(',').map(s => s.trim()).filter(Boolean);
      }
      continue;
    }

    // Boolean
    if (value === 'true') { result[key] = true; continue; }
    if (value === 'false') { result[key] = false; continue; }

    // Quoted string
    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
      result[key] = value.slice(1, -1);
      continue;
    }

    result[key] = value;
  }

  return result;
}

// --- File walker ---
function walkMdx(dir) {
  const files = [];
  if (!fs.existsSync(dir)) return files;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkMdx(fullPath));
    } else if (entry.name.endsWith('.mdx') && !entry.name.startsWith('_')) {
      files.push(fullPath);
    }
  }
  return files;
}

// --- Build nodes.json ---
function buildNodes() {
  const files = walkMdx(NODES_DIR);
  const nodes = [];

  for (const filePath of files) {
    const content = fs.readFileSync(filePath, 'utf8');
    const fm = parseFrontmatter(content);
    if (!fm.title) continue;

    // Derive slug from filename (no extension)
    const slug = path.basename(filePath, '.mdx');
    // Derive city folder from parent directory name
    const cityFolder = path.basename(path.dirname(filePath));

    nodes.push({
      slug,
      city_folder: cityFolder,
      title: fm.title || '',
      description: fm.description || '',
      agent_summary: fm.agent_summary || '',
      city: fm.city || '',
      category: fm.category || '',
      subcategory: fm.subcategory || '',
      status: fm.status || '',
      verified: fm.verified === true || fm.verified === 'true',
      agent_intent: Array.isArray(fm.agent_intent) ? fm.agent_intent : [],
      last_updated: fm.last_updated || '',
    });
  }

  // Sort by city then title
  nodes.sort((a, b) => {
    if (a.city < b.city) return -1;
    if (a.city > b.city) return 1;
    return a.title.localeCompare(b.title);
  });

  return nodes;
}

// --- Body section extractor ---
// Extracts plain text content of a named ## section from MDX body.
// Returns "" if the section is not found.
function extractSection(content, sectionName) {
  // Strip frontmatter first
  const body = content.replace(/^---[\s\S]*?---\n/, '');

  // Match from "## SectionName" to the next "##" heading (or end of file)
  const pattern = new RegExp(
    `##\\s+${sectionName}\\s*\\n([\\s\\S]*?)(?=\\n##\\s|$)`,
    'i'
  );
  const match = body.match(pattern);
  if (!match) return '';

  let text = match[1];

  // Strip markdown formatting
  text = text
    .replace(/\*\*(.+?)\*\*/g, '$1')   // bold
    .replace(/\*(.+?)\*/g, '$1')         // italic
    .replace(/`(.+?)`/g, '$1')           // inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links → label only
    .replace(/^[-*+]\s+/gm, '')          // unordered list markers
    .replace(/^\d+\.\s+/gm, '')          // ordered list markers
    .replace(/^#+\s+/gm, '')             // any remaining headings
    .replace(/\{\/\*.*?\*\/\}/gs, '')    // MDX comments
    .replace(/\n{3,}/g, '\n\n')          // collapse extra blank lines
    .trim();

  return text;
}

// --- Build briefs.json ---
function buildBriefs() {
  const files = walkMdx(BRIEFS_DIR);
  const briefs = [];

  for (const filePath of files) {
    const content = fs.readFileSync(filePath, 'utf8');
    const fm = parseFrontmatter(content);
    if (!fm.title) continue;

    const slug = path.basename(filePath, '.mdx');

    briefs.push({
      slug,
      title: fm.title || '',
      description: fm.description || '',
      date: fm.date || '',
      tags: Array.isArray(fm.tags) ? fm.tags : [],
      signal: extractSection(content, 'Signal'),
      agent_signal: extractSection(content, 'Agent Signal'),
      context: extractSection(content, 'Context'),
    });
  }

  // Sort by date descending (most recent first)
  briefs.sort((a, b) => {
    if (a.date > b.date) return -1;
    if (a.date < b.date) return 1;
    return 0;
  });

  return briefs;
}

// --- Schema validation ---
// Warns on missing required fields — does not block execution.
// Node required fields: agent_summary, agent_intent, status, verified
// Brief required fields (from 2026-02-23 onward): agent_signal
const BRIEF_AGENT_SIGNAL_CUTOFF = '2026-03-01';

function validate(nodes, briefs) {
  let warnings = 0;

  // Node validation
  const NODE_REQUIRED = ['agent_summary', 'agent_intent', 'status', 'verified'];
  for (const node of nodes) {
    for (const field of NODE_REQUIRED) {
      const val = node[field];
      const empty =
        val === '' ||
        val === false ||
        (Array.isArray(val) && val.length === 0) ||
        val === null ||
        val === undefined;
      if (empty) {
        console.warn(`WARN: ${node.slug} missing ${field}`);
        warnings++;
      }
    }
  }

  // Brief validation — agent_signal required from cutoff date onward
  for (const brief of briefs) {
    if (brief.date >= BRIEF_AGENT_SIGNAL_CUTOFF && brief.slug !== 'also-noted') {
      if (!brief.agent_signal || brief.agent_signal === '') {
        console.warn(`WARN: ${brief.slug} missing agent_signal`);
        warnings++;
      }
    }
  }

  // Also-noted briefs are exempt from agent_signal check (different structure)
  const eligibleBriefs = briefs.filter(
    b => b.date >= BRIEF_AGENT_SIGNAL_CUTOFF && !b.slug.includes('also-noted')
  );

  if (warnings === 0) {
    console.log(`Validation complete — ${nodes.length} nodes clean, ${eligibleBriefs.length} briefs clean`);
  } else {
    console.log(`Validation complete — ${warnings} warning${warnings === 1 ? '' : 's'} found`);
  }
}

// --- IndexNow submission ---
async function submitToIndexNow(urls) {
  const payload = {
    host: "agent.aicoachellavalley.com",
    key: "aicv-indexnow-2026",
    keyLocation: "https://agent.aicoachellavalley.com/aicv-indexnow-2026.txt",
    urlList: urls
  };

  const response = await fetch("https://api.indexnow.org/indexnow", {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(payload)
  });

  console.log(`IndexNow: ${response.status} — ${urls.length} URLs submitted`);
}

// --- Main ---
async function main() {
  const nodes = buildNodes();
  const briefs = buildBriefs();

  const nodesJson = JSON.stringify(nodes, null, 2);
  const briefsJson = JSON.stringify(briefs, null, 2);

  const nodesSize = Buffer.byteLength(nodesJson, 'utf8');
  const briefsSize = Buffer.byteLength(briefsJson, 'utf8');

  if (nodesSize > 2 * 1024 * 1024) {
    console.error(`ERROR: nodes.json is ${(nodesSize / 1024 / 1024).toFixed(2)}MB — exceeds 2MB limit`);
    process.exit(1);
  }
  if (briefsSize > 2 * 1024 * 1024) {
    console.error(`ERROR: briefs.json is ${(briefsSize / 1024 / 1024).toFixed(2)}MB — exceeds 2MB limit`);
    process.exit(1);
  }

  fs.writeFileSync(path.join(PUBLIC_DIR, 'nodes.json'), nodesJson, 'utf8');
  fs.writeFileSync(path.join(PUBLIC_DIR, 'briefs.json'), briefsJson, 'utf8');

  console.log(`nodes.json  — ${nodes.length} nodes   (${(nodesSize / 1024).toFixed(1)} KB)`);
  console.log(`briefs.json — ${briefs.length} briefs (${(briefsSize / 1024).toFixed(1)} KB)`);
  console.log('Output: nodes.json, briefs.json');

  validate(nodes, briefs);

  await submitToIndexNow([
    "https://agent.aicoachellavalley.com/nodes.json",
    "https://agent.aicoachellavalley.com/briefs.json",
    "https://agent.aicoachellavalley.com/llms.txt",
    "https://agent.aicoachellavalley.com/.well-known/mcp.json"
  ]);
}

main();
