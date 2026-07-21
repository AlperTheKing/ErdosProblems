#!/usr/bin/env python3
"""Run the exact GPT-Pro N2 falsifier on the bounded local corpus."""
from __future__ import annotations

import random

import networkx as nx

from test_gpt_n2 import (bits, components_outside, mz_values, nx_to_bitadj,
                         all_pairs_dist, eccentricities, ecc_of_set,
                         dist_to_set, girth, shortest_cycles, graph6)
from bridge_tests import adversarial_graphs
from route_b_tests import (cycle_random_legs, cycle_random_trees, chorded_cycle,
                           forced_girth_random, gen_theta, trap_family)
from sweep_families import build_family_graphs, random_graphs


def main():
    rng = random.Random(20260718)
    corpus = [("atlas", G) for G in nx.graph_atlas_g()]
    corpus += build_family_graphs()
    corpus += random_graphs(random.Random(20260718))
    corpus += adversarial_graphs() + trap_family()
    for _ in range(300):
        corpus.extend((cycle_random_legs(rng), cycle_random_trees(rng),
                       chorded_cycle(rng), gen_theta(rng)))
    got = tries = 0
    while got < 200 and tries < 5000:
        tries += 1
        q = forced_girth_random(rng, gmin=5)
        if q is not None:
            corpus.append(q)
            got += 1

    checked = 0
    failures = []
    seen = set()
    for name, G in corpus:
        if G.number_of_nodes() < 5 or not nx.is_connected(G):
            continue
        G = nx.convert_node_labels_to_integers(G)
        n, adj = nx_to_bitadj(G)
        g = girth(n, adj)
        if g < 5 or n - g > 15:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        r, D = min(ecc), max(ecc)
        cmask = sum(1 << v for v in range(n) if ecc[v] == r)
        e, s = ecc_of_set(n, dist, cmask), g // 2
        if e == 0 or e <= D - s:
            continue
        realizers = [v for v in range(n) if dist_to_set(dist, v, cmask) == e]
        ok = False
        last = None
        for K in shortest_cycles(G, g):
            kverts = sorted(K)
            kmask = sum(1 << v for v in kverts)
            comps = components_outside(adj, ((1 << n) - 1) & ~kmask)
            mz = mz_values(n, adj, kverts)
            for x in realizers:
                h = dist_to_set(dist, x, kmask)
                if h >= e:
                    ok = True
                    break
                for m in (a for a in kverts if dist[x][a] == h):
                    W = [a for a in kverts if dist[a][m] <= e - h - 1]
                    covsum = sum(sum(max(dist[sig][y] for y in bits(H)) >= r + 1
                                     for sig in W) for H in comps)
                    if any(z != m and covsum <= 2 * (mz[z] - h) for z in kverts):
                        ok = True
                        break
                if ok:
                    break
            if ok:
                break
            last = (name, g6, n, g, r, D, e, mz)
        checked += 1
        if not ok:
            failures.append(last)
    print({"checked": checked, "failures": len(failures)})
    for rec in failures[:20]:
        print(rec)


if __name__ == "__main__":
    main()
