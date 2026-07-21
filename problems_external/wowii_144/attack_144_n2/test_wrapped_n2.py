#!/usr/bin/env python3
"""Exact falsifier for the wrapped reserved-capacity bridge."""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
W144 = HERE.parent
W141 = W144.parent / "wowii_141" / "oracle"
sys.path[:0] = [str(W141), str(W144 / "oracle"),
                str(W144 / "wave2"), str(W144 / "proverC")]

from test_gpt_n2 import (  # noqa: E402
    all_pairs_dist,
    bits,
    components_outside,
    dist_to_set,
    ecc_of_set,
    eccentricities,
    girth,
    mz_values,
    nx_to_bitadj,
    shortest_cycles,
)


def evaluate(G: nx.Graph):
    """Return exact best slack and witness data, or None off-regime."""
    if not nx.is_connected(G):
        return None
    G = nx.convert_node_labels_to_integers(G)
    n, adj = nx_to_bitadj(G)
    g = girth(n, adj)
    if g < 5:
        return None
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    r, D = min(ecc), max(ecc)
    center = sum(1 << v for v in range(n) if ecc[v] == r)
    e = ecc_of_set(n, dist, center)
    if e == 0 or e <= D - g // 2:
        return None
    realizers = [v for v in range(n) if dist_to_set(dist, v, center) == e]
    best = None
    data = None
    for K in shortest_cycles(G, g):
        kv = sorted(K)
        kmask = sum(1 << v for v in kv)
        comps = components_outside(adj, ((1 << n) - 1) & ~kmask)
        mz = mz_values(n, adj, kv)
        for x in realizers:
            h = dist_to_set(dist, x, kmask)
            if h >= e:
                return 0, ("tail", kv, x, h, e)
            for m in (a for a in kv if dist[x][a] == h):
                delta = e - h
                W = [a for a in kv if dist[a][m] <= delta - 1]
                covsum = sum(
                    sum(max(dist[s][y] for y in bits(H)) >= r + 1
                        for s in W)
                    for H in comps
                )
                correction = max(0, 2 * delta - g)
                for z in kv:
                    if z == m:
                        continue
                    slack = 2 * (mz[z] - h) - covsum - correction
                    if best is None or slack > best:
                        best = slack
                        data = (n, g, r, D, e, kv, x, h, m, z, delta,
                                W, covsum, correction, mz)
    return best, data


def main(argv: list[str]) -> None:
    for g6 in argv:
        G = nx.from_graph6_bytes(g6.encode())
        print(g6, evaluate(G))


if __name__ == "__main__":
    main(sys.argv[1:])
