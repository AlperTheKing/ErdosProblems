#!/usr/bin/env python3
"""Rebuild a t=5 local-classifier hit payload on a pinned support graph.

The paper prints the graph6 strings of the two order-18 support graphs
(#298, #264) but the original hashed hit payloads are session records that
were not retained.  This script regenerates a payload in the exact schema
consumed by ``verify_t5_local_classifier_hit.py`` and
``extend_t5_hit_maxcut.py``: it fixes the printed support graph, recomputes
the complete same-class distance-four atom supply exactly (NetworkX shortest
paths), and reruns the archived engine's own circuit stage
(``choose_minimal_circuit`` from ``rooted_t5_support_cp_sat.py``, imported,
not re-implemented) with the production constraints: 25 selected atoms
including the rotor atom {2,3}, owner bad degree five at both middles,
triangle-free bad graph, support multiplicity >= 2, all 25 deletion-SDR
certificates, and the zero-vector local classifier at the recorded
(owner, active) pair.

The emitted witness is a primary CP-SAT artifact; it must be replayed with
the independent exact verifier before use.  A failure to find a witness is
reported honestly and exits nonzero.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "rooted_t5_support_cp_sat", HERE / "rooted_t5_support_cp_sat.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph6", required=True)
    parser.add_argument("--left", type=int, default=9)
    parser.add_argument("--right", type=int, default=9)
    parser.add_argument("--owner", type=int, default=0)
    parser.add_argument("--active", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--circuit-time", type=float, default=300.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must lie in 1..8")

    engine = load_engine()

    graph = nx.from_graph6_bytes(args.graph6.encode("ascii"))
    left_n, right_n = args.left, args.right
    n = left_n + right_n
    if graph.number_of_nodes() != n:
        raise SystemExit("graph order does not match the declared shores")
    if graph.number_of_edges() != 24:
        raise SystemExit("support graph must have 24 edges")
    if not nx.is_connected(graph):
        raise SystemExit("support graph must be connected")
    left = set(range(left_n))
    right = set(range(left_n, n))
    for u, v in graph.edges():
        if (u in left) == (v in left):
            raise SystemExit("support graph is not bipartite along shores 0..left-1 / left..n-1")
    reencoded = nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()
    if reencoded != args.graph6:
        raise SystemExit("graph6 round trip failed")
    if args.owner != 0:
        raise SystemExit("the independent verifier is rooted at owner 0")
    if graph.degree[0] != 5 or graph.degree[1] != 5:
        raise SystemExit("both middles must have support degree five")
    if args.active not in graph[args.owner]:
        raise SystemExit("active vertex is not a support neighbour of the owner")

    atoms = engine.distance_four_atoms(graph, left_n, right_n)
    chosen, status, meta = engine.choose_minimal_circuit(
        graph,
        atoms,
        left_n,
        right_n,
        workers=args.workers,
        time_limit=args.circuit_time,
        minimize_core_deficit=False,
        max_core_deficit=None,
        require_two_owner_profile=False,
        require_live_transition_profile=False,
        require_shared_bad_neighbour=False,
        owner_row_count=None,
        support_min_multiplicity=2,
        require_deletion_sdr=True,
        require_bad_triangle_free=True,
        selected_atom_count=25,
        owner_bad_degree=5,
        classifier_owners=(args.owner,),
        require_active_scope=False,
        classifier_active_min_degree=0,
        classifier_allowed_active=frozenset({args.active}),
    )
    if chosen is None:
        print(json.dumps({"verdict": "NO_WITNESS", "circuitStatus": status}, indent=2))
        raise SystemExit(1)

    # The engine's own exact acceptance layer (NetworkX, no solver).
    engine.verify_hit(
        graph,
        atoms,
        chosen,
        support_min_multiplicity=2,
        require_deletion_sdr=True,
        require_bad_triangle_free=True,
        selected_atom_count=25,
    )

    result = {
        "schema": "rooted-t5-local-classifier-hit-rebuild-v1",
        "left": left_n,
        "right": right_n,
        "workers": args.workers,
        "inputGraph6": args.graph6,
        "classifierOwner": args.owner,
        "classifierActiveNeighbour": args.active,
        "supportMinMultiplicity": 2,
        "requireDeletionSdr": True,
        "requireBadTriangleFree": True,
        "selectedAtomCount": 25,
        "ownerBadDegree": 5,
        "localClassifier": "v",
        "circuitStatus": status,
        "atomSupply": len(atoms),
        "hit": {
            "supportEdges": [list(edge) for edge in sorted(graph.edges())],
            "graph6": reencoded,
            "atomCountAvailable": len(atoms),
            "selectionMeta": meta,
            "selectedAtoms": [
                {
                    "shore": atoms[i]["shore"],
                    "u": atoms[i]["u"],
                    "v": atoms[i]["v"],
                    "rows": [list(row) for row in atoms[i]["rows"]],
                    "footprintEdges": [list(e) for e in atoms[i]["footprintEdges"]],
                }
                for i in chosen
            ],
        },
        "scope": (
            "circuit rebuild on the pinned printed support graph via the archived "
            "engine's circuit stage; primary CP-SAT witness, replay it with "
            "verify_t5_local_classifier_hit.py before use"
        ),
    }
    result["canonicalSha256"] = engine.canonical_sha(result)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["circuitStatus", "atomSupply", "canonicalSha256"]}, indent=2))


if __name__ == "__main__":
    main()
