#!/usr/bin/env python3
"""Integer verification of the C82 base-row obstruction probes."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C56 = load("c82_c56", "C56_dual_cert.py")
C75 = load("c82_c75", "C75_dual_exact_replay.py")
C79 = load("c82_c79_probe", "C79_fractional_boundary.py")


def integer(value: int | float) -> int:
    result = int(value)
    if value != result:
        raise RuntimeError(f"nonintegral model datum {value}")
    return result


def check_rows(model, point: list[int]) -> list[list[object]]:
    lhs = [0] * len(model.rhs)
    for row, column, coefficient in zip(model.rows, model.cols, model.data):
        lhs[row] += integer(coefficient) * point[column]
    return [
        [model.row_names[row], value - integer(model.rhs[row])]
        for row, value in enumerate(lhs)
        if value > integer(model.rhs[row])
    ]


def check_bounds(model, point: list[int]) -> None:
    bounds = (
        model.bounds
        if hasattr(model, "bounds")
        else list(zip(model.lower, model.upper))
    )
    for name, value, (lower, upper) in zip(model.names, point, bounds):
        if Fraction(str(lower)) > value:
            raise RuntimeError(f"lower-bound violation at {name}")
        if upper is not None and value > Fraction(str(upper)):
            raise RuntimeError(f"upper-bound violation at {name}")


def dot(left: list[int], right: list[int]) -> int:
    return sum(integer(a) * b for a, b in zip(left, right))


def audit(limit: int) -> dict:
    c56_model, c56_objective, c56_hard, _ = C56.build(limit)
    c56_point = [0] * len(c56_model.names)
    for seed in (2, 3):
        c56_point[c56_model.names.index(f"t_{seed}")] = 1
    check_bounds(c56_model, c56_point)
    c56_violations = check_rows(c56_model, c56_point)

    c75_model, _matrix, c75_objective, c75_hard = C75.build(limit)
    c75_point = [0] * len(c75_model.names)
    for seed in (2, 3):
        c75_point[c75_model.names.index(f"s_{seed}")] = 1
        c75_point[c75_model.names.index(f"f_{seed}")] = 1
    check_bounds(c75_model, c75_point)
    c75_violations = check_rows(c75_model, c75_point)

    c79_model, c79_objective, c79_hard, _ = C79.build(limit)
    c79_point = [0] * len(c79_model.names)
    for column, name in enumerate(c79_model.names):
        if name.startswith("u_") and name not in ("u_2", "u_3"):
            c79_point[column] = 1
    check_bounds(c79_model, c79_point)
    c79_violations = check_rows(c79_model, c79_point)

    expected_c56 = [["closure_5_2_3", 1]]
    expected_c75 = [["closure_5_2_3", 1], ["and_lower_5_0", 1]]
    expected_c79 = [["subadd_5_2_3", 1]]
    if c56_violations != expected_c56:
        raise RuntimeError(f"unexpected C56 violations: {c56_violations}")
    if c75_violations != expected_c75:
        raise RuntimeError(f"unexpected C75 violations: {c75_violations}")
    if c79_violations != expected_c79:
        raise RuntimeError(f"unexpected C79 violations: {c79_violations}")
    if not (len(c56_hard) == len(c75_hard) == len(c79_hard)):
        raise RuntimeError("hard-shape counts disagree")
    if dot(c56_objective, c56_point) != 0:
        raise RuntimeError("C56 probe objective is not zero")
    if dot(c75_objective, c75_point) != 0:
        raise RuntimeError("C75 probe objective is not zero")
    if dot(c79_objective, c79_point) != -len(c79_hard):
        raise RuntimeError("C79 probe objective mismatch")

    return {
        "limit": limit,
        "hard_shapes": len(c79_hard),
        "C56": {"objective": 0, "positive_row_violations": c56_violations},
        "C75": {"objective": 0, "positive_row_violations": c75_violations},
        "C79": {
            "objective": -len(c79_hard),
            "positive_row_violations": c79_violations,
        },
        "bounds_exact": True,
        "rows_exact": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [audit(limit) for limit in args.limits]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"schema_version": 1, "rows": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
