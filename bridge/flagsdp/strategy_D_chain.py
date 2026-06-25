#!/usr/bin/env python3
"""STRATEGY D - close the chain? Analyze the candidate reverse bounds and where they break.

At C5[q]:  every vertex has deg=2k=2N/5; e=N*k=N^2/5*... let's get exact. N=5k. deg=2k each. e=N*k?
   edges: each vertex deg 2k, e = N*2k/2 = N k = 5k*k=5k^2. So 2e/N = 2k = 2N/5.
   Gamma = q^2 * 25 where q=k^2? No: m=q^2 bad edges? Actually for C5[k]: beta = ... let's just read numerics.

The chain we WANT:
   (N/2)(Gamma - S1) >= LHS = sum_v deg(v) L(v) >= REVERSE(Gamma)  ==> bound on Gamma.
The cycle-degree gives the UPPER bound (left ineq). For the chain to yield Gamma<=N^2 we need a LOWER bound
REVERSE(Gamma) on sum deg*L that, combined with (N/2)(Gamma-S1) >= REVERSE, gives Gamma<=N^2.

Candidate reverse lower bounds tested (each must be (a) TRUE always, (b) tight at C5[q]):
  R1  sum deg*L >= (2e/N) Gamma                              -- Chebyshev (FALSE: 33 viols)
  R3  sum deg*L >= 2*(sum_v L)  = 2 Gamma  [since deg>=2 on every vertex carrying load? test]
  R4  sum deg*L >= (4 beta / N) * Gamma     [2e/N replaced by min over loaded set]
  R5  the *2-lambda<=deg* style: relate to congestion.

Also test the DIRECT degree-weighted Cauchy that ESCAPES uniform charging:
   Gamma = sum_v L(v) = sum_v sqrt(deg(v)) * (L(v)/sqrt(deg(v)))
        <= sqrt(sum_v deg(v)) * sqrt(sum_v L(v)^2/deg(v))     [Cauchy-Schwarz]
   => Gamma^2 <= (2e) * sum_v L(v)^2/deg(v).
   Is sum_v L(v)^2/deg(v) <= N^2 Gamma /(2e) ... need link.  MEASURE sum L^2/deg and the implied bound.

The MOST PROMISING degree-weighted route (escapes degree-blind charging):
   Cauchy:  Gamma = sum_v L(v) <= sqrt(N_load) * sqrt(sum_v L(v)^2),  N_load=#{v: L(v)>0}.
   AND we want sum_v L(v)^2 controlled by sum_v deg(v) L(v) (the (6)-bounded quantity):
        sum_v L(v)^2 <= (max_v L(v)/min_loaded deg) ... no.
   Test directly:  is  sum_v L(v)^2 <= (N/2) (Gamma - S1) * (something)?  We have sum deg*L = LHS<=(N/2)(Gamma-S1).
   If L(v) <= deg(v)*c then sum L^2 <= c * sum deg*L. MEASURE c* = max_v L(v)/deg(v).
"""
import itertools
import numpy as np
from collections import deque
import flag_engine as fe
from strategy_D_probe import adjset, maxcut, bfs_dist, c5n, cycle, petersen, gpt_k23


def analyze(N, A, label, verbose=True):
    adj = adjset(N, A)
    edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for (u, v) in edges if side[u] == side[v]]
    if not M: return None
    deg = np.array([len(adj[u]) for u in range(N)], dtype=float)
    adjB = [[] for _ in range(N)]
    for (u, v) in edges:
        if side[u] != side[v]: adjB[u].append(v); adjB[v].append(u)
    Lload = np.zeros(N); Gamma = 0.0; S1 = 0.0
    for (u, v) in M:
        dd, par = bfs_dist(N, adjB, u)
        if dd[v] < 0: return ('cross',)
        ell = dd[v] + 1
        path = [v]
        while path[-1] != u: path.append(par[path[-1]])
        Cset = set(path); Gamma += ell*ell; S1 += ell
        for w in Cset: Lload[w] += ell
    beta = len(M); e_G = len(edges)
    loaded = Lload > 1e-9
    nload = int(loaded.sum())
    # ratio c* = max over loaded v of L(v)/deg(v)
    cstar = float(np.max(Lload[loaded]/deg[loaded])) if nload else 0.0
    sumL2 = float((Lload**2).sum())
    sum_degL = float(np.dot(deg, Lload))
    sumL2_over_deg = float((Lload[loaded]**2/deg[loaded]).sum())
    res = dict(label=label, N=N, beta=beta, Gamma=Gamma, S1=S1, nload=nload,
               cstar=cstar, sumL2=sumL2, sum_degL=sum_degL, sumL2_over_deg=sumL2_over_deg,
               e_G=e_G, N2=N*N, GammaN2=Gamma <= N*N+1e-7)
    # candidate degree-weighted Cauchy:  Gamma^2 <= 2e * sum L^2/deg
    res['cauchy_deg_bound'] = 2*e_G*sumL2_over_deg     # >= Gamma^2 ?
    res['cauchy_deg_ok'] = res['cauchy_deg_bound'] >= Gamma*Gamma - 1e-6
    # candidate:  sum L^2 <= c* * sum deg*L  (always true by def of c*: L^2 = L*L <= c* deg * L)
    res['sumL2_le_cstar_degL'] = sumL2 <= cstar*sum_degL + 1e-6
    # candidate chain via c*:  Gamma^2/nload <= sum L^2 <= c* sum deg*L <= c* (N/2)(Gamma-S1)
    #   => Gamma^2 <= nload * c* (N/2)(Gamma-S1) <= N * c* (N/2) Gamma  => Gamma <= N^2 c*/2.
    #   So this CLOSES iff c* <= 2.  MEASURE c*.
    if verbose:
        print(f"{label:10s} N={N:3d} beta={beta:3d} Gamma={Gamma:7.1f} N^2={N*N:5d}  "
              f"c*=max L/deg={cstar:.4f}  nload={nload}")
        print(f"   degree-Cauchy: Gamma^2={Gamma*Gamma:.0f} <= 2e*sumL2/deg={res['cauchy_deg_bound']:.1f}? "
              f"{res['cauchy_deg_ok']}")
        print(f"   chain const c*/2={cstar/2:.4f}  (CLOSES via this chain iff c*<=2)")
    return res


if __name__ == "__main__":
    print("=== STRATEGY D chain analysis: the c* = max_v L(v)/deg(v) constant ===\n")
    named = [(*cycle(5), "C5"), (*cycle(7), "C7"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]"),
             (*c5n(4), "C5[4]"), (*petersen(), "Petersen"), (*gpt_k23(), "K23-N13")]
    for (N, A, lab) in named:
        analyze(N, A, lab); print()
    print("--- exhaustive tri-free N<=9: worst c*, and does degree-Cauchy ever fail? ---")
    worst_c = 0.0; worst_c_inst = None; dc_viol = 0; tot = 0
    # also: does the c*-chain const ever EXCEED 2 (the closing threshold)?
    over2 = 0
    for N in [5, 6, 7, 8, 9]:
        wN = 0.0
        for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
            r = analyze(n, A, "", verbose=False)
            if not isinstance(r, dict): continue
            tot += 1
            if not r['cauchy_deg_ok']: dc_viol += 1
            if r['cstar'] > 2 + 1e-9: over2 += 1
            if r['cstar'] > worst_c: worst_c = r['cstar']; worst_c_inst = (n, r['beta'], r['Gamma'])
            wN = max(wN, r['cstar'])
        print(f"N={N}: worst c*={wN:.4f}")
    print(f">>> tot={tot}  degree-Cauchy viol={dc_viol}  worst c*={worst_c:.4f} (inst N,beta,Gamma={worst_c_inst})")
    print(f">>> #instances with c*>2 (c*-chain would NOT close)={over2}")
    print("DONE")
