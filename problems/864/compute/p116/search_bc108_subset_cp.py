#!/usr/bin/env python3
"""Exact CP-SAT search for induced-subset BC108 falsifiers.

The parent indices are in the deterministic P86 archive ordering.  A FEASIBLE
solution is an exact witness; a no-witness conclusion is certified only when
the solver status is INFEASIBLE or OPTIMAL as appropriate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
P86_PATH = ROOT / "problems/864/compute/p86/dense_loose_search.py"
SCORER_PATH = ROOT / "problems/864/compute/p116/search_bc108_falsifier.py"
DEFAULT_PARENTS = (174, 1625, 2473, 2486, 2500)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def and_indicator(model, selected, support: Iterable[int], name: str):
    marks = tuple(sorted(set(support)))
    indicator = model.NewBoolVar(name)
    for mark in marks:
        model.Add(indicator <= selected[mark])
    model.Add(indicator >= sum(selected[mark] for mark in marks) - len(marks) + 1)
    return indicator


def positive_defect_min_p(h: int) -> int:
    p = 1
    while (3 * p * p - p + 2) // 2 <= h:
        p += 1
    return p


def hole_supports(values: Sequence[int], b: int) -> list[tuple[int, ...]]:
    sums = {
        left + right: (left, right)
        for index, left in enumerate(values) for right in values[index:]
    }
    differences = {
        right - left: (left, right)
        for index, right in enumerate(values) for left in values[:index]
    }
    rows = {
        tuple(sorted(set(pair + differences[total + b])))
        for total, pair in sums.items() if total + b in differences
    }
    return sorted(rows, key=lambda row: (len(row), row))


def triangle_supports(folds, triangles) -> list[tuple[int, ...]]:
    return [
        tuple(sorted({mark for fold_id in triangle for mark in folds[fold_id]}))
        for triangle in triangles
    ]


def model_for(values: tuple[int, ...], b: int, require_failure: bool):
    scorer = load(f"p116_scorer_model_{len(values)}_{b}", SCORER_PATH)
    h = values[-1] + 1
    system = scorer.fold_triangle_system(values, h)
    holes = hole_supports(values, b)
    supports = triangle_supports(system.folds, system.triangles)

    model = cp_model.CpModel()
    selected = {mark: model.NewBoolVar(f"x_{mark}") for mark in values}
    model.Add(selected[values[-1]] == 1)
    p_min = positive_defect_min_p(h)
    p_var = model.NewIntVar(p_min, len(values), "p")
    model.Add(p_var == sum(selected.values()))
    for support in holes:
        model.Add(sum(selected[mark] for mark in support) <= len(support) - 1)

    fold_vars = [
        and_indicator(model, selected, fold, f"f_{index}")
        for index, fold in enumerate(system.folds)
    ]
    triangle_vars = [
        and_indicator(model, selected, support, f"t_{index}")
        for index, support in enumerate(supports)
    ]
    folds_by_color: dict[int, list[object]] = defaultdict(list)
    triangles_by_color: dict[int, list[object]] = defaultdict(list)
    for index, (_a, _c, color, _v) in enumerate(system.folds):
        folds_by_color[color].append(fold_vars[index])
    for index, (_base, arm_au, arm_cu) in enumerate(system.triangles):
        color = system.folds[arm_au][2]
        if system.folds[arm_cu][2] != color:
            raise AssertionError("arm colors disagree")
        triangles_by_color[color].append(triangle_vars[index])

    excess_vars = []
    for color in sorted(triangles_by_color):
        n_max = len(folds_by_color[color])
        t_max = len(triangles_by_color[color])
        difference = model.NewIntVar(-n_max, t_max, f"d_{color}")
        model.Add(
            difference
            == sum(triangles_by_color[color]) - sum(folds_by_color[color])
        )
        positive = model.NewIntVar(0, t_max, f"e_{color}")
        sign = model.NewBoolVar(f"z_{color}")
        model.Add(positive >= difference)
        model.Add(positive <= difference + n_max * (1 - sign))
        model.Add(positive <= t_max * sign)
        excess_vars.append(positive)

    total_excess = model.NewIntVar(0, len(system.triangles), "total_excess")
    model.Add(total_excess == sum(excess_vars))
    margin = model.NewIntVar(-len(values), len(system.triangles), "margin")
    model.Add(margin == total_excess - p_var)
    if require_failure:
        model.Add(margin >= 1)
    metadata = {
        "h": h,
        "p_min": p_min,
        "system": system,
        "holes": holes,
        "selected": selected,
        "p_var": p_var,
        "total_excess": total_excess,
        "margin": margin,
    }
    return model, metadata


def audit_subset(values: tuple[int, ...], h: int, b: int) -> dict[str, object]:
    scorer = load(f"p116_scorer_audit_{len(values)}_{b}", SCORER_PATH)
    sums = scorer.unordered_sum_map(values)
    differences = scorer.positive_differences(values)
    if not differences.isdisjoint(total + b for total in sums):
        raise AssertionError("literal hole failed")
    p = len(values)
    delta = (3 * p * p - p + 2) // 2 - h
    if delta <= 0:
        raise AssertionError(("positive defect", delta))
    system = scorer.fold_triangle_system(values, h)
    matching = system.hall_matching
    return {
        "B": list(values),
        "p": p,
        "h": h,
        "b": b,
        "delta": delta,
        "C_S": len(system.folds),
        "T_F": len(system.triangles),
        "positive_color_excess": system.positive_color_excess,
        "BC108_margin": system.positive_color_excess - p,
        "difference_hall_matching": matching,
        "difference_hall_deficit": system.positive_color_excess - matching,
        "sha256": hashlib.sha256(
            ",".join(map(str, values)).encode("ascii")
        ).hexdigest(),
    }


def solve_job(parent_index: int, values: tuple[int, ...], b: int, seconds: int):
    model, data = model_for(values, b, True)
    model.Maximize(data["margin"])
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    status = solver.Solve(model)
    result: dict[str, object] = {
        "parent_index": parent_index,
        "b": b,
        "parent_p": len(values),
        "h": data["h"],
        "positive_defect_min_p": data["p_min"],
        "parent_folds": len(data["system"].folds),
        "parent_triangles": len(data["system"].triangles),
        "hole_obstructions": len(data["holes"]),
        "status": solver.StatusName(status),
        "best_margin_bound": solver.BestObjectiveBound(),
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "witness": None,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return result
    subset = tuple(mark for mark in values if solver.Value(data["selected"][mark]))
    witness = audit_subset(subset, int(data["h"]), b)
    if int(witness["BC108_margin"]) <= 0:
        raise AssertionError(("solver returned nonwitness", witness))
    if int(witness["BC108_margin"]) != solver.Value(data["margin"]):
        raise AssertionError((witness, solver.Value(data["margin"])))
    result["witness"] = witness

    # A second exact model minimizes p among all falsifying subsets of this parent.
    minimum_model, minimum_data = model_for(values, b, True)
    minimum_model.Minimize(minimum_data["p_var"])
    minimum_solver = cp_model.CpSolver()
    minimum_solver.parameters.num_search_workers = 1
    minimum_solver.parameters.max_time_in_seconds = seconds
    minimum_status = minimum_solver.Solve(minimum_model)
    result["minimum_p_status"] = minimum_solver.StatusName(minimum_status)
    result["minimum_p_bound"] = minimum_solver.BestObjectiveBound()
    result["minimum_p_wall_time_seconds"] = minimum_solver.WallTime()
    if minimum_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        minimum_subset = tuple(
            mark for mark in values
            if minimum_solver.Value(minimum_data["selected"][mark])
        )
        result["minimum_p_witness"] = audit_subset(
            minimum_subset, int(minimum_data["h"]), b
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parents", type=int, nargs="+", default=list(DEFAULT_PARENTS)
    )
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    p86 = load("p86_subset_p116", P86_PATH)
    bases, manifests = p86.load_archives()
    parent_indices = sorted(set(args.parents))
    if any(index < 0 or index >= len(bases) for index in parent_indices):
        raise ValueError((parent_indices, len(bases)))
    rows = []
    for index in parent_indices:
        for b in (1, 2):
            rows.append(solve_job(index, bases[index].values, b, max(1, args.seconds)))
    witnesses = [row for row in rows if row.get("witness") is not None]
    payload = {
        "schema_version": 1,
        "arithmetic": "exact integer CP-SAT model; exact Python-integer witness audit",
        "parent_indices": parent_indices,
        "seconds_per_solve": max(1, args.seconds),
        "archive_manifest": manifests,
        "jobs": len(rows),
        "witness_jobs": len(witnesses),
        "smallest_witness": min(
            (
                row.get("minimum_p_witness") or row["witness"]
                for row in witnesses
            ),
            key=lambda row: (int(row["p"]), int(row["h"]), int(row["b"]), row["B"]),
            default=None,
        ),
        "results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "output": str(args.output),
        "jobs": len(rows),
        "witness_jobs": len(witnesses),
        "smallest_witness": payload["smallest_witness"],
        "statuses": [
            [row["parent_index"], row["b"], row["status"], row["best_margin_bound"]]
            for row in rows
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
