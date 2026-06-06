#!/usr/bin/env python3
"""
Re-aggregate Phase 1 scoring outputs from disk. Deterministic — no LLM.

Reads:
  - auditor/chunks/chunk-*.jsonl    (scored records from Wide Scan)
  - scout/inventory-no-weburl.jsonl (auto Tier Z)

Writes:
  - auditor/partners-wide-scan.json       (canonical merged record set)
  - auditor/partners-by-tier.csv          (human-review sort)
  - auditor/rubric-results-per-dimension.json
  - auditor/tier-by-rawlabel.json         (Cut 1: raw labels, no collapsing)
  - auditor/tier-by-canonical.json        (Cut 2: CANONICAL_MAP applied)
  - auditor/tier-by-strategic.json        (Cut 3: STRATEGIC_MAP applied — 7 buckets)
  - auditor/tier-by-subcategory.json      (Cut 4: VGPS sub-categories)
  - auditor/chain-vs-indie.json           (Cut 5)

Constants mirror audit-scoring-workflow.js / TAXONOMY-CANONICAL.md.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2")
CHUNKS_DIR = ROOT / "auditor" / "chunks"
NO_WEBURL = ROOT / "scout" / "inventory-no-weburl.jsonl"
CLEAN = ROOT / "scout" / "partner-directory-clean.json"

OUT_WIDE_SCAN = ROOT / "auditor" / "partners-wide-scan.json"
OUT_CSV = ROOT / "auditor" / "partners-by-tier.csv"
OUT_RUBRIC = ROOT / "auditor" / "rubric-results-per-dimension.json"
OUT_RAW = ROOT / "auditor" / "tier-by-rawlabel.json"
OUT_CANONICAL = ROOT / "auditor" / "tier-by-canonical.json"
OUT_STRATEGIC = ROOT / "auditor" / "tier-by-strategic.json"
OUT_SUBCAT = ROOT / "auditor" / "tier-by-subcategory.json"
OUT_CHAIN = ROOT / "auditor" / "chain-vs-indie.json"

CANONICAL_MAP = {
    "STAY": "Lodging",
    "PLACES TO STAY": "Lodging",
    "EAT & DRINK": "Dining",
    "THINGS TO DO": "Activities",
    "ACTIVITIES & RECREATION": "Activities",
    "TOURS": "Tours",
    "ARTS & CULTURE": "Arts & Culture",
    "CASINOS & ENTERTAINMENT": "Entertainment",
    "GOLF": "Golf",
    "HIKING TRAILS": "Outdoor Recreation",
    "SPAS, BEAUTY & WELLNESS": "Spas & Wellness",
    "GROUP VENUES": "Group Venues",
    "MEETING & EVENT RESOURCES": "Meeting Resources",
    "WEDDINGS": "Weddings",
    "GETTING HERE": "Transportation",
    "GETTING HERE & AROUND": "Transportation",
    "VISITOR INFORMATION": "Visitor Services",
    "SHOPPING": "Shopping",
    "BUSINESS & PROFESSIONAL SERVICES": "Professional Services",
    "RELOCATION & RESOURCES": "Relocation",
    "FILM PRODUCTION SERVICES": "Film Production",
    "CANNABIS": "Cannabis",
    "DOG-FRIENDLY RESOURCES": "Pet Services",
}

STRATEGIC_MAP = {
    "Lodging": "Lodging",
    "Dining": "Dining",
    "Activities": "Experiences",
    "Tours": "Experiences",
    "Arts & Culture": "Experiences",
    "Entertainment": "Experiences",
    "Golf": "Experiences",
    "Outdoor Recreation": "Experiences",
    "Spas & Wellness": "Wellness",
    "Group Venues": "Meetings & Events",
    "Meeting Resources": "Meetings & Events",
    "Weddings": "Meetings & Events",
    "Transportation": "Mobility",
    "Visitor Services": "Mobility",
    "Shopping": "Retail & Services",
    "Professional Services": "Retail & Services",
    "Relocation": "Retail & Services",
    "Film Production": "Retail & Services",
    "Cannabis": "Retail & Services",
    "Pet Services": "Retail & Services",
}


def canonical_of(raw):
    if not raw:
        return "(uncategorized)"
    return CANONICAL_MAP.get(raw, f"(unmapped: {raw})")


def strategic_of(raw):
    if not raw:
        return "(uncategorized)"
    canon = CANONICAL_MAP.get(raw)
    if canon is None:
        return "(unmapped)"
    return STRATEGIC_MAP.get(canon, "(unmapped)")


def load_chunks():
    records = []
    chunk_files = sorted(CHUNKS_DIR.glob("chunk-*.jsonl"))
    for cf in chunk_files:
        for line in cf.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_tier_z():
    """Tier Z = inventory-no-weburl records. Synthesize the same schema as scored."""
    records = []
    for line in NO_WEBURL.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        inv = json.loads(line)
        records.append({
            "vgps_id": inv.get("vgps_id"),
            "name": inv.get("name"),
            "primary_category": inv.get("primary_category"),
            "subcategories": inv.get("subcategories") or [],
            "weburl": None,
            "chain_brand": False,
            "chain_brand_evidence": None,
            "score": 0,
            "tier": "Z",
            "checks": {
                "site_loads": False,
                "nap_consistent": False,
                "mobile_ready": False,
                "schema_present": False,
                "og_metadata": False,
                "faq_present": False,
                "content_fresh": False,
                "citation_density": False,
                "llms_txt_present": False,
                "gbp_linked": False,
                "notes": "auto Tier Z — no weburl",
            },
        })
    return records


def load_listing_urls():
    """For CSV: pull the original listing_url back from clean inventory."""
    clean = json.loads(CLEAN.read_text())
    return {r["vgps_id"]: r.get("listing_url") for r in clean}


def empty_bucket():
    return {
        "total": 0,
        "unique_businesses": 0,
        "tier_A": 0, "tier_B": 0, "tier_C": 0, "tier_D": 0, "tier_Z": 0,
        "chain_count": 0,
        "indie_count": 0,
        "_scores_excl_Z": [],
        "_weburls": set(),
    }


def finalize_bucket(b):
    scores = b.pop("_scores_excl_Z")
    weburls = b.pop("_weburls")
    b["mean_score_excluding_Z"] = round(sum(scores) / len(scores), 3) if scores else 0.0
    b["unique_businesses"] = len(weburls)
    return b


def aggregate():
    scored = load_chunks()
    tier_z = load_tier_z()
    all_records = scored + tier_z
    listing_urls = load_listing_urls()

    # 1. partners-wide-scan.json
    OUT_WIDE_SCAN.write_text(json.dumps(all_records, indent=2))

    # 2. CSV
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "vgps_id", "name", "raw_label", "canonical_category",
            "strategic_bucket", "chain_brand", "score", "tier",
            "weburl", "listing_url",
        ])
        tier_order = {"A": 0, "B": 1, "C": 2, "D": 3, "Z": 4}
        sorted_recs = sorted(
            all_records,
            key=lambda r: (tier_order.get(r.get("tier", "Z"), 5), -(r.get("score") or 0)),
        )
        for r in sorted_recs:
            raw = r.get("primary_category") or ""
            w.writerow([
                r.get("vgps_id"),
                r.get("name"),
                raw,
                canonical_of(raw),
                strategic_of(raw),
                "true" if r.get("chain_brand") else "false",
                r.get("score", 0),
                r.get("tier"),
                r.get("weburl") or "",
                listing_urls.get(r.get("vgps_id"), ""),
            ])

    # 3. Rubric pass rates (over A/B/C/D only)
    DIMS = [
        "site_loads", "nap_consistent", "mobile_ready", "schema_present",
        "og_metadata", "faq_present", "content_fresh", "citation_density",
        "llms_txt_present", "gbp_linked",
    ]
    pass_counts = {d: 0 for d in DIMS}
    n_scored = 0
    for r in all_records:
        if r.get("tier") == "Z":
            continue
        n_scored += 1
        checks = r.get("checks") or {}
        for d in DIMS:
            if checks.get(d):
                pass_counts[d] += 1
    rubric = {d: {"pass_count": pass_counts[d], "n": n_scored, "pass_rate": round(pass_counts[d] / n_scored, 4) if n_scored else 0.0} for d in DIMS}
    OUT_RUBRIC.write_text(json.dumps(rubric, indent=2))

    # 4-6. Tier-by-X buckets
    raw_buckets = defaultdict(empty_bucket)
    canonical_buckets = defaultdict(empty_bucket)
    strategic_buckets = defaultdict(empty_bucket)
    canonical_raw_labels = defaultdict(set)  # canonical → which raw labels rolled in
    strategic_canonicals = defaultdict(set)  # strategic → which canonicals rolled in

    for r in all_records:
        raw = r.get("primary_category") or ""
        canonical = canonical_of(raw)
        strategic = strategic_of(raw)
        tier = r.get("tier", "Z")
        score = r.get("score", 0)
        weburl = r.get("weburl")
        chain = r.get("chain_brand", False)

        for bucket, key in [(raw_buckets, raw or "(uncategorized)"), (canonical_buckets, canonical), (strategic_buckets, strategic)]:
            b = bucket[key]
            b["total"] += 1
            b[f"tier_{tier}"] = b.get(f"tier_{tier}", 0) + 1
            if tier != "Z":
                b["_scores_excl_Z"].append(score)
            if chain:
                b["chain_count"] += 1
            else:
                b["indie_count"] += 1
            b["_weburls"].add(weburl if weburl else f"_no_weburl_{r.get('vgps_id')}")

        if raw:
            canonical_raw_labels[canonical].add(raw)
            strategic_canonicals[strategic].add(canonical)

    raw_out = {k: finalize_bucket(v) for k, v in raw_buckets.items()}
    canonical_out = {}
    for k, v in canonical_buckets.items():
        fin = finalize_bucket(v)
        fin["raw_labels_included"] = sorted(canonical_raw_labels[k])
        canonical_out[k] = fin
    strategic_out = {}
    for k, v in strategic_buckets.items():
        fin = finalize_bucket(v)
        fin["canonical_categories_included"] = sorted(strategic_canonicals[k])
        strategic_out[k] = fin

    OUT_RAW.write_text(json.dumps(raw_out, indent=2))
    OUT_CANONICAL.write_text(json.dumps(canonical_out, indent=2))
    OUT_STRATEGIC.write_text(json.dumps(strategic_out, indent=2))

    # 7. Tier-by-subcategory
    subcat_buckets = defaultdict(lambda: {
        "primary_canonical": None,
        "total": 0,
        "tier_A": 0, "tier_B": 0, "tier_C": 0, "tier_D": 0, "tier_Z": 0,
        "_scores_excl_Z": [],
    })
    for r in all_records:
        raw = r.get("primary_category") or ""
        canonical = canonical_of(raw)
        tier = r.get("tier", "Z")
        score = r.get("score", 0)
        for sc in r.get("subcategories") or []:
            b = subcat_buckets[sc]
            b["primary_canonical"] = canonical
            b["total"] += 1
            b[f"tier_{tier}"] = b.get(f"tier_{tier}", 0) + 1
            if tier != "Z":
                b["_scores_excl_Z"].append(score)
    subcat_out = {"_note": "Sub-categories from VGPS catname array. A partner with multiple subcategories counts in each, so totals here will exceed the global record count."}
    for k, v in subcat_buckets.items():
        scores = v.pop("_scores_excl_Z")
        v["mean_score_excluding_Z"] = round(sum(scores) / len(scores), 3) if scores else 0.0
        subcat_out[k] = v
    OUT_SUBCAT.write_text(json.dumps(subcat_out, indent=2))

    # 8. Chain vs indie
    chain_vs_indie = {}
    for label, predicate in [("chain", lambda r: r.get("chain_brand")), ("indie", lambda r: not r.get("chain_brand"))]:
        subset = [r for r in all_records if predicate(r)]
        scores_excl_z = [r["score"] for r in subset if r.get("tier") != "Z"]
        weburls = set(r.get("weburl") or f"_no_weburl_{r.get('vgps_id')}" for r in subset)
        tiers = Counter(r.get("tier", "Z") for r in subset)
        by_strat = defaultdict(empty_bucket)
        for r in subset:
            strat = strategic_of(r.get("primary_category") or "")
            b = by_strat[strat]
            b["total"] += 1
            b[f"tier_{r.get('tier','Z')}"] = b.get(f"tier_{r.get('tier','Z')}", 0) + 1
            if r.get("tier") != "Z":
                b["_scores_excl_Z"].append(r.get("score", 0))
            b["_weburls"].add(r.get("weburl") or f"_no_weburl_{r.get('vgps_id')}")
            if r.get("chain_brand"):
                b["chain_count"] += 1
            else:
                b["indie_count"] += 1
        chain_vs_indie[label] = {
            "total": len(subset),
            "unique_businesses": len(weburls),
            "mean_score_excluding_Z": round(sum(scores_excl_z) / len(scores_excl_z), 3) if scores_excl_z else 0.0,
            "tier_A": tiers.get("A", 0), "tier_B": tiers.get("B", 0),
            "tier_C": tiers.get("C", 0), "tier_D": tiers.get("D", 0), "tier_Z": tiers.get("Z", 0),
            "by_strategic_bucket": {k: finalize_bucket(v) for k, v in by_strat.items()},
        }
    OUT_CHAIN.write_text(json.dumps(chain_vs_indie, indent=2))

    # Headline summary
    tier_counts = Counter(r.get("tier", "Z") for r in all_records)
    all_weburls = set()
    for r in all_records:
        all_weburls.add(r.get("weburl") or f"_no_weburl_{r.get('vgps_id')}")

    unmapped = sorted({r.get("primary_category") for r in all_records if r.get("primary_category") and r["primary_category"] not in CANONICAL_MAP})

    summary = {
        "total_listings": len(all_records),
        "unique_businesses": len(all_weburls),
        "tier_counts": dict(tier_counts),
        "strategic_summary": {k: {
            "total": v["total"],
            "unique_businesses": v["unique_businesses"],
            "mean_score_excluding_Z": v["mean_score_excluding_Z"],
            "tier_A": v["tier_A"], "tier_B": v["tier_B"],
            "tier_C": v["tier_C"], "tier_D": v["tier_D"], "tier_Z": v["tier_Z"],
        } for k, v in strategic_out.items()},
        "chain_vs_indie_headline": {
            "chain": {"total": chain_vs_indie["chain"]["total"], "mean_score_excluding_Z": chain_vs_indie["chain"]["mean_score_excluding_Z"]},
            "indie": {"total": chain_vs_indie["indie"]["total"], "mean_score_excluding_Z": chain_vs_indie["indie"]["mean_score_excluding_Z"]},
        },
        "unmapped_raw_labels": unmapped,
        "rubric_pass_rates": {d: rubric[d]["pass_rate"] for d in DIMS},
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    aggregate()
