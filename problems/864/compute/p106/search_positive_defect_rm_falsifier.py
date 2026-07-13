#!/usr/bin/env python3
"""Search exact ten-mark Sidon extensions of the lifted P105 RM witness."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106 = load("p106_extension_windows", ROOT / "problems/864/compute/p106/analyze_minimal_hall_interval.py")
p106m = load("p106_extension_match", ROOT / "problems/864/compute/p106/scan_source_mutations.py")


def audit(values, h, b):
    folds, triangles, intervals, slots, differences = p106.residual_system(values, h, b)
    matched = p106m.greedy_match(intervals, slots)
    sums = {
        left + right
        for i, left in enumerate(values)
        for right in values[i:]
    }
    literal_hole = differences.isdisjoint(total + b for total in sums)
    return {
        "C_S": len(folds), "T_F": len(triangles),
        "V_b": len(slots) - 2 * len(folds),
        "intervals": len(intervals), "slots": len(slots),
        "matched": matched, "RM97_failure": matched != len(intervals),
        "literal_hole": literal_hole,
    }


class Callback(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, candidates, base, h, b, max_solutions):
        super().__init__()
        self.variables = variables
        self.candidates = candidates
        self.base = base
        self.h = h
        self.b = b
        self.max_solutions = max_solutions
        self.solutions = 0
        self.witness = None
        self.best = None

    def on_solution_callback(self):
        additions = tuple(
            value for value, variable in zip(self.candidates, self.variables)
            if self.Value(variable)
        )
        values = tuple(sorted(self.base + additions))
        row = audit(values, self.h, self.b)
        self.solutions += 1
        retained = {"additions": additions, "B": values, **row}
        key = (row["intervals"] - row["matched"], row["intervals"] - row["slots"], row["T_F"])
        if self.best is None or key > self.best[0]:
            self.best = (key, retained)
        if row["RM97_failure"]:
            self.witness = retained
            self.StopSearch()
        elif self.solutions >= self.max_solutions:
            self.StopSearch()


def build_model(base, candidates, additions, phase_labels):
    model = cp_model.CpModel()
    selected = [model.NewBoolVar(f"x_{value}") for value in candidates]
    model.Add(sum(selected) == additions)

    occurrences = defaultdict(list)
    fixed_sums = {
        left + right for i, left in enumerate(base) for right in base[i:]
    }
    for i, value in enumerate(candidates):
        for mark in base:
            occurrences[value + mark].append(selected[i])
        occurrences[2 * value].append(selected[i])
    for i, left in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            right = candidates[j]
            pair = model.NewBoolVar(f"p_{left}_{right}")
            model.Add(pair <= selected[i])
            model.Add(pair <= selected[j])
            model.Add(pair >= selected[i] + selected[j] - 1)
            if left + right in fixed_sums:
                model.Add(pair == 0)
            else:
                occurrences[left + right].append(pair)
            if right - left in phase_labels:
                model.Add(selected[i] + selected[j] <= 1)
    for variables in occurrences.values():
        if len(variables) > 1:
            model.Add(sum(variables) <= 1)
    return model, selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--additions", type=int, default=10)
    parser.add_argument("--max-solutions", type=int, default=1000)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    p105 = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    lifted = p105["subset_search"]["q2_lifted_witness"]
    base, h, b = tuple(lifted["B"]), int(lifted["h"]), 1
    mutation = json.loads((ROOT / "problems/864/compute/p106/lifted_mutations.json").read_text())
    candidates = sorted({
        int(row["transform"].split()[1])
        for row in mutation["failure_records"]
        if row["transform"].startswith("insert ")
    })
    phase_labels = {a + c + b for a, c, _u, _v in (tuple(row) for row in lifted["folds"])}
    model, selected = build_model(base, candidates, args.additions, phase_labels)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = args.time_limit
    solver.parameters.enumerate_all_solutions = True
    callback = Callback(selected, candidates, base, h, b, args.max_solutions)
    status = solver.Solve(model, callback)

    witness = callback.witness
    if witness is not None:
        values = witness["B"]
        p = len(values)
        witness.update({
            "p": p, "h": h, "b": b,
            "delta": (3 * p * p - p + 2) // 2 - h,
            "sha256": hashlib.sha256(",".join(map(str, values)).encode("ascii")).hexdigest(),
        })
    result = {
        "schema_version": 1,
        "arithmetic": "CP-SAT exact Sidon extension constraints; exact integer RM97 audit",
        "base_p": len(base), "h": h, "candidate_insertions": len(candidates),
        "requested_additions": args.additions,
        "status": solver.StatusName(status),
        "solutions_audited": callback.solutions,
        "RM97_witness": witness,
        "best_nonwitness": callback.best[1] if callback.best and witness is None else None,
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(), "conflicts": solver.NumConflicts(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    summary = dict(result)
    if witness is not None:
        summary["RM97_witness"] = {key: value for key, value in witness.items() if key != "B"}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
