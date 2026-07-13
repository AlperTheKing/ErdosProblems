#!/usr/bin/env python3
"""Exact gate for matching color excess to arm-pair differences.

For each arm color u, there are n_u supporting folds and t_u loose
triangles.  The demand is max(0, t_u - n_u).  A loose triangle whose two
arms have high mates v_i, v_j exposes the represented positive difference
|v_i-v_j|.  This script tests whether all color demands can be matched to
distinct exposed differences.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p108 = load(
    "p108_p122",
    ROOT / "problems/864/compute/p108/audit_sweep_saturation.py",
)
p46 = p108.p46
p106 = p108.p106


def maximum_capacitated_matching(
    demand: dict[int, int], neighbors: dict[int, set[int]]
) -> tuple[int, dict[int, int]]:
    """Match identical demand copies of each color to unit resources."""

    resource_owner: dict[int, tuple[int, int]] = {}

    def augment(copy: tuple[int, int], seen: set[int]) -> bool:
        color, _copy_index = copy
        for resource in sorted(neighbors[color]):
            if resource in seen:
                continue
            seen.add(resource)
            previous = resource_owner.get(resource)
            if previous is None or augment(previous, seen):
                resource_owner[resource] = copy
                return True
        return False

    for color in sorted(demand, key=lambda u: (len(neighbors[u]), u)):
        for copy_index in range(demand[color]):
            augment((color, copy_index), set())
    matched_by_color = Counter(copy[0] for copy in resource_owner.values())
    return len(resource_owner), dict(matched_by_color)


def score(values: tuple[int, ...], h: int, b: int) -> dict[str, object]:
    folds, triangles, _intervals, _slots, differences = p106.residual_system(
        values, h, b
    )
    fold_count = Counter(u for _a, _c, u, _v in folds)
    triangle_count: Counter[int] = Counter()
    neighbors: dict[int, set[int]] = defaultdict(set)
    for _base, arm_au, arm_cu in triangles:
        left = folds[arm_au]
        right = folds[arm_cu]
        if left[2] != right[2]:
            raise AssertionError("arm colors disagree")
        color = left[2]
        difference = abs(left[3] - right[3])
        if difference == 0 or difference not in differences:
            raise AssertionError("invalid represented arm-pair difference")
        triangle_count[color] += 1
        neighbors[color].add(difference)

    demand = {
        color: triangle_count[color] - fold_count[color]
        for color in triangle_count
        if triangle_count[color] > fold_count[color]
    }
    required = sum(demand.values())
    matched, matched_by_color = maximum_capacitated_matching(demand, neighbors)
    p = len(values)
    delta = (3 * p * p - p + 2) // 2 - h
    literal_hole = differences.isdisjoint(
        x + y + b for index, x in enumerate(values) for y in values[index:]
    )
    return {
        "B": list(values),
        "p": p,
        "h": h,
        "b": b,
        "delta": delta,
        "literal_hole": literal_hole,
        "C_S": len(folds),
        "T_F": len(triangles),
        "positive_color_excess": required,
        "exposed_differences": len(set().union(*(neighbors.values() or [set()]))),
        "matching": matched,
        "deficit": required - matched,
        "demand": {str(key): value for key, value in sorted(demand.items())},
        "matched_by_color": {
            str(key): value for key, value in sorted(matched_by_color.items())
        },
    }


def width_scan(max_width: int, max_translation: int) -> dict[str, object]:
    tested = triangle_rows = positive_holes = failures = 0
    first_failure = None
    maximum_excess = maximum_deficit = 0
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            reflected = tuple(sorted(width - value for value in ruler))
            for gamma in range(max_translation + 1):
                values = tuple(gamma + value for value in reflected)
                h = gamma + width + 1
                for b in (1, 2):
                    tested += 1
                    row = score(values, h, b)
                    if int(row["T_F"]) == 0:
                        continue
                    triangle_rows += 1
                    maximum_excess = max(
                        maximum_excess, int(row["positive_color_excess"])
                    )
                    if bool(row["literal_hole"]) and int(row["delta"]) > 0:
                        positive_holes += 1
                    if int(row["deficit"]) > 0:
                        failures += 1
                        maximum_deficit = max(maximum_deficit, int(row["deficit"]))
                        first_failure = first_failure or row
    return {
        "max_width": max_width,
        "max_translation": max_translation,
        "tested": tested,
        "triangle_rows": triangle_rows,
        "positive_defect_literal_hole_triangle_rows": positive_holes,
        "failures": failures,
        "maximum_positive_color_excess": maximum_excess,
        "maximum_deficit": maximum_deficit,
        "first_failure": first_failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=0)
    parser.add_argument("--max-translation", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "exact Python integers and augmenting-path matching",
        "candidate": "color excess matches to distinct arm-pair differences",
        "mandatory": {
            name: score(*row) for name, row in p108.mandatory_rows().items()
        },
    }
    if args.max_width:
        result["width_scan"] = width_scan(args.max_width, args.max_translation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
