#!/usr/bin/env python3
"""Exact (Fractions) verification of the C5[q] hand-computation of T_uniform and the
'equality iff C5[q]' rigidity, plus a census probe of the SLACK structure K - max_v T_uniform.

T_uniform(v) = sum_{f in M} ell(f) * (#shortest cycles of f through v)/(#shortest cycles of f).
K = N + (N^2 - Gamma).  Claim U: max_v T_uniform(v) <= K, equality iff C5[q]-type (Gamma=N^2).
"""
import subprocess
from collections import deque
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def adj_of(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    return adj

def T_uniform(n, adj, side, M, ell):
    """Exact T_uniform per vertex. A 'shortest cycle' of bad edge f=(u,v) is a shortest
    B-geodesic from u to v (length ell-1) closed by the bad edge f. Vertices on that cycle =
    vertices on the geodesic path (which includes u and v)."""
    T = [F(0) for _ in range(n)]
    detail = []
    for (u, v) in M:
        Ps = geos(adj, side, u, v)
        nf = len(Ps)
        h = ell[(u, v)]              # = (length of geodesic)+1 = cycle length
        share = F(h, nf)            # ell(f) / (#shortest cycles)
        cnt_through = [0]*n
        for P in Ps:
            for w in set(P):
                cnt_through[w] += 1
        for w in range(n):
            T[w] += share * cnt_through[w]
        detail.append((u, v, h, nf))
    return T, detail

def analyze(n, E, label=""):
    adj = adj_of(n, E)
    r = gmin(n, adj, maxcut_all(n, adj))
    if r is None:
        return None
    side, G, M, ell = r
    T, detail = T_uniform(n, adj, side, M, ell)
    K = n + (n*n - G)
    maxT = max(T)
    return dict(n=n, Gamma=G, K=K, maxT=maxT, T=T, side=side, M=M, ell=ell,
               detail=detail, tight=(maxT == K), gamma_full=(G == n*n))

print("="*78)
print("PART A: C5[q] EXACT hand-computation (Fractions). Expect T(v)=N for ALL v, K=N.")
print("="*78)
for q in (1, 2, 3, 4, 5):
    n, E = blow(q)
    d = analyze(n, E, f"C5[{q}]")
    Tset = set(d['T'])
    print(f"C5[{q}]: N={n}  Gamma={d['Gamma']} (N^2={n*n})  K={d['K']}  "
          f"T-values={sorted(str(x) for x in Tset)}  maxT={d['maxT']}  "
          f"equality(maxT==K=N): {d['maxT']==d['K']==n}")
    # show the per-bad-edge detail for q small
    if q <= 2:
        # count bad edges and #geodesics per
        from collections import Counter
        cc = Counter((h, nf) for (_,_,h,nf) in d['detail'])
        print(f"     #bad edges |M|={len(d['M'])};  (ell, #shortest-cycles) multiset: {dict(cc)}")
        print(f"     #shortest 5-cycles through a fixed vertex check below.")

print()
print("="*78)
print("PART B: C5[q] structural counts (hand-formulas) cross-checked against code")
print("="*78)
for q in (1,2,3,4,5,6):
    n, E = blow(q)
    adj = adj_of(n, E)
    r = gmin(n, adj, maxcut_all(n, adj)) if n <= 16 else None
    if r is None:
        # n too large for brute maxcut; build the canonical C5[q] cut by hand:
        # parts 0..4 of size q; the gamma-min connected-B cut for C5[q] —
        # we instead only report the closed-form prediction
        print(f"C5[{q}]: N={n} (brute maxcut skipped n>16) predicted T(v)=N={n}, K=N={n}")
        continue
    side, G, M, ell = r
    # In C5[q]: |M| = number of monochromatic edges = ?; each bad edge has ell=5,
    # each has some number nf of shortest 5-cycles. Report exact:
    from collections import Counter
    T, detail = T_uniform(n, adj, side, M, ell)
    ells = Counter(h for (_,_,h,_) in detail)
    print(f"C5[{q}]: N={n} |M|={len(M)} ell-multiset={dict(ells)} "
          f"sum ell^2=Gamma={G}=N^2? {G==n*n}  T-uniform all == N? {all(t==n for t in T)}")

print()
print("="*78)
print("PART C: CENSUS N=5..11 — exact maxT, K, SLACK=K-maxT (Fractions). Equality iff Gamma=N^2.")
print("="*78)
import sys
maxN = int(sys.argv[1]) if len(sys.argv) > 1 else 10
for nn in range(5, maxN+1):
    out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
    viol = 0; tight = 0; tot = 0
    tight_gammafull = 0; tight_other = []
    worst_over = F(-10**9)
    min_slack_pos = None
    for g6 in out:
        n, E = dec(g6)
        d = analyze(n, E)
        if d is None:
            continue
        tot += 1
        slack = d['K'] - d['maxT']
        if slack < 0:
            viol += 1
            print(f"  *** VIOLATION g6={g6} N={d['n']} Gamma={d['Gamma']} K={d['K']} maxT={d['maxT']} slack={slack}")
        if slack > worst_over:
            worst_over = slack  # actually track min slack
        if d['maxT'] == d['K']:
            tight += 1
            if d['gamma_full']:
                tight_gammafull += 1
            else:
                tight_other.append(g6)
        else:
            if min_slack_pos is None or slack < min_slack_pos[0]:
                min_slack_pos = (slack, g6)
    msg = (f"  N={nn}: configs={tot} viol={viol} tight(maxT==K)={tight} "
           f"[of which Gamma=N^2: {tight_gammafull}; tight-but-Gamma<N^2: {len(tight_other)}]")
    print(msg, flush=True)
    if tight_other:
        print(f"     !!! tight-but-not-gamma-full g6 list: {tight_other[:20]}")
    if min_slack_pos:
        print(f"     smallest POSITIVE slack among non-tight: {min_slack_pos[0]} (g6={min_slack_pos[1]})")
