#!/usr/bin/env python3
"""GPT BREAKTHROUGH (optimal-cut geodesic cosystole) -- FALSIFIABLE numerical test.
For triangle-free G, take a MAXIMUM cut (X,Y). B = cut edges (bipartite good graph), M = monochromatic
(bad) edges, beta = |M|. STRUCTURAL CLAIM: every bad edge uv has d_B(u,v) even and >= 4 (so ell=d_B+1
in {5,7,...}). INVARIANT CLAIM (GC): Gamma = sum_{uv in M} ell(uv)^2 <= N^2  (=> beta <= N^2/25 since
ell^2 >= 25). Test over ALL triangle-free graphs; if the first max cut fails the structural/invariant
claim, retry over ALL max cuts (GPT says 'for SOME maximum cut'). Report worst Gamma/N^2 and any violation.
"""
import sys
from collections import deque
import flag_engine as fe

def all_maxcuts(n, adj):
    best = -1; cuts = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        c = sum(1 for u in range(n) for v in range(u + 1, n) if adj[u][v] and side[u] != side[v])
        if c > best:
            best = c; cuts = [side]
        elif c == best:
            cuts.append(side)
    return best, cuts

def bdist(n, adj, side, src):
    dist = [-1] * n; dist[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for v in range(n):
            if adj[u][v] and side[u] != side[v] and dist[v] < 0:
                dist[v] = dist[u] + 1; q.append(v)
    return dist

def gamma_for_cut(n, adj, side):
    M = [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u][v] and side[u] == side[v]]
    G = 0; struct_ok = True
    cache = {}
    for (u, v) in M:
        if u not in cache:
            cache[u] = bdist(n, adj, side, u)
        d = cache[u][v]
        if d < 0 or d % 2 != 0 or d < 4:
            struct_ok = False
            ell = (d + 1) if d >= 4 and d % 2 == 0 else 999
        else:
            ell = d + 1
        G += ell * ell
    return len(M), G, struct_ok

def run(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    worst_ratio = 0.0; worst = None; viol = 0; structfail = 0; checked = 0
    for (n, A) in states:
        adj = [[(A[u] >> v) & 1 for v in range(n)] for u in range(n)]
        e = sum(1 for u in range(n) for v in range(u + 1, n) if adj[u][v])
        if e == 0:
            continue
        checked += 1
        mc, cuts = all_maxcuts(n, adj)
        beta = e - mc
        # try max cuts; keep the one with SMALLEST Gamma (GPT: 'for some maximum cut')
        bestG = None; bestStruct = False
        for side in cuts:
            m, G, ok = gamma_for_cut(n, adj, side)
            if bestG is None or G < bestG:
                bestG = G; bestStruct = ok
        ratio = bestG / (n * n)
        if not bestStruct:
            structfail += 1
        if bestG > n * n:
            viol += 1
        if ratio > worst_ratio:
            worst_ratio = ratio; worst = (n, beta, bestG)
    print(f"N={N}: {checked} nonempty tri-free graphs. max Gamma/N^2 (best maxcut) = {worst_ratio:.5f} "
          f"(worst: beta={worst[1]} Gamma={worst[2]} N={worst[0]}); Gamma>N^2 VIOLATIONS: {viol}; "
          f"struct-claim fails (all maxcuts): {structfail}", flush=True)
    return worst_ratio, viol, structfail

if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or [5, 6, 7, 8, 9]
    res = {}
    for N in Ns:
        res[N] = run(N)
    print("SUMMARY (maxGamma/N^2, Gamma>N^2 viols, struct-fails):", res, flush=True)
    print("DONE", flush=True)
