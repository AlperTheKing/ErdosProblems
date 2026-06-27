#!/usr/bin/env python3
"""Test the CRUX of the extreme-phi angle: is the GPI maximizer ALWAYS a 0/1 indicator?
Compare, per band-max triangle-free census graph:
   R_full  = max_{phi>=0, sum phi<=1} sum_e h_e m_phi(e)      (the full LP)
   R_01    = max over 0/1 phi = max_{S nonempty} [ sum_e h_e min_P |P cap S| ] / |S|
If R_full > R_01 anywhere, the GPI does NOT reduce to 0/1 tolls (matches 'NOT SUFFICIENT' note).
Also report which S achieves R_01 and whether it is a B-distance level set / single shore."""
import numpy as np
from itertools import combinations
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs


def geos_he(N, adj, side, M):
    geos = []; he = []
    for (u, v) in M:
        gs = all_shortest_geos(N, adj, side, u, v)
        geos.append(gs); he.append(len(gs[0]))
    return geos, he


def R_full(N, M, geos, he):
    beta = len(M); nphi = N; nvar = nphi + beta
    c = np.zeros(nvar)
    for e in range(beta):
        c[nphi + e] = -he[e]
    rows = []; rhs = []
    for e in range(beta):
        for P in geos[e]:
            row = np.zeros(nvar); row[nphi + e] = 1.0
            for v in P:
                row[v] -= 1.0
            rows.append(row); rhs.append(0.0)
    row = np.zeros(nvar)
    for v in range(N):
        row[v] = 1.0
    rows.append(row); rhs.append(1.0)
    res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=[(0, None)] * nvar, method="highs")
    return -res.fun, res.x[:nphi]


def R_01(N, M, geos, he):
    best = 0.0; bestS = None
    for k in range(1, N + 1):
        for S in combinations(range(N), k):
            Sset = set(S)
            num = 0
            for e in range(len(M)):
                mn = min(sum(1 for v in P if v in Sset) for P in geos[e])
                num += he[e] * mn
            val = num / k
            if val > best + 1e-12:
                best = val; bestS = S
    return best, bestS


def run(N):
    maxgap = 0.0; gapinfo = None
    nworst_ratio = 0.0
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        res, mc = gamma_min_cut(n, adj, edges_of(adj))
        if res is None:
            continue
        side, G, M = res
        if not M:
            continue
        geos, he = geos_he(n, adj, side, M)
        rf, phi = R_full(n, M, geos, he)
        r01, S = R_01(n, M, geos, he)
        gap = rf - r01
        if gap > maxgap:
            maxgap = gap; gapinfo = (n, len(M), G, rf, r01, S)
        K = n + n * n - G
        nworst_ratio = max(nworst_ratio, rf / K)
    print("N=%d: max(R_full - R_01) = %.6e ; max R_full/K = %.4f" % (N, maxgap, nworst_ratio))
    if gapinfo and maxgap > 1e-7:
        print("   gap witness: n=%d beta=%d Gam=%d R_full=%.4f R_01=%.4f S=%s" % gapinfo)


if __name__ == "__main__":
    import sys
    for N in ([int(x) for x in sys.argv[1:]] or range(5, 10)):
        run(N)
