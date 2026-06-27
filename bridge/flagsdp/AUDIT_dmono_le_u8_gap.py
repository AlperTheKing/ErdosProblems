#!/usr/bin/env python3
"""ADVERSARIAL AUDIT (read-only, new file): is d_mono(W_G) <= U_8(W_G) for EVERY real triangle-free graph G?
Imports U8, dmono, tri_free from u8_max_check (the audited helpers) and ALSO recomputes d_mono with a fully
independent brute-force maxcut to cross-validate the helper. For every tri-free graph on n=5,6,7 (and n=8 if asked)
it reports the gap g = U_8 - d_mono. A single g < 0 on a REAL graph = the d_mono<=U_8 reduction is UNSOUND.
Prints: worst (smallest) gap, the argmin graph, any negative-gap graphs, and a per-graph d_mono cross-check.
"""
import sys, time
from u8_max_check import U8, dmono, tri_free, maxcut_graph
from compute_U8 import popcount
import flag_engine as fe

def dmono_indep(n, A):
    """Fully independent d_mono: count edges directly, brute maxcut over all 2^(n-1) colorings."""
    e = 0
    for v in range(n):
        for w in range(v+1, n):
            if (A[v] >> w) & 1: e += 1
    best = 0
    for mask in range(1 << (n-1)):
        c = 0
        for v in range(n):
            for w in range(v+1, n):
                if (A[v] >> w) & 1 and ((mask >> v) & 1) != ((mask >> w) & 1):
                    c += 1
        if c > best: best = c
    return 2*(e - best)/(n*n)

def main():
    ns = [int(x) for x in sys.argv[1:]] or [5, 6, 7]
    TWO25 = 2.0/25.0
    worst = 1e9; argw = None
    worst_u8mc = 1e9  # also track worst (2/25 - d_mono) sanity (NOT a soundness gate, just info)
    neg = []
    dm_mismatch = 0
    n_total = 0
    for nn in ns:
        gs = fe.enumerate_graphs(nn, triangle_free=True)
        t0 = time.time(); wn = 1e9; wnA = None
        for (k, A) in gs:
            assert tri_free(nn, A), f"enumerate returned non-tri-free n={nn} A={A}"
            dm = dmono(nn, A)
            dm2 = dmono_indep(nn, A)
            if abs(dm - dm2) > 1e-12:
                dm_mismatch += 1
                print(f"  D_MONO MISMATCH n={nn} helper={dm} indep={dm2} A={A}", flush=True)
            u8 = float(U8(nn, A))
            g = u8 - dm
            n_total += 1
            if g < wn: wn = g; wnA = A
            if g < worst: worst = g; argw = (nn, A, u8, dm)
            if g < -1e-9: neg.append((nn, A, u8, dm, g))
        print(f"n={nn}: {len(gs)} tri-free, min(U_8 - d_mono) = {wn:+.6e}  argmin A={wnA} [{time.time()-t0:.0f}s]", flush=True)
    print(f"\n=== AUDIT d_mono <= U_8 ===", flush=True)
    print(f"  graphs tested = {n_total}; d_mono helper-vs-independent mismatches = {dm_mismatch}", flush=True)
    if argw:
        nn, A, u8, dm = argw
        print(f"  WORST (smallest) gap U_8 - d_mono = {worst:+.6e}", flush=True)
        print(f"    at n={nn} A={A}  (U_8={u8:.6f}, d_mono={dm:.6f})", flush=True)
    print(f"  negative-gap (UNSOUND) graphs: {len(neg)}", flush=True)
    for (nn, A, u8, dm, g) in neg[:10]:
        print(f"    VIOLATION n={nn} gap={g:+.3e} U_8={u8:.6f} d_mono={dm:.6f} A={A}", flush=True)
    print(f"  d_mono <= U_8 SOUND for all tested ? {worst >= -1e-9 and dm_mismatch == 0}", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__": main()
