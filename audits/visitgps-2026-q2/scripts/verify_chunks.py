#!/usr/bin/env python3
"""
verify_chunks.py — reusable verification for any workflow with parallel chunk
writes to disk. Confirms that each chunk file on disk matches its expected
slice of the source dataset.

Codifies the architectural lesson from 2026-06-05:
  Agent structured-output returns can lie about disk side-effects. The
  workflow must verify on disk before treating a fan-out stage as complete.

Usage:
  python3 verify_chunks.py \\
    --source SOURCE.json \\
    --chunks-dir CHUNKS_DIR \\
    --n-chunks N \\
    [--manifest MANIFEST.json] \\
    [--filename-pattern chunk-{i}.jsonl]

Exit codes:
  0 — all expected chunks present, line counts match, first/last vgps_ids
      align with the source slice
  1 — any mismatch (missing file, wrong line count, wrong slice, parse error)

The verifier is intentionally strict. Any workflow that needs to tolerate
partial output should call this with awareness that exit 1 means
"reconciliation needed before downstream consumers can trust the data."
"""
import argparse
import json
import math
import sys
from pathlib import Path


def chunk_ranges(total, n_chunks):
    """Mirror the workflow's chunking logic. Must stay aligned with
    chunkRanges() in audit-scoring-workflow.js."""
    size = math.ceil(total / n_chunks)
    ranges = []
    for i in range(n_chunks):
        start = i * size
        end = min(total, start + size)
        if start >= total:
            break
        ranges.append((i, start, end))
    return ranges


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="Source JSON array file (the inventory)")
    ap.add_argument("--chunks-dir", required=True, help="Directory containing chunk-N.jsonl files")
    ap.add_argument("--n-chunks", type=int, required=True, help="Number of expected chunks")
    ap.add_argument("--manifest", help="Optional manifest JSON {chunks: [{index, scored_count, output_path}]} from the workflow's structured-output return; cross-checked against on-disk reality")
    ap.add_argument("--filename-pattern", default="chunk-{i}.jsonl", help="Filename template; {i} replaced with chunk index")
    ap.add_argument("--id-field", default="vgps_id", help="Record field used for first/last identity verification")
    args = ap.parse_args()

    src = json.loads(Path(args.source).read_text())
    if not isinstance(src, list):
        print(f"FAIL: --source {args.source} is not a JSON array", file=sys.stderr)
        sys.exit(1)
    total = len(src)
    ranges = chunk_ranges(total, args.n_chunks)
    chunks_dir = Path(args.chunks_dir)
    errors = []
    summary = []

    for idx, start, end in ranges:
        path = chunks_dir / args.filename_pattern.format(i=idx)
        expected_count = end - start
        if not path.exists():
            errors.append(
                f"chunk-{idx}: file missing at {path} (expected {expected_count} records for slice [{start},{end}))"
            )
            summary.append({"chunk": idx, "status": "MISSING", "expected": expected_count, "actual": 0})
            continue
        lines = [l for l in path.read_text().splitlines() if l.strip()]
        actual_count = len(lines)
        chunk_errors = []
        if actual_count != expected_count:
            chunk_errors.append(f"line count {actual_count} != expected {expected_count}")
        # Verify by SET membership, not by order. Chunk agents are free to
        # process and emit records in any order within their slice — the
        # contract is "score every record in your slice and write them,"
        # not "preserve source order."
        try:
            actual_ids = set()
            parse_errs = 0
            for ln in lines:
                try:
                    actual_ids.add(json.loads(ln).get(args.id_field))
                except Exception:
                    parse_errs += 1
            if parse_errs:
                chunk_errors.append(f"{parse_errs} unparseable lines")
        except Exception as e:
            chunk_errors.append(f"parse error: {e}")
            errors.extend([f"chunk-{idx}: {e}" for e in chunk_errors])
            summary.append({"chunk": idx, "status": "PARSE_FAIL", "expected": expected_count, "actual": actual_count})
            continue
        expected_ids = {src[i].get(args.id_field) for i in range(start, end)}
        intrusions = actual_ids - expected_ids   # ids on disk that don't belong to this slice
        missing_from_chunk = expected_ids - actual_ids  # ids in slice not present in this chunk
        set_ok = not intrusions and not missing_from_chunk
        if intrusions:
            sample = list(intrusions)[:5]
            chunk_errors.append(f"{len(intrusions)} ids on disk don't belong to slice [{start},{end}); sample {sample}")
        if missing_from_chunk:
            sample = list(missing_from_chunk)[:5]
            chunk_errors.append(f"{len(missing_from_chunk)} ids from slice [{start},{end}) missing from chunk; sample {sample}")
        errors.extend([f"chunk-{idx}: {e}" for e in chunk_errors])
        summary.append({
            "chunk": idx,
            "status": "OK" if not chunk_errors else "MISMATCH",
            "expected": expected_count,
            "actual": actual_count,
            "set_ok": set_ok,
            "intrusions": len(intrusions),
            "missing": len(missing_from_chunk),
        })

    # Optional manifest cross-check
    if args.manifest:
        try:
            manifest = json.loads(Path(args.manifest).read_text())
            for entry in manifest.get("chunks", []):
                idx = entry.get("index")
                if idx is None:
                    continue
                path = chunks_dir / args.filename_pattern.format(i=idx)
                if not path.exists():
                    errors.append(f"manifest chunk-{idx}: reported but file missing at {path}")
                    continue
                actual = len([l for l in path.read_text().splitlines() if l.strip()])
                reported = entry.get("scored_count")
                if reported is not None and actual != reported:
                    errors.append(
                        f"manifest chunk-{idx}: reported scored_count {reported} != on-disk line count {actual}"
                    )
        except Exception as e:
            errors.append(f"manifest read failed: {e}")

    # Print summary
    print(f"verify_chunks: source={args.source} chunks_dir={args.chunks_dir} total={total} n_chunks={args.n_chunks}")
    print()
    for s in summary:
        marker = "OK  " if s["status"] == "OK" else f"FAIL"
        line = f"  [{marker}] chunk-{s['chunk']:>2}: expected={s['expected']:4} actual={s['actual']:4}"
        if "set_ok" in s:
            line += f"  set_ok={'✓' if s['set_ok'] else '✗'}"
            if s.get("intrusions"):
                line += f"  intrusions={s['intrusions']}"
            if s.get("missing"):
                line += f"  missing={s['missing']}"
        line += f"  ({s['status']})"
        print(line)

    if errors:
        print()
        print(f"VERIFICATION FAILED: {len(errors)} errors")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print()
        print(f"VERIFICATION PASSED: all {len(ranges)} expected chunks verified")
        sys.exit(0)


if __name__ == "__main__":
    main()
