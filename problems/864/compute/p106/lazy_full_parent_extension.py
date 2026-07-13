#!/usr/bin/env python3
"""Exact lazy CP-SAT search for seven-mark extensions of lifted P88."""

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


p106s = load("p106_lazy_audit", ROOT / "problems/864/compute/p106/search_positive_defect_rm_falsifier.py")
p106m = load("p106_lazy_mutation", ROOT / "problems/864/compute/p106/scan_source_mutations.py")


def collision_support(values):
    by_sum = defaultdict(list)
    for i, left in enumerate(values):
        for j in range(i, len(values)):
            by_sum[left + values[j]].append((i, j))
    for pairs in by_sum.values():
        if len(pairs) <= 1:
            continue
        support = sorted({index for pair in pairs for index in pair})
        return support
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-valid-extensions", type=int, default=1000)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--allow-original-collisions", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    parent = data["full_P88_q2_lift"]
    base, h = tuple(parent["B"]), int(parent["h"])
    candidates = list(p106m.individually_admissible_insertions(base))
    phase_labels = {a + c + 1 for a, c, _u, _v in map(tuple, parent["folds"])}
    base_differences = {right - left for i, left in enumerate(base) for right in base[i + 1:]}
    fixed_sums = {left + right for i, left in enumerate(base) for right in base[i:]}
    if not args.allow_original_collisions:
        candidates = [
            value for value in candidates
            if all(abs(value - mark) not in phase_labels for mark in base)
        ]

    model = cp_model.CpModel()
    selected = [model.NewBoolVar(f"x_{value}") for value in candidates]
    model.Add(sum(selected) == 7)
    pair_constraints = 0
    for i, left in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            right = candidates[j]
            if (
                right - left in base_differences
                or (not args.allow_original_collisions and right - left in phase_labels)
                or left + right in fixed_sums
            ):
                model.Add(selected[i] + selected[j] <= 1)
                pair_constraints += 1

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 16
    valid_extensions = lazy_cuts = iterations = 0
    witness = None
    best = None
    statuses = []
    while valid_extensions < args.max_valid_extensions:
        iterations += 1
        solver.parameters.max_time_in_seconds = args.time_limit
        status = solver.Solve(model)
        statuses.append(solver.StatusName(status))
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            break
        additions = tuple(
            value for value, variable in zip(candidates, selected)
            if solver.Value(variable)
        )
        bad_support = collision_support(additions)
        if bad_support is not None:
            model.Add(sum(selected[candidates.index(additions[i])] for i in bad_support) <= len(bad_support) - 1)
            lazy_cuts += 1
            continue
        values = tuple(sorted(base + additions))
        assert p106m.is_sidon(values)
        valid_extensions += 1
        row = p106s.audit(values, h, 1)
        retained = {"additions": additions, **row}
        key = (row["intervals"] - row["matched"], row["intervals"] - row["slots"], row["T_F"])
        if best is None or key > best[0]:
            best = (key, retained)
        if row["RM97_failure"]:
            p = len(values)
            witness = {
                "B": values, "additions": additions,
                "p": p, "h": h, "b": 1,
                "delta": (3 * p * p - p + 2) // 2 - h,
                "sha256": hashlib.sha256(",".join(map(str, values)).encode("ascii")).hexdigest(),
                **row,
            }
            break
        model.Add(sum(selected[candidates.index(value)] for value in additions) <= 6)
        lazy_cuts += 1

    result = {
        "schema_version": 1,
        "base_p": len(base), "h": h,
        "allow_original_collisions": args.allow_original_collisions,
        "individually_admissible_candidates": len(candidates),
        "pair_constraints": pair_constraints,
        "solver_iterations": iterations, "lazy_cuts": lazy_cuts,
        "valid_seven_mark_extensions_audited": valid_extensions,
        "statuses": statuses[-10:],
        "positive_defect_RM97_witness": witness,
        "best_nonwitness": best[1] if best and witness is None else None,
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
