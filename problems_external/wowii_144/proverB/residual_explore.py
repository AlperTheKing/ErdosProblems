#!/usr/bin/env python3
"""Residual-case exploration (WOWII 144, Angle B piece 2).

Residual case:  G connected cyclic, e >= 1, e > D - s  (s = floor(g/2)).
Arithmetic facts:  empty at g = 3;  at g in {4,5}: e = r and D = r + 1;
in general r - s + 2 <= e <= r, r + 1 <= D <= e + s - 1.

Probe: is M(K) >= e always attainable using only PAIRWISE NON-INTERFERING
CANONICAL GEODESIC TAILS?  For each vertex y outside K let tail(y) be the
BFS-canonical geodesic from y to a nearest K-vertex, minus that K-vertex
(so |tail(y)| = h(y) = d(y,K)).  Two tails are compatible iff vertex-disjoint
and with no edge between them.  For a deletion vertex z in K a tail is
z-valid iff its last vertex's K-edge multiset has exactly one edge outside z
(g>=5: unique K-neighbour k, need k != z; g=4: neighbours {k} need k != z,
neighbours {k1,k2} (antipodal) need z in {k1,k2}).

TAILS(K) := max_z max { sum |tail| : compatible z-valid family }.
Question: residual  ==>  exists shortest K with TAILS(K) >= e ?

Also records: single-tail sufficiency (h_max >= e), which K works, stats per
girth, and dumps hard graphs (TAILS(K) < e for every K) for manual analysis.

Exact integer arithmetic. Run: python residual_explore.py  (seed 20260722)
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

SEED = 20260722
CYC_CAP = 10
EXP_CAP = 17


def mask_of(vs) -> int:
    m = 0
    for v in vs:
        m |= 1 << v
    return m


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


def tails_value(n, adj, dist, kverts, e_target):
    """Max sum of compatible z-valid canonical tails (greedy + exact fallback).
    Returns (best_sum, achieved_ge_target: bool)."""
    k_mask = mask_of(kverts)
    outside = [v for v in range(n) if not (k_mask >> v & 1)]
    tails = []
    for y in outside:
        h = dist_to_set(dist, y, k_mask)
        if h == 0:
            continue
        tgt = None
        for k in kverts:
            if dist[y][k] == h:
                tgt = k
                break
        path = bfs_geodesic(adj, dist, y, tgt)
        tv = path[:-1]                       # drop K endpoint
        last = tv[-1]
        knbrs = tuple(sorted(k for k in kverts if adj[last] >> k & 1))
        tails.append((len(tv), mask_of(tv), knbrs))
    # dedupe by mask
    seen = {}
    for sz, m, kn in tails:
        seen[m] = (sz, m, kn)
    tails = sorted(seen.values(), reverse=True)
    nt = len(tails)
    # adjacency closure masks for compatibility
    adjmask = []
    for sz, m, kn in tails:
        am = m
        mm = m
        while mm:
            b = mm & -mm
            mm ^= b
            am |= adj[b.bit_length() - 1]
        adjmask.append(am)

    best_overall = 0
    for z in kverts:
        valid = []
        for idx, (sz, m, kn) in enumerate(tails):
            if len(kn) == 1:
                if kn[0] != z:
                    valid.append(idx)
            elif len(kn) == 2:
                if z in kn:
                    valid.append(idx)
            # len(kn) == 0 impossible (height-1 last vertex)
        # greedy by size
        used = 0
        tot = 0
        for idx in valid:
            sz, m, kn = tails[idx]
            if adjmask[idx] & used:
                continue
            # also must not touch previously used tails' adjacency
            ok = True
            if m & used:
                ok = False
            if ok:
                # check no edge to used: adjmask includes m itself
                if (adjmask[idx] & used) == 0:
                    used |= m
                    tot += sz
        if tot > best_overall:
            best_overall = tot
        if best_overall >= e_target:
            return best_overall, True
    # exact fallback (branch and bound over tails, only if greedy failed)
    if nt <= 20:
        order = list(range(nt))
        suffix = [0] * (nt + 1)
        for i in range(nt - 1, -1, -1):
            suffix[i] = suffix[i + 1] + tails[i][0]
        for z in kverts:
            validset = []
            for idx in range(nt):
                kn = tails[idx][2]
                if (len(kn) == 1 and kn[0] != z) or (len(kn) == 2 and z in kn):
                    validset.append(idx)

            best_z = 0

            def rec(pos, used, tot):
                nonlocal best_z, best_overall
                if tot > best_z:
                    best_z = tot
                    if tot > best_overall:
                        best_overall = tot
                if best_overall >= e_target:
                    return True
                if pos >= len(validset):
                    return False
                rem = sum(tails[validset[q]][0] for q in range(pos, len(validset)))
                if tot + rem <= best_z:
                    return False
                idx = validset[pos]
                if not (adjmask[idx] & used):
                    if rec(pos + 1, used | tails[idx][1], tot + tails[idx][0]):
                        return True
                return rec(pos + 1, used, tot)

            if rec(0, 0, 0):
                return best_overall, True
    return best_overall, False


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
    by_g = Counter()
    single_tail_ok = 0
    tails_ok = 0
    hard = []
    checked_consistency = 0
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
        # residual case
        residual += 1
        by_g[g] += 1
        assert g != 3, "residual must be empty at g=3"
        if g in (4, 5):
            assert e == r0 and D == r0 + 1, "g in {4,5} residual arithmetic"
        assert r0 - s + 2 <= e <= r0 and r0 + 1 <= D <= e + s - 1
        checked_consistency += 1

        cyc = shortest_cycles(G, g)[:CYC_CAP]
        best_h = 0
        anyk = False
        for K in cyc:
            k_mask = mask_of(K)
            hmax = max(dist_to_set(dist, x, k_mask) for x in range(n))
            best_h = max(best_h, hmax)
            val, ok = tails_value(n, adj, dist, sorted(K), e)
            if ok:
                anyk = True
                break
        if best_h >= e:
            single_tail_ok += 1
        if anyk:
            tails_ok += 1
        else:
            hard.append((name, g6, n, g, r0, D, e, best_h))

    print(f"graphs seen                : {len(seen)}")
    print(f"residual-case graphs       : {residual}")
    print(f"  by girth                 : {dict(sorted(by_g.items()))}")
    print(f"arithmetic checks passed   : {checked_consistency}")
    print(f"single-tail (hmax>=e)      : {single_tail_ok}")
    print(f"tail-family TAILS(K)>=e    : {tails_ok}")
    print(f"HARD (no K with tails>=e)  : {len(hard)}")
    for hrec in hard[:40]:
        print("  ", hrec)


if __name__ == "__main__":
    main()
