#!/usr/bin/env python3
"""Structural analysis of a bare (no-classifier) tN circuit hit.

For each owner in {v=0, m=1} and each active neighbour choice, compute the
exact four-number classifier vector (eForced, iStep, dStep, dCoverage) over
the chosen atom set; report the lex-min.  Plus double-star kappa and the
exact min displayed-cut sigma (CP-SAT OPTIMAL; brute Gray-code cross-check
when order <= 26).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))
from verify_tN_hit import all_atoms, local_vector, min_sigma_cpsat, norm
from sweep_t6_cuttight_star import double_star_kappa


def main():
    src = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    t = src["t"]
    left_n, right_n = src["left"], src["right"]
    hit = src["hits"][0]
    graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = [
        atom_index[(rec["shore"], rec["u"], rec["v"])] for rec in hit["selectedAtoms"]
    ]
    bad_edges = sorted(norm(atoms[i]["u"], atoms[i]["v"]) for i in chosen)

    report = {"t": t, "left": left_n, "right": right_n, "order": left_n + right_n}
    vectors = {}
    for owner in (0, 1):
        if graph.degree[owner] != t:
            vectors[str(owner)] = f"OWNER_DEGREE_{graph.degree[owner]}"
            continue
        owner_bad = sum(owner in e for e in bad_edges)
        per_active = {}
        for active in sorted(graph[owner]):
            vec = local_vector(atoms, chosen, graph, owner, active, t)
            per_active[str(active)] = [
                vec["eForced"], vec["iStep"], vec["dStep"], vec["dCoverage"]
            ]
        vectors[str(owner)] = {
            "ownerBadDegree": owner_bad,
            "perActive": per_active,
            "lexMin": min(per_active.values()),
        }
    report["classifierVectors"] = vectors
    report["doubleStarKappa"] = double_star_kappa(graph, bad_edges, t)
    sigma, status = min_sigma_cpsat(len(graph), sorted(map(norm, *[zip(*[(e for e in graph.edges())])])) if False else sorted(norm(*e) for e in graph.edges()), bad_edges, workers=8, time_limit=300.0)
    report["minSigma"] = None if sigma is None else sigma[0]
    report["minSigmaSwitch"] = None if sigma is None else sorted(sigma[1])
    report["minSigmaStatus"] = status
    print(json.dumps(report, indent=1, sort_keys=True))
    Path(sys.argv[2]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
