#!/usr/bin/env python3
"""CP-SAT enumeration of full-gate endpoint sets beyond P96's width 30."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from ortools.sat.python import cp_model

from component_core import audit


def minimum_order(h: int) -> int:
    p = 1
    while (3 * p * p - p + 2) // 2 <= h:
        p += 1
    return p


class AuditCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, selected, h: int, b: int):
        super().__init__()
        self.selected = selected
        self.h = h
        self.b = b
        self.solutions = 0
        self.nonzero = 0
        self.tight_rows = 0
        self.failures = 0
        self.best = None
        self.largest_tight = None

    @staticmethod
    def key(row):
        return (
            int(row["maximum_component_excess"]),
            int(row["maximum_component_triangles"]),
            -int(row["maximum_component_folds"]),
            int(row["T_F"]),
        )

    def on_solution_callback(self):
        values = tuple(index for index, var in enumerate(self.selected) if self.Value(var))
        row = audit(values, self.h, self.b)
        self.solutions += 1
        if int(row["T_F"]) > 0:
            self.nonzero += 1
        excess = int(row["maximum_component_excess"])
        if excess > 0:
            self.failures += 1
        if excess == 0 and int(row["maximum_component_triangles"]) > 0:
            self.tight_rows += 1
            if self.largest_tight is None or self.key(row) > self.key(self.largest_tight):
                self.largest_tight = row
        if self.best is None or self.key(row) > self.key(self.best):
            self.best = row


def solve_job(job: tuple[int, int, float]) -> dict[str, object]:
    H, b, time_limit = job
    h = H + 1
    model = cp_model.CpModel()
    selected = [model.NewBoolVar(f"x_{value}") for value in range(H + 1)]
    model.Add(selected[H] == 1)
    model.Add(sum(selected) >= minimum_order(h))

    by_sum: list[list[cp_model.IntVar]] = [[] for _ in range(2 * H + 1)]
    for left in range(H + 1):
        for right in range(left, H + 1):
            pair = model.NewBoolVar(f"p_{left}_{right}")
            model.Add(pair <= selected[left])
            model.Add(pair <= selected[right])
            if left == right:
                model.Add(pair == selected[left])
            else:
                model.Add(pair >= selected[left] + selected[right] - 1)
            by_sum[left + right].append(pair)
    for pairs in by_sum:
        model.Add(sum(pairs) <= 1)

    hole_constraints = 0
    for x in range(H + 1):
        for y in range(x, H + 1):
            for z in range(y, H + 1):
                w = x + y + z + b
                if w > H:
                    break
                support = sorted(set((x, y, z, w)))
                model.Add(sum(selected[value] for value in support) <= len(support) - 1)
                hole_constraints += 1

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = time_limit
    callback = AuditCallback(selected, h, b)
    status = solver.SearchForAllSolutions(model, callback)
    return {
        "H": H,
        "h": h,
        "b": b,
        "minimum_p": minimum_order(h),
        "hole_constraints": hole_constraints,
        "status": solver.StatusName(status),
        "complete": status == cp_model.OPTIMAL,
        "solutions": callback.solutions,
        "nonzero_triangle_rows": callback.nonzero,
        "tight_rows": callback.tight_rows,
        "failures": callback.failures,
        "best": callback.best,
        "largest_tight": callback.largest_tight,
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-H", type=int, default=31)
    parser.add_argument("--max-H", type=int, default=32)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--time-limit", type=float, default=1800.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.min_H < 31 or args.max_H < args.min_H:
        raise ValueError("P98 domain must begin beyond P96 width 30")
    workers = max(1, min(16, args.workers))
    jobs = [
        (H, b, args.time_limit)
        for H in range(args.min_H, args.max_H + 1)
        for b in (1, 2)
    ]
    if workers == 1:
        rows = [solve_job(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(solve_job, jobs, chunksize=1))
    payload = {
        "schema_version": 1,
        "arithmetic": "CP-SAT Boolean feasibility; exact Python integer audit of every solution",
        "domain": f"all endpoint-normalized sets B subset [0,H], {args.min_H}<=H<={args.max_H}, b in {{1,2}}, under Sidon, positive-defect, literal-hole gates",
        "workers": workers,
        "all_jobs_complete": all(bool(row["complete"]) for row in rows),
        "solutions": sum(int(row["solutions"]) for row in rows),
        "failures": sum(int(row["failures"]) for row in rows),
        "tight_rows": sum(int(row["tight_rows"]) for row in rows),
        "jobs": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["all_jobs_complete"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
