#!/usr/bin/env python3
"""Independent exact verifier for the n=13 W144-MW counterexample."""
from __future__ import annotations

import json
import networkx as nx


def main():
    g = 7
    G = nx.cycle_graph(g)
    # A pendant path of five edges at cycle vertex 0.
    G.add_edges_from([(0, 7), (7, 8), (8, 9), (9, 10), (10, 11)])
    # The tested outside component H is the single leaf at cycle vertex 3.
    G.add_edge(3, 12)
    K = list(range(7))
    H = [12]
    z = 0

    dist = dict(nx.all_pairs_shortest_path_length(G))
    ecc = {v: max(dist[v].values()) for v in G}
    r = min(ecc.values())
    cycle_basis = nx.cycle_basis(G)
    girth = min(map(len, cycle_basis))
    attachments = sorted(a for a in K if any(G.has_edge(a, y) for y in H))

    rho = 13
    J = nx.Graph()
    J.add_nodes_from(H + [rho])
    J.add_edge(rho, 12)  # 12 attaches to 3 in K-{z}.
    jd = dict(nx.all_pairs_shortest_path_length(J))
    p = {y: jd[rho][y] for y in H}
    P = max(p[u] + p[v] + jd[u][v] for u in H for v in H)
    E_full = [sigma for sigma in K if max(dist[sigma][y] for y in H) >= r + 1]
    lam = 2 * r + 1 - girth
    graph6 = nx.to_graph6_bytes(G, header=False).decode().strip()

    record = dict(
        graph6=graph6,
        n=G.number_of_nodes(),
        edges=sorted(tuple(sorted(e)) for e in G.edges()),
        connected=nx.is_connected(G),
        girth=girth,
        radius=r,
        eccentricities=ecc,
        K=K,
        H=H,
        z=z,
        attachments=attachments,
        p=p,
        rooted_triameter=P,
        E_full=E_full,
        lambda_=lam,
        lhs=len(E_full) + lam,
        slack=P - len(E_full) - lam,
    )

    assert record["connected"]
    assert cycle_basis == [K] or len(cycle_basis) == 1
    assert girth == 7 and r == 5
    assert attachments == [3] and 3 != z
    assert p == {12: 1} and P == 2
    assert E_full == [] and lam == 4
    assert record["lhs"] == 4 > P and record["slack"] == -2
    assert graph6 == "LhCKK?@?G?_@C?"
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
