"""The dangerous failure mode (caveat b): uniform routing is suboptimal vs LP. If the
uniform maxT-K margin SHRINKS on the same graphs where uniform is most suboptimal
(maxT-tau* large), then at larger N uniform betweenness could over-concentrate past K
even while the true routing stays under. Cross-tabulate, per (graph,maxcut):
  subopt = maxT_uniform - tau*_LP   (how far uniform is from optimal)
  margin = K - maxT_uniform          (uniform's safety to the bound)
Report the cases of largest subopt and their margins, and the smallest positive margin."""
import numpy as np
from scipy.optimize import linprog
from flag_engine import enumerate_graphs
from mycielskian_check import all_shortest_geos, Bconnected, edges_of, maxcut_value, gamma_of

def adjset(n, A):
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if (A[i] >> j) & 1:
                adj[i].add(j)
    return adj

def geos_for(N, adj, side, M):
    paths = []; pe = []; he = []; edge_paths = []
    for ei, (u, v) in enumerate(M):
        geos = all_shortest_geos(N, adj, side, u, v); h = len(geos[0]); he.append(h); idxs = []
        for P in geos:
            idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    return paths, pe, he, edge_paths

def lp_tau(N, paths, pe, he, edge_paths, M):
    nvar = len(paths) + 1; tau = len(paths); c = np.zeros(nvar); c[tau] = 1.0
    Aeq = np.zeros((len(M), nvar)); beq = np.ones(len(M))
    for ei, idxs in enumerate(edge_paths):
        for k in idxs:
            Aeq[ei, k] = 1.0
    Aub = np.zeros((N, nvar))
    for k, P in enumerate(paths):
        w = he[pe[k]]
        for v in P:
            Aub[v, k] += w
    for v in range(N):
        Aub[v, tau] = -1.0
    res = linprog(c, A_ub=Aub, b_ub=np.zeros(N), A_eq=Aeq, b_eq=beq,
                  bounds=[(0, None)] * len(paths) + [(0, None)], method="highs")
    return res.fun

def maxT_uniform(N, paths, pe, he, edge_paths, M):
    T = np.zeros(N)
    for ei, idxs in enumerate(edge_paths):
        g = len(idxs); h = he[ei]; w = 1.0 / g
        for k in idxs:
            for x in paths[k]:
                T[x] += h * w
    return T.max()

rows = []  # (subopt, margin, n, G)
min_margin = 1e9; mm_case = None
for N in range(5, 11):
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = adjset(n, A); Ee = edges_of(adj); mc = maxcut_value(n, Ee)
        for mask in range(1 << (n - 1)):
            c = sum(1 for (u, v) in Ee if ((mask >> u) & 1) != ((mask >> v) & 1))
            if c != mc:
                continue
            side = [(mask >> u) & 1 for u in range(n)]
            if not Bconnected(n, adj, side):
                continue
            G, M = gamma_of(n, adj, side)
            if G is None or not M:
                continue
            paths, pe, he, ep = geos_for(n, adj, side, M)
            mt = maxT_uniform(n, paths, pe, he, ep, M)
            K = n + (n * n - G)
            margin = K - mt
            if margin < min_margin:
                min_margin = margin; mm_case = (n, G, K, mt)
            tl = lp_tau(n, paths, pe, he, ep, M)
            subopt = mt - tl
            rows.append((subopt, margin, n, G))
rows.sort(reverse=True)
print("Top 12 by uniform-suboptimality (subopt=maxT_unif - tau*_LP):")
print("  subopt  margin(K-maxT)  N  Gamma")
for r in rows[:12]:
    print("  %.4f   %.4f        %d   %d" % r)
print("Smallest uniform margin (K-maxT) over all pairs: %.6f at (n,G,K,maxT)=%s" % (min_margin, mm_case))
neg = [r for r in rows if r[1] < -1e-9]
print("pairs with margin<0 (uniform VIOLATES K): %d" % len(neg))
