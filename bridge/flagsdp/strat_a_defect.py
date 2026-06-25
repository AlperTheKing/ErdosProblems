"""STRATEGY A defect identity test.

Idea: write the bound via the fractional odd-cycle packing y (one shortest odd cycle C_e per bad edge,
weight 1 each so it is just the multiset {C_e}). For the packing-degree lambda_v = #{e : v in C_e}:
  - sum_v lambda_v = sum_e |C_e| = sum_e ell_e =: P  (perimeter)
  - by the proved cycle-degree inequality applied per cycle and summed:
        sum_e sum_{v in C_e} deg(v) <= sum_e N(ell_e - 1)/2
    i.e. sum_v deg(v) lambda_v <= (N/2) sum_e (ell_e - 1) = (N/2)(P - m).
We do NOT use that here for Gamma directly; instead test the SHARP two-variable form that yields 25.

CLEANER: per bad edge, ell_e^2 = ell_e * ell_e. We want sum ell_e^2 <= N^2. At C5[q]: ell=5, m=q^2,
N=5q: sum = 25 q^2 = N^2. At C_{2k+1}: ell=N, m=1, sum = N^2.

KEY two-family discriminant: define for the packing the quantities
   P = sum_e ell_e   (total cycle perimeter),  Q = sum_e ell_e^2 = Gamma.
Cauchy-Schwarz: Q >= P^2/m. We need an UPPER bound on Q. Test whether the cycle-degree inequality
gives a clean P-vs-N relation that, combined with the shell/AM-GM block bound, yields Q <= N^2 with
the 5 appearing. Measure P, Q, m, and the ratio that should be <= 1 at both extremes.
"""
import itertools, numpy as np
from collections import deque
import flag_engine as fe

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]
def maxcut(N, adj):
    best = -1; bs = None
    for m in range(1 << (N-1)):
        s = [(m >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and s[u] != s[v])
        if c > best: best = c; bs = s
    return best, bs

def stats(N, A):
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    M = [(u, v) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    if not M: return None
    adjB = [set(v for v in adj[u] if side[u] != side[v]) for u in range(N)]
    P = 0.0; Q = 0.0; ells = []
    for (u, v) in M:
        d = [-1]*N; d[u] = 0; q = deque([u])
        while q:
            x = q.popleft()
            for y in adjB[x]:
                if d[y] < 0: d[y] = d[x]+1; q.append(y)
        if d[v] < 0: return ('disc',)
        ell = d[v]+1; ells.append(ell); P += ell; Q += ell*ell
    m = len(M)
    # discriminant forms; we want a single quantity <=1 tight at BOTH extremes
    # form 1: Q / N^2 (the target)
    # form 2 (Cauchy lower vs N): P^2/(m N^2)  -- shows the 'P concentrates' regime
    return Q, P, m, N, ells

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A
def odd_cycle(L):
    A = [0]*L
    for i in range(L): A[i] |= 1 << ((i+1) % L); A[(i+1) % L] |= 1 << i
    return L, A
def petersen():
    verts = list(itertools.combinations(range(5), 2)); A = [0]*10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b): A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A
def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

print("=== STRATEGY A: P (perimeter) / Q (Gamma) / m structure at the two extremal families ===")
print(f"{'graph':10s} {'N':>3s} {'m':>4s} {'P':>5s} {'Q=Gam':>6s} {'Q/N^2':>6s} {'P/(5m)':>7s} {'P^2/(25m)':>9s} {'P^2/(25m)/N^2 (<=1?)':>20s}")
for (N, A, lab) in [(*c5n(1), "C5"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]"),
                    (*odd_cycle(5), "C5cyc"), (*odd_cycle(7), "C7"), (*odd_cycle(9), "C9"),
                    (*petersen(), "Petersen"), (*gpt_k23(), "K23-N13")]:
    r = stats(N, A)
    if r is None or r[0] == 'disc': print(f"{lab}: skip"); continue
    Q, P, m, n, ells = r
    # The KEY identity: at C5[q], P=5m, so P^2/(25m)=m=q^2 ... but N^2=25q^2=25m, and Q=25m.
    # so Q = 25m and P^2/(25m)=m. These differ. Let me also print Q vs 25m and Q vs P^2/m.
    print(f"{lab:10s} {n:3d} {m:4d} {P:5.0f} {Q:6.0f} {Q/(n*n):6.3f} {P/(5*m):7.3f} {P*P/(25*m):9.2f} {P*P/(25*m)/(n*n):20.4f}")
print()
print("Note: at C5[q] P=5m, Q=25m, N^2=25m -> Q/N^2=1, P^2/(25m)=m=q^2, P^2/(25m)/N^2=1/25. At C_L cyc: m=1,P=L=N,Q=N^2.")
