#!/usr/bin/env python3
"""For the tight cases (R_01=K), find the optimal 0/1 set S* and characterize it:
- Is S* always a single B-shore intersected with a B-distance level set from one endpoint?
- For each bad edge e, what is min_P |P cap S*| and how does it relate to h_e?
Goal: identify the COMBINATORIAL invariant that makes Sum_e h_e min_P|P cap S| = K|S| tight,
to attempt a direct proof for the maximizing S (not all S)."""
from itertools import combinations
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut, bdistB
from flag_engine import enumerate_graphs


def C5q(q):
    n = 5 * q; vid = lambda i, j: i * q + j
    side = [0] * n; adj = [set() for _ in range(n)]
    for i in range(5):
        for j in range(q):
            side[vid(i, j)] = (0 if i in (0, 2, 4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u = vid(i, a); v = vid((i + 1) % 5, b); adj[u].add(v); adj[v].add(u)
    M = [(vid(4, a), vid(0, b)) for a in range(q) for b in range(q)]
    return n, adj, side, 25 * len(M), M


def best_01(N, geos, he, kmax):
    best = -1; bestS = None
    for k in range(1, kmax + 1):
        for S in combinations(range(N), k):
            Sset = set(S)
            num = sum(he[e] * min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(geos)))
            val = num / k
            if val > best + 1e-12:
                best = val; bestS = S
    return best, bestS


print("=== C5[q]: optimal S structure ===")
for q in (2, 3, 4):
    n, adj, side, G, M = C5q(q)
    geos = [all_shortest_geos(n, adj, side, u, v) for (u, v) in M]
    he = [len(g[0]) for g in geos]
    r01, S = best_01(n, geos, he, kmax=q + 1)
    K = n + n * n - G
    # which "parts" (i index) does S occupy?
    parts = sorted(set(v // q for v in S))
    sides = sorted(set(side[v] for v in S))
    print("q=%d: R_01=%.2f K=%d |S|=%d  S-parts(i)=%s  S-sides=%s" % (q, r01, K, len(S), parts, sides))
    # per-edge min count
    mincounts = [min(sum(1 for v in P if v in set(S)) for P in geos[e]) for e in range(len(M))]
    print("   per-bad-edge min|P cap S|: min=%d max=%d  (h_e all=%d)  Sum h_e mc = %d = K|S| = %d" % (
        min(mincounts), max(mincounts), he[0], sum(he[e] * mincounts[e] for e in range(len(M))), K * len(S)))

print("\n=== census tight cases: is optimal S always a single B-shore? ===")
for N in range(5, 9):
    nshore = 0; nlevel = 0; ntight = 0
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        res, mc = gamma_min_cut(n, adj, edges_of(adj))
        if not res:
            continue
        side, G, M = res
        if not M:
            continue
        geos = [all_shortest_geos(n, adj, side, u, v) for (u, v) in M]
        he = [len(g[0]) for g in geos]
        K = n + n * n - G
        r01, S = best_01(n, geos, he, kmax=n)
        if abs(r01 - K) < 1e-6:
            ntight += 1
            if S and (set(side[v] for v in S) == {0} or set(side[v] for v in S) == {1}):
                nshore += 1
    print("N=%d: tight cases=%d ; optimal-S single-shore=%d" % (N, ntight, nshore))
