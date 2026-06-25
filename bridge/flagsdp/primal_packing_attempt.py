"""Attempt to CONSTRUCT the extremal fractional odd-cycle packing achieving nu* >= 25 t^2/n^2 directly,
using the cycle-degree inequality as the certificate of feasibility.

Idea (mirrors the odd-K5-free proof but WITHOUT Guenin): pick a min signature S, B=K-S bipartite. For each
bad edge e in S, route a UNIT demand fractionally over ALL shortest B-geodesics (length d_B(e)) -> each
routed geodesic + e is an odd cycle C with C cap S = {e}. This gives a fractional family of private cycles.
Vertex load lambda_v = total weight of cycles through v. Want a SCALING alpha so that alpha*lambda is a
feasible odd-cycle packing (edge-load <= 1) with value alpha * t maximized.

The cycle-degree inequality gives sum_{v in C} deg(v) <= n(|C|-1)/2 = n*d_B(e)/2 for each geodesic cycle.
KEY new test: with the SPREAD (electrical/uniform-over-geodesics) routing, is the per-EDGE congestion
<= max{1, n^2/(25t)} so that scaling by 25t/n^2 yields value 25t^2/n^2?  (this is GPT's QFC25 which was
REFUTED by dilution -- but here we use the BEST signature for the toll, and the ATOM is 2-connected
edge-critical, NOT a dilution. Re-test on the actual atoms + K23.)
"""
import numpy as np
import heapq
from collections import deque, defaultdict
import verify_D25_lemma16 as L


def all_geodesics_load(N, adjB, u, v, dB_uv):
    """uniform spread over all shortest u->v paths in B. Returns dict edge->fractional load (sums to 1
    per unit demand) using the standard #paths DP (counts via BFS layers)."""
    # BFS distances from u and from v
    def bfs(s):
        d = [-1]*N; d[s] = 0; q = deque([s])
        while q:
            x = q.popleft()
            for y in adjB[x]:
                if d[y] < 0:
                    d[y] = d[x]+1; q.append(y)
        return d
    du = bfs(u); dv = bfs(v)
    if du[v] != dB_uv:
        return None
    # number of shortest paths u->x (npu) and x->v (npv) using layer DP on the shortest-path DAG
    npu = [0.0]*N; npu[u] = 1.0
    order = sorted(range(N), key=lambda x: du[x])
    for x in order:
        for y in adjB[x]:
            if du[y] == du[x]+1:
                npu[y] += npu[x]
    npv = [0.0]*N; npv[v] = 1.0
    order2 = sorted(range(N), key=lambda x: dv[x])
    for x in order2:
        for y in adjB[x]:
            if dv[y] == dv[x]+1:
                npv[y] += npv[x]
    total = npu[v]
    if total == 0:
        return None
    load = {}
    vload = np.zeros(N)
    for x in range(N):
        for y in adjB[x]:
            if du[x]+1 == du[y] and du[y]+dv[y] == dB_uv:
                # edge x->y on some shortest path: fraction = npu[x]*npv[y]/total
                f = npu[x]*npv[y]/total
                if f > 0:
                    load[frozenset((x, y))] = load.get(frozenset((x, y)), 0.0)+f
    # vertex load: fraction of paths through x = npu[x]*npv[x]/total (for internal x)
    for x in range(N):
        vload[x] = npu[x]*npv[x]/total
    return load, vload


def analyze(builder, lab):
    N, A = builder
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges)-mc
    if tau == 0:
        print(f"{lab}: bipartite"); return
    sigs = L.min_signatures(N, adj, edges, tau)
    # try EVERY signature, take the one with smallest max congestion of the spread routing
    bestcong = None
    for S in sigs:
        Bset = set(edges)-set(S)
        adjB = [[] for _ in range(N)]
        for b in Bset:
            a, c = tuple(b); adjB[a].append(c); adjB[c].append(a)
        # d_B per bad edge
        congestion = defaultdict(float)
        ok = True
        for e in S:
            u, v = tuple(e)
            # bfs dist
            d = [-1]*N; d[u] = 0; q = deque([u])
            while q:
                x = q.popleft()
                for y in adjB[x]:
                    if d[y] < 0:
                        d[y] = d[x]+1; q.append(y)
            if d[v] < 0:
                ok = False; break
            res = all_geodesics_load(N, adjB, u, v, d[v])
            if res is None:
                ok = False; break
            load, vload = res
            for b, f in load.items():
                congestion[b] += f  # B-edge load
            # the bad edge e itself carries 1 unit (one M-edge per cycle) -> its load is 1
        if not ok:
            continue
        maxc = max(congestion.values()) if congestion else 0.0
        if bestcong is None or maxc < bestcong[0]:
            bestcong = (maxc, S)
    maxc, S = bestcong
    bound = max(1.0, N*N/(25.0*tau))
    # scale by 1/max(1,maxc): value = tau / max(1,maxc); need >= 25 tau^2/n^2
    val = tau/max(1.0, maxc)
    need = 25*tau*tau/(N*N)
    print(f"{lab}: N={N} tau={tau} best-sig spread max B-congestion={maxc:.4f} "
          f"max(1,n^2/25t)={bound:.4f}  QFC-style OK={maxc <= bound+1e-7}")
    print(f"    -> packing value tau/max(1,cong)={val:.4f} need 25t^2/n^2={need:.4f}  OK={val >= need-1e-7}")


for b, lab in [(L.c5(), 'C5'), (L.c5n(2), 'C5[2]'), (L.petersen(), 'Petersen'),
               (L.gpt_k23(), 'K23-N13'), (L.c5n(3), 'C5[3]')]:
    analyze(b, lab)
