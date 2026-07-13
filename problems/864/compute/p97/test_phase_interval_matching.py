#!/usr/bin/env python3
"""Test global matching from triangles to folds in their phase-label hulls."""

from __future__ import annotations

import importlib.util
import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p75 = load("p75_interval", ROOT / "problems/864/compute/p75/verify_hard_fold_counterexample.py")
p88 = load("p88_interval", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")
p92 = load("p92_interval", ROOT / "problems/864/compute/p92/verify_hexagon_hall_counterexample.py")
p93 = load("p93_interval", ROOT / "problems/864/compute/p93/audit_triangle_components.py")


def maximum_matching(neighbors, right_count):
    left_match = [-1] * len(neighbors)
    right_match = [-1] * right_count
    while True:
        parent = [-1] * len(neighbors)
        via = [-1] * len(neighbors)
        queue = deque(i for i, match in enumerate(left_match) if match < 0)
        seen = set(queue)
        endpoint = None
        while queue and endpoint is None:
            left = queue.popleft()
            for right in neighbors[left]:
                other = right_match[right]
                if other < 0:
                    endpoint = (left, right)
                    break
                if other not in seen:
                    seen.add(other); parent[other] = left; via[other] = right
                    queue.append(other)
        if endpoint is None:
            break
        left, right = endpoint
        while left >= 0:
            old_right = left_match[left]
            left_match[left] = right; right_match[right] = left
            next_left = parent[left]
            if next_left < 0:
                break
            right = via[left]
            left = next_left
            assert old_right == right
    return sum(match >= 0 for match in left_match)


def score(values, h, b, extra_bad):
    folds, triangles = p93.fold_triangle_system(values, h)
    labels = [a + c + b for a, c, _u, _v in folds]
    differences = {right - left for left in values for right in values if left < right}
    slots = []
    for fold_id, label in enumerate(labels):
        slots.append((fold_id, label))
        if extra_bad and label in differences:
            slots.append((fold_id, label))
    neighbors = []
    for triangle in triangles:
        low = min(labels[i] for i in triangle)
        high = max(labels[i] for i in triangle)
        neighbors.append([slot_id for slot_id, (_fold_id, label) in enumerate(slots) if low <= label <= high])
    matching = maximum_matching(neighbors, len(slots))
    return {
        "folds": len(folds), "triangles": len(triangles),
        "bad": sum(label in differences for label in labels),
        "slots": len(slots), "matching": matching,
        "unmatched": len(triangles) - matching,
    }


def main():
    audit = json.loads((ROOT / "problems/864/compute/p97/prefix_audit.json").read_text())
    tight = audit["max_component_excess_row"]
    rows = {
        "P75": (p75.B, p75.h, p75.b),
        "P88_b1": (p88.B, p88.H, 1),
        "P88_b2": (p88.B, p88.H, 2),
        "P92": (p92.B, p92.H, 1),
        "tight": (tuple(tight["B"]), tight["h"], tight["b"]),
    }
    print(json.dumps({name: {
        "single": score(*args, extra_bad=False),
        "corrected": score(*args, extra_bad=True),
    } for name, args in rows.items()}, indent=2))


if __name__ == "__main__":
    main()
