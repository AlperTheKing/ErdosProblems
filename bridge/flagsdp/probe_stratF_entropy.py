#!/usr/bin/env python3
"""
STRATEGY F probe: random-reference-vertex / random-partition second-moment.

CORE IDEA being tested:
For each bad edge uv, ell(uv)=d_B(u,v)+1. The coarea form of CD says
   sum_{uv in M} |f(u)-f(v)| <= sum_{uv in B} |f(u)-f(v)|   for ALL f.
Take f = d_B(r, .) for a RANDOM reference vertex r (uniform over V).
Each B-edge is 1-Lipschitz for d_B(r,.): |f(x)-f(y)| in {0,1}.
For a bad edge uv: |d_B(r,u)-d_B(r,v)| can be larger.

We test several candidate inequalities, summed/averaged over r in V.
"""
import itertools
from collections import deque

def adjset(N, E):
    adj = [set() for _ in range(N)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return adj

def maxcut(N, E):
    best = -1; bs = None
    for m in range(1 << (N - 1)):
        s = [(m >> u) & 1 for u in range(N)]
        c = sum(1 for u, v in E if s[u] != s[v])
        if c > best:
            best = c; bs = s
    return best, bs

def bdist(N, Badj, src):
    d = [-1] * N; d[src] = 0; q = deque([src])
    while q:
        u = q.popleft()
        for w in Badj[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d

def analyze(N, E, lab):
    mc, side = maxcut(N, E)
    M = [(u, v) for u, v in E if side[u] == side[v]]
    Bset = [(u, v) for u, v in E if side[u] != side[v]]
    Badj = adjset(N, Bset)
    Dall = [bdist(N, Badj, r) for r in range(N)]
    ell = {}
    for (u, v) in M:
        du = Dall[u][v]
        ell[(u, v)] = (du if du > 0 else 0) + 1
    Gamma = sum(e * e for e in ell.values())
    Bconn = all(min(Dall[r]) >= 0 for r in range(N))
    LHS = 0; RHS = 0; L1M = 0; L1B = 0
    for r in range(N):
        d = Dall[r]
        for (u, v) in M:
            if d[u] >= 0 and d[v] >= 0:
                LHS += (d[u] - d[v]) ** 2; L1M += abs(d[u] - d[v])
        for (u, v) in Bset:
            if d[u] >= 0 and d[v] >= 0:
                RHS += (d[u] - d[v]) ** 2; L1B += abs(d[u] - d[v])
    print(f"{lab:14s} N={N:3d} m={len(M):3d} |B|={len(Bset):3d} Gamma={Gamma:5d} N^2={N*N:5d} Bconn={Bconn}")
    print(f"    [L2] sum_r sum_M dd^2={LHS:6d}  sum_r sum_B dd^2={RHS:6d}  ratio M/B={LHS/RHS if RHS else 0:.3f}")
    print(f"    [L1] sum_r sum_M|dd|={L1M:6d}  sum_r sum_B|dd|={L1B:6d}  L1 M<=B={L1M <= L1B}")
    print(f"    [tgt] Gamma={Gamma}  N*Gamma={N*Gamma}  sum_r L2M={LHS}  (Gamma vs sum_r L2M/N = {LHS/N:.2f})")
    return dict(N=N, m=len(M), B=len(Bset), Gamma=Gamma, L2M=LHS, L2B=RHS, L1M=L1M, L1B=L1B)

def c5n(k):
    N = 5 * k; part = lambda v: v // k; E = []
    for u in range(N):
        for v in range(u + 1, N):
            if (part(u) - part(v)) % 5 in (1, 4):
                E.append((u, v))
    return N, E

def theta_atom(l1, l2):
    E = [(0, 1)]; nxt = 2; prev = 0
    for _ in range(l1 - 1):
        E.append((prev, nxt)); prev = nxt; nxt += 1
    E.append((prev, 1)); prev = 0
    for _ in range(l2 - 1):
        E.append((prev, nxt)); prev = nxt; nxt += 1
    E.append((prev, 1))
    return nxt, E

def gpt_k23():
    N = 13; E = []
    for i in (0, 1):
        for j in (2, 3, 4):
            E.append((i, j))
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt + 1; nxt += 2
        E.append((x, a)); E.append((a, b)); E.append((b, y))
    return N, E

def cyc(n):
    return n, [(i, (i + 1) % n) for i in range(n)]

def petersen():
    verts = list(itertools.combinations(range(5), 2))
    E = []
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b):
                E.append((i, j))
    return 10, E

if __name__ == "__main__":
    for lab, (N, E) in [("C5", c5n(1)), ("C5[2]", c5n(2)), ("C5[3]", c5n(3)),
                        ("C7", cyc(7)), ("C9", cyc(9)),
                        ("theta46", theta_atom(4, 6)), ("theta44", theta_atom(4, 4)),
                        ("K23-N13", gpt_k23()), ("Petersen", petersen())]:
        analyze(N, E, lab)
    print("DONE")
