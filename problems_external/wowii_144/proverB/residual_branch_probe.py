#!/usr/bin/env python3
"""Residual probe 2: branch-granularity structure of tail families.

For every residual-case graph (cyclic, e >= 1, e > D - s) and every shortest
cycle K (cap), compute:

  BR1(K):  max sum of tail heights over families with AT MOST ONE canonical
           tail PER BRANCH of G - K (distinct branches never interfere),
           z-valid as in residual_explore.  Tail of branch B at position rho:
           height H_B(rho) = max d(y,K) over y in B with a nearest K-vertex
           rho; per branch we may pick ANY ONE (rho, tail).
  BR2(K):  same but the per-branch tail is forced to be the branch's GLOBAL
           deepest tail (canonical x realizing max_y d(y,K) in B).

Questions (falsify!):
  Q-A: residual ==> exists K with BR1(K) >= e ?
  Q-B: residual ==> EVERY K has BR1(K) >= e ?   (E_forall-flavoured)
  Q-C: residual ==> exists K with BR2(K) >= e ?

Also dumps failures with full structure for manual proof mining.
Run: python residual_branch_probe.py   (seed 20260723)
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W141 = ROOT.parent.parent / "wowii_141" / "oracle"
W144O = ROOT.parent / "oracle"
WAVE2 = ROOT.parent / "wave2"
sys.path.insert(0, str(W141))
sys.path.insert(0, str(W144O))
sys.path.insert(0, str(WAVE2))

from invariants import (  # noqa: E402
    all_pairs_dist,
    dist_to_set,
    ecc_of_set,
    eccentricities,
    girth,
    graph_connected,
    nx_to_bitadj,
)
from bridge_tests import adversarial_graphs, shortest_cycles  # noqa: E402
from sweep_families import build_family_graphs, random_graphs  # noqa: E402
from route_b_tests import (  # noqa: E402
    chorded_cycle,
    cycle_random_legs,
    cycle_random_trees,
    forced_girth_random,
    gen_theta,
    graph6,
    trap_family,
)

SEED = 20260723
CYC_CAP = 10
EXP_CAP = 17


def mask_of(vs) -> int:
    m = 0
    for v in vs:
        m |= 1 << v
    return m


def components_of(adj, mask: int) -> list[int]:
    comps = []
    rem = mask
    while rem:
        start = rem & -rem
        reached = start
        frontier = start
        while frontier:
            new = 0
            f = frontier
            while f:
                b = f & -f
                f ^= b
                new |= adj[b.bit_length() - 1]
            new &= mask & ~reached
            reached |= new
            frontier = new
        comps.append(reached)
        rem &= ~reached
    return comps


def bfs_geodesic(adj, dist, u, v):
    path = [u]
    cur = u
    while cur != v:
        m = adj[cur]
        nxt = None
        while m:
            b = m & -m
            m ^= b
            w = b.bit_length() - 1
            if dist[w][v] == dist[cur][v] - 1:
                nxt = w
                break
        path.append(nxt)
        cur = nxt
    return path


def branch_options(n, adj, dist, kverts, k_mask):
    """Per branch: list of (height, last_K_nbrs tuple) options, one per
    (deepest-y, nearest-rho) pair; plus the branch's global max height."""
    full = (1 << n) - 1
    out_mask = full & ~k_mask
    branches = components_of(adj, out_mask)
    opts = []
    for bm in branches:
        cand = {}
        deepest = (0, None, None)
        m = bm
        while m:
            b = m & -m
            m ^= b
            y = b.bit_length() - 1
            h = dist_to_set(dist, y, k_mask)
            for rho in kverts:
                if dist[y][rho] == h:
                    key = rho
                    if h > cand.get(key, (0,))[0]:
                        path = bfs_geodesic(adj, dist, y, rho)
                        tv = path[:-1]
                        last = tv[-1]
                        knbrs = tuple(sorted(k for k in kverts
                                             if adj[last] >> k & 1))
                        cand[key] = (h, knbrs)
                    if h > deepest[0]:
                        deepest = (h, y, rho)
            # note: y contributes an option at EVERY nearest rho
        options = sorted(set(cand.values()), reverse=True)
        # deepest tail option (BR2): recompute canonical
        h, y, rho = deepest
        path = bfs_geodesic(adj, dist, y, rho)
        tv = path[:-1]
        last = tv[-1]
        knbrs = tuple(sorted(k for k in kverts if adj[last] >> k & 1))
        opts.append((options, (h, knbrs)))
    return opts


def z_valid(h_kn, z):
    h, kn = h_kn
    if len(kn) == 1:
        return kn[0] != z
    if len(kn) == 2:
        return z in kn
    return False


def br_values(kverts, opts, e_target):
    """(BR1, BR2) = best over z of sum over branches of best z-valid option /
    forced-deepest option."""
    br1 = br2 = 0
    for z in kverts:
        tot1 = 0
        tot2 = 0
        for options, deepopt in opts:
            best = 0
            for h, kn in options:
                if z_valid((h, kn), z):
                    best = h
                    break            # options sorted desc
            tot1 += best
            if z_valid(deepopt, z):
                tot2 += deepopt[0]
        br1 = max(br1, tot1)
        br2 = max(br2, tot2)
        if br1 >= e_target and br2 >= e_target:
            break
    return br1, br2


def main() -> None:
    rng = random.Random(SEED)
    corpora: list[tuple[str, nx.Graph]] = []
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() >= 2 and nx.is_connected(graph):
            corpora.append(("atlas", graph))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(1500):
        corpora.append(cycle_random_legs(rng))
    for _ in range(1000):
        corpora.append(cycle_random_trees(rng))
    for _ in range(800):
        corpora.append(chorded_cycle(rng))
    for _ in range(500):
        corpora.append(gen_theta(rng))
    got = tries = 0
    while got < 900 and tries < 20000:
        tries += 1
        res = forced_girth_random(rng, gmin=5)
        if res is not None:
            corpora.append(res)
            got += 1
    got = tries = 0
    while got < 500 and tries < 20000:
        tries += 1
        res = forced_girth_random(rng, gmin=4)
        if res is not None:
            corpora.append(res)
            got += 1

    seen = set()
    residual = 0
    qa_ok = qb_ok = qc_ok = 0
    qa_fail, qb_fail, qc_fail = [], [], []
    for name, G in corpora:
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 2 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g == 0 or n - g > EXP_CAP:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        r0 = min(ecc)
        D = max(ecc)
        cm = 0
        for v in range(n):
            if ecc[v] == r0:
                cm |= 1 << v
        e = ecc_of_set(n, dist, cm)
        s = g // 2
        if e == 0 or e <= D - s:
            continue
        residual += 1
        cyc = shortest_cycles(G, g)[:CYC_CAP]
        a = b = c = 0        # counts of K with BR1>=e / all / BR2>=e
        nk = len(cyc)
        for K in cyc:
            kverts = sorted(K)
            k_mask = mask_of(kverts)
            opts = branch_options(n, adj, dist, kverts, k_mask)
            br1, br2 = br_values(kverts, opts, e)
            if br1 >= e:
                a += 1
            if br2 >= e:
                c += 1
        if a >= 1:
            qa_ok += 1
        else:
            qa_fail.append((name, g6, n, g, r0, D, e))
        if a == nk:
            qb_ok += 1
        else:
            qb_fail.append((name, g6, n, g, r0, D, e, f"{a}/{nk}"))
        if c >= 1:
            qc_ok += 1
        else:
            qc_fail.append((name, g6, n, g, r0, D, e))

    print(f"graphs seen             : {len(seen)}")
    print(f"residual-case graphs    : {residual}")
    print(f"Q-A exists-K BR1>=e     : {qa_ok}   FAIL {len(qa_fail)}")
    print(f"Q-B every-K  BR1>=e     : {qb_ok}   FAIL {len(qb_fail)}")
    print(f"Q-C exists-K BR2>=e     : {qc_ok}   FAIL {len(qc_fail)}")
    for tag, lst in (("QA", qa_fail), ("QB", qb_fail), ("QC", qc_fail)):
        for rec in lst[:15]:
            print(f"  {tag} ", rec)


if __name__ == "__main__":
    main()
