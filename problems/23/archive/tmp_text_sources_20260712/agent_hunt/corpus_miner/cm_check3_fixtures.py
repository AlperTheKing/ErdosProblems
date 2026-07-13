# CHECK-3 (corpus miner): decode the two zero-vector falsifier fixtures from the archives
# (#298 R49, #264 R50) and verify structural claims + non-applicability boundaries of the
# proposed top-order lemma. Integer arithmetic only.
import sys
from collections import deque

def graph6_decode(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    assert 0 <= n <= 62
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [[0]*n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i][j] = adj[j][i] = 1
            idx += 1
    return n, adj

def analyze(name, g6):
    n, adj = graph6_decode(g6)
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if adj[i][j]]
    m = len(edges)
    # bipartition (BFS 2-coloring)
    color = [-1]*n
    bip = True
    for s in range(n):
        if color[s] == -1:
            color[s] = 0
            dq = deque([s])
            while dq:
                u = dq.popleft()
                for v in range(n):
                    if adj[u][v]:
                        if color[v] == -1:
                            color[v] = 1 - color[u]
                            dq.append(v)
                        elif color[v] == color[u]:
                            bip = False
    shores = (sum(1 for c in color if c == 0), sum(1 for c in color if c == 1))
    degs = [sum(adj[i]) for i in range(n)]
    deg5 = [i for i in range(n) if degs[i] == 5]
    # connected components
    comp = [-1]*n; nc = 0
    for s in range(n):
        if comp[s] == -1:
            nc += 1
            dq = deque([s]); comp[s] = nc
            while dq:
                u = dq.popleft()
                for v in range(n):
                    if adj[u][v] and comp[v] == -1:
                        comp[v] = nc; dq.append(v)
    mu = m - n + nc
    # BFS distances
    def bfs(s):
        d = [-1]*n; d[s] = 0; dq = deque([s])
        while dq:
            u = dq.popleft()
            for v in range(n):
                if adj[u][v] and d[v] == -1:
                    d[v] = d[u] + 1; dq.append(v)
        return d
    dist = [bfs(i) for i in range(n)]
    same_shore_d4 = [(i, j) for i in range(n) for j in range(i+1, n)
                     if color[i] == color[j] and dist[i][j] == 4]
    print(f"{name}: n={n} edges={m} bipartite={bip} shores={shores} components={nc} mu={mu}")
    print(f"  degree sequence: {sorted(degs, reverse=True)}")
    print(f"  deg-5 vertices: {deg5}")
    print(f"  same-shore distance-4 pairs (atom candidates): {len(same_shore_d4)}")
    # top-order lemma applicability: t=5 needs |V| = 21
    print(f"  top-order (t^2-t+1=21) lemma applies: {n == 21}")
    return n, m, bip, shores, mu, len(same_shore_d4)

analyze("#298 (R49 zero-vector hit)", "Q??????wE_[?EGs?D_@A?C_B???")
analyze("#264 (R50 live-x hit)     ", "Q??????wE_Bws?s?DCD??@?@???")
analyze("R46 CP-SAT support hit    ", "Q???????F?Y?E{d?KOE??B?B???")

# 18-vtx near-candidate (R46 sec 8) built from its explicit description:
# L = {v,m,a,b0..b4} (indices 0=v,1=m,2=a,3..7=b0..b4), R = {x0..x4 (8..12), y0..y4 (13..17)}
n = 18
adj = [[0]*n for _ in range(n)]
def add(i, j): adj[i][j] = adj[j][i] = 1
for xi in range(8, 13):
    add(0, xi); add(1, xi)          # v,m -> all x_i
for xi in range(8, 12):
    add(2, xi)                       # a -> x0..x3
for yj in range(13, 18):
    add(2, yj)                       # a -> y_j
for k in range(5):
    add(3 + k, 13 + k)               # b_j -> y_j
m_e = sum(sum(r) for r in adj)//2
print(f"near-candidate rebuild: edges={m_e} (expect 24)")
# shared blue star check: N(v) == N(m)?
Nv = {j for j in range(n) if adj[0][j]}
Nm = {j for j in range(n) if adj[1][j]}
print(f"  N_B(v)==N_B(m): {Nv == Nm}  (shared-star motif present at order 18: {sorted(Nv)})")
# bounce coverage row shape (x4, m, x_i, a, y_j): verify path edges exist
row_ok = adj[12][1] and adj[1][8] and adj[8][2] and adj[2][13]
print(f"  bounce row (x4,m,x0,a,y0) is a path in the graph: {bool(row_ok)}")
