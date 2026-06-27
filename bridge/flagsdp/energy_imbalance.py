#!/usr/bin/env python3
"""Probe the IMBALANCE bridge for the energy angle.
At energy-optimal routing x*, load T(v); mean = Gamma/N. Define imbalance D = max_v T(v) - Gamma/N.
GPI(L-inf) wants max_v T(v) <= K = N + (N^2-Gamma).
Equivalently (since K - Gamma/N = N + N^2 - Gamma - Gamma/N):
   want  D <= K - Gamma/N = N - Gamma/N + (N^2 - Gamma) = (N-Gamma/N) + (N^2-Gamma).
Since Gamma <= N^2 (target), Gamma/N <= N so N - Gamma/N >= 0.

Candidate energy-based bridge: the spread max_v T - min_v T is controlled by sqrt(N * variance),
variance = E*/N - (Gamma/N)^2. Test whether
   max_v T(v) <= Gamma/N + sqrt((N-1)(E* - Gamma^2/N)/N)   (Chebyshev/std bound on max deviation)
and whether THAT RHS <= K. This is the honest energy->Linf chain; quantify the loss factor.
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
    return res.fun, A @ res.x

def main(Nmax):
    worst_cheb = -1e9; cheb_case = None
    worst_chebRHS_minus_K = -1e9; chk_case = None
    n_cheb_fail = 0; n_checked = 0
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
            K = N + (N * N - G)
            Estar, T = energy_star(N, Amat, edge_paths)
            mean = G / N; maxT = T.max()
            var = Estar / N - mean * mean
            # Chebyshev-type max-deviation bound: max_v T - mean <= sqrt((N-1)*var) (tight for one outlier)
            cheb = mean + np.sqrt(max(var, 0.0) * (N - 1))
            n_checked += 1
            # how loose: does the Chebyshev SURROGATE already exceed K? if so this bridge is too lossy
            d = cheb - K
            if d > worst_chebRHS_minus_K:
                worst_chebRHS_minus_K = d; chk_case = (N, G, K, maxT, cheb)
            if cheb > K + 1e-6:
                n_cheb_fail += 1
            # also report actual max vs cheb surrogate gap
            gap = cheb - maxT
            if gap > worst_cheb:
                worst_cheb = gap; cheb_case = (N, G, maxT, cheb)
    print(f"Nmax={Nmax}: checked {n_checked}")
    print(f"  Chebyshev surrogate cheb=mean+sqrt((N-1)var):")
    print(f"    cases where cheb>K (energy->Linf bridge fails to give GPI): {n_cheb_fail}/{n_checked}")
    print(f"    worst cheb-K = {worst_chebRHS_minus_K:.4f} at (N,G,K,maxT,cheb)={chk_case}")
    print(f"    worst (cheb-maxT) looseness = {worst_cheb:.4f} at (N,G,maxT,cheb)={cheb_case}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
