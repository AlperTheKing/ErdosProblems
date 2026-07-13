#!/usr/bin/env python3
"""Extract minimal RM97 Hall-deficient windows and endpoint transfers."""

from __future__ import annotations

import argparse
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


p93 = load("p93_p106", ROOT / "problems/864/compute/p93/audit_triangle_components.py")


def residual_system(values: tuple[int, ...], h: int, b: int):
    folds, triangles = p93.fold_triangle_system(values, h)
    differences = {right - left for left in values for right in values if left < right}
    intervals = []
    for fold_id, (a, c, u, _v) in enumerate(folds):
        tau, lam = u - a - c - b, h - b - u
        intervals.append({
            "kind": "canonical", "id": fold_id, "support": [fold_id],
            "tau": tau, "lambda": lam, "left": min(tau, lam), "right": max(tau, lam),
        })
    for triangle_id, (base, arm_au, arm_cu) in enumerate(triangles):
        a, c, _r, _s = folds[base]
        u = folds[arm_au][2]
        assert folds[arm_cu][2] == u
        tau, lam = u - a - c - b, h - b - u
        intervals.append({
            "kind": "loose", "id": triangle_id,
            "support": [base, arm_au, arm_cu],
            "tau": tau, "lambda": lam, "left": min(tau, lam), "right": max(tau, lam),
        })
    slots = []
    for fold_id, (a, c, u, v) in enumerate(folds):
        lower, upper = h - b - v, h - b - u
        slots.extend((
            {"fold": fold_id, "kind": "L", "value": lower},
            {"fold": fold_id, "kind": "U", "value": upper},
        ))
        if a + c + b in differences:
            slots.append({"fold": fold_id, "kind": "V", "value": lower})
    return folds, triangles, intervals, slots, differences


def deficient_windows(intervals, slots):
    lefts = sorted({row["left"] for row in intervals})
    rights = sorted({row["right"] for row in intervals})
    rows = []
    for left in lefts:
        for right in rights:
            if left > right:
                continue
            contained = [i for i, row in enumerate(intervals) if left <= row["left"] and row["right"] <= right]
            slot_ids = [i for i, row in enumerate(slots) if left <= row["value"] <= right]
            deficit = len(contained) - len(slot_ids)
            if deficit > 0:
                rows.append({
                    "left": left, "right": right, "deficit": deficit,
                    "interval_ids": contained, "slot_ids": slot_ids,
                })
    minimal = []
    for row in rows:
        if not any(
            other["left"] >= row["left"] and other["right"] <= row["right"]
            and (other["left"], other["right"]) != (row["left"], row["right"])
            for other in rows
        ):
            minimal.append(row)
    return rows, minimal


def summarize_window(window, folds, triangles, intervals, slots, differences):
    left, right = window["left"], window["right"]
    contained = [intervals[i] for i in window["interval_ids"]]
    canonical = [row for row in contained if row["kind"] == "canonical"]
    loose = [row for row in contained if row["kind"] == "loose"]
    inside_slots = [slots[i] for i in window["slot_ids"]]
    crossing = []
    outside = []
    for fold_id, (a, c, u, v) in enumerate(folds):
        lower, upper = sorted((h_global - b_global - v, h_global - b_global - u))
        inside = int(left <= lower <= right) + int(left <= upper <= right)
        if inside == 1:
            crossing.append(fold_id)
        elif inside == 0 and lower < left and right < upper:
            outside.append(fold_id)
    transfer = Counter()
    base_relations = []
    for row in loose:
        base, arm_au, arm_cu = row["support"]
        a, c, r, _s = folds[base]
        u = folds[arm_au][2]
        R = r - u
        base_row = intervals[base]
        relation = (
            "base_inside" if left <= base_row["left"] and base_row["right"] <= right
            else "base_contains" if base_row["left"] < left and right < base_row["right"]
            else "base_crosses" if not (base_row["right"] < left or right < base_row["left"])
            else "base_disjoint"
        )
        transfer[relation] += 1
        base_relations.append({
            "triangle": row["id"], "base": base, "R": R,
            "loose_interval": [row["left"], row["right"]],
            "base_interval": [base_row["left"], base_row["right"]],
            "relation": relation,
            "base_phase_label": a + c + b_global,
            "base_phase_collided": a + c + b_global in differences,
        })
    support_counts = Counter(fold for row in loose for fold in row["support"])
    return {
        "J": [left, right], "deficit": window["deficit"],
        "contained_intervals": len(contained),
        "contained_canonical": len(canonical), "contained_loose": len(loose),
        "slots_in_J": len(inside_slots),
        "slot_kind_counts": dict(sorted(Counter(row["kind"] for row in inside_slots).items())),
        "crossing_fold_intervals": len(crossing),
        "strictly_containing_fold_intervals": len(outside),
        "base_transfer_counts": dict(sorted(transfer.items())),
        "distinct_support_folds": len(support_counts),
        "maximum_support_multiplicity": max(support_counts.values(), default=0),
        "base_relations": base_relations,
    }


def analyze(values: tuple[int, ...], h: int, b: int):
    global h_global, b_global
    h_global, b_global = h, b
    folds, triangles, intervals, slots, differences = residual_system(values, h, b)
    deficient, minimal = deficient_windows(intervals, slots)
    p = len(values)
    return {
        "B": list(values), "p": p, "h": h, "b": b,
        "delta": (3 * p * p - p + 2) // 2 - h,
        "C_S": len(folds), "T_F": len(triangles),
        "V_b": len(slots) - 2 * len(folds),
        "intervals": len(intervals), "slots": len(slots),
        "deficient_windows": len(deficient),
        "minimal_deficient_windows": [
            summarize_window(row, folds, triangles, intervals, slots, differences)
            for row in minimal
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.witness:
        data = json.loads(args.witness.read_text())
        witness = data["positive_defect_RM97_witness"]
        if witness is None:
            raise ValueError("input contains no positive-defect RM97 witness")
    else:
        data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
        witness = data["subset_search"]["q2_lifted_witness"]
    result = analyze(tuple(witness["B"]), int(witness["h"]), int(witness["b"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: value for key, value in result.items() if key != "B"}, indent=2))


if __name__ == "__main__":
    main()
