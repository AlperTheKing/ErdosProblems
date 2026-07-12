#!/usr/bin/env python3
"""Targeted t=6 falsifier cell: CUT-TIGHT DOUBLE-STAR supports.

Round-1 farkas_dual Finding 5: kappa(doubleStar) = 2t - outward(F*-blue degree
of N_B(v) u N_B(m)) + (right-shore bads crossing).  Every archived t=5 fixture
had outward << 2t, hence intrinsic demand kappa >= t+1 concentrated at the
star -- the CheapGeometry kill.  The ONLY regime that beats the uniform demand
conjecture (I) is outward >= 2t, affordable within the t^2-1 edge budget for
t >= 6 (t=5: 10+10+~8 > 24 infeasible-ish; t=6: 12+12+~11 = 35 borderline).

This wrapper = rooted_tN_support_cp_sat engine + the constraint
    #edges(L minus {v,m} -> N_B(v) u N_B(m)) >= 2t
and per-hit exact post-hoc kappa reporting at the double-star switch.
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
    and2,
    build_rooted_support_model,
    canonical_sha,
    choose_minimal_circuit,
    distance_four_atoms,
    graph_from_solution,
    norm,
    verify_hit,
)


def add_cuttight_star_constraint(model, edge, left_n, right_n, t):
    """outward blue degree of N_B(v) u N_B(m) >= 2t."""
    outward_terms = []
    star_right = {}
    for r in range(right_n):
        o = model.new_bool_var(f"starR_{r}")
        model.add(o >= edge[V, r])
        model.add(o >= edge[M, r])
        model.add(o <= edge[V, r] + edge[M, r])
        star_right[r] = o
    for u in range(left_n):
        if u in (V, M):
            continue
        for r in range(right_n):
            w = and2(model, edge[u, r], star_right[r], f"outw_{u}_{r}")
            outward_terms.append(w)
    model.add(sum(outward_terms) >= 2 * t)
    return outward_terms


def double_star_kappa(graph: nx.Graph, bad_edges, t: int):
    """Exact kappa at S* = {v,m} u N_B(v) u N_B(m) for a realized hit."""
    star = {V, M} | set(graph[V]) | set(graph[M])
    blue_cross = sum(1 for u, w in graph.edges() if (u in star) != (w in star))
    bad_cross = sum(1 for u, w in bad_edges if (u in star) != (w in star))
    return {
        "switch": sorted(star),
        "badCross": bad_cross,
        "blueCross": blue_cross,
        "kappa": bad_cross - blue_cross,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, default=6)
    parser.add_argument("--left", type=int, required=True)
    parser.add_argument("--right", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-supports", type=int, default=100)
    parser.add_argument("--support-time", type=float, default=60.0)
    parser.add_argument("--circuit-time", type=float, default=240.0)
    parser.add_argument("--max-hits", type=int, default=3)
    parser.add_argument(
        "--no-scope",
        action="store_true",
        help="harvest classifier-passing circuits without the scope gate",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    t = args.t

    model, edge = build_rooted_support_model(args.left, args.right, t)
    add_cuttight_star_constraint(model, edge, args.left, args.right, t)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.support_time
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = 1

    result = {
        "schema": "rooted-tN-cuttight-star-search-v1",
        "t": t,
        "left": args.left,
        "right": args.right,
        "workers": args.workers,
        "supportLimit": args.max_supports,
        "outwardStarDegreeMin": 2 * t,
        "localClassifier": "v",
        "requireActiveScope": not args.no_scope,
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
                not args.no_scope,
            )
            result["circuitStatuses"][circuit_status] = (
                result["circuitStatuses"].get(circuit_status, 0) + 1
            )
            if chosen is not None:
                verify_hit(graph, atoms, chosen, t)
                bads = [
                    norm(atoms[i]["u"], atoms[i]["v"]) for i in chosen
                ]
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
        "HIT_CUTTIGHT_STAR_CIRCUIT"
        if result["hits"]
        else "NO_HIT_WITHIN_EXPLICIT_LIMIT"
    )
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
