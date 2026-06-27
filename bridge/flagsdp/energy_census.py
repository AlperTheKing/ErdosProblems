#!/usr/bin/env python3
"""Census sweep of the ENERGY-ELECTRICAL angle for GPI.
For each connected triangle-free graph (N<=Nmax) with a connected-B max cut and finite Gamma:
  - compute E* = min_x sum_v T_x(v)^2 (energy-optimal routing), its max-load maxE
  - compare maxE to K=N+(N^2-Gamma); also tau* (true L-inf optimum) for reference on small N
  - record excess = E* - Gamma^2/N and ratio excess/(N^2-Gamma)
Report: any case where energy-routing maxload > K (would kill the 'energy gives GPI' hope),
and the worst (closest-to-violating) cases. Also check the candidate inequality
   E* <= Gamma^2/N + something  and whether maxE <= K always.
"""
import sys
import numpy as np
from scipy.optimize import linprog, minimize
import flag_engine
from mycielskian_check import gamma_min_cut, all_shortest_geos, Bconnected

def adj_sets(n, A):
    return [set(j for j in range(n) if (A[i] >> j) & 1) for i in range(n)]

def is_connected(n, adj):
    from collections import deque
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
    f = lambda x: float(x @ Q @ x)
    g = lambda x: 2 * Q @ x
    cons = [make_eq((lambda idxs: (lambda: np.eye(1))())) for _ in []]
    cons = []
    for idxs in edge_paths:
        a = np.zeros(nv); a[idxs] = 1.0; cons.append(make_eq(a))
    x0 = np.zeros(nv)
    for idxs in edge_paths:
        x0[idxs] = 1.0 / len(idxs)
    res = minimize(f, x0, jac=g, constraints=cons, bounds=[(0, None)] * nv,
                   method='SLSQP', options={'maxiter': 1000, 'ftol': 1e-13})
    T = A @ res.x
    return res.fun, T

def tau_star(N, A, edge_paths, nM):
    npaths = A.shape[1]; nvar = npaths + 1; tau = npaths
    c = np.zeros(nvar); c[tau] = 1.0
    Aeq = np.zeros((nM, nvar)); beq = np.ones(nM)
    for ei, idxs in enumerate(edge_paths):
        for k in idxs:
            Aeq[ei, k] = 1.0
    Aub = np.zeros((N, nvar)); Aub[:, :npaths] = A; Aub[:, tau] = -1.0; bub = np.zeros(N)
    res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                  bounds=[(0, None)] * npaths + [(0, None)], method="highs")
    return res.fun

def main(Nmax):
    worst_maxE_minus_K = -1e9; worst_case = None
    worst_ratio = -1e9; worst_ratio_case = None
    n_checked = 0; n_viol_energy = 0; n_viol_tau = 0
    ratios = []
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
            maxE = T.max()
            n_checked += 1
            dE = maxE - K
            if dE > worst_maxE_minus_K:
                worst_maxE_minus_K = dE; worst_case = (N, G, K, maxE, len(M))
            if dE > 1e-6:
                n_viol_energy += 1
            # tau* for small N only (LP cheap)
            if N <= 11:
                ts = tau_star(N, Amat, edge_paths, len(M))
                if ts > K + 1e-6:
                    n_viol_tau += 1
            floor = G * G / N
            if N * N - G > 0:
                r = (Estar - floor) / (N * N - G)
                ratios.append(r)
                if r > worst_ratio:
                    worst_ratio = r; worst_ratio_case = (N, G, Estar, floor, len(M))
    print(f"Nmax={Nmax}: checked {n_checked} (graph,maxcut) instances")
    print(f"  energy-routing maxload>K violations: {n_viol_energy}")
    print(f"  worst maxE-K = {worst_maxE_minus_K:.5f}  at (N,G,K,maxE,beta)={worst_case}")
    print(f"  tau*>K violations (N<=11): {n_viol_tau}")
    if ratios:
        print(f"  excess/(N^2-G): max={max(ratios):.4f} mean={np.mean(ratios):.4f} min={min(ratios):.4f}")
        print(f"  worst-ratio case (N,G,E*,floor,beta)={worst_ratio_case}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
