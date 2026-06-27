#!/usr/bin/env python3
"""Probe extreme-phi 0/1-extremality on the TIGHT family C5[q] and a few structured larger graphs.
At C5[q] Gamma=N^2 so K=N (deficit 0); GPI is EQUALITY for uniform phi=1 AND for seam 1_{V0}.
Question: is the LP maximizer 0/1 there too, or does the equality set contain fractional optima
(so 0/1-extremality is non-generic)? Report R_full, the optimal phi, and the best 0/1 value R_01,
and whether some fractional phi attains R_full strictly outside the 0/1 hull."""
import numpy as np
from itertools import combinations
from scipy.optimize import linprog
from mycielskian_check import all_shortest_geos, edges_of


def C5q(q):
    n = 5 * q
    vid = lambda i, j: i * q + j
    side = [0] * n
    adj = [set() for _ in range(n)]
    for i in range(5):
        for j in range(q):
            side[vid(i, j)] = (0 if i in (0, 2, 4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u = vid(i, a); v = vid((i + 1) % 5, b)
                adj[u].add(v); adj[v].add(u)
    M = [(vid(4, a), vid(0, b)) for a in range(q) for b in range(q)]
    G = 25 * len(M)
    return n, adj, side, G, M


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


def best_01(N, M, geos, he, cap_k=None):
    best = 0.0; bestS = None
    ks = range(1, N + 1) if cap_k is None else range(1, cap_k + 1)
    for k in ks:
        for S in combinations(range(N), k):
            Sset = set(S)
            num = sum(he[e] * min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(M)))
            val = num / k
            if val > best + 1e-12:
                best = val; bestS = S
    return best, bestS


for q in (2, 3, 4):
    n, adj, side, G, M = C5q(q)
    geos, he = geos_he(n, adj, side, M)
    rf, phi = R_full(n, M, geos, he)
    K = n + n * n - G
    # is phi 0/1?
    mx = phi.max()
    is01 = all(abs(p) < 1e-7 or abs(p - mx) < 1e-7 for p in phi)
    # how many distinct values
    vals = sorted(set(round(p / mx, 5) for p in phi if p > 1e-9))
    r01, S = best_01(n, M, geos, he, cap_k=q + 2)
    print("C5[%d]: N=%d K=%d  R_full=%.5f  R_01=%.5f  0/1-optimal? %s  |distinct phi vals|=%d %s" % (
        q, n, K, rf, r01, str(rf - r01 < 1e-7), len(vals), vals[:6]))
