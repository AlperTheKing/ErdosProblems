#!/usr/bin/env python3
"""STRATEGY 7 DENSITY MECHANISM: how does N^2/(25m) bound R?

We have (from probe2/3, when rho>=1):  rho = R = min over a_S>=0 of
    [sum_S a_S e_B(S,~S)] / sum_b ell*_b      s.t.  sum_S a_S |1_S(u)-1_S(v)| = d^B_ell*(u,v) on M-pairs.

Equivalently, normalize sum_b ell*_b = 1.  Then sum_M d^B_ell*(u,v) = rho (the dual optimum), and there is
a cut representation a_S>=0 with  sum_S a_S e_M(S,~S) = sum_M d^B = rho  and sum_S a_S e_B(S,~S) = rho...
wait that says e_M-cost = e_B-cost = rho, i.e. CD is TIGHT on the representation (sum-level).

The density factor must come from a DIFFERENT inequality. Reconsider via the PRIMAL packing:
   rho = max load => odd-cycle packing nu* >= m/rho.  Combined with nu* <= N^2/25 (PROVED), we get
   m/rho <= N^2/25  <=>  rho >= 25m/N^2.  That is the WRONG direction (lower bound on rho)!
   The bound we WANT is rho <= N^2/(25m) (upper).  These are consistent only if 25m/N^2 <= N^2/(25m),
   i.e. (25m)^2 <= N^4, i.e. 25m <= N^2 -- which is the CONCLUSION.  So upper bound on rho is the crux,
   NOT derivable from nu*<=N^2/25 alone.

KEY: the upper bound rho <= N^2/(25m) is equivalent (via packing) to nu* >= m^2 * 25/N^2 = 25m^2/N^2 = (T').
   And (T') with nu*<=N^2/25 gives m <= N^2/25.  So QFC25 <=> (T'): nu* >= 25 m^2/N^2.  CONFIRM this.

THE REAL TARGET is therefore (T'): nu*(G) >= 25 tau^2 / N^2.  Let me verify (T') and probe its proof:
   nu* is the max fractional odd-cycle packing; tau=m=|M|.  We need a LOWER bound on nu*.
   LOWER bound on nu* = EXHIBIT a feasible packing of value >= 25m^2/N^2.  THE primal certificate!
   The packing comes from routing: y_C = f_{e,P}/rho for the optimal routing.  value = m/rho.
   So (T') <=> m/rho >= 25m^2/N^2 <=> rho <= N^2/(25m).  Circular with QFC25 as expected.

DIRECT route to (T'): construct a GOOD fractional odd-cycle packing of value >= 25m^2/N^2 from M-structure.
   Test: is there a SIMPLE explicit packing achieving this?  E.g. uniform on shortest odd cycles through
   each bad edge.  Measure value of: y_C = c on each shortest odd cycle (bad-edge + its B-geodesic),
   scaled to feasibility.  Compare value to 25m^2/N^2.
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

def nu_star(N, adj, edges):
    cyc = all_odd_cycles(N, adj)
    if not cyc:
        return 0.0
    eidx = {e: i for i, e in enumerate(edges)}; nC = len(cyc); nE = len(edges)
    Aub = np.zeros((nE, nC))
    for j, (_, es) in enumerate(cyc):
        for e in es:
            Aub[eidx[e], j] = 1.0
    res = linprog(-np.ones(nC), A_ub=Aub, b_ub=np.ones(nE), bounds=[(0, None)]*nC, method="highs")
    return -res.fun

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

print("=== (T'): nu* >= 25 m^2 / N^2  (the real target; QFC25 <=> this) ===", flush=True)
named = [("C5[1]", *c5n(1)), ("C5[2]", *c5n(2)), ("C5[3]", *c5n(3)), ("K23-N13", *gpt_k23())]
for (label, N, A) in named:
    adj = adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    m = len(M)
    if m == 0:
        continue
    nu = nu_star(N, adj, edges)
    target = 25.0*m*m/(N*N)
    print(f"  {label}: N={N} m={m} nu*={nu:.4f} 25m^2/N^2={target:.4f} Tprime_ok={nu>=target-1e-7}", flush=True)

print("=== exhaustive (T') ===", flush=True)
for N in [5, 6, 7, 8, 9]:
    states = fe.enumerate_graphs(N, triangle_free=True)
    tot = 0; viol = 0; worst = 1e9
    for (n, A) in states:
        adj = adjset(n, A); edges = [frozenset((u, v)) for u in range(n) for v in adj[u] if v > u]
        if not edges:
            continue
        mc, side = maxcut(n, adj)
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        m = len(M)
        if m == 0:
            continue
        nu = nu_star(n, adj, edges)
        target = 25.0*m*m/(n*n)
        tot += 1
        slack = nu - target
        if slack < -1e-7:
            viol += 1
        worst = min(worst, nu/target if target > 0 else 1e9)
    print(f"  N={n}: instances={tot} Tprime_violations={viol} worst nu*/(25m^2/N^2)={worst:.4f}", flush=True)
print("DONE", flush=True)
