#!/usr/bin/env python3
"""Exact parallel scan of the C87 universal common-bank ratio."""

from __future__ import annotations

import argparse
import importlib.util
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
C87_PATH = HERE / "C87_horn_implication.py"


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def load_c87():
    spec = importlib.util.spec_from_file_location("c87_horn", C87_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load C87_horn_implication.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def one(cutoff: int) -> dict:
    c87 = load_c87()
    row = c87.solve(cutoff)
    hard = len(row["hard_roots"])
    common = int(row["common_neighbor_count"])
    return {
        "cutoff": cutoff,
        "hard": hard,
        "common": common,
        "margin_4C_minus_3H": 4 * common - 3 * hard,
        "matching": int(row["matching_size"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(1 <= args.workers <= 16, ("worker-cap", args.workers))
    gate = json.loads(args.gate.read_text(encoding="utf-8"))
    cutoffs = sorted({int(row["selected_cutoff"]) for row in gate["rows"]})
    require(cutoffs, "empty-cutoff-list")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(one, cutoffs, chunksize=1))
    rows.sort(key=lambda row: row["cutoff"])
    worst = min(rows, key=lambda row: (Fraction(row["common"], row["hard"]), row["cutoff"]))
    failures = [row for row in rows if row["margin_4C_minus_3H"] <= 0]
    output = {
        "schema": "C91-common-bank-v1",
        "cutoff_count": len(rows),
        "cutoff_first": rows[0]["cutoff"],
        "cutoff_last": rows[-1]["cutoff"],
        "strict_three_quarters_failures": failures,
        "worst_ratio": [worst["common"], worst["hard"]],
        "worst_row": worst,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key != "rows"}, sort_keys=True))


if __name__ == "__main__":
    main()
