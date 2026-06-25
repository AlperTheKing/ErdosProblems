#!/usr/bin/env python3
"""STRATEGY 7 PROBE: structure of the optimal MT25 dual metric.

QFC25: rho(B,M) <= max{1, N^2/(25m)}.  Dual MT25 metric form:
   rho = max_{ell>=0} sum_{uv in M} d^B_ell(u,v) / sum_b ell_b.

PROBE QUESTIONS:
 (Q1) Is the optimal dual metric ell* always a NONNEGATIVE COMBINATION OF CUT METRICS
      restricted to B?  (ell* in the cut cone of B).  If YES, MT25 reduces to CD directly.
 (Q2) When ell* is NOT in cut-cone(B), what L1 distortion is needed; does N^2/(25m) absorb it.
"""
import itertools, math, heapq
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N, A):
    return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N-1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c; bs = side
    return best, bs

def rho_dual_metric(N, adj, side):
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    Bset = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    m = len(M)
    if m == 0:
        return None
    adjB = [set() for _ in range(N)]
    for (u, v) in Bset:
        adjB[u].add(v); adjB[v].add(u)
    def simple_paths(s, t, maxlen=12):
        out = []
        def dfs(u, path, vis):
            if u == t:
                out.append(list(path)); return
            if len(path) > maxlen:
                return
            for w in adjB[u]:
                if w not in vis:
                    vis.add(w); path.append(w); dfs(w, path, vis); path.pop(); vis.discard(w)
        dfs(s, [s], {s}); return out
    paths = [simple_paths(s, t) for (s, t) in M]
    edge_list = Bset; nB = len(edge_list)
    offs = []; cur = 0
    for k, plist in enumerate(paths):
        offs.append(cur); cur += len(plist)
    nf = cur; KAP = nf; nvar = nf + 1
    def vi(k, pi):
        return offs[k] + pi
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    for k, plist in enumerate(paths):
        row = np.zeros(nvar)
        for pi in range(len(plist)):
            row[vi(k, pi)] = 1.0
        A_eq.append(row); b_eq.append(1.0)
    A_ub = []; b_ub = []
    for e in edge_list:
        row = np.zeros(nvar)
        for k, plist in enumerate(paths):
            for pi, p in enumerate(plist):
                pe = set(tuple(sorted((p[i], p[i+1]))) for i in range(len(p)-1))
                if e in pe:
                    row[vi(k, pi)] += 1.0
        row[KAP] = -1.0; A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nf + [(0, None)], method="highs")
    rho = res.fun
    ell = -res.ineqlin.marginals
    return rho, M, Bset, ell, m

def in_cut_cone_B(N, Bset, ell):
    edge_list = Bset; nB = len(edge_list)
    cols = []
    for mask in range(1, 1 << (N-1)):
        S = [(mask >> u) & 1 for u in range(N)]
        col = np.zeros(nB)
        for i, (u, v) in enumerate(edge_list):
            if S[u] != S[v]:
                col[i] = 1.0
        cols.append(col)
    Amat = np.array(cols).T
    ncuts = Amat.shape[1]
    res = linprog(np.zeros(ncuts), A_eq=Amat, b_eq=ell, bounds=[(0, None)]*ncuts, method="highs")
    return res.success

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4):
                A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v):
        A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4):
            add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

print("=== Q1: is optimal dual metric ell* in cut-cone(B)? ===", flush=True)
named = [("C5[1]", *c5n(1)), ("C5[2]", *c5n(2)), ("K23-N13", *gpt_k23())]
for (label, N, A) in named:
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    r = rho_dual_metric(N, adj, side)
    if r is None:
        print(f"  {label}: m=0"); continue
    rho, M, Bset, ell, m = r
    incone = in_cut_cone_B(N, Bset, ell) if N <= 14 else "skip"
    bound = max(1.0, N*N/(25.0*m))
    print(f"  {label}: N={N} m={m} rho={rho:.4f} bound={bound:.4f} ell*_in_cutcone(B)={incone}", flush=True)

print("=== exhaustive small N: how often is ell* NON-L1 (not in cut-cone B)? ===", flush=True)
for N in [5, 6, 7, 8]:
    states = fe.enumerate_graphs(N, triangle_free=True)
    tot = 0; nonl1 = 0; worst_ratio_nonl1 = 0.0
    for (n, A) in states:
        adj = adjset(n, A); mc, side = maxcut(n, adj)
        r = rho_dual_metric(n, adj, side)
        if r is None:
            continue
        rho, M, Bset, ell, m = r
        if rho < 1e-9 or np.sum(ell) < 1e-9:
            continue
        tot += 1
        if not in_cut_cone_B(n, Bset, ell):
            nonl1 += 1
            bound = max(1.0, n*n/(25.0*m))
            worst_ratio_nonl1 = max(worst_ratio_nonl1, rho/bound)
    print(f"  N={n}: instances={tot} non-L1 ell*={nonl1} worst rho/bound on non-L1={worst_ratio_nonl1:.4f}", flush=True)
print("DONE", flush=True)
