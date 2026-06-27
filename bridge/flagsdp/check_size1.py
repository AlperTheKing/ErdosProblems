import numpy as np
from itertools import combinations
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
from flag_engine import enumerate_graphs


def best_01_full(N, geos, he):
    best = -1; bestk = None; ties = set()
    for k in range(1, N + 1):
        for S in combinations(range(N), k):
            Sset = set(S)
            num = sum(he[e] * min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(geos)))
            val = num / k
            if val > best + 1e-9:
                best = val; bestk = k; ties = {k}
            elif abs(val - best) < 1e-9:
                ties.add(k)
    return best, bestk, ties


for N in range(5, 9):
    bysize = {}; min_opt_size = {}
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
        b, k, ties = best_01_full(n, geos, he)
        bysize[k] = bysize.get(k, 0) + 1
        msz = min(ties)
        min_opt_size[msz] = min_opt_size.get(msz, 0) + 1
    print("N=%d optimal |S| (first-found): %s ; MIN optimal |S| among ties: %s" % (
        N, sorted(bysize.items()), sorted(min_opt_size.items())))
