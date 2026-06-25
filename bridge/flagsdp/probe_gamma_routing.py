#!/usr/bin/env python3
"""
Strategy-6 probe: relate Gamma = sum_M ell^2 to a single routing energy.
Route each bad edge over ALL its B-geodesics uniformly; t_uv(x)=fraction through x;
sum_x t_uv(x)=ell. lambda_x = sum_uv t_uv(x). Test candidate aggregation inequalities.
"""
import sys
from collections import deque
import flag_engine as fe


def adjset(n, A):
    return [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]


def maxcut(n, adj):
    best = -1
    bs = None
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        c = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c
            bs = side
    return best, bs


def blayers(n, adjB, src):
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adjB[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def geodesic_flow(n, adjB, u, v, d):
    du = blayers(n, adjB, u)
    dv = blayers(n, adjB, v)
    if du[v] != d:
        return None
    nu = [0] * n
    nu[u] = 1
    for x in sorted(range(n), key=lambda x: du[x] if du[x] >= 0 else 10 ** 9):
        if du[x] < 0 or x == u:
            continue
        nu[x] = sum(nu[w] for w in adjB[x] if du[w] == du[x] - 1)
    nv = [0] * n
    nv[v] = 1
    for x in sorted(range(n), key=lambda x: dv[x] if dv[x] >= 0 else 10 ** 9):
        if dv[x] < 0 or x == v:
            continue
        nv[x] = sum(nv[w] for w in adjB[x] if dv[w] == dv[x] - 1)
    total = nu[v]
    if total == 0:
        return None
    t = [0.0] * n
    for x in range(n):
        if du[x] >= 0 and dv[x] >= 0 and du[x] + dv[x] == d:
            t[x] = nu[x] * nv[x] / total
    return t


def run(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    wG = 0.0
    wR = 0.0
    viol = 0
    for (n, A) in states:
        adj = adjset(n, A)
        E = [(u, v) for u in range(n) for v in adj[u] if v > u]
        if not E:
            continue
        mc, side = maxcut(n, adj)
        M = [(u, v) for (u, v) in E if side[u] == side[v]]
        if not M:
            continue
        adjB = [set() for _ in range(n)]
        for (u, v) in E:
            if side[u] != side[v]:
                adjB[u].add(v)
                adjB[v].add(u)
        lam = [0.0] * n
        Gamma = 0.0
        ok = True
        for (u, v) in M:
            du = blayers(n, adjB, u)
            d = du[v]
            if d < 4 or d % 2:
                ok = False
                continue
            ell = d + 1
            Gamma += ell * ell
            t = geodesic_flow(n, adjB, u, v, d)
            if t is None:
                ok = False
                continue
            for x in range(n):
                lam[x] += t[x]
        E2 = sum(l * l for l in lam)
        if Gamma > N * N + 1e-9:
            viol += 1
        wG = max(wG, Gamma / (N * N))
        if E2 > 1e-12:
            wR = max(wR, Gamma / (N * E2))
    print("N=%d graphs=%d maxGamma/N^2=%.4f viol=%d worst Gamma/(N*E2)=%.4f"
          % (N, len(states), wG, viol, wR), flush=True)


if __name__ == "__main__":
    for N in [int(x) for x in sys.argv[1:]] or [5, 6, 7, 8, 9]:
        run(N)
    print("DONE", flush=True)
