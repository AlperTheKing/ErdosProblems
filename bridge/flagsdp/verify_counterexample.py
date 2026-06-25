#!/usr/bin/env python3
"""AUDIT GPT's counterexample to the global-layering mechanism (P5 breakthrough, chat 6a3b5aba).
M = C5 on x_0..x_4 (bad edges x_i x_{i+1}); for each i a disjoint B-path Q_i: x_i-y_i-z_i-w_i-x_{i+1}.
Claims to verify: (1) triangle-free; (2) d_B(x_i,x_{i+1})=4 for each bad edge; (3) the cut X={x_i,z_i},
Y={y_i,w_i} has beta=|M|=5 and IS a MAXIMUM cut (=> cut-domination CD holds, since CD <=> max cut);
(4) M=C5 is not bipartite; (5) 25|M|=125 < N^2=400. If all hold, the global-layering mechanism is genuinely
obstructed (so the Sync gap is real), exactly as GPT claims.
"""
from collections import deque

def build():
    # x_i = i (0..4); y_i,z_i,w_i = 5+3i, 6+3i, 7+3i
    x = [i for i in range(5)]
    y = [5 + 3 * i for i in range(5)]; z = [6 + 3 * i for i in range(5)]; w = [7 + 3 * i for i in range(5)]
    N = 20
    B = set(); M = set()
    for i in range(5):
        a, b = x[i], x[(i + 1) % 5]
        M.add((min(a, b), max(a, b)))
        for (u, v) in [(x[i], y[i]), (y[i], z[i]), (z[i], w[i]), (w[i], x[(i + 1) % 5])]:
            B.add((min(u, v), max(u, v)))
    return N, B, M, x, y, z, w

def adjset(N, E):
    A = [set() for _ in range(N)]
    for (u, v) in E:
        A[u].add(v); A[v].add(u)
    return A

def trifree(N, A):
    for u in range(N):
        for v in A[u]:
            if v > u and (A[u] & A[v]):
                return False
    return True

def bdist(N, AB, src, dst):
    dist = [-1] * N; dist[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            return dist[u]
        for v in AB[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1; q.append(v)
    return dist[dst]

def maxcut(N, Aall, E):
    adj = [[1 if v in Aall[u] else 0 for v in range(N)] for u in range(N)]
    best = 0
    for mask in range(1 << (N - 1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = 0
        for (u, v) in E:
            if side[u] != side[v]:
                c += 1
        if c > best:
            best = c
    return best

def main():
    N, B, M, x, y, z, w = build()
    Aall = adjset(N, B | M); AB = adjset(N, B)
    e = len(B) + len(M)
    print(f"N={N}, |B|={len(B)}, |M|={len(M)}, e={e}", flush=True)
    tf = trifree(N, Aall); print(f"(1) triangle-free: {tf}", flush=True)
    dists = [bdist(N, AB, a, b) for (a, b) in M]
    print(f"(2) d_B per bad edge: {dists}  (all == 4: {all(d == 4 for d in dists)})", flush=True)
    # cut X={x_i,z_i}, Y={y_i,w_i}
    X = set(x) | set(z); side = [0 if u in X else 1 for u in range(N)]
    betaM = sum(1 for (u, v) in M if side[u] == side[v]); betaB = sum(1 for (u, v) in B if side[u] == side[v])
    cutval = sum(1 for (u, v) in (B | M) if side[u] != side[v])
    print(f"(3) cut X={{x,z}},Y={{y,w}}: mono-in-M={betaM} (=|M|? {betaM==len(M)}), mono-in-B={betaB} (=0? {betaB==0}); cut={cutval}", flush=True)
    mc = maxcut(N, Aall, list(B | M))
    print(f"    MaxCut(G)={mc}; this cut={cutval}; IS MAX (=> CD holds): {cutval==mc}; beta=e-MaxCut={e-mc}", flush=True)
    # M = C5 bipartite? odd cycle -> no
    print(f"(4) M is C5 (odd cycle) -> not bipartite: True", flush=True)
    print(f"(5) 25|M|={25*len(M)} < N^2={N*N}: {25*len(M) < N*N}  (P5 bound itself fine)", flush=True)
    ok = tf and all(d == 4 for d in dists) and betaM == len(M) and betaB == 0 and cutval == mc
    print(f"COUNTEREXAMPLE VALID (all GPT claims hold): {ok}", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
