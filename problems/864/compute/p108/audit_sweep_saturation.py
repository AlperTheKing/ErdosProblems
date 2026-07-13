#!/usr/bin/env python3
"""Exact audit of the P108 min-side residual matching candidate.

For the RM97 interval system, test whether a maximum matching always has
size min(number of intervals, number of slots).  Equivalently, every Hall
window deficit is bounded by the global cardinality deficit.
"""

from __future__ import annotations

import argparse
import heapq
import importlib.util
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p46 = load("p46_p108", ROOT / "problems/864/compute/p46/carry_statistics.py")
p75 = load("p75_p108", ROOT / "problems/864/compute/p75/verify_hard_fold_counterexample.py")
p88 = load("p88_p108", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")
p106 = load("p106_p108", ROOT / "problems/864/compute/p106/analyze_minimal_hall_interval.py")


def maximum_interval_point_matching(intervals, slots) -> int:
    """Maximum matching size for closed intervals versus point slots."""
    rows = sorted((row["left"], row["right"]) for row in intervals)
    points = sorted(row["value"] for row in slots)
    heap: list[int] = []
    index = matched = 0
    for point in points:
        while index < len(rows) and rows[index][0] <= point:
            heapq.heappush(heap, rows[index][1])
            index += 1
        while heap and heap[0] < point:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            matched += 1
    return matched


def score(values: tuple[int, ...], h: int, b: int) -> dict[str, object]:
    folds, triangles, intervals, slots, differences = p106.residual_system(values, h, b)
    matching = maximum_interval_point_matching(intervals, slots)
    loose_intervals = intervals[len(folds):]
    upper_slots = [
        {"value": h - b - u}
        for _a, _c, u, _v in folds
    ]
    upper_matching = maximum_interval_point_matching(loose_intervals, upper_slots)
    folds_by_color = Counter(u for _a, _c, u, _v in folds)
    triangles_by_color = Counter(folds[arm_au][2] for _base, arm_au, _arm_cu in triangles)
    positive_color_excess = sum(
        max(0, triangles_by_color[u] - folds_by_color[u])
        for u in triangles_by_color
    )
    target = min(len(intervals), len(slots))
    p = len(values)
    delta = (3 * p * p - p + 2) // 2 - h
    rm_defect = len(intervals) - matching
    return {
        "B": list(values),
        "p": p,
        "h": h,
        "b": b,
        "delta": delta,
        "C_S": len(folds),
        "T_F": len(triangles),
        "V_b": len(slots) - 2 * len(folds),
        "intervals": len(intervals),
        "slots": len(slots),
        "matching": matching,
        "RM_defect": rm_defect,
        "negative_delta_budget": max(0, -delta),
        "defect_bound_residual": rm_defect - max(0, -delta),
        "upper_matching": upper_matching,
        "upper_matching_defect": len(triangles) - upper_matching,
        "upper_defect_bound_residual": len(triangles) - upper_matching - max(0, -delta),
        "positive_color_excess": positive_color_excess,
        "color_excess_minus_p": positive_color_excess - p,
        "corrected_color_excess_residual": (
            positive_color_excess - p - (len(slots) - 2 * len(folds))
        ),
        "budgeted_color_excess_residual": (
            positive_color_excess
            - p
            - (len(slots) - 2 * len(folds))
            - max(0, -delta)
        ),
        "min_side": target,
        "min_side_defect": target - matching,
        "literal_hole": differences.isdisjoint(
            x + y + b for i, x in enumerate(values) for y in values[i:]
        ),
    }


def mandatory_rows() -> dict[str, tuple[tuple[int, ...], int, int]]:
    p94_data = json.loads(
        (ROOT / "problems/864/compute/p94/c84_archived_audit.json").read_text()
    )["translation"]["max_ratio_row"]
    p105_data = json.loads(
        (ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text()
    )["subset_search"]["q2_lifted_witness"]
    p94_values = tuple(p94_data["B"])
    return {
        "P75": (tuple(p75.B), p75.h, p75.b),
        "P94": (p94_values, int(p94_data["h"]), int(p94_data["b"])),
        "P98": (tuple(x for x in p94_values if x != 4740), int(p94_data["h"]), 1),
        "P105": (tuple(p105_data["B"]), int(p105_data["h"]), int(p105_data["b"])),
        "P88_b1": (tuple(p88.B), p88.H, 1),
        "P88_b2": (tuple(p88.B), p88.H, 2),
        "P88_q2_literal_hole": (
            tuple(2 * value + 1 for value in p88.B), 2 * p88.H, 1
        ),
    }


def width_scan(max_width: int, max_translation: int) -> dict[str, object]:
    tested = triangle_rows = failures = 0
    first = None
    maximum_defect = 0
    defect_bound_failures = 0
    first_defect_bound_failure = None
    corrected_color_excess_failures = 0
    first_corrected_color_excess_failure = None
    budgeted_color_excess_failures = 0
    first_budgeted_color_excess_failure = None
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            reflected = tuple(sorted(width - x for x in ruler))
            for gamma in range(max_translation + 1):
                values = tuple(gamma + x for x in reflected)
                h = gamma + width + 1
                for b in (1, 2):
                    tested += 1
                    row = score(values, h, b)
                    triangle_rows += int(row["T_F"] > 0)
                    defect = int(row["min_side_defect"])
                    maximum_defect = max(maximum_defect, defect)
                    if defect:
                        failures += 1
                        first = first or row
                    if int(row["defect_bound_residual"]) > 0:
                        defect_bound_failures += 1
                        first_defect_bound_failure = first_defect_bound_failure or row
                    if int(row["corrected_color_excess_residual"]) > 0:
                        corrected_color_excess_failures += 1
                        first_corrected_color_excess_failure = (
                            first_corrected_color_excess_failure or row
                        )
                    if int(row["budgeted_color_excess_residual"]) > 0:
                        budgeted_color_excess_failures += 1
                        first_budgeted_color_excess_failure = (
                            first_budgeted_color_excess_failure or row
                        )
    return {
        "max_width": max_width,
        "max_translation": max_translation,
        "tested": tested,
        "triangle_rows": triangle_rows,
        "failures": failures,
        "maximum_min_side_defect": maximum_defect,
        "first_failure": first,
        "RM_le_negative_delta_failures": defect_bound_failures,
        "first_RM_le_negative_delta_failure": first_defect_bound_failure,
        "corrected_color_excess_failures": corrected_color_excess_failures,
        "first_corrected_color_excess_failure": first_corrected_color_excess_failure,
        "budgeted_color_excess_failures": budgeted_color_excess_failures,
        "first_budgeted_color_excess_failure": first_budgeted_color_excess_failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=0)
    parser.add_argument("--max-translation", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "candidate": "maximum matching equals the smaller side",
        "mandatory": {
            name: score(*row) for name, row in mandatory_rows().items()
        },
    }
    if args.max_width:
        result["width_scan"] = width_scan(args.max_width, args.max_translation)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
