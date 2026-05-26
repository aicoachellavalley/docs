# sunshine.fm Launch Checklist

Source of truth for new page and experiment launches.
Referenced by sunshine-fm/CLAUDE.md.

Last updated: 2026-05-26

---

## New Page or Experiment Launch — Five Steps

Complete all five steps in order for every new standalone 
page or lab experiment. Do not deploy without confirming 
each step is done.

### 1. lab/index.json
Add one JSON object for the new experiment. Required fields:

  {
    "name": "",
    "tagline": "",
    "status": "",
    "key_fact": "",
    "url": "",
    "type": "",
    "cta": "",
    "launched": "YYYY-MM-DD",
    "ended": null,
    "external": true
  }

The lab page at sunshine.fm/lab/ renders from this file 
automatically. No HTML changes needed.

### 2. sitemap.xml
Add a <url> block for any new subdirectory page:

  <url>
    <loc>https://sunshine.fm/[path]/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

Not required for subdomains — they maintain their own 
sitemaps.

### 3. llms.txt
Add a new ## Section if the experiment has agent-callable 
endpoints or a data file worth indexing:

  ## [Experiment Name]
  - URL: https://sunshine.fm/[path]/
  - Data: https://sunshine.fm/[path]/index.json
  - Description: [one-line description]

Minimum entry is URL and one-line description.

### 4. journal/index.html
Three changes, in this order:
- Bump the total counter by 1
- Increment the journal entries subcounter by 1
- Prepend a new entry at the top of the current month 
  group, matching the exact entry markup pattern already 
  in the file

Entry sub text should include: what shipped, what changed, 
tools used, estimated tokens.

### 5. Commit message
Use this format:
  feat(lab): add [experiment-name] — [one-line description]

---

## Lab Status Vocabulary

Use only these five values in lab/index.json:

| Value | Meaning |
|-------|---------|
| live | Running, actively maintained |
| in-beta | Shipped but limited or experimental access |
| season-complete | Seasonal by design, ended as planned, case study exists |
| ended | Ended, no case study |
| coming-soon | Announced, not yet live |

---

## Lab Type Vocabulary

Use only these four values in lab/index.json:

| Value | Meaning |
|-------|---------|
| experiment | One-off, time-bounded, or novel concept |
| tool | Utility, used repeatedly |
| service | Ongoing, transactional, or infrastructure |
| labs | Internal or AICV-adjacent, technical audience |

---

## Subdomain vs. Subdirectory Decision Rule

Default to subdirectory (/lab/experiment-name/) for SEO 
authority consolidation.

Use a subdomain (experiment.sunshine.fm) only when the 
project has a bounded identity with a designed beginning, 
middle, and end — i.e. seasonal projects like Mirage.

---

## Standing Session Rules

These apply to every Claude Code session in this repo:

- Read before writing. Always.
- Show diff, wait for explicit approval, then write.
- One file at a time.
- Never modify files outside the scope of the current task.
- Verify current state before prescribing changes.
- Do not create new files unless explicitly instructed.
- Never deploy without explicit approval.

---

## Page Architecture Reference

sunshine.fm is a hybrid build:

- Vanilla HTML — all pages except guide and list
- Astro (my111-builder/) — guide/index.html and 
  list/index.html only
- Cloudflare Pages — deployment target
- All pages are fully self-contained HTML — no shared 
  includes, no server-side partials
- All CSS is inline per page
- Google Fonts: Barlow Condensed 900, Syne 400/600/700

When building a new vanilla HTML page, clone 
blog/index.html as the template. It is the canonical 
standalone page pattern.

When updating guide or list pages, edit the Astro source 
in my111-builder/ — never patch the built output directly 
or changes will be overwritten on next build.
