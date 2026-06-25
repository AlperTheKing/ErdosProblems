#!/usr/bin/env python3
"""
Checkpointed warm-start SCS solve with LIVE progress (own flushed Python prints, bypassing SCS's
C-level output buffering). Each chunk runs CHUNK more SCS iterations from the warm start and prints
the current objective so the bound's descent is visible.
Usage: python solve_n6_progress.py <config> [chunk] [maxtot] [eps]
  config in {baseline, psdloc, weakloc}
"""
import sys, time, pickle, traceback
import numpy as np
import scipy.sparse as sp
import cvxpy as cp

CFG = sys.argv[1] if len(sys.argv) > 1 else "psdloc"
CHUNK = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
MAXTOT = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
EPS = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-6
t0 = time.time()
with open("n6_cache.pkl", "rb") as f:
    D = pickle.load(f)
ns = D["ns"]; band = D["band"]
dmono = D["dmono"]; dedge = D["dedge"]; basic = D["basic"]; weakloc = D["weakloc"]; gsw = D["gsw"]
print(f"[{CFG}] cache ns={ns} band={band} chunk={CHUNK} eps={EPS} [{time.time()-t0:.0f}s]", flush=True)

x = cp.Variable(ns, nonneg=True)
cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1]]
for (S, t) in D["moment"]:
    M = cp.reshape(S @ x, (t, t), order='C')
    cons.append(0.5*(M + M.T) >> 0)
for g in basic:
    cons.append(g @ x <= 0)
if CFG == "weakloc":
    for g in weakloc:
        cons.append(g @ x <= 0)
if CFG == "psdloc":
    for (S, t, c, low) in D["loc"]:
        L = cp.reshape(S @ x, (t, t), order='C')
        cons.append(0.5*(L + L.T) >> 0)
if CFG in ("psdloc", "weakloc"):
    cons.append(gsw @ x <= 0)
prob = cp.Problem(cp.Maximize(dmono @ x), cons)
print(f"[{CFG}] problem built: {len(cons)} constraints [{time.time()-t0:.0f}s]; checkpointed solve ...", flush=True)

total = 0; prev = None; stall = 0
while total < MAXTOT:
    try:
        val = prob.solve(solver=cp.SCS, max_iters=CHUNK, warm_start=True, eps_abs=EPS, eps_rel=EPS)
    except Exception as e:
        print(f"[{CFG}] SOLVE ERROR at ~{total}: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc(); break
    total += CHUNK
    v = float(val) if val is not None and np.isfinite(val) else float('nan')
    print(f"[{CFG}] ~{total:6d} iters | {time.time()-t0:5.0f}s | d_mono = {v:.6f}  (beta/N^2 <= {v/2:.5f})  status={prob.status}", flush=True)
    if prob.status in ("optimal",):
        print(f"[{CFG}] CONVERGED (optimal) at ~{total} iters", flush=True); break
    if prev is not None and abs(v - prev) < 1e-6:
        stall += 1
        if stall >= 4:
            print(f"[{CFG}] objective stalled ({v:.6f}); treating as converged", flush=True); break
    else:
        stall = 0
    prev = v
print(f"[{CFG}] FINAL d_mono = {v:.6f}  (beta/N^2 <= {v/2:.5f})  [{time.time()-t0:.0f}s] DONE", flush=True)
