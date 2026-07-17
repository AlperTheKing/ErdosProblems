#!/usr/bin/env python3
"""Exact CP-SAT active-scope gate for a fixed t=5 local-profile circuit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ortools.sat.python import cp_model


def norm(u, v):
    return (u, v) if u < v else (v, u)


def canonical_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--time", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must lie in 1..8")

    source = json.loads(args.input.read_text(encoding="utf-8"))
    source_sha = source["canonicalSha256"]
    hit = source["hit"]
    owner = 0
    active = hit["selectionMeta"]["localClassifiers"][str(owner)][
        "activeNeighbour"
    ]
    support_edges = sorted(norm(*edge) for edge in hit["supportEdges"])
    atoms = hit["selectedAtoms"]
    vertex_count = source["left"] + source["right"]

    model = cp_model.CpModel()
    rows = []
    for i, atom in enumerate(atoms):
        row_vars = [model.new_bool_var(f"row_{i}_{j}") for j in range(len(atom["rows"]))]
        model.add(sum(row_vars) == 1)
        rows.append(row_vars)

    def row_terms(predicate):
        return [
            rows[i][j]
            for i, atom in enumerate(atoms)
            for j, row in enumerate(atom["rows"])
            if predicate(tuple(row))
        ]

    selected_support = {}
    for edge in support_edges:
        uses = row_terms(
            lambda row, e=edge: e in {norm(row[k], row[k + 1]) for k in range(4)}
        )
        present = model.new_bool_var(f"support_{edge[0]}_{edge[1]}")
        model.add(sum(uses) >= present)
        model.add(sum(uses) <= 25 * present)
        selected_support[edge] = present

    neighbours = sorted(v for edge in support_edges for v in edge if owner in edge and v != owner)
    model.add(sum(row_terms(lambda row: owner in row)) == 5)
    for neighbour in neighbours:
        present = selected_support[norm(owner, neighbour)]
        model.add(present == (0 if neighbour == active else 1))
        if neighbour != active:
            model.add(
                sum(row_terms(lambda row, y=neighbour: active in row and y in row))
                >= 1
            )
    model.add(sum(row_terms(lambda row: active in row)) >= 1)

    active_edge = {}
    for edge, present in selected_support.items():
        active_var = model.new_bool_var(f"active_{edge[0]}_{edge[1]}")
        model.add(active_var + present == 1)
        active_edge[edge] = active_var

    scope_atom = [model.new_bool_var(f"scope_atom_{i}") for i in range(25)]
    model.add(sum(scope_atom) == 1)
    directed = [(u, v, edge) for edge in support_edges for u, v in [edge, edge[::-1]]]
    flows = []
    for commodity in range(2):
        flow = {}
        for u, v, edge in directed:
            var = model.new_bool_var(f"flow_{commodity}_{u}_{v}")
            model.add(var <= active_edge[edge])
            flow[u, v] = var
        flows.append(flow)
        for z in range(vertex_count):
            outflow = sum(var for (u, _), var in flow.items() if u == z)
            inflow = sum(var for (_, v), var in flow.items() if v == z)
            sink = sum(
                scope_atom[i]
                for i, atom in enumerate(atoms)
                if atom["u" if commodity == 0 else "v"] == z
            )
            model.add(outflow - inflow == (1 if z == owner else 0) - sink)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    solver.parameters.max_time_in_seconds = args.time
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    result = {
        "schema": "t5-active-scope-profile-gate-v1",
        "sourceCanonicalSha256": source_sha,
        "owner": owner,
        "activeNeighbour": active,
        "status": solver.status_name(status),
        "scopeWitness": None,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen_rows = [
            atom["rows"][next(j for j, var in enumerate(rows[i]) if solver.value(var))]
            for i, atom in enumerate(atoms)
        ]
        scope = next(i for i, var in enumerate(scope_atom) if solver.value(var))
        result["scopeWitness"] = {
            "atomIndex": scope,
            "badEdge": [atoms[scope]["u"], atoms[scope]["v"]],
            "selectedRows": chosen_rows,
            "activeEdges": [
                list(edge) for edge, var in active_edge.items() if solver.value(var)
            ],
            "flows": [
                [[u, v] for (u, v), var in flow.items() if solver.value(var)]
                for flow in flows
            ],
        }
        result["verdict"] = "HIT_POSITIVE_ACTIVE_SCOPE_PROFILE"
    else:
        result["verdict"] = "NO_ACTIVE_SCOPE_PROFILE_FOR_FIXED_CIRCUIT"
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
