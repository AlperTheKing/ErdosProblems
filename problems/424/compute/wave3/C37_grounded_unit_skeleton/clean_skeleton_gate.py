#!/usr/bin/env python3
"""Exact gate for clean unit grounded-dual skeletons.

A clean skeleton uses only complete lower image gates, complete upper image
gates, and boundary-lower rows.  All remaining stationarity is discharged by
variable bounds, which can be eliminated exactly from the model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model


HERE = Path(__file__).resolve().parent
C34 = HERE.parent / "C34_image_dual_core"
sys.path.insert(0, str(C34))

from ground_core_lp import grounded_core  # noqa: E402
from lp_probe import admissible_pairs, allowed, hard_shape  # noqa: E402


def data_at(limit: int) -> tuple[list[int], dict[int, list[tuple[int, int]]], set[int]]:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    return values, pairs, grounded_core(values, pairs)


def solve(limit: int, time_limit: float | None = None, details: bool = True) -> dict:
    values, pairs, ground = data_at(limit)
    hard = {value for value in values if hard_shape(value, pairs[value])}
    model = cp_model.CpModel()

    boundary = {
        2 * parent - 1: model.new_bool_var(f"c_{2 * parent - 1}")
        for parent in values
        if 2 * parent - 1 <= limit
    }
    lower = {
        (value, pair_index): model.new_bool_var(f"l_{value}_{pair_index}")
        for value in values
        for pair_index in range(len(pairs[value]))
    }
    upper = {
        value: model.new_bool_var(f"u_{value}")
        for value in values
        if pairs[value]
    }
    choose_left = {}
    choose_right = {}
    for value, upper_var in upper.items():
        for pair_index in range(len(pairs[value])):
            left = model.new_bool_var(f"ul_{value}_{pair_index}")
            right = model.new_bool_var(f"ur_{value}_{pair_index}")
            choose_left[value, pair_index] = left
            choose_right[value, pair_index] = right
            model.add(left + right == upper_var)

    lower_count = {value: [] for value in values}
    upper_count = {value: [] for value in values}
    for (node, pair_index), variable in lower.items():
        left, right = pairs[node][pair_index]
        lower_count[left].append(variable)
        lower_count[right].append(variable)
    for (node, pair_index), variable in choose_left.items():
        left, right = pairs[node][pair_index]
        upper_count[left].append(variable)
        upper_count[right].append(choose_right[node, pair_index])

    score_terms = []
    source_penalties = {}
    for value in values:
        lower_sum = sum(lower_count[value])
        upper_sum = sum(upper_count[value])
        if value in ground:
            score_terms.append(lower_sum - upper_sum)
        else:
            maximum = len(upper_count[value])
            penalty = model.new_int_var(0, maximum, f"sp_{value}")
            model.add(penalty >= upper_sum - lower_sum)
            source_penalties[value] = penalty
            score_terms.append(-penalty)

    f_residuals = {}
    f_penalties = {}
    for value in values:
        incoming = boundary.get(value, 0)
        outgoing = boundary.get(2 * value - 1, 0)
        lower_sum = sum(
            lower[value, pair_index] for pair_index in range(len(pairs[value]))
        )
        upper_var = upper.get(value, 0)
        # The bound coefficient needed at f_value after all selected rows.
        residual = (
            int(value in hard) + incoming - outgoing - lower_sum + upper_var
        )
        f_residuals[value] = residual
        if value in (2, 3):
            # f_2=f_3=1, so either bound has objective equal to the residual.
            score_terms.append(residual)
        elif not pairs[value]:
            # f_value=0, so its bound multiplier has zero objective.
            pass
        else:
            maximum = 3 + len(pairs[value])
            penalty = model.new_int_var(0, maximum, f"fp_{value}")
            model.add(penalty >= -residual)
            f_penalties[value] = penalty
            score_terms.append(-penalty)

    score_terms.extend(-variable for variable in lower.values())
    score = sum(score_terms)
    model.add(score >= len(hard))

    # Count the actual non-bound rows.  A lower gate has two rows; an upper
    # gate has one OR row plus one selected AND row per parent pair.
    complexity = (
        sum(boundary.values())
        + 2 * sum(lower.values())
        + sum((1 + len(pairs[value])) * variable for value, variable in upper.items())
    )
    model.minimize(complexity)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    solver.parameters.cp_model_presolve = True
    if time_limit is not None:
        solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    payload = {
        "schema_version": 1,
        "limit": limit,
        "status": solver.status_name(status),
        "hard_count": len(hard),
        "ground_size": len(ground),
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return payload

    payload.update(
        {
            "score": int(solver.value(score)),
            "complexity": int(solver.value(complexity)),
            "boundary_count": sum(solver.value(variable) for variable in boundary.values()),
            "lower_gate_count": sum(solver.value(variable) for variable in lower.values()),
            "upper_gate_count": sum(solver.value(variable) for variable in upper.values()),
        }
    )
    if not details:
        return payload

    selected_boundary = sorted(
        child for child, variable in boundary.items() if solver.value(variable)
    )
    selected_lower = [
        {
            "node": node,
            "pair_index": pair_index,
            "parents": list(pairs[node][pair_index]),
        }
        for (node, pair_index), variable in lower.items()
        if solver.value(variable)
    ]
    selected_upper = []
    for node, variable in upper.items():
        if not solver.value(variable):
            continue
        choices = []
        for pair_index, pair in enumerate(pairs[node]):
            side = 0 if solver.value(choose_left[node, pair_index]) else 1
            choices.append(
                {
                    "pair_index": pair_index,
                    "pair": list(pair),
                    "selected_parent": pair[side],
                }
            )
        selected_upper.append({"node": node, "choices": choices})
    payload["selected_boundary"] = selected_boundary
    payload["selected_lower"] = selected_lower
    payload["selected_upper"] = selected_upper
    payload["source_penalties"] = {
        str(value): solver.value(variable)
        for value, variable in source_penalties.items()
        if solver.value(variable)
    }
    payload["f_penalties"] = {
        str(value): solver.value(variable)
        for value, variable in f_penalties.items()
        if solver.value(variable)
    }
    payload["f_residuals"] = {
        str(value): solver.value(residual)
        for value, residual in f_residuals.items()
        if solver.value(residual)
    }
    return payload


def hard_cutoffs(stop: int) -> list[int]:
    return [
        value
        for value in range(4, stop + 1)
        if allowed(value) and hard_shape(value, admissible_pairs(value))
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--limit", type=int)
    mode.add_argument("--stop", type=int)
    parser.add_argument("--time-limit", type=float)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.limit is not None:
        payload = solve(args.limit, args.time_limit, True)
    else:
        results = []
        for cutoff in hard_cutoffs(args.stop):
            result = solve(cutoff, args.time_limit, False)
            results.append(result)
            if result["status"] not in ("OPTIMAL", "FEASIBLE"):
                break
        payload = {
            "schema_version": 1,
            "stop": args.stop,
            "tested": len(results),
            "all_feasible": all(
                result["status"] in ("OPTIMAL", "FEASIBLE") for result in results
            ),
            "results": results,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                key: payload[key]
                for key in (
                    "limit", "stop", "tested", "all_feasible", "status",
                    "hard_count", "score", "complexity", "wall_time_seconds",
                )
                if key in payload
            }
        )
    )


if __name__ == "__main__":
    main()
