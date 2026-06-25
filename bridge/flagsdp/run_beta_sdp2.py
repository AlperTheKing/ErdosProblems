#!/usr/bin/env python3
"""Driver v2: full fractional rooted-switch families (p in {0,1/2,1}) for k=0,1 roots."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import flag_engine_col as fc
import flag_sdp_col as fs
import flag_switch as sw

def run(N, kmax_roots=1, kmax_types=2):
    print(f"\n===== N={N} =====")
    t0 = time.time()
    states = fc.enumerate_colored(N, triangle_free=True)
    tf = fs.colored_types(N, kmax=kmax_types)
    print(f"  states={len(states)} types={len(tf)}  (build {time.time()-t0:.1f}s)")
    band = (0.2486, 0.32)
    cum = []
    import flag_engine_col as fcc
    for kr in range(0, kmax_roots+1):
        ts = time.time()
        # build only the k=kr layer, accumulate
        layer = []
        seen = set(tuple(__import__('numpy').round(v,6)) for v in cum)
        for (kk, A, col) in fcc.enumerate_colored(kr, triangle_free=True):
            pv = (0.0, 0.5, 1.0) if kr <= 1 else (0.0, 1.0)
            for v in sw.gen_rooted_switches(states, (kr, A, tuple(col)), pvals=pv):
                key = tuple(__import__('numpy').round(v,6))
                if key not in seen and any(abs(x)>1e-9 for x in v):
                    seen.add(key); layer.append(v)
        cum = cum + layer
        v, st, _, _ = fs.solve_primal(N, tf, band=band, extra_lin=cum, verbose=False)
        print(f"  switches k<= {kr}: #cons={len(cum):5d}  max d_mono = {v:.6f}  beta/N^2<= {v/2:.5f} "
              f"(target 0.04={1/25:.4f})  [{time.time()-ts:.1f}s] {st}")
    print(f"  [{time.time()-t0:.1f}s total]")

if __name__ == "__main__":
    import sys
    NK = [(5,2),(6,2)]
    if len(sys.argv)>1: NK=[(int(sys.argv[1]), int(sys.argv[2]))]
    for (N,kr) in NK:
        run(N, kmax_roots=kr)
    print("\nDONE")
