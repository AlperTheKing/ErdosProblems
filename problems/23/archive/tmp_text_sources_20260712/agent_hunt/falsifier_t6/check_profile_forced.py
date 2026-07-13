#!/usr/bin/env python3
"""Which support edges are ProfileForced (R50): some chosen atom's EVERY
row uses the edge?  Cross-check against the exact per-edge forcing landscape.
Residual = edges FORCED in the landscape but NOT ProfileForced => genuinely
profile-layer (selection-interaction) forced."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

import sys
sys.path.insert(0, str(Path(__file__).parent))
from verify_tN_hit import all_atoms, norm


def main():
    src = json.loads(Path("t6_cuttight_l12_r9_harvest.json").read_text())
    left_n, right_n = src["left"], src["right"]
    hit = src["hits"][0]
    graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = [atom_index[(r["shore"], r["u"], r["v"])] for r in hit["selectedAtoms"]]

    landscape = json.loads(Path("t6_fixture_forcing.json").read_text())
    support_edges = sorted(norm(*e) for e in graph.edges())

    profile_forced = {}
    for e in support_edges:
        holders = [
            i
            for i in chosen
            if all(
                e in {norm(row[k], row[k + 1]) for k in range(4)}
                for row in atoms[i]["rows"]
            )
        ]
        profile_forced[e] = holders

    rows = []
    for e in support_edges:
        land = landscape["edges"]["%d-%d" % e]
        pf = bool(profile_forced[e])
        rows.append((e, land, "ProfileForced" if pf else "-", len(profile_forced[e])))
    residual = [
        e for e in support_edges
        if landscape["edges"]["%d-%d" % e] == "FORCED" and not profile_forced[e]
    ]
    consistent = [
        e for e in support_edges
        if landscape["edges"]["%d-%d" % e] == "LATENT_OK" and profile_forced[e]
    ]
    for r in rows:
        print(r)
    print("ProfileForced count:", sum(1 for e in support_edges if profile_forced[e]))
    print("landscape FORCED count:", sum(1 for e in support_edges if landscape['edges']['%d-%d' % e] == 'FORCED'))
    print("RESIDUAL (forced but not ProfileForced):", residual)
    print("CONTRADICTIONS (latent-ok but ProfileForced):", consistent)
    assert not consistent, "ProfileForced must imply landscape FORCED"
    out = {
        "profileForcedEdges": ["%d-%d" % e for e in support_edges if profile_forced[e]],
        "residualForcedEdges": ["%d-%d" % e for e in residual],
    }
    Path("t6_fixture_profileforced.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
