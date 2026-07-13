#!/usr/bin/env python3
"""Test matching all shadow triangles to fold residual endpoint slots."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p75 = load("p75_resint", ROOT / "problems/864/compute/p75/verify_hard_fold_counterexample.py")
p88 = load("p88_resint", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")
p93 = load("p93_resint", ROOT / "problems/864/compute/p93/audit_triangle_components.py")
p97 = load("p97_resint", ROOT / "problems/864/compute/p97/audit_phase_interval_matching_w30.py")
p97_phase = load("p97_phase_match", ROOT / "problems/864/compute/p97/test_phase_interval_matching.py")


def score(values, h, b, duplicate):
    folds, triangles = p93.fold_triangle_system(values, h)
    differences = {right - left for left in values for right in values if left < right}
    shared = [(a, c, u) for a, c, u, _v in folds]
    for base, au, cu in triangles:
        a, c, _r, _s = folds[base]
        u = folds[au][2]
        assert folds[cu][2] == u
        shared.append((a, c, u))
    intervals = []
    for a, c, u in shared:
        tau, lam = u - a - c - b, h - b - u
        intervals.append((min(tau, lam), max(tau, lam)))
    slots = []
    for a, c, u, v in folds:
        lower, upper = h - b - v, h - b - u
        slots.extend((lower, upper))
        if a + c + b in differences:
            slots.append(lower if duplicate == "lower" else upper)
    matched = p97.greedy_match(intervals, slots)
    endpoint_neighbors = [
        [slot_id for slot_id, point in enumerate(slots) if point in endpoints]
        for endpoints in ({left, right} for left, right in intervals)
    ]
    endpoint_matching = p97_phase.maximum_matching(endpoint_neighbors, len(slots))
    loose_intervals = intervals[len(folds):]
    lower_slots = [h - b - v for _a, _c, _u, v in folds]
    lower_slots.extend(
        h - b - v for a, c, _u, v in folds if a + c + b in differences
    )
    lower_matching = p97.greedy_match(loose_intervals, lower_slots)
    return {"C": len(folds), "T": len(triangles), "V": len(slots) - 2 * len(folds), "matching": matched, "unmatched": len(intervals) - matched, "endpoint_matching": endpoint_matching, "endpoint_unmatched": len(intervals) - endpoint_matching, "lower_matching": lower_matching, "lower_unmatched": len(loose_intervals) - lower_matching}


def main():
    audit = json.loads((ROOT / "problems/864/compute/p97/prefix_audit.json").read_text())
    tight = audit["max_component_excess_row"]
    rows = {"P75": (p75.B, p75.h, p75.b), "P88_b1": (p88.B, p88.H, 1), "P88_b2": (p88.B, p88.H, 2), "tight": (tuple(tight["B"]), tight["h"], tight["b"])}
    print(json.dumps({name: {side: score(*args, side) for side in ("lower", "upper")} for name, args in rows.items()}, indent=2))


if __name__ == "__main__":
    main()
