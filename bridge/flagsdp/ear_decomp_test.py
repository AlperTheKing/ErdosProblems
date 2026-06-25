"""Test the EAR-DECOMPOSITION INDUCTION (Strategy B) for the Connected-B Gamma Lemma.

Setup: G triangle-free, max cut (X,Y), B=cut graph (CONNECTED, assume 2-connected),
M=bad edges, ell(uv)=d_B(u,v)+1. We want Gamma = sum ell^2 <= N^2.

An open ear decomposition of a 2-connected graph B:
   B_0 = a cycle; B_{k} = B_{k-1} + ear P_k (a path whose 2 endpoints are in B_{k-1},
   internal vertices new). #internal = p_k. N = (len of B_0) + sum p_k.

Idea: maintain an invariant that is N^2 minus a 'used budget'. The candidate is:
   after building B_t on N_t vertices, the bad edges 'supported' inside B_t satisfy
   Gamma_t <= N_t^2 - slack_t. We need to find what per-ear inequality holds.

BUT: bad edges are NOT in B. They are determined by G. A bad edge uv lives between
two vertices of B; its ell depends on d_B. Adding an ear can DECREASE d_B(u,v) for
existing bad edges (shortcut) -> ell can only go DOWN -> Gamma DOWN as ears are added.
=> Build B 'in reverse': start from full B, remove ears; d_B only INCREASES; ells go UP.
The base (a single cycle) is an odd cycle = extremal. Hmm.

This script empirically tests, for connected-B instances, a DIFFERENT clean idea:

  THE 'BAD-EDGE CHARGES TO ITS GEODESIC RECTANGLE' partition.
For each bad edge uv with ell=d_B(u,v)+1, pick a shortest B-path P_uv (length ell-1).
Define for a vertex v its 'radius' r(v) and test whether the family of geodesics
can be packed so that congestion is <= the AM-GM bound.

We test: is sum_{uv} ell(uv) <= ... and is there a fractional vertex 2-coloring /
weighting giving Gamma <= N^2 via Cauchy-Schwarz with the RIGHT inner product.
"""
from collections import deque
import flag_engine as fe

def adjset(n, A):
    return [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]

def all_maxcuts(n, adj):
    best = -1; cuts = []
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        c = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c; cuts = [side]
        elif c == best:
            cuts.append(side)
    return best, cuts

def bdist(n, adjB, src):
    d = [-1] * n; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def all_shortest_geodesics_edge_load(n, adjB, u, v):
    """Return for each B-edge the FRACTION of shortest u-v geodesics through it
    (uniform over all shortest paths), as a dict edge->load in [0,1]. Sum of loads
    = (ell-1) = number of edges on each path."""
    du = bdist(n, adjB, u); dv = bdist(n, adjB, v)
    D = du[v]
    if D < 0:
        return {}, D
    # count shortest paths via DAG of edges on some geodesic
    # number of shortest u->x paths
    from functools import lru_cache
    cntu = [0] * n; cntu[u] = 1
    order = sorted(range(n), key=lambda x: du[x])
    for x in order:
        if du[x] < 0:
            continue
        for w in adjB[x]:
            if du[w] == du[x] + 1:
                cntu[w] += cntu[x]
    # number of shortest x->v paths = shortest paths in reversed using dv
    cntv = [0] * n; cntv[v] = 1
    orderv = sorted(range(n), key=lambda x: dv[x])
    for x in orderv:
        if dv[x] < 0:
            continue
        for w in adjB[x]:
            if dv[w] == dv[x] + 1:
                cntv[w] += cntv[x]
    total = cntu[v]
    load = {}
    for x in range(n):
        for w in adjB[x]:
            if x < w:
                # edge xw on a geodesic iff du[x]+1==du[w] and lies on some u..v path
                for (a, b) in [(x, w), (w, x)]:
                    if du[a] + 1 == du[b] and du[a] + 1 + dv[b] == D:
                        paths_through = cntu[a] * cntv[b]
                        load[(min(x, w), max(x, w))] = paths_through / total
    return load, D

def connectedB_instances(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    out = []
    for (n, A) in states:
        adj = adjset(n, A)
        E = [(u, v) for u in range(n) for v in adj[u] if v > u]
        if not E:
            continue
        mc, cuts = all_maxcuts(n, adj)
        for side in cuts[:1]:
            adjB = [set() for _ in range(n)]
            for (u, v) in E:
                if side[u] != side[v]:
                    adjB[u].add(v); adjB[v].add(u)
            seen = set([0]); q = deque([0])
            while q:
                u = q.popleft()
                for w in adjB[u]:
                    if w not in seen:
                        seen.add(w); q.append(w)
            if len(seen) != n:
                continue
            M = [(u, v) for (u, v) in E if side[u] == side[v]]
            if not M:
                continue
            ok = True; ells = []
            for (u, v) in M:
                d = bdist(n, adjB, u)[v]
                if d < 4 or d % 2:
                    ok = False; break
                ells.append(d + 1)
            if not ok:
                continue
            out.append((n, adjB, M, ells))
    return out

if __name__ == "__main__":
    # TEST: the "geodesic vertex-load" certificate.
    # For each bad edge route 1 unit along its (uniform) shortest geodesics. Each unit
    # path of length ell-1 deposits ell-1 edge-load total. Define vertex load
    #   lam_v = (sum over bad edges) of [fraction of geodesic passing THROUGH v].
    # A geodesic of length ell-1 has ell-2 internal vertices + 2 endpoints.
    # CLAIM candidate: 2*sum_v lam_v^2 <= N * sum_uv ell? or Cauchy gives Gamma bound?
    # Empirically measure max congestion and the resulting bound.
    for N in [8, 9, 10]:
        inst = connectedB_instances(N)
        worst_cong = 0.0; worst_inst = None
        for (n, adjB, M, ells) in inst:
            # vertex load from uniform geodesic routing
            lam = [0.0] * n
            for (u, v) in M:
                load, D = all_shortest_geodesics_edge_load(n, adjB, u, v)
                # convert edge-load to vertex-load: a vertex's load = (sum incident edge-load)/2
                vl = [0.0] * n
                for (a, b), f in load.items():
                    vl[a] += f / 2; vl[b] += f / 2
                # endpoints u,v get an extra 1/2 each to count them fully on the path
                for i in range(n):
                    lam[i] += vl[i]
            maxlam = max(lam)
            if maxlam > worst_cong:
                worst_cong = maxlam; worst_inst = (n, sorted(ells))
        print(f"N={N}: instances={len(inst)} max vertex geodesic-load lam={worst_cong:.3f} at {worst_inst}")
    print("DONE")
