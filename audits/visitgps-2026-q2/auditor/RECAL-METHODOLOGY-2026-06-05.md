# Recalibration methodology — 2026-06-05

Re-scored two dimensions of the Phase 1 rubric per Sat's directive after the
verification spot-checks confirmed measurement artifacts in the original
chunk agents' implementation.

## Inputs
- Source: `scout/partner-directory-clean.json` (3,333 weburl-eligible records)
- Pre-recal chunks: `auditor/_pre-recal-2026-06-05/chunks/` (preserved)
- Pre-recal cuts: `auditor/_pre-recal-2026-06-05/cuts/` (preserved)

## schema_present — corrected rule

Fetch partner homepage with `User-Agent: AICV-Audit/2026Q2 (+https://aicoachellavalley.org)`, timeout 12s, lenient SSL.
Parse for any `<script type="application/ld+json">` block. Walk every block
(including `@graph` traversal). Collect all `@type` values across all blocks.

Pass if any collected `@type` is in this accepted set (documented per Sat's
directive that the methodology be recoverable):

```
['EntertainmentBusiness', 'Event', 'FoodEstablishment', 'Hotel', 'LocalBusiness', 'LodgingBusiness', 'Organization', 'Place', 'Product', 'RealEstateAgent', 'Restaurant', 'Service', 'TouristAttraction', 'WebSite']
```

This list reflects what actually appears on real SMB / hospitality sites.
The earlier rubric's narrower filter rejected sites emitting `WebSite`,
`Organization`, `Place`, etc. — schema that IS agent-readable, just not
strictly LocalBusiness-flavored.

## nap_consistent — corrected rule

Three sub-checks, ALL must pass:

**Phone:** Last 10 digits of VGPS phone (after stripping non-digits) appear
anywhere in the HTML's digit-only projection. Tolerant of any visual format
on the partner site — `(760) 326-1234`, `760.326.1234`, `+1-760-326-1234`,
etc. all match.

**Name:** Pass if ANY of:
- (a) Full VGPS name substring appears in lowercased HTML
- (b) First 2-3 significant words (length > 2) of VGPS name all present in HTML
- (c) Domain root (≥4 chars, e.g. "modernway" from modernway.com) appears
  as substring in alphanumeric-only VGPS name

Rule (c) is the most forgiving and reflects how operators actually brand:
businesses often appear in VGPS under their full legal name but use a
shorter brand on their website. A `modernway.com` domain matching the VGPS
listing "Modernway Vintage Furniture & Mid-Century Modern" should pass.

**City:** VGPS city (e.g. "Palm Desert") appears as substring in lowercased HTML.

## Other dimensions

Unchanged. The 6 remaining scored dimensions (site_loads, mobile_ready,
og_metadata, faq_present, content_fresh, citation_density) and the 2
unscored diagnostics (llms_txt_present, gbp_linked) carry over from the
original chunk scoring.

## Score and tier

Score = sum of 8 scored dimensions (each True = +1). Tier:
- 7-8 → A
- 4-6 → B
- 1-3 → C
- 0   → D

## Provenance fields added to each record's checks

- `_recal_status`: `"ok"` or `"fetch_failed"` or `"exception: ..."`
- `_recal_error`: error string if fetch failed
- `_recal_schema_types_found`: list of all @types collected from partner site
- `_recal_schema_matched`: subset that matched the accepted list
- `_recal_nap_evidence`: per-component name/phone/city pass results plus the
  matching rule that fired for name

These provenance fields make the methodology auditable per partner.

## Results (this run)

- Total records re-checked: 3333
- Fetch failures during recal: 969
- schema_present pass rate: 0 (0.0%) → 1314 (39.4%)
- nap_consistent pass rate: 168 (5.0%) → 1145 (34.4%)
- Tier shifts:
  - A: 225 → 58 (-167)
  - B: 1647 → 1388 (-259)
  - C: 669 → 1128 (+459)
  - D: 792 → 759 (-33)
