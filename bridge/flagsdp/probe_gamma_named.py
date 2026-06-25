#!/usr/bin/env python3
"""Probe Gamma vs routing energy on the named tight/obstruction instances.
Report: m, Gamma, L1=sum ell, E2=sum lambda_x^2, sum lambda_x, and several candidate
aggregation inequalities, to locate the exact 2-step decomposition of Gamma<=N^2."""
from collections import deque
import verify_bridge_QFC25 as vb


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


def analyze(N, A, label):
    adj = adjset(N, A)
    E = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for (u, v) in E if side[u] == side[v]]
    adjB = [set() for _ in range(N)]
    for (u, v) in E:
        if side[u] != side[v]:
            adjB[u].add(v)
            adjB[v].add(u)
    lam = [0.0] * N
    L1 = 0.0
    Gamma = 0.0
    m = len(M)
    for (u, v) in M:
        du = blayers(N, adjB, u)
        d = du[v]
        ell = d + 1
        L1 += ell
        Gamma += ell * ell
        t = geodesic_flow(N, adjB, u, v, d)
        for x in range(N):
            lam[x] += t[x]
    SL = sum(lam)
    E2 = sum(l * l for l in lam)
    # candidate inequalities
    print("%-12s N=%2d m=%2d Gamma=%6.1f L1=%5.1f sumLam=%6.2f E2=%7.2f | "
          "Gamma/N^2=%.3f  Gamma<=N*E2:%s (%.3f)  E2<=L1*max_t? "
          "SL^2/N=%.2f<=E2?%s  L1^2<=m*Gamma:%s"
          % (label, N, m, Gamma, L1, SL, E2,
             Gamma / (N * N),
             Gamma <= N * E2 + 1e-9, Gamma / (N * E2) if E2 > 0 else 0,
             SL * SL / N, SL * SL / N <= E2 + 1e-9,
             L1 * L1 <= m * Gamma + 1e-9), flush=True)


if __name__ == "__main__":
    named = [(*vb.petersen(), "Petersen"), (*vb.gpt_k23(), "K23-N13"),
             (*vb.c5paths20(), "C5paths-N20"), (*vb.c5n(1), "C5[1]"),
             (*vb.c5n(2), "C5[2]"), (*vb.c5n(3), "C5[3]"), (*vb.c5n(4), "C5[4]")]
    for (N, A, lab) in named:
        analyze(N, A, lab)
    print("DONE", flush=True)
