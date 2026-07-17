#!/usr/bin/env python3
"""Exact Boolean falsifier search for splitless-closed boundary (SCB).

The model contains no q variables.  Closure with the seed 2 gives

    t_m <= t_(2m-1),

so q_(2m-1) is exactly t_(2m-1)-t_m, even before optimization.  A
counterexample therefore satisfies the single integer inequality

    #hard - sum_h t_h - sum_m (t_(2m-1)-t_m) >= 1.

OR-Tools CP-SAT is used only with Boolean/integer constraints.  Any returned
witness is independently replayable by C61_scb_verify.py.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from array import array
from pathlib import Path

from ortools.sat.python import cp_model


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pair_iter(limit: int):
    """Yield every allowed distinct factorization n+1=a*b exactly once."""
    for a in range(2, math.isqrt(limit + 1) + 1):
        if not allowed(a):
            continue
        for b in range(a + 1, (limit + 1) // a + 1):
            if allowed(b):
                yield a * b - 1, a, b


def structure(limit: int):
    pair_count = array("I", [0]) * (limit + 1)
    total_pairs = 0
    for n, _, _ in pair_iter(limit):
        pair_count[n] += 1
        total_pairs += 1
    values = [n for n in range(2, limit + 1) if allowed(n)]
    splitless = [n for n in values if n not in (2, 3) and pair_count[n] == 0]
    hard = []
    for n in values:
        if n % 2 or pair_count[n] == 0:
            continue
        if (n + 1) % 3:
            hard.append(n)
            continue
        parent = (n + 1) // 3
        if not (allowed(parent) and parent != 3):
            hard.append(n)
    return values, pair_count, splitless, hard, total_pairs


def verify_t(limit: int, members: set[int]) -> dict:
    values, pair_count, splitless, hard, total_pairs = structure(limit)
    allowed_set = set(values)
    if not members <= allowed_set:
        raise RuntimeError("witness contains a disallowed or out-of-range value")
    if 2 not in members or 3 not in members:
        raise RuntimeError("witness omits a seed")
    forbidden = sorted(set(splitless) & members)
    if forbidden:
        raise RuntimeError(f"witness contains structural splitless values: {forbidden[:8]}")
    for n, a, b in pair_iter(limit):
        if a in members and b in members and n not in members:
            raise RuntimeError(f"closure failure {a}*{b}-1={n}")
    hard_holes = [n for n in hard if n not in members]
    boundaries = []
    for m in values:
        child = 2 * m - 1
        if child <= limit and m not in members and child in members:
            boundaries.append(child)
    return {
        "limit": limit,
        "value_count": len(values),
        "pair_count": total_pairs,
        "splitless_count": len(splitless),
        "hard_count": len(hard),
        "member_count": len(members),
        "H": len(hard_holes),
        "Q": len(boundaries),
        "H_minus_Q": len(hard_holes) - len(boundaries),
        "hard_holes": hard_holes,
        "boundaries": boundaries,
    }


def solve(limit: int, workers: int, seconds: float, witness_dir: Path | None) -> dict:
    started = time.perf_counter()
    values, pair_count, splitless, hard, total_pairs = structure(limit)
    splitless_set = set(splitless)

    model = cp_model.CpModel()
    variables: dict[int, cp_model.IntVar] = {}
    fixed: dict[int, int] = {2: 1, 3: 1}
    fixed.update({n: 0 for n in splitless})
    for n in values:
        if n not in fixed:
            variables[n] = model.new_bool_var(f"t_{n}")

    closure_rows = 0
    skipped_zero_antecedent = 0
    implications = 0
    ternary_clauses = 0
    forced_outputs = 0
    for n, a, b in pair_iter(limit):
        sa = fixed.get(a)
        sb = fixed.get(b)
        if sa == 0 or sb == 0:
            skipped_zero_antecedent += 1
            continue
        out = variables[n]
        closure_rows += 1
        if sa == 1 and sb == 1:
            model.add(out == 1)
            forced_outputs += 1
        elif sa == 1:
            model.add_implication(variables[b], out)
            implications += 1
        elif sb == 1:
            model.add_implication(variables[a], out)
            implications += 1
        else:
            model.add_bool_or([variables[a].Not(), variables[b].Not(), out])
            ternary_clauses += 1

    score_constant = len(hard)
    coefficients: dict[int, int] = {}

    def add_t(n: int, coefficient: int) -> None:
        nonlocal score_constant
        state = fixed.get(n)
        if state is None:
            coefficients[n] = coefficients.get(n, 0) + coefficient
        else:
            score_constant += coefficient * state

    for n in hard:
        add_t(n, -1)
    seed2_edges = 0
    for m in values:
        child = 2 * m - 1
        if child > limit:
            continue
        seed2_edges += 1
        add_t(child, -1)
        add_t(m, 1)

    score = score_constant + sum(
        coefficient * variables[n]
        for n, coefficient in coefficients.items()
        if coefficient
    )
    model.add(score >= 1)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.cp_model_presolve = True
    solver.parameters.linearization_level = 2
    status = solver.solve(model)
    status_name = solver.status_name(status)

    result = {
        "limit": limit,
        "status": status_name,
        "exact_conclusion": (
            "NO_BOOLEAN_COUNTEREXAMPLE" if status == cp_model.INFEASIBLE else
            "BOOLEAN_COUNTEREXAMPLE" if status in (cp_model.FEASIBLE, cp_model.OPTIMAL) else
            "INCONCLUSIVE"
        ),
        "wall_seconds": time.perf_counter() - started,
        "solver_wall_seconds": solver.wall_time,
        "workers": workers,
        "value_count": len(values),
        "boolean_variables": len(variables),
        "pair_count": total_pairs,
        "active_closure_rows": closure_rows,
        "skipped_zero_antecedent": skipped_zero_antecedent,
        "implications": implications,
        "ternary_clauses": ternary_clauses,
        "forced_outputs": forced_outputs,
        "splitless_count": len(splitless_set),
        "hard_count": len(hard),
        "seed2_edges": seed2_edges,
        "conflicts": solver.num_conflicts,
        "branches": solver.num_branches,
        "deterministic_time": solver.response_proto.deterministic_time,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        members = {
            n for n in values
            if fixed.get(n) == 1 or (n in variables and solver.boolean_value(variables[n]))
        }
        replay = verify_t(limit, members)
        if replay["H_minus_Q"] <= 0:
            raise RuntimeError("CP-SAT assignment does not falsify SCB")
        result["replay"] = replay
        if witness_dir is not None:
            witness_dir.mkdir(parents=True, exist_ok=True)
            witness_path = witness_dir / f"C61_witness_{limit}.json"
            witness_path.write_text(
                json.dumps({"limit": limit, "members": sorted(members)}, indent=2) + "\n",
                encoding="utf-8",
            )
            result["witness_path"] = str(witness_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seconds", type=float, default=600.0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--witness-dir", type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("--workers must lie in [1,64]")
    rows = [
        solve(limit, args.workers, args.seconds, args.witness_dir)
        for limit in args.limits
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
