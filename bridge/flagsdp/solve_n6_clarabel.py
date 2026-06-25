#!/usr/bin/env python3
"""
Solve the cached N=6 SDP with CLARABEL (interior-point) instead of SCS (first-order).
Interior-point converges in ~tens of iterations (vs SCS thousands), is more accurate, and its
KKT factorization is BLAS-heavy so it actually uses many threads. Likely far faster here.
Usage: python solve_n6_clarabel.py <config>
"""
import sys, time, pickle
import numpy as np
import scipy.sparse as sp
import cvxpy as cp

CFG = sys.argv[1] if len(sys.argv) > 1 else "psdloc"
t0 = time.time()
with open("n6_cache.pkl", "rb") as f:
    D = pickle.load(f)
ns = D["ns"]; band = D["band"]
dmono = D["dmono"]; dedge = D["dedge"]; basic = D["basic"]; weakloc = D["weakloc"]; gsw = D["gsw"]
print(f"[{CFG}/clarabel] cache ns={ns} band={band} [{time.time()-t0:.0f}s]", flush=True)

x = cp.Variable(ns, nonneg=True)
cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1]]
for (S, t) in D["moment"]:
    M = cp.reshape(S @ x, (t, t), order='C'); cons.append(0.5*(M + M.T) >> 0)
for g in basic:
    cons.append(g @ x <= 0)
if CFG == "weakloc":
    for g in weakloc: cons.append(g @ x <= 0)
if CFG == "psdloc":
    for (S, t, c, low) in D["loc"]:
        L = cp.reshape(S @ x, (t, t), order='C'); cons.append(0.5*(L + L.T) >> 0)
if CFG in ("psdloc", "weakloc"):
    cons.append(gsw @ x <= 0)
prob = cp.Problem(cp.Maximize(dmono @ x), cons)
print(f"[{CFG}/clarabel] built {len(cons)} constraints [{time.time()-t0:.0f}s]; solving CLARABEL (verbose) ...", flush=True)
try:
    val = prob.solve(solver=cp.CLARABEL, verbose=True)
    print(f"[{CFG}/clarabel] max d_mono = {val:.6f}  (beta/N^2 <= {val/2:.5f})  status={prob.status}  [{time.time()-t0:.0f}s]", flush=True)
except Exception as e:
    import traceback
    print(f"[{CFG}/clarabel] FAILED: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
print(f"[{CFG}/clarabel] DONE [{time.time()-t0:.0f}s]", flush=True)
