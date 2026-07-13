"""Exact CP-SAT search for a block core with intersection excess two.

The eight common marks occupy K_{3,3} minus one edge.  Each side has one
private mark completing its degree-two block.  Hence two distinct sum columns
would have 8 common marks but only 3+3 blocks, falsifying the +1 bound.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path

from ortools.sat.python import cp_model


OUT = Path(__file__).with_name("excess2_core_result.json")


def verify(common: list[int], left_private: int, right_private: int) -> None:
    # Cell order: 01,02,10,11,12,20,21,22.
    u01, u02, u10, u11, u12, u20, u21, u22 = common
    left = [
        (u01, u02, left_private),
        (u10, u11, u12),
        (u20, u21, u22),
    ]
    right = [
        (u10, u20, right_private),
        (u01, u11, u21),
        (u02, u12, u22),
    ]
    assert len({sum(block) for block in left}) == 1
    assert len({sum(block) for block in right}) == 1
    assert sum(left[0]) != sum(right[0])
    labels = [*common, left_private, right_private]
    assert len(labels) == len(set(labels)) == 10
    sums = [
        labels[i] + labels[j]
        for i, j in combinations_with_replacement(range(10), 2)
    ]
    assert len(sums) == len(set(sums)) == 55


def search(bound: int, workers: int, seconds: float) -> dict[str, object] | None:
    model = cp_model.CpModel()
    names = ("u01", "u02", "u10", "u11", "u12", "u20", "u21", "u22")
    common = [model.new_int_var(0, bound, name) for name in names]
    lp = model.new_int_var(0, bound, "left_private")
    rp = model.new_int_var(0, bound, "right_private")
    labels = [*common, lp, rp]
    model.add_all_different(labels)
    minimum = model.new_int_var(0, bound, "minimum")
    maximum = model.new_int_var(0, bound, "maximum")
    model.add_min_equality(minimum, labels)
    model.add_max_equality(maximum, labels)
    model.add(minimum == 0)

    u01, u02, u10, u11, u12, u20, u21, u22 = common
    x = model.new_int_var(0, 3 * bound, "x")
    y = model.new_int_var(0, 3 * bound, "y")
    model.add(x == u01 + u02 + lp)
    model.add(x == u10 + u11 + u12)
    model.add(x == u20 + u21 + u22)
    model.add(y == u10 + u20 + rp)
    model.add(y == u01 + u11 + u21)
    model.add(y == u02 + u12 + u22)
    model.add(y >= x + 1)

    pair_sums = []
    for i, j in combinations_with_replacement(range(10), 2):
        value = model.new_int_var(0, 2 * bound, f"s_{i}_{j}")
        model.add(value == labels[i] + labels[j])
        pair_sums.append(value)
    model.add_all_different(pair_sums)
    model.minimize(maximum)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = seconds
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    cc = [solver.value(value) for value in common]
    left_private = solver.value(lp)
    right_private = solver.value(rp)
    verify(cc, left_private, right_private)
    labels_out = [*cc, left_private, right_private]
    return {
        "status": solver.status_name(status),
        "bound": bound,
        "maximum": max(labels_out),
        "common": dict(zip(names, cc, strict=True)),
        "left_private": left_private,
        "right_private": right_private,
        "x": solver.value(x),
        "y": solver.value(y),
        "labels": sorted(labels_out),
        "pair_sums": 55,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=250)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--seconds", type=float, default=300.0)
    args = parser.parse_args()
    result = search(args.bound, args.workers, args.seconds)
    payload = {"exact_solver": "OR-Tools CP-SAT", "result": result}
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
