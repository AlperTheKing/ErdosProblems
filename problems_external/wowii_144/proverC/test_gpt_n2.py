#!/usr/bin/env python3
"""Bounded falsifier for GPT-Pro Candidate N2, on the graph atlas.

For residual g>=5 instances and each shortest cycle K, enumerate M_z(K)
exactly and test whether some admissible realizer/anchor and z != anchor
satisfy sum_H |E_H cap W| <= 2(M_z(K)-h).
"""
from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W141 = ROOT.parent.parent / "wowii_141" / "oracle"
W144O = ROOT.parent / "oracle"
WAVE2 = ROOT.parent / "wave2"
sys.path[:0] = [str(W141), str(W144O), str(WAVE2)]

from invariants import (all_pairs_dist, dist_to_set, ecc_of_set,
                        eccentricities, girth, nx_to_bitadj)
from bridge_tests import shortest_cycles
from route_b_tests import graph6
from lemma_e_tests import components_of_mask, edges_in_mask


def bits(mask):
    while mask:
        b = mask & -mask
        mask ^= b
        yield b.bit_length() - 1


def mz_values(n, adj, kverts):
    kmask = sum(1 << v for v in kverts)
    outside = [v for v in range(n) if not (kmask >> v & 1)]
    best = {z: 0 for z in kverts}
    for sub in range(1, 1 << len(outside)):
        sz = sub.bit_count()
        if sz <= min(best.values()):
            continue
        mask = sum(1 << outside[i] for i in range(len(outside)) if sub >> i & 1)
        comps = components_of_mask(adj, mask)
        if edges_in_mask(adj, mask) != sz - len(comps):
            continue
        tallies = []
        for cm in comps:
            tally = {z: 0 for z in kverts}
            for v in bits(cm):
                for a in bits(adj[v] & kmask):
                    tally[a] += 1
            tallies.append(tally)
        for z in kverts:
            if all(sum(v for a, v in ta.items() if a != z) == 1 for ta in tallies):
                best[z] = max(best[z], sz)
    return best


def components_outside(adj, outside_mask):
    return components_of_mask(adj, outside_mask)


def main():
    checked = 0
    failures = []
    for G in nx.graph_atlas_g():
        if G.number_of_nodes() < 5 or not nx.is_connected(G):
            continue
        G = nx.convert_node_labels_to_integers(G)
        n, adj = nx_to_bitadj(G)
        g = girth(n, adj)
        if g < 5:
            continue
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        r, D = min(ecc), max(ecc)
        cmask = sum(1 << v for v in range(n) if ecc[v] == r)
        e = ecc_of_set(n, dist, cmask)
        s = g // 2
        if e == 0 or e <= D - s:
            continue
        realizers = [v for v in range(n) if dist_to_set(dist, v, cmask) == e]
        graph_ok = False
        rec = None
        for K in shortest_cycles(G, g):
            kverts = sorted(K)
            kmask = sum(1 << v for v in kverts)
            outside_mask = ((1 << n) - 1) & ~kmask
            comps = components_outside(adj, outside_mask)
            mz = mz_values(n, adj, kverts)
            for x in realizers:
                h = dist_to_set(dist, x, kmask)
                if h >= e:
                    graph_ok = True
                    break
                anchors = [a for a in kverts if dist[x][a] == h]
                for m in anchors:
                    delta = e - h
                    W = [a for a in kverts if dist[a][m] <= delta - 1]
                    for z in kverts:
                        if z == m:
                            continue
                        covsum = 0
                        for H in comps:
                            EH = 0
                            for sig in W:
                                if max(dist[sig][y] for y in bits(H)) >= r + 1:
                                    EH += 1
                            covsum += EH
                        if covsum <= 2 * (mz[z] - h):
                            graph_ok = True
                            break
                    if graph_ok:
                        break
                if graph_ok:
                    break
            if graph_ok:
                break
            rec = (graph6(G), n, g, r, D, e, mz)
        checked += 1
        if not graph_ok:
            failures.append(rec)
    print({"checked": checked, "failures": len(failures)})
    for rec in failures[:20]:
        print(rec)


if __name__ == "__main__":
    main()
