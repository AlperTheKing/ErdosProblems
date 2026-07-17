#!/usr/bin/env python3
"""Exact audits for the C75 image LP and its dual schema.

The optimizer is used only to recover integral primal witnesses for the four
tight cutoffs.  Stored duals, recovered primals, the non-TU minor, and the
cutoff-21 non-TDI certificate are all replayed with ``Fraction`` arithmetic.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, csr_matrix


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "C75_unconditional_image_lp.py"
SPEC = importlib.util.spec_from_file_location("c75_source_for_c76", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {SOURCE}")
C75 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C75
SPEC.loader.exec_module(C75)


@dataclass
class Model:
    builder: object
    matrix: csr_matrix
    objective: list[int]
    hard: list[int]


def build(limit: int) -> Model:
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
        if value in (2, 3):
            continue
        for pair_index, (left, right) in enumerate(pairs[value]):
            builder.inequality(
                {s[left]: 1, s[right]: 1, s[value]: -1},
                1,
                f"closure_{value}_{left}_{right}",
            )
            witness = builder.variable(f"w_{value}_{pair_index}")
            local.append(witness)
            builder.inequality(
                {witness: 1, s[left]: -1},
                0,
                f"and_left_{value}_{pair_index}",
            )
            builder.inequality(
                {witness: 1, s[right]: -1},
                0,
                f"and_right_{value}_{pair_index}",
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
            {f[value]: 1, s[value]: -1},
            0,
            f"image_subset_{value}",
        )

    boundaries: dict[int, int] = {}
    for parent in values:
        child = 2 * parent - 1
        if child > limit:
            continue
        boundary = builder.variable(f"q_{child}")
        boundaries[child] = boundary
        builder.inequality(
            {boundary: 1, f[parent]: 1},
            1,
            f"boundary_parent_{child}",
        )
        builder.inequality(
            {boundary: 1, f[child]: -1},
            0,
            f"boundary_child_{child}",
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
    return Model(builder, matrix, objective, hard)


def as_fraction(value: float | int) -> Fraction:
    return Fraction(str(value))


def columns(model: Model) -> list[dict[int, int]]:
    result: list[dict[int, int]] = [dict() for _ in model.builder.names]
    for row, column, coefficient in zip(
        model.builder.rows, model.builder.cols, model.builder.data
    ):
        integer = int(coefficient)
        if integer != coefficient:
            raise RuntimeError(f"nonintegral matrix coefficient {coefficient}")
        result[column][row] = result[column].get(row, 0) + integer
    return result


def verify_dual(
    model: Model,
    objective: list[int],
    inequality: list[Fraction],
    lower: list[Fraction],
    upper: list[Fraction],
) -> Fraction:
    if not all(value <= 0 for value in inequality):
        raise RuntimeError("positive <=-row multiplier")
    if not all(value >= 0 for value in lower):
        raise RuntimeError("negative lower-bound multiplier")
    if not all(value <= 0 for value in upper):
        raise RuntimeError("positive upper-bound multiplier")
    matrix_columns = columns(model)
    for column, expected in enumerate(objective):
        reconstructed = lower[column] + upper[column]
        reconstructed += sum(
            inequality[row] * coefficient
            for row, coefficient in matrix_columns[column].items()
        )
        if reconstructed != expected:
            name = model.builder.names[column]
            raise RuntimeError(
                f"stationarity failure at {name}: {reconstructed} != {expected}"
            )
    value = sum(
        multiplier * as_fraction(rhs)
        for multiplier, rhs in zip(inequality, model.builder.rhs)
    )
    value += sum(
        multiplier * as_fraction(bound)
        for multiplier, bound in zip(lower, model.builder.lower)
    )
    value += sum(
        multiplier * as_fraction(bound)
        for multiplier, bound in zip(upper, model.builder.upper)
    )
    return value


def verify_primal(model: Model, point: list[Fraction]) -> Fraction:
    if len(point) != len(model.builder.names):
        raise RuntimeError("wrong primal dimension")
    for name, value, lower, upper in zip(
        model.builder.names,
        point,
        model.builder.lower,
        model.builder.upper,
    ):
        if not as_fraction(lower) <= value <= as_fraction(upper):
            raise RuntimeError(f"bound failure at {name}: {value}")
    lhs = [Fraction(0) for _ in model.builder.rhs]
    for row, column, coefficient in zip(
        model.builder.rows, model.builder.cols, model.builder.data
    ):
        lhs[row] += int(coefficient) * point[column]
    for name, value, rhs in zip(model.builder.row_names, lhs, model.builder.rhs):
        if value > as_fraction(rhs):
            raise RuntimeError(f"row failure at {name}: {value} > {rhs}")
    return sum(coefficient * value for coefficient, value in zip(model.objective, point))


def named_vector(names: list[str], entries: dict[str, Fraction]) -> list[Fraction]:
    unknown = set(entries).difference(names)
    if unknown:
        raise RuntimeError(f"unknown names: {sorted(unknown)}")
    return [entries.get(name, Fraction(0)) for name in names]


def replay_stored(row: dict) -> dict:
    limit = int(row["limit"])
    model = build(limit)
    builder = model.builder
    inequality_entries = {
        entry["name"]: as_fraction(entry["marginal"])
        for entry in row["dual"]["inequalities"]
    }
    lower_entries = {
        entry["name"]: as_fraction(entry["marginal"])
        for entry in row["dual"]["lower_bounds"]
    }
    upper_entries = {
        entry["name"]: as_fraction(entry["marginal"])
        for entry in row["dual"]["upper_bounds"]
    }
    inequality = named_vector(builder.row_names, inequality_entries)
    lower = named_vector(builder.names, lower_entries)
    upper = named_vector(builder.names, upper_entries)
    dual_value = verify_dual(model, model.objective, inequality, lower, upper)

    result = linprog(
        np.asarray(model.objective, dtype=float),
        A_ub=model.matrix,
        b_ub=np.asarray(builder.rhs, dtype=float),
        bounds=list(zip(builder.lower, builder.upper)),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    primal = [Fraction(round(float(value))) for value in result.x]
    if any(abs(float(exact) - float(value)) > 1e-8 for exact, value in zip(primal, result.x)):
        raise RuntimeError(f"tight-cutoff primal is fractional at {limit}")
    primal_value = verify_primal(model, primal)
    if primal_value != dual_value or dual_value != len(model.hard):
        raise RuntimeError(
            f"duality failure at {limit}: primal={primal_value}, "
            f"dual={dual_value}, hard={len(model.hard)}"
        )
    all_multipliers = inequality + lower + upper
    return {
        "limit": limit,
        "hard_shapes": len(model.hard),
        "exact_primal_objective": [primal_value.numerator, primal_value.denominator],
        "exact_dual_objective": [dual_value.numerator, dual_value.denominator],
        "nonzero_inequality_multipliers": sum(value != 0 for value in inequality),
        "nonzero_lower_multipliers": sum(value != 0 for value in lower),
        "nonzero_upper_multipliers": sum(value != 0 for value in upper),
        "maximum_multiplier_denominator": max(
            value.denominator for value in all_multipliers
        ),
        "primal_feasibility_exact": True,
        "dual_stationarity_exact": True,
    }


def determinant(matrix: list[list[int]]) -> int:
    work = [row[:] for row in matrix]
    size = len(work)
    sign = 1
    previous = 1
    for pivot_index in range(size - 1):
        if work[pivot_index][pivot_index] == 0:
            swap = next(
                (
                    row
                    for row in range(pivot_index + 1, size)
                    if work[row][pivot_index] != 0
                ),
                None,
            )
            if swap is None:
                return 0
            work[pivot_index], work[swap] = work[swap], work[pivot_index]
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for column in range(pivot_index + 1, size):
                numerator = (
                    pivot * work[row][column]
                    - work[row][pivot_index] * work[pivot_index][column]
                )
                if numerator % previous:
                    raise RuntimeError("Bareiss division was not exact")
                work[row][column] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def tdi_counterexample() -> dict:
    model = build(21)
    builder = model.builder
    objective = [0] * len(builder.names)
    for name, coefficient in {"s_11": 2, "q_11": -2, "q_21": -1}.items():
        objective[builder.names.index(name)] = coefficient

    one = {
        "s_2",
        "s_3",
        "s_5",
        "s_9",
        "s_14",
        "s_17",
        "f_2",
        "f_3",
        "f_5",
        "f_9",
        "f_14",
        "f_17",
        "w_5_0",
        "w_9_0",
        "w_14_0",
        "w_17_0",
    }
    half = {
        "s_6",
        "s_11",
        "s_21",
        "f_11",
        "f_21",
        "w_11_0",
        "w_17_1",
        "w_21_0",
        "q_11",
        "q_21",
    }
    primal_entries = {name: Fraction(1) for name in one}
    primal_entries.update({name: Fraction(1, 2) for name in half})
    primal = named_vector(builder.names, primal_entries)
    verify_primal(model, primal)
    primal_value = sum(
        coefficient * value for coefficient, value in zip(objective, primal)
    )

    inequality_entries = {
        "closure_11_2_6": Fraction(-3, 2),
        "and_right_11_0": Fraction(-3, 2),
        "support_upper_11": Fraction(-3, 2),
        "and_right_21_0": Fraction(-1, 2),
        "support_upper_21": Fraction(-1, 2),
        "boundary_child_11": Fraction(-2),
        "boundary_parent_21": Fraction(-1, 2),
        "boundary_child_21": Fraction(-1, 2),
    }
    lower_entries = {"s_2": Fraction(3, 2)}
    inequality = named_vector(builder.row_names, inequality_entries)
    lower = named_vector(builder.names, lower_entries)
    upper = [Fraction(0) for _ in builder.names]
    dual_value = verify_dual(model, objective, inequality, lower, upper)
    if primal_value != Fraction(-1, 2) or dual_value != primal_value:
        raise RuntimeError(
            f"cutoff-21 certificate mismatch: {primal_value}, {dual_value}"
        )

    row_names = [
        "closure_11_2_6",
        "and_right_11_0",
        "support_upper_11",
        "and_right_21_0",
        "support_upper_21",
        "boundary_parent_21",
        "boundary_child_21",
    ]
    column_names = [
        "s_6",
        "s_11",
        "w_11_0",
        "f_11",
        "w_21_0",
        "f_21",
        "q_21",
    ]
    row_indices = [builder.row_names.index(name) for name in row_names]
    column_indices = [builder.names.index(name) for name in column_names]
    minor = [
        [int(value) for value in row]
        for row in model.matrix[row_indices, :][:, column_indices].toarray()
    ]
    minor_determinant = determinant(minor)
    if minor_determinant != 2:
        raise RuntimeError(f"unexpected minor determinant {minor_determinant}")

    integral_cases = []
    for source_6, source_11 in ((0, 0), (0, 1), (1, 1)):
        q_11 = source_6
        q_21 = (1 - source_6) * source_11
        value = 2 * source_11 - 2 * q_11 - q_21
        integral_cases.append(
            {
                "s_6": source_6,
                "s_11": source_11,
                "objective": value,
            }
        )
    if min(case["objective"] for case in integral_cases) != 0:
        raise RuntimeError("unexpected integer optimum")
    return {
        "limit": 21,
        "objective": {"s_11": 2, "q_11": -2, "q_21": -1},
        "exact_lp_optimum": [primal_value.numerator, primal_value.denominator],
        "exact_integer_optimum": [0, 1],
        "integral_cases": integral_cases,
        "fractional_primal_nonzero": {
            name: [value.numerator, value.denominator]
            for name, value in primal_entries.items()
        },
        "dual_inequalities": {
            name: [value.numerator, value.denominator]
            for name, value in inequality_entries.items()
        },
        "dual_lower_bounds": {
            name: [value.numerator, value.denominator]
            for name, value in lower_entries.items()
        },
        "non_tu_minor": {
            "rows": row_names,
            "columns": column_names,
            "matrix": minor,
            "determinant": minor_determinant,
        },
        "primal_feasibility_exact": True,
        "dual_stationarity_exact": True,
    }


def projection_audit(limit: int) -> dict:
    values = [value for value in range(2, limit + 1) if C75.allowed(value)]
    model = build(limit)
    builder = model.builder
    row_terms: list[dict[int, int]] = [dict() for _ in builder.row_names]
    for row, column, coefficient in zip(
        builder.rows, builder.cols, builder.data
    ):
        row_terms[row][column] = row_terms[row].get(column, 0) + int(coefficient)

    def add_row(total: dict[int, int], name: str) -> int:
        row = builder.row_names.index(name)
        for column, coefficient in row_terms[row].items():
            total[column] = total.get(column, 0) + coefficient
        return int(builder.rhs[row])

    relation_count = 0
    seed_relation_count = 0
    for value in values:
        for pair_index, (left, right) in enumerate(C75.admissible_pairs(value)):
            relation_count += 1
            total: dict[int, int] = {}
            rhs = 0
            for factor in (left, right):
                if factor in (2, 3):
                    seed_relation_count += 1
                else:
                    rhs += add_row(total, f"image_subset_{factor}")
            rhs += add_row(total, f"and_lower_{value}_{pair_index}")
            rhs += add_row(total, f"support_lower_{value}_{pair_index}")
            for seed in (2, 3):
                source = builder.names.index(f"s_{seed}")
                image = builder.names.index(f"f_{seed}")
                total[image] = total.get(image, 0) + total.pop(source, 0)
            total = {column: coefficient for column, coefficient in total.items() if coefficient}
            expected = {
                builder.names.index(f"f_{left}"): 1,
                builder.names.index(f"f_{right}"): 1,
                builder.names.index(f"f_{value}"): -1,
            }
            expected = {
                column: coefficient
                for column, coefficient in expected.items()
                if coefficient
            }
            if rhs != 1 or total != expected:
                raise RuntimeError(
                    f"projection identity failed at {value}=({left})({right})-1"
                )
    splitless = [
        value
        for value in values
        if value not in (2, 3) and not C75.admissible_pairs(value)
    ]
    for value in splitless:
        column = builder.names.index(f"f_{value}")
        if builder.lower[column] != 0 or builder.upper[column] != 0:
            raise RuntimeError(f"splitless image value not fixed to zero: {value}")
    return {
        "limit": limit,
        "image_closure_relations": relation_count,
        "seed_equalities_used": seed_relation_count,
        "identity": (
            "(f_a-s_a)+(f_b-s_b)+"
            "(-w+s_a+s_b)+(w-f_n) = f_a+f_b-f_n <= 1"
        ),
        "boundary_row": "f_(2m-1)-f_m-q_(2m-1) <= 0",
        "splitless_image_values_are_fixed_zero": True,
        "algebra_exact": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--duals",
        default=str(HERE / "C75_unconditional_image_lp_duals.json"),
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--projection-limit", type=int, default=362)
    args = parser.parse_args()

    with open(args.duals, "r", encoding="utf-8") as handle:
        stored = json.load(handle)
    tight = [replay_stored(row) for row in stored["rows"]]
    output = {
        "schema_version": 1,
        "tight_cutoff_dual_replays": tight,
        "projection_audit": projection_audit(args.projection_limit),
        "tdi_counterexample": tdi_counterexample(),
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
