#!/usr/bin/env python3
"""STRATEGY E probe: spectral / fractional-relaxation LOWER bound on nu*.

nu* = max fractional odd-cycle packing = tau* (LP dual = fractional odd-cycle
edge cover). We compute exact nu* via LP, compare to 25 t^2 / N^2, and test
spectral lower-bound candidates (esp. on K23-N13 signature-rotation).
"""
import itertools, math
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe


def adjset(N, A):
    return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]


def maxcut(N, adj):
    best = -1
    bs = None
    for mask in range(1 << (N - 1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c
            bs = side
    return best, bs


def all_odd_cycles(N, adj, maxlen=None):
    if maxlen is None:
        maxlen = N
    cycles = set()

    def cyc_edges(path):
        return frozenset(frozenset((path[i], path[(i + 1) % len(path)])) for i in range(len(path)))

    def dfs(start, v, visited, path):
        for w in adj[v]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                cycles.add(cyc_edges(path))
            elif w > start and w not in visited and len(path) < maxlen:
                visited.add(w)
                path.append(w)
                dfs(start, w, visited, path)
                path.pop()
                visited.discard(w)

    for s in range(N):
        dfs(s, s, {s}, [s])
    return [tuple(sorted((tuple(sorted(e)) for e in c))) for c in cycles]


def nu_star(N, adj):
    edges = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u]
    eidx = {e: i for i, e in enumerate(edges)}
    ne = len(edges)
    cyc = all_odd_cycles(N, adj)
    if not cyc:
        return 0.0, edges, []
    nc = len(cyc)
    c = -np.ones(nc)
    A_ub = np.zeros((ne, nc))
    b_ub = np.ones(ne)
    for j, C in enumerate(cyc):
        for e in C:
            ee = tuple(sorted(e))
            A_ub[eidx[ee]][j] += 1.0
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * nc, method="highs")
    return -res.fun, edges, cyc


def tau_int(N, adj):
    ne = sum(1 for u in range(N) for v in adj[u] if v > u)
    mc, _ = maxcut(N, adj)
    return ne - mc


def lambda_eigs(N, adj):
    A = np.zeros((N, N))
    for u in range(N):
        for v in adj[u]:
            A[u][v] = 1.0
    return np.linalg.eigvalsh(A)


def petersen():
    verts = list(itertools.combinations(range(5), 2))
    A = [0] * 10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b):
                A[i] |= 1 << j
                A[j] |= 1 << i
    return 10, A


def c5n(k):
    N = 5 * k
    A = [0] * N
    for u in range(N):
        for v in range(u + 1, N):
            if (u // k - v // k) % 5 in (1, 4):
                A[u] |= 1 << v
                A[v] |= 1 << u
    return N, A


def gpt_k23():
    N = 13
    A = [0] * N

    def add(u, v):
        A[u] |= 1 << v
        A[v] |= 1 << u

    for i in (0, 1):
        for j in (2, 3, 4):
            add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt + 1
        nxt += 2
        add(x, a)
        add(a, b)
        add(b, y)
    return N, A


def theta46():
    N = 1 + 1 + 3 + 5
    A = [0] * N

    def add(u, v):
        A[u] |= 1 << v
        A[v] |= 1 << u

    u, v = 0, 1
    p4 = [u, 2, 3, 4, v]
    p6 = [u, 5, 6, 7, 8, 9, v]
    for i in range(len(p4) - 1):
        add(p4[i], p4[i + 1])
    for i in range(len(p6) - 1):
        add(p6[i], p6[i + 1])
    add(u, v)
    return N, A


print("=== Strategy E: spectral/LP lower bounds on nu* ===", flush=True)
hdr = f"{'name':10s} {'N':>3s} {'t':>4s} {'nu*':>7s} {'25t^2/N^2':>10s} {'gap':>7s} {'-lam_min':>9s} {'e':>4s} {'lam1':>7s}"
print(hdr, flush=True)
named = [(*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*theta46(), "theta46"),
         (*c5n(1), "C5[1]"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]")]
for (N, A, label) in named:
    adj = adjset(N, A)
    ns, edges, cyc = nu_star(N, adj)
    t = tau_int(N, adj)
    target = 25.0 * t * t / (N * N)
    lams = lambda_eigs(N, adj)
    lmin = lams[0]
    lam1 = lams[-1]
    e = len(edges)
    gap = "OK" if ns >= target - 1e-6 else "FAIL"
    print(f"{label:10s} {N:>3d} {t:>4d} {ns:>7.3f} {target:>10.3f} {gap:>7s} {-lmin:>9.3f} {e:>4d} {lam1:>7.3f}", flush=True)
