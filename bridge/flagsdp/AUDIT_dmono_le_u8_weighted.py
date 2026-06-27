#!/usr/bin/env python3
"""ADVERSARIAL probe (read-only, new file): try to BREAK d_mono(W) <= U_8(W) on NON-UNIFORM blow-ups.
A real triangle-free graphon = a step-graphon = a vertex-weighted blow-up of a finite tri-free template T with
weights alpha (a probability vector). d_mono and U_8 are both well-defined for the WEIGHTED blow-up. The C5
extremal and the project's past FALSE closures lived at UNBALANCED weightings, so we hammer weighted C5/C7/Petersen
and random weighted small templates, looking for ANY alpha with d_mono(W) > U_8(W).

d_mono(weighted T, alpha) = 2*beta/N^2 normalized: for a step graphon it is
    d_mono = min over 2-colorings sigma of T of  sum_{uv edge} alpha_u alpha_v [sigma_u==sigma_v]   (monochromatic edge mass)
i.e. = t(K2) - maxcut_weighted(T,alpha).  U8(m,T,alpha) is the order-10 8-anchor envelope (imported).
"""
import sys, time, itertools, random
from fractions import Fraction as F
from u8_max_check import U8, popcount

def edges_of(m, T):
    return [(u, w) for u in range(m) for w in range(u+1, m) if (T[u] >> w) & 1]

def dmono_weighted(m, T, alpha):
    """min monochromatic edge mass over 2-colorings = t(K2) - weighted maxcut. Exact in floats."""
    E = edges_of(m, T)
    tK2 = sum(alpha[u]*alpha[w] for (u, w) in E)  # each undirected edge once; t(K2)=2*this in ordered, but
    # d_mono def in helpers uses 2*(e-maxcut)/n^2 on the *unweighted* graph; for the step graphon the matching
    # quantity is 2 * min_sigma sum_{u<w edge} a_u a_w [same color].  Keep the factor 2 to match U8 edge-units.
    best_cut = 0.0
    for mask in range(1 << (m-1)):
        cut = 0.0
        for (u, w) in E:
            if ((mask >> u) & 1) != ((mask >> w) & 1):
                cut += alpha[u]*alpha[w]
        if cut > best_cut: best_cut = cut
    return 2.0*(tK2 - best_cut)

def cyc(m):
    A = [0]*m
    for i in range(m): A[i] |= 1 << ((i+1) % m); A[i] |= 1 << ((i-1) % m)
    return A
def petersen():
    A=[0]*10
    def e(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in range(5): e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return A

def probe(name, m, T, alpha):
    a = [float(x) for x in alpha]; s = sum(a); a = [x/s for x in a]
    dm = dmono_weighted(m, T, a)
    u8 = float(U8(m, T, [F(int(round(x*10**6)), 10**6) for x in a]))
    gap = u8 - dm
    flag = "  <<< VIOLATION (d_mono > U_8)!" if gap < -1e-9 else ""
    return name, dm, u8, gap, flag, a

def main():
    random.seed(7)
    results = []
    worst = 1e9; worst_info = None
    # 1. uniform extremals (sanity)
    for (nm, m, T) in [("C5", 5, cyc(5)), ("C7", 7, cyc(7)), ("Petersen", 10, petersen())]:
        r = probe(nm+"(unif)", m, T, [1.0]*m); results.append(r)
    # 2. weighted C5: sweep perturbations of uniform + extreme unbalanced
    for trial in range(200):
        a = [1.0 + 0.6*random.uniform(-1, 1) for _ in range(5)]
        results.append(probe(f"C5w{trial}", 5, cyc(5), a))
    # heavy single-vertex / opposite-pair unbalance on C5
    for w in [2, 4, 8, 16, 50]:
        results.append(probe(f"C5 vtx0={w}", 5, cyc(5), [w, 1, 1, 1, 1]))
        results.append(probe(f"C5 v0=v2={w}", 5, cyc(5), [w, 1, w, 1, 1]))
        results.append(probe(f"C5 v0=v1={w}", 5, cyc(5), [w, w, 1, 1, 1]))
    # 3. weighted C7
    for trial in range(120):
        a = [1.0 + 0.7*random.uniform(-1, 1) for _ in range(7)]
        results.append(probe(f"C7w{trial}", 7, cyc(7), a))
    for r in results:
        nm, dm, u8, gap, flag, a = r
        if gap < worst: worst = gap; worst_info = r
        if flag:
            print(f"{nm:14s} d_mono={dm:.6f} U_8={u8:.6f} gap={gap:+.3e}{flag} alpha={['%.3f'%x for x in a]}", flush=True)
    nm, dm, u8, gap, flag, a = worst_info
    print(f"\n=== WEIGHTED-blowup adversarial probe: {len(results)} step-graphons tested ===", flush=True)
    print(f"  WORST gap (U_8 - d_mono) = {worst:+.6e}", flush=True)
    print(f"    at {nm}: d_mono={dm:.6f} U_8={u8:.6f} alpha={['%.4f'%x for x in a]}", flush=True)
    nviol = sum(1 for r in results if r[3] < -1e-9)
    print(f"  violations (d_mono > U_8): {nviol}", flush=True)
    print(f"  d_mono <= U_8 holds on all weighted blow-ups tested ? {worst >= -1e-9}", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__": main()
