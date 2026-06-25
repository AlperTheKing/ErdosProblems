"""Probe the Gamma proof structure: for the min-Gamma signature S (B=K-S bipartite), build geodesic
certificate cycles C_e (shortest B-path u..v plus edge e) and test the Cauchy/cycle-degree chain that
the odd-K5-free proof uses, but applied to GEODESIC cycles only. Goal: see whether Gamma<=N^2 follows
from cycle-degree ineq (6) + a vertex-load Cauchy bound, WITHOUT Guenin."""
import numpy as np
from collections import deque
import verify_D25_lemma16 as L


def dB_dist(N, adjB, s):
    d = [-1]*N; d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for v in adjB[u]:
            if d[v] < 0:
                d[v] = d[u]+1; q.append(v)
    return d


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
        g = 0; ds = {}; ok = True
        for e in S:
            u, v = tuple(e); dd = dB_dist(N, adjB, u)
            if dd[v] < 0:
                ok = False; break
            ds[e] = dd[v]; g += (dd[v]+1)**2
        if ok and (best is None or g < best[0]):
            best = (g, S, Bset, ds)
    g, S, Bset, ds = best
    deg = [len(adj[u]) for u in range(N)]
    adjB = [[] for _ in range(N)]
    for e in Bset:
        a, b = tuple(e); adjB[a].append(b); adjB[b].append(a)
    lam = np.zeros(N); ells = []
    for e in S:
        u, v = tuple(e)
        par = [-1]*N; dd = [-1]*N; dd[u] = 0; q = deque([u])
        while q:
            x = q.popleft()
            for y in adjB[x]:
                if dd[y] < 0:
                    dd[y] = dd[x]+1; par[y] = x; q.append(y)
        path = [v]
        while path[-1] != u:
            path.append(par[path[-1]])
        ell = ds[e]+1; ells.append(ell)
        for w in set(path):
            lam[w] += 1
    ells = np.array(ells); sum_ell = ells.sum(); sum_ell2 = (ells**2).sum()
    supp = int((lam > 0).sum())
    print(f"{label}: N={N} tau={tau} Gamma={g} N^2={N*N} ratio={g/(N*N):.3f}")
    print(f"   ells={sorted(ells.tolist())} sum_ell={sum_ell} Gamma={sum_ell2}")
    print(f"   sum lam={lam.sum():.0f} sum lam^2={(lam**2).sum():.1f} support={supp}/{N}")
    print(f"   sum deg*lam={(np.array(deg)*lam).sum():.1f}  N*sum(ell-1)/2={N*(sum_ell-len(ells))/2:.1f}")


for b, lab in [(L.c5(), 'C5'), (L.c5n(2), 'C5[2]'), (L.petersen(), 'Petersen'),
               (L.gpt_k23(), 'K23-N13'), (L.c5n(3), 'C5[3]')]:
    analyze(*b, lab)
