#!/usr/bin/env python3
"""Optimize P101 and RM97 over every positive-defect P94 subset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ortools.sat.python import cp_model

from core import audit, canonical_folds, loose_triangles
from search_p88_rm97 import iff_ge_constant, iff_le_constant
from search_p88_subsets import and_var, minimum_positive_defect_size


ROOT = Path(__file__).resolve().parents[4]
P94_JSON = ROOT / "problems/864/compute/p94/c84_archived_audit.json"


def load_seed() -> tuple[tuple[int, ...], int, int]:
    row = json.loads(P94_JSON.read_text(encoding="ascii"))["translation"]["max_ratio_row"]
    return tuple(int(value) for value in row["B"]), int(row["h"]), int(row["b"])


def base_model(
    values: Sequence[int], h: int,
) -> tuple[cp_model.CpModel, list[cp_model.IntVar], list[cp_model.IntVar], list[cp_model.IntVar], list[tuple[int, int, int, int]], list[tuple[int, int, int]]]:
    folds = canonical_folds(values, h)
    triangles = loose_triangles(folds)
    index = {value: i for i, value in enumerate(values)}
    model = cp_model.CpModel()
    marks = [model.new_bool_var(f"mark_{i}") for i in range(len(values))]
    model.add(marks[-1] == 1)
    model.add(sum(marks) >= minimum_positive_defect_size(h))
    active_folds = [
        and_var(
            model,
            [marks[index[value]] for value in sorted(set(fold))],
            f"fold_{fold_id}",
        )
        for fold_id, fold in enumerate(folds)
    ]
    active_triangles = [
        and_var(
            model,
            [active_folds[fold_id] for fold_id in triangle],
            f"triangle_{triangle_id}",
        )
        for triangle_id, triangle in enumerate(triangles)
    ]
    return model, marks, active_folds, active_triangles, folds, triangles


def configure_solver(workers: int, seconds: float, seed: int) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.random_seed = seed
    solver.parameters.log_search_progress = False
    return solver


def common_result(
    solver: cp_model.CpSolver, status: cp_model.CpSolverStatus, workers: int,
    seconds: float,
) -> dict[str, object]:
    return {
        "status": solver.status_name(status),
        "workers": workers,
        "time_limit_seconds": seconds,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "best_objective_bound": solver.best_objective_bound,
    }


def solve_p101(
    values: tuple[int, ...], h: int, b: int, workers: int, seconds: float,
) -> dict[str, object]:
    model, marks, active_folds, active_triangles, folds, triangles = base_model(values, h)
    model.maximize(sum(active_triangles) - sum(active_folds))
    for value, variable in zip(values, marks):
        model.add_hint(variable, int(value != 4740))
    solver = configure_solver(workers, seconds, 10741)
    status = solver.solve(model)
    result = common_result(solver, status, workers, seconds)
    result.update({"parent_folds": len(folds), "parent_triangles": len(triangles)})
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = tuple(value for value, variable in zip(values, marks) if solver.value(variable))
        exact = audit(selected, h, b)
        result.update({"objective": solver.objective_value, "candidate": exact})
        if exact["delta"] <= 0 or not exact["literal_hole"] or exact["V_b"] != 0:
            raise AssertionError(("gate replay", exact["delta"], exact["literal_hole"], exact["V_b"]))
        if int(exact["P101_excess"]) != int(round(solver.objective_value)):
            raise AssertionError(("objective replay", exact["P101_excess"], solver.objective_value))
    return result


def solve_rm97(
    values: tuple[int, ...], h: int, b: int, workers: int, seconds: float,
) -> dict[str, object]:
    model, marks, active_folds, active_triangles, folds, triangles = base_model(values, h)
    shared = [(a, c, u) for a, c, u, _v in folds]
    for base, au, cu in triangles:
        a, c, _r, _s = folds[base]
        u = folds[au][2]
        if folds[cu][2] != u:
            raise AssertionError((base, au, cu))
        shared.append((a, c, u))
    intervals = [
        (min(u - a - c - b, h - b - u), max(u - a - c - b, h - b - u))
        for a, c, u in shared
    ]
    fold_slots = [(h - b - v, h - b - u) for _a, _c, u, v in folds]
    coordinates = [coordinate for interval in intervals for coordinate in interval]
    coordinates.extend(point for pair in fold_slots for point in pair)
    left = model.new_int_var(min(coordinates), max(coordinates), "window_left")
    right = model.new_int_var(min(coordinates), max(coordinates), "window_right")
    model.add(left <= right)
    active_demands = active_folds + active_triangles
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
    for value, variable in zip(values, marks):
        model.add_hint(variable, int(value != 4740))
    solver = configure_solver(workers, seconds, 10742)
    status = solver.solve(model)
    result = common_result(solver, status, workers, seconds)
    result.update({
        "parent_folds": len(folds),
        "parent_triangles": len(triangles),
        "coordinate_range": [min(coordinates), max(coordinates)],
    })
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = tuple(value for value, variable in zip(values, marks) if solver.value(variable))
        exact = audit(selected, h, b)
        window = [solver.value(left), solver.value(right)]
        demands = sum(solver.value(term) for term in demand_terms)
        slots = sum(solver.value(term) for term in slot_terms)
        result.update({
            "objective": solver.objective_value,
            "window": window,
            "window_demand_count": demands,
            "window_slot_count": slots,
            "candidate": exact,
        })
        if exact["delta"] <= 0 or not exact["literal_hole"] or exact["V_b"] != 0:
            raise AssertionError(("gate replay", exact["delta"], exact["literal_hole"], exact["V_b"]))
        if demands - slots != int(round(solver.objective_value)):
            raise AssertionError(("objective replay", demands, slots, solver.objective_value))
        if solver.objective_value > 0 and exact["RM97_unmatched"] <= 0:
            raise AssertionError(("RM97 replay", window, exact["RM97_unmatched"]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seconds", type=float, default=600.0)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("p94_subset_search.json"))
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be in [1,16]")
    values, h, b = load_seed()
    seed = audit(values, h, b)
    if not seed["literal_hole"] or seed["delta"] <= 0:
        raise AssertionError((seed["literal_hole"], seed["delta"]))
    payload = {
        "schema_version": 1,
        "arithmetic": "CP-SAT selects subsets; all retained candidates replayed with exact integers",
        "domain": "all endpoint-preserving subsets of P94 with strict positive defect; Sidon and literal-hole gates are hereditary",
        "parent": {key: seed[key] for key in ("sha256", "p", "h", "b", "delta", "C_S", "T_F", "V_b")},
        "minimum_positive_defect_size": minimum_positive_defect_size(h),
        "P101": solve_p101(values, h, b, args.workers, args.seconds),
        "RM97": solve_rm97(values, h, b, args.workers, args.seconds),
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

