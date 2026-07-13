#!/usr/bin/env python3
"""Exact transformation and CP-SAT subset search for corrected C84."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence

from ortools.sat.python import cp_model


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "corrected_c84_falsifier.json"

P88 = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941,
    1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613, 1617,
    1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380,
    2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901, 2950,
    2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222,
    3248, 3285,
)


def digest(values: Sequence[int]) -> str:
    payload = ",".join(map(str, values)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in result:
                raise ValueError(("repeated sum", total, result[total], (left, right)))
            result[total] = (left, right)
    return result


def difference_set(values: Sequence[int]) -> set[int]:
    result: set[int] = set()
    for j, right in enumerate(values):
        for left in values[:j]:
            difference = right - left
            if difference in result:
                raise ValueError(("repeated difference", difference))
            result.add(difference)
    return result


def folds_for(values: Sequence[int], h: int) -> list[tuple[int, int, int, int]]:
    sums = sum_map(values)
    folds = []
    for low in sorted(sums):
        if low + h not in sums:
            continue
        a, c = sums[low]
        u, v = sums[low + h]
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v))
        folds.append((a, c, u, v))
    return folds


def triangles_for(
    folds: Sequence[tuple[int, int, int, int]],
) -> list[tuple[int, int, int]]:
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    for a, c in ac:
        for aa, u in au:
            if aa != a:
                continue
            ids = (ac[a, c], au[a, u], cu.get((c, u)))
            if ids[2] is None or ids[0] == ids[1] == ids[2]:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("linearity", ids))
            triangles.append((ids[0], ids[1], ids[2]))
    return triangles


def audit(values_input: Iterable[int], h: int, b: int) -> dict[str, object]:
    values = tuple(sorted(values_input))
    if len(values) != len(set(values)) or not values:
        raise AssertionError("marks must be nonempty and distinct")
    if values[0] < 0 or values[-1] != h - 1 or b not in (1, 2):
        raise AssertionError(("endpoint", values[:1], values[-1:], h, b))
    sums = sum_map(values)
    differences = difference_set(values)
    folds = folds_for(values, h)
    triangles = triangles_for(folds)
    collisions = [fold for fold in folds if fold[0] + fold[1] + b in differences]
    literal_hole = differences.isdisjoint(total + b for total in sums)
    excess = len(triangles) - len(folds) - len(collisions)
    delta = (3 * len(values) * len(values) - len(values) + 2) // 2 - h
    return {
        "B": list(values),
        "sha256": digest(values),
        "p": len(values),
        "h": h,
        "b": b,
        "delta": delta,
        "sum_count": len(sums),
        "difference_count": len(differences),
        "C_S": len(folds),
        "T_F": len(triangles),
        "V_b": len(collisions),
        "excess": excess,
        "literal_hole": literal_hole,
        "folds": [list(fold) for fold in folds],
        "triangles": [list(triangle) for triangle in triangles],
    }


def q2_lift(values: Sequence[int], h: int) -> tuple[tuple[int, ...], int, int]:
    return tuple(2 * value + 1 for value in values), 2 * h, 1


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


def minimize_seed_subset(workers: int) -> dict[str, object]:
    seed_h = P88[-1] + 1
    folds = folds_for(P88, seed_h)
    triangles = triangles_for(folds)
    index = {value: i for i, value in enumerate(P88)}

    model = cp_model.CpModel()
    marks = [model.new_bool_var(f"mark_{i}") for i in range(len(P88))]
    model.add(marks[-1] == 1)
    active_folds = []
    for fold_id, fold in enumerate(folds):
        needed = [marks[index[value]] for value in sorted(set(fold))]
        active_folds.append(and_var(model, needed, f"fold_{fold_id}"))
    active_triangles = []
    for triangle_id, triangle in enumerate(triangles):
        needed = [active_folds[fold_id] for fold_id in triangle]
        active_triangles.append(and_var(model, needed, f"triangle_{triangle_id}"))

    model.add(sum(active_triangles) >= sum(active_folds) + 1)
    model.minimize(sum(marks))

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 105
    solver.parameters.log_search_progress = False
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f"CP-SAT failed with status {solver.status_name(status)}")

    subset = tuple(value for value, variable in zip(P88, marks) if solver.value(variable))
    source_audit = audit(subset, seed_h, 1)
    lifted, lifted_h, lifted_b = q2_lift(subset, seed_h)
    lifted_audit = audit(lifted, lifted_h, lifted_b)
    if source_audit["T_F"] <= source_audit["C_S"]:
        raise AssertionError("source subset is not a C84 falsifier")
    if lifted_audit["excess"] <= 0 or not lifted_audit["literal_hole"]:
        raise AssertionError("lifted subset is not a corrected-C84 falsifier")
    return {
        "cp_sat_status": solver.status_name(status),
        "workers": workers,
        "objective_mark_count": int(round(solver.objective_value)),
        "best_bound": int(round(solver.best_objective_bound)),
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "source_subset": source_audit,
        "q2_lifted_witness": lifted_audit,
    }


def verify_payload(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="ascii"))
    search = payload["subset_search"]
    for key, b in (("source_subset", 1), ("q2_lifted_witness", 1)):
        stored = search[key]
        fresh = audit(stored["B"], int(stored["h"]), b)
        for field in (
            "sha256", "p", "h", "b", "sum_count", "difference_count",
            "delta", "C_S", "T_F", "V_b", "excess", "literal_hole", "folds",
            "triangles",
        ):
            if fresh[field] != stored[field]:
                raise AssertionError((key, field, fresh[field], stored[field]))
    witness = search["q2_lifted_witness"]
    assert witness["T_F"] > witness["C_S"] + witness["V_b"]
    print("PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be in [1,16]")
    if args.verify:
        verify_payload(args.verify)
        return

    seed_lift, seed_lift_h, seed_lift_b = q2_lift(P88, P88[-1] + 1)
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers; CP-SAT only selects a subset",
        "transformation": "B -> 2B+1, h -> 2h, b=1",
        "full_P88_q2_lift": audit(seed_lift, seed_lift_h, seed_lift_b),
        "subset_search": minimize_seed_subset(args.workers),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "output": str(args.output),
        "full": {
            key: result["full_P88_q2_lift"][key]
            for key in ("p", "h", "delta", "C_S", "T_F", "V_b", "excess")
        },
        "subset_search": {
            key: result["subset_search"][key]
            for key in (
                "cp_sat_status", "objective_mark_count", "best_bound",
                "wall_time_seconds", "branches", "conflicts",
            )
        },
        "witness": {
            key: result["subset_search"]["q2_lifted_witness"][key]
            for key in ("B", "sha256", "p", "h", "b", "delta", "C_S", "T_F", "V_b", "excess")
        },
    }, indent=2))


if __name__ == "__main__":
    main()
