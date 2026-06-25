#!/usr/bin/env python3
"""GPT Q35 (Pick iii): VERIFY the low-codegree penalty inequality before attempting a proof.
Claim:  triangle-free G on N vtx with delta_2(G) <= floor(N/8)  =>  d_mono = 2*beta/N^2 <= 2/25 - gamma.
delta_2 = min over NON-ADJACENT pairs {u,v} of codegree |N(u) cap N(v)| (edges have codeg 0 in tri-free).
Brute over all triangle-free G (enumerate_graphs) for N=8..11; report max d_mono among delta_2<=floor(N/8),
and gamma = 2/25 - that max. Also report the OVERALL max d_mono (sanity, should approach C5 0.08 only at
high codegree). Flags any low-codegree graph with d_mono close to 2/25 (would break the route).
"""
import sys
import numpy as np
import flag_engine as fe

def maxcut(n, A):
    adj = [[(A[u] >> v) & 1 for v in range(n)] for u in range(n)]
    best = 0
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        cut = sum(1 for u in range(n) for v in range(u + 1, n) if adj[u][v] and side[u] != side[v])
        if cut > best:
            best = cut
    return best

def delta2(n, A):
    """min codegree over non-adjacent unordered pairs (incl non-edges only)."""
    best = None
    for u in range(n):
        for v in range(u + 1, n):
            if (A[u] >> v) & 1:
                continue                       # skip edges (codeg 0 in triangle-free)
            cod = bin(A[u] & A[v]).count("1")  # common neighbors
            best = cod if best is None else min(best, cod)
    return best if best is not None else 0     # complete graph: no non-edge (irrelevant, not tri-free for n>2)

def run(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    thr = N // 8
    t = 2.0 / 25
    max_low = -1.0; arg_low = None; max_all = -1.0; arg_all = None
    near = []
    for (n, A) in states:
        e = sum(1 for u in range(n) for v in range(u + 1, n) if (A[u] >> v) & 1)
        if e == 0:
            continue
        beta = e - maxcut(n, A)
        dm = 2.0 * beta / (n * n)
        if dm > max_all:
            max_all = dm; arg_all = A
        d2 = delta2(n, A)
        if d2 <= thr:
            if dm > max_low:
                max_low = dm; arg_low = (A, d2, e, beta)
            if dm > t - 0.01:
                near.append((dm, d2, e, beta, A))
    gamma = t - max_low
    print(f"N={N}: floor(N/8)={thr}, {len(states)} tri-free graphs", flush=True)
    print(f"  OVERALL max d_mono = {max_all:.5f} (target 2/25={t:.5f})", flush=True)
    print(f"  LOW-codeg (delta_2<={thr}) max d_mono = {max_low:.5f}  =>  gamma = 2/25 - that = {gamma:+.5f}", flush=True)
    if gamma > 0:
        print(f"  INEQUALITY HOLDS at N={N}: low-codeg d_mono <= 2/25 - {gamma:.5f}", flush=True)
    else:
        print(f"  *** INEQUALITY FAILS at N={N}: a low-codeg graph has d_mono={max_low:.5f} >= 2/25 ***", flush=True)
        print(f"      witness delta_2={arg_low[1]} e={arg_low[2]} beta={arg_low[3]}", flush=True)
    if near:
        print(f"  {len(near)} low-codeg graphs with d_mono within 0.01 of 2/25 (watch):", flush=True)
        for (dm, d2, e, beta, A) in near[:5]:
            print(f"    d_mono={dm:.5f} delta_2={d2} e={e} beta={beta}", flush=True)
    return gamma

if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or [8, 9, 10, 11]
    gammas = {}
    for N in Ns:
        gammas[N] = run(N)
    print(f"SUMMARY gamma by N: {gammas}", flush=True)
    print("DONE", flush=True)
