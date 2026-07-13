#!/usr/bin/env python3
"""HiGHS IPM+crossover feasibility-basis EXACT core extraction.

Simplex was unreliable (infeasible when Clarabel feasible). IPM is robust; run_crossover=on yields a
VERTEX basis (the actual optimal active set), which is what the exact solve needs. Objective min 1'x
s.t. A_src x <= target, x>=0 -> sparse feasible vertex.  Writes the exact square core A[T,S] x=target[T].

Usage: python claude_febasis_ipm.py <chart> <dom> <band> <support> <out_core.jsonl>
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from fractions import Fraction
import numpy as np
from scipy import sparse
import highspy

WRITEUP = str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup")
if WRITEUP not in sys.path:
    sys.path.insert(0, WRITEUP)
import _codex_eq_odl1_rung2_scipy_core_probe as probe

chart = int(sys.argv[1]); dom = int(sys.argv[2]); band = sys.argv[3]; support = sys.argv[4]
out_core = Path(sys.argv[5])

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
A = sparse.csc_matrix((vv, (ri, cj)), shape=(m, ncol)).tocsc()

inf = highspy.kHighsInf
lp = highspy.HighsLp()
lp.num_col_ = ncol; lp.num_row_ = m
lp.col_cost_ = np.ones(ncol); lp.sense_ = highspy.ObjSense.kMinimize
lp.col_lower_ = np.zeros(ncol); lp.col_upper_ = np.full(ncol, inf)
lp.row_lower_ = np.full(m, -inf); lp.row_upper_ = target.copy()
mat = highspy.HighsSparseMatrix()
mat.format_ = highspy.MatrixFormat.kColwise
mat.num_col_ = ncol; mat.num_row_ = m
mat.start_ = A.indptr.tolist(); mat.index_ = A.indices.tolist(); mat.value_ = A.data.tolist()
lp.a_matrix_ = mat
h = highspy.Highs()
h.setOptionValue("output_flag", False)
h.setOptionValue("solver", "ipm")
h.setOptionValue("run_crossover", "on")
h.setOptionValue("presolve", "on")
h.passModel(lp); h.run()
status = h.getModelStatus()
basis = h.getBasis(); sol = h.getSolution()
kBasic = highspy.HighsBasisStatus.kBasic
xstar = np.array(sol.col_value)
S = [j for j in range(ncol) if basis.col_status[j] == kBasic]
T = [i for i in range(m) if basis.row_status[i] != kBasic]
resid = target - A.dot(xstar)
print(f"row={chart}/{dom} status={status} |S|(basic cols)={len(S)} |T|(tight rows)={len(T)} "
      f"min_x={xstar.min():.2e} min_resid={resid.min():.2e} neg_x_float={(xstar<-1e-7).sum()} "
      f"neg_resid_float={(resid<-1e-7).sum()}", flush=True)
dim = len(S)
recs = [{"type": "meta", "dimension": dim}]
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
print(json.dumps({"row": f"{chart}/{dom}", "dim": dim, "tight_rows": len(T), "square": len(S) == len(T),
                  "status": str(status), "core": str(out_core)}))
