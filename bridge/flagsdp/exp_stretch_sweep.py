#!/usr/bin/env python3
"""EXHAUSTIVE no-stretch sweep: is "optimal dual metric ell* never stretches an M-geodesic beyond d_B"
UNIVERSAL over triangle-free max-cut instances? If yes, MT25 reduces to a pure congestion bound over
unit d_B-geodesics (no metrics). Tests all tri-free N<=9 + an obstruction battery.
"""
import itertools, heapq, sys
import numpy as np
from collections import deque, defaultdict
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]
def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N-1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best: best = c; bs = side
    return best, bs
def bdist(N, adjB, s):
    d = [-1]*N; d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for v in adjB[u]:
            if d[v] < 0: d[v] = d[u]+1; q.append(v)
    return d
def simple_paths(adjB, s, t, maxlen):
    out = []
    def dfs(u, path, ps):
        if u == t and len(path) > 1: out.append(list(path)); return
        if len(path)-1 >= maxlen: return
        for w in adjB[u]:
            if w not in ps: ps.add(w); path.append(w); dfs(w, path, ps); path.pop(); ps.discard(w)
    dfs(s, [s], {s}); return out

def stretch_count(N, A):
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    Bedges = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    if not M or not Bedges: return 0, 0, 0.0
    adjB = [set() for _ in range(N)]
    for (u, v) in Bedges: adjB[u].add(v); adjB[v].add(u)
    bidx = {e: i for i, e in enumerate(Bedges)}; nB = len(Bedges)
    dB = {}
    for (u, v) in M:
        d = bdist(N, adjB, u); dB[(u, v)] = d[v]
    if any(dB[e] < 0 for e in M): return -1, 0, 0.0   # disconnected (shouldn't happen for min sig)
    maxlen = max(dB.values()) + 4
    m = len(M); nvar = nB + m
    c = np.zeros(nvar); c[nB:] = -1.0
    A_ub = []; b_ub = []
    for k, e in enumerate(M):
        for p in simple_paths(adjB, e[0], e[1], maxlen):
            P = [tuple(sorted((p[i], p[i+1]))) for i in range(len(p)-1)]
            row = np.zeros(nvar); row[nB+k] = 1.0
            for b in P: row[bidx[b]] -= 1.0
            A_ub.append(row); b_ub.append(0.0)
    A_eq = [np.concatenate([np.ones(nB), np.zeros(m)])]; b_eq = [1.0]
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nvar, method="highs")
    if not res.success: return -2, 0, 0.0
    ell = res.x[:nB]; rho = -res.fun
    def ellw(b): return ell[bidx[b]]
    stretched = 0
    for (u, v) in M:
        dist = [float('inf')]*N; dist[u] = 0.0; pq = [(0.0, u)]
        while pq:
            d0, x = heapq.heappop(pq)
            if d0 > dist[x]+1e-7: continue
            for y in adjB[x]:
                w = ellw(tuple(sorted((x, y))))
                if dist[x]+w < dist[y]-1e-7: dist[y] = dist[x]+w; heapq.heappush(pq, (dist[y], y))
        succ = defaultdict(list)
        for (x, y) in Bedges:
            w = ellw((x, y))
            if abs(dist[x]+w-dist[y]) < 1e-6: succ[x].append(y)
            if abs(dist[y]+w-dist[x]) < 1e-6: succ[y].append(x)
        de = {u: 0}; q = deque([u])
        while q:
            x = q.popleft()
            for y in succ[x]:
                if y not in de: de[y] = de[x]+1; q.append(y)
        minedges = de.get(v, None)
        if minedges is None or minedges > dB[(u, v)]: stretched += 1
    return stretched, m, rho

def sweep_exhaustive(Ns):
    tot = 0; stretch_graphs = 0; worst = []
    for N in Ns:
        states = fe.enumerate_graphs(N, triangle_free=True); sg = 0; cnt = 0
        for (n, A) in states:
            sc, m, rho = stretch_count(n, A)
            if m == 0: continue
            cnt += 1
            if sc > 0: sg += 1; stretch_graphs += 1; worst.append((N, sc, m))
            elif sc < 0: pass
        print(f"N={N}: {cnt} maxcut instances, graphs with STRETCH={sg}", flush=True)
        tot += cnt
    print(f">>> total {tot} instances, STRETCH graphs={stretch_graphs}", flush=True)
    if worst: print("   stretch examples:", worst[:10], flush=True)
    return stretch_graphs

# obstruction battery
def grotzsch():
    E = []
    for i in range(5): E.append((i, (i+1) % 5))
    for i in range(5):
        for j in [(i+1) % 5, (i-1) % 5]: E.append((5+i, j))
        E.append((10, 5+i))
    N = 11; A = [0]*N
    for (u, v) in set(map(lambda e: tuple(sorted(e)), E)): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A
def subdivk5(sub):
    E = []; nxt = 5
    for a in range(5):
        for b in range(a+1, 5):
            prev = a
            for _ in range(sub): E.append((prev, nxt)); prev = nxt; nxt += 1
            E.append((prev, b))
    N = nxt; A = [0]*N
    for (u, v) in E: A[u] |= 1 << v; A[v] |= 1 << u
    return N, A
def mycielski_cyc(n):
    E0 = [(i, (i+1) % n) for i in range(n)]; N0 = n
    adj0 = [set() for _ in range(N0)]
    for (u, v) in E0: adj0[u].add(v); adj0[v].add(u)
    N = 2*N0+1; w = 2*N0; Es = set(map(lambda e: tuple(sorted(e)), E0))
    for i in range(N0):
        for j in adj0[i]: Es.add(tuple(sorted((N0+i, j))))
        Es.add(tuple(sorted((w, N0+i))))
    A = [0]*N
    for (u, v) in Es: A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

if __name__ == "__main__":
    print("=== EXHAUSTIVE no-stretch sweep ===", flush=True)
    sweep_exhaustive([5, 6, 7, 8, 9])
    print("--- obstruction battery ---", flush=True)
    for (N, A, lab) in [(*grotzsch(), "Grotzsch"), (*subdivk5(1), "subdivK5-1"), (*subdivk5(2), "subdivK5-2"),
                        (*subdivk5(3), "subdivK5-3"), (*mycielski_cyc(7), "Myciel-C7")]:
        sc, m, rho = stretch_count(N, A)
        print(f"{lab:12s} N={N} m={m} rho={rho:.3f} STRETCHED={sc}", flush=True)
    print("DONE", flush=True)
