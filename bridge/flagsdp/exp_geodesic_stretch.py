#!/usr/bin/env python3
"""DECISIVE EXPERIMENT (Workflow wf7a8np3k recommendation): does the optimal dual metric ell* of
   rho = max_{ell>=0} (sum_{uv in M} d^B_ell(u,v)) / (sum_b ell_b)
STRETCH any M-geodesic beyond its unweighted B-distance d_B(u,v)?

If NO stretch (every M-pair has an ell*-shortest B-path using exactly d_B(u,v) edges), then CUTCOST25(ii)
collapses onto the already-proved unit cosystole Gamma=sum_M (d_B+1)^2 <= N^2, and the cut-cone route CLOSES.
If stretch occurs, the route needs the full non-scalar congestion bound (as hard as BCL).

Method: enumerate simple B-paths per M-pair (capped); metric LP max sum D_k s.t. sum ell=1, D_k<=path-sum;
then with ell*, Dijkstra in B to get exact ell*-distance, build the tight shortest-path DAG, and find the
MIN edge-count among ell*-shortest paths; compare to d_B.
"""
import itertools, heapq
import numpy as np
from collections import deque, defaultdict
from scipy.optimize import linprog

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
            if w not in ps:
                ps.add(w); path.append(w); dfs(w, path, ps); path.pop(); ps.discard(w)
    dfs(s, [s], {s})
    return out

def analyze(N, A, label):
    adj = adjset(N, A); adjlist = [sorted(adj[u]) for u in range(N)]
    mc, side = maxcut(N, adj)
    Bedges = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    adjB = [set() for _ in range(N)]
    for (u, v) in Bedges: adjB[u].add(v); adjB[v].add(u)
    bidx = {e: i for i, e in enumerate(Bedges)}; nB = len(Bedges)
    # d_B per M-pair
    dB = {}
    for (u, v) in M:
        d = bdist(N, adjB, u); dB[(u, v)] = d[v]
    maxlen = max(dB.values()) + 6
    # enumerate paths per M-pair
    paths = {}
    for (u, v) in M:
        ps = simple_paths(adjB, u, v, maxlen)
        paths[(u, v)] = [[tuple(sorted((p[i], p[i+1]))) for i in range(len(p)-1)] for p in ps]
    # metric LP: vars [ell_0..ell_{nB-1}, D_0..D_{m-1}] ; max sum D  => min -sum D
    m = len(M); nvar = nB + m
    c = np.zeros(nvar); c[nB:] = -1.0
    A_ub = []; b_ub = []
    for k, e in enumerate(M):
        for P in paths[e]:
            row = np.zeros(nvar); row[nB+k] = 1.0
            for b in P: row[bidx[b]] -= 1.0
            A_ub.append(row); b_ub.append(0.0)        # D_k - sum ell_b <= 0
    A_eq = [np.concatenate([np.ones(nB), np.zeros(m)])]; b_eq = [1.0]   # sum ell = 1
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nvar, method="highs")
    ell = res.x[:nB]; rho = -res.fun
    bound = max(1.0, N*N/(25.0*m))
    # ell*-shortest distance + min edge-count among ell*-shortest paths (Dijkstra + tight DAG BFS)
    def ellw(b): return ell[bidx[b]]
    stretch_pairs = []; unit_ratio_num = 0
    EPS = 1e-7
    for (u, v) in M:
        # dijkstra
        dist = [float('inf')]*N; dist[u] = 0.0; pq = [(0.0, u)]
        while pq:
            d0, x = heapq.heappop(pq)
            if d0 > dist[x]+EPS: continue
            for y in adjB[x]:
                w = ellw(tuple(sorted((x, y))))
                if dist[x]+w < dist[y]-EPS: dist[y] = dist[x]+w; heapq.heappush(pq, (dist[y], y))
        Dval = dist[v]
        # tight DAG: edge (x,y) tight if dist[x]+w == dist[y]
        succ = defaultdict(list)
        for (x, y) in Bedges:
            w = ellw((x, y))
            if abs(dist[x]+w - dist[y]) < 1e-6: succ[x].append(y)
            if abs(dist[y]+w - dist[x]) < 1e-6: succ[y].append(x)
        # min #edges from u to v in tight DAG (BFS by edge count)
        de = [None]*N; de[u] = 0; q = deque([u])
        while q:
            x = q.popleft()
            for y in succ[x]:
                if de[y] is None or de[x]+1 < de[y]:
                    if de[y] is None: q.append(y)
                    de[y] = de[x]+1 if (de[y] is None or de[x]+1 < de[y]) else de[y]
        minedges = de[v]
        unit_ratio_num += dB[(u, v)]
        if minedges is None or minedges > dB[(u, v)]:
            stretch_pairs.append(((u, v), dB[(u, v)], minedges, Dval))
    unit_ratio = unit_ratio_num/nB
    print(f"{label}: N={N} |B|={nB} m={m} rho={rho:.4f} bound=max(1,N^2/25m)={bound:.4f} "
          f"unit-metric-ratio(sum dB/|B|)={unit_ratio:.4f}", flush=True)
    print(f"   ell* support size={int(np.sum(ell>1e-7))}/{nB}  STRETCHED M-pairs (minedges>d_B): {len(stretch_pairs)}", flush=True)
    for sp in stretch_pairs[:8]:
        print(f"     pair {sp[0]} d_B={sp[1]} ell*-shortest min#edges={sp[2]}", flush=True)
    if not stretch_pairs:
        print("   >>> NO STRETCH: every M-pair has an ell*-shortest path of exactly d_B edges => route reduces to Gamma<=N^2", flush=True)
    else:
        print("   >>> STRETCH PRESENT: ell* lengthens some geodesic => CUTCOST25(ii) needs the full congestion bound", flush=True)
    return rho, len(stretch_pairs)

# graph builders
def petersen():
    verts = list(itertools.combinations(range(5), 2)); A = [0]*10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b): A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A
def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A
def c5paths20():
    N = 20; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    x = lambda i: i % 5; y = lambda i: 5+(i % 5); z = lambda i: 10+(i % 5); w = lambda i: 15+(i % 5)
    for i in range(5):
        add(x(i), x(i+1)); add(x(i), y(i)); add(y(i), z(i)); add(z(i), w(i)); add(w(i), x(i+1))
    return N, A
def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

if __name__ == "__main__":
    print("=== DECISIVE EXPERIMENT: does ell* stretch M-geodesics? ===", flush=True)
    for (N, A, lab) in [(*gpt_k23(), "K23-N13"), (*c5paths20(), "C5paths-N20"),
                        (*petersen(), "Petersen"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]")]:
        analyze(N, A, lab)
        print(flush=True)
    print("DONE", flush=True)
