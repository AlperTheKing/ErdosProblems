"""
Final check: the LAMINAR ANNULUS RECURSION and its cosystole charging.

Claim of Strategy 2 (the recursion):
Fix optimal metric d=d_ell, sum ell=1. Pick root r. phi(x)=d(r,x).
- The 'radial' part of each demand: rad_uv = |phi(u)-phi(v)|.  By (P1): sum_M rad_uv <= 1.
- The 'tangential' part: tan_uv = d(u,v) - rad_uv >= 0 (triangle-ineq defect).
The tangential demands live INSIDE annuli {t <= phi < t+dt} and are routed recursively.

Strategy-2 recursion inequality (to verify):
   rho = sum_M d(u,v) <= 1 + sum_{annuli} rho(annulus).
But that telescopes badly unless each annulus is 'smaller'. The cosystole gives the base:
each tangential demand uv with shortest cert cycle length ell(uv)>=5 contributes;
the TOTAL tangential charge is bounded by the number of B-edges available to route, which
is controlled by Gamma = sum ell(uv)^2 <= N^2.

CONCRETE TEST of the master inequality I will assert:
   (MASTER)  m * rho^2  <=  Gamma_ell   where Gamma_ell := sum_{uv in M} d_ell(u,v)^2 / (per-edge...).
Actually the clean Cauchy form: rho = sum_M s_uv <= sqrt(m) * sqrt(sum_M s_uv^2) = sqrt(m * R2)
where R2 = sum_M d(u,v)^2 (normalized). So IF we prove
   (Q)  sum_{uv in M} d_ell(u,v)^2  <=  (N^2/25) * (1/m) * (sum_b ell_b)^2 * m = (N^2/25)(sum ell)^2 ...
let me just measure R2*m and compare with (N^2/25):
   rho <= sqrt(m*R2);  want rho <= max(1,N^2/(25m)).
   If m <= N^2/25: need sqrt(m*R2) <= N^2/(25m) i.e. m^3 R2 <= (N^2/25)^2, i.e. R2 <= (N^2/25)^2/m^3.
   If m >  N^2/25: need rho<=1, separate (weakly-bipartite) regime.
Measure R2 = sum_M (d/sum_ell)^2 and the target (N^2/25)^2/m^3.
"""
import math, heapq, itertools
import numpy as np
import sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
sys.path.insert(0, r'E:\Projects\ErdosProblems\attack3_scratch')
import flag_engine as fe
from laminar_recursion import adjset, maxcut, rho_mcf
from crossing_defect import dell_all, optimal_metric_lp

def analyze(N, A, name):
    adj = adjset(N, A); edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(min(u, v), max(u, v)) for (u, v) in edges if side[u] == side[v]]
    if not M: return
    adjB = [set() for _ in range(N)]; Be = []
    for (u, v) in edges:
        if side[u] != side[v]: adjB[u].add(v); adjB[v].add(u); Be.append((min(u, v), max(u, v)))
    m = len(M)
    rho = rho_mcf(N, adjB, M)
    # cosystole with UNIT ell (graph distance): ell(uv)=d_B(uv)+1
    unitell = {e: 1.0 for e in Be}
    Du = dell_all(N, adjB, unitell)
    Gamma = sum((Du[u][v]+1)**2 for (u, v) in M)
    # near-optimal metric R2
    ell = optimal_metric_lp(N, adjB, M, Be)
    D = dell_all(N, adjB, ell); se = sum(ell.values())
    R2 = sum((D[u][v]/se)**2 for (u, v) in M)
    target_R2 = (N*N/25.0)**2 / m**3 if m <= N*N/25.0 else None
    print(f"{name}: N={N} m={m} rho={rho:.4f} Gamma={Gamma}(<=N^2={N*N}) "
          f"R2={R2:.4f} m^3*R2={m**3*R2:.3f} (N^2/25)^2={(N*N/25.0)**2:.3f} "
          f"-> Cauchy-OK={m**3*R2 <= (N*N/25.0)**2 + 1e-6 if m<=N*N/25 else 'm>N^2/25(wb regime)'}")

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

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

analyze(*gpt_k23(), "K23-N13")
analyze(*petersen(), "Petersen")
analyze(*c5n(2), "C5[2]")
analyze(*c5n(3), "C5[3]")
print("DONE", flush=True)
