#!/usr/bin/env python3
"""
LIVE-progress N=6 solve via the scs persistent workspace: factorize ONCE, then run the ADMM in
CHUNK-iteration bursts with warm start, printing the current bound + residuals each burst (own
flushed prints, no SCS C-buffering, no per-chunk re-factorization).
d_mono estimate = -pobj (cvxpy FlipObjective: SCS minimizes -dmono; offset 0 for this linear obj).
Validated by running config=baseline -> must trend to the known 0.125.
Usage: python solve_n6_persist.py <config> [chunk] [maxtot] [eps]
"""
import sys, time, pickle
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
import scs

CFG = sys.argv[1] if len(sys.argv) > 1 else "psdloc"
CHUNK = int(sys.argv[2]) if len(sys.argv) > 2 else 300
MAXTOT = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
EPS = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-5
t0 = time.time()
with open("n6_cache.pkl", "rb") as f:
    D = pickle.load(f)
ns = D["ns"]; band = D["band"]
dmono = D["dmono"]; dedge = D["dedge"]; basic = D["basic"]; weakloc = D["weakloc"]; gsw = D["gsw"]
print(f"[{CFG}] cache ns={ns} band={band} chunk={CHUNK} eps={EPS} [{time.time()-t0:.0f}s]", flush=True)

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

data, chain, inv_data = prob.get_problem_data(cp.SCS)
A = data['A']; b = data['b']; cc = data['c']; dims = data['dims']
cone = {}
if getattr(dims, 'zero', 0): cone['z'] = int(dims.zero)
if getattr(dims, 'nonneg', 0): cone['l'] = int(dims.nonneg)
if getattr(dims, 'soc', None): cone['q'] = [int(v) for v in dims.soc]
if getattr(dims, 'psd', None): cone['s'] = [int(v) for v in dims.psd]
if getattr(dims, 'exp', 0): cone['ep'] = int(dims.exp)
print(f"[{CFG}] conic form: vars={A.shape[1]} rows={A.shape[0]} nnz(A)={A.nnz} "
      f"cone(z={cone.get('z',0)},l={cone.get('l',0)},#psd={len(cone.get('s',[]))}) [{time.time()-t0:.0f}s]; factorizing once ...", flush=True)

solver = scs.SCS({'A': A, 'b': b, 'c': cc}, cone, max_iters=CHUNK, eps_abs=EPS, eps_rel=EPS,
                 verbose=False, acceleration_lookback=0)
sol = solver.solve()
total = CHUNK
print(f"[{CFG}] factorized + first burst [{time.time()-t0:.0f}s]", flush=True)
while True:
    info = sol['info']
    pobj = info.get('pobj', float('nan'))
    dmest = -pobj
    print(f"[{CFG}] ~{total:6d} it | {time.time()-t0:5.0f}s | d_mono~{dmest:.6f} (beta/N^2~{dmest/2:.5f}) | "
          f"res_pri={info.get('res_pri',float('nan')):.1e} res_dual={info.get('res_dual',float('nan')):.1e} "
          f"gap={info.get('gap',float('nan')):.1e} st={info.get('status','?')}", flush=True)
    st = str(info.get('status', ''))
    if 'solved' in st.lower() or total >= MAXTOT:
        break
    sol = solver.solve(warm_start=True, x=sol['x'], y=sol['y'], s=sol['s'])
    total += CHUNK
print(f"[{CFG}] FINAL d_mono~{-sol['info'].get('pobj',float('nan')):.6f} "
      f"(beta/N^2~{-sol['info'].get('pobj',float('nan'))/2:.5f}) status={sol['info'].get('status')} "
      f"[{time.time()-t0:.0f}s] DONE", flush=True)
