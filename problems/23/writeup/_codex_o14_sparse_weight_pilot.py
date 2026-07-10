#!/usr/bin/env python3
"""Emit a standalone Lean module containing one O14 slot's exact weights."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_solution(path: Path) -> list[tuple[int, int, int]]:
    rows: list[tuple[int, int, int]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rec = json.loads(line)
            rows.append((int(rec["source_col"]), int(rec["num"]), int(rec["den"])))
    rows.sort()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--namespace", default="Chart000Weights")
    args = parser.parse_args()

    rows = read_solution(args.solution)
    lines = [
        "import Mathlib",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        f"namespace {args.namespace}",
        "",
        f"def count : Nat := {len(rows)}",
        "",
    ]
    for index, (source_col, num, den) in enumerate(rows):
        lines.append(f"def sourceCol{index:04d} : Nat := {source_col}")
        lines.append(
            f"def weight{index:04d} : Rat := "
            f"(({num} : Rat) / ({den} : Rat))"
        )
        lines.append("")
    lines.extend([
        f"end {args.namespace}",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "weights": len(rows),
        "bytes": args.out.stat().st_size,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
