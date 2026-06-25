#!/usr/bin/env python3
"""STRATEGY E: is the tight nu* certificate at C5[n] / hard atoms rank-1 (spectral)?

We compute the optimal odd-cycle packing y* and look at the dual: an assignment
of edge prices q_a in [0,1] (sum over odd cycle >=1) minimizing sum q_a... actually
the LP dual of nu* (max packing, edge-cap 1) is:
   min sum_a x_a  s.t.  sum_{a in C} x_a >= 1 for all odd cycles C,  x>=0
i.e. tau* = fractional odd-cycle EDGE cover. By LP duality nu* = tau*.

KEY DIAGNOSTIC for whether a spectral lower bound on nu* can reach 25t^2/N^2:
The Lovasz-theta-style relaxation of odd-cycle packing. We instead directly test
the strongest *fractional relaxation* that is spectrally computable: the
ODD-COCLIQUE / cut-norm relaxation.

Concretely we test the candidate identity at tightness:
   At C5[n], every edge price x_a = 1/5 is dual-optimal (each C5 has 5 edges,
   sum = 1). tau* = e/5 = (5n^2)/5 ... let's just confirm the dual is uniform =>
   tightness is governed by a UNIFORM (rank-1, all-ones-like) certificate scaled
   by the cycle structure. We compute the dual x* and its 'rank' via the support
   pattern and check if x* is constant on edge-orbits.
"""
import itertools
import numpy as np
from scipy.optimize import linprog
from strat_e_probe import (adjset, maxcut, tau_int, all_odd_cycles,
                           petersen, c5n, gpt_k23, theta46)


def tau_star_dual(N, adj):
    """fractional odd-cycle edge cover (= nu* by duality). Return value + edge prices x*."""
    edges = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u]
    eidx = {e: i for i, e in enumerate(edges)}
    ne = len(edges)
    cyc = all_odd_cycles(N, adj)
    if not cyc:
        return 0.0, edges, {}
    nc = len(cyc)
    # min sum x_a  s.t.  for each cycle C: sum_{a in C} x_a >= 1
    c = np.ones(ne)
    A_ub = np.zeros((nc, ne))
    b_ub = -np.ones(nc)
    for j, C in enumerate(cyc):
        for e in C:
            A_ub[j][eidx[tuple(sorted(e))]] = -1.0
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * ne, method="highs")
    prices = {edges[i]: res.x[i] for i in range(ne)}
    return res.fun, edges, prices


def run():
    named = [(*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*theta46(), "theta46"),
             (*c5n(1), "C5[1]"), (*c5n(2), "C5[2]")]
    for (N, A, label) in named:
        adj = adjset(N, A)
        val, edges, prices = tau_star_dual(N, adj)
        t = tau_int(N, adj)
        vals = sorted(set(round(v, 4) for v in prices.values()))
        nz = sum(1 for v in prices.values() if v > 1e-7)
        print(f"{label:10s} N={N:2d} t={t:2d} tau*(=nu*)={val:7.3f} distinct_edge_prices={vals} "
              f"#nonzero={nz}/{len(edges)}", flush=True)
        # For K23-N13: print which edges carry nonzero price (the signature-rotation core)
        if label == "K23-N13":
            print("   K23 nonzero-price edges:", flush=True)
            for e, v in sorted(prices.items()):
                if v > 1e-7:
                    print(f"      {e}: {v:.4f}", flush=True)


if __name__ == "__main__":
    run()
