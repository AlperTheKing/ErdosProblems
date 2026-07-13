#!/usr/bin/env python3
"""Maximize a six-by-six outer-fold rectangle near the P75 ruler."""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "problems/864/compute/p81/cpsat_p75_rectangle_optimization.json"
P75_B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505,
    519, 631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
]


def exact_rectangle(values: list[int], h: int) -> tuple[list[dict], list[dict]]:
    pairs = {}
    for i, low in enumerate(values):
        for high in values[i + 1 :]:
            difference = high - low
            if difference in pairs:
                raise AssertionError("non-Sidon output")
            pairs[difference] = (low, high)
    edges = []
    missing = []
    for outer_low in values[:6]:
        for outer_high in values[-6:]:
            target = h - (outer_high - outer_low)
            inner = pairs.get(target)
            if inner is None or not (outer_low <= inner[0] < inner[1] <= outer_high):
                missing.append(
                    {
                        "outer_edge": [outer_low, outer_high],
                        "target_inner_difference": target,
                        "represented_pair": None if inner is None else list(inner),
                    }
                )
                continue
            edges.append(
                {
                    "outer_edge": [outer_low, outer_high],
                    "inner_edge": list(inner),
                    "low_sum": outer_low + inner[0],
                    "high_sum": inner[1] + outer_high,
                }
            )
    return edges, missing


def verify(values: list[int], h: int, edges: list[dict]) -> dict:
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
    assert values[-1] == h - 1
    assert len(sums) == p * (p + 1) // 2 and max(sums.values()) == 1
    assert len(differences) == p * (p - 1) // 2 and max(differences.values()) == 1
    assert set(differences).isdisjoint({total + 1 for total in sums})
    delta = (3 * p * p - p + 2) // 2 - h
    assert delta > 0
    for edge in edges:
        assert edge["low_sum"] + h == edge["high_sum"]
    return {
        "p": p,
        "h": h,
        "b": 1,
        "delta": delta,
        "sum_count": len(sums),
        "difference_count": len(differences),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    p = 26
    min_width = 325
    max_width = 499
    model = cp_model.CpModel()
    marks = [model.new_int_var(0, max_width, f"x_{i}") for i in range(p)]
    model.add(marks[-1] >= min_width)
    for i in range(p - 1):
        model.add(marks[i + 1] >= marks[i] + 1)

    differences = []
    for i in range(p):
        for j in range(i + 1, p):
            difference = model.new_int_var(1, max_width, f"difference_{i}_{j}")
            model.add(difference == marks[j] - marks[i])
            differences.append(difference)
    model.add_all_different(differences)

    left_indices = list(range(6))
    right_indices = list(range(20, 26))
    model.add(2 * marks[5] < marks[-1])
    model.add(2 * marks[20] >= marks[-1])

    edge_variables = []
    index_variables = {}
    for i in left_indices:
        for j in right_indices:
            edge = model.new_bool_var(f"edge_{i}_{j}")
            c_index = model.new_int_var(i, j - 1, f"c_index_{i}_{j}")
            u_index = model.new_int_var(i + 1, j, f"u_index_{i}_{j}")
            model.add(c_index < u_index)
            c_value = model.new_int_var(0, max_width, f"c_value_{i}_{j}")
            u_value = model.new_int_var(0, max_width, f"u_value_{i}_{j}")
            model.add_element(c_index, marks, c_value)
            model.add_element(u_index, marks, u_value)
            model.add(
                marks[i] + c_value + marks[-1] + 1 == u_value + marks[j]
            ).only_enforce_if(edge)
            edge_variables.append(edge)
            index_variables[(i, j)] = (c_index, u_index, edge)
    model.add(sum(edge_variables) >= 30)
    model.maximize(sum(edge_variables))

    scaled_hint = [(value - 1) // 2 for value in P75_B]
    for variable, value in zip(marks, scaled_hint):
        model.add_hint(variable, value)
    hint_pairs = {
        P75_B[j] - P75_B[i]: (i, j)
        for i in range(p)
        for j in range(i + 1, p)
    }
    hinted_edges = 0
    for i in left_indices:
        for j in right_indices:
            c_index, u_index, edge = index_variables[(i, j)]
            inner = hint_pairs.get(988 - (P75_B[j] - P75_B[i]))
            nested = inner is not None and i <= inner[0] < inner[1] <= j
            model.add_hint(edge, int(nested))
            if nested:
                model.add_hint(c_index, inner[0])
                model.add_hint(u_index, inner[1])
                hinted_edges += 1
    if hinted_edges != 30:
        raise AssertionError(("unexpected P75 hint score", hinted_edges))

    validation_error = model.validate()
    if validation_error:
        raise RuntimeError(validation_error)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = 86481
    started = time.perf_counter()
    status = solver.solve(model)
    elapsed = time.perf_counter() - started

    output: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "exact integer CP-SAT",
        "domain": "26 odd marks; six lowest by six highest outer rectangle; positive-defect endpoint range",
        "P75_hint_score": hinted_edges,
        "status": solver.status_name(status),
        "objective_value": None,
        "best_objective_bound": solver.best_objective_bound,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "elapsed_seconds": elapsed,
        "solution": None,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        scaled = [solver.value(mark) for mark in marks]
        values = [2 * value + 1 for value in scaled]
        h = 2 * scaled[-1] + 2
        edges, missing = exact_rectangle(values, h)
        checks = verify(values, h, edges)
        objective = int(round(solver.objective_value))
        if objective != len(edges):
            raise AssertionError(("objective mismatch", objective, len(edges)))
        output["objective_value"] = objective
        output["solution"] = {
            "B": values,
            "left": values[:6],
            "right": values[-6:],
            "edges": edges,
            "missing": missing,
            **checks,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
