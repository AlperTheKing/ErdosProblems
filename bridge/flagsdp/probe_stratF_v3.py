#!/usr/bin/env python3
"""
STRATEGY F v3: C5[q] with EXPLICIT known max cut (no brute force), compute random-reference
second moments exactly to extract the limiting identity, and test the L1 coarea margin.

C5[q]: parts V_0..V_4 each size q, V_i ~ V_{i+1} complete bipartite (mod 5).
Known maximum cut: X = V_0 u V_1 u V_2 (size 3q ... but blow-up of C5 max cut).
Actually max cut of C5 puts the 5 vertices: cut value 4 (one part has 3, edges across=4).
For C5: vertices 0,1,2,3,4 cycle. Max cut X={0,2}, Y={1,3,4}? edges crossing: 01,12,23,34,40
 -> 01 cross,12 cross,23 cross,34 same(3,4 both Y),40 cross =>4 crossing,1 mono(34).
So in C5[q] the analogous max cut: X=V_0 u V_2, Y=V_1 u V_3 u V_4. Mono (bad) edges = within
V_3~V_4 (the analog of edge 34) => m = q^2, all bad edges between V_3 and V_4.
B = all other complete-bipartite pairs: V0V1,V1V2,V2V3,V4V0 (V3V4 is the mono one).
B-distance between u in V3 and v in V4: shortest even B-path. In C5[q], d_B(V3,V4) via
V3-V2-V1-V0-V4 = length 4. So ell=5 for every bad edge. Good, m=q^2, Gamma=25q^2=(5q)^2=N^2.
"""
from collections import deque

def build_c5q(q):
    # parts 0..4, vertex (p,i) -> id p*q+i
    N = 5 * q
    def vid(p, i):
        return p * q + i
    part = lambda v: v // q
    Eall = []
    for p in range(5):
        for pp in range(p + 1, 5):
            if (p - pp) % 5 in (1, 4):
                for i in range(q):
                    for j in range(q):
                        Eall.append((vid(p, i), vid(pp, j)))
    # known max cut: bad = V3~V4
    # B = everything except V3-V4 edges
    M = [(u, v) for (u, v) in Eall if {part(u), part(v)} == {3, 4}]
    Bset = [(u, v) for (u, v) in Eall if {part(u), part(v)} != {3, 4}]
    return N, Eall, M, Bset

def adjset(N, E):
    adj = [set() for _ in range(N)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return adj

def bdist(N, Badj, src):
    d = [-1] * N; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in Badj[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def stats(q):
    N, Eall, M, Bset = build_c5q(q)
    Badj = adjset(N, Bset)
    Dall = [bdist(N, Badj, r) for r in range(N)]
    # verify all ell=5
    ells = set()
    for (u, v) in M:
        ells.add(Dall[u][v] + 1)
    L2M = sum((Dall[r][u] - Dall[r][v]) ** 2 for r in range(N) for (u, v) in M)
    L2B = sum((Dall[r][u] - Dall[r][v]) ** 2 for r in range(N) for (u, v) in Bset)
    L1M = sum(abs(Dall[r][u] - Dall[r][v]) for r in range(N) for (u, v) in M)
    L1B = sum(abs(Dall[r][u] - Dall[r][v]) for r in range(N) for (u, v) in Bset)
    Gamma = 25 * len(M)
    return dict(q=q, N=N, m=len(M), B=len(Bset), Gamma=Gamma, ells=ells,
                L2M=L2M, L2B=L2B, L1M=L1M, L1B=L1B)

print("C5[q] EXACT scaling (explicit cut):")
print(f"{'q':>2} {'N':>3} {'m':>4} {'ells':>8} {'Gamma':>6} {'L2M':>8} {'L2B':>8} "
      f"{'L1M':>7} {'L1B':>7} {'L1B-L1M':>8} {'L2M/m':>7} {'L2B/B':>7}")
for q in range(1, 9):
    s = stats(q)
    print(f"{s['q']:>2} {s['N']:>3} {s['m']:>4} {str(sorted(s['ells'])):>8} {s['Gamma']:>6} "
          f"{s['L2M']:>8} {s['L2B']:>8} {s['L1M']:>7} {s['L1B']:>7} {s['L1B']-s['L1M']:>8} "
          f"{s['L2M']/s['m']:>7.3f} {s['L2B']/s['B']:>7.3f}")
print()
print("Fit L1M, L1B, L2M, L2B as polynomials in q (m=q^2, |B|=4q^2, N=5q):")
print("DONE")
