#!/usr/bin/env python3
"""The CLEANEST checkable sub-claim of the energy angle.
Let x* = energy-optimal routing, T its load, mean=Gamma/N, E*=sum T^2 = min energy.
The Chebyshev (single-outlier) bound gives:  max_v T(v) <= mean + sqrt((N-1)(E*/N - mean^2)).
If we can prove an ENERGY UPPER BOUND  E* <= U(N,Gamma)  with
      mean + sqrt((N-1)(U/N - mean^2)) <= K = N+(N^2-Gamma),
then GPI follows. Rearranged, the bridge needs:
   (SC)   E* <= Gamma^2/N + (N/(N-1)) * (N + N^2 - Gamma - Gamma/N)^2.
Define RHS_SC. Test margin RHS_SC - E* over census; if always >=0 this is the target energy bound.
ALSO test the simpler hoped-for linear bound  E* <= Gamma^2/N + c*(N^2-Gamma)  and find min c that works,
and whether c is bounded (if c blows up, linear energy bound is false -> need the quadratic SC form).
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

def build(N, adj, side, M):
    paths = []; pe = []; he = []; edge_paths = []
    for ei, (u, v) in enumerate(M):
        geos = all_shortest_geos(N, adj, side, u, v)
        if not geos:
            return None
        h = len(geos[0]); he.append(h); idxs = []
        for P in geos:
            idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    A = np.zeros((N, len(paths)))
    for k, P in enumerate(paths):
        w = he[pe[k]]
        for v in P:
            A[v, k] += w
    return paths, pe, he, edge_paths, A

def make_eq(a):
    return {'type': 'eq', 'fun': (lambda x, a=a: a @ x - 1.0), 'jac': (lambda x, a=a: a)}

def energy_star(N, A, edge_paths):
    nv = A.shape[1]; Q = A.T @ A
    f = lambda x: float(x @ Q @ x); g = lambda x: 2 * Q @ x
    cons = []
    for idxs in edge_paths:
        a = np.zeros(nv); a[idxs] = 1.0; cons.append(make_eq(a))
    x0 = np.zeros(nv)
    for idxs in edge_paths:
        x0[idxs] = 1.0 / len(idxs)
    res = minimize(f, x0, jac=g, constraints=cons, bounds=[(0, None)] * nv,
                   method='SLSQP', options={'maxiter': 1000, 'ftol': 1e-13})
    return res.fun

def main(Nmax):
    worst_SC = 1e9; sc_case = None; n_sc_fail = 0
    max_c = -1e9; c_case = None; n_checked = 0
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
            b = build(n, adj, side, M)
            if b is None:
                continue
            paths, pe, he, edge_paths, Amat = b
            K = N + (N * N - G); mean = G / N
            Estar = energy_star(N, Amat, edge_paths)
            n_checked += 1
            RHS_SC = mean * mean * N + (N / (N - 1)) * (K - mean) ** 2  # E* <= this  (note sum form: floor=G^2/N=mean^2*N)
            margin = RHS_SC - Estar
            if margin < worst_SC:
                worst_SC = margin; sc_case = (N, G, Estar, RHS_SC, K)
            if margin < -1e-6:
                n_sc_fail += 1
            if N * N - G > 0:
                c = (Estar - mean * mean * N) / (N * N - G)
                if c > max_c:
                    max_c = c; c_case = (N, G, Estar, c)
    print(f"Nmax={Nmax}: checked {n_checked}")
    print(f"  Quadratic sub-claim (SC) E* <= G^2/N + (N/(N-1))(K-G/N)^2:")
    print(f"    failures (margin<0): {n_sc_fail}/{n_checked}")
    print(f"    worst margin (RHS_SC - E*) = {worst_SC:.5f}  at (N,G,E*,RHS_SC,K)={sc_case}")
    print(f"  Linear bound E* <= G^2/N + c*(N^2-G): min feasible c = max observed = {max_c:.4f}")
    print(f"    at (N,G,E*,c)={c_case}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
