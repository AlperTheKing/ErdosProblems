#!/usr/bin/env python3
"""Exact countermodel search for a universal one-step image cap-two lemma.

For every forward-closed source S on the arithmetic prefix, the model forms
its exact Horn image F(S).  It then maximizes H_{F(S)}-Q2_{F(S)} using the
real canonical C39 components.  A positive optimum above one falsifies the
claim that one grounded image step alone forces cap-two transport.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from ortools.sat.python import cp_model

from C52_closed_countermodel import (
    admissible_pairs,
    allowed,
    canonical_root,
    seed_three_easy,
)


def solve(limit: int, workers: int, time_limit: float) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: admissible_pairs(n) for n in values}
    hard_shapes = [
        n for n in values
        if n % 2 == 0 and pairs[n] and not seed_three_easy(n)
    ]

    model = cp_model.CpModel()
    source = {n: model.new_bool_var(f"source_{n}") for n in values}
    image = {n: model.new_bool_var(f"image_{n}") for n in values}
    model.add(source[2] == 1)
    model.add(source[3] == 1)
    model.add(image[2] == 1)
    model.add(image[3] == 1)

    closure_count = 0
    support_indicators = 0
    for n in values:
        for a, b in pairs[n]:
            model.add(source[a] + source[b] - 1 <= source[n])
            closure_count += 1
        if n in (2, 3):
            continue
        witnesses = []
        for a, b in pairs[n]:
            witness = model.new_bool_var(f"witness_{n}_{a}_{b}")
            model.add(witness <= source[a])
            model.add(witness <= source[b])
            model.add(witness >= source[a] + source[b] - 1)
            witnesses.append(witness)
            support_indicators += 1
        if witnesses:
            for witness in witnesses:
                model.add(image[n] >= witness)
            model.add(image[n] <= sum(witnesses))
        else:
            model.add(image[n] == 0)

    exits_by_root: dict[int, list[tuple[int, cp_model.IntVar]]] = defaultdict(list)
    for child in values:
        if child % 2 == 0 or child <= 3:
            continue
        parent = (child + 1) // 2
        exit_var = model.new_bool_var(f"exit_{child}")
        model.add(exit_var <= image[child])
        model.add(exit_var + image[parent] <= 1)
        model.add(exit_var >= image[child] - image[parent])
        exits_by_root[canonical_root(parent)].append((child, exit_var))

    q2_terms = []
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

    hard_count = len(hard_shapes) - sum(image[n] for n in hard_shapes)
    q2_count = sum(q2_terms)
    model.maximize(hard_count - q2_count)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    payload = {
        "schema_version": 1,
        "limit": limit,
        "status": solver.status_name(status),
        "workers": workers,
        "time_limit_seconds": time_limit,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "best_objective_bound": solver.best_objective_bound,
        "closure_clauses": closure_count,
        "support_indicators": support_indicators,
        "hard_shape_values": hard_shapes,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return payload

    source_set = {n for n in values if solver.value(source[n])}
    image_set = {n for n in values if solver.value(image[n])}
    hard = [n for n in hard_shapes if n not in image_set]
    exit_components = []
    selected_exits = []
    all_exits = []
    for root, entries in sorted(exits_by_root.items()):
        root_exits = [child for child, var in entries if solver.value(var)]
        if not root_exits:
            continue
        chosen = root_exits[:2]
        all_exits.extend(root_exits)
        selected_exits.extend(chosen)
        exit_components.append({
            "root": root,
            "exits": root_exits,
            "selected": chosen,
        })
    excess = len(hard) - len(selected_exits)
    if excess != round(solver.objective_value):
        raise AssertionError((excess, solver.objective_value))

    closure_violations = []
    image_mismatches = []
    for n in values:
        supported = n in (2, 3) or any(
            a in source_set and b in source_set for a, b in pairs[n]
        )
        if supported != (n in image_set):
            image_mismatches.append(n)
        for a, b in pairs[n]:
            if a in source_set and b in source_set and n not in source_set:
                closure_violations.append([a, b, n])
    image_closure_violations = []
    for n in values:
        for a, b in pairs[n]:
            if a in image_set and b in image_set and n not in image_set:
                image_closure_violations.append([a, b, n])

    payload.update({
        "objective_excess": excess,
        "H": len(hard),
        "Q2": len(selected_exits),
        "source_members": sorted(source_set),
        "image_members": sorted(image_set),
        "hard": hard,
        "all_exits": sorted(all_exits),
        "selected_exits": sorted(selected_exits),
        "exit_components": exit_components,
        "source_closure_violations": closure_violations,
        "image_equivalence_mismatches": image_mismatches,
        "image_closure_violations": image_closure_violations,
    })
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--scan-hard-cutoffs", action="store_true")
    args = parser.parse_args()
    if args.limit < 4:
        parser.error("--limit must be at least 4")
    if not 1 <= args.workers <= 64:
        parser.error("--workers must lie in [1,64]")
    if not args.scan_hard_cutoffs:
        print(json.dumps(solve(args.limit, args.workers, args.time_limit), indent=2))
        return

    events = [
        n for n in range(2, args.limit + 1)
        if allowed(n)
        and n % 2 == 0
        and admissible_pairs(n)
        and not seed_three_easy(n)
    ]
    maximum = None
    maximum_x = None
    first_failure = None
    checked = 0
    total_wall = 0.0
    for cutoff in events:
        result = solve(cutoff, args.workers, args.time_limit)
        checked += 1
        total_wall += result["wall_time_seconds"]
        if result["status"] != "OPTIMAL":
            first_failure = {
                "X": cutoff,
                "reason": "solver did not prove optimality",
                "status": result["status"],
                "objective": result.get("objective_excess"),
                "bound": result["best_objective_bound"],
            }
            break
        objective = result["objective_excess"]
        if maximum is None or objective > maximum:
            maximum = objective
            maximum_x = cutoff
        if objective > 1:
            first_failure = {
                "X": cutoff,
                "objective": objective,
                "H": result["H"],
                "Q2": result["Q2"],
                "hard": result["hard"],
                "selected_exits": result["selected_exits"],
            }
            break
    print(json.dumps({
        "schema_version": 1,
        "search": "universal one-step image at every hard-shape cutoff",
        "limit": args.limit,
        "hard_cutoffs_total": len(events),
        "hard_cutoffs_checked": checked,
        "all_optimal": first_failure is None,
        "maximum_objective": maximum,
        "maximum_X": maximum_x,
        "first_plus_one_failure": first_failure,
        "solver_wall_time_seconds": total_wall,
    }, indent=2))


if __name__ == "__main__":
    main()
