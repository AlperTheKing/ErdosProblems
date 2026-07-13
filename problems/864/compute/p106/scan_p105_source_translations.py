#!/usr/bin/env python3
"""Exact RM97 scan of every positive-defect P105 source translation."""

from __future__ import annotations

import argparse
import heapq
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106 = load("p106_windows", ROOT / "problems/864/compute/p106/analyze_minimal_hall_interval.py")


def greedy_match(intervals, slots):
    intervals = sorted((row["left"], row["right"]) for row in intervals)
    points = sorted(row["value"] for row in slots)
    heap = []
    index = matched = 0
    for point in points:
        while index < len(intervals) and intervals[index][0] <= point:
            heapq.heappush(heap, intervals[index][1]); index += 1
        if heap and heap[0] < point:
            return matched
        if heap:
            heapq.heappop(heap); matched += 1
    return matched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    source = data["subset_search"]["source_subset"]
    base = tuple(source["B"])
    p, width = len(base), base[-1]
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = baseline - width - 2
    rows = failures = scalar_failures = holes = 0
    minimum_slack = None
    minimum_row = None
    first_failure = None
    for gamma in range(max_gamma + 1):
        values = tuple(x + gamma for x in base)
        h = width + gamma + 1
        for b in (1, 2):
            rows += 1
            folds, triangles, intervals, slots, differences = p106.residual_system(values, h, b)
            matched = greedy_match(intervals, slots)
            slack = len(slots) - len(intervals)
            correction = len(slots) - 2 * len(folds)
            scalar_excess = len(triangles) - len(folds) - correction
            literal_hole = correction == 0 and differences.isdisjoint(
                x + y + b for i, x in enumerate(values) for y in values[i:]
            )
            holes += literal_hole
            scalar_failures += scalar_excess > 0
            if minimum_slack is None or slack < minimum_slack:
                minimum_slack = slack
                minimum_row = {
                    "gamma": gamma, "b": b, "delta": baseline - h,
                    "C_S": len(folds), "T_F": len(triangles),
                    "V_b": correction, "slot_minus_interval": slack,
                    "matched": matched, "literal_hole": literal_hole,
                }
            if matched != len(intervals):
                failures += 1
                if first_failure is None:
                    first_failure = {
                        "B": values, "gamma": gamma, "b": b,
                        "delta": baseline - h, "C_S": len(folds),
                        "T_F": len(triangles), "V_b": correction,
                        "intervals": len(intervals), "slots": len(slots),
                        "matched": matched,
                    }
    result = {
        "source_p": p, "source_width": width,
        "positive_defect_translations": max_gamma + 1,
        "phase_rows": rows, "literal_holes": holes,
        "scalar_failures": scalar_failures, "RM97_failures": failures,
        "minimum_scalar_slack_row": minimum_row,
        "first_RM97_failure": first_failure,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
