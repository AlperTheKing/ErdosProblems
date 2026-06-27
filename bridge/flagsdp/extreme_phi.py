#!/usr/bin/env python3
"""Extreme-phi angle for GPI. For each band-max triangle-free graph in the census, MAXIMIZE
   R(phi) = sum_e h_e * m_phi(e)  over {phi>=0, sum_v phi(v) <= 1},
where m_phi(e) = min_{P in P_e} sum_{v in P} phi(v).  This is an LP (epigraph t_e <= sum_P phi).
GPI <=> R_max <= K = N + (N^2 - Gamma).  We characterize the structure of the optimal phi*:
0/1 indicator? single B-shore? all of V?  And report the slack K - R_max."""
import numpy as np
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs


def dual_maximize(N, adj, side, G, M):
    beta = len(M)
    geos = []; he = []
    for (u, v) in M:
        gs = all_shortest_geos(N, adj, side, u, v)
        geos.append(gs); he.append(len(gs[0]))
    nphi = N; nt = beta; nvar = nphi + nt
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
    A = np.array(rows); b = np.array(rhs)
    bounds = [(0, None)] * nvar
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
    return -res.fun, res.x[:nphi], he


def classify(N, side, phi):
    mx = phi.max() if phi.size else 0.0
    if mx <= 1e-9:
        return False, 0, False, False
    is01 = all(abs(p) < 1e-7 or abs(p - mx) < 1e-7 for p in phi)
    S = [v for v in range(N) if phi[v] > 0.5 * mx]
    allV = (len(S) == N)
    oneside = bool(S) and (set(side[v] for v in S) == {0} or set(side[v] for v in S) == {1})
    return is01, len(S), allV, oneside


def run(N):
    rows = []
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        E = edges_of(adj)
        res, mc = gamma_min_cut(n, adj, E)
        if res is None:
            continue
        side, G, M = res
        if not M:
            continue
        R, phi, he = dual_maximize(n, adj, side, G, M)
        K = n + (n * n - G)
        is01, szS, allV, oneside = classify(n, side, phi)
        rows.append((R / K, R, K, is01, szS, allV, oneside, n, len(M), G))
    rows.sort(reverse=True)
    print("N=%d: %d band-max graphs" % (N, len(rows)))
    print("%8s %8s %5s %4s %4s %5s %6s %5s %5s" % ("R/K", "R", "K", "01?", "|S|", "allV", "1side", "beta", "Gam"))
    for w in rows[:12]:
        print("%8.4f %8.3f %5d %4s %4d %5s %6s %5d %5d" % (w[0], w[1], w[2], str(w[3]), w[4], str(w[5]), str(w[6]), w[8], w[9]))
    tight = [w for w in rows if w[0] > 1 - 1e-6]
    viol = [w for w in rows if w[0] > 1 + 1e-7]
    print("  tight(R=K): %d; of those 0/1: %d; allV: %d; 1side: %d | VIOLATIONS(R>K): %d" % (
        len(tight), sum(1 for w in tight if w[3]), sum(1 for w in tight if w[5]),
        sum(1 for w in tight if w[6]), len(viol)))


if __name__ == "__main__":
    import sys
    Ns = [int(x) for x in sys.argv[1:]] or range(5, 10)
    for N in Ns:
        run(N)
