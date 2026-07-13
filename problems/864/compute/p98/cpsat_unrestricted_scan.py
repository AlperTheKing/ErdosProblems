#!/usr/bin/env python3
"""Exact unrestricted endpoint-Sidon search and gate recovery for P98."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from ortools.sat.python import cp_model

from component_core import correction_V, positive_differences, score, unordered_sum_map


def has_hole(values: tuple[int, ...], b: int) -> bool:
    sums = unordered_sum_map(values)
    differences = positive_differences(values)
    return differences.isdisjoint(total + b for total in sums)


def recovery_data(values: tuple[int, ...], raw: dict[str, object]) -> dict[str, object]:
    p = len(values)
    H = values[-1]
    h0 = H + 1
    baseline = (3 * p * p - p + 2) // 2
    direct_defect = baseline - h0
    direct_holes = [b for b in (1, 2) if has_hole(values, b)]
    full_recoveries = []
    translation_tests = 0
    max_gamma = min(H - 1, baseline - H - 2)
    for gamma in range(max(0, max_gamma + 1)):
        translated = tuple(value + gamma for value in values)
        h = H + gamma + 1
        translated_row = score(translated, h)
        translation_tests += 2
        for b in (1, 2):
            if not has_hole(translated, b):
                continue
            if int(translated_row["maximum_component_excess"]) > 0:
                full_recoveries.append({
                    **translated_row,
                    "b": b,
                    "delta": baseline - h,
                    "transform": f"translation gamma={gamma}",
                })

    q_lift_tests = 0
    max_q = (baseline - 1) // h0
    for q in range(2, max_q + 1):
        lifted = tuple(q * value + q - 1 for value in values)
        h = q * h0
        lifted_row = score(lifted, h)
        q_lift_tests += 1
        if int(lifted_row["maximum_component_excess"]) != int(raw["maximum_component_excess"]):
            raise AssertionError(("q-lift changed component excess", q, raw, lifted_row))
        if not has_hole(lifted, 1):
            raise AssertionError(("q-lift lost automatic b=1 hole", q))
        full_recoveries.append({
            **lifted_row,
            "b": 1,
            "delta": baseline - h,
            "transform": f"endpoint affine q-lift q={q}",
        })
    return {
        "direct_delta": direct_defect,
        "direct_positive_defect": direct_defect > 0,
        "direct_hole_phases": direct_holes,
        "translation_phase_tests": translation_tests,
        "q_lifts_tested": q_lift_tests,
        "full_recovery_count": len(full_recoveries),
        "first_full_recovery": full_recoveries[0] if full_recoveries else None,
    }


class Callback(cp_model.CpSolverSolutionCallback):
    def __init__(self, selected, H: int):
        super().__init__()
        self.selected = selected
        self.H = H
        self.solutions = 0
        self.with_folds = 0
        self.with_triangles = 0
        self.component_failures = 0
        self.global_failures = 0
        self.recoverable_failures = 0
        self.tight_components = 0
        self.smallest_component_failure = None
        self.smallest_global_failure = None
        self.largest_tight = None
        self.corrected_tests = 0
        self.corrected_failures = 0
        self.maximum_corrected_excess = None
        self.maximum_corrected_excess_row = None

    @staticmethod
    def failure_key(row):
        return (int(row["p"]), int(row["h"]), row["B"])

    @staticmethod
    def tight_key(row):
        return (
            int(row["maximum_component_triangles"]),
            int(row["T_F"]),
            -int(row["p"]),
        )

    def on_solution_callback(self):
        values = tuple(index for index, var in enumerate(self.selected) if self.Value(var))
        row = score(values, self.H + 1)
        self.solutions += 1
        if int(row["C_S"]):
            self.with_folds += 1
        if int(row["T_F"]):
            self.with_triangles += 1
        if (
            int(row["maximum_component_excess"]) == 0
            and int(row["maximum_component_triangles"]) > 0
        ):
            self.tight_components += 1
            if self.largest_tight is None or self.tight_key(row) > self.tight_key(self.largest_tight):
                self.largest_tight = row
        if int(row["maximum_component_excess"]) > 0:
            self.component_failures += 1
            recovery = recovery_data(values, row)
            retained = {**row, "recovery": recovery}
            if int(recovery["full_recovery_count"]) > 0:
                self.recoverable_failures += 1
            if (
                self.smallest_component_failure is None
                or self.failure_key(retained) < self.failure_key(self.smallest_component_failure)
            ):
                self.smallest_component_failure = retained
        if int(row["T_F"]) > int(row["C_S"]):
            self.global_failures += 1
            retained = {**row, "recovery": recovery_data(values, row)}
            if (
                self.smallest_global_failure is None
                or self.failure_key(retained) < self.failure_key(self.smallest_global_failure)
            ):
                self.smallest_global_failure = retained
        for b in (1, 2):
            self.corrected_tests += 1
            correction = correction_V(values, self.H + 1, b)
            excess = int(row["T_F"]) - int(row["C_S"]) - correction
            if excess > 0:
                self.corrected_failures += 1
            if self.maximum_corrected_excess is None or excess > self.maximum_corrected_excess:
                self.maximum_corrected_excess = excess
                self.maximum_corrected_excess_row = {
                    **row, "b": b, "V_b": correction, "corrected_excess": excess,
                }


def solve(H: int, time_limit: float) -> dict[str, object]:
    model = cp_model.CpModel()
    selected = [model.NewBoolVar(f"x_{value}") for value in range(H + 1)]
    model.Add(selected[H] == 1)
    model.Add(sum(selected) >= 3)
    by_sum = [[] for _ in range(2 * H + 1)]
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
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = time_limit
    callback = Callback(selected, H)
    status = solver.SearchForAllSolutions(model, callback)
    return {
        "H": H,
        "status": solver.StatusName(status),
        "complete": status == cp_model.OPTIMAL,
        "solutions": callback.solutions,
        "with_folds": callback.with_folds,
        "with_triangles": callback.with_triangles,
        "component_failures": callback.component_failures,
        "global_failures": callback.global_failures,
        "recoverable_component_failures": callback.recoverable_failures,
        "tight_component_rows": callback.tight_components,
        "smallest_component_failure": callback.smallest_component_failure,
        "smallest_global_failure": callback.smallest_global_failure,
        "largest_tight": callback.largest_tight,
        "corrected_tests": callback.corrected_tests,
        "corrected_failures": callback.corrected_failures,
        "maximum_corrected_excess": callback.maximum_corrected_excess,
        "maximum_corrected_excess_row": callback.maximum_corrected_excess_row,
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    }


def solve_job(job: tuple[int, float]) -> dict[str, object]:
    return solve(*job)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-H", type=int, default=31)
    parser.add_argument("--max-H", type=int, default=36)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--time-limit", type=float, default=1800.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.min_H < 31 or args.max_H < args.min_H:
        raise ValueError("unrestricted P98 domain begins beyond width 30")
    workers = max(1, min(16, args.workers))
    jobs = [(H, args.time_limit) for H in range(args.min_H, args.max_H + 1)]
    if workers == 1:
        rows = [solve(*job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(solve_job, jobs, chunksize=1))
    payload = {
        "schema_version": 1,
        "arithmetic": "CP-SAT exhaustive Boolean enumeration; exact integer scoring and gate recovery",
        "domain": f"all endpoint Sidon B subset [0,H] with H in B, |B|>=3, {args.min_H}<=H<={args.max_H}; no hole or defect gate",
        "workers": workers,
        "all_jobs_complete": all(bool(row["complete"]) for row in rows),
        "solutions": sum(int(row["solutions"]) for row in rows),
        "component_failures": sum(int(row["component_failures"]) for row in rows),
        "global_failures": sum(int(row["global_failures"]) for row in rows),
        "recoverable_component_failures": sum(int(row["recoverable_component_failures"]) for row in rows),
        "tight_component_rows": sum(int(row["tight_component_rows"]) for row in rows),
        "corrected_tests": sum(int(row["corrected_tests"]) for row in rows),
        "corrected_failures": sum(int(row["corrected_failures"]) for row in rows),
        "jobs": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["all_jobs_complete"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
