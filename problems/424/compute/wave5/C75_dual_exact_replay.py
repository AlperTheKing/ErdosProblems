#!/usr/bin/env python3
"""Exact rational replay of finite C75 LP dual certificates.

SciPy/HiGHS is used only to discover a dual.  Every returned multiplier is
rationally reconstructed and then checked against the integer matrix using
``fractions.Fraction``.  Acceptance is therefore exact for the finite rows.
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
SOURCE = HERE / "C75_unconditional_image_lp.py"
SPEC = importlib.util.spec_from_file_location("c75_source", SOURCE)
assert SPEC and SPEC.loader
C75 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C75
SPEC.loader.exec_module(C75)


def build(limit: int):
    values = [value for value in range(2, limit + 1) if C75.allowed(value)]
    pairs = {value: C75.admissible_pairs(value) for value in values}
    hard = [value for value in values if C75.hard_shape(value, pairs[value])]
    builder = C75.Builder.empty()
    s = {value: builder.variable(f"s_{value}") for value in values}
    f = {value: builder.variable(f"f_{value}") for value in values}
    for seed in (2, 3):
        builder.lower[s[seed]] = builder.upper[s[seed]] = 1.0
        builder.lower[f[seed]] = builder.upper[f[seed]] = 1.0

    for value in values:
        local: list[int] = []
        if value not in (2, 3):
            for pair_index, (left, right) in enumerate(pairs[value]):
                builder.inequality(
                    {s[left]: 1, s[right]: 1, s[value]: -1},
                    1,
                    f"closure_{value}_{left}_{right}",
                )
                witness = builder.variable(f"w_{value}_{pair_index}")
                local.append(witness)
                builder.inequality(
                    {witness: 1, s[left]: -1}, 0, f"and_left_{value}_{pair_index}"
                )
                builder.inequality(
                    {witness: 1, s[right]: -1}, 0, f"and_right_{value}_{pair_index}"
                )
                builder.inequality(
                    {witness: -1, s[left]: 1, s[right]: 1},
                    1,
                    f"and_lower_{value}_{pair_index}",
                )
                builder.inequality(
                    {witness: 1, f[value]: -1},
                    0,
                    f"support_lower_{value}_{pair_index}",
                )
            if local:
                terms = {f[value]: 1}
                for witness in local:
                    terms[witness] = terms.get(witness, 0) - 1
                builder.inequality(terms, 0, f"support_upper_{value}")
            else:
                builder.lower[f[value]] = builder.upper[f[value]] = 0.0
            builder.inequality(
                {f[value]: 1, s[value]: -1}, 0, f"image_subset_{value}"
            )

    boundaries: dict[int, int] = {}
    for parent in values:
        child = 2 * parent - 1
        if child > limit:
            continue
        boundary = builder.variable(f"q_{child}")
        boundaries[child] = boundary
        builder.inequality(
            {boundary: 1, f[parent]: 1}, 1, f"boundary_parent_{child}"
        )
        builder.inequality(
            {boundary: 1, f[child]: -1}, 0, f"boundary_child_{child}"
        )
        builder.inequality(
            {boundary: -1, f[parent]: -1, f[child]: 1},
            0,
            f"boundary_lower_{child}",
        )

    objective = [0] * len(builder.names)
    for value in hard:
        objective[f[value]] += 1
    for boundary in boundaries.values():
        objective[boundary] += 1
    matrix = coo_matrix(
        (builder.data, (builder.rows, builder.cols)),
        shape=(len(builder.rhs), len(builder.names)),
    ).tocsr()
    return builder, matrix, objective, hard


def rational(value: float, denominator: int) -> Fraction:
    answer = Fraction(value).limit_denominator(denominator)
    if abs(float(answer) - value) > 1e-8:
        raise AssertionError((value, answer))
    return answer


def replay(limit: int, denominator: int) -> dict:
    builder, matrix, objective, hard = build(limit)
    result = linprog(
        np.asarray(objective, dtype=float),
        A_ub=matrix,
        b_ub=np.asarray(builder.rhs, dtype=float),
        bounds=list(zip(builder.lower, builder.upper)),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    inequality = [rational(value, denominator) for value in result.ineqlin.marginals]
    lower = [rational(value, denominator) for value in result.lower.marginals]
    upper = [rational(value, denominator) for value in result.upper.marginals]
    assert all(value <= 0 for value in inequality)
    assert all(value >= 0 for value in lower)
    assert all(value <= 0 for value in upper)

    columns: list[dict[int, int]] = [dict() for _ in builder.names]
    for row, column, coefficient in zip(builder.rows, builder.cols, builder.data):
        columns[column][row] = columns[column].get(row, 0) + int(coefficient)
    for column, expected in enumerate(objective):
        reconstructed = lower[column] + upper[column]
        reconstructed += sum(
            inequality[row] * coefficient
            for row, coefficient in columns[column].items()
        )
        if reconstructed != expected:
            raise AssertionError(
                (builder.names[column], reconstructed, expected)
            )

    dual_objective = sum(
        multiplier * Fraction(rhs)
        for multiplier, rhs in zip(inequality, builder.rhs)
    )
    dual_objective += sum(
        multiplier * Fraction(bound)
        for multiplier, bound in zip(lower, builder.lower)
    )
    dual_objective += sum(
        multiplier * Fraction(bound)
        for multiplier, bound in zip(upper, builder.upper)
    )
    assert dual_objective == rational(float(result.fun), denominator)
    return {
        "limit": limit,
        "hard_shapes": len(hard),
        "exact_dual_objective": [
            dual_objective.numerator,
            dual_objective.denominator,
        ],
        "exact_maximum_relaxed_H_minus_Q": [
            len(hard) * dual_objective.denominator - dual_objective.numerator,
            dual_objective.denominator,
        ],
        "nonzero_inequality_multipliers": sum(value != 0 for value in inequality),
        "nonzero_lower_multipliers": sum(value != 0 for value in lower),
        "nonzero_upper_multipliers": sum(value != 0 for value in upper),
        "maximum_denominator": max(
            [value.denominator for value in inequality + lower + upper]
        ),
        "stationarity_exact": True,
        "dual_signs_exact": True,
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
