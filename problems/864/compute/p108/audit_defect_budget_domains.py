#!/usr/bin/env python3
"""Exact P108 audit on all normalized subsets of the P98 parent."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "problems/864/compute/p98"))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


p98 = load("p98_p108", ROOT / "problems/864/compute/p98/search_transformed_parent.py")
p108 = load("sweep_p108", ROOT / "problems/864/compute/p108/audit_sweep_saturation.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tested = min_side_failures = defect_bound_failures = 0
    positive_defect_rows = positive_defect_rm_failures = 0
    literal_holes = literal_hole_rm_failures = 0
    literal_hole_upper_failures = literal_hole_upper_bound_failures = 0
    literal_hole_color_excess_failures = 0
    first_min_side = first_bound = first_positive = first_hole = None
    first_upper = first_upper_bound = None
    first_color_excess = None
    maximum_bound_residual = None
    corrected_color_excess_failures = 0
    first_corrected_color_excess = None
    budgeted_color_excess_failures = 0
    first_budgeted_color_excess = None
    lifted_tested = lifted_rm_failures = lifted_bound_failures = 0
    lifted_upper_failures = lifted_upper_bound_failures = 0
    lifted_color_excess_failures = 0
    first_lifted_rm = first_lifted_bound = None
    first_lifted_upper = first_lifted_upper_bound = None
    first_lifted_color_excess = None
    for values in p98.subset_bases(p98.SOURCE):
        h = values[-1] + 1
        for b in (1, 2):
            tested += 1
            row = p108.score(tuple(values), h, b)
            rm_defect = int(row["RM_defect"])
            min_defect = int(row["min_side_defect"])
            residual = int(row["defect_bound_residual"])
            if min_defect > 0:
                min_side_failures += 1
                first_min_side = first_min_side or row
            if residual > 0:
                defect_bound_failures += 1
                first_bound = first_bound or row
            if int(row["delta"]) > 0:
                positive_defect_rows += 1
                if rm_defect > 0:
                    positive_defect_rm_failures += 1
                    first_positive = first_positive or row
            if bool(row["literal_hole"]):
                literal_holes += 1
                if rm_defect > 0:
                    literal_hole_rm_failures += 1
                    first_hole = first_hole or row
                if int(row["upper_matching_defect"]) > 0:
                    literal_hole_upper_failures += 1
                    first_upper = first_upper or row
                if int(row["upper_defect_bound_residual"]) > 0:
                    literal_hole_upper_bound_failures += 1
                    first_upper_bound = first_upper_bound or row
                if int(row["color_excess_minus_p"]) > 0:
                    literal_hole_color_excess_failures += 1
                    first_color_excess = first_color_excess or row
            if maximum_bound_residual is None or residual > int(maximum_bound_residual[0]):
                maximum_bound_residual = (residual, row)
            if int(row["corrected_color_excess_residual"]) > 0:
                corrected_color_excess_failures += 1
                first_corrected_color_excess = first_corrected_color_excess or row
            if int(row["budgeted_color_excess_residual"]) > 0:
                budgeted_color_excess_failures += 1
                first_budgeted_color_excess = first_budgeted_color_excess or row
        lifted_values = tuple(2 * value + 1 for value in values)
        lifted = p108.score(lifted_values, 2 * h, 1)
        lifted_tested += 1
        if not bool(lifted["literal_hole"]):
            raise AssertionError(("parity lift is not a literal hole", lifted))
        if int(lifted["RM_defect"]) > 0:
            lifted_rm_failures += 1
            first_lifted_rm = first_lifted_rm or lifted
        if int(lifted["defect_bound_residual"]) > 0:
            lifted_bound_failures += 1
            first_lifted_bound = first_lifted_bound or lifted
        if int(lifted["upper_matching_defect"]) > 0:
            lifted_upper_failures += 1
            first_lifted_upper = first_lifted_upper or lifted
        if int(lifted["upper_defect_bound_residual"]) > 0:
            lifted_upper_bound_failures += 1
            first_lifted_upper_bound = first_lifted_upper_bound or lifted
        if int(lifted["color_excess_minus_p"]) > 0:
            lifted_color_excess_failures += 1
            first_lifted_color_excess = first_lifted_color_excess or lifted
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "domain": "all normalized orientations of all subsets of the P98 17-mark parent with at least three marks, b=1,2",
        "tested": tested,
        "min_side_saturation_failures": min_side_failures,
        "first_min_side_saturation_failure": first_min_side,
        "RM_le_negative_delta_failures": defect_bound_failures,
        "first_RM_le_negative_delta_failure": first_bound,
        "positive_defect_rows": positive_defect_rows,
        "positive_defect_RM_failures": positive_defect_rm_failures,
        "first_positive_defect_RM_failure": first_positive,
        "literal_holes": literal_holes,
        "literal_hole_RM_failures": literal_hole_rm_failures,
        "first_literal_hole_RM_failure": first_hole,
        "literal_hole_upper_matching_failures": literal_hole_upper_failures,
        "first_literal_hole_upper_matching_failure": first_upper,
        "literal_hole_upper_le_negative_delta_failures": literal_hole_upper_bound_failures,
        "first_literal_hole_upper_le_negative_delta_failure": first_upper_bound,
        "literal_hole_color_excess_le_p_failures": literal_hole_color_excess_failures,
        "first_literal_hole_color_excess_le_p_failure": first_color_excess,
        "maximum_defect_bound_residual_row": maximum_bound_residual[1],
        "corrected_color_excess_failures": corrected_color_excess_failures,
        "first_corrected_color_excess_failure": first_corrected_color_excess,
        "budgeted_color_excess_failures": budgeted_color_excess_failures,
        "first_budgeted_color_excess_failure": first_budgeted_color_excess,
        "parity_lift_domain": {
            "definition": "B -> 2B+1, h -> 2h, b=1 for every normalized parent subset",
            "tested": lifted_tested,
            "literal_hole_RM_failures": lifted_rm_failures,
            "first_literal_hole_RM_failure": first_lifted_rm,
            "RM_le_negative_delta_failures": lifted_bound_failures,
            "first_RM_le_negative_delta_failure": first_lifted_bound,
            "upper_matching_failures": lifted_upper_failures,
            "first_upper_matching_failure": first_lifted_upper,
            "upper_le_negative_delta_failures": lifted_upper_bound_failures,
            "first_upper_le_negative_delta_failure": first_lifted_upper_bound,
            "color_excess_le_p_failures": lifted_color_excess_failures,
            "first_color_excess_le_p_failure": first_lifted_color_excess,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
