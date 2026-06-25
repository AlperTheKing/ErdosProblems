#!/usr/bin/env python3
"""
N=6 margin SDP with PSD-LIFTED localizers, OLD band (0.2486,0.32) [the correct medium-density band].
Compares, reusing one expensive build:
  (1) baseline: PSD moment matrices + edge band + basic side switches only
  (2) + weak averaged-scalar localizers + margin switch          (the old Phase F/G)
  (3) + PSD-lifted localizers + margin switch                    (Phase F2 — the audit's fix)
Decisive question: does (3) break max d_mono below 0.09375 toward the in-band-sufficient 0.08?
"""
import sys, time
import numpy as np
import cvxpy as cp
import flag_engine_kcol as kc
import flag_sdp_col as fs
import flag_margin_sdp as ms
import flag_psd_localizer as pl

t0 = time.time()
N = 6
BAND = (0.2486, 0.32)
TAU = 1.0/8
SMAX_LOC = int(sys.argv[1]) if len(sys.argv) > 1 else 1   # PSD-localizer flag order (1 or 2)
print(f"=== N={N} margin SDP + PSD localizers (band={BAND}, tau={TAU}, smax_loc={SMAX_LOC}) ===", flush=True)
states = kc.enumerate_kcolored(N, 4, triangle_free=True)
ns = len(states)
tf = ms.kcolored_types(N, kmax=2)
print(f"  states={ns} types={len(tf)} [{time.time()-t0:.0f}s]", flush=True)

dmono = ms.d_mono_vec(states); dedge = ms.d_edge_vec(states)
basic = [ms.side_sw0_vec(states, dmono, dedge), ms.side_sw1_vec(states, 0), ms.side_sw1_vec(states, 1)]
weakloc = ms.localizer_vecs(states)
gsw = ms.margin_switch_vec(states)

print("building P_sigma moment matrices ...", flush=True)
Pflats = []
for (sigma, flags) in tf:
    if len(flags) < 2: continue
    mats = fs.P_sigma_col(states, sigma, flags)
    Pflats.append((np.stack([m.ravel() for m in mats], axis=1), len(flags)))
print(f"  {len(Pflats)} moment blocks [{time.time()-t0:.0f}s]; building PSD localizer blocks ...", flush=True)
locblocks = pl.build_all_localizers(states, TAU, smax=SMAX_LOC)
Lflats = []
for (c, low, flags, mats) in locblocks:
    Lflats.append((np.stack([m.ravel() for m in mats], axis=1), len(flags), c, low))
print(f"  {len(Lflats)} PSD localizer blocks [{time.time()-t0:.0f}s]", flush=True)


def solve_cfg(use_weakloc, use_psdloc, use_switch, tag):
    ts = time.time()
    x = cp.Variable(ns, nonneg=True)
    cons = [cp.sum(x) == 1, dedge @ x >= BAND[0], dedge @ x <= BAND[1]]
    for (Pflat, t) in Pflats:
        M = cp.reshape(Pflat @ x, (t, t), order='C')
        cons.append(0.5*(M + M.T) >> 0)
    for g in basic:
        cons.append(g @ x <= 0)
    if use_weakloc:
        for g in weakloc:
            cons.append(g @ x <= 0)
    if use_psdloc:
        for (Lflat, t, c, low) in Lflats:
            L = cp.reshape(Lflat @ x, (t, t), order='C')
            cons.append(0.5*(L + L.T) >> 0)
    if use_switch:
        cons.append(gsw @ x <= 0)
    prob = cp.Problem(cp.Maximize(dmono @ x), cons)
    val = prob.solve(solver=cp.SCS, max_iters=80000)
    print(f"  [{tag}] max d_mono={val:.6f} (beta/N^2<={val/2:.5f}) [{time.time()-ts:.0f}s] {prob.status}", flush=True)
    return val

print("\n--- configs (OLD band; target break <0.09375 toward 0.08) ---", flush=True)
solve_cfg(False, False, False, "1 baseline (band+moments+basic-switch)")
solve_cfg(False, True,  True,  "3 +PSD-loc +margin-switch  (Phase F2 -- DECISIVE)")
solve_cfg(True,  False, True,  "2 +weak-loc +margin-switch (old Phase F/G, for contrast)")
print(f"DONE [{time.time()-t0:.0f}s]", flush=True)
