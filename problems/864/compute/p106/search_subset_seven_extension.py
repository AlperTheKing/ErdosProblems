#!/usr/bin/env python3
"""Solve exact seven-extension models on deterministic candidate subsets."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106s = load("p106_subset_audit", ROOT / "problems/864/compute/p106/search_positive_defect_rm_falsifier.py")
p106m = load("p106_subset_mutation", ROOT / "problems/864/compute/p106/scan_source_mutations.py")
p106l = load("p106_subset_lazy", ROOT / "problems/864/compute/p106/lazy_full_parent_extension.py")


def model_for_subset(base, candidates):
    model = cp_model.CpModel()
    variables = [model.NewBoolVar(f"x_{value}") for value in candidates]
    model.Add(sum(variables) == 7)
    differences = {right - left for i, left in enumerate(base) for right in base[i + 1:]}
    fixed_sums = {left + right for i, left in enumerate(base) for right in base[i:]}
    for i, left in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            right = candidates[j]
            if right - left in differences or left + right in fixed_sums:
                model.Add(variables[i] + variables[j] <= 1)
    return model, variables


def solve_subset(base, h, candidates, time_limit):
    model, variables = model_for_subset(base, candidates)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 16
    solver.parameters.max_time_in_seconds = time_limit
    cuts = 0
    while True:
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return solver.StatusName(status), cuts, None
        additions = tuple(
            value for value, variable in zip(candidates, variables)
            if solver.Value(variable)
        )
        collision = p106l.collision_support(additions)
        if collision is None:
            values = tuple(sorted(base + additions))
            assert p106m.is_sidon(values)
            return solver.StatusName(status), cuts, additions
        model.Add(sum(variables[candidates.index(additions[i])] for i in collision) <= len(collision) - 1)
        cuts += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--subset-size", type=int, default=300)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    parent = data["full_P88_q2_lift"]
    base, h = tuple(parent["B"]), int(parent["h"])
    all_candidates = [
        row["insertion"]
        for row in json.loads((ROOT / "problems/864/compute/p106/full_parent_insertions.json").read_text())["preserving_rows"]
    ]
    rng = random.Random(106)
    trial_rows = []
    witness = None
    for trial in range(args.trials):
        candidates = sorted(rng.sample(all_candidates, min(args.subset_size, len(all_candidates))))
        status, cuts, additions = solve_subset(base, h, candidates, args.time_limit)
        trial_rows.append({"trial": trial, "status": status, "lazy_cuts": cuts, "found_extension": additions is not None})
        if additions is None:
            continue
        values = tuple(sorted(base + additions))
        row = p106s.audit(values, h, 1)
        p = len(values)
        retained = {
            "B": values, "additions": additions,
            "p": p, "h": h, "b": 1,
            "delta": (3 * p * p - p + 2) // 2 - h,
            "sha256": hashlib.sha256(",".join(map(str, values)).encode("ascii")).hexdigest(),
            **row,
        }
        if row["RM97_failure"]:
            witness = retained
            break
    result = {
        "schema_version": 1,
        "candidate_pool": len(all_candidates),
        "subset_size": args.subset_size,
        "trials_requested": args.trials,
        "trial_rows": trial_rows,
        "positive_defect_RM97_witness": witness,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    summary = dict(result)
    if witness is not None:
        summary["positive_defect_RM97_witness"] = {
            key: value for key, value in witness.items() if key != "B"
        }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
