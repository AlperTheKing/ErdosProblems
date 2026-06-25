#!/usr/bin/env python3
"""Does the UNIFORM-over-d_B-geodesics routing always satisfy the geodesic-congestion bound
   max B-edge load <= max{1, N^2/(25 m)} ?
If YES universally, this is the clean Lean-friendly construction (no LP optimization needed): split each
bad edge's unit flow equally over ALL its d_B-edge B-geodesics; bound the max load.
Exhaustive over tri-free N<=9 + obstruction battery. Exact (Fraction) arithmetic.
"""
import itertools
from collections import deque, defaultdict
from fractions import Fraction
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

def num_geodesics_through(N, adjB, s, t):
    """Return (#geodesics s->t, dict edge->#geodesics-through-edge) via DAG DP."""
    ds = bdist(N, adjB, s); dt = bdist(N, adjB, t); D = ds[t]
    if D < 0: return 0, {}
    # count paths from s to each node along DAG (ds[x]+1=ds[y]); and from each node to t
    fwd = [0]*N; fwd[s] = 1
    order = sorted(range(N), key=lambda x: ds[x])
    for x in order:
        if ds[x] < 0: continue
        for y in adjB[x]:
            if ds[x]+1 == ds[y]: fwd[y] += fwd[x]
    bwd = [0]*N; bwd[t] = 1
    for x in sorted(range(N), key=lambda x: -ds[x]):
        for y in adjB[x]:
            if ds[x]+1 == ds[y]: bwd[x] += bwd[y]
    total = fwd[t]
    edge_through = {}
    for x in range(N):
        if ds[x] < 0: continue
        for y in adjB[x]:
            # geodesic DAG arc x->y, and both endpoints on a shortest s-t path
            if ds[x]+1 == ds[y] and ds[x]+dt[x] == D and ds[y]+dt[y] == D:
                key = (min(x, y), max(x, y))
                edge_through[key] = edge_through.get(key, 0) + fwd[x]*bwd[y]
    return total, edge_through

def uniform_maxload(N, A):
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    B = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    if not M: return None
    adjB = [set() for _ in range(N)]
    for (u, v) in B: adjB[u].add(v); adjB[v].add(u)
    load = defaultdict(Fraction)
    for (u, v) in M:
        total, et = num_geodesics_through(N, adjB, u, v)
        if total == 0: return ('disc',)
        for e, cnt in et.items(): load[e] += Fraction(cnt, total)
    m = len(M); maxload = max(load.values()) if load else Fraction(0)
    bound = max(Fraction(1), Fraction(N*N, 25*m))
    return maxload, bound, m

def sweep(Ns):
    worst = Fraction(0); worst_inst = None; viol = 0; tot = 0
    for N in Ns:
        states = fe.enumerate_graphs(N, triangle_free=True); wN = Fraction(0); vN = 0; cnt = 0
        for (n, A) in states:
            r = uniform_maxload(n, A)
            if r is None or (isinstance(r, tuple) and r and r[0] == 'disc'): continue
            maxload, bound, m = r; cnt += 1; tot += 1
            ratio = maxload/bound
            if maxload > bound: vN += 1; viol += 1
            if ratio > wN: wN = ratio
            if ratio > worst: worst = ratio; worst_inst = (N, float(maxload), float(bound), m)
        print(f"N={N}: {cnt} instances, uniform>bound VIOLATIONS={vN}, worst maxload/bound={float(wN):.4f}", flush=True)
    print(f">>> total {tot}, uniform-routing VIOLATIONS={viol}, overall worst ratio={float(worst):.4f} at {worst_inst}", flush=True)
    return viol

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
def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

if __name__ == "__main__":
    print("=== UNIFORM-geodesic routing congestion vs bound ===", flush=True)
    sweep([5, 6, 7, 8, 9])
    print("--- battery ---", flush=True)
    for (N, A, lab) in [(*grotzsch(), "Grotzsch"), (*subdivk5(2), "subdivK5-2"), (*c5n(4), "C5[4]"), (*c5n(5), "C5[5]")]:
        r = uniform_maxload(N, A)
        if r and not (isinstance(r, tuple) and r[0] == 'disc'):
            maxload, bound, m = r
            print(f"{lab:12s} N={N} m={m} uniform-maxload={float(maxload):.4f} bound={float(bound):.4f} OK={maxload<=bound}", flush=True)
    print("DONE", flush=True)
