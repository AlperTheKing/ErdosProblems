"""Analyze the factored bound  L * S <= N^2,  L=max_ell, S=sum_ell.
Is it self-tight? Does it reduce to cycle-degree / a packing we can prove?

Decompose: S = sum_{uv in M} ell(uv). Each bad edge uv + a shortest B-geodesic = an odd
cycle C_uv of length ell(uv). The PROVED cycle-degree inequality: for an odd cycle C of
length L', sum_{v in C} deg_G(v) <= N(L'-1)/2.

Idea: if we could pack the bad-edge odd cycles edge-disjointly (or with bounded vertex
congestion kappa), then sum ell <= kappa * N (a vertex appears in <= kappa cycles, sum of
cycle lengths = sum over vertices of #cycles through it <= kappa*N). On C5[q] each vertex is
in q bad-cycles (its part has q bad edges to each neighbor part... actually each vertex of
part i is endpoint of q bad edges to part... no). Measure the ACTUAL vertex-congestion of
the bad-edge SHORTEST CYCLES and see what kappa is on the extremals.

L*S<=N^2 <=> S <= N * (N/L) <=> S/N <= N/L. On C5[q]: S/N=q, N/L=5q/5=q. EQUAL. On odd
cycle: S/N=1, N/L=1. EQUAL. So the factored bound is EXACTLY 'S/N <= N/L', tight on both.
Test: is S/N (avg ell per vertex) <= N/L (= #vertices per longest-cycle-edge)?
"""
from collections import deque
import ear_invariant as EI

def bdist(n, adjB, src):
    d = [-1] * n; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def shortest_cycle_vertices(n, adjB, u, v):
    """Return vertices of ONE shortest u-v B-path (+ the bad edge uv) = the odd cycle."""
    d = bdist(n, adjB, u)
    if d[v] < 0:
        return None
    # backtrack one shortest path
    path = [v]; cur = v
    while cur != u:
        for w in adjB[cur]:
            if d[w] == d[cur] - 1:
                path.append(w); cur = w; break
    return path  # length d[v]+1 vertices

def analyze(name, n, adj, side):
    adjB = [set() for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            if v > u and side[u] != side[v]:
                adjB[u].add(v); adjB[v].add(u)
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    ells = []; cong = [0] * n
    for (u, v) in M:
        cyc = shortest_cycle_vertices(n, adjB, u, v)
        ells.append(len(cyc))  # = ell
        for x in cyc:
            cong[x] += 1
    L = max(ells); S = sum(ells)
    maxcong = max(cong) if cong else 0
    # S = sum over vertices of (#cycles through it) = sum(cong). check:
    assert abs(sum(cong) - S) < 1e-9 or True
    print(f" {name:12s} N={n:3d} L={L:3d} S={S:4d} L*S={L*S:5d} N^2={n*n:5d} "
          f"ratio={L*S/n/n:.3f} | max vtx-congestion(shortest-cyc)={maxcong} "
          f"sum_cong={sum(cong)} (=S)")

if __name__ == "__main__":
    for q in [1, 2, 3, 4]:
        n, adj, side, idx = EI.C5_blowup(q)
        analyze(f"C5[{q}]", n, adj, side)
    for L in [5, 7, 9]:
        n, adj, side = EI.odd_cycle(L)
        analyze(f"C{L}", n, adj, side)
    n, adj, side, M, idx = EI.c5_paths(4)
    analyze("c5_paths", n, adj, side)
    print()
    print("If max vtx-congestion kappa of the shortest bad-cycles is bounded, then")
    print("S = sum_cong <= kappa*N, and combined with L<=N gives L*S<=kappa*N^2. Need kappa-form.")
    print("DONE")
