#!/usr/bin/env python3
"""Probe: is the routing vertex-load lambda_x controlled by CD/separator so that
Gamma <= N^2 follows? Candidate chain:
  Gamma = sum_M ell^2.  With uniform-geodesic routing, for each bad edge ell=sum_x t_uv(x).
  By Cauchy on each edge:  ell^2 = (sum_x t_uv(x))^2 <= (#support) * sum_x t_uv(x)^2  -- not it.
Instead test the GLOBAL second-moment route:
  Define n_r = sum_{uv} [number of geodesic-vertices of uv at u-distance r], r=0..ell-1.
  Then sum_r (stuff). Look for an inequality  Gamma <= N * max_x lambda_x  or  Gamma <= (sum lambda)*(max lambda).
Report max_x lambda_x / (N/5), and test Gamma <= L1 * maxlam, and Gamma <= N*maxlam."""
from collections import deque
import verify_bridge_QFC25 as vb
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


def gflow(n, adjB, u, v, d):
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
    return [nu[x] * nv[x] / total if (du[x] >= 0 and dv[x] >= 0 and du[x] + dv[x] == d) else 0.0
            for x in range(n)]


def info(N, A):
    adj = adjset(N, A)
    E = [(u, v) for u in range(N) for v in adj[u] if v > u]
    if not E:
        return None
    mc, side = maxcut(N, adj)
    M = [(u, v) for (u, v) in E if side[u] == side[v]]
    if not M:
        return None
    adjB = [set() for _ in range(N)]
    for (u, v) in E:
        if side[u] != side[v]:
            adjB[u].add(v)
            adjB[v].add(u)
    lam = [0.0] * N
    Gamma = 0.0
    L1 = 0.0
    for (u, v) in M:
        du = blayers(N, adjB, u)
        d = du[v]
        if d < 4 or d % 2:
            return None
        ell = d + 1
        Gamma += ell * ell
        L1 += ell
        t = gflow(N, adjB, u, v, d)
        if t is None:
            return None
        for x in range(N):
            lam[x] += t[x]
    return len(M), Gamma, L1, max(lam), sum(lam)


def named():
    ns = [(*vb.petersen(), "Pet"), (*vb.gpt_k23(), "K23"), (*vb.c5paths20(), "C5p"),
          (*vb.c5n(2), "C5[2]"), (*vb.c5n(3), "C5[3]"), (*vb.c5n(4), "C5[4]")]
    for (N, A, lab) in ns:
        r = info(N, A)
        if r:
            m, G, L1, ML, SL = r
            print("%-6s N=%2d m=%2d Gamma=%5.0f maxlam=%5.2f N/5=%.1f maxlam/(N/5)=%.3f "
                  "Gamma<=L1*maxlam:%s(%.2f) Gamma<=N*maxlam:%s"
                  % (lab, N, m, G, ML, N / 5, ML / (N / 5),
                     G <= L1 * ML + 1e-9, G / (L1 * ML), G <= N * ML + 1e-9), flush=True)


def sweep(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    wmaxlam = 0.0
    wg1 = 0
    wg2 = 0
    for (n, A) in states:
        r = info(n, A)
        if not r:
            continue
        m, G, L1, ML, SL = r
        wmaxlam = max(wmaxlam, ML / (n / 5.0))
        if G > L1 * ML + 1e-9:
            wg1 += 1
        if G > n * ML + 1e-9:
            wg2 += 1
    print("N=%d: worst maxlam/(N/5)=%.3f  Gamma>L1*maxlam viol=%d  Gamma>N*maxlam viol=%d"
          % (N, wmaxlam, wg1, wg2), flush=True)


if __name__ == "__main__":
    named()
    for N in [5, 6, 7, 8, 9]:
        sweep(N)
    print("DONE", flush=True)
