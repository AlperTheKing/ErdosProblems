"""
The KEY Strategy-2 quantitative test.

Strategy 2 reduces MT25 to bounding the L1-distortion of the shortest-path metric d_ell,
but PAID FOR by the density factor. The clean target inequality I want to test:

  (DECOMP)  For the optimal dual metric d=d_ell on V (induced by B-lengths ell),
            sum_{uv in M} d(u,v)  <=  sum_b ell_b  +  (1/(2m')) * sum_{uv in M} d(u,v)^2 * (m/(N^2/25 - ...))
  ... too vague. Instead test the PROVABLE chain:

  Chain A (the one I will assert in the writeup):
    Step 1 (cut part):  d decomposes as d = d_L1 + d_perp  where d_L1 is the maximal L1
            (cut-cone) metric dominated by d. On d_L1, MT25 holds with factor 1 (= CD/coarea).
    Step 2 (residual):  d_perp is supported on "non-laminar crossings". We must show
            sum_M d_perp(u,v) <= (N^2/(25m) - 1)_+ * sum_b ell_b.

  The cleanest sufficient inequality, which I test here numerically over the obstructions:
    (RES)   sum_{uv in M} d(u,v)  <=  sum_b ell_b  +  (1/5) sqrt(m) * (N/5) ... ???

Let me instead test the EXACT thing the density factor must absorb, namely whether

   rho(B,M) <= 1 + (something <= N^2/(25m) - 1).

Equivalently test  m * rho <= max{m, N^2/25}, i.e.  m*rho <= N^2/25 whenever rho>1,
AND m*rho is exactly the "routed packing denominator". Since nu* >= m/rho, this says
   nu* >= m/rho >= 25 m^2 / N^2 ... that's (T'). So the SINGLE inequality to test is:

   (CORE)   m * rho(B,M) <= max{ m , N^2/25 }.

Equivalently  rho <= max{1, N^2/(25m)}  = QFC25 itself. (tautology check, but lets us see slack.)

The REAL question for the recursion: can we PROVE  m*rho <= N^2/25  directly when rho>1?
Test: is it true that  rho > 1  ==>  m <= N^2/25  (i.e. the bound already holds at the M level)?
That would mean: the non-L1 regime ONLY occurs when m is already small enough that N^2/(25m)>=1
gives all the room. Check the contrapositive over data: does m > N^2/25 force rho=1 (L1/weakly bip)?
"""
import math, itertools
import numpy as np
from scipy.optimize import linprog
import sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
sys.path.insert(0, r'E:\Projects\ErdosProblems\attack3_scratch')
import flag_engine as fe
from laminar_recursion import adjset, maxcut, rho_mcf

print("Testing: does m > N^2/25 (bound at M-level tight/exceeded) force rho=1 ?", flush=True)
print("If YES universally, then QFC25 splits cleanly: rho>1 => m<N^2/25 => factor covers it.", flush=True)
for N in [5, 6, 7, 8, 9, 10]:
    states = fe.enumerate_graphs(N, triangle_free=True)
    viol_split = 0; n_rho_gt1 = 0; n_m_ge = 0; both = 0; total = 0
    worst_case = None; worst_prod = 0
    for (n, A) in states:
        adj = adjset(n, A); edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
        if not edges: continue
        mc, side = maxcut(n, adj)
        M = [(min(u, v), max(u, v)) for (u, v) in edges if side[u] == side[v]]
        if not M: continue
        adjB = [set() for _ in range(n)]
        for (u, v) in edges:
            if side[u] != side[v]: adjB[u].add(v); adjB[v].add(u)
        m = len(M)
        rho = rho_mcf(n, adjB, M)
        total += 1
        mge = (m >= n*n/25.0 - 1e-9)
        rgt = (rho > 1.0 + 1e-7)
        if mge: n_m_ge += 1
        if rgt: n_rho_gt1 += 1
        if mge and rgt: both += 1  # would be the dangerous case
        # the core product m*rho vs N^2/25
        prod = m*rho
        if prod > worst_prod:
            worst_prod = prod; worst_case = (n, m, round(rho, 3), round(prod, 2), round(n*n/25.0, 2))
    print(f"N={N}: total={total} #(m>=N^2/25)={n_m_ge} #(rho>1)={n_rho_gt1} "
          f"#(BOTH, dangerous)={both} | max(m*rho)={worst_prod:.2f} at {worst_case} (N^2/25={N*N/25.0:.2f})", flush=True)
print("DONE", flush=True)
