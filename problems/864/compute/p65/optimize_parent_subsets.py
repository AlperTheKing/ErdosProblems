#!/usr/bin/env python3
"""Exact CP-SAT subset audit around the P53 26-mark fold falsifier.

For each relevant translation and b in {1,2}, maximize C_S-2|B| over
all subsets retaining the top endpoint, subject to positive defect and the
literal condition -b notin 3B-B.  Every collision and every repeated-variable
hole relation is encoded as a finite Boolean constraint.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from itertools import combinations_with_replacement
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
AUDIT_SCRIPT = ROOT / "problems/864/compute/p65/search_hole_restricted_folds.py"
PARENT = (
    0, 1, 33, 83, 104, 110, 124, 163, 185, 200, 203, 249, 251,
    258, 314, 318, 343, 356, 386, 430, 440, 456, 464, 475, 487, 492,
)


def load_audit_module():
    spec = importlib.util.spec_from_file_location("p65_audit", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(AUDIT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sum_pairs(values: tuple[int, ...]) -> dict[int, tuple[int, int]]:
    out = {}
    for i, x in enumerate(values):
        for j in range(i, len(values)):
            y = values[j]
            s = x + y
            if s in out:
                raise AssertionError(("parent is not Sidon", s, out[s], (i, j)))
            out[s] = (i, j)
    return out


def collision_hyperedges(values: tuple[int, ...], h: int) -> list[tuple[int, ...]]:
    sums = sum_pairs(values)
    edges = []
    for low, pair0 in sums.items():
        pair1 = sums.get(low + h)
        if pair1 is not None:
            edges.append(tuple(sorted(set(pair0 + pair1))))
    return edges


def hole_hyperedges(base: tuple[int, ...], gamma: int, b: int) -> list[tuple[int, ...]]:
    values = tuple(gamma + z for z in base)
    index = {x: i for i, x in enumerate(values)}
    forbidden = set()
    for i, j, k in combinations_with_replacement(range(len(values)), 3):
        w = values[i] + values[j] + values[k] + b
        ell = index.get(w)
        if ell is not None:
            forbidden.add(tuple(sorted({i, j, k, ell})))
    return sorted(forbidden)


def minimum_positive_delta_cardinality(h: int) -> int:
    p = 1
    while (3 * p * p - p + 2) // 2 <= h:
        p += 1
    return p


def solve_universe(
    base_values: tuple[int, ...], gamma: int, b: int, seconds: float, workers: int,
) -> dict[str, object]:
    h = base_values[-1] + gamma + 1
    p_min = minimum_positive_delta_cardinality(h)
    collisions = collision_hyperedges(base_values, h)
    full_upper = len(collisions) - 2 * p_min
    summary = {
        "gamma": gamma, "h": h, "b": b, "p_min": p_min,
        "full_collision_count": len(collisions),
    }
    if p_min > len(base_values):
        return {**summary, "status": "SKIP_NO_POSITIVE_DELTA_SUBSET"}
    if len(collisions) <= 2 * p_min - 3:
        return {
            **summary, "status": "SKIP_MONOTONE_UPPER_BOUND",
            "objective_upper_bound": full_upper,
        }

    holes = hole_hyperedges(base_values, gamma, b)
    summary["hole_hyperedges"] = len(holes)

    model = cp_model.CpModel()
    selected = [model.new_bool_var(f"x_{i}") for i in range(len(base_values))]
    model.add(selected[-1] == 1)
    model.add(sum(selected) >= p_min)
    for edge in holes:
        model.add(sum(selected[i] for i in edge) <= len(edge) - 1)

    active = []
    for row, edge in enumerate(collisions):
        y = model.new_bool_var(f"fold_{row}")
        for i in edge:
            model.add(y <= selected[i])
        model.add(y >= sum(selected[i] for i in edge) - (len(edge) - 1))
        active.append(y)
    model.maximize(sum(active) - 2 * sum(selected))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.cp_model_presolve = True
    status = solver.solve(model)
    status_name = solver.status_name(status)
    row: dict[str, object] = {
        **summary, "status": status_name,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "best_objective_bound": solver.best_objective_bound,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = tuple(
            base_values[i] for i in range(len(base_values)) if solver.value(selected[i])
        )
        objective = int(round(solver.objective_value))
        row.update({
            "objective_C_S_minus_2p": objective,
            "Z_subset": list(chosen),
            "p": len(chosen),
            "C_S": sum(solver.value(y) for y in active),
        })
        audit = load_audit_module().fold_rows(chosen, gamma, b)
        if not audit["hole"] or audit["delta"] <= 0:
            raise AssertionError(("bad extracted solution", row, audit))
        if audit["C_S"] - 2 * audit["p"] != objective:
            raise AssertionError(("objective mismatch", row, audit))
        row["audit"] = audit
    return row


def solve_one(gamma: int, b: int, seconds: float, workers: int) -> dict[str, object]:
    return solve_universe(PARENT, gamma, b, seconds, workers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-gamma", type=int, default=491)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "problems/864/compute/p65/parent_subset_optimization.json",
    )
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")
    started = time.perf_counter()
    rows = []
    for gamma in range(args.max_gamma + 1):
        for b in (1, 2):
            rows.append(solve_one(gamma, b, args.seconds, args.workers))
    unresolved = [r for r in rows if r["status"] not in {
        "OPTIMAL", "INFEASIBLE", "SKIP_MONOTONE_UPPER_BOUND",
        "SKIP_NO_POSITIVE_DELTA_SUBSET",
    }]
    optimized = [r for r in rows if r["status"] == "OPTIMAL"]
    falsifiers = [r for r in optimized if int(r["objective_C_S_minus_2p"]) >= -2]
    output = {
        "schema_version": 1, "arithmetic": "exact integer CP-SAT",
        "domain": (
            "all subsets of the normalized P53 26-mark parent retaining its "
            f"top endpoint, gamma=0..{args.max_gamma}, b in {{1,2}}"
        ),
        "parent": list(PARENT), "rows": rows,
        "status_counts": dict(sorted(__import__("collections").Counter(
            str(r["status"]) for r in rows
        ).items())),
        "unresolved_count": len(unresolved), "unresolved": unresolved,
        "falsifier_count": len(falsifiers), "falsifiers": falsifiers,
        "maximum_objective": max(
            (int(r["objective_C_S_minus_2p"]) for r in optimized), default=None
        ),
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "status_counts": output["status_counts"],
        "unresolved_count": output["unresolved_count"],
        "falsifier_count": output["falsifier_count"],
        "maximum_objective": output["maximum_objective"],
        "elapsed_seconds": output["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
