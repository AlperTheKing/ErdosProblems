#!/usr/bin/env python3
"""Exact collisionUnits optimization for the balanced C5[3] row product."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
WRITEUP = ROOT / "problems" / "23" / "writeup"
SOFTCAP = HERE.parent / "r53_global_softcap_gate"
for path in (HERE, WRITEUP, SOFTCAP):
    sys.path.insert(0, str(path))

from ortools.sat.python import cp_model  # noqa: E402
from _codex_r20_c5_blowup_cpsat import build_model  # noqa: E402
from _codex_r20_c5_blowup_local_min_gate import rows_of, verify_graph  # noqa: E402
import global_softcap as soft  # noqa: E402
from exchange_gate import build_metric  # noqa: E402


T = 3
WITNESS = (12, 16, 11, 1, 5, 6, 26, 18, 22)


def chosen_tuple(solver, choose):
    return tuple(
        next(index for index, variable in enumerate(row) if solver.value(variable))
        for row in choose
    )


def solve_collision_minimum(workers, nearest_to=None):
    model, choose, _score, layers, info, families, state = build_model(T)
    collision = sum(state["collision"])
    if nearest_to is None:
        model.minimize(collision)
    else:
        optimum = nearest_to[0]
        witness = nearest_to[1]
        model.add(collision == optimum)
        model.maximize(sum(choose[index][choice] for index, choice in enumerate(witness)))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 230053
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        raise AssertionError(solver.status_name(status))
    choice = chosen_tuple(solver, choose)
    rows = rows_of(families, choice)
    ctx = soft.make_graph_context(5 * T, info["Bset"], info["Mset"])
    metric = build_metric(ctx, rows, force_full=True, p4_scope="unscoped")
    return {
        "status": solver.status_name(status),
        "collisionUnits": metric["collision"],
        "choice": list(choice),
        "hammingFromWitness": sum(a != b for a, b in zip(choice, WITNESS)),
        "flowDefect": metric["defect"],
        "maximumFlow": metric["flow"],
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }, (layers, info, families)


def nearest_strict_collision_descent(workers, old_collision):
    model, choose, _score, layers, info, families, state = build_model(T)
    collision = sum(state["collision"])
    model.add(collision < old_collision)
    model.maximize(
        sum(choose[index][choice] for index, choice in enumerate(WITNESS))
    )
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 230053
    status = solver.solve(model)
    if status == cp_model.INFEASIBLE:
        return {
            "status": solver.status_name(status),
            "collisionUpperBound": old_collision - 1,
            "meaning": "the witness is globally collision-minimal",
            "branches": solver.num_branches,
            "conflicts": solver.num_conflicts,
        }
    if status != cp_model.OPTIMAL:
        raise AssertionError(solver.status_name(status))
    choice = chosen_tuple(solver, choose)
    rows = rows_of(families, choice)
    ctx = soft.make_graph_context(5 * T, info["Bset"], info["Mset"])
    metric = build_metric(ctx, rows, force_full=True, p4_scope="unscoped")
    return {
        "status": solver.status_name(status),
        "collisionUnits": metric["collision"],
        "choice": list(choice),
        "hammingFromWitness": sum(a != b for a, b in zip(choice, WITNESS)),
        "flowDefect": metric["defect"],
        "maximumFlow": metric["flow"],
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }


def solve_min_capacity_loss(workers, collision_optimum):
    model, choose, _score, layers, info, families, state = build_model(T)
    collision = sum(state["collision"])
    model.add(collision == collision_optimum)
    unselected = sum(
        1 - state["covered"][(vertex, vertex)] for vertex in range(5 * T)
    )
    active = sum(state["active"].values())
    model.minimize(unselected + active)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 230053
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        raise AssertionError(solver.status_name(status))
    choice = chosen_tuple(solver, choose)
    rows = rows_of(families, choice)
    ctx = soft.make_graph_context(5 * T, info["Bset"], info["Mset"])
    metric = build_metric(ctx, rows, force_full=True, p4_scope="unscoped")
    state_value = metric["state"]
    unselected_value = (5 * T) - len(state_value.selected)
    active_value = len(state_value.active_edges)
    return {
        "status": solver.status_name(status),
        "choice": list(choice),
        "collisionUnits": metric["collision"],
        "unselectedVertices": unselected_value,
        "activeEdges": active_value,
        "minimumUnselectedPlusActive": unselected_value + active_value,
        "groupedCapacityUpperBound": 2 * (
            metric["collision"] - unselected_value - active_value
        ),
        "globalCollisionHalfDemand": 2 * metric["collision"],
        "predictedDefectLowerBound": 2 * (unselected_value + active_value),
        "actualFlowDefect": metric["defect"],
        "maximumFlow": metric["flow"],
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 1))
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("workers must be in 1..64")

    optimum, data = solve_collision_minimum(args.workers)
    layers, info, families = data
    graph_check = verify_graph(T, layers, info, families)
    ctx = soft.make_graph_context(5 * T, info["Bset"], info["Mset"])
    witness_metric = build_metric(
        ctx, rows_of(families, WITNESS), force_full=True, p4_scope="unscoped"
    )

    nearest_optimum, _ = solve_collision_minimum(
        args.workers, nearest_to=(optimum["collisionUnits"], WITNESS)
    )
    nearest_descent = nearest_strict_collision_descent(
        args.workers, witness_metric["collision"]
    )
    capacity_obstruction = solve_min_capacity_loss(
        args.workers, optimum["collisionUnits"]
    )
    exact_counterexample = (
        capacity_obstruction["minimumUnselectedPlusActive"] > 0
    )
    payload = {
        "schema": "CDC_WAVE1_C5_3_GLOBAL_COLLISION_MIN_V1",
        "arithmetic": "integer CP-SAT plus exact integral Dinic max flow",
        "graphCheck": graph_check,
        "witness": {
            "choice": list(WITNESS),
            "collisionUnits": witness_metric["collision"],
            "flowDefect": witness_metric["defect"],
            "maximumFlow": witness_metric["flow"],
        },
        "globalMinimum": optimum,
        "nearestGlobalMinimum": nearest_optimum,
        "nearestStrictCollisionDescent": nearest_descent,
        "capacityObstructionOnEntireOptimalFace": capacity_obstruction,
        "selectorVerdict": (
            "EXACT_COUNTEREXAMPLE_ALL_GLOBAL_MINIMA_FAIL"
            if exact_counterexample
            else "PASS_EXPLICIT_GLOBAL_MINIMUM"
            if (
                optimum["flowDefect"] == 0
                or nearest_optimum["flowDefect"] == 0
                or capacity_obstruction["actualFlowDefect"] == 0
            )
            else "OPTIMAL_FACE_UNDECIDED"
        ),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if payload["selectorVerdict"] != "OPTIMAL_FACE_UNDECIDED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
