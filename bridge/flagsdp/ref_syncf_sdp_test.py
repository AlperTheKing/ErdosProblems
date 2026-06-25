#!/usr/bin/env python3
"""DECISIVE adversarial test of SYNC-F (the 'concretely stuck on' Hilbert-embedding form).

The proposal's closing chain is:
   Gamma = sum_M ell^2  <=  N * E[sum_M dpsi^2]      (per-edge stretch >= ell^2/N)
                         <=  N * E[sum_B dpsi^2]      (M-energy <= B-energy)
                         <=  N * N = N^2              (B-energy budget <= N)
So a NECESSARY condition for the route to close is the existence of a 1-Lipschitz-on-B
embedding psi (equivalently a measure mu on such) with
   sum_M ||dpsi||^2 >= Gamma/N   AND   sum_B ||dpsi||^2 <= N.
We test the strongest possible version by SDP relaxation: maximize sum_M ||dpsi||^2
subject to 1-Lipschitz-on-B (||dpsi||^2<=1 per B-edge) and sum_B ||dpsi||^2 <= N.
Call optimum S*. The route NEEDS S* >= Gamma/N on every graph where Gamma<=N^2 is true.

This SDP is a RELAXATION (allows any psd Gram, i.e. any measure on 1-Lip potentials and more),
so if even this relaxed S* < Gamma/N, the route is provably dead on that graph.
"""
import numpy as np, cvxpy as cp
from collections import deque

def adjset(N, E):
    adj = [set() for _ in range(N)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return adj

def bdist(N, adjB, s):
    d = [-1] * N; d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def maxcut(N, E):
    best = -1; bs = None
    for m in range(1 << (N - 1)):
        s = [(m >> u) & 1 for u in range(N)]
        c = sum(1 for u, v in E if s[u] != s[v])
        if c > best:
            best = c; bs = s
    return best, bs

def c5q(q):
    N = 5 * q; part = lambda v: v // q; E = []
    for u in range(N):
        for v in range(u + 1, N):
            if (part(u) - part(v)) % 5 in (1, 4):
                E.append((u, v))
    return N, E

def c5paths20():
    N = 20; E = []
    x = lambda i: i % 5; y = lambda i: 5 + i % 5
    z = lambda i: 10 + i % 5; w = lambda i: 15 + i % 5
    for i in range(5):
        E += [(x(i), x((i + 1) % 5)), (x(i), y(i)), (y(i), z(i)),
              (z(i), w(i)), (w(i), x((i + 1) % 5))]
    return N, E

def test(N, E, lab):
    mc, side = maxcut(N, E)
    M = [(u, v) for u, v in E if side[u] == side[v]]
    B = [(u, v) for u, v in E if side[u] != side[v]]
    adjB = adjset(N, B); Dall = [bdist(N, adjB, r) for r in range(N)]
    ell = {(u, v): Dall[u][v] + 1 for (u, v) in M}
    Gamma = sum(e * e for e in ell.values())
    G = cp.Variable((N, N), PSD=True)
    def d2(u, v): return G[u, u] + G[v, v] - 2 * G[u, v]
    cons = []
    for (u, v) in B:
        cons.append(d2(u, v) <= 1)
    cons.append(cp.sum([d2(u, v) for (u, v) in B]) <= N)
    obj = cp.Maximize(cp.sum([d2(u, v) for (u, v) in M]))
    prob = cp.Problem(obj, cons)
    prob.solve(solver=cp.SCS, eps=1e-7, max_iters=50000)
    Sstar = prob.value
    need = Gamma / N
    ok = "YES" if (Sstar is not None and Sstar >= need - 1e-2) else "NO  <-- ROUTE FAILS"
    print(f"{lab:12s} N={N:2d} m={len(M):2d} Gamma={Gamma:4d} N^2={N*N:4d}  "
          f"S*(max M-energy)={Sstar if Sstar is None else round(Sstar,3):>8}  "
          f"need Gamma/N={round(need,3):>7}  status={prob.status}  SYNCF={ok}")
    return Sstar, need

if __name__ == "__main__":
    print("SDP relaxation of SYNC-F: maximize sum_M ||dpsi||^2  s.t. 1-Lip-on-B & sum_B<=N")
    print("(if S* < Gamma/N on any graph with Gamma<=N^2, the proposed route is dead there)\n")
    for q in range(1, 5):
        test(*c5q(q), f"C5[{q}]")
    test(*c5paths20(), "c5paths20")
