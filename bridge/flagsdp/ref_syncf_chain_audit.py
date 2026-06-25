#!/usr/bin/env python3
"""Audit the TWO load-bearing steps of SYNC-F separately.

The closing chain needs ONE measure mu with all of:
   (i)   per-edge:  E_mu[d2(u,v)] >= ell(uv)^2 / N   for every uv in M
   (ii)  M<=B:      E_mu[sum_M d2] <= E_mu[sum_B d2]
   (iii) budget:    E_mu[sum_B d2] <= N

Step (ii) is the UNPROVEN quadratic ("L2") coarea claim. Test whether it is even TRUE
as a pointwise statement: can a single 1-Lipschitz-on-B embedding VIOLATE sum_M d2 <= sum_B d2?
Maximize (sum_M d2 - sum_B d2) over psd Gram with d2<=1 on B. If the max is > 0, the L2 coarea
inequality is FALSE for some 1-Lip potential, so (ii) cannot hold for a point mass and the
proposal must rely on cancellation across the mixture mu -- which is exactly the unproved content.

Step (i)+(iii) feasibility: is the per-edge stretch target jointly consistent with the budget?
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

def test_quadratic_coarea(N, E, lab):
    M, B, ell = parts(N, E)
    G = cp.Variable((N, N), PSD=True)
    def d2(u, v): return G[u, u] + G[v, v] - 2 * G[u, v]
    cons = [d2(u, v) <= 1 for (u, v) in B]
    cons.append(G[0, 0] == 0)
    obj = cp.Maximize(cp.sum([d2(u, v) for (u, v) in M]) - cp.sum([d2(u, v) for (u, v) in B]))
    prob = cp.Problem(obj, cons)
    prob.solve(solver=cp.SCS, eps=1e-7, max_iters=60000)
    val = prob.value
    verdict = "VIOLATES L2 coarea (>0)" if (val is not None and val > 1e-3) else "L2 coarea holds (<=0)"
    print(f"  [QUAD-COAREA] {lab:11s}: max(sum_M d2 - sum_B d2) over 1-Lip-on-B = "
          f"{round(val,3) if val is not None else val}  ({verdict})")
    return val

def test_i_iii(N, E, lab):
    M, B, ell = parts(N, E)
    Gamma = sum(e * e for e in ell.values())
    G = cp.Variable((N, N), PSD=True)
    def d2(u, v): return G[u, u] + G[v, v] - 2 * G[u, v]
    cons = [d2(u, v) <= 1 for (u, v) in B]
    cons.append(cp.sum([d2(u, v) for (u, v) in B]) <= N)
    for (u, v) in M:
        cons.append(d2(u, v) >= ell[(u, v)] ** 2 / N)
    prob = cp.Problem(cp.Minimize(0), cons)
    prob.solve(solver=cp.SCS, eps=1e-7, max_iters=60000)
    print(f"  [(i)+(iii) feas] {lab:11s}: status={prob.status}  Gamma={Gamma} N^2={N*N}")
    return prob.status

if __name__ == "__main__":
    print("=== Is the L2 coarea inequality sum_M d2 <= sum_B d2 TRUE for every 1-Lip-on-B? ===")
    for q in range(1, 5):
        test_quadratic_coarea(*c5q(q), f"C5[{q}]")
    test_quadratic_coarea(*c5paths20(), "c5paths20")
    print()
    print("=== Feasibility of SYNC-F per-edge(i)+budget(iii) ===")
    for q in range(1, 5):
        test_i_iii(*c5q(q), f"C5[{q}]")
    test_i_iii(*c5paths20(), "c5paths20")
