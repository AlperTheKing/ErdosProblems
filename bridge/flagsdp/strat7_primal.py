#!/usr/bin/env python3
"""STRATEGY 7 PRIMAL CERTIFICATE: explicit routing => congestion bound.

Instead of the dual metric, exhibit an explicit fractional routing f (a PRIMAL certificate for QFC25)
whose max B-edge load <= max{1, N^2/(25m)}.  This is Lean-checkable (just verify load on each edge).

Candidate routings to test:
 (R1) each bad edge routed UNIFORMLY over all its shortest (length-4, i.e. d_B(u,v)=4) B-geodesics.
 (R2) the LP-optimal routing (gives rho exactly; the certificate is its load vector).
 (R3) electrical/uniform-over-all-simple-paths.

We measure max load for each and compare with the density bound.  Crucially, the PRIMAL certificate is
what closes Step 2: it directly yields the odd-cycle packing nu* >= m/kappa with kappa = max load.
"""
import itertools, math, heapq
import numpy as np
from collections import deque
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N, A):
    return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N-1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c; bs = side
    return best, bs

def bfs_dist(N, adjB, s):
    D = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for v in adjB[u]:
            if v not in D:
                D[v] = D[u] + 1; q.append(v)
    return D

def count_geodesics(N, adjB, s, t):
    """Number of shortest s-t paths and the per-edge flow if 1 unit routed uniformly over geodesics."""
    Ds = bfs_dist(N, adjB, s)
    if t not in Ds:
        return None
    L = Ds[t]
    # count paths via DAG DP from s; cnt[v] = #shortest s->v
    cnt = {s: 1}
    order = sorted(Ds.keys(), key=lambda v: Ds[v])
    for v in order:
        if v == s:
            continue
        c = 0
        for u in adjB[v]:
            if Ds.get(u, 1e9) == Ds[v] - 1:
                c += cnt.get(u, 0)
        cnt[v] = c
    total = cnt[t]
    # edge flow: for edge (u,v) on a geodesic (Ds[v]=Ds[u]+1), flow = cnt[u]*cntT[v]/total
    Dt = bfs_dist(N, adjB, t)
    cntT = {t: 1}
    orderT = sorted(Dt.keys(), key=lambda v: Dt[v])
    for v in orderT:
        if v == t:
            continue
        c = 0
        for u in adjB[v]:
            if Dt.get(u, 1e9) == Dt[v] - 1:
                c += cntT.get(u, 0)
        cntT[v] = c
    eflow = {}
    for u in Ds:
        for v in adjB[u]:
            if Ds.get(v, 1e9) == Ds[u] + 1 and Dt.get(v, 1e9) == Dt[u] - 1:
                # edge u->v lies on a geodesic
                f = cnt.get(u, 0) * cntT.get(v, 0) / total
                e = tuple(sorted((u, v)))
                eflow[e] = eflow.get(e, 0.0) + f
    return L, total, eflow

def routing_geodesic_load(N, adj, side):
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    Bset = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    m = len(M)
    if m == 0:
        return None
    adjB = [set() for _ in range(N)]
    for (u, v) in Bset:
        adjB[u].add(v); adjB[v].add(u)
    load = {e: 0.0 for e in Bset}
    for (s, t) in M:
        g = count_geodesics(N, adjB, s, t)
        if g is None:
            return ("disconnected", m)
        L, total, eflow = g
        for e, f in eflow.items():
            load[e] += f
    return max(load.values()), m

def rho_lp(N, adj, side):
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    Bset = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    m = len(M)
    if m == 0:
        return None
    adjB = [set() for _ in range(N)]
    for (u, v) in Bset:
        adjB[u].add(v); adjB[v].add(u)
    def simple_paths(s, t, maxlen=12):
        out = []
        def dfs(u, path, vis):
            if u == t:
                out.append(list(path)); return
            if len(path) > maxlen:
                return
            for w in adjB[u]:
                if w not in vis:
                    vis.add(w); path.append(w); dfs(w, path, vis); path.pop(); vis.discard(w)
        dfs(s, [s], {s}); return out
    paths = [simple_paths(s, t) for (s, t) in M]
    offs = []; cur = 0
    for k, plist in enumerate(paths):
        offs.append(cur); cur += len(plist)
    nf = cur; KAP = nf; nvar = nf + 1
    def vi(k, pi):
        return offs[k] + pi
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    for k, plist in enumerate(paths):
        row = np.zeros(nvar)
        for pi in range(len(plist)):
            row[vi(k, pi)] = 1.0
        A_eq.append(row); b_eq.append(1.0)
    A_ub = []; b_ub = []
    for e in Bset:
        row = np.zeros(nvar)
        for k, plist in enumerate(paths):
            for pi, p in enumerate(plist):
                pe = set(tuple(sorted((p[i], p[i+1]))) for i in range(len(p)-1))
                if e in pe:
                    row[vi(k, pi)] += 1.0
        row[KAP] = -1.0; A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nf + [(0, None)], method="highs")
    return res.fun, m

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4):
                A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v):
        A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4):
            add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

print("=== (R1) uniform-geodesic routing load  vs  rho_LP  vs  bound ===", flush=True)
named = [("C5[1]", *c5n(1)), ("C5[2]", *c5n(2)), ("C5[3]", *c5n(3)), ("K23-N13", *gpt_k23())]
for (label, N, A) in named:
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    g = routing_geodesic_load(N, adj, side)
    r = rho_lp(N, adj, side)
    if g is None:
        print(f"  {label}: m=0"); continue
    geoload, m = g
    rho = r[0]
    bound = max(1.0, N*N/(25.0*m))
    print(f"  {label}: N={N} m={m} geodesic_load={geoload:.4f} rho_LP={rho:.4f} bound={bound:.4f} "
          f"R1_ok={geoload<=bound+1e-7}", flush=True)

print("=== exhaustive: does uniform-geodesic routing satisfy the bound? ===", flush=True)
for N in [5, 6, 7, 8, 9]:
    states = fe.enumerate_graphs(N, triangle_free=True)
    tot = 0; viol = 0; worst = 0.0; worstinst = None
    for (n, A) in states:
        adj = adjset(n, A); mc, side = maxcut(n, adj)
        g = routing_geodesic_load(n, adj, side)
        if g is None or g[0] == "disconnected":
            continue
        geoload, m = g
        tot += 1
        bound = max(1.0, n*n/(25.0*m))
        ratio = geoload/bound
        if geoload > bound + 1e-7:
            viol += 1
        if ratio > worst:
            worst = ratio; worstinst = (n, m, geoload, bound)
    print(f"  N={n}: instances={tot} R1_violations={viol} worst_ratio={worst:.4f} at {worstinst}", flush=True)
print("DONE", flush=True)
