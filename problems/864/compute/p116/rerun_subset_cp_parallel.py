#!/usr/bin/env python3
"""Parallel feasibility rerun for unresolved P116 induced-subset models."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=int, required=True)
    parser.add_argument("--b", type=int, choices=(1, 2), required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seconds", type=int, default=300)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be in [1,16]")
    p86 = load("p86_subset_parallel", ROOT / "problems/864/compute/p86/dense_loose_search.py")
    subset = load("p116_subset_parallel", ROOT / "problems/864/compute/p116/search_bc108_subset_cp.py")
    bases, manifests = p86.load_archives()
    values = tuple(bases[args.parent].values)
    model, data = subset.model_for(values, args.b, True)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    solver.parameters.max_time_in_seconds = args.seconds
    status = solver.Solve(model)
    witness = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = tuple(
            mark for mark in values if solver.Value(data["selected"][mark])
        )
        witness = subset.audit_subset(selected, int(data["h"]), args.b)
        if int(witness["BC108_margin"]) <= 0:
            raise AssertionError(witness)
    result = {
        "schema_version": 1,
        "arithmetic": "exact integer CP-SAT feasibility model; exact integer witness audit",
        "parent_index": args.parent,
        "b": args.b,
        "parent_p": len(values),
        "h": int(data["h"]),
        "positive_defect_min_p": int(data["p_min"]),
        "parent_folds": len(data["system"].folds),
        "parent_triangles": len(data["system"].triangles),
        "hole_obstructions": len(data["holes"]),
        "workers": args.workers,
        "seconds_limit": args.seconds,
        "status": solver.StatusName(status),
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "witness": witness,
        "archive_manifest": manifests,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "parent": args.parent, "b": args.b, "status": result["status"],
        "wall_time_seconds": result["wall_time_seconds"], "witness": witness,
    }, indent=2))


if __name__ == "__main__":
    main()
