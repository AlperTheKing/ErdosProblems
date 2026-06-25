#!/usr/bin/env python3
"""STRATEGY 7 FINAL: the candidate KEY LEMMA bounding rho = sum_S a_S e_B(S).

From the optimal cut decomposition (a_S>=0) of the dual metric on M-pairs (normalize sum_b ell_b=1):
   rho = sum_M D(u,v) = sum_S a_S e_M(S,~S) = sum_S a_S e_B(S,~S)   (CD tight at the sum level on the optimum).
   each demand uv in M has D(u,v) = sum_{S sep uv} a_S >= ell-distance >= 4*min_ell (geodesic length >=4
   in B with >= 4 edges).  Actually each M-pair has d_B(u,v)>=4 => any feasible ell with sum ell=1 has
   D(u,v) <= (path length).  The KEY constraint linking to m and N:

CANDIDATE KEY INEQUALITY (to bound rho):
   sum_M D(u,v) <= N^2/(25 m) * sum_b ell_b.
   Mirror of nu*<=N^2/25: define lambda_v = sum_{S: a_S, v in S} a_S (separator-vertex load). Each used
   cut contributes e_B(S) B-edges crossing.  We want a Cauchy giving the 25.

TEST the LOWER-BOUND form (T'): nu* >= 25 m^2 / N^2 directly via an EXPLICIT packing certificate built
   from the optimal routing, and measure the four exact deficit terms of (Def) to confirm where slack lives.

Also: test the CLEANEST candidate sufficient lemma  -- 'each M-demand is routed at distance >= 4 and the
   total B-length is >= ... '.  Concretely verify:
       (KL)  m * (min geodesic length)^2  <=  N^2  * (max load)      ???
   i.e. relate m, geodesic length, N, and rho. Let me just measure all quantities.
"""
import itertools, math, heapq
import numpy as np
from collections import deque
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

def all_odd_cycles(N, adj, maxlen=None):
    if maxlen is None:
        maxlen = N
    seen = set(); out = []
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                es = frozenset(frozenset((path[i], path[(i+1) % len(path)])) for i in range(len(path)))
                if es not in seen:
                    seen.add(es); out.append((tuple(path), es))
            elif w not in ps and w > start and len(path) < maxlen:
                path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N):
        dfs(s, s, [s], {s})
    return out

def nu_star_packing(N, adj, edges):
    """returns nu*, and an optimal packing y over odd cycles."""
    cyc = all_odd_cycles(N, adj)
    if not cyc:
        return 0.0, [], None
    eidx = {e: i for i, e in enumerate(edges)}; nC = len(cyc); nE = len(edges)
    Aub = np.zeros((nE, nC))
    for j, (_, es) in enumerate(cyc):
        for e in es:
            Aub[eidx[e], j] = 1.0
    res = linprog(-np.ones(nC), A_ub=Aub, b_ub=np.ones(nE), bounds=[(0, None)]*nC, method="highs")
    return -res.fun, cyc, res.x

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

# Verify the (Def)-style identity in the OPTIMAL-PACKING form gives (T'). We confirm the chain
# nu* = sum y_C; lambda_v = sum_{C ni v} y_C; 2 lambda_v <= d(v); L=sum y_C(|C|-1); Cauchy.
# Already proven nu* <= N^2/25. We want the LOWER bound nu* >= 25 m^2/N^2.  This needs a LOWER bound on
# the packing, NOT an upper bound -- a DIFFERENT argument.  Measure the gap structure:

print("=== diagnostic: where does the (T') lower bound slack come from? ===", flush=True)
print("    cols: m, nu*, 25m^2/N^2, ratio nu*/(25m^2/N^2), and the routing congestion rho", flush=True)
for (label, N, A) in [("C5[1]", *c5n(1)), ("C5[2]", *c5n(2)), ("C5[3]", *c5n(3)), ("K23-N13", *gpt_k23())]:
    adj = adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    m = len(M)
    if m == 0:
        continue
    nu, cyc, y = nu_star_packing(N, adj, edges)
    target = 25.0*m*m/(N*N)
    ratio = nu/target if target > 0 else 0
    # of the packing, how many positive cycles, mean length
    pos = [(c, y[j]) for j, c in enumerate(cyc) if y[j] > 1e-9]
    Lsum = sum(w*(len(c[0])-1) for c, w in pos)
    t = Lsum/nu if nu > 0 else 0
    print(f"  {label}: N={N} m={m} nu*={nu:.4f} target(25m^2/N^2)={target:.4f} ratio={ratio:.4f} "
          f"#poscyc={len(pos)} t=L/nu={t:.3f}", flush=True)
print("DONE", flush=True)
