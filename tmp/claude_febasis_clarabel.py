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

# 1) Clarabel L1-min -> sparse feasible x*
q = np.ones(ncol); P = sparse.csc_matrix((ncol, ncol))
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

# 2) most-binding rows -> QR-pivot to nS independent rows
Ax = A.dot(xstar)
r = target - Ax                      # residual (>=0 ~feasible; ~0 = binding)
cand = np.argsort(np.abs(r))[: min(m, 4 * nS + 50)]   # most-binding candidate rows
A_cand_S = np.asarray(A[cand][:, S].todense())         # (|cand| x nS)
# pivoted QR on transpose picks independent rows (columns of A_cand_S.T)
_, R, piv = qr(A_cand_S.T, mode="economic", pivoting=True)
diag = np.abs(np.diag(R))
tol = max(diag.max() * 1e-9, 1e-12) if diag.size else 1e-12
rank = int((diag > tol).sum())
sel = piv[:nS]
T = [int(cand[i]) for i in sel[:nS]]
print(f"tight_candidates={len(cand)} qr_rank={rank} selected_rows={len(T)} need={nS} "
      f"square={rank >= nS and len(T) == nS}", flush=True)

# 3) exact square core A[T,S] x_S = target[T], col k -> source_col S[k]
recs = [{"type": "meta", "dimension": nS}]
for k, j in enumerate(S):
    recs.append({"type": "col", "col": k, "source_col": j})
for ti, row in enumerate(T):
    tv = target_frac[row]
    recs.append({"type": "rhs", "row": ti, "value": f"{tv.numerator}/{tv.denominator}"})
    for k, j in enumerate(S):
        c = col_map[j].get(row)
        if c:
            recs.append({"type": "term", "row": ti, "col": k, "value": f"{c.numerator}/{c.denominator}"})
out_core.parent.mkdir(parents=True, exist_ok=True)
with out_core.open("w", encoding="utf-8") as f:
    for rec in recs:
        f.write(json.dumps(rec) + "\n")
print(json.dumps({"row": f"{chart}/{dom}", "dim": nS, "rank": rank, "square": rank >= nS,
                  "core": str(out_core), "clarabel_status": str(sol.status)}))
