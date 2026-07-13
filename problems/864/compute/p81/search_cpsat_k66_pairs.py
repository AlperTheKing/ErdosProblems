#!/usr/bin/env python3
"""Exact p=26 K_6,6 search with explicit nested complementary pairs."""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "problems/864/compute/p81/cpsat_k66_explicit_pairs.json"
P75_B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505,
    519, 631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
]


def verify(values: list[int], h: int, left: list[int], right: list[int]) -> dict:
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
    pairs = {
        values[j] - values[i]: (values[i], values[j])
        for i in range(p)
        for j in range(i + 1, p)
    }
    edges = []
    for outer_low in left:
        for outer_high in right:
            inner = pairs[h - (outer_high - outer_low)]
            assert outer_low <= inner[0] < inner[1] <= outer_high
            edges.append(
                {
                    "outer_edge": [outer_low, outer_high],
                    "inner_edge": list(inner),
                    "low_sum": outer_low + inner[0],
                    "high_sum": inner[1] + outer_high,
                }
            )
    assert len(edges) == 36
    assert all(edge["low_sum"] + h == edge["high_sum"] for edge in edges)
    return {
        "p": p,
        "h": h,
        "b": 1,
        "delta": delta,
        "B": values,
        "left": left,
        "right": right,
        "sum_count": len(sums),
        "difference_count": len(differences),
        "edges": edges,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seed", type=int, default=86481)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    p = 26
    model = cp_model.CpModel()
    marks = [model.new_int_var(0, 499, f"x_{i}") for i in range(p)]
    model.add(marks[-1] >= 325)
    for i in range(p - 1):
        model.add(marks[i + 1] >= marks[i] + 1)

    differences = {}
    for i in range(p):
        for j in range(i + 1, p):
            difference = model.new_int_var(1, 499, f"d_{i}_{j}")
            model.add(difference == marks[j] - marks[i])
            differences[(i, j)] = difference
    model.add_all_different(list(differences.values()))
    model.add(2 * marks[5] < marks[-1])
    model.add(2 * marks[20] >= marks[-1])

    selectors = {}
    for i in range(6):
        for j in range(20, 26):
            choices = []
            for c in range(i, j):
                for u in range(c + 1, j + 1):
                    selected = model.new_bool_var(f"z_{i}_{j}_{c}_{u}")
                    model.add(
                        differences[(i, j)] + differences[(c, u)]
                        == marks[-1] + 1
                    ).only_enforce_if(selected)
                    choices.append(selected)
                    selectors[(i, j, c, u)] = selected
            model.add_exactly_one(choices)

    scaled_hint = [(value - 1) // 2 for value in P75_B]
    for variable, value in zip(marks, scaled_hint):
        model.add_hint(variable, value)
    hint_pairs = {
        P75_B[j] - P75_B[i]: (i, j)
        for i in range(p)
        for j in range(i + 1, p)
    }
    hinted_edges = 0
    for i in range(6):
        for j in range(20, 26):
            inner = hint_pairs.get(988 - (P75_B[j] - P75_B[i]))
            if inner is None or not (i <= inner[0] < inner[1] <= j):
                continue
            model.add_hint(selectors[(i, j, inner[0], inner[1])], 1)
            hinted_edges += 1
    if hinted_edges != 30:
        raise AssertionError(("unexpected hint score", hinted_edges))

    validation_error = model.validate()
    if validation_error:
        raise RuntimeError(validation_error)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    started = time.perf_counter()
    status = solver.solve(model)
    elapsed = time.perf_counter() - started
    output: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "exact integer CP-SAT",
        "domain": "26 odd marks, positive defect, K6,6 on the six lowest and six highest marks",
        "encoding": "explicit nested pair selector with complementary distance sum",
        "P75_hinted_edges": hinted_edges,
        "parameters": {
            "seconds": args.seconds,
            "workers": args.workers,
            "random_seed": args.seed,
        },
        "status": solver.status_name(status),
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "elapsed_seconds": elapsed,
        "witness": None,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        scaled = [solver.value(mark) for mark in marks]
        values = [2 * value + 1 for value in scaled]
        h = 2 * scaled[-1] + 2
        output["witness"] = verify(values, h, values[:6], values[-6:])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
