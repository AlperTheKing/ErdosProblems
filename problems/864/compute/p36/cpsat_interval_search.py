#!/usr/bin/env python3
"""Exact CP-SAT search for centered C20 or its linear LG33 bridge.

The model uses endpoint-normalized A subset [0,N-1].  Every unordered pair,
including every diagonal, is represented explicitly.  At most one sum label
may have multiplicity at least two.  The occupied thickening is modeled as
the OR of the selected H-intervals, and all objective values are integral.

LG33 has a linear objective.  C20 uses CP-SAT's exact integer multiplication
constraint for M*(H^2+2Z).  A returned witness is independently rebuilt by
the P36 direct checker; only status OPTIMAL is an exact finite certificate.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

from ortools.sat.python import cp_model

from interval_gate_search import ceil_cuberoot_square, classify, profile


def build_model(n: int, objective: str) -> tuple[cp_model.CpModel, dict[str, Any]]:
    if n < 2:
        raise ValueError("N must be at least two")
    if objective not in {"c20", "lg33"}:
        raise ValueError("unknown objective")
    h = ceil_cuberoot_square(n)
    model = cp_model.CpModel()
    selected = [model.NewBoolVar(f"x_{value}") for value in range(n)]
    model.Add(selected[0] == 1)
    model.Add(selected[n - 1] == 1)

    pair: dict[tuple[int, int], cp_model.IntVar] = {}
    by_sum: dict[int, list[cp_model.IntVar]] = {
        value: [] for value in range(2 * n - 1)
    }
    for left in range(n):
        pair[left, left] = selected[left]
        by_sum[2 * left].append(selected[left])
        for right in range(left + 1, n):
            both = model.NewBoolVar(f"pair_{left}_{right}")
            model.Add(both <= selected[left])
            model.Add(both <= selected[right])
            model.Add(both >= selected[left] + selected[right] - 1)
            pair[left, right] = both
            by_sum[left + right].append(both)

    repeated_flags = []
    for pair_sum, terms in by_sum.items():
        if len(terms) <= 1:
            continue
        repeated = model.NewBoolVar(f"repeated_sum_{pair_sum}")
        count = cp_model.LinearExpr.sum(terms)
        model.Add(count <= 1 + (len(terms) - 1) * repeated)
        model.Add(count >= 2 * repeated)
        repeated_flags.append(repeated)
    model.Add(cp_model.LinearExpr.sum(repeated_flags) <= 1)

    difference_counts: dict[int, cp_model.LinearExpr] = {}
    for difference in range(1, n):
        terms = [pair[left, left + difference] for left in range(n - difference)]
        count = cp_model.LinearExpr.sum(terms)
        model.Add(count <= 2)
        difference_counts[difference] = count

    occupied = []
    for point in range(-(h - 1), n):
        candidates = selected[max(0, point) : min(n - 1, point + h - 1) + 1]
        present = model.NewBoolVar(f"occupied_{point + h - 1}")
        for term in candidates:
            model.Add(present >= term)
        model.Add(present <= cp_model.LinearExpr.sum(candidates))
        occupied.append(present)

    k = model.NewIntVar(2, n, "k")
    model.Add(k == cp_model.LinearExpr.sum(selected))
    m = model.NewIntVar(h + 1, n + h - 1, "M")
    model.Add(m == cp_model.LinearExpr.sum(occupied))
    w = model.NewIntVar(0, h * (h - 1), "W")
    model.Add(
        w
        == cp_model.LinearExpr.sum(
            (h - difference) * difference_counts[difference]
            for difference in range(1, h)
        )
    )
    s = model.NewIntVar(h, 2 * h * h - h, "S")
    model.Add(s == h + 2 * w)

    if objective == "c20":
        product = model.NewIntVar(0, (n + h - 1) * (2 * h * h - h), "M_times_S")
        model.AddMultiplicationEquality(product, [m, s])
        objective_expr = (
            6 * product
            - 8 * n * h * h
            - 9 * h * h * h
            - 9 * n * (k - 1) * h
        )
    else:
        model.Add(3 * m >= 2 * n)
        z_expr = w - h * (h - 1) // 2
        g_expr = n + h - 1 - m
        objective_expr = (
            8 * n * z_expr
            - 12 * h * h * g_expr
            + 3 * h * h * h
            - 12 * h * h
            - 9 * n * (k - 1) * h
        )
    model.Maximize(objective_expr)
    return model, {
        "selected": selected,
        "k": k,
        "M": m,
        "W": w,
        "S": s,
        "H": h,
    }


def solve(
    n: int,
    objective: str,
    workers: int,
    time_limit: float,
    log_search: bool,
) -> dict[str, Any]:
    model, variables = build_model(n, objective)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 360864
    solver.parameters.log_search_progress = log_search
    start = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - start
    result: dict[str, Any] = {
        "N": n,
        "H": variables["H"],
        "objective_name": objective,
        "status": solver.StatusName(status),
        "workers": workers,
        "time_limit_seconds": time_limit,
        "wall_seconds": elapsed,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "finite_optimum_certified": status == cp_model.OPTIMAL,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        a = tuple(
            index
            for index, variable in enumerate(variables["selected"])
            if solver.Value(variable)
        )
        structure = classify(a)
        if not structure.admissible:
            raise AssertionError("CP-SAT returned a non-admissible set")
        direct = profile(a, n)
        objective_key = "c20_margin" if objective == "c20" else "lg33_margin"
        solver_objective = int(round(solver.ObjectiveValue()))
        if solver_objective != int(direct[objective_key]):
            raise AssertionError(
                f"objective mismatch: solver={solver_objective}, direct={direct[objective_key]}"
            )
        result.update(direct)
        result["repeated_sums"] = list(structure.repeated_sums)
        result["objective"] = solver_objective
        result["is_falsifier"] = solver_objective > 0
    if status != cp_model.UNKNOWN:
        bound = solver.BestObjectiveBound()
        if math.isfinite(bound):
            result["diagnostic_best_bound"] = bound
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--objective", choices=("c20", "lg33"), required=True)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--log-search", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise SystemExit("--workers must be in [1,64]")
    if args.time_limit <= 0:
        raise SystemExit("--time-limit must be positive")
    result = solve(
        args.n,
        args.objective,
        args.workers,
        args.time_limit,
        args.log_search,
    )
    text = json.dumps(result, sort_keys=True, separators=(",", ":"))
    print(text)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
