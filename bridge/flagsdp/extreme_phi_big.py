#!/usr/bin/env python3
"""Stress-test 0/1-extremality of the GPI maximizer on LARGER structured graphs:
C5[5] (N=25), Petersen, Mycielskian(C5)=Grotzsch (N=11), and a few random triangle-free graphs.
For each: solve R_full (LP), check whether the optimal phi is 0/1 (single distinct nonzero value),
and whether a perturbation toward a 0/1 vertex keeps the value (extreme-face test).
We do NOT enumerate all S (too big); instead we test 0/1-ness of the LP optimum directly and
re-solve forcing phi in {0,1}-hull is not possible, so we report the fractional structure."""
import numpy as np, random
from scipy.optimize import linprog
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut, mycielskian, bdistB


def C5q(q):
    n = 5 * q
    vid = lambda i, j: i * q + j
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
    return -res.fun, res.x[:nphi], he


def report(name, N, adj, side, G, M):
    if not M:
        print("%s: no bad edges" % name); return
    rf, phi, he = R_full(N, adj, side, M)
    K = N + N * N - G
    mx = phi.max() if phi.size else 0.0
    vals = sorted(set(round(p / mx, 4) for p in phi if p > 1e-7)) if mx > 1e-9 else []
    is01 = (len(vals) <= 1)
    # round the LP phi to its support-as-indicator and evaluate R_01 of THAT set
    S = set(v for v in range(N) if phi[v] > 0.5 * mx) if mx > 1e-9 else set()
    if S:
        geos = [all_shortest_geos(N, adj, side, u, v) for (u, v) in M]
        num = sum(he[e] * min(sum(1 for v in P if v in S) for P in geos[e]) for e in range(len(M)))
        r01_supp = num / len(S)
    else:
        r01_supp = 0.0
    print("%s: N=%d K=%d R_full=%.4f R_full/K=%.4f  0/1? %s  |distinctvals|=%d  R_01(supp)=%.4f  |S|=%d" % (
        name, N, K, rf, rf / K, str(is01), len(vals), r01_supp, len(S)))


# C5[5] = N=25 tight extremal
n, adj, side, G, M = C5q(5)
report("C5[5]", n, adj, side, G, M)

# Grotzsch = Mycielskian(C5), N=11, chromatic 4, triangle-free
C5edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
N, adjm = mycielskian(5, C5edges)
res, mc = gamma_min_cut(N, adjm, edges_of(adjm))
if res:
    side, G, M = res
    report("Grotzsch=M(C5)", N, adjm, side, G, M)

# Petersen (triangle-free, but band-max may have no bad edges if bipartite-ish) -> compute
pet = [(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),(5,7),(7,9),(9,6),(6,8),(8,5)]
adjp = [set() for _ in range(10)]
for (u, v) in pet:
    adjp[u].add(v); adjp[v].add(u)
res, mc = gamma_min_cut(10, adjp, edges_of(adjp))
if res:
    side, G, M = res
    report("Petersen", 10, adjp, side, G, M)

# random triangle-free graphs N=12..16
def rand_tf(N, p, seed):
    random.seed(seed)
    adj = [set() for _ in range(N)]
    edges = [(u, v) for u in range(N) for v in range(u + 1, N)]
    random.shuffle(edges)
    for (u, v) in edges:
        if random.random() < p:
            if not (adj[u] & adj[v]):  # keep triangle-free
                adj[u].add(v); adj[v].add(u)
    return adj

cnt01 = 0; tot = 0; worst = 0.0
for seed in range(40):
    N = random.choice([12, 13, 14, 15, 16])
    adj = rand_tf(N, 0.5, seed)
    res, mc = gamma_min_cut(N, adj, edges_of(adj), cap=2000)
    if not res:
        continue
    side, G, M = res
    if not M:
        continue
    rf, phi, he = R_full(N, adj, side, M)
    mx = phi.max() if phi.size else 0.0
    vals = sorted(set(round(p / mx, 4) for p in phi if p > 1e-7)) if mx > 1e-9 else []
    tot += 1
    if len(vals) <= 1:
        cnt01 += 1
    K = N + N * N - G
    worst = max(worst, rf / K)
print("random TF graphs: %d/%d had 0/1 optimum; max R_full/K=%.4f" % (cnt01, tot, worst))
