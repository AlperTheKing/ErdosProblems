"""Exact CP-SAT discovery solver for fully reflected Problem 864 sets.

For 0=x_0<...<x_{p-1}<theta/2, the reflected set

    X union (theta-X)

is admissible with exceptional sum theta exactly when the p^2 positive labels

    x_j-x_i, theta-x_i-x_j (i<j), theta-2*x_i

are pairwise distinct.  This script minimizes theta.  A FEASIBLE record is an
exact construction; only OPTIMAL certifies the minimum.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from ortools.sat.python import cp_model


def literal_check(points: list[int], theta: int) -> dict[str, object]:
    lower = sorted(points)
    reflected = sorted(set(lower) | {theta - x for x in lower})
    counts: Counter[int] = Counter()
    for i, a in enumerate(reflected):
        for b in reflected[i:]:
            counts[a + b] += 1
    repeated = sorted((s, m) for s, m in counts.items() if m >= 2)
    labels: list[int] = []
    p = len(lower)
    for i in range(p):
        labels.append(theta - 2 * lower[i])
        for j in range(i + 1, p):
            labels.append(lower[j] - lower[i])
            labels.append(theta - lower[i] - lower[j])
    return {
        "admissible": repeated == [(theta, p)],
        "repeated_sums": repeated,
        "labels_distinct": len(labels) == len(set(labels)) == p * p,
        "reflected_set": reflected,
    }


def solve(p: int, upper: int, seconds: float, workers: int) -> dict[str, object]:
    model = cp_model.CpModel()
    theta = model.new_int_var(p * p, upper, "theta")
    x = [model.new_int_var(0, upper // 2, f"x_{i}") for i in range(p)]
    model.add(x[0] == 0)
    for i in range(p - 1):
        model.add(x[i] < x[i + 1])
    model.add(2 * x[-1] < theta)

    labels = []
    for i in range(p):
        e = model.new_int_var(1, upper, f"e_{i}")
        model.add(e == theta - 2 * x[i])
        labels.append(e)
        for j in range(i + 1, p):
            d = model.new_int_var(1, upper, f"d_{i}_{j}")
            c = model.new_int_var(1, upper, f"c_{i}_{j}")
            model.add(d == x[j] - x[i])
            model.add(c == theta - x[i] - x[j])
            labels.extend((d, c))
    model.add_all_different(labels)
    model.minimize(theta)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 864
    solver.parameters.log_search_progress = False
    status = solver.solve(model)
    status_name = solver.status_name(status)
    record: dict[str, object] = {
        "p": p,
        "status": status_name,
        "workers": workers,
        "time_limit_seconds": seconds,
        "finite_optimum_certified": status == cp_model.OPTIMAL,
        "diagnostic_best_bound": solver.best_objective_bound,
        "wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        points = [solver.value(v) for v in x]
        center = solver.value(theta)
        check = literal_check(points, center)
        if not check["admissible"] or not check["labels_distinct"]:
            raise RuntimeError("internal literal verification failed")
        record.update(
            {
                "theta": center,
                "points": points,
                "theta_over_p2": f"{center}/{p*p}",
                **check,
            }
        )
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--upper", type=int)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()
    if args.p < 1:
        parser.error("--p must be positive")
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")
    upper = args.upper if args.upper is not None else 4 * args.p * args.p
    if upper < args.p * args.p:
        parser.error("--upper must be at least p^2")
    print(json.dumps(solve(args.p, upper, args.seconds, args.workers), sort_keys=True))


if __name__ == "__main__":
    main()
