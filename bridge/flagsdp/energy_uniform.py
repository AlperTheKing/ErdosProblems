#!/usr/bin/env python3
"""Test the EXPLICIT uniform routing (each bad edge split equally over its shortest geodesics).
Its load T_unif(v) and energy E_unif = sum T_unif^2. Question:
  (A) does E_unif <= RHS_SC (so the constructive uniform routing already proves SC, no optimization)?
  (B) does max_v T_unif(v) <= K directly (uniform routing already proves GPI)?  -- if yes the energy detour is moot
  (C) compare E_unif to E* (how far is uniform from electrical-optimal).
This isolates whether the OPEN step is 'bound a specific routing's load via CD' (constructive) vs needs the optimizer.
"""
import sys
import numpy as np
from scipy.optimize import minimize
import flag_engine
from mycielskian_check import gamma_min_cut, all_shortest_geos
from collections import deque

def adj_sets(n, A):
    return [set(j for j in range(n) if (A[i] >> j) & 1) for i in range(n)]

def is_connected(n, adj):
    seen = {0}; q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen) == n

def loads_uniform(N, adj, side, M):
    T = np.zeros(N)
    for (u, v) in M:
        geos = all_shortest_geos(N, adj, side, u, v)
        if not geos:
            return None
        h = len(geos[0]); w = h / len(geos)
        for P in geos:
            for x in P:
                T[x] += w
    return T

def main(Nmax):
    n_A_fail = 0; n_B_fail = 0; worstA = 1e9; worstB = -1e9; A_case = None; B_case = None
    n_checked = 0
    for N in range(5, Nmax + 1):
        for (n, A) in flag_engine.enumerate_graphs(N, triangle_free=True):
            adj = adj_sets(n, A)
            if not is_connected(n, adj):
                continue
            E = [(i, j) for i in range(n) for j in adj[i] if j > i]
            res, mc = gamma_min_cut(n, adj, E)
            if res is None:
                continue
            side, G, M = res
            if len(M) == 0:
                continue
            T = loads_uniform(N, adj, side, M)
            if T is None:
                continue
            n_checked += 1
            assert abs(T.sum() - G) < 1e-6, (T.sum(), G)
            K = N + (N * N - G); mean = G / N
            E_unif = float((T * T).sum())
            RHS_SC = mean * mean * N + (N / (N - 1)) * (K - mean) ** 2
            mA = RHS_SC - E_unif
            if mA < worstA:
                worstA = mA; A_case = (N, G, E_unif, RHS_SC)
            if mA < -1e-6:
                n_A_fail += 1
            mB = T.max() - K
            if mB > worstB:
                worstB = mB; B_case = (N, G, T.max(), K)
            if mB > 1e-6:
                n_B_fail += 1
    print(f"Nmax={Nmax}: checked {n_checked}")
    print(f"  (A) uniform routing satisfies SC (E_unif<=RHS_SC)? failures={n_A_fail}; worst margin={worstA:.4f} at {A_case}")
    print(f"  (B) uniform routing satisfies GPI directly (maxT_unif<=K)? failures={n_B_fail}; worst maxT-K={worstB:.4f} at {B_case}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
