#!/usr/bin/env python3
"""Inspect violating graphs from battery1: print structure + optimal M(K)
witness forests (component shapes) to learn the right general extraction."""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "wowii_141" / "oracle"))
sys.path.insert(0, str(ROOT.parent / "oracle"))
sys.path.insert(0, str(ROOT.parent / "wave2"))

from invariants import (all_pairs_dist, dist_to_set, eccentricities, girth,
                        graph_connected, nx_to_bitadj)
from bridge_tests import shortest_cycles
from lemma_e_tests import M_of_cycle, components_of_mask, edges_in_mask


def best_forests(n, adj, kv):
    """All maximum witness forests for M(K): list of (mask, z, comps)."""
    kmask = 0
    for v in kv:
        kmask |= 1 << v
    outside = [v for v in range(n) if not (kmask >> v & 1)]
    best, wits = 0, []
    for sz in range(len(outside), 0, -1):
        if sz < best:
            break
        for combo in combinations(outside, sz):
            mask = 0
            for v in combo:
                mask |= 1 << v
            comps = components_of_mask(adj, mask)
            if edges_in_mask(adj, mask) != sz - len(comps):
                continue
            for z in kv:
                good = True
                for cm in comps:
                    tot = 0
                    cc = cm
                    while cc:
                        b = cc & -cc
                        cc ^= b
                        tot += bin(adj[b.bit_length() - 1] & kmask
                                   & ~(1 << z)).count("1")
                    if tot != 1:
                        good = False
                        break
                if good:
                    if sz > best:
                        best, wits = sz, []
                    wits.append((mask, z, comps))
                    break
        if wits and sz == len(outside):
            break
    return best, wits


def show(g6, Ksel=None, xstar=None):
    G = nx.from_graph6_bytes(g6.encode())
    n, adj = nx_to_bitadj(G)
    g = girth(n, adj)
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    r = min(ecc)
    cmask = 0
    for v in range(n):
        if ecc[v] == r:
            cmask |= 1 << v
    e = max(dist_to_set(dist, v, cmask) for v in range(n))
    print(f"== {g6}: n={n} g={g} r={r} e={e} center={bin(cmask)}")
    print("   edges:", sorted(G.edges()))
    print("   ecc:", ecc)
    for K in shortest_cycles(G, g):
        kv = sorted(K)
        if Ksel is not None and kv != sorted(Ksel):
            continue
        kmask = 0
        for v in kv:
            kmask |= 1 << v
        mk, wits = best_forests(n, adj, kv)
        h = {v: dist_to_set(dist, v, kmask) for v in range(n)
             if not (kmask >> v & 1)}
        print(f" K={kv} M={mk} heights={h}")
        comps = components_of_mask(adj, ((1 << n) - 1) & ~kmask)
        for cm in comps:
            vs = [v for v in range(n) if cm >> v & 1]
            att = sorted({u for v in vs for u in kv if adj[v] >> u & 1})
            print(f"   branch {vs} D={max(h[v] for v in vs)} attach={att}")
        for mask, z, cc in wits[:4]:
            desc = []
            for cm in cc:
                vs = [v for v in range(n) if cm >> v & 1]
                att = sorted({(v, u) for v in vs for u in kv
                              if adj[v] >> u & 1})
                desc.append(f"{vs}->{att}")
            print(f"   F(z={z}): " + " | ".join(desc))


if __name__ == "__main__":
    show("FjCHO")
    show("FxOWO")
    show("FHt@G")
    show("FhELO")
