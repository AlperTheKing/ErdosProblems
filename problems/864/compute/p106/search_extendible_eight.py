#!/usr/bin/env python3
"""Enumerate eight-addition RM witnesses and seek a p=67 completion."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106s = load("p106_extendible_search", ROOT / "problems/864/compute/p106/search_positive_defect_rm_falsifier.py")
p106m = load("p106_extendible_mutation", ROOT / "problems/864/compute/p106/scan_source_mutations.py")


class Callback(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, candidates, base, h, max_solutions):
        super().__init__()
        self.variables = variables
        self.candidates = candidates
        self.base = base
        self.h = h
        self.max_solutions = max_solutions
        self.solutions = 0
        self.rm_failures = 0
        self.max_insertions = -1
        self.max_row = None
        self.p67_tests = 0
        self.witness = None

    def on_solution_callback(self):
        additions = tuple(
            value for value, variable in zip(self.candidates, self.variables)
            if self.Value(variable)
        )
        seed = tuple(sorted(self.base + additions))
        row = p106s.audit(seed, self.h, 1)
        self.solutions += 1
        if not row["RM97_failure"]:
            if self.solutions >= self.max_solutions:
                self.StopSearch()
            return
        self.rm_failures += 1
        insertions = list(p106m.individually_admissible_insertions(seed))
        if len(insertions) > self.max_insertions:
            self.max_insertions = len(insertions)
            self.max_row = {"additions": additions, "admissible_next": insertions[:100], **row}
        for i, left in enumerate(insertions):
            for right in insertions[i + 1:]:
                values = tuple(sorted(seed + (left, right)))
                if not p106m.is_sidon(values):
                    continue
                self.p67_tests += 1
                final = p106s.audit(values, self.h, 1)
                if not final["RM97_failure"]:
                    continue
                p = len(values)
                self.witness = {
                    "B": values, "eight_additions": additions,
                    "final_additions": [left, right],
                    "p": p, "h": self.h, "b": 1,
                    "delta": (3 * p * p - p + 2) // 2 - self.h,
                    "sha256": hashlib.sha256(",".join(map(str, values)).encode("ascii")).hexdigest(),
                    **final,
                }
                self.StopSearch()
                return
        if self.solutions >= self.max_solutions:
            self.StopSearch()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-solutions", type=int, default=500)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    p105 = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    lifted = p105["subset_search"]["q2_lifted_witness"]
    base, h = tuple(lifted["B"]), int(lifted["h"])
    mutation = json.loads((ROOT / "problems/864/compute/p106/lifted_mutations.json").read_text())
    candidates = sorted({
        int(row["transform"].split()[1])
        for row in mutation["failure_records"]
        if row["transform"].startswith("insert ")
    })
    phase_labels = {a + c + 1 for a, c, _u, _v in map(tuple, lifted["folds"])}
    model, variables = p106s.build_model(base, candidates, 8, phase_labels)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = args.time_limit
    solver.parameters.enumerate_all_solutions = True
    callback = Callback(variables, candidates, base, h, args.max_solutions)
    status = solver.Solve(model, callback)
    result = {
        "status": solver.StatusName(status),
        "solutions_audited": callback.solutions,
        "RM97_eight_addition_witnesses": callback.rm_failures,
        "maximum_admissible_next_insertions": callback.max_insertions,
        "maximum_extension_row": callback.max_row,
        "compatible_p67_completions_audited": callback.p67_tests,
        "positive_defect_RM97_witness": callback.witness,
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(), "conflicts": solver.NumConflicts(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    summary = dict(result)
    if callback.witness is not None:
        summary["positive_defect_RM97_witness"] = {
            key: value for key, value in callback.witness.items() if key != "B"
        }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
