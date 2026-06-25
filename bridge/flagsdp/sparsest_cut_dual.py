"""The spread-geodesic congestion rho_B (for fixed best signature S, B=K-S) has a concurrent-flow /
sparsest-cut dual. rho_B = max-concurrent-congestion of routing each bad-edge demand over B-geodesics.
By LP duality (single-commodity-per-pair geodesic routing), the bottleneck is a B-edge cut.

We compute the EXACT congestion LP dual (min-congestion multiflow restricted to geodesics) and read the
tight dual: a B-edge length function ell with rho_B = (sum_e d^B_ell(e)) / (sum_b ell_b) (the metric form).
Then we test whether the tight ell is the INDICATOR of a CUT (coherent layer prefix) -- which would connect
to the PROVED coherent-P5 block lemma and (Sep).

Specifically: is rho_B = max over B-edge subsets F of (sum_e [geodesic of e must use an F-edge]) / |F| ...
no. The clean dual for max-concurrent-flow over fixed geodesic sets is a fractional edge length. Compute it.
"""
import numpy as np
from collections import deque, defaultdict
from scipy.optimize import linprog
import verify_D25_lemma16 as L


def geodesic_edges(N, adjB, u, v):
    """return list of geodesics as edge-frozensets (all shortest paths)."""
    d = [-1]*N; d[u] = 0; q = deque([u])
    while q:
        x = q.popleft()
        for y in adjB[x]:
            if d[y] < 0:
                d[y] = d[x]+1; q.append(y)
    if d[v] < 0:
        return None, None
    # enumerate all shortest paths via DAG DFS
    paths = []
    def dfs(x, acc):
        if x == v:
            paths.append(list(acc)); return
        for y in adjB[x]:
            if d[y] == d[x]+1:
                acc.append(frozenset((x, y))); dfs(y, acc); acc.pop()
    dfs(u, [])
    return paths, d[v]


def cong_lp(N, A, S, edges):
    """min-congestion: each bad edge e routes 1 unit split over its geodesic-paths; minimize max B-edge load.
    Returns rho_B and the dual edge length ell (tight cut)."""
    Bset = set(edges)-set(S)
    Blist = list(Bset)
    bidx = {b: i for i, b in enumerate(Blist)}
    adjB = [[] for _ in range(N)]
    for b in Bset:
        a, c = tuple(b); adjB[a].append(c); adjB[c].append(a)
    # variables: for each bad edge e, a weight per geodesic-path; plus rho.
    pathvars = []  # (e_index, path_edges)
    for ei, e in enumerate(S):
        u, v = tuple(e)
        paths, dd = geodesic_edges(N, adjB, u, v)
        if not paths:
            return None
        for P in paths:
            pathvars.append((ei, P))
    npv = len(pathvars); nE = len(S); RHO = npv; nvar = npv+1
    c = np.zeros(nvar); c[RHO] = 1.0
    # sum of path weights per bad edge = 1
    A_eq = []; b_eq = []
    for ei in range(nE):
        row = np.zeros(nvar)
        for j, (e2, P) in enumerate(pathvars):
            if e2 == ei:
                row[j] = 1.0
        A_eq.append(row); b_eq.append(1.0)
    # per B-edge load <= rho
    A_ub = []; b_ub = []; edgemap = []
    for b in Blist:
        row = np.zeros(nvar)
        for j, (e2, P) in enumerate(pathvars):
            if b in P:
                row[j] += 1.0
        row[RHO] = -1.0
        A_ub.append(row); b_ub.append(0.0); edgemap.append(b)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*npv+[(0, None)], method="highs")
    if not res.success:
        return None
    rho = res.fun
    ell = -res.ineqlin.marginals  # dual on edge constraints = edge lengths
    return rho, {edgemap[i]: max(0.0, ell[i]) for i in range(len(edgemap))}, Blist


def best_sig_cong(N, A):
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges)-mc
    sigs = L.min_signatures(N, adj, edges, tau)
    best = None
    for S in sigs:
        r = cong_lp(N, A, S, edges)
        if r is None:
            continue
        rho, ell, Blist = r
        if best is None or rho < best[0]:
            best = (rho, ell, Blist, S)
    return best, tau, edges


def analyze(builder, lab):
    N, A = builder
    best, tau, edges = best_sig_cong(N, A)
    if best is None:
        print(f"{lab}: skip"); return
    rho, ell, Blist, S = best
    # is ell (scaled) a 0/1 indicator of a cut?
    vals = sorted(set(round(v, 4) for v in ell.values() if v > 1e-6))
    nz = [(tuple(sorted(b)), round(v, 4)) for b, v in ell.items() if v > 1e-6]
    print(f"\n{lab}: n={N} t={tau} rho_B={rho:.4f} n^2/25t={N*N/(25*tau):.4f}")
    print(f"   tight dual ell: support={len(nz)} B-edges, distinct vals={vals}")
    print(f"   01-cut-like (single value)={len(vals)==1}")


for b, lab in [(L.gpt_k23(), 'K23-N13'), (L.petersen(), 'Petersen'), (L.c5n(2), 'C5[2]'),
               (L.c5(), 'C5')]:
    analyze(b, lab)
