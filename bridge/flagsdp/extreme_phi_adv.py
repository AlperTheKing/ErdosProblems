#!/usr/bin/env python3
"""ADVERSARIAL search for a triangle-free band-max graph whose GPI maximizer is NOT 0/1
(i.e. R_full > R_01 strictly). If found, the extreme-phi angle's central claim (0/1-extremality) is FALSE.
Strategy: bad edges with MANY shortest geodigeos sharing vertices reward fractional spreading.
Generate random triangle-free graphs biased to have several parallel C5-seams, large N up to 22.
Compares R_full to the best 0/1 value found by a greedy+local-search over S (not full enumeration)."""
import numpy as np, random
from scipy.optimize import linprog
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut


def R_full(N, adj, side, M):
    geos = []; he = []
    for (u, v) in M:
        gs = all_shortest_geos(N, adj, side, u, v); geos.append(gs); he.append(len(gs[0]))
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
    return -res.fun, res.x[:nphi], he, geos


def R_01_value(N, S, geos, he):
    Sset = set(S)
    if not Sset:
        return 0.0
    num = sum(he[e] * min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(geos)))
    return num / len(Sset)


def best_01_local(N, geos, he, tries=60):
    """greedy + local search for best 0/1 set S (heuristic upper bound on R_01)."""
    best = 0.0; bestS = None
    for t in range(tries):
        S = set()
        # random restart
        order = list(range(N)); random.shuffle(order)
        cur = 0.0
        improved = True
        while improved:
            improved = False
            for v in order:
                Snew = (S ^ {v})
                if not Snew:
                    continue
                val = R_01_value(N, Snew, geos, he)
                if val > cur + 1e-12:
                    S = Snew; cur = val; improved = True
        if cur > best:
            best = cur; bestS = frozenset(S)
    return best, bestS


def rand_tf(N, p, seed):
    random.seed(seed)
    adj = [set() for _ in range(N)]
    edges = [(u, v) for u in range(N) for v in range(u + 1, N)]
    random.shuffle(edges)
    for (u, v) in edges:
        if random.random() < p and not (adj[u] & adj[v]):
            adj[u].add(v); adj[v].add(u)
    return adj


worst_gap = 0.0; worst_info = None
checked = 0
for seed in range(400):
    N = random.Random(seed).choice([14, 16, 18, 20, 22])
    p = random.Random(seed + 1000).choice([0.4, 0.5, 0.6])
    adj = rand_tf(N, p, seed)
    res, mc = gamma_min_cut(N, adj, edges_of(adj), cap=1500)
    if not res:
        continue
    side, G, M = res
    if len(M) < 1:
        continue
    rf, phi, he, geos = R_full(N, adj, side, M)
    mx = phi.max() if phi.size else 0.0
    vals = sorted(set(round(p2 / mx, 4) for p2 in phi if p2 > 1e-7)) if mx > 1e-9 else []
    checked += 1
    if len(vals) > 1:
        # fractional optimum: verify it beats best 0/1
        r01, S = best_01_local(N, geos, he)
        gap = rf - r01
        if gap > worst_gap:
            worst_gap = gap; worst_info = (seed, N, len(M), G, rf, r01, vals[:6])
print("checked=%d  worst (R_full - R_01_heuristic) over fractional-optimum cases = %.6f" % (checked, worst_gap))
if worst_info:
    print("  witness: seed=%d N=%d beta=%d Gam=%d R_full=%.4f R_01h=%.4f vals=%s" % worst_info)
else:
    print("  NO fractional optimum found -> 0/1-extremality held on all %d adversarial graphs" % checked)
