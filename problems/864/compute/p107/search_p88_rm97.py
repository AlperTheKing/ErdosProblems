#!/usr/bin/env python3
"""Joint CP-SAT optimization of RM97 Hall deficit over all P88 subsets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ortools.sat.python import cp_model

from core import audit, canonical_folds, loose_triangles
from search_p88_subsets import (
    P88,
    P105_SOURCE,
    and_var,
    collision_supports,
    minimum_positive_defect_size,
)


HERE = Path(__file__).resolve().parent


def iff_le_constant(
    model: cp_model.CpModel, variable: cp_model.IntVar, constant: int, name: str
) -> cp_model.IntVar:
    flag = model.new_bool_var(name)
    model.add(variable <= constant).only_enforce_if(flag)
    model.add(variable >= constant + 1).only_enforce_if(flag.Not())
    return flag


def iff_ge_constant(
    model: cp_model.CpModel, variable: cp_model.IntVar, constant: int, name: str
) -> cp_model.IntVar:
    flag = model.new_bool_var(name)
    model.add(variable >= constant).only_enforce_if(flag)
    model.add(variable <= constant - 1).only_enforce_if(flag.Not())
    return flag


def solve(b: int, workers: int, seconds: float) -> dict[str, object]:
    h = P88[-1] + 1
    folds = canonical_folds(P88, h)
    triangles = loose_triangles(folds)
    index = {value: i for i, value in enumerate(P88)}
    collision_sets = collision_supports(P88, b)

    shared: list[tuple[int, int, int]] = [(a, c, u) for a, c, u, _v in folds]
    for base, au, cu in triangles:
        a, c, _r, _s = folds[base]
        u = folds[au][2]
        if folds[cu][2] != u:
            raise AssertionError((base, au, cu))
        shared.append((a, c, u))
    intervals = [
        (
            min(u - a - c - b, h - b - u),
            max(u - a - c - b, h - b - u),
        )
        for a, c, u in shared
    ]
    fold_slots = [
        (h - b - v, h - b - u)
        for _a, _c, u, v in folds
    ]
    coordinates = [coordinate for interval in intervals for coordinate in interval]
    coordinates.extend(point for pair in fold_slots for point in pair)
    minimum_coordinate, maximum_coordinate = min(coordinates), max(coordinates)

    model = cp_model.CpModel()
    marks = [model.new_bool_var(f"mark_{i}") for i in range(len(P88))]
    model.add(marks[-1] == 1)
    minimum_p = minimum_positive_defect_size(h)
    model.add(sum(marks) >= minimum_p)
    for support in collision_sets:
        model.add(sum(marks[i] for i in support) <= len(support) - 1)

    active_folds = []
    for fold_id, fold in enumerate(folds):
        active_folds.append(and_var(
            model,
            [marks[index[value]] for value in sorted(set(fold))],
            f"fold_{fold_id}",
        ))
    active_triangles = []
    for triangle_id, triangle in enumerate(triangles):
        active_triangles.append(and_var(
            model,
            [active_folds[fold_id] for fold_id in triangle],
            f"triangle_{triangle_id}",
        ))
    active_demands = active_folds + active_triangles

    left = model.new_int_var(minimum_coordinate, maximum_coordinate, "window_left")
    right = model.new_int_var(minimum_coordinate, maximum_coordinate, "window_right")
    model.add(left <= right)

    demand_terms = []
    for demand_id, ((lower, upper), active) in enumerate(zip(intervals, active_demands)):
        starts = iff_le_constant(model, left, lower, f"demand_left_{demand_id}")
        ends = iff_ge_constant(model, right, upper, f"demand_right_{demand_id}")
        contained = and_var(model, (starts, ends), f"demand_contained_{demand_id}")
        demand_terms.append(and_var(model, (active, contained), f"demand_used_{demand_id}"))

    slot_terms = []
    for fold_id, (points, active) in enumerate(zip(fold_slots, active_folds)):
        for side, point in enumerate(points):
            starts = iff_le_constant(model, left, point, f"slot_left_{fold_id}_{side}")
            ends = iff_ge_constant(model, right, point, f"slot_right_{fold_id}_{side}")
            inside = and_var(model, (starts, ends), f"slot_inside_{fold_id}_{side}")
            slot_terms.append(and_var(model, (active, inside), f"slot_used_{fold_id}_{side}"))

    model.maximize(sum(demand_terms) - sum(slot_terms))
    for value, variable in zip(P88, marks):
        model.add_hint(variable, int(value in P105_SOURCE))

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 10720 + b
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
        "literal_collision_supports": len(collision_sets),
        "parent_folds": len(folds),
        "parent_triangles": len(triangles),
        "coordinate_range": [minimum_coordinate, maximum_coordinate],
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = tuple(value for value, variable in zip(P88, marks) if solver.value(variable))
        exact = audit(selected, h, b)
        window = [solver.value(left), solver.value(right)]
        demand_count = sum(solver.value(term) for term in demand_terms)
        slot_count = sum(solver.value(term) for term in slot_terms)
        result.update({
            "objective": solver.objective_value,
            "window": window,
            "window_demand_count": demand_count,
            "window_slot_count": slot_count,
            "candidate": exact,
        })
        if exact["delta"] <= 0 or not exact["literal_hole"]:
            raise AssertionError(("gate replay", exact["delta"], exact["literal_hole"]))
        if demand_count - slot_count != int(round(solver.objective_value)):
            raise AssertionError(("objective replay", demand_count, slot_count, solver.objective_value))
        if solver.objective_value > 0 and exact["RM97_unmatched"] <= 0:
            raise AssertionError(("RM97 replay", window, exact["RM97_unmatched"]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seconds", type=float, default=600.0)
    parser.add_argument("--b", type=int, choices=(1, 2), nargs="+", default=(1, 2))
    parser.add_argument("--output", type=Path, default=HERE / "p88_rm97_search.json")
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be in [1,16]")
    payload = {
        "schema_version": 1,
        "arithmetic": "CP-SAT selection and Hall-window optimization; exact integer replay",
        "domain": "all endpoint-preserving positive-defect literal-hole subsets of P88",
        "results": [solve(b, args.workers, args.seconds) for b in args.b],
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

