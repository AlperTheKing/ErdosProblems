# Stress the dichotomy: push for gapped cases with HIGH R/K (toward/over 1/3).
# Use random TF graphs across many sizes/densities + witnesses C5[q].
import numpy as np, random
from scipy.optimize import linprog
from itertools import combinations
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut

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

def rand_tf(N, p, seed):
    random.seed(seed); adj = [set() for _ in range(N)]
    edges = [(u, v) for u in range(N) for v in range(u + 1, N)]; random.shuffle(edges)
    for (u, v) in edges:
        if random.random() < p and not (adj[u] & adj[v]): adj[u].add(v); adj[v].add(u)
    return adj

THIRD = 1.0 / 3.0
worst_gapped = (0,)
viol = []
seen = 0
for seed in range(3000):
    N = random.Random(seed).choice([9, 10, 11, 12])
    p = random.Random(seed + 7).choice([0.4, 0.5, 0.6, 0.7])
    adj = rand_tf(N, p, seed)
    res, mc = gamma_min_cut(N, adj, edges_of(adj), cap=2000)
    if not res: continue
    side, G, M = res
    if not M: continue
    geos, he = geos_he(N, adj, side, M)
    rf = R_full(N, M, geos, he); r01 = R01(N, M, geos, he)
    K = N + N * N - G; gap = rf - r01; ratio = rf / K
    seen += 1
    if gap > 1e-6:
        if ratio > worst_gapped[0]: worst_gapped = (ratio, gap, seed, N, G)
        if ratio > THIRD + 1e-9: viol.append((ratio, gap, seed, N, G))
print("random graphs evaluated: %d" % seen)
print("worst gapped R/K = %s" % str(worst_gapped))
print("dichotomy violations (gap>0 AND R/K>1/3): %d" % len(viol))
for v in viol[:10]: print("  VIOL", v)
