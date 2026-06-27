# Distribution of R/K among GAPPED cases on full census N<=10.
# Question: is 1/3 a real barrier or just loose? Print histogram of gapped R/K
# and the max. Also: among NON-gapped (0/1-optimal) cases, what is max R/K (should reach 1.0).
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
    best = 0
    for k in range(1, N + 1):
        for S in combinations(range(N), k):
            Sset = set(S)
            num = sum(he[e] * min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(M)))
            if num / k > best: best = num / k
    return best

gapped_ratios = []
nongapped_max = 0.0
for N in range(5, 11):
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        res, mc = gamma_min_cut(n, adj, edges_of(adj))
        if not res: continue
        side, G, M = res
        if not M: continue
        geos, he = geos_he(n, adj, side, M)
        rf = R_full(n, M, geos, he); r01 = R01(n, M, geos, he)
        K = n + n * n - G; gap = rf - r01; ratio = rf / K
        if gap > 1e-6:
            gapped_ratios.append(ratio)
        else:
            nongapped_max = max(nongapped_max, ratio)
gr = np.array(gapped_ratios)
print("gapped count=%d  max gapped R/K=%.4f  mean=%.4f  95pct=%.4f" % (
    len(gr), gr.max(), gr.mean(), np.percentile(gr, 95)))
bins = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 1.0/3.0, 0.4, 1.0]
hist, _ = np.histogram(gr, bins=bins)
print("histogram of gapped R/K by bins", bins)
print(hist.tolist())
print("non-gapped(0/1-optimal) max R/K = %.6f" % nongapped_max)
