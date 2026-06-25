#!/usr/bin/env python3
"""STRATEGY E certificate search.

Goal: find a SPECTRAL lower bound L(G) with  nu*(G) >= L(G) >= 25 t^2/N^2.

We exhaustively test triangle-free 2-connected graphs N<=9 and the named hard
instances, evaluating several candidate lower bounds and reporting:
  - whether candidate <= nu*  (must hold to be a valid LB on nu*)
  - whether candidate >= 25t^2/N^2  (must hold to finish the theorem)

Candidates (all elementary/spectral):
 (E1) Hoffman odd-transversal:  tau* >= e + N*lam_min/2 ?  [signed-Laplacian Hoffman]
      For the ALL-NEGATIVE signing (frustration), tau = min frustration; a Hoffman
      bound for frustration index uses lambda_min of adjacency.
 (E2) -lam_min based packing LB:  N*(-lam_min - (something)) ...
 (E3) the exact tau* = nu* (LP) -- the ground truth, to confirm 25t^2/N^2.
 (E4) energy/Rayleigh:  for the bad-edge incidence, a Rayleigh quotient LB.

We also dump, for each instance, the optimal dual VERTEX potential of the
nu* LP restricted to a quadratic form, to detect whether the binding certificate
is rank-1 (=> spectral) or genuinely higher-rank (=> spectral LB impossible).
"""
import itertools
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe
from strat_e_probe import (adjset, maxcut, nu_star, tau_int, lambda_eigs,
                           petersen, c5n, gpt_k23, theta46, all_odd_cycles)


def signed_frustration_lb(N, adj):
    """Hoffman-type LB for the minimum frustration (all-negative signing).
    For all-negative signed graph, switching class frustration index = min #edges
    to delete to make bipartite = tau (odd-cycle transversal, edge version) ONLY
    when graph is connected & we use the e-MaxCut form. Hoffman/eigenvalue bound:
      frustration >= (e - mu_max * N / 2)/?  -- we test the cleanest form
      tau = e - MaxCut, and MaxCut <= (e/2) + (N/4)*(-lam_min)  [Mohar-Poljak].
    => tau = e - MaxCut >= e/2 - (N/4)*(-lam_min).
    This is a LOWER bound on tau (integral), and tau* <= tau, so it does NOT
    directly lower bound nu*=tau*. We record it to see scaling vs 25t^2/N^2.
    """
    lams = lambda_eigs(N, adj)
    lmin = lams[0]
    e = sum(1 for u in range(N) for v in adj[u] if v > u)
    return e / 2.0 - (N / 4.0) * (-lmin)


def run():
    print("=== Strategy E certificate diagnostics ===", flush=True)
    print("Per instance: t, nu*(=tau*), 25t^2/N^2, MoharPoljak tau-LB, ratio nu*/(25t^2/N^2)", flush=True)
    named = [(*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*theta46(), "theta46"),
             (*c5n(1), "C5[1]"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]")]
    for (N, A, label) in named:
        adj = adjset(N, A)
        ns, edges, cyc = nu_star(N, adj)
        t = tau_int(N, adj)
        target = 25.0 * t * t / (N * N)
        mp = signed_frustration_lb(N, adj)
        ratio = ns / target if target > 1e-9 else float('inf')
        print(f"  {label:10s} N={N:2d} t={t:2d} nu*={ns:7.3f} 25t^2/N^2={target:7.3f} "
              f"MP-tauLB={mp:6.2f} nu*/target={ratio:5.3f}", flush=True)

    # Exhaustive: does nu*/target ever drop below 1? Where is it closest (the true frontier)?
    print("\n=== Exhaustive 2-connected tri-free N<=9: min(nu* - 25t^2/N^2) and where ===", flush=True)
    for N in range(5, 10):
        states = fe.enumerate_graphs(N, triangle_free=True)
        worst = 1e9
        worst_inst = None
        cnt = 0
        for (n, A) in states:
            adj = adjset(n, A)
            t = tau_int(n, adj)
            if t == 0:
                continue
            # only need atoms with positive beta; cheap filter
            ns, edges, cyc = nu_star(n, adj)
            target = 25.0 * t * t / (n * n)
            slack = ns - target
            cnt += 1
            if slack < worst:
                worst = slack
                worst_inst = (n, t, ns, target)
        print(f"  N={N}: {cnt} graphs(beta>0), min(nu*-25t^2/N^2)={worst:+.4f} at "
              f"(n,t,nu*,target)={worst_inst}", flush=True)


if __name__ == "__main__":
    run()
