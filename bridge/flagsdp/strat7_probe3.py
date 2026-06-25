#!/usr/bin/env python3
"""STRATEGY 7 PROBE 3: is rho = R ALWAYS (L1-tightness), exhaustively?

R := min over L1 reps a_S>=0 of [sum_S a_S e_B(S,~S)] / (sum_b ell*_b), where ell* is the optimal
dual metric and we require sum_S a_S |1_S(u)-1_S(v)| = d^B_ell*(u,v) on all M-pairs.

If rho = R exhaustively, then the cleanest certificate route is:
   rho = R = min L1 B-cost  =>  reduces MT25 to bounding the CUT-METRIC concurrent flow, where CD applies
   per cut.  Then the density factor must come from bounding R.

Actually the deeper claim to test: is the WHOLE concurrent flow LP equivalent to its CUT relaxation?
i.e. is  rho(B,M) = max over CUT metrics delta_S restricted to B of  sum_M 1_S-crossing / e_B(S,~S)?
That maximum (single-cut) is exactly  max_S e_M(S,~S)/e_B(S,~S) <= 1 by CD -- too weak (gives rho<=1, FALSE).
So rho != single-cut.  But the cut-CONE (L1) dual can still equal rho.  THE TEST: rho == R exhaustively.
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

def rho_and_ell(N, adj, side):
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
    edge_list = Bset
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

def sp_metric(N, Bset, ell):
    adj = {}
    for (x, y), w in zip(Bset, ell):
        adj.setdefault(x, []).append((y, w)); adj.setdefault(y, []).append((x, w))
    D = np.full((N, N), 1e18)
    for s in range(N):
        D[s, s] = 0.0; pq = [(0.0, s)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > D[s, u]:
                continue
            for v, w in adj.get(u, []):
                nd = d + w
                if nd < D[s, v]:
                    D[s, v] = nd; heapq.heappush(pq, (nd, v))
    return D

def min_Bcost_L1_rep(N, M, Bset, D, ellsum):
    masks = list(range(1, 1 << (N-1)))
    cols = []; obj = []
    for mask in masks:
        S = [(mask >> u) & 1 for u in range(N)]
        col = np.array([1.0 if S[u] != S[v] else 0.0 for (u, v) in M])
        eB = sum(1 for (u, v) in Bset if S[u] != S[v])
        cols.append(col); obj.append(float(eB))
    Amat = np.array(cols).T
    obj = np.array(obj)
    b = np.array([D[u, v] for (u, v) in M])
    res = linprog(obj, A_eq=Amat, b_eq=b, bounds=[(0, None)]*len(masks), method="highs")
    if not res.success:
        return None
    return res.fun / ellsum if ellsum > 0 else None

print("=== rho == R exhaustively over triangle-free N<=8 ===", flush=True)
for N in [5, 6, 7, 8]:
    states = fe.enumerate_graphs(N, triangle_free=True)
    tot = 0; eq = 0; maxgap = 0.0; worst = None
    for (n, A) in states:
        adj = adjset(n, A); mc, side = maxcut(n, adj)
        r = rho_and_ell(n, adj, side)
        if r is None:
            continue
        rho, M, Bset, ell, m = r
        ellsum = float(np.sum(ell))
        if rho < 1e-9 or ellsum < 1e-9:
            continue
        tot += 1
        D = sp_metric(n, Bset, ell)
        R = min_Bcost_L1_rep(n, M, Bset, D, ellsum)
        if R is None:
            continue
        gap = abs(R - rho)
        if gap < 1e-6:
            eq += 1
        else:
            if gap > maxgap:
                maxgap = gap; worst = (n, m, rho, R)
    print(f"  N={n}: instances={tot} (rho==R)={eq} maxgap={maxgap:.2e} worst={worst}", flush=True)
print("DONE", flush=True)
