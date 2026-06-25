#!/usr/bin/env python3
"""STRATEGY 7 PROBE 2: the CORRECT L1 question.

MT25:  sum_{uv in M} d^B_ell(u,v) <= max{1, N^2/(25m)} * sum_b ell_b   for ALL ell>=0.

The shortest-path metric  D(u,v) = d^B_ell(u,v)  is what appears on the LHS. We want to know:
 (Q3) For the WORST ell (the one achieving rho), is the induced SHORTEST-PATH metric D restricted
      to the M-pairs dominated by an L1 metric that 'costs' the same on B?  Precisely, the cleanest
      reduction:  is there a representation
         d^B_ell(u,v) = sum_S a_S |1_S(u) - 1_S(v)|   (a_S >= 0)
      with  sum_S a_S * e_B(S, ~S) <= (1+eps) * sum_b ell_b  ?
   Because then sum_M d^B_ell = sum_S a_S e_M(S,~S) <= sum_S a_S e_B(S,~S) (CD) <= (1+eps) sum ell.
   That gives rho <= 1+eps -- too strong (false, K23 has rho=4/3). So pure CD canNOT give it; the
   factor must enter. The RIGHT statement uses (Sep) with the DENSITY factor.

KEY TEST: compute, for the optimal ell*, the tightest L1 representation of the shortest-path metric D
   over the M-pairs and measure the 'B-cost ratio'  R := [sum_S a_S e_B(S,~S)] / sum_b ell_b  minimized.
   MT25 LHS = sum_M D(u,v) = sum_S a_S e_M(S,~S) <= sum_S a_S e_B(S,~S) = R * sum ell.
   So rho <= min over L1-reps R.  If min R <= max{1,N^2/(25m)} we are done via CD on each cut.
   THE DENSITY FACTOR question: is min_R <= max{1, N^2/(25m)}?  (it can EXCEED 1, that is the point.)
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
    return rho, M, Bset, ell, m, adjB

def sp_metric(N, Bset, ell):
    """All-pairs shortest path distances over B with lengths ell."""
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
    """Minimize sum_S a_S e_B(S,~S) s.t. sum_S a_S |1_S(u)-1_S(v)| = D(u,v) for all M-pairs (u,v),
    a_S>=0.  Returns R = optimum / ellsum.  This is the tightest L1 'B-cost' to realize D on M-pairs.
    Constraint only on M-pairs (we only need LHS = sum over M of D)."""
    masks = list(range(1, 1 << (N-1)))
    # columns: for each cut S, vector of |1_S(u)-1_S(v)| over M-pairs; objective coeff = e_B(S,~S)
    nM = len(M)
    cols = []; obj = []
    for mask in masks:
        S = [(mask >> u) & 1 for u in range(N)]
        col = np.array([1.0 if S[u] != S[v] else 0.0 for (u, v) in M])
        eB = sum(1 for (u, v) in Bset if S[u] != S[v])
        cols.append(col); obj.append(float(eB))
    Amat = np.array(cols).T  # nM x ncuts
    obj = np.array(obj)
    b = np.array([D[u, v] for (u, v) in M])
    res = linprog(obj, A_eq=Amat, b_eq=b, bounds=[(0, None)]*len(masks), method="highs")
    if not res.success:
        return None
    return res.fun / ellsum if ellsum > 0 else None

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

print("=== Q3: min B-cost L1 representation R of shortest-path metric on M-pairs ===", flush=True)
print("    (MT25 holds via 'CD on each cut' if R <= max{1,N^2/(25m)}; R = rho would be ideal)", flush=True)
named = [("C5[1]", *c5n(1)), ("C5[2]", *c5n(2)), ("K23-N13", *gpt_k23())]
for (label, N, A) in named:
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    r = rho_and_ell(N, adj, side)
    if r is None:
        print(f"  {label}: m=0"); continue
    rho, M, Bset, ell, m, adjB = r
    ellsum = float(np.sum(ell))
    D = sp_metric(N, Bset, ell)
    R = min_Bcost_L1_rep(N, M, Bset, D, ellsum) if N <= 14 else None
    bound = max(1.0, N*N/(25.0*m))
    print(f"  {label}: N={N} m={m} rho={rho:.4f} R(minBcostL1)={R} bound={bound:.4f}", flush=True)
print("DONE", flush=True)
