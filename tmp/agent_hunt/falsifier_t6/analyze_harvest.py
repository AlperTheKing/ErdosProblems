#!/usr/bin/env python3
"""Post-analysis of harvested t=6 classifier-passing circuits (gate-a survivors).

Per hit:
  1. replay classifier vector exactly (must be (0,0,0,0));
  2. exhaustive intrinsic scope CP-SAT for the recorded (owner, active):
     INFEASIBLE = scope-vacuity certificate over ALL profile-consistent
     row selections (the R49/R50 fallback statement at t=6);
  3. round-1 SC / CommonNeighbourBlanket structure: deg(x0), coverage fibers
     C_y = N(x0) cap N(y) minus {v} per star pair, singleton-fiber map;
  4. double-star kappa + exact min displayed-cut sigma (CP-SAT OPTIMAL).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from verify_tN_hit import all_atoms, local_vector, min_sigma_cpsat, norm
from rooted_tN_support_cp_sat import active_scope_profile_for_fixed_selection
from sweep_t6_cuttight_star import double_star_kappa


def main():
    src = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    t = src["t"]
    left_n, right_n = src["left"], src["right"]
    out = {"schema": "t6-harvest-scope-analysis-v1", "t": t, "hits": []}
    for hit_idx, hit in enumerate(src["hits"]):
        graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
        atoms = all_atoms(graph, left_n, right_n)
        atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
        chosen = [
            atom_index[(r["shore"], r["u"], r["v"])] for r in hit["selectedAtoms"]
        ]
        bad_edges = sorted(norm(atoms[i]["u"], atoms[i]["v"]) for i in chosen)
        owner_key = sorted(hit["selectionMeta"]["localClassifiers"])[0]
        owner = int(owner_key)
        classifier = hit["selectionMeta"]["localClassifiers"][owner_key]
        active = classifier["activeNeighbour"]

        vec = local_vector(atoms, chosen, graph, owner, active, t)
        vector = [vec["eForced"], vec["iStep"], vec["dStep"], vec["dCoverage"]]

        witness, scope_status = active_scope_profile_for_fixed_selection(
            graph, atoms, chosen, owner, active, t, workers=8, time_limit=300.0
        )

        neighbours = sorted(graph[owner])
        fibers = {}
        for y in neighbours:
            if y == active:
                continue
            common = (set(graph[active]) & set(graph[y])) - {owner}
            fibers[str(y)] = sorted(common)
        singleton_fibers = {y: c for y, c in fibers.items() if len(c) == 1}
        x0_edges = [w for w in sorted(graph[active]) if w != owner]
        forced_edges = sorted(
            {c[0] for c in singleton_fibers.values()}
        )
        sc_blanket = set(forced_edges) == set(x0_edges)

        sigma, status = min_sigma_cpsat(
            len(graph),
            sorted(norm(*e) for e in graph.edges()),
            bad_edges,
            workers=8,
            time_limit=300.0,
        )
        out["hits"].append(
            {
                "hitIndex": hit_idx,
                "graph6": hit["graph6"],
                "owner": owner,
                "active": active,
                "classifierVector": vector,
                "scopeStatus": scope_status,
                "scopeWitness": None
                if witness is None
                else {
                    "scopeBadEdge": witness["scopeBadEdge"],
                    "activeEdgeCount": len(witness["activeEdges"]),
                },
                "degX0": graph.degree[active],
                "coverageFibers": fibers,
                "singletonFiberForcedEdges": forced_edges,
                "x0NonOwnerNbrs": x0_edges,
                "scBlanketCertificate": sc_blanket,
                "doubleStarKappa": double_star_kappa(graph, bad_edges, t),
                "minSigma": None if sigma is None else sigma[0],
                "minSigmaStatus": status,
            }
        )
        print(json.dumps(out["hits"][-1], indent=1, sort_keys=True), flush=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
