#!/usr/bin/env python3
"""Exact minimum-deletion literal-hole subset search around the P88 near-falsifier."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model

from bc108_core import hole_conflicts, structure_score
from search_bc108 import canonical_bytes, sha256_file


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def better(row, old):
    if old is None:
        return row
    key = (row["bc108_residual"], row["positive_color_excess"], row["T_F"], row["B"])
    old_key = (old["bc108_residual"], old["positive_color_excess"], old["T_F"], old["B"])
    return row if key > old_key else old


class AuditCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, values, variables, h, b):
        super().__init__()
        self.values = values
        self.variables = variables
        self.h = h
        self.b = b
        self.solutions = 0
        self.failures = 0
        self.worst = None
        self.failure = None
        self.digest = hashlib.sha256()

    def on_solution_callback(self):
        deleted = tuple(
            value for value, variable in zip(self.values, self.variables)
            if self.Value(variable)
        )
        retained = tuple(value for value in self.values if value not in set(deleted))
        row = structure_score(retained, self.h)
        row = {
            "B": row["B"], "p": row["p"], "h": row["h"], "b": self.b,
            "delta": row["delta"], "C_S": row["C_S"], "T_F": row["T_F"],
            "positive_color_excess": row["positive_color_excess"],
            "bc108_residual": row["bc108_residual"],
            "deleted": list(deleted), "colors": row["colors"],
        }
        if int(row["delta"]) <= 0:
            raise AssertionError(("nonpositive subset", row))
        self.solutions += 1
        self.digest.update(canonical_bytes(row))
        self.worst = better(row, self.worst)
        if int(row["bc108_residual"]) > 0:
            self.failures += 1
            self.failure = better(row, self.failure)


def run_phase(values, h, b):
    conflicts = hole_conflicts(values, b)
    index = {value: i for i, value in enumerate(values)}
    p = len(values)
    max_deletions = max(
        deletion_count
        for deletion_count in range(p)
        if (3 * (p - deletion_count) ** 2 - (p - deletion_count) + 2) // 2 > h
    )
    summaries = []
    minimum = None
    for deletion_count in range(max_deletions + 1):
        model = cp_model.CpModel()
        deleted = [model.NewBoolVar(f"deleted_{i}") for i in range(p)]
        for conflict in conflicts:
            support = set(conflict["sum_pair"]) | set(conflict["difference_pair"])
            model.Add(sum(deleted[index[value]] for value in support) >= 1)
        model.Add(deleted[-1] == 0)
        model.Add(sum(deleted) == deletion_count)
        callback = AuditCallback(values, deleted, h, b)
        solver = cp_model.CpSolver()
        solver.parameters.enumerate_all_solutions = True
        solver.parameters.num_search_workers = 1
        status = solver.Solve(model, callback)
        if callback.solutions and minimum is None:
            minimum = deletion_count
        summaries.append({
            "deletions": deletion_count,
            "solver_status": solver.StatusName(status),
            "solutions": callback.solutions,
            "bc108_failures": callback.failures,
            "solution_sha256": callback.digest.hexdigest(),
            "worst": callback.worst,
            "failure": callback.failure,
        })
    return {
        "b": b,
        "conflicts": len(conflicts),
        "max_positive_defect_deletions": max_deletions,
        "minimum_literal_hole_deletions_with_max_endpoint_retained": minimum,
        "by_deletion_count": summaries,
        "failures": sum(row["bc108_failures"] for row in summaries),
        "failure": next((row["failure"] for row in summaries if row["failure"]), None),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    p88 = load("p88_p116_subset", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")
    values = tuple(p88.B)
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers; exhaustive CP-SAT Boolean enumeration",
        "domain": (
            "all subsets of P88 retaining max(B), separately for b=1,2, "
            "with positive defect and literal-hole constraints"
        ),
        "B": list(values),
        "h": int(p88.H),
        "source_manifest": {
            "P88": sha256_file(ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py"),
            "bc108_core.py": sha256_file(Path(__file__).with_name("bc108_core.py")),
            "search_p88_hole_subsets.py": sha256_file(Path(__file__)),
        },
        "phases": [run_phase(values, int(p88.H), b) for b in (1, 2)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "phases": [
            {
                "b": row["b"], "conflicts": row["conflicts"],
                "max_deletions": row["max_positive_defect_deletions"],
                "minimum_hole_deletions": row["minimum_literal_hole_deletions_with_max_endpoint_retained"],
                "solutions": sum(x["solutions"] for x in row["by_deletion_count"]),
                "failures": row["failures"],
            }
            for row in result["phases"]
        ]
    }, indent=2))


if __name__ == "__main__":
    main()
