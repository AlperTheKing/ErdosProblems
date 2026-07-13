#!/usr/bin/env python3
"""Exact CP-SAT falsifier for the universal two-scale hole contraction.

For a cutoff X, this searches over every subset S of the allowed integers
2 <= n <= X (n != 1 mod 3) that contains 2 and 3 and is closed under

    a,b in S, 2 <= a < b, n = a*b - 1 <= X  ==>  n in S.

It maximizes

    R_S(X) - M_S(floor((X+1)/2)) - M_S(floor((X+1)/3)),

where M counts allowed holes and R counts holes n for which n+1 has at
least one admissible factorization a*b with 2 <= a < b.  A positive optimum
is an exact finite counterexample to deriving the candidate inequality from
closure alone.  A nonpositive optimum certifies the universal inequality at
that cutoff through an integer linear model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ortools.sat.python import cp_model


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    pairs: list[tuple[int, int]] = []
    a = 2
    while a * a < product:
        if product % a == 0:
            b = product // a
            if a < b and allowed(a) and allowed(b):
                pairs.append((a, b))
        a += 1
    return pairs


def solve_cutoff(limit: int, workers: int, time_limit: float) -> dict:
    if limit < 4:
        raise ValueError("limit must be at least 4")

    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: admissible_pairs(n) for n in values}
    reducible = {n for n in values if pairs[n]}

    model = cp_model.CpModel()
    member = {n: model.new_bool_var(f"s_{n}") for n in values}
    model.add(member[2] == 1)
    model.add(member[3] == 1)

    closure_constraints = 0
    for n in values:
        for a, b in pairs[n]:
            model.add(member[a] + member[b] - 1 <= member[n])
            closure_constraints += 1

    half = (limit + 1) // 2
    third = (limit + 1) // 3

    # Constants cancel correctly when holes are expanded as 1 - s_n.
    objective_terms = []
    objective_constant = 0
    for n in values:
        coefficient = int(n in reducible) - int(n <= half) - int(n <= third)
        if coefficient:
            objective_constant += coefficient
            objective_terms.append(-coefficient * member[n])

    objective_expr = objective_constant + sum(objective_terms)
    model.maximize(objective_expr)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.cp_model_presolve = True
    status = solver.solve(model)

    status_name = solver.status_name(status)
    result = {
        "schema_version": 1,
        "limit": limit,
        "allowed_count": len(values),
        "reducible_count": len(reducible),
        "factor_pairs": closure_constraints,
        "half": half,
        "third": third,
        "workers": workers,
        "time_limit_seconds": time_limit,
        "status": status_name,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        members = [n for n in values if solver.value(member[n])]
        holes = [n for n in values if not solver.value(member[n])]
        r = sum(n in reducible for n in holes)
        m_half = sum(n <= half for n in holes)
        m_third = sum(n <= third for n in holes)
        exact_excess = r - m_half - m_third
        solver_objective = int(round(solver.objective_value))
        if exact_excess != solver_objective:
            raise AssertionError((exact_excess, solver_objective))
        result.update(
            {
                "objective_excess": exact_excess,
                "R": r,
                "Mhalf": m_half,
                "Mthird": m_third,
                "member_count": len(members),
                "hole_count": len(holes),
                "members": members,
                "holes": holes,
            }
        )

        # Independent exact closure replay.
        member_set = set(members)
        for n in members:
            if not allowed(n):
                raise AssertionError(f"disallowed member {n}")
        for n in values:
            for a, b in pairs[n]:
                if a in member_set and b in member_set and n not in member_set:
                    raise AssertionError(f"closure violation {a}*{b}-1={n}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not 1 <= args.workers <= 64:
        raise ValueError("workers must lie in [1,64]")

    result = solve_cutoff(args.limit, args.workers, args.time_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        f"limit={result['limit']} status={result['status']} "
        f"excess={result.get('objective_excess')} "
        f"wall={result['wall_time_seconds']:.3f}s"
    )


if __name__ == "__main__":
    main()
