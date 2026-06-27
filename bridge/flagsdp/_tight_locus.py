#!/usr/bin/env python3
"""Where is the uniform-routing GPI bound (maxT_unif <= K) TIGHT?
The strategy claims tight ONLY at bare odd cycles C_N (Gamma=N^2). Verify, and
record the ratio maxT/K and the Gamma/N^2 ratio for every census instance, so we
can see whether 'tight' coincides exactly with Gamma=N^2 (=> circularity: a proof
of the uniform bound must know Gamma<=N^2 to know it is not violated)."""
import sys
import numpy as np
import flag_engine
from mycielskian_check import gamma_min_cut, all_shortest_geos
from collections import deque

def adj_sets(n, A):
    return [set(j for j in range(n) if (A[i] >> j) & 1) for i in range(n)]

def is_connected(n, adj):
    seen = {0}; q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen) == n

def loads_uniform(N, adj, side, M):
    T = np.zeros(N)
    for (u, v) in M:
        geos = all_shortest_geos(N, adj, side, u, v)
        if not geos:
            return None
        h = len(geos[0]); w = h / len(geos)
        for P in geos:
            for x in P:
                T[x] += w
    return T

def main(Nmax):
    near_tight = []   # ratio maxT/K within 1e-6 of 1
    n_checked = 0
    for N in range(5, Nmax + 1):
        for (n, A) in flag_engine.enumerate_graphs(N, triangle_free=True):
            adj = adj_sets(n, A)
            if not is_connected(n, adj):
                continue
            E = [(i, j) for i in range(n) for j in adj[i] if j > i]
            res, mc = gamma_min_cut(n, adj, E)
            if res is None:
                continue
            side, G, M = res
            if len(M) == 0:
                continue
            T = loads_uniform(n, adj, side, M)
            if T is None:
                continue
            n_checked += 1
            K = N + (N*N - G)
            ratio = T.max() / K
            if ratio > 1 - 1e-6:
                nedges = len(E)
                near_tight.append((N, len(M), G, N*N, nedges, round(ratio, 6)))
    print("checked", n_checked)
    print("NEAR-TIGHT (maxT/K >= 1-1e-6):  (N, beta, Gamma, N^2, #edges, ratio)")
    for t in near_tight:
        is_cycle = (t[4] == t[0] and t[1] == 1)  # N edges, beta=1 => C_N
        print("   ", t, "  bare-odd-cycle?" , is_cycle, "  Gamma==N^2?", t[2]==t[3])

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10)
