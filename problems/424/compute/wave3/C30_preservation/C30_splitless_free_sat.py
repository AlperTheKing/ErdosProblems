#!/usr/bin/env python3
"""Exact H/Q falsifier for closed sets containing no splitless nonseed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ortools.sat.python import cp_model


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    result = []
    for left in range(2, int(product**0.5) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def hard_shape(value: int, pairs: list[tuple[int, int]]) -> bool:
    if value % 2 or not pairs:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


def boundary_var(model: cp_model.CpModel, parent, child, name: str):
    result = model.new_bool_var(name)
    model.add(result <= 1 - parent)
    model.add(result <= child)
    model.add(result >= child - parent)
    return result


def solve(limit: int, workers: int, time_limit: float) -> dict:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    hard = [
        value for value in values if hard_shape(value, pairs[value])
    ]

    model = cp_model.CpModel()
    member = {
        value: model.new_bool_var(f"s_{value}") for value in values
    }
    model.add(member[2] == 1)
    model.add(member[3] == 1)
    closure_constraints = 0
    splitless_exclusions = 0
    for value in values:
        if value not in (2, 3) and not pairs[value]:
            model.add(member[value] == 0)
            splitless_exclusions += 1
        for left, right in pairs[value]:
            model.add(member[left] + member[right] - 1 <= member[value])
            closure_constraints += 1

    boundaries = {}
    for parent in values:
        child = 2 * parent - 1
        if child <= limit:
            boundaries[child] = boundary_var(
                model, member[parent], member[child], f"q_{child}"
            )

    model.maximize(
        sum(1 - member[value] for value in hard)
        - sum(boundaries.values())
    )
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    result = {
        "schema_version": 1,
        "limit": limit,
        "workers": workers,
        "time_limit_seconds": time_limit,
        "status": solver.status_name(status),
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "closure_constraints": closure_constraints,
        "splitless_exclusions": splitless_exclusions,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return result

    members = {value for value in values if solver.value(member[value])}
    hard_holes = [value for value in hard if value not in members]
    q_children = [
        child
        for child in boundaries
        if (child + 1) // 2 not in members and child in members
    ]
    exact_excess = len(hard_holes) - len(q_children)
    if exact_excess != round(solver.objective_value):
        raise AssertionError("objective replay mismatch")
    for value in values:
        if value not in (2, 3) and not pairs[value] and value in members:
            raise AssertionError(f"splitless member {value}")
        for left, right in pairs[value]:
            if left in members and right in members and value not in members:
                raise AssertionError(f"closure failure at {value}")

    failures = []
    excess = 0
    hard_set = set(hard_holes)
    q_set = set(q_children)
    for value in range(2, limit + 1):
        excess += value in hard_set
        excess -= value in q_set
        if excess > 0:
            failures.append(value)
    result.update(
        {
            "objective_excess": exact_excess,
            "hard_holes": hard_holes,
            "boundary_children": q_children,
            "first_failure": failures[0] if failures else None,
            "members": sorted(members),
        }
    )
    return result


def scan(stop: int, workers: int, time_limit: float) -> dict:
    cutoffs = [
        value
        for value in range(4, stop + 1)
        if allowed(value)
        and hard_shape(value, admissible_pairs(value))
    ]
    for index, cutoff in enumerate(cutoffs, start=1):
        result = solve(cutoff, workers, time_limit)
        if result["status"] != "OPTIMAL":
            return {
                "schema_version": 1,
                "stop": stop,
                "tested": index,
                "inconclusive": result,
            }
        if result["objective_excess"] > 0:
            return {
                "schema_version": 1,
                "stop": stop,
                "tested": index,
                "first_failure": result,
            }
    return {
        "schema_version": 1,
        "stop": stop,
        "tested": len(cutoffs),
        "first_failure": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--limit", type=int)
    mode.add_argument("--stop", type=int)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must lie in [1,64]")
    result = (
        solve(args.limit, args.workers, args.time_limit)
        if args.limit is not None
        else scan(args.stop, args.workers, args.time_limit)
    )
    args.output.write_text(
        json.dumps(result, indent=2) + "\n", encoding="ascii"
    )
    failure = result.get("first_failure")
    if args.limit is not None:
        print(
            f"limit={args.limit} status={result['status']} "
            f"excess={result.get('objective_excess')}"
        )
    else:
        print(
            f"stop={args.stop} tested={result['tested']} "
            f"failure={None if failure is None else failure['limit']}"
        )


if __name__ == "__main__":
    main()
