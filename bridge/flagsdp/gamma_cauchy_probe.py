"""Test the precise Cauchy chain for Gamma=sum ell_e^2 <= N^2.

For min signature S, B=K-S bipartite. Each e=uv in S: ell_e=d_B(u,v)+1. The shortest certificate cycle
C_e (geodesic B-path + e) has length ell_e. We want a vertex-load argument.

KEY: instead of all-weight-1, weight cycle C_e by w_e and define lam_v = sum_{e: v in C_e} w_e.
Then sum_v lam_v = sum_e w_e ell_e, and sum_v deg(v) lam_v = sum_e w_e (sum_{v in C_e} deg v)
                                                          <= sum_e w_e * N(ell_e-1)/2  [cycle-degree (6)].
Cauchy with weights: (sum_e w_e ell_e)^2 = (sum_v lam_v)^2 <= |supp| sum_v lam_v^2  -- but supp<=N.
We also have 2 lam_v <= deg(v) IF the cycles through v are EDGE-DISJOINT at v (congestion 1).
Geodesic certs are NOT edge-disjoint, so test the CONGESTION:
  cong(b) = #certificate cycles using B-edge b (or weighted). If we can bound congestion, normalize.

Test 1: what is the max B-edge congestion of the geodesic certificate cycles (all weight 1)?
Test 2: does dividing weights by congestion give a feasible packing of value >= 25 tau^2/N^2?
Test 3 (the real one): the odd-K5-free Cauchy uses 2 lam_v <= deg(v) from congestion-1 packing.
  For Gamma we want a DIFFERENT route. Test whether:
     sum_e ell_e^2 <= N * sum_e ell_e  ... NO (would give Gamma<=N*sum_ell).
  Better: per the equal-length analysis, Gamma=sum ell^2, and we want <= N^2.
  Try: is sum_e ell_e (= sum_v lam_v) and (sum_e ell_e)^2 <= N sum_v lam_v^2,
       with sum_v lam_v^2 <= (1/2) sum_v deg(v) lam_v / (min congestion factor)?
"""
import numpy as np
from collections import deque
import verify_D25_lemma16 as L


def bfs_tree(N, adjB, s):
    par = [-1]*N; dd = [-1]*N; dd[s] = 0; q = deque([s])
    while q:
        x = q.popleft()
        for y in adjB[x]:
            if dd[y] < 0:
                dd[y] = dd[x]+1; par[y] = x; q.append(y)
    return par, dd


def analyze(N, A, label):
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges)-mc
    if tau == 0:
        print(f"{label}: bipartite"); return
    sigs = L.min_signatures(N, adj, edges, tau)
    best = None
    for S in sigs:
        Bset = set(edges)-set(S)
        adjB = [[] for _ in range(N)]
        for e in Bset:
            a, b = tuple(e); adjB[a].append(b); adjB[b].append(a)
        g = 0; ok = True
        for e in S:
            u, v = tuple(e); _, dd = bfs_tree(N, adjB, u)
            if dd[v] < 0:
                ok = False; break
            g += (dd[v]+1)**2
        if ok and (best is None or g < best[0]):
            best = (g, S, Bset)
    g, S, Bset = best
    deg = np.array([len(adj[u]) for u in range(N)])
    adjB = [[] for _ in range(N)]
    for e in Bset:
        a, b = tuple(e); adjB[a].append(b); adjB[b].append(a)
    # build geodesic certificate cycles
    cycs = []  # list of (vertex set, edge list incl bad edge, ell)
    for e in S:
        u, v = tuple(e)
        par, dd = bfs_tree(N, adjB, u)
        path = [v]
        while path[-1] != u:
            path.append(par[path[-1]])
        ell = dd[v]+1
        bedges = [frozenset((path[i], path[i+1])) for i in range(len(path)-1)]
        cycs.append((set(path), bedges, ell, e))
    # B-edge congestion
    cong = {}
    for (vs, be, ell, e) in cycs:
        for b in be:
            cong[b] = cong.get(b, 0)+1
    maxcong = max(cong.values()) if cong else 0
    # vertex load with weight 1
    lam = np.zeros(N)
    for (vs, be, ell, e) in cycs:
        for w in vs:
            lam[w] += 1
    sum_ell = sum(c[2] for c in cycs)
    Gamma = sum(c[2]**2 for c in cycs)
    # The congestion-normalized packing: y_e = 1/maxcong gives feasible? value = tau/maxcong
    print(f"{label}: N={N} tau={tau} Gamma={Gamma} N^2={N*N}  maxBcong={maxcong}")
    print(f"   value tau/maxcong={tau/maxcong:.3f}  need 25tau^2/N^2={25*tau*tau/(N*N):.3f}  "
          f"-> packing OK: {tau/maxcong >= 25*tau*tau/(N*N)-1e-9}")
    # Cauchy chain test for Gamma directly:
    # (sum lam)^2 <= N * sum lam^2 ; and sum lam = sum ell
    s1 = lam.sum(); s2 = (lam**2).sum()
    print(f"   sum_ell={sum_ell} (sum lam={s1:.0f}) sum lam^2={s2:.1f}  (sum_ell)^2/N={s1*s1/N:.1f} <= sum lam^2? {s1*s1/N <= s2+1e-9}")


for b, lab in [(L.c5(), 'C5'), (L.c5n(2), 'C5[2]'), (L.petersen(), 'Petersen'),
               (L.gpt_k23(), 'K23-N13'), (L.c5n(3), 'C5[3]')]:
    analyze(*b, lab)
