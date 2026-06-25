#!/usr/bin/env python3
"""Referee: check the colleague's KEY sub-lemma 2*lambda_v <= deg(v) for the UNIFORM
geodesic flow, and also examine the claimed (E1) and the 'self-improving' Cauchy chain.
We use the same uniform geodesic-flow construction as probe_gamma_named.py."""
import sys
sys.path.insert(0, '.')
import verify_bridge_QFC25 as vb
from collections import deque


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


def geoflow(n, adjB, u, v, d):
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


def check(N, A, label):
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
    for (u, v) in M:
        du = blayers(N, adjB, u)
        d = du[v]
        ell = d + 1
        L1 += ell
        Gamma += ell * ell
        t = geoflow(N, adjB, u, v, d)
        for x in range(N):
            lam[x] += t[x]
    deg = [len(adj[u]) for u in range(N)]
    SL = sum(lam)
    E2 = sum(l * l for l in lam)
    # sub-lemma 2*lam_v <= deg_v
    viol = [(v, 2 * lam[v], deg[v]) for v in range(N) if 2 * lam[v] > deg[v] + 1e-9]
    maxratio = max((2 * lam[v] / deg[v] if deg[v] > 0 else 0) for v in range(N))
    # the claimed (E1): sum lam^2 <= (N/4)*L1
    E1_rhs = (N / 4.0) * L1
    # 'self-improving' closed form: under congestion-1 and cycle-degree, claim sum lam^2 <= N^2/25
    target_E2 = N * N / 25.0
    # the chain claim: Gamma <= N*E2 ; and final Gamma <= n^2
    print(f"{label:12s} N={N} m={len(M)} Gamma={Gamma:.1f} L1={L1:.1f} E2={E2:.2f} "
          f"SL={SL:.2f}")
    print(f"    sub-lemma 2lam<=deg: viol={len(viol)} max(2lam/deg)={maxratio:.3f}")
    print(f"    (E1) E2<= (N/4)L1={E1_rhs:.2f} ? {E2 <= E1_rhs + 1e-9}  (E2/E1rhs={E2/E1_rhs:.3f})")
    print(f"    E2 <= N^2/25={target_E2:.2f} ? {E2 <= target_E2 + 1e-9}  (E2/(N^2/25)={E2/target_E2:.3f})")
    print(f"    Gamma <= N*E2={N*E2:.1f} ? {Gamma <= N*E2 + 1e-9}; Gamma<=N^2={N*N}? {Gamma<=N*N+1e-9}")
    # The 'self-improving' algebra the colleague writes: from (E1) E2<=(N/4)L1 and
    # (E2) Gamma<=N*E2, plus L1<=Gamma/5, we get Gamma<=N*(N/4)*(Gamma/5)=N^2 Gamma/20.
    # That gives 1<=N^2/20, VACUOUS. Show it:
    chain = N * (N / 4.0) * (Gamma / 5.0)
    print(f"    'self-improving' RHS N*(N/4)*(Gamma/5)={chain:.1f} vs Gamma={Gamma:.1f}  "
          f"=> bound is Gamma<=({N*N/20.0:.2f})*Gamma  [VACUOUS if coeff>=1: {N*N/20.0>=1}]")
    for v, a, b in viol:
        print(f"      VERTEX {v}: 2lam={a:.3f} > deg={b}")
    print()


if __name__ == "__main__":
    named = [(*vb.petersen(), "Petersen"), (*vb.gpt_k23(), "K23-N13"),
             (*vb.c5paths20(), "C5paths20"), (*vb.c5n(1), "C5[1]"),
             (*vb.c5n(2), "C5[2]"), (*vb.c5n(3), "C5[3]"), (*vb.c5n(4), "C5[4]")]
    for (N, A, lab) in named:
        check(N, A, lab)
    print("DONE")
