#!/usr/bin/env python3
"""Exact rational replay of finite C79 LP dual certificates."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "C79_fractional_boundary.py"
SPEC = importlib.util.spec_from_file_location("c79_source", SOURCE)
if not SPEC or not SPEC.loader:
    raise RuntimeError(f"cannot load {SOURCE}")
C79 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C79
SPEC.loader.exec_module(C79)


def rational(value: float, denominator: int) -> Fraction:
    answer = Fraction(value).limit_denominator(denominator)
    if abs(float(answer) - value) > 1e-8:
        raise RuntimeError(f"rational reconstruction failed: {value} -> {answer}")
    return answer


def replay(limit: int, denominator: int) -> dict:
    model, objective, hard, splitless = C79.build(limit)
    matrix = coo_matrix(
        (model.data, (model.rows, model.cols)),
        shape=(len(model.rhs), len(model.names)),
    ).tocsr()
    result = linprog(
        np.asarray(objective, dtype=float),
        A_ub=matrix,
        b_ub=np.asarray(model.rhs, dtype=float),
        bounds=list(zip(model.lower, model.upper)),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    inequality = [rational(value, denominator) for value in result.ineqlin.marginals]
    lower = [rational(value, denominator) for value in result.lower.marginals]
    upper = [rational(value, denominator) for value in result.upper.marginals]
    if any(value > 0 for value in inequality):
        raise RuntimeError("positive <=-row dual multiplier")
    if any(value < 0 for value in lower):
        raise RuntimeError("negative lower-bound dual multiplier")
    if any(value > 0 for value in upper):
        raise RuntimeError("positive upper-bound dual multiplier")

    columns: list[dict[int, int]] = [dict() for _ in model.names]
    for row, column, coefficient in zip(model.rows, model.cols, model.data):
        columns[column][row] = columns[column].get(row, 0) + coefficient
    for column, expected in enumerate(objective):
        reconstructed = lower[column] + upper[column]
        reconstructed += sum(
            inequality[row] * coefficient
            for row, coefficient in columns[column].items()
        )
        if reconstructed != expected:
            raise RuntimeError(
                f"stationarity failed at {model.names[column]}: "
                f"{reconstructed} != {expected}"
            )

    dual_objective = sum(
        multiplier * Fraction(rhs)
        for multiplier, rhs in zip(inequality, model.rhs)
    )
    dual_objective += sum(
        multiplier * Fraction(str(bound))
        for multiplier, bound in zip(lower, model.lower)
    )
    dual_objective += sum(
        multiplier * Fraction(str(bound))
        for multiplier, bound in zip(upper, model.upper)
        if bound is not None
    )
    if any(
        multiplier != 0
        for multiplier, bound in zip(upper, model.upper)
        if bound is None
    ):
        raise RuntimeError("nonzero multiplier on an absent upper bound")
    primal_objective = rational(float(result.fun), denominator)
    if dual_objective != primal_objective:
        raise RuntimeError(
            f"primal-dual objective mismatch: {primal_objective} != "
            f"{dual_objective}"
        )
    return {
        "limit": limit,
        "hard_shapes": len(hard),
        "splitless_values": len(splitless),
        "exact_minimum_boundary_minus_hard": [
            dual_objective.numerator,
            dual_objective.denominator,
        ],
        "exact_maximum_fractional_hard_minus_boundary": [
            -dual_objective.numerator,
            dual_objective.denominator,
        ],
        "nonzero_inequality_multipliers": sum(value != 0 for value in inequality),
        "nonzero_lower_multipliers": sum(value != 0 for value in lower),
        "nonzero_upper_multipliers": sum(value != 0 for value in upper),
        "maximum_denominator": max(
            value.denominator for value in inequality + lower + upper
        ),
        "stationarity_exact": True,
        "dual_signs_exact": True,
        "objective_exact": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--max-denominator", type=int, default=1_000_000)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = [replay(limit, args.max_denominator) for limit in args.limits]
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 1, "rows": rows}, handle, indent=2)
        handle.write("\n")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
