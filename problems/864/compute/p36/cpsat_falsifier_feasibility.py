#!/usr/bin/env python3
"""Exact CP-SAT decision search for a positive C20 or LG33 margin."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from ortools.sat.python import cp_model

import cpsat_interval_search
from interval_gate_search import classify, profile


_linear_sum = cp_model.LinearExpr.sum
cp_model.LinearExpr.sum = staticmethod(lambda terms: _linear_sum(list(terms)))


def solve(
    n: int,
    objective: str,
    workers: int,
    time_limit: float,
    log_search: bool,
) -> dict[str, Any]:
    model, variables = cpsat_interval_search.build_model(n, objective)
    model.ClearObjective()
    h = int(variables["H"])
    k = variables["k"]
    m = variables["M"]
    w = variables["W"]
    if objective == "c20":
        s = variables["S"]
        product = model.NewIntVar(0, (n + h - 1) * (2 * h * h - h), "decision_MS")
        model.AddMultiplicationEquality(product, [m, s])
        margin = (
            6 * product
            - 8 * n * h * h
            - 9 * h * h * h
            - 9 * n * (k - 1) * h
        )
    else:
        z = w - h * (h - 1) // 2
        g = n + h - 1 - m
        margin = (
            8 * n * z
            - 12 * h * h * g
            + 3 * h * h * h
            - 12 * h * h
            - 9 * n * (k - 1) * h
        )
    model.Add(margin >= 1)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 361864
    solver.parameters.log_search_progress = log_search
    start = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - start
    result: dict[str, Any] = {
        "N": n,
        "H": h,
        "target": f"{objective}_margin >= 1",
        "status": solver.StatusName(status),
        "workers": workers,
        "time_limit_seconds": time_limit,
        "wall_seconds": elapsed,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "no_falsifier_certified": status == cp_model.INFEASIBLE,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        a = tuple(
            index
            for index, variable in enumerate(variables["selected"])
            if solver.Value(variable)
        )
        structure = classify(a)
        direct = profile(a, n)
        if not structure.admissible:
            raise AssertionError("decision solver returned a non-admissible set")
        margin_key = "c20_margin" if objective == "c20" else "lg33_margin"
        if int(direct[margin_key]) <= 0:
            raise AssertionError("decision solver witness does not falsify target")
        result.update(direct)
        result["repeated_sums"] = list(structure.repeated_sums)
        result["falsifier_margin"] = int(direct[margin_key])
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
    result = solve(
        args.n,
        args.objective,
        args.workers,
        args.time_limit,
        args.log_search,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
