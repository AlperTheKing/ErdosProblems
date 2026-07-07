#!/usr/bin/env python3
"""HiGHS-free feasibility-basis EXACT core extraction (Clarabel support + pivoted-QR row selection).

HiGHS simplex is unreliable on the 167960-row expansion (reports infeasible when Clarabel says
feasible). This avoids simplex entirely:
  1. Clarabel L1-min (min 1'x s.t. A_src x<=target, x>=0) -> sparse feasible x*, support S={j:x*_j>tau}.
  2. residual r*=target-A_src x*; pick the most-binding rows (smallest r*), QR-pivot to |S| INDEPENDENT
     rows T -> square invertible A[T,S] whose exact solution reconstructs the LP vertex.
  3. Write the exact square core A[T,S] x_S = target[T] (exact Fractions) with col k -> source_col S[k].
The |S|-square exact system (~core-sized ~2905) is then solved by tmp/claude_modular_solve_parallel.py and
verified by the official source_solution_check (exact_ok requires x_S>=0 AND A_src x_S<=target on ALL rows).

Usage: python claude_febasis_clarabel.py <chart> <dom> <band> <support> <out_core.jsonl> [tau]
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from fractions import Fraction
import numpy as np
from scipy import sparse
from scipy.linalg import qr
import clarabel

WRITEUP = str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup")
if WRITEUP not in sys.path:
    sys.path.insert(0, WRITEUP)
import _codex_eq_odl1_rung2_scipy_core_probe as probe

chart = int(sys.argv[1]); dom = int(sys.argv[2]); band = sys.argv[3]; support = sys.argv[4]
out_core = Path(sys.argv[5]); tau = float(sys.argv[6]) if len(sys.argv) > 6 else 1e-4

prepared, columns, _m, _b = probe.build_lp(chart, dom, band, support)
target_frac = list(prepared.p_beta)
target = np.array([float(x) for x in target_frac]); m = len(target_frac); ncol = len(columns)

col_map = [dict() for _ in range(ncol)]
ri = []; cj = []; vv = []
for j, col in enumerate(columns):
    for (r, coeff) in col.terms:
        col_map[j][r] = col_map[j].get(r, Fraction(0)) + coeff
    for r, coeff in col_map[j].items():
        ri.append(r); cj.append(j); vv.append(float(coeff))
A = sparse.csc_matrix((vv, (ri, cj)), shape=(m, ncol))

# 1) Clarabel with GENERIC positive objective -> UNIQUE NON-DEGENERATE vertex (breaks L1 ties -> invertible basis)
q = np.array([1.0 + ((j * 1103515245 + 12345) % 100003) / 100003.0 for j in range(ncol)], dtype=float)
P = sparse.csc_matrix((ncol, ncol))
Amat = sparse.vstack([A, -sparse.identity(ncol, format="csc")], format="csc")
b = np.concatenate([target, np.zeros(ncol)])
cones = [clarabel.NonnegativeConeT(m), clarabel.NonnegativeConeT(ncol)]
st = clarabel.DefaultSettings(); st.verbose = False; st.max_iter = 400
sol = clarabel.DefaultSolver(P, q, Amat, b, cones, st).solve()
xstar = np.array(sol.x)
print(f"row={chart}/{dom} clarabel_status={sol.status}", flush=True)
S = [j for j in range(ncol) if xstar[j] > tau]
nS = len(S)
print(f"support |S|={nS} (tau={tau})", flush=True)

# 2) RANK-AWARE basis: independent columns S' (rank r0) + r0 independent binding rows T
Ax = A.dot(xstar)
r = target - Ax                      # residual (>=0 ~feasible; ~0 = binding)
AS = A[:, S]                          # (m x nS)
rownorm = np.asarray(np.abs(AS).sum(axis=1)).ravel()
nontrivial = np.where(rownorm > 1e-12)[0]                   # exclude all-zero (0<=0 trivial) rows
binding = int((np.abs(r[nontrivial]) < 1e-7).sum())
order = nontrivial[np.argsort(np.abs(r[nontrivial]))]       # most-binding non-trivial first
cand = order[: min(len(order), 6 * nS + 100)]
A_cand_S = np.asarray(AS[cand].todense())                  # (|cand| x nS)
# (a) independent COLUMNS of A_cand_S -> rank r0 basis columns S'
_, Rc, pivc = qr(A_cand_S, mode="economic", pivoting=True)
dc = np.abs(np.diag(Rc)); tolc = max(dc.max() * 1e-9, 1e-12) if dc.size else 1e-12
r0 = int((dc > tolc).sum())
colsel = pivc[:r0]                                          # local indices into S
Sb = [S[c] for c in colsel]                                # basis source columns
# (b) independent ROWS over the basis columns -> r0 tight rows T
A_cand_Sb = A_cand_S[:, colsel]                            # (|cand| x r0)
_, Rr, pivr = qr(A_cand_Sb.T, mode="economic", pivoting=True)
dr = np.abs(np.diag(Rr)); tolr = max(dr.max() * 1e-9, 1e-12) if dr.size else 1e-12
rrank = int((dr > tolr).sum())
T = [int(cand[i]) for i in pivr[:r0]]
rank = min(r0, rrank)
print(f"nontrivial_rows={len(nontrivial)} binding_nontrivial={binding} candidates={len(cand)} "
      f"col_rank r0={r0} row_rank={rrank} |Sb|={len(Sb)} |T|={len(T)} square={r0 == rrank == len(T)}", flush=True)

# 3) exact square core A[T,Sb] x = target[T], core col k -> source_col Sb[k]
recs = [{"type": "meta", "dimension": len(Sb)}]
for k, j in enumerate(Sb):
    recs.append({"type": "col", "col": k, "source_col": j})
for ti, row in enumerate(T):
    tv = target_frac[row]
    recs.append({"type": "rhs", "row": ti, "value": f"{tv.numerator}/{tv.denominator}"})
    for k, j in enumerate(Sb):
        c = col_map[j].get(row)
        if c:
            recs.append({"type": "term", "row": ti, "col": k, "value": f"{c.numerator}/{c.denominator}"})
out_core.parent.mkdir(parents=True, exist_ok=True)
with out_core.open("w", encoding="utf-8") as f:
    for rec in recs:
        f.write(json.dumps(rec) + "\n")
print(json.dumps({"row": f"{chart}/{dom}", "dim": len(Sb), "col_rank": r0, "row_rank": rrank,
                  "square": r0 == rrank == len(T), "support": nS,
                  "core": str(out_core), "clarabel_status": str(sol.status)}))
