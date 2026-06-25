#!/usr/bin/env python3
"""
Z2-symmetry-reduced N=6 SDP (Stage A): restrict to tau-symmetric x = O @ y, solve over y (~2x fewer
vars). Sound: the problem is tau-invariant + convex, so an optimal tau-symmetric solution exists.
Validate: config=baseline must reproduce the full-model 0.125.
Usage: python solve_n6_sym.py <config> [solver=scs|clarabel] [eps] [maxit]
"""
import sys, time, pickle
import numpy as np
import scipy.sparse as sp
import cvxpy as cp

CFG = sys.argv[1] if len(sys.argv) > 1 else "psdloc"
SOLVER = sys.argv[2] if len(sys.argv) > 2 else "scs"
EPS = float(sys.argv[3]) if len(sys.argv) > 3 else 1e-4
MAXIT = int(sys.argv[4]) if len(sys.argv) > 4 else 20000
t0 = time.time()
with open("n6_cache.pkl", "rb") as f:
    D = pickle.load(f)
O = sp.load_npz("sym_O.npz").tocsc()
ns, n_orb = O.shape
band = D["band"]
sizes = np.asarray(O.sum(axis=0)).ravel()          # orbit sizes (1 or 2)
dmono = D["dmono"] @ O; dedge = D["dedge"] @ O
basic = [g @ O for g in D["basic"]]
weakloc = [g @ O for g in D["weakloc"]]
gsw = D["gsw"] @ O
print(f"[{CFG}/{SOLVER}/sym] ns={ns}->n_orb={n_orb} band={band} eps={EPS} [{time.time()-t0:.0f}s]; reducing blocks ...", flush=True)
moment = [(S @ O, t) for (S, t) in D["moment"]]
loc = [(S @ O, t, c, low) for (S, t, c, low) in D["loc"]]
print(f"[{CFG}/{SOLVER}/sym] {len(moment)} moment + {len(loc)} loc blocks reduced [{time.time()-t0:.0f}s]; building ...", flush=True)

y = cp.Variable(n_orb, nonneg=True)
cons = [sizes @ y == 1, dedge @ y >= band[0], dedge @ y <= band[1]]
for (SO, t) in moment:
    M = cp.reshape(SO @ y, (t, t), order='C'); cons.append(0.5*(M + M.T) >> 0)
for g in basic:
    cons.append(g @ y <= 0)
if CFG == "weakloc":
    for g in weakloc: cons.append(g @ y <= 0)
if CFG == "psdloc":
    for (SO, t, c, low) in loc:
        L = cp.reshape(SO @ y, (t, t), order='C'); cons.append(0.5*(L + L.T) >> 0)
if CFG in ("psdloc", "weakloc"):
    cons.append(gsw @ y <= 0)
prob = cp.Problem(cp.Maximize(dmono @ y), cons)
print(f"[{CFG}/{SOLVER}/sym] built {len(cons)} constraints [{time.time()-t0:.0f}s]; solving ...", flush=True)
try:
    if SOLVER == "clarabel":
        val = prob.solve(solver=cp.CLARABEL, verbose=True)
    else:
        val = prob.solve(solver=cp.SCS, max_iters=MAXIT, eps_abs=EPS, eps_rel=EPS, verbose=False)
    print(f"[{CFG}/{SOLVER}/sym] max d_mono = {val:.6f}  (beta/N^2 <= {val/2:.5f})  status={prob.status}  [{time.time()-t0:.0f}s]", flush=True)
except Exception as e:
    import traceback
    print(f"[{CFG}/{SOLVER}/sym] FAILED: {type(e).__name__}: {e}", flush=True); traceback.print_exc()
print(f"[{CFG}/{SOLVER}/sym] DONE [{time.time()-t0:.0f}s]", flush=True)
