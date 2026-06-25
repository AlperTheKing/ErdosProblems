#!/usr/bin/env python3
"""STRATEGY 7 CERTIFICATE TEST: the Farkas/LP-duality certificate chain.

GOAL: prove  rho(B,M) <= max{1, N^2/(25m)}.

CERTIFICATE STRUCTURE (the thing to formalize):
Step A (L1 reduction of the dual). For ANY length ell>=0 on B with induced shortest-path metric
   D(u,v)=d^B_ell(u,v), there is an EXACT cut-cone representation of D *as a metric on V*:
       D(u,v) = sum_{S} a_S |1_S(u)-1_S(v)|   for ALL u,v in V,   a_S >= 0,
   with the COST identity   sum_b ell_b  >=  sum_S a_S e_B(S,~S).
   [This is the standard fact: a shortest-path/graph metric with edge-lengths ell is in the cut cone,
    and the cheapest cut representation costs no more on B than ell does -- because ell itself, viewed
    edge by edge, decomposes each edge {x,y} (a cut of the single pair) ... NO: need the metric form.]

   The RIGHT standard fact: For shortest-path metric D of (B,ell), the layers of EVERY potential give
   cuts; D is L1 and admits a cut decomposition with sum_S a_S * (ell-length of cut) <= ... .
   We TEST the precise inequality below.

Step B (CD per cut). sum_{uv in M} D(u,v) = sum_S a_S e_M(S,~S) <= sum_S a_S e_B(S,~S) <= sum_b ell_b.
   --> gives rho <= 1.  This is the L1/cut part; it is TRUE only up to the density correction.
   The K23 obstruction (rho=4/3>1) shows the naive a_S e_B(S,~S) <= ell_b cost bound is NOT exactly
   tight; the cut decomposition of the shortest-path metric can cost MORE than ell on B. The GAP
   between sum_S a_S e_B(S,~S) and sum_b ell_b is exactly the L1 distortion, bounded by the density.

TEST: for the worst ell (=optimal dual), compute
   cutcost := min over cut-cone reps of D (on ALL pairs) of sum_S a_S e_B(S,~S),
   ratio := cutcost / sum ell   -- this is how much MORE the cut rep costs vs ell on B.
   Then  rho = sum_M D / sum ell <= sum_S a_S e_M(S,~S)/sum ell <= cutcost/sum ell = ratio... but
   we apply CD: sum_M D = sum_S a_S e_M(S,~S) <= sum_S a_S e_B(S,~S) = cutcost. So rho <= cutcost/sumell.
   Need cutcost/sumell <= max{1,N^2/(25m)}.
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

def min_cutcost_allpairs(N, Bset, D):
    """min over a_S>=0 of sum_S a_S e_B(S,~S) s.t. sum_S a_S|1_S(u)-1_S(v)| = D(u,v) for ALL pairs u<v."""
    masks = list(range(1, 1 << (N-1)))
    pairs = [(u, v) for u in range(N) for v in range(u+1, N)]
    cols = []; obj = []
    for mask in masks:
        S = [(mask >> u) & 1 for u in range(N)]
        col = np.array([1.0 if S[u] != S[v] else 0.0 for (u, v) in pairs])
        eB = sum(1 for (u, v) in Bset if S[u] != S[v])
        cols.append(col); obj.append(float(eB))
    Amat = np.array(cols).T
    obj = np.array(obj)
    b = np.array([D[u, v] for (u, v) in pairs])
    res = linprog(obj, A_eq=Amat, b_eq=b, bounds=[(0, None)]*len(masks), method="highs")
    if not res.success:
        return None, None
    a = res.x
    return res.fun, a

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

print("=== cutcost(allpairs L1 rep of D) / sum ell  vs  rho  vs  bound ===", flush=True)
named = [("C5[1]", *c5n(1)), ("C5[2]", *c5n(2)), ("K23-N13", *gpt_k23())]
for (label, N, A) in named:
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    r = rho_and_ell(N, adj, side)
    if r is None:
        print(f"  {label}: m=0"); continue
    rho, M, Bset, ell, m = r
    ellsum = float(np.sum(ell))
    D = sp_metric(N, Bset, ell)
    cc, a = min_cutcost_allpairs(N, Bset, D)
    ratio = cc/ellsum if cc is not None else None
    bound = max(1.0, N*N/(25.0*m))
    # also: cut representation cost on M directly = sum_M D
    sumMD = sum(D[u, v] for (u, v) in M)
    print(f"  {label}: N={N} m={m} rho={rho:.4f} sumMD/sumell={sumMD/ellsum:.4f} cutcost/sumell={ratio} bound={bound:.4f}", flush=True)
print("DONE", flush=True)
