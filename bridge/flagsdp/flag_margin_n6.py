#!/usr/bin/env python3
"""
N=6 margin-color SDP driver (corrected band INCLUDING the C5[n] extremal at d_edge=0.40).
Builds the expensive P_sigma matrices + constraint vectors ONCE, then solves several
(band, localizers, switch) configs reusing them. Decisive test: at the extremal band,
does the margin-conditioned switch pull max d_mono down toward the sharp 0.08?
"""
import sys, time
import numpy as np
import cvxpy as cp
import flag_engine_kcol as kc
import flag_sdp_col as fs
import flag_margin_sdp as ms

t0 = time.time()
N = 6
print(f"=== N={N} margin SDP (single build + reuse) ===", flush=True)
print("enumerating states + types ...", flush=True)
states = kc.enumerate_kcolored(N, 4, triangle_free=True)
ns = len(states)
tf = ms.kcolored_types(N, kmax=2)
print(f"  states={ns}  types={len(tf)}  [{time.time()-t0:.0f}s]", flush=True)

print("building constraint vectors ...", flush=True)
dmono = ms.d_mono_vec(states); dedge = ms.d_edge_vec(states)
basic = [ms.side_sw0_vec(states, dmono, dedge), ms.side_sw1_vec(states, 0), ms.side_sw1_vec(states, 1)]
locs = ms.localizer_vecs(states)
gsw = ms.margin_switch_vec(states)
print(f"  done  [{time.time()-t0:.0f}s]", flush=True)

print("building P_sigma matrices (the slow part) ...", flush=True)
Pflats = []
for ti, (sigma, flags) in enumerate(tf):
    if len(flags) < 2:
        continue
    mats = fs.P_sigma_col(states, sigma, flags)
    t = len(flags)
    Pflats.append((np.stack([m.ravel() for m in mats], axis=1), t))
    if (ti+1) % 5 == 0:
        print(f"   type {ti+1}/{len(tf)}  [{time.time()-t0:.0f}s]", flush=True)
print(f"  built {len(Pflats)} PSD blocks  [{time.time()-t0:.0f}s]", flush=True)


def solve_cfg(band, use_loc, use_switch, tag):
    ts = time.time()
    x = cp.Variable(ns, nonneg=True)
    cons = [cp.sum(x) == 1]
    if band:
        cons += [dedge @ x >= band[0], dedge @ x <= band[1]]
    for (Pflat, t) in Pflats:
        M = cp.reshape(Pflat @ x, (t, t), order='C')
        cons.append(0.5*(M + M.T) >> 0)
    for g in basic:
        cons.append(g @ x <= 0)
    nl = nsw = 0
    if use_loc:
        for g in locs:
            cons.append(g @ x <= 0); nl += 1
    if use_switch:
        cons.append(gsw @ x <= 0); nsw = 1
    prob = cp.Problem(cp.Maximize(dmono @ x), cons)
    val = prob.solve(solver=cp.SCS, max_iters=60000)
    print(f"  [{tag}] band={band} loc={nl} sw={nsw} | max d_mono={val:.6f} "
          f"(beta/N^2<={val/2:.5f}) [{time.time()-ts:.0f}s] {prob.status}", flush=True)
    return val


print("\n--- configs ---", flush=True)
# Extremal band (contains C5[n] at d_edge=0.40): the decisive sharp-point test
solve_cfg((0.34, 0.46), False, False, "extremal-band baseline (basic only)")
solve_cfg((0.34, 0.46), True,  False, "extremal-band +localizers")
solve_cfg((0.34, 0.46), True,  True,  "extremal-band +loc+MARGIN-SWITCH")
# Wide band (whole binding region) full machinery
solve_cfg((0.25, 0.46), True,  True,  "wide-band +loc+MARGIN-SWITCH")
# Old band, full machinery: does the margin switch break the 0.10 plateau there?
solve_cfg((0.2486, 0.32), True, True, "old-band +loc+MARGIN-SWITCH (plateau-break check)")
print(f"DONE [{time.time()-t0:.0f}s]", flush=True)
