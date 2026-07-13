"""Exact CP-SAT search for a q=4 block core with intersection excess three."""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path

from ortools.sat.python import cp_model


OUT = Path(__file__).with_name("q4_excess_core_result.json")


def edge_list() -> list[tuple[int, int]]:
    # K_4,4 minus the diagonal perfect matching and the edge (0,1).
    return [
        (i, j)
        for i in range(4)
        for j in range(4)
        if i != j and (i, j) != (0, 1)
    ]


def verify(
    edges: list[tuple[int, int]],
    common: list[int],
    left_private: int,
    right_private: int,
) -> tuple[int, int]:
    labels = [*common, left_private, right_private]
    assert len(labels) == len(set(labels)) == 13
    sums = [
        labels[i] + labels[j]
        for i, j in combinations_with_replacement(range(13), 2)
    ]
    assert len(sums) == len(set(sums)) == 91
    left = []
    right = []
    for i in range(4):
        block = [common[k] for k, (u, _) in enumerate(edges) if u == i]
        if i == 0:
            block.append(left_private)
        assert len(block) == 3
        left.append(tuple(block))
    for j in range(4):
        block = [common[k] for k, (_, v) in enumerate(edges) if v == j]
        if j == 1:
            block.append(right_private)
        assert len(block) == 3
        right.append(tuple(block))
    assert len({sum(block) for block in left}) == 1
    assert len({sum(block) for block in right}) == 1
    assert sum(left[0]) != sum(right[0])
    return sum(left[0]), sum(right[0])


def search(bound: int, workers: int, seconds: float) -> dict[str, object] | None:
    edges = edge_list()
    assert len(edges) == 11
    model = cp_model.CpModel()
    common = [
        model.new_int_var(0, bound, f"u_{i}_{j}") for i, j in edges
    ]
    lp = model.new_int_var(0, bound, "left_private")
    rp = model.new_int_var(0, bound, "right_private")
    labels = [*common, lp, rp]
    model.add_all_different(labels)
    minimum = model.new_int_var(0, bound, "minimum")
    model.add_min_equality(minimum, labels)
    model.add(minimum == 0)
    x = model.new_int_var(0, 3 * bound, "x")
    y = model.new_int_var(0, 3 * bound, "y")
    for i in range(4):
        terms = [common[k] for k, (u, _) in enumerate(edges) if u == i]
        if i == 0:
            terms.append(lp)
        model.add(x == sum(terms))
    for j in range(4):
        terms = [common[k] for k, (_, v) in enumerate(edges) if v == j]
        if j == 1:
            terms.append(rp)
        model.add(y == sum(terms))
    model.add(y >= x + 1)

    pair_sums = []
    for i, j in combinations_with_replacement(range(13), 2):
        value = model.new_int_var(0, 2 * bound, f"s_{i}_{j}")
        model.add(value == labels[i] + labels[j])
        pair_sums.append(value)
    model.add_all_different(pair_sums)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.random_seed = 67
    solver.parameters.randomize_search = True
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    cc = [solver.value(value) for value in common]
    left_private = solver.value(lp)
    right_private = solver.value(rp)
    x_value, y_value = verify(edges, cc, left_private, right_private)
    return {
        "status": solver.status_name(status),
        "bound": bound,
        "edges": [list(edge) for edge in edges],
        "common": cc,
        "left_private": left_private,
        "right_private": right_private,
        "x": x_value,
        "y": y_value,
        "labels": sorted([*cc, left_private, right_private]),
        "intersection_size": 11,
        "block_count_sum": 8,
        "excess": 3,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=1000)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--seconds", type=float, default=300.0)
    args = parser.parse_args()
    result = search(args.bound, args.workers, args.seconds)
    payload = {"exact_solver": "OR-Tools CP-SAT", "result": result}
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
