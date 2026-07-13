"""Exact CP-SAT feasibility gate for a prescribed signed-ruler length cap."""

from __future__ import annotations

import argparse
import json

from ortools.sat.python import cp_model

from solve_signed_ruler import literal_check


def find(p: int, cap: int, seconds: float, workers: int, seed: int) -> dict[str, object]:
    model = cp_model.CpModel()
    theta = model.new_int_var(p * p, cap, "theta")
    x = [model.new_int_var(0, cap // 2, f"x_{i}") for i in range(p)]
    model.add(x[0] == 0)
    for i in range(p - 1):
        model.add(x[i] < x[i + 1])
    model.add(2 * x[-1] < theta)

    labels = []
    for i in range(p):
        diagonal = model.new_int_var(1, cap, f"e_{i}")
        model.add(diagonal == theta - 2 * x[i])
        labels.append(diagonal)
        for j in range(i + 1, p):
            difference = model.new_int_var(1, cap, f"d_{i}_{j}")
            shifted_sum = model.new_int_var(1, cap, f"c_{i}_{j}")
            model.add(difference == x[j] - x[i])
            model.add(shifted_sum == theta - x[i] - x[j])
            labels.extend((difference, shifted_sum))
    model.add_all_different(labels)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.log_search_progress = False
    status = solver.solve(model)
    record: dict[str, object] = {
        "p": p,
        "cap": cap,
        "status": solver.status_name(status),
        "workers": workers,
        "seed": seed,
        "time_limit_seconds": seconds,
        "wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "infeasibility_certified": status == cp_model.INFEASIBLE,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        points = [solver.value(v) for v in x]
        center = solver.value(theta)
        check = literal_check(points, center)
        if not check["admissible"] or not check["labels_distinct"]:
            raise RuntimeError("literal verification failed")
        record.update({"theta": center, "points": points, **check})
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--cap", type=int)
    parser.add_argument("--ratio-num", type=int, default=2)
    parser.add_argument("--ratio-den", type=int, default=1)
    parser.add_argument("--seconds", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.p < 1 or args.ratio_num < 1 or args.ratio_den < 1:
        parser.error("positive p and ratio required")
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")
    cap = args.cap
    if cap is None:
        cap = args.ratio_num * args.p * args.p // args.ratio_den
    if cap < args.p * args.p:
        parser.error("cap must be at least p^2")
    seed = args.seed if args.seed is not None else 864 + args.p + cap
    print(json.dumps(find(args.p, cap, args.seconds, args.workers, seed), sort_keys=True))


if __name__ == "__main__":
    main()
