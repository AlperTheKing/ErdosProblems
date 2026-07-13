#!/usr/bin/env python3
"""Targeted t=6 falsifier cell: SHARED-STAR (K_{2,6} core) supports.

Corpus motif (R46 near-candidate, cm_check3, R49 bounce): every archived
near-miss realizes N_B(v) = N_B(m).  This wrapper forces edge[m,r] == edge[v,r]
for every right vertex r, optionally adds the cut-tight outward >= 2t
constraint, then runs the standard circuit/classifier/scope loop.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import networkx as nx
from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).parent))
from rooted_tN_support_cp_sat import (
    V,
    M,
    build_rooted_support_model,
    canonical_sha,
    choose_minimal_circuit,
    distance_four_atoms,
    graph_from_solution,
    norm,
    verify_hit,
)
from sweep_t6_cuttight_star import add_cuttight_star_constraint, double_star_kappa


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, default=6)
    parser.add_argument("--left", type=int, required=True)
    parser.add_argument("--right", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-supports", type=int, default=120)
    parser.add_argument("--support-time", type=float, default=60.0)
    parser.add_argument("--circuit-time", type=float, default=240.0)
    parser.add_argument("--cuttight", action="store_true")
    parser.add_argument("--max-hits", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    t = args.t

    model, edge = build_rooted_support_model(args.left, args.right, t)
    for r in range(args.right):
        model.add(edge[M, r] == edge[V, r])
    if args.cuttight:
        add_cuttight_star_constraint(model, edge, args.left, args.right, t)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.support_time
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = 1

    result = {
        "schema": "rooted-tN-shared-star-search-v1",
        "t": t,
        "left": args.left,
        "right": args.right,
        "workers": args.workers,
        "supportLimit": args.max_supports,
        "sharedStar": True,
        "cuttight": bool(args.cuttight),
        "localClassifier": "v",
        "requireActiveScope": True,
        "supportsSolved": 0,
        "supportsWithEnoughAtoms": 0,
        "circuitStatuses": {},
        "hits": [],
        "scope": "falsifier search; a no-hit is not a proof",
    }

    for _ in range(args.max_supports):
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            result["supportTerminalStatus"] = solver.status_name(status)
            break
        result["supportsSolved"] += 1
        graph = graph_from_solution(solver, edge, args.left, args.right)
        atoms = distance_four_atoms(graph, args.left, args.right)
        if len(atoms) >= t * t:
            result["supportsWithEnoughAtoms"] += 1
            chosen, circuit_status, selection_meta = choose_minimal_circuit(
                graph,
                atoms,
                args.left,
                args.right,
                t,
                args.workers,
                args.circuit_time,
                (V,),
                True,
            )
            result["circuitStatuses"][circuit_status] = (
                result["circuitStatuses"].get(circuit_status, 0) + 1
            )
            if chosen is not None:
                verify_hit(graph, atoms, chosen, t)
                bads = [norm(atoms[i]["u"], atoms[i]["v"]) for i in chosen]
                result["hits"].append(
                    {
                        "supportEdges": [list(e) for e in sorted(graph.edges())],
                        "graph6": nx.to_graph6_bytes(graph, header=False)
                        .decode("ascii")
                        .strip(),
                        "atomCountAvailable": len(atoms),
                        "selectionMeta": selection_meta,
                        "doubleStarKappa": double_star_kappa(graph, bads, t),
                        "selectedAtoms": [
                            {
                                "shore": atoms[i]["shore"],
                                "u": atoms[i]["u"],
                                "v": atoms[i]["v"],
                                "rows": [list(row) for row in atoms[i]["rows"]],
                                "footprintEdges": [
                                    list(e) for e in atoms[i]["footprintEdges"]
                                ],
                            }
                            for i in chosen
                        ],
                    }
                )
                if len(result["hits"]) >= args.max_hits:
                    break

        differences = []
        for var in edge.values():
            differences.append(1 - var if solver.value(var) else var)
        model.add(sum(differences) >= 1)
    else:
        result["supportTerminalStatus"] = "LIMIT_REACHED"

    result["verdict"] = (
        "HIT_SHARED_STAR_CIRCUIT" if result["hits"] else "NO_HIT_WITHIN_EXPLICIT_LIMIT"
    )
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
