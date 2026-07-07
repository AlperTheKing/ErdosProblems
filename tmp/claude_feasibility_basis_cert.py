#!/usr/bin/env python3
"""Feasibility-basis EXACT cert extraction for a 'broad' row (no face-split).

The ConeCert condition is x>=0, A_src x <= target over the FULL source columns. Clarabel proved
this feasible for the broad rows (broad-failure was a core-selection artifact). This extracts an
EXACT nonneg cert:
  1. HiGHS SIMPLEX on min 1'x s.t. A_src x <= target, x>=0  -> a basic feasible VERTEX + basis.
  2. Basis = basic structural columns S + tight rows T (|T|=|S|); A[T,S] is invertible.
  3. Write the exact square core A[T,S] x_S = target[T] (exact Fractions) as a modular-solver core,
     with col k -> source_col S[k] mapping records.
  4. Exact solve is done downstream by tmp/claude_modular_solve_parallel.py (48 workers), then
     convert (col->source_col) + official source_solution_check must show exact_ok=true.

This script writes the core .jsonl (meta/term/rhs + col records) and a summary; the caller runs the
parallel modular solve + convert + source check.

Usage: python claude_feasibility_basis_cert.py <chart> <dom> [band] [support] <out_core.jsonl>
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

chart = int(sys.argv[1]); dom = int(sys.argv[2])
band = sys.argv[3] if len(sys.argv) > 4 else "near_2s_minus_1"
support = sys.argv[4] if len(sys.argv) > 5 else "negative"
out_core = Path(sys.argv[-1])

prepared, columns, _m, _b = probe.build_lp(chart, dom, band, support)
target_frac = list(prepared.p_beta)                # exact Fractions
target = np.array([float(x) for x in target_frac])
m = len(target_frac); ncol = len(columns)

# exact per-column row->coeff dicts + float A
col_map = [dict() for _ in range(ncol)]
ri = []; cj = []; vv = []
for j, col in enumerate(columns):
    for (r, coeff) in col.terms:
        col_map[j][r] = col_map[j].get(r, Fraction(0)) + coeff
    for r, coeff in col_map[j].items():
        ri.append(r); cj.append(j); vv.append(float(coeff))
A = sparse.csc_matrix((vv, (ri, cj)), shape=(m, ncol))

# HiGHS simplex: min 1'x s.t. -inf <= A x <= target, x >= 0
inf = highspy.kHighsInf
lp = highspy.HighsLp()
lp.num_col_ = ncol; lp.num_row_ = m
lp.col_cost_ = np.ones(ncol)
lp.sense_ = highspy.ObjSense.kMinimize
lp.col_lower_ = np.zeros(ncol); lp.col_upper_ = np.full(ncol, inf)
lp.row_lower_ = np.full(m, -inf); lp.row_upper_ = target.copy()
Acsc = A.tocsc()
mat = highspy.HighsSparseMatrix()
mat.format_ = highspy.MatrixFormat.kColwise
mat.num_col_ = ncol; mat.num_row_ = m
mat.start_ = Acsc.indptr.tolist(); mat.index_ = Acsc.indices.tolist(); mat.value_ = Acsc.data.tolist()
lp.a_matrix_ = mat
h = highspy.Highs()
h.setOptionValue("output_flag", False)
h.setOptionValue("solver", "simplex")
h.setOptionValue("presolve", "on")
h.passModel(lp)
h.run()
model_status = h.getModelStatus()
basis = h.getBasis()
sol = h.getSolution()
xstar = np.array(sol.col_value)
kBasic = highspy.HighsBasisStatus.kBasic
S = [j for j in range(ncol) if basis.col_status[j] == kBasic]
T = [i for i in range(m) if basis.row_status[i] != kBasic]   # nonbasic rows = tight (Ax==target)
print(f"row={chart}/{dom} status={model_status} ncol={ncol} m={m} |S|(basic cols)={len(S)} |T|(tight rows)={len(T)}", flush=True)

if len(S) != len(T):
    print(f"WARN: |S|={len(S)} != |T|={len(T)} (degenerate basis); still writing square min(|S|,|T|) not valid.", flush=True)

# exact square core A[T,S] x_S = target[T]; core col k -> source_col S[k]
dim = len(S)
Sset_index = {j: k for k, j in enumerate(S)}
recs = []
recs.append({"type": "meta", "dimension": dim})
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
    for r in recs:
        f.write(json.dumps(r) + "\n")
print(json.dumps({"row": f"{chart}/{dom}", "dim": dim, "tight_rows": len(T), "basic_cols": len(S),
                  "square": len(S) == len(T), "core": str(out_core), "model_status": str(model_status)}))
