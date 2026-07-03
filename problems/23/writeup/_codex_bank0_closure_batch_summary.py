#!/usr/bin/env python3
"""Aggregate Bank0 B0-5 closure-trace shard summaries.

The shard emitter writes one summary JSON per `--skip-records/--limit-cuts`
window.  This helper recomputes the total no-hom routing-record count from the
source JSONL and emits a reproducible combined coverage summary.
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from pathlib import Path


ROUTING_KIND = "pure_no_hom_or_no_mono_hom"


def count_routing_records(source: Path) -> int:
    total = 0
    with source.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("kind") == ROUTING_KIND:
                total += 1
    return total


def load_summary(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        rec = json.load(fh)
    if rec.get("schema") != "bank0_closure_trace_summary_v1":
        raise ValueError(f"unexpected schema in {path}: {rec.get('schema')!r}")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="hom-trace JSONL source")
    ap.add_argument("--summaries", nargs="*", default=[], help="summary JSON files")
    ap.add_argument("--glob", default="", help="optional glob for summary JSON files")
    ap.add_argument("--output", required=True, help="combined summary JSON output")
    args = ap.parse_args()

    summary_paths = [Path(p) for p in args.summaries]
    if args.glob:
        summary_paths.extend(Path(p) for p in glob.glob(args.glob))
    summary_paths = sorted(set(summary_paths), key=lambda p: str(p))
    if not summary_paths:
        raise SystemExit("no summary files provided")

    items = [load_summary(path) for path in summary_paths]
    counts: Counter[str] = Counter()
    fails = 0
    first_fail = None
    for rec in items:
        for key, value in rec.get("counts", {}).items():
            counts[key] += int(value)
        fails += int(rec.get("counts", {}).get("fails", 0))
        if first_fail is None and rec.get("first_fail") is not None:
            first_fail = rec["first_fail"]

    source = Path(args.source)
    total = count_routing_records(source)
    checked = counts.get("records", 0)
    out = {
        "schema": "bank0_closure_trace_n11_batches_v2",
        "source": str(source),
        "total_no_hom_records": total,
        "checked_records": checked,
        "unchecked_records": total - checked,
        "batch_summaries": [str(path) for path in summary_paths],
        "counts": dict(sorted(counts.items())),
        "fails": fails,
        "first_fail": first_fail,
        "verdict": "PASS_PARTIAL" if fails == 0 and checked < total else ("PASS" if fails == 0 else "FAIL"),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
