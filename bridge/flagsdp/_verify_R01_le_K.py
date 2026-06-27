# Does the FULL 0/1 bound hold?  R_01 = max_{S nonempty} [sum_e h_e min_P |P cap S|]/|S|  <=  K ?
# This is what step 3 of the strategy NEEDS (V1 alone = only |S|=1).
from itertools import combinations
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
from flag_engine import enumerate_graphs

def geos_he(N, adj, side, M):
    geos = []; he = []
    for (u, v) in M:
        gs = all_shortest_geos(N, adj, side, u, v); geos.append(gs); he.append(len(gs[0]))
    return geos, he

def R01_full(N, M, geos, he):
    best = 0; bestS = None; bestk = None
    for k in range(1, N + 1):
        for S in combinations(range(N), k):
            Sset = set(S)
            num = sum(he[e] * min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(M)))
            if num / k > best: best = num / k; bestS = S; bestk = k
    return best, bestS, bestk

worst = 0.0; viol = 0; worst_info = None
ng = 0
for N in range(5, 11):
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        res, mc = gamma_min_cut(n, adj, edges_of(adj))
        if not res: continue
        side, G, M = res
        if not M: continue
        geos, he = geos_he(n, adj, side, M)
        r01, S, k = R01_full(n, M, geos, he)
        K = n + n * n - G
        ng += 1
        if r01 / K > worst: worst = r01 / K; worst_info = (n, G, k, r01, K)
        if r01 > K + 1e-6: viol += 1
print("Census N<=10: %d graphs" % ng)
print("max R_01/K = %.6f ; |S| of worst = %s ; violations(R_01>K) = %d" % (worst, str(worst_info), viol))
