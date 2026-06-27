#!/usr/bin/env python3
"""Does the ELECTRICAL optimizer E* ever do strictly better than the constructive
uniform routing E_unif in a way that matters for SC? If SC margin is comfortably
positive for E_unif everywhere, the optimizer is never needed -> energy relaxation
adds nothing. Report, per instance: (E_unif - E*) and (RHS_SC - E_unif). The crux
claim is that proving SC requires bounding SOME routing's energy from above, and the
cheapest such bound (uniform) already works -- i.e. the open task = bound E_unif, not E*."""
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

def energies(N, A, edge_paths):
    nv = A.shape[1]; Q = A.T @ A
    x0 = np.zeros(nv)
    for idxs in edge_paths:
        x0[idxs] = 1.0/len(idxs)
    E_unif = float(x0 @ Q @ x0)
    cons = []
    for idxs in edge_paths:
        a = np.zeros(nv); a[idxs] = 1.0
        cons.append({'type': 'eq', 'fun': (lambda x, a=a: a @ x - 1.0),
                     'jac': (lambda x, a=a: a)})
    res = minimize(lambda x: float(x @ Q @ x), x0, jac=lambda x: 2*Q@x,
                   constraints=cons, bounds=[(0, None)]*nv, method='SLSQP',
                   options={'maxiter': 1000, 'ftol': 1e-13})
    return E_unif, res.fun

def main(Nmax):
    worst_unif_margin = 1e9; worst_case = None
    max_gap = -1e9; gap_case = None  # E_unif - E*
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
            b = build(n, adj, side, M)
            if b is None:
                continue
            paths, pe, he, edge_paths, Amat = b
            E_unif, Estar = energies(N, Amat, edge_paths)
            n_checked += 1
            K = N + (N*N - G); mean = G/N
            RHS = mean*mean*N + (N/(N-1))*(K-mean)**2
            m_unif = RHS - E_unif
            if m_unif < worst_unif_margin:
                worst_unif_margin = m_unif; worst_case = (N, G, E_unif, Estar, RHS)
            gap = E_unif - Estar
            if gap > max_gap:
                max_gap = gap; gap_case = (N, G, E_unif, Estar)
    print("checked", n_checked)
    print("worst (RHS_SC - E_unif) margin =", round(worst_unif_margin,5), "at (N,G,E_unif,E*,RHS)=", worst_case)
    print("max (E_unif - E*) gap =", round(max_gap,5), "at (N,G,E_unif,E*)=", gap_case)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
