#!/usr/bin/env python3
"""
Solve ONE config of the cached N=6 4-color SDP (sparse). Run per-config in its own process so each
prints an independent result and an OOM in one does not lose the others.
Usage: python solve_n6_cached.py <config> [max_iters]
  config in {baseline, psdloc, weakloc}
"""
import sys, time, pickle, traceback
import numpy as np
import scipy.sparse as sp
import cvxpy as cp

CFG = sys.argv[1] if len(sys.argv) > 1 else "baseline"
MAXIT = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
VERB = (len(sys.argv) > 3 and sys.argv[3] in ("1", "v", "verbose"))
EPS = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-5
INDIRECT = (len(sys.argv) > 5 and sys.argv[5] in ("1", "indirect"))
t0 = time.time()
with open("n6_cache.pkl", "rb") as f:
    D = pickle.load(f)
ns = D["ns"]; band = D["band"]
dmono = D["dmono"]; dedge = D["dedge"]; basic = D["basic"]; weakloc = D["weakloc"]; gsw = D["gsw"]
print(f"[{CFG}] loaded cache ns={ns} band={band} [{time.time()-t0:.0f}s]", flush=True)

x = cp.Variable(ns, nonneg=True)
cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1]]
for (S, t) in D["moment"]:
    M = cp.reshape(S @ x, (t, t), order='C')
    cons.append(0.5*(M + M.T) >> 0)
for g in basic:
    cons.append(g @ x <= 0)
use_weak = (CFG == "weakloc")
use_psd = (CFG == "psdloc")
use_switch = CFG in ("psdloc", "weakloc")
if use_weak:
    for g in weakloc:
        cons.append(g @ x <= 0)
if use_psd:
    for (S, t, c, low) in D["loc"]:
        L = cp.reshape(S @ x, (t, t), order='C')
        cons.append(0.5*(L + L.T) >> 0)
if use_switch:
    cons.append(gsw @ x <= 0)
print(f"[{CFG}] built problem: {len(cons)} constraints [{time.time()-t0:.0f}s]; solving SCS (max_iters={MAXIT}) ...", flush=True)
prob = cp.Problem(cp.Maximize(dmono @ x), cons)
try:
    val = prob.solve(solver=cp.SCS, max_iters=MAXIT, verbose=VERB, eps_abs=EPS, eps_rel=EPS,
                     use_indirect=INDIRECT)
    print(f"[{CFG}] max d_mono = {val:.6f}  (beta/N^2 <= {val/2:.5f})  status={prob.status}  [{time.time()-t0:.0f}s]", flush=True)
except Exception as e:
    print(f"[{CFG}] SOLVE FAILED: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
print(f"[{CFG}] DONE [{time.time()-t0:.0f}s]", flush=True)
