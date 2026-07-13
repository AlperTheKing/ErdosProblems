#!/usr/bin/env python3
"""Verify the exact P108 sweep identities on all mandatory hard rows."""

from __future__ import annotations

import argparse
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


p108 = load("sweep_verify_p108", ROOT / "problems/864/compute/p108/audit_sweep_saturation.py")
p106 = p108.p106


def verify_row(values: tuple[int, ...], h: int, b: int) -> dict[str, object]:
    folds, triangles, intervals, slots, _differences = p106.residual_system(values, h, b)
    canonical = intervals[:len(folds)]
    loose = intervals[len(folds):]
    ordinary_slots = [row for row in slots if row["kind"] in ("L", "U")]
    extra_slots = [row for row in slots if row["kind"] == "V"]
    upper_slots = [h - b - u for _a, _c, u, _v in folds]
    coordinates = sorted(
        {row["left"] for row in intervals}
        | {row["right"] for row in intervals}
        | {row["value"] for row in slots}
    )
    global_excess = len(intervals) - len(slots)
    windows = full_identity_failures = upper_identity_failures = 0
    maximum_full_deficit = maximum_upper_deficit = None
    full_argmax = upper_argmax = None
    for left in coordinates:
        for right in coordinates:
            if left > right:
                continue
            windows += 1
            demand_inside = sum(
                left <= row["left"] and row["right"] <= right
                for row in intervals
            )
            slots_inside = sum(
                left <= row["value"] <= right for row in slots
            )
            full_deficit = demand_inside - slots_inside
            canonical_avoiding = sum(
                not (left <= row["left"] <= right)
                and not (left <= row["right"] <= right)
                for row in canonical
            )
            extra_outside = sum(
                not (left <= row["value"] <= right) for row in extra_slots
            )
            loose_escaping = sum(
                not (left <= row["left"] and row["right"] <= right)
                for row in loose
            )
            reconstructed = (
                global_excess + canonical_avoiding + extra_outside - loose_escaping
            )
            if reconstructed != full_deficit:
                full_identity_failures += 1
            loose_inside = sum(
                left <= row["left"] and row["right"] <= right for row in loose
            )
            upper_inside = sum(left <= point <= right for point in upper_slots)
            upper_deficit = loose_inside - upper_inside
            color_low, color_high = h - b - right, h - b - left
            selected_by_color = 0
            for row in loose:
                u = h - b - row["lambda"]
                tau = row["tau"]
                selected_by_color += (
                    color_low <= u <= color_high and left <= tau <= right
                )
            folds_by_color = sum(
                color_low <= u <= color_high for _a, _c, u, _v in folds
            )
            if selected_by_color - folds_by_color != upper_deficit:
                upper_identity_failures += 1
            if maximum_full_deficit is None or full_deficit > maximum_full_deficit:
                maximum_full_deficit = full_deficit
                full_argmax = [left, right]
            if maximum_upper_deficit is None or upper_deficit > maximum_upper_deficit:
                maximum_upper_deficit = upper_deficit
                upper_argmax = [left, right]
    if full_identity_failures or upper_identity_failures:
        raise AssertionError((full_identity_failures, upper_identity_failures))
    score = p108.score(values, h, b)
    return {
        key: score[key]
        for key in (
            "p", "h", "b", "delta", "C_S", "T_F", "V_b",
            "literal_hole", "RM_defect", "upper_matching_defect"
        )
    } | {
        "windows": windows,
        "full_sweep_identity_failures": full_identity_failures,
        "upper_color_identity_failures": upper_identity_failures,
        "maximum_full_window_deficit": maximum_full_deficit,
        "maximum_full_window": full_argmax,
        "maximum_upper_window_deficit": maximum_upper_deficit,
        "maximum_upper_window": upper_argmax,
        "ordinary_slots_checked": len(ordinary_slots),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "rows": {
            name: verify_row(*row)
            for name, row in p108.mandatory_rows().items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
