#!/usr/bin/env python3
"""Find the reverse bound that is tight at BOTH C5[q] and C_{2k+1}, and test if Strategy D closes.

Observed exact equalities we must preserve:
  At C5[q]:  cycle-degree (6) tight for every C_e; sum deg*L = (N/2)(Gamma - S1); 2e/N = 2N/5.
  At C_{2k+1} (m=1): the single cycle is the whole graph; deg=2; L(v)=ell=N on all N vertices; Gamma=N^2.

Key structural quantities at the extremals (per-cycle weighting w_e=ell_e):
  define  T2 := sum_e ell_e^2 * (sum_{v in C_e} deg(v))  ... no. Let's hunt the closing identity.

THE CLEAN STRATEGY-D CHAIN (degree-weighted Cauchy-Schwarz on the cycle-degree quantity).
We have two sums over bad edges e (weight ell_e on cycle C_e):
   A := sum_e ell_e * (sum_{v in C_e} deg(v))        [(6) gives A <= (N/2) sum_e ell_e(ell_e-1) = (N/2)(Gamma-S1)]
   Want a LOWER bound on A that forces Gamma<=N^2 and is tight at both families.
Note A = sum_v deg(v) L(v). By Cauchy-Schwarz with the *measure* deg(v):
   (sum_v deg(v) * (L(v)/deg(v)) )^2 <= (sum_v deg(v)) (sum_v deg(v) (L(v)/deg(v))^2)
   i.e. (sum_v L(v))^2 <= 2e * sum_v L(v)^2/deg(v)   -- already tested, slack at C5[q].
Instead weight by L:  Cauchy on  sum_v L(v) = sum_v sqrt(deg(v) L(v)) * sqrt(L(v)/deg(v)):
   Gamma^2 = (sum_v L)^2 <= (sum_v deg(v) L(v)) (sum_v L(v)/deg(v)) = A * sum_v (L(v)/deg(v)).
   => Gamma^2 <= A * P,  P := sum_v L(v)/deg(v).
   With A <= (N/2)(Gamma-S1):   Gamma^2 <= (N/2)(Gamma-S1) * P.
   CLOSES to Gamma<=N^2 iff  (N/2)(Gamma-S1) P <= N^2 Gamma, i.e.  P (Gamma-S1) <= 2 N Gamma.
   Since Gamma-S1 < Gamma: SUFFICES  P <= 2N. MEASURE P=sum_v L(v)/deg(v) and P/N (need <=2; tight where?).
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
    A_sum = float(np.dot(deg, Lload))
    P = float((Lload[loaded]/deg[loaded]).sum())     # sum_v L(v)/deg(v)
    # the Cauchy:  Gamma^2 <= A * P
    cauchy_AP = A_sum * P
    # closing test: Gamma^2 <= (N/2)(Gamma-S1)*P, and final Gamma<=N^2 iff P(Gamma-S1)<=2N Gamma
    rhs_close = (N/2.0)*(Gamma - S1)*P
    final_ok = Gamma <= N*N + 1e-7
    res = dict(label=label, N=N, beta=beta, Gamma=Gamma, S1=S1, A=A_sum, P=P,
               P_over_N=P/N, cauchy_AP_ok=cauchy_AP >= Gamma*Gamma - 1e-6,
               close_step_ok=Gamma*Gamma <= rhs_close + 1e-6,
               PGamma_test=P*(Gamma - S1) <= 2*N*Gamma + 1e-6, N2=N*N, GammaN2=final_ok)
    if verbose:
        print(f"{label:10s} N={N:3d} beta={beta:3d} Gamma={Gamma:7.1f} N^2={N*N:5d}  "
              f"P=sum L/deg={P:7.3f}  P/N={P/N:.4f}")
        print(f"   Cauchy Gamma^2 <= A*P : {Gamma*Gamma:.0f} <= {cauchy_AP:.1f}  ok={res['cauchy_AP_ok']}")
        print(f"   close-step Gamma^2 <= (N/2)(Gamma-S1)P={rhs_close:.1f} ok={res['close_step_ok']}")
        print(f"   FINAL test P(Gamma-S1)<=2N*Gamma : {P*(Gamma-S1):.1f} <= {2*N*Gamma:.1f} -> {res['PGamma_test']}")
    return res


if __name__ == "__main__":
    print("=== STRATEGY D: the P = sum_v L(v)/deg(v) closing route (need P<=2N) ===\n")
    named = [(*cycle(5), "C5"), (*cycle(7), "C7"), (*cycle(9), "C9"), (*cycle(11), "C11"),
             (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]"), (*c5n(4), "C5[4]"),
             (*petersen(), "Petersen"), (*gpt_k23(), "K23-N13")]
    for (N, A, lab) in named:
        analyze(N, A, lab); print()
    print("--- exhaustive tri-free N<=9: does the FINAL P-chain hold? worst P/N? ---")
    worst_P = 0.0; close_viol = 0; final_viol = 0; cauchy_viol = 0; tot = 0
    worst_inst = None
    for N in [5, 6, 7, 8, 9]:
        wN = 0.0
        for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
            r = analyze(n, A, "", verbose=False)
            if not isinstance(r, dict): continue
            tot += 1
            if not r['cauchy_AP_ok']: cauchy_viol += 1
            if not r['close_step_ok']: close_viol += 1
            if not r['PGamma_test']: final_viol += 1
            if r['P_over_N'] > wN: wN = r['P_over_N']
            if r['P_over_N'] > worst_P: worst_P = r['P_over_N']; worst_inst = (n, r['beta'], r['Gamma'], r['P'])
        print(f"N={N}: worst P/N={wN:.4f}")
    print(f">>> tot={tot}  Cauchy(A*P) viol={cauchy_viol}  close-step viol={close_viol}  "
          f"FINAL P(Gamma-S1)<=2NGamma viol={final_viol}")
    print(f">>> worst P/N={worst_P:.4f} (inst N,beta,Gamma,P={worst_inst})")
    print("DONE")
