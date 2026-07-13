#!/usr/bin/env python3
"""Complete width-30 exact gate for the P108 upper-slot candidate."""

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


p46 = load("p46_upper_p108", ROOT / "problems/864/compute/p46/carry_statistics.py")
p108 = load("sweep_upper_p108", ROOT / "problems/864/compute/p108/audit_sweep_saturation.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tested = holes = triangle_rows = failures = color_excess_failures = 0
    maximum_defect = 0
    first = worst = first_color_excess = None
    for width in range(1, args.max_width + 1):
        for ruler in p46.sidon_rulers(width):
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            reflected = tuple(sorted(width - x for x in ruler))
            forbidden = p46.forbidden_three_minus_one(ruler)
            for gamma in range(max_gamma + 1):
                values = tuple(gamma + x for x in reflected)
                h = gamma + width + 1
                for b in (1, 2):
                    tested += 1
                    if 2 * width + 2 * gamma + b in forbidden:
                        continue
                    holes += 1
                    row = p108.score(values, h, b)
                    if not bool(row["literal_hole"]) or int(row["delta"]) <= 0:
                        raise AssertionError(("gate mismatch", row))
                    triangle_rows += int(row["T_F"] > 0)
                    defect = int(row["upper_matching_defect"])
                    maximum_defect = max(maximum_defect, defect)
                    if worst is None or (defect, int(row["T_F"])) > (
                        int(worst["upper_matching_defect"]), int(worst["T_F"])
                    ):
                        worst = row
                    if defect:
                        failures += 1
                        first = first or row
                    if int(row["color_excess_minus_p"]) > 0:
                        color_excess_failures += 1
                        first_color_excess = first_color_excess or row
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "max_width": args.max_width,
        "positive_defect_candidates": tested,
        "literal_holes": holes,
        "triangle_rows": triangle_rows,
        "upper_matching_failures": failures,
        "maximum_upper_matching_defect": maximum_defect,
        "first_failure": first,
        "color_excess_le_p_failures": color_excess_failures,
        "first_color_excess_le_p_failure": first_color_excess,
        "worst_row": worst,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
