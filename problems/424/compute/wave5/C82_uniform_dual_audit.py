#!/usr/bin/env python3
"""Exact audit of selected coefficient minima in the C79 dual.

The floating-point solve is only a discovery step.  Both sides of the
secondary LP optimum are reconstructed as ``Fraction`` values and checked
against the integer matrix.  The secondary LP minimizes one nonnegative
proof multiplier among all C79 dual certificates with objective at least 0.
"""

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
SPEC = importlib.util.spec_from_file_location("c82_c79", SOURCE)
if not SPEC or not SPEC.loader:
    raise RuntimeError("cannot load C79_fractional_boundary.py")
C79 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C79
SPEC.loader.exec_module(C79)


def rational(value: float, max_denominator: int) -> Fraction:
    result = Fraction(value).limit_denominator(max_denominator)
    if abs(float(result) - value) > 1e-8:
        raise RuntimeError(f"rational reconstruction failed: {value} -> {result}")
    return result


def audit(limit: int, row_name: str, max_denominator: int) -> dict:
    model, objective, hard, _splitless = C79.build(limit)
    try:
        target_row = model.row_names.index(row_name)
    except ValueError as error:
        raise RuntimeError(f"row {row_name!r} absent at cutoff {limit}") from error

    row_count = len(model.rhs)
    column_count = len(model.names)
    finite_upper = [index for index, bound in enumerate(model.upper) if bound is not None]
    upper_slot = {column: slot for slot, column in enumerate(finite_upper)}

    # z=(alpha, lambda, nu)>=0, where the original SciPy-sign multipliers are
    # y=-alpha for <= rows, lower=lambda, and upper=-nu.
    alpha_offset = 0
    lower_offset = row_count
    upper_offset = row_count + column_count
    variable_count = upper_offset + len(finite_upper)

    eq_rows: list[int] = []
    eq_cols: list[int] = []
    eq_data: list[int] = []
    for row, column, coefficient in zip(model.rows, model.cols, model.data):
        eq_rows.append(column)
        eq_cols.append(alpha_offset + row)
        eq_data.append(-int(coefficient))
    for column in range(column_count):
        eq_rows.append(column)
        eq_cols.append(lower_offset + column)
        eq_data.append(1)
        if column in upper_slot:
            eq_rows.append(column)
            eq_cols.append(upper_offset + upper_slot[column])
            eq_data.append(-1)
    stationarity = coo_matrix(
        (eq_data, (eq_rows, eq_cols)),
        shape=(column_count, variable_count),
    ).tocsr()

    # A C79 certificate must have dual objective
    #   sum(lo*lambda)-sum(hi*nu) >= 0.
    dual_value = np.zeros(variable_count, dtype=float)
    for column, bound in enumerate(model.lower):
        dual_value[lower_offset + column] = float(bound)
    for column, slot in upper_slot.items():
        dual_value[upper_offset + slot] = -float(model.upper[column])

    secondary_objective = np.zeros(variable_count, dtype=float)
    secondary_objective[alpha_offset + target_row] = 1.0
    result = linprog(
        secondary_objective,
        A_ub=coo_matrix(-dual_value.reshape(1, -1)).tocsr(),
        b_ub=np.asarray([0.0]),
        A_eq=stationarity,
        b_eq=np.asarray(objective, dtype=float),
        bounds=[(0.0, None)] * variable_count,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    primal = [rational(float(value), max_denominator) for value in result.x]
    equality_dual = [
        rational(float(value), max_denominator) for value in result.eqlin.marginals
    ]
    inequality_dual = rational(float(result.ineqlin.marginals[0]), max_denominator)
    lower_dual = [
        rational(float(value), max_denominator) for value in result.lower.marginals
    ]

    if any(value < 0 for value in primal):
        raise RuntimeError("negative secondary-primal variable")
    if inequality_dual > 0:
        raise RuntimeError("positive <=-row secondary-dual multiplier")
    if any(value < 0 for value in lower_dual):
        raise RuntimeError("negative secondary lower-bound multiplier")

    # Exact secondary-primal stationarity and objective floor.
    exact_columns: list[dict[int, int]] = [dict() for _ in range(variable_count)]
    for row, column, coefficient in zip(eq_rows, eq_cols, eq_data):
        exact_columns[column][row] = exact_columns[column].get(row, 0) + coefficient
    reconstructed_stationarity = [Fraction(0) for _ in range(column_count)]
    for row, column, coefficient in zip(eq_rows, eq_cols, eq_data):
        reconstructed_stationarity[row] += Fraction(coefficient) * primal[column]
    if reconstructed_stationarity != [Fraction(value) for value in objective]:
        raise RuntimeError("secondary primal fails exact C79 stationarity")
    exact_dual_value = sum(
        Fraction(str(value)) * primal[index]
        for index, value in enumerate(dual_value)
    )
    if exact_dual_value < 0:
        raise RuntimeError("secondary primal has negative C79 dual objective")

    # Exact secondary-dual stationarity.  The sole <= row is -g*z<=0.
    for column in range(variable_count):
        reconstructed = lower_dual[column]
        reconstructed += sum(
            Fraction(coefficient) * equality_dual[row]
            for row, coefficient in exact_columns[column].items()
        )
        reconstructed += Fraction(str(-dual_value[column])) * inequality_dual
        expected = Fraction(1 if column == alpha_offset + target_row else 0)
        if reconstructed != expected:
            raise RuntimeError(
                f"secondary dual stationarity failed at z_{column}: "
                f"{reconstructed} != {expected}"
            )
    exact_secondary_primal = primal[alpha_offset + target_row]
    exact_secondary_dual = sum(
        Fraction(value) * equality_dual[row]
        for row, value in enumerate(objective)
    )
    if exact_secondary_primal != exact_secondary_dual:
        raise RuntimeError(
            f"secondary objective mismatch: {exact_secondary_primal} != "
            f"{exact_secondary_dual}"
        )

    return {
        "limit": limit,
        "hard_shapes": len(hard),
        "target_row": row_name,
        "exact_minimum_multiplier": [
            exact_secondary_primal.numerator,
            exact_secondary_primal.denominator,
        ],
        "certificate_dual_objective": [
            exact_dual_value.numerator,
            exact_dual_value.denominator,
        ],
        "maximum_denominator": max(
            value.denominator
            for value in primal + equality_dual + [inequality_dual] + lower_dual
        ),
        "secondary_primal_exact": True,
        "secondary_dual_exact": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--row", default="subadd_5_2_3")
    parser.add_argument("--max-denominator", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = [audit(limit, args.row, args.max_denominator) for limit in args.limits]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"schema_version": 1, "rows": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
