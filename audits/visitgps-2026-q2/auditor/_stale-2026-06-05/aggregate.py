#!/usr/bin/env python3
"""Aggregate scored chunks + Tier Z records into report artifacts."""
import json
import csv
import glob
import os
from collections import defaultdict

ROOT = "/Users/macmini/Projects/aicv-playbook/audits/visitgps-2026-q2"
CHUNKS_DIR = f"{ROOT}/auditor/chunks"
SCOUT_DIR = f"{ROOT}/scout"
AUDIT_DIR = f"{ROOT}/auditor"

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

TIERS = ["A", "B", "C", "D", "Z"]
DIMENSIONS = [
    "site_loads",
    "nap_consistent",
    "mobile_ready",
    "schema_markup",
    "og_metadata",
    "faq_qa",
    "content_fresh",
    "citation_density",
    "llms_txt_present",
    "gbp_linked",
]


def canonical(raw):
    if raw is None or raw == "":
        return "(uncategorized)"
    if raw in CANONICAL_MAP:
        return CANONICAL_MAP[raw]
    return f"(unmapped: {raw})"


def strategic(canon):
    if canon == "(uncategorized)":
        return "(uncategorized)"
    if canon.startswith("(unmapped"):
        return "(unmapped)"
    return STRATEGIC_MAP.get(canon, "(unmapped)")


def main():
    # ---- Load listing_url map from partner-directory-clean.json
    with open(f"{SCOUT_DIR}/partner-directory-clean.json") as f:
        pdir = json.load(f)
    listing_url_by_id = {r["vgps_id"]: r.get("listing_url") for r in pdir}

    # ---- Load scored chunks
    records = []
    chunk_errors = []
    for cf in sorted(glob.glob(f"{CHUNKS_DIR}/chunk-*.jsonl")):
        with open(cf) as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    records.append(r)
                except json.JSONDecodeError as e:
                    chunk_errors.append(f"{os.path.basename(cf)}:{i} {e}")

    # ---- Load Tier Z (no weburl)
    z_records = []
    with open(f"{SCOUT_DIR}/inventory-no-weburl.jsonl") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            src = json.loads(line)
            # Backfill listing_url from inventory if not in partner-directory
            if src["vgps_id"] not in listing_url_by_id or not listing_url_by_id[src["vgps_id"]]:
                listing_url_by_id[src["vgps_id"]] = src.get("listing_url")
            checks = {d: False for d in DIMENSIONS}
            checks["notes"] = "auto Tier Z — no weburl"
            z_records.append({
                "vgps_id": src["vgps_id"],
                "name": src["name"],
                "primary_category": src.get("primary_category"),
                "subcategories": src.get("subcategories", []),
                "weburl": None,
                "chain_brand": False,
                "chain_brand_evidence": None,
                "score": 0,
                "tier": "Z",
                "checks": checks,
            })

    all_records = records + z_records

    # ---- Write merged JSON
    merged_path = f"{AUDIT_DIR}/partners-wide-scan.json"
    with open(merged_path, "w") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    # ---- CSV by tier
    tier_order = {t: i for i, t in enumerate(TIERS)}
    csv_rows = []
    for r in all_records:
        raw = r.get("primary_category") or ""
        canon = canonical(r.get("primary_category"))
        strat = strategic(canon)
        csv_rows.append({
            "vgps_id": r["vgps_id"],
            "name": r["name"],
            "raw_label": raw,
            "canonical_category": canon,
            "strategic_bucket": strat,
            "chain_brand": r.get("chain_brand", False),
            "score": r.get("score", 0),
            "tier": r.get("tier", "Z"),
            "weburl": r.get("weburl") or "",
            "listing_url": listing_url_by_id.get(r["vgps_id"], "") or "",
        })

    csv_rows.sort(key=lambda x: (tier_order.get(x["tier"], 99), -int(x["score"] or 0)))

    csv_path = f"{AUDIT_DIR}/partners-by-tier.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "vgps_id", "name", "raw_label", "canonical_category",
            "strategic_bucket", "chain_brand", "score", "tier",
            "weburl", "listing_url",
        ])
        w.writeheader()
        for row in csv_rows:
            w.writerow(row)

    # ---- Rubric pass rates (A/B/C/D only)
    scored = [r for r in all_records if r.get("tier") != "Z"]
    n_scored = len(scored)
    rubric = {}
    for d in DIMENSIONS:
        passes = sum(1 for r in scored if r.get("checks", {}).get(d) is True)
        rubric[d] = {
            "pass_count": passes,
            "pass_rate": round((passes / n_scored), 4) if n_scored else 0.0,
            "n": n_scored,
        }
    with open(f"{AUDIT_DIR}/rubric-results-per-dimension.json", "w") as f:
        json.dump(rubric, f, indent=2)

    # ---- helper: aggregate by key
    def empty_bucket():
        return {
            "total": 0,
            "unique_businesses": set(),
            "score_sum": 0,
            "score_count": 0,  # excluding Z
            "tier_A": 0, "tier_B": 0, "tier_C": 0, "tier_D": 0, "tier_Z": 0,
            "chain_count": 0,
            "indie_count": 0,
        }

    def finalize_bucket(b):
        unique = b["unique_businesses"]
        mean = (b["score_sum"] / b["score_count"]) if b["score_count"] else 0.0
        return {
            "total": b["total"],
            "unique_businesses": len(unique),
            "mean_score_excluding_Z": round(mean, 3),
            "tier_A": b["tier_A"],
            "tier_B": b["tier_B"],
            "tier_C": b["tier_C"],
            "tier_D": b["tier_D"],
            "tier_Z": b["tier_Z"],
            "chain_count": b["chain_count"],
            "indie_count": b["indie_count"],
        }

    def add_record_to_bucket(b, r):
        b["total"] += 1
        wu = r.get("weburl")
        if wu:
            b["unique_businesses"].add(wu)
        else:
            b["unique_businesses"].add(f"__nullweb__{r['vgps_id']}")
        tier = r.get("tier", "Z")
        b[f"tier_{tier}"] += 1
        if tier != "Z":
            b["score_sum"] += r.get("score", 0)
            b["score_count"] += 1
        if r.get("chain_brand"):
            b["chain_count"] += 1
        else:
            b["indie_count"] += 1

    # ---- Cut 1: tier × raw label
    raw_buckets = defaultdict(empty_bucket)
    for r in all_records:
        raw = r.get("primary_category") or "(null)"
        add_record_to_bucket(raw_buckets[raw], r)
    raw_out = {k: finalize_bucket(v) for k, v in raw_buckets.items()}
    raw_out = dict(sorted(raw_out.items(), key=lambda kv: -kv[1]["total"]))
    with open(f"{AUDIT_DIR}/tier-by-rawlabel.json", "w") as f:
        json.dump(raw_out, f, indent=2)

    # ---- Cut 2: tier × canonical category
    canon_buckets = defaultdict(empty_bucket)
    canon_raw_labels = defaultdict(set)
    for r in all_records:
        raw = r.get("primary_category") or ""
        canon = canonical(r.get("primary_category"))
        add_record_to_bucket(canon_buckets[canon], r)
        canon_raw_labels[canon].add(raw if raw else "(null)")
    canon_out = {}
    for k, v in canon_buckets.items():
        fin = finalize_bucket(v)
        fin["raw_labels_included"] = sorted(canon_raw_labels[k])
        canon_out[k] = fin
    canon_out = dict(sorted(canon_out.items(), key=lambda kv: -kv[1]["total"]))
    with open(f"{AUDIT_DIR}/tier-by-canonical.json", "w") as f:
        json.dump(canon_out, f, indent=2)

    # ---- Cut 3: tier × strategic bucket
    strat_buckets = defaultdict(empty_bucket)
    for r in all_records:
        canon = canonical(r.get("primary_category"))
        strat = strategic(canon)
        add_record_to_bucket(strat_buckets[strat], r)
    strat_out = {k: finalize_bucket(v) for k, v in strat_buckets.items()}
    expected = [
        "Lodging", "Dining", "Experiences", "Wellness",
        "Meetings & Events", "Mobility", "Retail & Services",
        "(unmapped)", "(uncategorized)",
    ]
    strat_ordered = {}
    for k in expected:
        if k in strat_out:
            strat_ordered[k] = strat_out[k]
    for k, v in strat_out.items():
        if k not in strat_ordered:
            strat_ordered[k] = v
    with open(f"{AUDIT_DIR}/tier-by-strategic.json", "w") as f:
        json.dump(strat_ordered, f, indent=2)

    # ---- Cut 4: tier × VGPS subcategory
    sub_buckets = defaultdict(empty_bucket)
    sub_primary_canon = defaultdict(lambda: defaultdict(int))
    for r in all_records:
        subs = r.get("subcategories") or []
        canon = canonical(r.get("primary_category"))
        if not subs:
            continue
        for sc in subs:
            add_record_to_bucket(sub_buckets[sc], r)
            sub_primary_canon[sc][canon] += 1
    sub_out = {
        "_note": "A partner with multiple subcategories counts in each. primary_canonical = most common canonical category for that subcategory.",
    }
    sub_finalized = {}
    for k, v in sub_buckets.items():
        fin = finalize_bucket(v)
        canons = sub_primary_canon[k]
        primary = max(canons.items(), key=lambda kv: kv[1])[0] if canons else None
        fin = {"primary_canonical": primary, **fin}
        sub_finalized[k] = fin
    sub_finalized = dict(sorted(sub_finalized.items(), key=lambda kv: -kv[1]["total"]))
    sub_out.update(sub_finalized)
    with open(f"{AUDIT_DIR}/tier-by-subcategory.json", "w") as f:
        json.dump(sub_out, f, indent=2)

    # ---- Cut 5: chain vs indie
    def empty_ci():
        b = empty_bucket()
        b["by_strategic_bucket"] = defaultdict(empty_bucket)
        return b

    chain_b = empty_ci()
    indie_b = empty_ci()
    for r in all_records:
        canon = canonical(r.get("primary_category"))
        strat = strategic(canon)
        target = chain_b if r.get("chain_brand") else indie_b
        add_record_to_bucket(target, r)
        add_record_to_bucket(target["by_strategic_bucket"][strat], r)

    def finalize_ci(b):
        fin = finalize_bucket(b)
        bys = {k: finalize_bucket(v) for k, v in b["by_strategic_bucket"].items()}
        bys_ordered = {}
        for k in expected:
            if k in bys:
                bys_ordered[k] = bys[k]
        for k, v in bys.items():
            if k not in bys_ordered:
                bys_ordered[k] = v
        fin["by_strategic_bucket"] = bys_ordered
        return fin

    ci_out = {
        "chain": finalize_ci(chain_b),
        "indie": finalize_ci(indie_b),
    }
    with open(f"{AUDIT_DIR}/chain-vs-indie.json", "w") as f:
        json.dump(ci_out, f, indent=2)

    # ---- Headline counts
    tier_counts = {t: sum(1 for r in all_records if r.get("tier") == t) for t in TIERS}
    unique_set = set()
    for r in all_records:
        wu = r.get("weburl")
        if wu:
            unique_set.add(wu)
        else:
            unique_set.add(f"__nullweb__{r['vgps_id']}")
    unique_businesses = len(unique_set)
    total_listings = len(all_records)

    # ---- strategic_summary
    strategic_summary = {}
    for k, v in strat_ordered.items():
        strategic_summary[k] = {
            "total": v["total"],
            "unique_businesses": v["unique_businesses"],
            "mean_score_excluding_Z": v["mean_score_excluding_Z"],
            "tier_A": v["tier_A"],
            "tier_B": v["tier_B"],
            "tier_C": v["tier_C"],
            "tier_D": v["tier_D"],
            "tier_Z": v["tier_Z"],
        }

    # ---- Anomalies
    unmapped_raw_labels = sorted({
        r.get("primary_category") for r in all_records
        if r.get("primary_category") and r.get("primary_category") not in CANONICAL_MAP
    })
    anomalies = []
    uncat = sum(1 for r in all_records if not r.get("primary_category"))
    if uncat:
        anomalies.append(f"{uncat} record(s) with null/empty primary_category → (uncategorized)")
    for raw in unmapped_raw_labels:
        n = sum(1 for r in all_records if r.get("primary_category") == raw)
        anomalies.append(f"unmapped raw label '{raw}': {n} record(s)")
    if chunk_errors:
        anomalies.append(f"chunk parse errors: {len(chunk_errors)} (first: {chunk_errors[0]})")
    if tier_counts["Z"]:
        anomalies.append(f"Tier Z (auto-assigned, no weburl): {tier_counts['Z']} record(s)")
    a_pct = tier_counts["A"] / total_listings * 100 if total_listings else 0
    d_pct = tier_counts["D"] / total_listings * 100 if total_listings else 0
    anomalies.append(f"Tier A share: {a_pct:.1f}% ; Tier D share: {d_pct:.1f}%")
    seen = defaultdict(int)
    for r in all_records:
        seen[r["vgps_id"]] += 1
    dups = [k for k, v in seen.items() if v > 1]
    if dups:
        anomalies.append(f"duplicate vgps_id values: {len(dups)} (e.g. {dups[:3]})")
    no_web_scored = sum(1 for r in scored if not r.get("weburl"))
    if no_web_scored:
        anomalies.append(f"{no_web_scored} scored record(s) with no weburl (expected 0)")
    no_listing = sum(1 for row in csv_rows if not row["listing_url"])
    if no_listing:
        anomalies.append(f"{no_listing} record(s) missing listing_url in CSV")
    anomalies = anomalies[:10]

    out = {
        "total_listings": total_listings,
        "unique_businesses": unique_businesses,
        "tier_counts": tier_counts,
        "tier_by_rawlabel_path": f"{AUDIT_DIR}/tier-by-rawlabel.json",
        "tier_by_canonical_path": f"{AUDIT_DIR}/tier-by-canonical.json",
        "tier_by_strategic_path": f"{AUDIT_DIR}/tier-by-strategic.json",
        "tier_by_subcategory_path": f"{AUDIT_DIR}/tier-by-subcategory.json",
        "chain_vs_indie_path": f"{AUDIT_DIR}/chain-vs-indie.json",
        "rubric_stats_path": f"{AUDIT_DIR}/rubric-results-per-dimension.json",
        "csv_path": csv_path,
        "strategic_summary": strategic_summary,
        "chain_vs_indie": {
            "chain": {"total": ci_out["chain"]["total"], "mean_score": ci_out["chain"]["mean_score_excluding_Z"]},
            "indie": {"total": ci_out["indie"]["total"], "mean_score": ci_out["indie"]["mean_score_excluding_Z"]},
        },
        "unmapped_raw_labels": unmapped_raw_labels,
        "anomalies_summary": anomalies,
        "merged_path": merged_path,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
