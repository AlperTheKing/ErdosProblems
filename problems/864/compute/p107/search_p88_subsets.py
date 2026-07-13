#!/usr/bin/env python3
"""CP-SAT search for a positive-defect literal-hole P101 witness in P88."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ortools.sat.python import cp_model

from core import audit, canonical_folds, loose_triangles


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "p88_subset_search.json"

P88 = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941,
    1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613, 1617,
    1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380,
    2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901, 2950,
    2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222,
    3248, 3285,
)

P105_SOURCE = {
    0, 122, 163, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941, 1051,
    1070, 1117, 1340, 1414, 1449, 1520, 1608, 1613, 1617, 1715, 1853,
    1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380, 2475, 2521,
    2564, 2596, 2598, 2654, 2788, 2839, 2901, 2950, 2958, 3026, 3070,
    3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222, 3248, 3285,
}


def and_var(
    model: cp_model.CpModel,
    inputs: Sequence[cp_model.IntVar],
    name: str,
) -> cp_model.IntVar:
    output = model.new_bool_var(name)
    for variable in inputs:
        model.add(output <= variable)
    model.add(output >= sum(inputs) - len(inputs) + 1)
    return output


def collision_supports(values: Sequence[int], b: int) -> list[tuple[int, ...]]:
    index = {value: i for i, value in enumerate(values)}
    supports: set[tuple[int, ...]] = set()
    for i, x in enumerate(values):
        for y in values[i + 1:]:
            difference = y - x
            for j, a in enumerate(values):
                for c in values[j:]:
                    if a + c + b != difference:
                        continue
                    supports.add(tuple(sorted({index[x], index[y], index[a], index[c]})))
    return sorted(supports)


def minimum_positive_defect_size(h: int) -> int:
    p = 1
    while (3 * p * p - p + 2) // 2 - h <= 0:
        p += 1
    return p


def solve(b: int, workers: int, seconds: float) -> dict[str, object]:
    h = P88[-1] + 1
    folds = canonical_folds(P88, h)
    triangles = loose_triangles(folds)
    index = {value: i for i, value in enumerate(P88)}
    collisions = collision_supports(P88, b)

    model = cp_model.CpModel()
    marks = [model.new_bool_var(f"mark_{i}") for i in range(len(P88))]
    model.add(marks[-1] == 1)
    minimum_p = minimum_positive_defect_size(h)
    model.add(sum(marks) >= minimum_p)
    for support in collisions:
        model.add(sum(marks[i] for i in support) <= len(support) - 1)

    active_folds = []
    for fold_id, fold in enumerate(folds):
        needed = [marks[index[value]] for value in sorted(set(fold))]
        active_folds.append(and_var(model, needed, f"fold_{fold_id}"))
    active_triangles = []
    for triangle_id, triangle in enumerate(triangles):
        needed = [active_folds[fold_id] for fold_id in triangle]
        active_triangles.append(and_var(model, needed, f"triangle_{triangle_id}"))

    objective = sum(active_triangles) - sum(active_folds)
    model.maximize(objective)
    for value, variable in zip(P88, marks):
        model.add_hint(variable, int(value in P105_SOURCE))

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 10700 + b
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.log_search_progress = False
    status = solver.solve(model)

    result: dict[str, object] = {
        "b": b,
        "status": solver.status_name(status),
        "workers": workers,
        "time_limit_seconds": seconds,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "best_objective_bound": solver.best_objective_bound,
        "minimum_positive_defect_size": minimum_p,
        "literal_collision_supports": len(collisions),
        "parent_folds": len(folds),
        "parent_triangles": len(triangles),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = tuple(value for value, variable in zip(P88, marks) if solver.value(variable))
        exact = audit(selected, h, b)
        result["objective"] = solver.objective_value
        result["candidate"] = exact
        if exact["delta"] <= 0 or not exact["literal_hole"]:
            raise AssertionError(("gate replay", exact["delta"], exact["literal_hole"]))
        if int(exact["P101_excess"]) != int(round(solver.objective_value)):
            raise AssertionError(("objective replay", exact["P101_excess"], solver.objective_value))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seconds", type=float, default=600.0)
    parser.add_argument("--b", type=int, choices=(1, 2), nargs="+", default=(1, 2))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be in [1,16]")
    payload = {
        "schema_version": 1,
        "arithmetic": "CP-SAT selects marks; every candidate is replayed with exact Python integers",
        "domain": "all endpoint-preserving subsets of the 60-mark P88 Sidon ruler with strict positive defect and the literal b-hole",
        "results": [solve(b, args.workers, args.seconds) for b in args.b],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

