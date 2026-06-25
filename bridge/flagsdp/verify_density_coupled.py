#!/usr/bin/env python3
"""GPT Q36 (corrected): verify the DENSITY-COUPLED low-codegree penalty
   delta_2(G) <= floor(N/8)  =>  d_mono <= 2/25 - c*(2/5 - d_edge)  (+ o(1)),
i.e. the required slope  c_req(G) = (2/25 - d_mono)/(2/5 - d_edge)  is bounded BELOW by some c>0 over all
triangle-free low-codegree G with d_edge < 2/5. Empirical c = min c_req. GPT says c=1e-3 suffices (gives
>8e-5 band gap). Also tests GPT's counterexample family C5[m]+z (pendant): it sits at d_edge=2/5 exactly
(0/0), confirming the UNIFORM penalty fails only at the extremal density (out of band).
"""
import sys
import numpy as np
import flag_engine as fe

T = 2.0 / 25
EXTR = 2.0 / 5

def maxcut(n, A):
    adj = [[(A[u] >> v) & 1 for v in range(n)] for u in range(n)]
    best = 0
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        cut = sum(1 for u in range(n) for v in range(u + 1, n) if adj[u][v] and side[u] != side[v])
        best = max(best, cut)
    return best

def delta2(n, A):
    best = None
    for u in range(n):
        for v in range(u + 1, n):
            if (A[u] >> v) & 1:
                continue
            cod = bin(A[u] & A[v]).count("1")
            best = cod if best is None else min(best, cod)
    return best if best is not None else 10**9

def stats(n, A):
    e = sum(1 for u in range(n) for v in range(u + 1, n) if (A[u] >> v) & 1)
    beta = e - maxcut(n, A)
    return e, beta, 2.0 * beta / (n * n), e / (n * (n - 1) / 2)   # e, beta, d_mono, d_edge

def c5_blowup_plus_pendant(m):
    """C5[m] (parts 0..4, i~i+1) + vertex z adjacent to all of part 0. N=5m+1."""
    n = 5 * m + 1
    A = [0] * n
    def part(v): return v // m if v < 5 * m else -1
    for u in range(5 * m):
        for v in range(u + 1, 5 * m):
            pu, pv = part(u), part(v)
            if (pu - pv) % 5 in (1, 4):
                A[u] |= 1 << v; A[v] |= 1 << u
    z = 5 * m
    for u in range(0, m):     # z ~ part 0
        A[z] |= 1 << u; A[u] |= 1 << z
    return n, A

def run(N):
    states = fe.enumerate_graphs(N, triangle_free=True)
    thr = N // 8
    cmin = None; arg = None
    for (n, A) in states:
        e, beta, dm, de = stats(n, A)
        if e == 0 or de >= EXTR:
            continue
        if delta2(n, A) <= thr:
            creq = (T - dm) / (EXTR - de)
            if cmin is None or creq < cmin:
                cmin = creq; arg = (dm, de, e, beta, delta2(n, A))
    print(f"N={N} floor(N/8)={thr}: min c_req over low-codeg (d_edge<2/5) = {cmin:.5f}", flush=True)
    if arg:
        print(f"   argmin: d_mono={arg[0]:.4f} d_edge={arg[1]:.4f} e={arg[2]} beta={arg[3]} delta_2={arg[4]}", flush=True)
    return cmin

if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or [8, 9, 10, 11]
    cs = {}
    for N in Ns:
        cs[N] = run(N)
    print(f"SUMMARY empirical c (min slope) by N: { {k: round(v,5) for k,v in cs.items()} }", flush=True)
    print(f"  GPT needs c >= 1e-3 for an 8e-5 band gap; observed min = {min(cs.values()):.5f}", flush=True)
    print("--- GPT counterexample family C5[m]+pendant z (should be at d_edge=2/5 exactly) ---", flush=True)
    for m in (2, 3, 4):
        n, A = c5_blowup_plus_pendant(m)
        e, beta, dm, de = stats(n, A)
        print(f"  C5[{m}]+z: N={n} e={e} beta={beta} d_mono={dm:.5f} d_edge={de:.5f} delta_2={delta2(n,A)}", flush=True)
    print("DONE", flush=True)
