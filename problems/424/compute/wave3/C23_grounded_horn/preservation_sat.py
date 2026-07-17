#!/usr/bin/env python3
"""CP-SAT falsifier for one-step grounded-contraction image properties.

At a finite cutoff let S be a forward-closed allowed set containing 2,3.
Let F(S) contain 2,3 and exactly the outputs having an admissible parent
pair in S. The proposed induction step is

    P(S) at every prefix  ==>  P(F(S)) at every prefix,

where P(T) is H_T <= Q_T, H_T counts hard-shaped holes, and Q_T counts
seed-2 boundary edges m notin T, 2m-1 in T. The source-side P(S)
condition is optional, so the unconditional modes search all S exactly.
"""

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
    left = 2
    while left * left < product:
        if product % left == 0:
            right = product // left
            if allowed(left) and allowed(right):
                result.append((left, right))
        left += 1
    return result


def hard_shape(value: int, pairs: list[tuple[int, int]]) -> bool:
    if value % 2 or not pairs:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


def and_var(
    model: cp_model.CpModel,
    left,
    right,
    name: str,
):
    result = model.new_bool_var(name)
    model.add(result <= left)
    model.add(result <= right)
    model.add(result >= left + right - 1)
    return result


def boundary_var(
    model: cp_model.CpModel,
    parent_member,
    child_member,
    name: str,
):
    result = model.new_bool_var(name)
    model.add(result <= 1 - parent_member)
    model.add(result <= child_member)
    model.add(result >= child_member - parent_member)
    return result


def prefix_excess_vars(
    model: cp_model.CpModel,
    members: dict[int, object],
    boundaries: dict[int, object],
    hard_values: list[int],
    value_count: int,
    name: str,
) -> dict[int, object]:
    """Return exact H-Q variables at hard cutoffs using sparse recurrences."""
    result = {}
    boundary_children = sorted(boundaries)
    boundary_index = 0
    previous_excess = 0
    for cutoff in hard_values:
        local_boundaries = []
        while (
            boundary_index < len(boundary_children)
            and boundary_children[boundary_index] <= cutoff
        ):
            child = boundary_children[boundary_index]
            local_boundaries.append(boundaries[child])
            boundary_index += 1
        current_excess = model.new_int_var(
            -value_count,
            value_count,
            f"{name}_{cutoff}",
        )
        model.add(
            current_excess
            == previous_excess
            + 1
            - members[cutoff]
            - sum(local_boundaries)
        )
        result[cutoff] = current_excess
        previous_excess = current_excess
    return result


def exact_counts(
    limit: int,
    members: set[int],
    pairs: dict[int, list[tuple[int, int]]],
) -> tuple[list[int], list[int], list[int]]:
    hard_holes = [
        value
        for value in range(2, limit + 1)
        if allowed(value)
        and hard_shape(value, pairs[value])
        and value not in members
    ]
    boundary_children = [
        child
        for parent in range(2, (limit + 1) // 2 + 1)
        if allowed(parent)
        for child in [2 * parent - 1]
        if parent not in members and child in members
    ]
    failures = []
    hard_count = 0
    boundary_count = 0
    hard_set = set(hard_holes)
    boundary_set = set(boundary_children)
    for value in range(2, limit + 1):
        hard_count += value in hard_set
        boundary_count += value in boundary_set
        if hard_count > boundary_count:
            failures.append(value)
    return hard_holes, boundary_children, failures


def solve(
    limit: int,
    workers: int,
    time_limit: float,
    assumption: str = "prefix",
) -> dict:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    hard_values = [
        value for value in values if hard_shape(value, pairs[value])
    ]

    model = cp_model.CpModel()
    previous = {
        value: model.new_bool_var(f"s_{value}") for value in values
    }
    following = {
        value: model.new_bool_var(f"f_{value}") for value in values
    }
    model.add(previous[2] == 1)
    model.add(previous[3] == 1)
    model.add(following[2] == 1)
    model.add(following[3] == 1)

    witnesses: dict[int, list] = {}
    for value in values:
        if value in (2, 3):
            witnesses[value] = []
            continue
        local = []
        for index, (left, right) in enumerate(pairs[value]):
            # S is forward closed.
            model.add(previous[left] + previous[right] - 1 <= previous[value])
            local.append(
                and_var(
                    model,
                    previous[left],
                    previous[right],
                    f"w_{value}_{index}",
                )
            )
        witnesses[value] = local
        if local:
            for witness in local:
                model.add(following[value] >= witness)
            model.add(following[value] <= sum(local))
        else:
            model.add(following[value] == 0)

    previous_boundary = {}
    following_boundary = {}
    for parent in values:
        child = 2 * parent - 1
        if child > limit:
            continue
        previous_boundary[child] = boundary_var(
            model,
            previous[parent],
            previous[child],
            f"q_{child}",
        )
        following_boundary[child] = boundary_var(
            model,
            following[parent],
            following[child],
            f"qf_{child}",
        )

    # Optionally require P(S) at every prefix or only at the target cutoff.
    previous_hard_terms = []
    previous_boundary_terms = []
    hard_set = set(hard_values)
    for value in range(2, limit + 1):
        if value in hard_set:
            previous_hard_terms.append(1 - previous[value])
        if value in previous_boundary:
            previous_boundary_terms.append(previous_boundary[value])
        if assumption == "prefix":
            model.add(
                sum(previous_hard_terms) <= sum(previous_boundary_terms)
            )
    if assumption == "endpoint":
        model.add(sum(previous_hard_terms) <= sum(previous_boundary_terms))
    elif assumption not in {
        "prefix",
        "selected",
        "unconditional",
        "unconditional_selected",
    }:
        raise ValueError(assumption)

    selected_cutoff_vars = {}
    selected_modes = {"selected", "unconditional_selected"}
    if assumption in selected_modes:
        previous_prefix_excess = prefix_excess_vars(
            model,
            previous,
            previous_boundary,
            hard_values,
            len(values),
            "previous_excess",
        )
        following_prefix_excess = prefix_excess_vars(
            model,
            following,
            following_boundary,
            hard_values,
            len(values),
            "following_excess",
        )
        selected_excess = model.new_int_var(
            -len(values), len(values), "selected_excess"
        )
        for cutoff in hard_values:
            selector = model.new_bool_var(f"select_{cutoff}")
            selected_cutoff_vars[cutoff] = selector
            if assumption == "selected":
                model.add(
                    previous_prefix_excess[cutoff] <= 0
                ).only_enforce_if(selector)
            model.add(
                selected_excess == following_prefix_excess[cutoff]
            ).only_enforce_if(selector)
        model.add_exactly_one(selected_cutoff_vars.values())
        model.maximize(selected_excess)
    else:
        following_hard = sum(1 - following[value] for value in hard_values)
        following_q = sum(following_boundary.values())
        model.maximize(following_hard - following_q)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    status_name = solver.status_name(status)
    result = {
        "schema_version": 1,
        "limit": limit,
        "workers": workers,
        "time_limit_seconds": time_limit,
        "assumption": assumption,
        "status": status_name,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "best_objective_bound": solver.best_objective_bound,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return result

    selected_cutoff = limit
    if assumption in selected_modes:
        selected_cutoff = next(
            cutoff
            for cutoff, selector in selected_cutoff_vars.items()
            if solver.value(selector)
        )

    previous_members = {
        value for value in values if solver.value(previous[value])
    }
    following_members = {
        value for value in values if solver.value(following[value])
    }
    replay_following = {2, 3}
    for value in values:
        if value in (2, 3):
            continue
        if any(
            left in previous_members and right in previous_members
            for left, right in pairs[value]
        ):
            replay_following.add(value)
    if replay_following != following_members:
        raise AssertionError("F(S) replay mismatch")

    for value in values:
        for left, right in pairs[value]:
            if (
                left in previous_members
                and right in previous_members
                and value not in previous_members
            ):
                raise AssertionError(f"S closure failure at {value}")

    prev_h, prev_q, prev_failures = exact_counts(
        selected_cutoff, previous_members, pairs
    )
    next_h, next_q, next_failures = exact_counts(
        selected_cutoff, following_members, pairs
    )
    if assumption == "prefix" and prev_failures:
        raise AssertionError(f"P(S) failure at {prev_failures[0]}")
    if assumption in {"prefix", "endpoint", "selected"} and (
        len(prev_h) > len(prev_q)
    ):
        raise AssertionError("endpoint P(S) failure")
    exact_excess = len(next_h) - len(next_q)
    if exact_excess != round(solver.objective_value):
        raise AssertionError("objective replay mismatch")

    unsupported = []
    for value in sorted(previous_members - {2, 3}):
        if not any(
            left in previous_members and right in previous_members
            for left, right in pairs[value]
        ):
            unsupported.append(value)

    removed = sorted(
        value
        for value in previous_members - following_members
        if value <= selected_cutoff
    )
    for value in removed:
        if value % 2:
            predecessor = (value + 1) // 2
            if predecessor in previous_members:
                raise AssertionError(
                    f"removed nonthreshold chain member {value}"
                )
            if value not in prev_q:
                raise AssertionError(
                    f"removed odd threshold is not old boundary {value}"
                )

    half = (selected_cutoff + 1) // 2
    dangerous_boundaries = [
        value for value in removed if value % 2 and value > half
    ]
    dangerous_hard_roots = [
        value
        for value in removed
        if value % 2 == 0
        and value > half
        and hard_shape(value, pairs[value])
    ]
    helpful_nonhard_roots = [
        value
        for value in removed
        if value % 2 == 0
        and value <= half
        and not hard_shape(value, pairs[value])
    ]
    old_slack = len(prev_q) - len(prev_h)
    new_slack = len(next_q) - len(next_h)
    threshold_identity_slack = (
        old_slack
        - len(dangerous_boundaries)
        - len(dangerous_hard_roots)
        + len(helpful_nonhard_roots)
    )
    if new_slack != threshold_identity_slack:
        raise AssertionError(
            (new_slack, threshold_identity_slack)
        )

    credit_keys = sorted(
        prev_q
        + [
            2 * value - 1
            for value in removed
            if 2 * value - 1 <= selected_cutoff
        ]
    )
    demand_keys = sorted(
        prev_h
        + [value for value in removed if value % 2]
        + [
            value
            for value in removed
            if value % 2 == 0 and hard_shape(value, pairs[value])
        ]
    )
    if len(demand_keys) - len(credit_keys) != exact_excess:
        raise AssertionError("sorted event count mismatch")
    first_sorted_violation = None
    for index, demand in enumerate(demand_keys):
        if index >= len(credit_keys) or credit_keys[index] > demand:
            first_sorted_violation = {
                "index": index,
                "demand": demand,
                "credit": (
                    credit_keys[index]
                    if index < len(credit_keys)
                    else None
                ),
            }
            break

    result.update(
        {
            "objective_excess": exact_excess,
            "selected_cutoff": selected_cutoff,
            "previous_members": sorted(
                value
                for value in previous_members
                if value <= selected_cutoff
            ),
            "previous_hard_holes": prev_h,
            "previous_boundary_children": prev_q,
            "following_members": sorted(
                value
                for value in following_members
                if value <= selected_cutoff
            ),
            "following_hard_holes": next_h,
            "following_boundary_children": next_q,
            "following_first_failure": (
                next_failures[0] if next_failures else None
            ),
            "unsupported_previous_members": unsupported,
            "threshold_shift_identity": {
                "half": half,
                "old_slack_Q_minus_H": old_slack,
                "dangerous_moved_boundaries": dangerous_boundaries,
                "dangerous_removed_hard_roots": dangerous_hard_roots,
                "helpful_removed_nonhard_roots": helpful_nonhard_roots,
                "new_slack_Q_minus_H": new_slack,
            },
            "sorted_event_dominance": {
                "credit_keys": credit_keys,
                "demand_keys": demand_keys,
                "first_violation": first_sorted_violation,
            },
        }
    )
    return result


def scan(
    stop: int,
    workers: int,
    time_limit: float,
    assumption: str = "prefix",
) -> dict:
    hard_cutoffs = [
        value
        for value in range(4, stop + 1)
        if allowed(value)
        and hard_shape(value, admissible_pairs(value))
    ]
    tested = 0
    for limit in hard_cutoffs:
        result = solve(limit, workers, time_limit, assumption)
        tested += 1
        if result["status"] != "OPTIMAL":
            return {
                "schema_version": 1,
                "stop": stop,
                "tested": tested,
                "inconclusive": result,
            }
        if result["objective_excess"] > 0:
            return {
                "schema_version": 1,
                "stop": stop,
                "tested": tested,
                "first_failure": result,
            }
    return {
        "schema_version": 1,
        "stop": stop,
        "tested": tested,
        "first_failure": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--stop", type=int)
    mode.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument(
        "--assumption",
        choices=(
            "prefix",
            "endpoint",
            "selected",
            "unconditional",
            "unconditional_selected",
        ),
        default="prefix",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must lie in [1,64]")

    result = (
        solve(args.limit, args.workers, args.time_limit, args.assumption)
        if args.limit is not None
        else scan(args.stop, args.workers, args.time_limit, args.assumption)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="ascii",
    )
    if args.limit is not None:
        print(
            f"limit={result['limit']} status={result['status']} "
            f"excess={result.get('objective_excess')} "
            f"selected={result.get('selected_cutoff')} "
            f"first_failure={result.get('following_first_failure')}"
        )
    else:
        failure = result.get("first_failure")
        print(
            f"stop={result['stop']} tested={result['tested']} "
            f"first_failure={None if failure is None else failure['limit']} "
            f"excess={None if failure is None else failure['objective_excess']}"
        )


if __name__ == "__main__":
    main()
