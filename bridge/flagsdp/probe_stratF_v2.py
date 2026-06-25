#!/usr/bin/env python3
"""
STRATEGY F v2: identify the CORRECT random object whose first moment is Gamma and whose
control comes from CD, tight at C5[q].

Key facts established:
 - CD coarea: for ALL f, sum_M |f(u)-f(v)| <= sum_B |f(u)-f(v)|.
 - For a SINGLE bad edge e=uv, taking f = d_B(u,.) gives |f(u)-f(v)| = ell_e - 1 = d_B(u,v).
   This is the per-edge stretch potential used in the single-block proof.

The Sync gap: one scalar f can't stretch every bad edge fully at once.

NEW probe: instead of a global potential, use the LOCAL per-edge potential f_e = d_B(u_e,.)
truncated, and a RANDOM CONVEX COMBINATION / random threshold. Test whether
   Gamma = sum_e ell_e^2 = sum_e ell_e * (ell_e)
can be written as an integral over random thresholds of a quantity controlled by |B|.

LAYER-CAKE FOR ell^2: ell_e^2 = sum_{i,j>=0, i<ell, j<ell} 1 ... no.
Better: ell_e^2 = 2 * sum_{t=1..ell_e} t - ell_e  ... but we want a CUT representation.

Use: for the potential f_e(x)=min(d_B(u_e,x), ell_e-1), the threshold cuts S_{e,t}={x: f_e(x) < t}
for t=1..ell_e-1 are nested; bad edge e crosses ALL of them (u in, v out). So
   sum_{t} |delta_M(S_{e,t})| counts e exactly (ell_e - 1) times PLUS other bad edges that cross.
If we could pick ONE common nested family of cuts where bad edge e crosses ~ell_e of them and
B-edges total crossing <= N per cut... that's the energy profile route (self-tight).

Instead test the DIRECTED / VARIANCE decomposition that explains the ratio-1 limit.

We compute, at C5[q], the EXACT value of sum_r sum_M dd^2 and sum_r sum_B dd^2 as functions of q,
to extract the limiting identity.
"""
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

def c5n(k):
    N = 5 * k; part = lambda v: v // k; E = []
    for u in range(N):
        for v in range(u + 1, N):
            if (part(u) - part(v)) % 5 in (1, 4):
                E.append((u, v))
    return N, E

def stats_c5q(k):
    N, E = c5n(k)
    mc, side = maxcut(N, E)
    M = [(u, v) for u, v in E if side[u] == side[v]]
    Bset = [(u, v) for u, v in E if side[u] != side[v]]
    Badj = adjset(N, Bset)
    Dall = [bdist(N, Badj, r) for r in range(N)]
    L2M = sum((Dall[r][u] - Dall[r][v]) ** 2 for r in range(N) for (u, v) in M)
    L2B = sum((Dall[r][u] - Dall[r][v]) ** 2 for r in range(N) for (u, v) in Bset)
    L1M = sum(abs(Dall[r][u] - Dall[r][v]) for r in range(N) for (u, v) in M)
    L1B = sum(abs(Dall[r][u] - Dall[r][v]) for r in range(N) for (u, v) in Bset)
    Gamma = 25 * len(M)
    return dict(q=k, N=N, m=len(M), B=len(Bset), Gamma=Gamma,
                L2M=L2M, L2B=L2B, L1M=L1M, L1B=L1B)

print("C5[q] scaling -- find the limiting identity:")
print(f"{'q':>2} {'N':>3} {'m':>4} {'|B|':>4} {'Gamma':>6} {'L2M':>7} {'L2B':>7} "
      f"{'L2M/N':>7} {'L2B/N':>7} {'L1M':>6} {'L1B':>6} {'L1M/m':>6}")
for k in range(1, 8):
    s = stats_c5q(k)
    print(f"{s['q']:>2} {s['N']:>3} {s['m']:>4} {s['B']:>4} {s['Gamma']:>6} "
          f"{s['L2M']:>7} {s['L2B']:>7} {s['L2M']/s['N']:>7.2f} {s['L2B']/s['N']:>7.2f} "
          f"{s['L1M']:>6} {s['L1B']:>6} {s['L1M']/s['m']:>6.2f}")
print()
print("Looking for: does L2M/N -> Gamma? does (L2M - something)/N -> Gamma asymptotically?")
print("DONE")
