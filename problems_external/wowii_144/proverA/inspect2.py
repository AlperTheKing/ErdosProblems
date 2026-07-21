#!/usr/bin/env python3
"""Structural stats for the two unproved g>=5 sub-claims:
BIG   (delta > g//2)          : exists z, u in B_c : tau_z(u) >= e
FBX   (TENT failure at sigma) : exists z, u in B_x : tau_z(u) >= e
Collect candidate-inequality slacks to find the provable route.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, deque
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "wowii_141" / "oracle"))
sys.path.insert(0, str(ROOT.parent / "oracle"))
sys.path.insert(0, str(ROOT.parent / "wave2"))

from invariants import (all_pairs_dist, dist_to_set, eccentricities, girth,
                        graph_connected, nx_to_bitadj)
from bridge_tests import shortest_cycles, adversarial_graphs
from sweep_families import build_family_graphs, random_graphs
from route_b_tests import (cycle_random_legs, cycle_random_trees,
                           chorded_cycle, gen_theta, forced_girth_random,
                           trap_family, graph6)
from stress_lemma_e import subdivided_multigraph, webbed_annulus
from lemma_e_tests import components_of_mask
from battery2 import bfs_dist_avoid

SEED = 20260718


def main() -> None:
    rng = random.Random(SEED)
    corpora = []
    for A in nx.graph_atlas_g():
        if A.number_of_nodes() >= 2 and nx.is_connected(A):
            corpora.append(("atlas", A))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(500):
        corpora.append(cycle_random_legs(rng))
    for _ in range(400):
        corpora.append(cycle_random_trees(rng))
    for _ in range(250):
        corpora.append(chorded_cycle(rng))
    for _ in range(400):
        corpora.append(gen_theta(rng))
    for i in range(600):
        corpora.append((f"subdiv{i}", subdivided_multigraph(rng)))
    for i in range(600):
        corpora.append((f"annulus{i}", webbed_annulus(rng)))
    got = tries = 0
    while got < 600 and tries < 15000:
        tries += 1
        r_ = forced_girth_random(rng, gmin=5)
        if r_ is not None:
            corpora.append(r_)
            got += 1

    seen = set()
    bigstats = Counter()
    fbxstats = Counter()
    slack = {}

    def note(key, s, wit):
        if key not in slack or s < slack[key][0]:
            slack[key] = (s, wit)

    for name, G in corpora:
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 3 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g < 5:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        r = min(ecc)
        cmask = 0
        for v in range(n):
            if ecc[v] == r:
                cmask |= 1 << v
        e = max(dist_to_set(dist, v, cmask) for v in range(n))
        if e == 0:
            continue
        cycles = shortest_cycles(G, g)[:40]
        xs = [v for v in range(n) if dist_to_set(dist, v, cmask) == e][:6]
        half = g // 2
        for K in cycles:
            kv = sorted(K)
            kmask = 0
            for v in kv:
                kmask |= 1 << v
            comps = components_of_mask(adj, ((1 << n) - 1) & ~kmask)
            tauz = {z: bfs_dist_avoid(n, adj, kmask & ~(1 << z), z)
                    for z in kv}
            for xstar in xs:
                hx = dist_to_set(dist, xstar, kmask)
                delta = e - hx
                if delta <= 0:
                    continue
                bxi = None
                if hx >= 1:
                    for i, cm in enumerate(comps):
                        if cm >> xstar & 1:
                            bxi = i
                            break
                if delta > half:
                    cs = [c for c in range(n)
                          if (cmask >> c & 1) and dist[xstar][c] == e]
                    for c in cs:
                        bci = next(i for i, cm in enumerate(comps)
                                   if cm >> c & 1)
                        hc = dist_to_set(dist, c, kmask)
                        bcm = comps[bci]
                        # best (z,u)
                        bT, bz, bu = -1, None, None
                        for z in kv:
                            mm = bcm
                            while mm:
                                b = mm & -mm
                                mm ^= b
                                u = b.bit_length() - 1
                                t = tauz[z][u]
                                if t < 10 ** 8 and t > bT:
                                    bT, bz, bu = t, z, u
                        xin = bcm >> xstar & 1
                        bigstats[("xInBc", bool(xin))] += 1
                        note("BIG:T-e", bT - e, f"{name} [{g6}]")
                        note("BIG:T-(hx+hc+half)", bT - (hx + hc + half),
                             f"{name} [{g6}] T={bT} hx={hx} hc={hc} "
                             f"half={half} e={e} r={r} g={g}")
                        # u structure
                        hu = dist_to_set(dist, bu, kmask)
                        note("BIG:hu-e", hu - e, f"{name} [{g6}]")
                        note("BIG:T-(r+1-hc)", bT - (r + 1 - hc),
                             f"{name} [{g6}]")
                        note("BIG:T-(r+1)", bT - (r + 1), f"{name} [{g6}]")
                        note("BIG:Dxc",
                             dist[xstar][c] - (hx + half + hc),
                             f"{name} [{g6}]")
                    continue
                ms = [a for a in kv if dist[xstar][a] == hx]
                if bxi is None:
                    continue
                bxm = comps[bxi]
                for m in ms:
                    W0 = [a for a in kv if dist[m][a] <= delta - 1]
                    for sig in W0:
                        cbs = set()
                        fars_bx = []
                        for u in range(n):
                            if kmask >> u & 1 or dist[sig][u] <= r:
                                continue
                            for i, cm in enumerate(comps):
                                if cm >> u & 1:
                                    if i == bxi:
                                        fars_bx.append(u)
                                    else:
                                        cbs.add(i)
                        if cbs or not fars_bx:
                            continue
                        # TENT failure at sig; stats
                        for u in fars_bx[:4]:
                            bT, bz = -1, None
                            for z in kv:
                                t = tauz[z][u]
                                if t < 10 ** 8 and t > bT:
                                    bT, bz = t, z
                            hu = dist_to_set(dist, u, kmask)
                            fbxstats[("tau_far>=e", bT >= e)] += 1
                            note("FBX:tau_far-e", bT - e,
                                 f"{name} [{g6}] u={u} sig={sig} "
                                 f"dsu={dist[sig][u]} hu={hu} e={e} r={r} "
                                 f"g={g} hx={hx} delta={delta}")
                            # is z=antipode(sig) enough?
                            anti = [a for a in kv
                                    if dist[sig][a] == half]
                            bTa = max((tauz[z][u] for z in anti
                                       if tauz[z][u] < 10 ** 8),
                                      default=-1)
                            fbxstats[("tau_anti>=e", bTa >= e)] += 1
                            note("FBX:tau_anti-e", bTa - e,
                                 f"{name} [{g6}] u={u}")
                            note("FBX:dsu-(r+1)", dist[sig][u] - (r + 1),
                                 f"{name} [{g6}]")
                            note("FBX:dxu",
                                 dist[xstar][u] - (r + 2 - e),
                                 f"{name} [{g6}]")

    print("graphs:", len(seen))
    print("bigstats:", dict(bigstats))
    print("fbxstats:", dict(fbxstats))
    for k in sorted(slack):
        print(f"min {k}: {slack[k][0]}  @ {slack[k][1][:110]}")


if __name__ == "__main__":
    main()
