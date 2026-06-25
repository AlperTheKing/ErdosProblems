#!/usr/bin/env python3
"""Precise diagnosis: WHY P<=2N fails on C_{2k+1}, and whether the exact close-step inequality
   Gamma^2 <= (N/2)(Gamma - S1) * P   ALONE already implies Gamma<=N^2 (it does NOT need P<=2N if we
   keep S1). Solve: given the close-step is an inequality in Gamma, what does it give?

   close-step:  Gamma^2 <= (N/2)(Gamma - S1) P.
   This is an upper bound on Gamma^2 in terms of (Gamma, S1, P). It does NOT by itself bound Gamma by N^2
   unless we control P. On C_{2k+1}: Gamma=N^2, S1=N, P=N^2/2, RHS=(N/2)(N^2-N)(N^2/2)=N^3(N-1)/4 >> N^4.
   So the close-step is FAR from tight on C_{2k+1} (huge slack) -- it is tight ONLY at C5[q].
   => Strategy D's Cauchy is tight at C5[q] but LOSES the C_{2k+1} family badly: P explodes there.

   The obstruction is STRUCTURAL: the two extremal families need OPPOSITE handling.
     - C5[q]: dense (deg=2N/5), quadratic; Cauchy A*P tight, P/N=5/2.
     - C_{2k+1}: sparse (deg=2), m=1, linear; P/N -> infinity.
   A single degree-weighted Cauchy with a uniform P-bound cannot be tight at both.

   TEST a fix: replace the global Cauchy by a per-bad-edge / per-component split so the C_{2k+1} family
   (handled by the trivial m=1 base case Gamma=ell^2<=N^2) is removed before applying the dense Cauchy.
   Measure: among CONNECTED-B instances with beta>=2 (so not a single odd cycle), is P<=2N?
"""
import itertools
import numpy as np
from collections import deque
import flag_engine as fe
from strategy_D_probe import adjset, maxcut, bfs_dist, c5n, cycle, petersen, gpt_k23


def analyze(N, A):
    adj = adjset(N, A)
    edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for (u, v) in edges if side[u] == side[v]]
    if not M: return None
    deg = np.array([len(adj[u]) for u in range(N)], dtype=float)
    adjB = [[] for _ in range(N)]
    for (u, v) in edges:
        if side[u] != side[v]: adjB[u].append(v); adjB[v].append(u)
    # connected-B check
    seen = [False]*N
    comp_count = 0
    for s in range(N):
        if deg[s] == 0: continue
    # treat B-connectivity among non-isolated vtxs
    Lload = np.zeros(N); Gamma = 0.0; S1 = 0.0
    for (u, v) in M:
        dd, par = bfs_dist(N, adjB, u)
        if dd[v] < 0: return ('cross',)
        ell = dd[v] + 1
        path = [v]
        while path[-1] != u: path.append(par[path[-1]])
        Cset = set(path); Gamma += ell*ell; S1 += ell
        for w in Cset: Lload[w] += ell
    beta = len(M)
    loaded = Lload > 1e-9
    P = float((Lload[loaded]/deg[loaded]).sum())
    return dict(N=N, beta=beta, Gamma=Gamma, S1=S1, P=P, P_over_N=P/N)


if __name__ == "__main__":
    print("=== diagnosis: P/N among beta>=2 instances (single odd cycle excluded) ===")
    worst_all = (0, None); worst_b2 = (0, None)
    tot = 0; b2 = 0
    for N in [5, 6, 7, 8, 9]:
        wA = 0.0; wB = 0.0
        for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
            r = analyze(n, A)
            if not isinstance(r, dict): continue
            tot += 1
            wA = max(wA, r['P_over_N'])
            if r['P_over_N'] > worst_all[0]: worst_all = (r['P_over_N'], (n, r['beta']))
            if r['beta'] >= 2:
                b2 += 1
                wB = max(wB, r['P_over_N'])
                if r['P_over_N'] > worst_b2[0]: worst_b2 = (r['P_over_N'], (n, r['beta'], r['Gamma']))
        print(f"N={n}: worst P/N (all)={wA:.4f}   worst P/N (beta>=2)={wB:.4f}")
    print(f">>> tot={tot} (beta>=2: {b2})")
    print(f">>> worst P/N overall = {worst_all[0]:.4f} at {worst_all[1]}")
    print(f">>> worst P/N beta>=2 = {worst_b2[0]:.4f} at {worst_b2[1]}")
    print(f">>> Does P<=2N hold for beta>=2? {worst_b2[0] <= 2.0 + 1e-9}")
    print()
    print("=== confirm the two extremal families pull P opposite ways ===")
    for (N, A, lab) in [(*cycle(5), 'C5(m=1)'), (*cycle(9), 'C9(m=1)'),
                        (*c5n(2), 'C5[2]'), (*c5n(4), 'C5[4]')]:
        r = analyze(N, A)
        print(f"  {lab:10s}: beta={r['beta']} Gamma={r['Gamma']:.0f}=N^2={N*N} P/N={r['P_over_N']:.3f}")
    print("DONE")
