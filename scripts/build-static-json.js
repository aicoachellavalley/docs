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
      signal: fm.signal || '',
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

// --- Main ---
function main() {
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
  console.log('Output: public/nodes.json, public/briefs.json');
}

main();
