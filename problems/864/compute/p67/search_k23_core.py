"""Exact CP-SAT search for a K_{2,3} block-intersection core.

Two disjoint triples A_i and B_i have common sum x.  Three triples
(A_i,B_i,C_i) have common sum y.  Their block-intersection graph is K_{2,3},
so any Sidon labeling is a two-cycle obstruction to the pseudoforest route.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path

from ortools.sat.python import cp_model


OUT = Path(__file__).with_name("k23_core_result.json")


def verify(values: list[int], a: list[int], b: list[int], c: list[int]) -> None:
    assert len(values) == len(set(values)) == 9
    pair_values = [
        values[i] + values[j]
        for i, j in combinations_with_replacement(range(9), 2)
    ]
    assert len(pair_values) == len(set(pair_values)) == 45
    x = sum(a)
    assert sum(b) == x
    right = [a[i] + b[i] + c[i] for i in range(3)]
    assert len(set(right)) == 1
    assert right[0] != x


def search(bound: int, workers: int) -> dict[str, object] | None:
    model = cp_model.CpModel()
    a = [model.new_int_var(0, bound, f"a{i}") for i in range(3)]
    b = [model.new_int_var(0, bound, f"b{i}") for i in range(3)]
    c = [model.new_int_var(0, bound, f"c{i}") for i in range(3)]
    labels = [*a, *b, *c]
    model.add_all_different(labels)

    minimum = model.new_int_var(0, bound, "minimum")
    maximum = model.new_int_var(0, bound, "maximum")
    model.add_min_equality(minimum, labels)
    model.add_max_equality(maximum, labels)
    model.add(minimum == 0)

    x = model.new_int_var(0, 3 * bound, "x")
    y = model.new_int_var(0, 3 * bound, "y")
    model.add(x == sum(a))
    model.add(x == sum(b))
    for i in range(3):
        model.add(y == a[i] + b[i] + c[i])
    model.add(y >= x + 1)

    # Jointly permuting the three right blocks permits sorting A.
    model.add(a[0] < a[1])
    model.add(a[1] < a[2])

    pair_sums = []
    for i, j in combinations_with_replacement(range(9), 2):
        pair_sum = model.new_int_var(0, 2 * bound, f"s_{i}_{j}")
        model.add(pair_sum == labels[i] + labels[j])
        pair_sums.append(pair_sum)
    model.add_all_different(pair_sums)
    model.minimize(maximum)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = 300.0
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    aa = [solver.value(value) for value in a]
    bb = [solver.value(value) for value in b]
    cc = [solver.value(value) for value in c]
    values = aa + bb + cc
    verify(values, aa, bb, cc)
    return {
        "status": solver.status_name(status),
        "bound": bound,
        "maximum": max(values),
        "A": aa,
        "B": bb,
        "C": cc,
        "x": sum(aa),
        "y": aa[0] + bb[0] + cc[0],
        "labels": sorted(values),
        "pair_sums": 45,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=160)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    result = search(args.bound, args.workers)
    payload = {"exact_solver": "OR-Tools CP-SAT", "result": result}
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
