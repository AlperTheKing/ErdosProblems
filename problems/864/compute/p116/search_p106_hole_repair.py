#!/usr/bin/env python3
"""Exact minimum-hole-repair and Sidon-completion search around P106."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ortools.sat.python import cp_model

from bc108_core import hole_conflicts, literal_hole, structure_score, valid_insertions
from search_bc108 import canonical_bytes, sha256_file


ROOT = Path(__file__).resolve().parents[4]


def minimum_hitting_sets(values, b):
    conflicts = hole_conflicts(values, b)
    index = {value: i for i, value in enumerate(values)}
    model = cp_model.CpModel()
    deleted = [model.NewBoolVar(f"deleted_{i}") for i in range(len(values))]
    for conflict in conflicts:
        support = set(conflict["sum_pair"]) | set(conflict["difference_pair"])
        model.Add(sum(deleted[index[value]] for value in support) >= 1)
    model.Minimize(sum(deleted))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 16
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        raise AssertionError(solver.StatusName(status))
    optimum = int(solver.ObjectiveValue())

    enum_model = cp_model.CpModel()
    enum_deleted = [enum_model.NewBoolVar(f"deleted_{i}") for i in range(len(values))]
    for conflict in conflicts:
        support = set(conflict["sum_pair"]) | set(conflict["difference_pair"])
        enum_model.Add(sum(enum_deleted[index[value]] for value in support) >= 1)
    enum_model.Add(sum(enum_deleted) == optimum)

    class Callback(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self.rows = []

        def on_solution_callback(self):
            self.rows.append(tuple(
                value for value, variable in zip(values, enum_deleted)
                if self.Value(variable)
            ))

    callback = Callback()
    enum_solver = cp_model.CpSolver()
    enum_solver.parameters.enumerate_all_solutions = True
    enum_solver.parameters.num_search_workers = 1
    enum_status = enum_solver.Solve(enum_model, callback)
    if enum_status != cp_model.OPTIMAL:
        raise AssertionError(enum_solver.StatusName(enum_status))
    return conflicts, optimum, sorted(callback.rows)


def completion_search(values, deleted_sets, b, ambient_max, target_p):
    digest = hashlib.sha256()
    nodes = 0
    maximum_p = 0
    target_completions = 0
    positive_rows = 0
    failures = 0
    best = None
    failure = None

    def retain(row, deleted, added):
        nonlocal best, failure, positive_rows, failures
        h = row[-1] + 1
        score = structure_score(row, h)
        compact = {
            "B": score["B"], "p": score["p"], "h": score["h"], "b": b,
            "delta": score["delta"], "C_S": score["C_S"], "T_F": score["T_F"],
            "positive_color_excess": score["positive_color_excess"],
            "bc108_residual": score["bc108_residual"],
            "deleted": list(deleted), "added": list(added),
        }
        if int(compact["delta"]) > 0:
            positive_rows += 1
            key = (
                compact["bc108_residual"], compact["positive_color_excess"],
                compact["T_F"], compact["p"], compact["B"],
            )
            if best is None or key > best[0]:
                best = (key, compact)
            if int(compact["bc108_residual"]) > 0:
                failures += 1
                if failure is None or key > failure[0]:
                    failure = (key, compact)

    def dfs(row, last, deleted, added):
        nonlocal nodes, maximum_p, target_completions
        nodes += 1
        maximum_p = max(maximum_p, len(row))
        digest.update(canonical_bytes([list(deleted), list(added), list(row)]))
        retain(row, deleted, added)
        if len(row) >= target_p:
            target_completions += 1
            return
        candidates = []
        for value in valid_insertions(row, 0, ambient_max):
            if value <= last:
                continue
            candidate = tuple(sorted(row + (value,)))
            if literal_hole(candidate, b):
                candidates.append(value)
        for value in candidates:
            dfs(tuple(sorted(row + (value,))), value, deleted, added + (value,))

    for deleted in deleted_sets:
        retained = tuple(value for value in values if value not in set(deleted))
        if not literal_hole(retained, b):
            raise AssertionError(("hitting set did not make a hole", b, deleted))
        dfs(retained, -1, deleted, ())
    return {
        "nodes": nodes,
        "node_sha256": digest.hexdigest(),
        "maximum_p": maximum_p,
        "target_p": target_p,
        "target_completions": target_completions,
        "positive_defect_rows": positive_rows,
        "bc108_failures": failures,
        "best_positive_row": None if best is None else best[1],
        "failure": None if failure is None else failure[1],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_path = ROOT / "problems/864/compute/p106/positive_rm97_falsifier_certificate.json"
    source = json.loads(source_path.read_text())
    values = tuple(source["B"])
    phases = []
    for b in (1, 2):
        conflicts, optimum, deleted_sets = minimum_hitting_sets(values, b)
        completion = completion_search(values, deleted_sets, b, values[-1], len(values))
        phases.append({
            "b": b,
            "initial_conflicts": len(conflicts),
            "minimum_deletions": optimum,
            "minimum_hitting_sets": [list(row) for row in deleted_sets],
            "minimum_hitting_set_count": len(deleted_sets),
            "completion": completion,
        })
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers; exact CP-SAT Boolean enumeration",
        "domain": (
            "all minimum-cardinality hole repairs of P106 for b=1,2, followed by "
            "all Sidon- and hole-preserving additions in [0,max(P106)] up to p=67"
        ),
        "source_B": list(values),
        "source_manifest": {
            "P106": sha256_file(source_path),
            "bc108_core.py": sha256_file(Path(__file__).with_name("bc108_core.py")),
            "search_p106_hole_repair.py": sha256_file(Path(__file__)),
        },
        "phases": phases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "phases": [
            {
                "b": row["b"], "conflicts": row["initial_conflicts"],
                "minimum_deletions": row["minimum_deletions"],
                "minimum_hitting_sets": row["minimum_hitting_set_count"],
                **row["completion"],
            }
            for row in phases
        ]
    }, indent=2))


if __name__ == "__main__":
    main()
