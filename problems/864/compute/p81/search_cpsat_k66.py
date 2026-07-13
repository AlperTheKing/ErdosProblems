#!/usr/bin/env python3
"""Search directly for an odd positive-defect Sidon ruler with outer K_6,6."""

from __future__ import annotations

import argparse
import itertools
import json
import time
from collections import Counter
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p81/cpsat_k66_result.json"
P75_B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505,
    519, 631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
]


def verify(values: list[int], h: int, b: int, left: list[int], right: list[int]) -> dict:
    p = len(values)
    sums = Counter(
        values[i] + values[j]
        for i in range(p)
        for j in range(i, p)
    )
    differences = Counter(
        values[j] - values[i]
        for i in range(p)
        for j in range(i + 1, p)
    )
    if max(values) != h - 1:
        raise AssertionError("endpoint normalization")
    if len(sums) != p * (p + 1) // 2 or max(sums.values()) != 1:
        raise AssertionError("integer Sidon sums")
    if len(differences) != p * (p - 1) // 2 or max(differences.values()) != 1:
        raise AssertionError("integer Sidon differences")
    shifted_sums = {value + b for value in sums}
    if not set(differences).isdisjoint(shifted_sums):
        raise AssertionError("literal hole support form")
    direct_hole = not any(
        x + y + z + b == w
        for x in values
        for y in values
        for z in values
        for w in values
    )
    if not direct_hole:
        raise AssertionError("literal hole direct form")
    delta = (3 * p * p - p + 2) // 2 - h
    if delta <= 0:
        raise AssertionError("positive defect")

    difference_pair = {}
    for i, low in enumerate(values):
        for high in values[i + 1 :]:
            difference_pair[high - low] = (low, high)
    edges = []
    for outer_low in left:
        for outer_high in right:
            inner = difference_pair.get(h - (outer_high - outer_low))
            if inner is None:
                raise AssertionError(("missing inner label", outer_low, outer_high))
            inner_low, inner_high = inner
            if not (outer_low <= inner_low < inner_high <= outer_high):
                raise AssertionError(("non-nested label", outer_low, outer_high, inner))
            low_sum = outer_low + inner_low
            high_sum = inner_high + outer_high
            if low_sum + h != high_sum:
                raise AssertionError("fold equation")
            edges.append(
                {
                    "outer_edge": [outer_low, outer_high],
                    "inner_edge": [inner_low, inner_high],
                    "low_sum": low_sum,
                    "high_sum": high_sum,
                }
            )
    return {
        "p": p,
        "h": h,
        "b": b,
        "delta": delta,
        "sum_count": len(sums),
        "difference_count": len(differences),
        "literal_hole_direct": direct_hole,
        "left": left,
        "right": right,
        "edges": edges,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=30)
    parser.add_argument("--min-width", type=int, default=435)
    parser.add_argument("--mode", choices=("odd", "direct"), default="odd")
    parser.add_argument("--hint-p75", action="store_true")
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.p < 24:
        raise ValueError("the fixed six-low/six-high model needs room for inner labels")

    p = args.p
    baseline = (3 * p * p - p + 2) // 2
    max_width = (
        (baseline - 3) // 2 if args.mode == "odd" else baseline - 2
    )
    if args.min_width > max_width:
        raise ValueError(("empty width range", args.min_width, max_width))

    model = cp_model.CpModel()
    marks = [model.new_int_var(0, max_width, f"x_{i}") for i in range(p)]
    model.add(marks[-1] >= args.min_width)
    for i in range(p - 1):
        model.add(marks[i + 1] >= marks[i] + 1)

    differences = []
    for i in range(p):
        for j in range(i + 1, p):
            difference = model.new_int_var(1, max_width, f"difference_{i}_{j}")
            model.add(difference == marks[j] - marks[i])
            differences.append(difference)
    model.add_all_different(differences)
    if args.mode == "direct":
        for difference in differences:
            for i in range(p):
                for j in range(i, p):
                    model.add(difference != marks[i] + marks[j] + 1)

    left_indices = list(range(6))
    right_indices = list(range(p - 6, p))
    model.add(2 * marks[left_indices[-1]] < marks[-1])
    model.add(2 * marks[right_indices[0]] >= marks[-1])

    inner_index_rows = []
    inner_differences = []
    for i in left_indices:
        row = []
        for j in right_indices:
            c_index = model.new_int_var(i, j - 1, f"c_index_{i}_{j}")
            u_index = model.new_int_var(i + 1, j, f"u_index_{i}_{j}")
            model.add(c_index < u_index)
            c_value = model.new_int_var(0, max_width, f"c_value_{i}_{j}")
            u_value = model.new_int_var(0, max_width, f"u_value_{i}_{j}")
            model.add_element(c_index, marks, c_value)
            model.add_element(u_index, marks, u_value)
            model.add(marks[i] + c_value + marks[-1] + 1 == u_value + marks[j])
            inner_difference = model.new_int_var(
                1, max_width, f"inner_difference_{i}_{j}"
            )
            model.add(inner_difference == u_value - c_value)
            inner_differences.append(inner_difference)
            row.append([c_index, u_index])
        inner_index_rows.append(row)
    model.add_all_different(inner_differences)

    hinted_inner_pairs = 0
    if args.hint_p75:
        if p != len(P75_B) or args.mode != "odd":
            raise ValueError("--hint-p75 requires --p 26 --mode odd")
        scaled_hint = [(value - 1) // 2 for value in P75_B]
        for variable, value in zip(marks, scaled_hint):
            model.add_hint(variable, value)
        hint_difference_pairs = {
            P75_B[j] - P75_B[i]: (i, j)
            for i in range(p)
            for j in range(i + 1, p)
        }
        for row_offset, i in enumerate(left_indices):
            for column_offset, j in enumerate(right_indices):
                inner_length = 988 - (P75_B[j] - P75_B[i])
                inner_pair = hint_difference_pairs.get(inner_length)
                if inner_pair is None:
                    continue
                if not (i <= inner_pair[0] < inner_pair[1] <= j):
                    continue
                pair_variables = inner_index_rows[row_offset][column_offset]
                model.add_hint(pair_variables[0], inner_pair[0])
                model.add_hint(pair_variables[1], inner_pair[1])
                hinted_inner_pairs += 1

    validation_error = model.validate()
    if validation_error:
        raise RuntimeError(f"CP-SAT model validation failed: {validation_error}")

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = 86481
    started = time.perf_counter()
    status = solver.solve(model)
    elapsed = time.perf_counter() - started
    status_name = solver.status_name(status)

    output: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "exact integer CP-SAT",
        "model": {
            "p": p,
            "mode": args.mode,
            "scaled_width_min": args.min_width,
            "scaled_width_max": max_width,
            "left_indices": left_indices,
            "right_indices": right_indices,
            "all_positive_differences_distinct": True,
            "all_actual_marks_odd": args.mode == "odd",
            "literal_hole_encoding": (
                "parity" if args.mode == "odd" else "all difference/sum disequalities"
            ),
            "explicit_inner_labels": 36,
            "P75_hint": args.hint_p75,
            "P75_hinted_inner_pairs": hinted_inner_pairs,
        },
        "parameters": {
            "seconds": args.seconds,
            "workers": args.workers,
            "random_seed": 86481,
        },
        "status": status_name,
        "elapsed_seconds": elapsed,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "wall_time": solver.wall_time,
        "witness": None,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        scaled = [solver.value(mark) for mark in marks]
        if args.mode == "odd":
            actual = [2 * value + 1 for value in scaled]
            h = 2 * scaled[-1] + 2
        else:
            actual = scaled
            h = scaled[-1] + 1
        left = [actual[index] for index in left_indices]
        right = [actual[index] for index in right_indices]
        certificate = verify(actual, h, 1, left, right)
        chosen_indices = [
            [
                [solver.value(pair[0]), solver.value(pair[1])]
                for pair in row
            ]
            for row in inner_index_rows
        ]
        output["witness"] = {
            "scaled_marks": scaled,
            "B": actual,
            "inner_indices": chosen_indices,
            **certificate,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
