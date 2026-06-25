#!/usr/bin/env python3
"""
Driver: 2-colored flag SDP for d_mono (beta density) WITH max-cut switching constraints.
Compares: band-only baseline -> +0-root switching -> +1-root SW1.  Target d_mono <= 2/25 = 0.08.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import flag_engine_col as fc
import flag_sdp_col as fs
import flag_switch as sw


def run(N, kmax=2):
    print(f"\n===== N={N} =====")
    t0 = time.time()
    states = fc.enumerate_colored(N, triangle_free=True)
    tf = fs.colored_types(N, kmax=kmax)
    print(f"  states={len(states)}  types={len(tf)}  (build {time.time()-t0:.1f}s)")
    band = (0.2486, 0.32)
    # baseline (band only)
    v0, st0, _, _ = fs.solve_primal(N, tf, band=band, extra_lin=None, verbose=False)
    print(f"  band only:                 max d_mono = {v0:.6f}  ({st0})")
    # + 0-root switching
    sw0 = sw.all_switching(states, include_sw1=False)
    v1, st1, _, _ = fs.solve_primal(N, tf, band=band, extra_lin=sw0, verbose=False)
    print(f"  + 0-root switching:        max d_mono = {v1:.6f}  ({st1})")
    # + 1-root SW1
    swA = sw.all_switching(states, include_sw1=True)
    v2, st2, _, _ = fs.solve_primal(N, tf, band=band, extra_lin=swA, verbose=False)
    print(f"  + 0-root & 1-root (SW1):   max d_mono = {v2:.6f}  ({st2})   target<=0.08")
    print(f"  [{time.time()-t0:.1f}s total]")
    return v2


if __name__ == "__main__":
    for N in (5, 6):
        run(N, kmax=2)
    print("\nDONE")
