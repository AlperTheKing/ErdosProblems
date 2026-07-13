#!/usr/bin/env python3
"""Audit phase-hull interval matching on the complete width-30 hole domain."""

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


p46 = load("p46_interval_w30", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_interval_w30", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")
p93 = load("p93_interval_w30", ROOT / "problems/864/compute/p93/audit_triangle_components.py")


def greedy_match(intervals, slots):
    intervals = sorted(intervals)
    slots = sorted(slots)
    heap = []
    index = matched = 0
    for point in slots:
        while index < len(intervals) and intervals[index][0] <= point:
            heapq.heappush(heap, intervals[index][1])
            index += 1
        if heap and heap[0] < point:
            return matched
        if heap:
            heapq.heappop(heap)
            matched += 1
    return matched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--unrestricted", action="store_true")
    args = parser.parse_args()
    holes = triangle_rows = failures = 0
    witness = None
    for width in range(1, args.max_width + 1):
        for ruler in p46.sidon_rulers(width):
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = p46.forbidden_three_minus_one(ruler)
            z = tuple(sorted(width - x for x in ruler))
            differences = {right - left for left in z for right in z if left < right}
            for b in (1, 2):
                for gamma in range(max_gamma + 1):
                    is_hole = 2 * width + 2 * gamma + b not in forbidden
                    if not args.unrestricted and not is_hole:
                        continue
                    holes += 1
                    values = tuple(gamma + x for x in z)
                    h = gamma + width + 1
                    folds, triangles = p93.fold_triangle_system(values, h)
                    if not triangles:
                        continue
                    triangle_rows += 1
                    labels = [a + c + b for a, c, _u, _v in folds]
                    intervals = [
                        (min(labels[i] for i in triangle), max(labels[i] for i in triangle))
                        for triangle in triangles
                    ]
                    slots = list(labels)
                    if args.unrestricted:
                        slots.extend(label for label in labels if label in differences)
                    matched = greedy_match(intervals, slots)
                    if matched != len(triangles):
                        failures += 1
                        if witness is None:
                            witness = {
                                "B": values, "h": h, "b": b,
                                "C_S": len(folds), "T_F": len(triangles),
                                "matching": matched,
                            }
    print(json.dumps({
        "max_width": args.max_width, "rows": holes, "unrestricted": args.unrestricted,
        "triangle_rows": triangle_rows, "matching_failures": failures,
        "first_failure": witness,
    }, indent=2))


if __name__ == "__main__":
    main()
