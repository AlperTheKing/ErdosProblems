#!/usr/bin/env python3
"""Exact CP-SAT countermodel search for unranked cap-two transport.

The model uses the real arithmetic canonical-parent map and all forward
closure clauses with distinct inputs.  It intentionally does not impose
grounded support for every selected member.  A solution with H-Q2 > 1 is
therefore a falsifier to deriving cap-two transport from forward closure and
canonical-forest constraints alone, not a counterexample for the least set G.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from ortools.sat.python import cp_model


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for a in range(2, int(product**0.5) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return result


def canonical_parent(n: int) -> int | None:
    if n > 3 and n % 2:
        return (n + 1) // 2
    if n % 2 == 0 and (n + 1) % 3 == 0:
        parent = (n + 1) // 3
        if parent != 3 and allowed(parent):
            return parent
    return None


def canonical_root(n: int) -> int:
    while (parent := canonical_parent(n)) is not None:
        n = parent
    return n


def seed_three_easy(n: int) -> bool:
    return n % 2 == 0 and canonical_parent(n) is not None


def solve(limit: int, workers: int, time_limit: float, support: str) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: admissible_pairs(n) for n in values}
    hard_shapes = [
        n for n in values
        if n % 2 == 0 and pairs[n] and not seed_three_easy(n)
    ]

    model = cp_model.CpModel()
    member = {n: model.new_bool_var(f"s_{n}") for n in values}
    model.add(member[2] == 1)
    model.add(member[3] == 1)
    closure_count = 0
    for n in values:
        for a, b in pairs[n]:
            model.add(member[a] + member[b] - 1 <= member[n])
            closure_count += 1

    support_clause_count = 0
    support_pair_count = 0
    for n in values:
        if n in (2, 3):
            continue
        require_support = (
            support == "all"
            or (support == "even" and n % 2 == 0)
            or (support == "roots" and canonical_parent(n) is None)
        )
        if not require_support:
            continue
        witnesses = []
        for a, b in pairs[n]:
            witness = model.new_bool_var(f"support_{n}_{a}_{b}")
            model.add(witness <= member[a])
            model.add(witness <= member[b])
            model.add(witness >= member[a] + member[b] - 1)
            witnesses.append(witness)
            support_pair_count += 1
        if witnesses:
            model.add(member[n] <= sum(witnesses))
        else:
            model.add(member[n] == 0)
        support_clause_count += 1

    exits_by_root: dict[int, list[tuple[int, cp_model.IntVar]]] = defaultdict(list)
    for child in values:
        if child % 2 == 0 or child <= 3:
            continue
        parent = (child + 1) // 2
        exit_var = model.new_bool_var(f"exit_{child}")
        # exit_var <=> child is selected and its canonical T2 parent is a hole.
        model.add(exit_var <= member[child])
        model.add(exit_var + member[parent] <= 1)
        model.add(exit_var >= member[child] - member[parent])
        exits_by_root[canonical_root(parent)].append((child, exit_var))

    q2_terms = []
    component_indicators = {}
    for root, entries in exits_by_root.items():
        exit_sum = sum(var for _, var in entries)
        count = len(entries)
        has_one = model.new_bool_var(f"root_{root}_has_one")
        has_two = model.new_bool_var(f"root_{root}_has_two")
        model.add(exit_sum >= has_one)
        model.add(exit_sum <= count * has_one)
        model.add(exit_sum >= 2 * has_two)
        model.add(exit_sum <= 1 + (count - 1) * has_two)
        model.add(has_two <= has_one)
        q2_terms.extend((has_one, has_two))
        component_indicators[root] = (has_one, has_two)

    hard_count = len(hard_shapes) - sum(member[n] for n in hard_shapes)
    q2_count = sum(q2_terms)
    model.maximize(hard_count - q2_count)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    status_name = solver.status_name(status)
    payload = {
        "schema_version": 1,
        "limit": limit,
        "status": status_name,
        "workers": workers,
        "time_limit_seconds": time_limit,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "best_objective_bound": solver.best_objective_bound,
        "closure_clauses": closure_count,
        "support_mode": support,
        "support_clauses": support_clause_count,
        "support_pair_indicators": support_pair_count,
        "hard_shapes": len(hard_shapes),
        "hard_shape_values": hard_shapes,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return payload

    selected = {n for n in values if solver.value(member[n])}
    holes = [n for n in values if n not in selected]
    hard = [n for n in hard_shapes if n not in selected]
    exits = []
    per_component = []
    for root, entries in sorted(exits_by_root.items()):
        root_exits = [child for child, var in entries if solver.value(var)]
        if root_exits:
            exits.extend(root_exits)
            per_component.append({
                "root": root,
                "exits": root_exits,
                "Q2": min(2, len(root_exits)),
            })
    q2 = sum(row["Q2"] for row in per_component)
    excess = len(hard) - q2
    if excess != round(solver.objective_value):
        raise AssertionError((excess, solver.objective_value))

    closure_violations = []
    for n in values:
        for a, b in pairs[n]:
            if a in selected and b in selected and n not in selected:
                closure_violations.append([a, b, n])
    unsupported = [
        n for n in sorted(selected - {2, 3})
        if not any(a in selected and b in selected for a, b in pairs[n])
    ]
    hole_parent_failures = []
    for n in holes:
        parent = canonical_parent(n)
        if parent is not None and parent in selected:
            hole_parent_failures.append([n, parent])

    payload.update({
        "objective_excess": excess,
        "H": len(hard),
        "Q2": q2,
        "member_count": len(selected),
        "hole_count": len(holes),
        "members": sorted(selected),
        "holes": holes,
        "hard": hard,
        "all_exits": sorted(exits),
        "exit_components": per_component,
        "unsupported_members": unsupported,
        "closure_violations": closure_violations,
        "canonical_hole_parent_failures": hole_parent_failures,
    })
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument(
        "--support",
        choices=("none", "roots", "even", "all"),
        default="none",
    )
    args = parser.parse_args()
    if args.limit < 4:
        parser.error("--limit must be at least 4")
    if not 1 <= args.workers <= 64:
        parser.error("--workers must lie in [1,64]")
    print(json.dumps(
        solve(args.limit, args.workers, args.time_limit, args.support), indent=2
    ))


if __name__ == "__main__":
    main()
