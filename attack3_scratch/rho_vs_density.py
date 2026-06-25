"""
Strategy-2 accounting probe.
For the worst (dual-optimal) metric ell, rho = sum_M d_ell(u,v) / sum_b ell_b (max over ell).
Decompose rho via a SINGLE-ROOT potential + crossing defect, and measure how the
crossing defect scales with m/N^2.

Two single-root facts (PROVED, used below):
  (P1) For any vertex r and phi(x)=d_ell(r,x): sum_{uv in M} |phi(u)-phi(v)| <= sum_b ell_b.
       [coarea/Sep: phi 1-Lipschitz on B, threshold cuts W_t={phi<=t} laminar chain, integrate Sep.]
  (P2) d_ell(u,v) >= |phi(u)-phi(v)|, with equality iff some shortest u-v path is "phi-monotone".
The defect Delta = sum_M [ d_ell(u,v) - |phi(u)-phi(v)| ] is what one root misses.

We test: with the BEST root, what is rho_single = sum_M|phi(u)-phi(v)|/sum ell and the residual.
Then test the hierarchical (laminar) bound: recurse the defect on annuli.
"""
import math, heapq, itertools
import numpy as np
from scipy.optimize import linprog
import sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
sys.path.insert(0, r'E:\Projects\ErdosProblems\attack3_scratch')
from laminar_recursion import adjset, maxcut

def dell(N, adjB, ellmap, s):
    dist = [math.inf]*N; dist[s] = 0; pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for w in adjB[u]:
            e = (min(u, w), max(u, w)); nd = d + ellmap[e]
            if nd < dist[w]: dist[w] = nd; heapq.heappush(pq, (nd, w))
    return dist

def dual_metric(N, adjB, M, Be):
    """Solve the metric LP: max sum_M d_ell(u,v) s.t. sum ell=1, ell>=0.
    Equivalent to rho. Use the cut-cone... no, use the path LP dual directly:
    rho = max over ell>=0, sum ell<=1 of sum_M d_ell. This is a concave max of LP; we
    solve via the multiplicative-weights-free direct LP on the *metric polytope is hard*;
    instead read rho from the flow LP and recover ell from duals.  We approximate the
    optimal ell by a few iterations of subgradient ascent (good enough to probe)."""
    ell = {e: 1.0/len(Be) for e in Be}
    best = 0; bestell = dict(ell)
    lr = 0.3
    for it in range(400):
        # gradient: for each demand, shortest path -> +1 on its edges
        grad = {e: 0.0 for e in Be}
        tot = 0.0
        for (u, v) in M:
            # dijkstra with parent to recover path
            dist = [math.inf]*N; par = [(-1, None)]*N; dist[u] = 0; pq = [(0.0, u)]
            while pq:
                d, x = heapq.heappop(pq)
                if d > dist[x]: continue
                for w in adjB[x]:
                    e = (min(x, w), max(x, w)); nd = d + ell[e]
                    if nd < dist[w]: dist[w] = nd; par[w] = (x, e); pq.append((nd, w))
            tot += dist[v]
            x = v
            while x != u and par[x][0] != -1:
                grad[par[x][1]] += 1.0; x = par[x][0]
        if tot > best: best = tot; bestell = dict(ell)
        # projected gradient ascent on simplex sum ell = 1
        for e in Be: ell[e] += lr/math.sqrt(it+1)*grad[e]
        s = sum(ell.values())
        for e in Be: ell[e] = max(0.0, ell[e])/s
        s = sum(ell.values())
        for e in Be: ell[e] /= s
    return best, bestell

def analyze(N, A, name):
    adj = adjset(N, A); edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(min(u, v), max(u, v)) for (u, v) in edges if side[u] == side[v]]
    if not M: return None
    adjB = [set() for _ in range(N)]
    Be = []
    for (u, v) in edges:
        if side[u] != side[v]:
            adjB[u].add(v); adjB[v].add(u); Be.append((min(u, v), max(u, v)))
    m = len(M)
    rho_approx, ell = dual_metric(N, adjB, M, Be)
    sumell = sum(ell.values())
    # best single-root coarea ratio
    best_single = 0; best_root = None
    for r in range(N):
        phi = dell(N, adjB, ell, r)
        s = sum(abs(phi[u]-phi[v]) for (u, v) in M)
        if s > best_single: best_single = s; best_root = r
    bound = max(1.0, N*N/(25.0*m))
    print(f"{name}: N={N} m={m} |B|={len(Be)}  rho~={rho_approx/sumell:.4f}  "
          f"best_single_root_coarea={best_single/sumell:.4f} (always<=1)  bound={bound:.4f}", flush=True)
    return rho_approx/sumell, m, N

def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

def petersen():
    verts = list(itertools.combinations(range(5), 2)); A = [0]*10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b): A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A

analyze(*gpt_k23(), "K23-N13")
analyze(*petersen(), "Petersen")
print("DONE", flush=True)
