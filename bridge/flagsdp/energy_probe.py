#!/usr/bin/env python3
"""ENERGY-ELECTRICAL angle for GPI.
Routing x_{e,P}>=0, sum_P x_{e,P}=1 per bad edge e. Load T_x(v)=sum_{e,P:v in P} h_e x_{e,P}.
FACT: sum_v T_x(v) = sum_e h_e^2 = Gamma (every shortest geo of e has exactly h_e vertices).
So min_x sum_v T_x(v)^2 >= Gamma^2/N (Cauchy-Schwarz), equality iff T_x balanced (=Gamma/N everywhere).
GPI L-inf form wants: exists x with max_v T_x(v) <= K := N+(N^2-Gamma).
"""
import numpy as np
from scipy.optimize import linprog, minimize
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos, mycielskian

def build(N, adj, side, M):
    paths = []; pe = []; he = []; edge_paths = []
    for ei, (u, v) in enumerate(M):
        geos = all_shortest_geos(N, adj, side, u, v)
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

def make_eq(a):
    return {'type': 'eq', 'fun': (lambda x, a=a: a @ x - 1.0), 'jac': (lambda x, a=a: a)}

def energy_star(N, A, edge_paths, nM):
    nv = A.shape[1]; Q = A.T @ A
    f = lambda x: float(x @ Q @ x)
    g = lambda x: 2 * Q @ x
    cons = []
    for idxs in edge_paths:
        a = np.zeros(nv); a[idxs] = 1.0; cons.append(make_eq(a))
    x0 = np.zeros(nv)
    for idxs in edge_paths:
        x0[idxs] = 1.0 / len(idxs)
    res = minimize(f, x0, jac=g, constraints=cons, bounds=[(0, None)] * nv,
                   method='SLSQP', options={'maxiter': 1000, 'ftol': 1e-14})
    x = res.x; T = A @ x
    return res.fun, T, x

def run(name, N, adj, side, M, G):
    paths, pe, he, edge_paths, A = build(N, adj, side, M)
    nM = len(M)
    tau = tau_star(N, A, edge_paths, nM)
    E, Tenergy, x = energy_star(N, A, edge_paths, nM)
    K = N + (N * N - G); Gamma = G; floor = Gamma * Gamma / N; maxE = Tenergy.max()
    print(f"{name}: N={N} b={nM} G={G} def={N*N-G} K={K}")
    print(f"   tau*={tau:.4f} (<=K {tau<=K+1e-6}, ==N {abs(tau-N)<1e-6})")
    print(f"   E*={E:.3f}  floor=G^2/N={floor:.3f}  excess E*-floor={E-floor:.4f}")
    print(f"   sqrt(E*)={np.sqrt(E):.4f} <=K? {np.sqrt(E)<=K+1e-6}   energy-routing maxload={maxE:.4f} <=K? {maxE<=K+1e-6}")
    if N * N - G > 0:
        print(f"   excess/(N^2-G)={(E-floor)/(N*N-G):.5f}")
    return dict(N=N, G=G, tau=tau, E=E, floor=floor, K=K, maxE=maxE)

def C5q(q):
    n = 5 * q; vid = lambda i, j: i * q + j; side = [0] * n; adj = [set() for _ in range(n)]
    for i in range(5):
        for j in range(q):
            side[vid(i, j)] = (0 if i in (0, 2, 4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u = vid(i, a); v = vid((i + 1) % 5, b); adj[u].add(v); adj[v].add(u)
    M = [(vid(4, a), vid(0, b)) for a in range(q) for b in range(q)]; G = 25 * len(M)
    return n, adj, side, G, M

if __name__ == "__main__":
    for q in (2, 3, 4):
        n, adj, side, G, M = C5q(q); run(f"C5[{q}]", n, adj, side, M, G)
