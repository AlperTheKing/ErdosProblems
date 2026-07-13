#!/usr/bin/env python3
"""Try to extend the rooted t=5 support hit to a 25-vertex maximum cut.

Only blue edges incident with one of the seven ambient vertices may be added.
The script enforces triangle-freeness, preserves the complete shortest-row
footprint of every selected bad atom, and lazily separates every violated
maximum-cut switch inequality exactly with CP-SAT.

A hit is a real graph/cut/complete-row cage through the minimal-circuit layer.
A no-hit under a time/iteration limit is not a proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def xor_var(model: cp_model.CpModel, a, b, name: str):
    out = model.new_bool_var(name)
    model.add(out >= a - b)
    model.add(out >= b - a)
    model.add(out <= a + b)
    model.add(out <= 2 - a - b)
    return out


def separating_switch(
    vertex_count: int,
    blue_edges: list[tuple[int, int]],
    bad_edges: list[tuple[int, int]],
    workers: int,
    time_limit: float,
):
    model = cp_model.CpModel()
    side = [model.new_bool_var(f"side_{v}") for v in range(vertex_count)]
    model.add(side[0] == 0)
    blue_cross = [
        xor_var(model, side[u], side[v], f"bc_{i}")
        for i, (u, v) in enumerate(blue_edges)
    ]
    bad_cross = [
        xor_var(model, side[u], side[v], f"mc_{i}")
        for i, (u, v) in enumerate(bad_edges)
    ]
    model.minimize(sum(blue_cross) - sum(bad_cross))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = min(workers, 8)
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, solver.status_name(status)
    switch = {v for v in range(vertex_count) if solver.value(side[v])}
    sigma = sum((u in switch) ^ (v in switch) for u, v in blue_edges) - sum(
        (u in switch) ^ (v in switch) for u, v in bad_edges
    )
    return (sigma, switch), solver.status_name(status)


def build_split_model(
    existing_left: set[int],
    existing_right: set[int],
    new_left: set[int],
    new_right: set[int],
    fixed_blue: set[tuple[int, int]],
    bad_edges: set[tuple[int, int]],
    allow_existing_extra: bool,
):
    model = cp_model.CpModel()
    left = existing_left | new_left
    right = existing_right | new_right
    new_vertices = new_left | new_right
    potential = {}
    for u in sorted(left):
        for v in sorted(right):
            edge = norm(u, v)
            if edge in fixed_blue:
                continue
            if not allow_existing_extra and u not in new_vertices and v not in new_vertices:
                continue
            potential[edge] = model.new_bool_var(f"e_{edge[0]}_{edge[1]}")

    def edge_expr(u: int, v: int):
        edge = norm(u, v)
        if edge in fixed_blue:
            return 1
        return potential.get(edge, 0)

    # A bad edge and two blue edges cannot form a triangle.
    for u, v in bad_edges:
        opposite = right if u in left else left
        for z in opposite:
            model.add(edge_expr(u, z) + edge_expr(v, z) <= 1)

    model.minimize(sum(potential.values()))
    return model, potential


def canonical_sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--solve-time", type=float, default=20.0)
    parser.add_argument("--allow-existing-extra", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must lie in 1..8")

    source = json.loads(args.payload.read_text(encoding="utf-8"))
    hit = source["hit"]
    if hit is None:
        raise SystemExit("source has no hit")
    existing_n = source["left"] + source["right"]
    if existing_n != 18:
        raise SystemExit("this first extension harness expects the 18-vertex hit")

    fixed_blue = {norm(*edge) for edge in hit["supportEdges"]}
    bad_edges = {norm(atom["u"], atom["v"]) for atom in hit["selectedAtoms"]}
    original_footprints = {
        norm(atom["u"], atom["v"]): {norm(*edge) for edge in atom["footprintEdges"]}
        for atom in hit["selectedAtoms"]
    }
    existing_left = set(range(source["left"]))
    existing_right = set(range(source["left"], existing_n))
    all_new = list(range(existing_n, 25))

    result = {
        "schema": "rooted-t5-ambient-maxcut-extension-v1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "workers": args.workers,
        "iterationLimitPerSplit": args.iterations,
        "allowExistingExtraBlue": args.allow_existing_extra,
        "splits": [],
        "hit": None,
        "scope": "exact lazy separation; UNKNOWN/limit is not a proof",
    }

    for left_extra in range(8):
        new_left = set(all_new[:left_extra])
        new_right = set(all_new[left_extra:])
        model, potential = build_split_model(
            existing_left,
            existing_right,
            new_left,
            new_right,
            fixed_blue,
            bad_edges,
            args.allow_existing_extra,
        )
        split_record = {
            "newLeft": left_extra,
            "newRight": 7 - left_extra,
            "iterations": 0,
            "rowPathCuts": 0,
            "pathCuts": [],
            "maxCutCuts": 0,
            "separators": [],
            "status": None,
        }

        for _ in range(args.iterations):
            split_record["iterations"] += 1
            solver = cp_model.CpSolver()
            solver.parameters.num_search_workers = args.workers
            solver.parameters.max_time_in_seconds = args.solve_time
            solver.parameters.random_seed = 1
            status = solver.solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                split_record["status"] = solver.status_name(status)
                break
            added = {edge for edge, var in potential.items() if solver.value(var)}
            blue = fixed_blue | added
            blue_graph = nx.Graph()
            blue_graph.add_nodes_from(range(25))
            blue_graph.add_edges_from(blue)

            # Preserve the complete shortest-row union exactly.  Each newly
            # found length-four row contributes a concrete forbidden path cut.
            violating_paths = {}
            for bad, original in original_footprints.items():
                u, v = bad
                if nx.shortest_path_length(blue_graph, u, v) != 4:
                    raise AssertionError("triangle constraints should preserve distance four")
                for path in nx.all_shortest_paths(blue_graph, u, v):
                    path_edges = tuple(norm(path[i], path[i + 1]) for i in range(4))
                    if any(edge not in original for edge in path_edges):
                        variable_edges = tuple(sorted(edge for edge in path_edges if edge in potential))
                        if not variable_edges:
                            raise AssertionError("new fixed shortest path")
                        violating_paths.setdefault(
                            variable_edges,
                            {
                                "badEdge": list(bad),
                                "pathEdges": [list(edge) for edge in path_edges],
                                "variableEdges": [list(edge) for edge in variable_edges],
                            },
                        )
            if violating_paths:
                for path_edges, witness in violating_paths.items():
                    model.add(sum(potential[edge] for edge in path_edges) <= len(path_edges) - 1)
                    split_record["pathCuts"].append(witness)
                split_record["rowPathCuts"] += len(violating_paths)
                continue

            separation, sep_status = separating_switch(
                25,
                sorted(blue),
                sorted(bad_edges),
                args.workers,
                args.solve_time,
            )
            if separation is None:
                split_record["status"] = "SEPARATION_" + sep_status
                break
            sigma, switch = separation
            if sigma < 0:
                fixed_cross = sum((u in switch) ^ (v in switch) for u, v in fixed_blue)
                bad_cross = sum((u in switch) ^ (v in switch) for u, v in bad_edges)
                variable_cross = [
                    var
                    for (u, v), var in potential.items()
                    if (u in switch) ^ (v in switch)
                ]
                model.maximize(sum(variable_cross))
                capacity_solver = cp_model.CpSolver()
                capacity_solver.parameters.num_search_workers = args.workers
                capacity_solver.parameters.max_time_in_seconds = args.solve_time
                capacity_solver.parameters.random_seed = 1
                capacity_status = capacity_solver.solve(model)
                capacity = None
                manual_capacity = None
                if capacity_status == cp_model.OPTIMAL:
                    capacity = int(round(capacity_solver.objective_value))
                    manual_capacity = sum(capacity_solver.value(var) for var in variable_cross)
                split_record["separators"].append(
                    {
                        "switch": sorted(switch),
                        "sigmaBeforeCut": sigma,
                        "fixedBlueCross": fixed_cross,
                        "badCross": bad_cross,
                        "requiredVariableBlueCross": bad_cross - fixed_cross,
                        "potentialVariableCross": len(variable_cross),
                        "prePathClosureCapacityStatus": capacity_solver.status_name(capacity_status),
                        "prePathClosureMaximumVariableCross": capacity,
                        "prePathClosureManualVariableCross": manual_capacity,
                    }
                )
                model.add(fixed_cross + sum(variable_cross) >= bad_cross)
                split_record["maxCutCuts"] += 1
                continue

            full_graph = nx.Graph()
            full_graph.add_nodes_from(range(25))
            full_graph.add_edges_from(blue)
            full_graph.add_edges_from(bad_edges)
            if any(nx.triangles(full_graph).values()):
                raise AssertionError("triangle-free master constraint failed")
            split_record["status"] = "HIT"
            result["hit"] = {
                "newLeft": sorted(new_left),
                "newRight": sorted(new_right),
                "addedBlueEdges": [list(edge) for edge in sorted(added)],
                "totalBlueEdges": len(blue),
                "badEdges": [list(edge) for edge in sorted(bad_edges)],
                "minimumSwitchSigma": sigma,
            }
            break
        else:
            split_record["status"] = "ITERATION_LIMIT"

        result["splits"].append(split_record)
        if result["hit"] is not None:
            break

    result["verdict"] = (
        "HIT_25_VERTEX_MAXCUT_ROW_PRESERVING_EXTENSION"
        if result["hit"] is not None
        else "NO_HIT_OR_INFEASIBLE_BY_RECORDED_SPLIT_STATUS"
    )
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
