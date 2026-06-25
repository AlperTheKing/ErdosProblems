#!/usr/bin/env python3
"""DECISIVE TEST for GPT's signed-graph proof (chat 6a3b5aba).

GPT's odd-K5-free theorem proves |M| <= N^2/25 whenever the max-fractional-odd-cycle-packing value
nu*(G) EQUALS the min cover tau(G) = |M| (= weakly bipartite = no odd-K5 minor). The remaining
"bridge" is only needed when nu* < tau.

QUESTION: in OUR setting (M = monochromatic edges of a MAXIMUM cut of a triangle-free G), is nu* = tau
ALWAYS?  If yes, the odd-K5-free theorem alone proves the whole conjecture (no bridge needed).
If no, the witnesses where nu* < tau are the genuine odd-K5 obstruction instances; check the bound
|M| <= N^2/25 still holds there.

nu*(G) = max sum_C y_C  s.t.  sum_{C ni e} y_C <= 1 for every edge e,  y_C >= 0,  C over ALL odd cycles.
tau(G) = |M| = e - MaxCut  (min odd-cycle edge transversal).
"""
import itertools
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N, A):
    return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def all_odd_cycles(N, adj, maxlen=None):
    """All odd cycles as edge-frozensets (dedup)."""
    if maxlen is None:
        maxlen = N
    seen = set(); out = []
    def dfs(start, u, path, pathset):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                edges = frozenset(frozenset((path[i], path[(i + 1) % len(path)])) for i in range(len(path)))
                if edges not in seen:
                    seen.add(edges); out.append(edges)
            elif w not in pathset and w > start and len(path) < maxlen:
                path.append(w); pathset.add(w); dfs(start, w, path, pathset); path.pop(); pathset.discard(w)
    for s in range(N):
        dfs(s, s, [s], {s})
    return out

def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N - 1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c; bs = side
    return best, bs

def nu_star(N, adj, edges):
    """max fractional odd-cycle packing via LP."""
    cycles = all_odd_cycles(N, adj)
    if not cycles:
        return 0.0, 0
    eidx = {e: i for i, e in enumerate(edges)}
    nC = len(cycles); nE = len(edges)
    # max sum y  s.t.  A y <= 1 ; linprog minimizes c^T x  => c = -1
    Aub = np.zeros((nE, nC))
    for j, C in enumerate(cycles):
        for e in C:
            Aub[eidx[e], j] = 1.0
    bub = np.ones(nE)
    c = -np.ones(nC)
    res = linprog(c, A_ub=Aub, b_ub=bub, bounds=[(0, None)] * nC, method="highs")
    return -res.fun, nC

def analyze(N, A, label):
    adj = adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    tau = len(edges) - mc
    nu, nC = nu_star(N, adj, edges)
    gap = tau - nu
    bound_ok = (25 * tau <= N * N + 1e-9)
    flag = "" if gap < 1e-6 else "  <<< nu* < tau : GENUINE ODD-K5 OBSTRUCTION"
    print(f"{label:22s} N={N:2d} |E|={len(edges):3d} tau=|M|={tau:3d} nu*={nu:7.3f} gap={gap:6.3f} "
          f"odd_cyc={nC:4d} 25tau<=N^2:{bound_ok}{flag}", flush=True)
    return gap

def petersen():
    # Kneser(5,2)
    verts = list(itertools.combinations(range(5), 2)); idx = {v: i for i, v in enumerate(verts)}
    A = [0] * 10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b):
                A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A

def c5_paths_n20():
    """The audited 'global-layering counterexample': M=C5 on x_0..x_4 + B-paths x_i-y_i-z_i-w_i-x_{i+1}."""
    # x_i = i (0..4); y_i=5+i, z_i=10+i, w_i=15+i
    N = 20; A = [0] * N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    x = lambda i: i % 5; y = lambda i: 5 + (i % 5); z = lambda i: 10 + (i % 5); w = lambda i: 15 + (i % 5)
    for i in range(5):
        add(x(i), x(i + 1))                       # bad edges = C5
        add(x(i), y(i)); add(y(i), z(i)); add(z(i), w(i)); add(w(i), x(i + 1))  # B-path
    return N, A

if __name__ == "__main__":
    print("=== nu*(odd-cycle packing) vs tau=|M| for max-cut of triangle-free G ===", flush=True)
    genuine = 0; tot = 0
    for N in [5, 6, 7, 8, 9]:
        states = fe.enumerate_graphs(N, triangle_free=True)
        worst = 0.0; ng = 0
        for (n, Ai) in states:
            adj = adjset(n, Ai); edges = [frozenset((u, v)) for u in range(n) for v in adj[u] if v > u]
            if not edges:
                continue
            mc, side = maxcut(n, adj); tau = len(edges) - mc
            if tau == 0:
                continue
            nu, _ = nu_star(n, adj, edges); g = tau - nu
            tot += 1
            if g > 1e-6:
                ng += 1; genuine += 1; worst = max(worst, g)
        print(f"N={N}: {len(states)} graphs, nu*<tau (genuine obstruction) in {ng}; worst gap={worst:.3f}", flush=True)
    print("--- named witnesses ---", flush=True)
    analyze(*petersen(), "Petersen")
    analyze(*c5_paths_n20(), "C5+Bpaths(N=20)")
    print(f"\nSUMMARY: genuine odd-K5 obstruction (nu*<tau) in {genuine}/{tot} triangle-free max-cut instances N<=9", flush=True)
    print("If genuine==0 => odd-K5-free theorem alone proves the bound for all N<=9 (no bridge needed there).", flush=True)
    print("DONE", flush=True)
