#!/usr/bin/env python3
"""Exact CP-SAT falsifier search for the unrestricted P65 statement.

The Boolean model includes every mark in [0,H], every unordered pair
(diagonals included), all Sidon sum constraints, all literal -b in 3B-B
constraints with repeated variables, and every h-shifted sum fold.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from ortools.sat.python import cp_model


ROOT = Path(__file__).resolve().parents[4]
AUDIT_SCRIPT = ROOT / "problems/864/compute/p65/search_hole_restricted_folds.py"


def load_audit():
    spec = importlib.util.spec_from_file_location("p65_unrestricted_audit", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(AUDIT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--H", type=int, required=True)
    parser.add_argument("--b", type=int, choices=(1, 2), required=True)
    parser.add_argument("--target", type=int)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")
    p, H, b = args.p, args.H, args.b
    h = H + 1
    target = args.target if args.target is not None else 2 * p - 2
    delta = (3 * p * p - p + 2) // 2 - h
    if delta <= 0:
        parser.error("the requested (p,H) does not have positive delta")

    model = cp_model.CpModel()
    marks = [model.new_bool_var(f"x_{i}") for i in range(H + 1)]
    model.add(sum(marks) == p)
    model.add(marks[H] == 1)

    pair: dict[tuple[int, int], cp_model.IntVar] = {}
    by_sum: list[list[cp_model.IntVar]] = [[] for _ in range(2 * H + 1)]
    for x in range(H + 1):
        pair[(x, x)] = marks[x]
        by_sum[2 * x].append(marks[x])
        for y in range(x + 1, H + 1):
            z = model.new_bool_var(f"pair_{x}_{y}")
            model.add(z <= marks[x])
            model.add(z <= marks[y])
            model.add(z >= marks[x] + marks[y] - 1)
            pair[(x, y)] = z
            by_sum[x + y].append(z)

    sum_active = []
    for s, representations in enumerate(by_sum):
        active = model.new_bool_var(f"sum_{s}")
        model.add(sum(representations) == active)
        sum_active.append(active)

    # If x+y=s and w-z=s+b, selecting both pairs gives x+y+z-w=-b.
    # Pair variables are exact ANDs, so this includes all coincidences and
    # repeated variables without a distinctness assumption.
    hole_constraints = 0
    for s in range(H - b + 1):
        d = s + b
        for z in range(H - d + 1):
            w = z + d
            model.add(sum_active[s] + pair[(z, w)] <= 1)
            hole_constraints += 1

    folds = []
    for s in range(H):
        fold = model.new_bool_var(f"fold_{s}")
        model.add(fold <= sum_active[s])
        model.add(fold <= sum_active[s + h])
        model.add(fold >= sum_active[s] + sum_active[s + h] - 1)
        folds.append(fold)
    model.add(sum(folds) >= target)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.cp_model_presolve = True
    status = solver.solve(model)
    status_name = solver.status_name(status)
    output: dict[str, object] = {
        "schema_version": 1, "arithmetic": "exact integer CP-SAT",
        "p": p, "H": H, "h": h, "b": b, "delta": delta,
        "target_C_S": target, "pair_variables_including_diagonals": len(pair),
        "hole_constraints": hole_constraints,
        "status": status_name, "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches, "conflicts": solver.num_conflicts,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        values = tuple(i for i in range(H + 1) if solver.value(marks[i]))
        audit = load_audit().fold_rows(values, 0, b)
        if audit["p"] != p or audit["h"] != h or audit["delta"] != delta:
            raise AssertionError((output, audit))
        if not audit["hole"] or audit["C_S"] < target:
            raise AssertionError(("invalid extracted witness", output, audit))
        output["witness"] = audit
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
