"""
Pin down the EXACT crossing-defect accounting for the laminar recursion.

Setup recap. Optimal dual metric d = d_ell on V, ell on B, normalize sum_b ell_b = 1.
rho = sum_{uv in M} d(u,v).  We want rho <= max{1, N^2/(25m)}.

LAMINAR RECURSION (the actual argument):
We do NOT use a single root. We use the family of ALL geodesic balls. The key object is the
"separating cut measure": for the metric d, define for each ordered threshold the level cut.
By the cut-cone decomposition of an L1 metric, ANY metric d has a maximal L1 part. But d itself
need not be L1.

The accounting I want to verify: define for each bad edge its STRETCH s_uv = d(u,v). Then
   rho = sum_uv s_uv.
CD/coarea (Sep) controls the L1 (cut) part. The QUADRATIC control is:
   sum_uv s_uv^2 <= (cosystole-type invariant) <= ... related to N^2.
Test the Cauchy bridge:  rho = sum s_uv <= sqrt(m * sum s_uv^2).
If we can show  sum_{uv in M} d_ell(u,v)^2 <= (1/25) N^2 * (sum_b ell_b)^2 / m * m ... let's just measure
the ratio  R2 := sum_uv d(u,v)^2 / (sum_b ell_b)^2   and compare to N^2/25 and to m.
"""
import math, heapq, itertools
import numpy as np
import sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
sys.path.insert(0, r'E:\Projects\ErdosProblems\attack3_scratch')
import flag_engine as fe
from laminar_recursion import adjset, maxcut, rho_mcf

def dell_all(N, adjB, ellmap):
    D = [[math.inf]*N for _ in range(N)]
    for s in range(N):
        dist = [math.inf]*N; dist[s] = 0; pq = [(0.0, s)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]: continue
            for w in adjB[u]:
                e = (min(u, w), max(u, w)); nd = d + ellmap[e]
                if nd < dist[w]: dist[w] = nd; heapq.heappush(pq, (nd, w))
        D[s] = dist
    return D

def optimal_metric_lp(N, adjB, M, Be):
    """Solve rho exactly via LP and recover an optimal ell from the dual of the flow LP.
    We solve the *fractional sparsest-cut-style* dual directly:
       rho = max_{ell>=0} sum_M d_ell(u,v)  s.t. sum_b ell_b <= 1.
    This is a max of a concave (min over paths) -> LP after enumerating simple paths is huge.
    Instead: the LP  max sum_uv z_uv ; z_uv <= sum_{b in P} ell_b for all u-v paths P in B (exp many);
    sum ell <=1. We use the equivalent compact 'metric on B-edges' LP via the cut formulation is
    also hard. So: get rho from rho_mcf (flow LP), and recover ell by solving the small LP only on
    the SHORTEST paths discovered greedily (column generation)."""
    # column generation for the path-LP dual
    ell = {e: 1.0/len(Be) for e in Be}
    for _ in range(2000):
        D = dell_all(N, adjB, ell)
        # objective grad: shortest path edges
        # subgradient ascent
        grad = {e: 0.0 for e in Be}
        tot = 0.0
        for (u, v) in M:
            # recover one shortest path
            dist = [math.inf]*N; par = [(-1, None)]*N; dist[u] = 0; pq = [(0.0, u)]
            while pq:
                dd, x = heapq.heappop(pq)
                if dd > dist[x]: continue
                for w in adjB[x]:
                    e = (min(x, w), max(x, w)); nd = dd + ell[e]
                    if nd < dist[w]-1e-15: dist[w] = nd; par[w] = (x, e); pq.append((nd, w))
            tot += dist[v]
            x = v
            while x != u and par[x][0] != -1:
                grad[par[x][1]] += 1.0; x = par[x][0]
        lr = 0.5/math.sqrt(_+1)
        for e in Be: ell[e] += lr*grad[e]
        for e in Be: ell[e] = max(0.0, ell[e])
        s = sum(ell.values())
        if s > 0:
            for e in Be: ell[e] /= s
    return ell

def analyze(N, A, name, exact_rho=None):
    adj = adjset(N, A); edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(min(u, v), max(u, v)) for (u, v) in edges if side[u] == side[v]]
    if not M: return
    adjB = [set() for _ in range(N)]; Be = []
    for (u, v) in edges:
        if side[u] != side[v]: adjB[u].add(v); adjB[v].add(u); Be.append((min(u, v), max(u, v)))
    m = len(M)
    rho = rho_mcf(N, adjB, M)
    ell = optimal_metric_lp(N, adjB, M, Be)
    D = dell_all(N, adjB, ell)
    sumell = sum(ell.values())
    s = [D[u][v]/sumell for (u, v) in M]   # normalized stretches
    rho_recovered = sum(s)
    sum_s2 = sum(x*x for x in s)
    print(f"{name}: N={N} m={m} rho(flow)={rho:.4f} rho(recovered metric)={rho_recovered:.4f}")
    print(f"    stretches s_uv = {[round(x,3) for x in s]}")
    print(f"    sum s = {rho_recovered:.4f}  sum s^2 = {sum_s2:.4f}  sqrt(m*sum s^2)={math.sqrt(m*sum_s2):.4f}")
    print(f"    N^2/25 = {N*N/25.0:.3f}   m*sum_s2 (vs (N^2/25)?) = {m*sum_s2:.3f}")
    print(f"    bound max(1,N^2/25m)={max(1.0,N*N/(25.0*m)):.4f}")

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
