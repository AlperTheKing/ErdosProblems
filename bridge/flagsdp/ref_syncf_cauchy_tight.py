#!/usr/bin/env python3
"""The Cauchy step in SYNC-F is LOSSLESS only when per-edge stretch is EQUAL, not >=.

The proposal writes Gamma = sum_M ell^2 <= N * E[sum_M d2] using "per-edge E[d2] >= ell^2/N".
But that direction of Cauchy-Schwarz needs equality to be tight: sum ell^2 = N * sum_M E[d2]
requires E[d2(e)] PROPORTIONAL to ell_e^2 with the constant = (sum ell^2)/(N * sum E[d2]).
The CLEAN necessary form: there is a measure mu (psd Gram) with
   E[d2(e)] = ell_e^2 / N exactly      (so Cauchy is tight, no slack)
   sum_B E[d2] <= N.
Then min over such of sum_B E[d2] is the REAL test. If that minimum EXCEEDS N anywhere with
Gamma<=N^2, the proposal's chain is infeasible (cannot reach Gamma<=N^2 through this route).
If the minimum equals exactly N at C5[q] (zero slack) AND <N strictly off-extremal, the route
is consistent but its binding value is a CUT/ENERGY certificate that equals Gamma at C5[q] --
i.e. self-tight by construction.

We compute:  minimize sum_B d2  s.t. d2(e)=ell_e^2/N on M, d2<=1 on B (1-Lip).
Call it Bmin. Compare Bmin to N. Also report whether the proposal's claim 'E[sum_B d2]<=N is
provable from CD' is even consistent with Bmin.
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

def parts(N, E):
    mc, side = maxcut(N, E)
    M = [(u, v) for u, v in E if side[u] == side[v]]
    B = [(u, v) for u, v in E if side[u] != side[v]]
    adjB = adjset(N, B); Dall = [bdist(N, adjB, r) for r in range(N)]
    ell = {(u, v): Dall[u][v] + 1 for (u, v) in M}
    return M, B, ell

def test(N, E, lab):
    M, B, ell = parts(N, E)
    Gamma = sum(e * e for e in ell.values())
    G = cp.Variable((N, N), PSD=True)
    def d2(u, v): return G[u, u] + G[v, v] - 2 * G[u, v]
    cons = [d2(u, v) <= 1 for (u, v) in B]
    for (u, v) in M:
        cons.append(d2(u, v) == ell[(u, v)] ** 2 / N)   # Cauchy-TIGHT per edge
    obj = cp.Minimize(cp.sum([d2(u, v) for (u, v) in B]))
    prob = cp.Problem(obj, cons)
    prob.solve(solver=cp.SCS, eps=1e-7, max_iters=80000)
    Bmin = prob.value
    if Bmin is None:
        print(f"{lab:12s} N={N:2d} Gamma={Gamma:4d} N^2={N*N:4d}  status={prob.status} (per-edge stretch INFEASIBLE under 1-Lip)")
        return
    print(f"{lab:12s} N={N:2d} Gamma={Gamma:4d} N^2={N*N:4d}  min sum_B d2 (Cauchy-tight)={round(Bmin,3):>8}  "
          f"N={N}  Bmin<=N? {'YES' if Bmin<=N+1e-2 else 'NO'}  slack(N-Bmin)={round(N-Bmin,3)}")

if __name__ == "__main__":
    print("min B-energy with per-edge stretch fixed = ell^2/N (the lossless-Cauchy point):")
    print("(zero slack at C5[q] + strict slack off-extremal => binding value is a self-tight certificate)\n")
    for q in range(1, 5):
        test(*c5q(q), f"C5[{q}]")
    test(*c5paths20(), "c5paths20")
