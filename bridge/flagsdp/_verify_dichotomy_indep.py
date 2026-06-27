# INDEPENDENT verification:
#  (A) GPI itself: R_full <= K
#  (B) DICHOTOMY: gap = R_full - R_01 > 1e-6  ==>  R_full/K <= 1/3
# over FULL triangle-free band-max census N<=10, plus witnesses.
import numpy as np
from scipy.optimize import linprog
from itertools import combinations
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
from flag_engine import enumerate_graphs

def geos_he(N, adj, side, M):
    geos = []; he = []
    for (u, v) in M:
        gs = all_shortest_geos(N, adj, side, u, v); geos.append(gs); he.append(len(gs[0]))
    return geos, he

def R_full(N, M, geos, he):
    beta = len(M); nphi = N; nvar = nphi + beta
    c = np.zeros(nvar)
    for e in range(beta): c[nphi + e] = -he[e]
    rows = []; rhs = []
    for e in range(beta):
        for P in geos[e]:
            row = np.zeros(nvar); row[nphi + e] = 1.0
            for v in P: row[v] -= 1.0
            rows.append(row); rhs.append(0.0)
    row = np.zeros(nvar)
    for v in range(N): row[v] = 1.0
    rows.append(row); rhs.append(1.0)
    res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=[(0, None)] * nvar, method="highs")
    return -res.fun

def R01(N, M, geos, he):
    best = 0; bestS = None
    for k in range(1, N + 1):
        for S in combinations(range(N), k):
            Sset = set(S)
            num = sum(he[e] * min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(M)))
            if num / k > best: best = num / k; bestS = S
    return best, bestS

THIRD = 1.0 / 3.0
worst_gpi = 0.0; gpi_viol = 0
worst_gapped = None
dich_viol = []
ngraphs = 0
for N in range(5, 11):
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        res, mc = gamma_min_cut(n, adj, edges_of(adj))
        if not res: continue
        side, G, M = res
        if not M: continue
        geos, he = geos_he(n, adj, side, M)
        rf = R_full(n, M, geos, he); r01, _ = R01(n, M, geos, he)
        K = n + n * n - G; gap = rf - r01; ratio = rf / K
        ngraphs += 1
        if ratio > worst_gpi: worst_gpi = ratio
        if rf > K + 1e-6: gpi_viol += 1
        if gap > 1e-6:
            if worst_gapped is None or ratio > worst_gapped[0]: worst_gapped = (ratio, r01 / K, gap, n, G)
            if ratio > THIRD + 1e-9: dich_viol.append((ratio, gap, n, G))
print("Census N<=10: %d band-max graphs with bad edges" % ngraphs)
print("(A) GPI  max R_full/K = %.6f ; violations(R_full>K) = %d" % (worst_gpi, gpi_viol))
print("(B) DICHOTOMY worst gapped R/K = %s" % (str(worst_gapped)))
print("    dichotomy violations (gap>1e-6 AND R/K>1/3): %d" % len(dich_viol))
for d in dich_viol[:10]: print("    VIOL", d)
