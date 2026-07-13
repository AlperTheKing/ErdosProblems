#!/usr/bin/env python3
"""Test whether a 'broad' row certifies DIRECTLY via a full-source nonneg feasibility LP.

The ConeCert condition (per source_solution_check) is: exists x>=0 over the SOURCE columns with
A_src x <= target (residual = target - A_src x >= 0 componentwise). The 'broad-failure' diagnosis
came from the family/dynamic-markowitz CORE subset + its objective — NOT a proof that no feasible
x exists over the FULL source column set. This solves the true feasibility LP with Clarabel (fast
IPM). If FEASIBLE -> the row certifies directly (then exact-verify via the parallel modular solver),
NO face-split needed. If Clarabel reports PrimalInfeasible -> face-split is genuinely required.

Usage: python claude_source_cone_feasibility.py <chart> <dominant> [band] [support]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from scipy import sparse
import clarabel

WRITEUP = str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup")
if WRITEUP not in sys.path:
    sys.path.insert(0, WRITEUP)
import _codex_eq_odl1_rung2_scipy_core_probe as probe

chart = int(sys.argv[1]); dom = int(sys.argv[2])
band = sys.argv[3] if len(sys.argv) > 3 else "near_2s_minus_1"
support = sys.argv[4] if len(sys.argv) > 4 else "negative"

prepared, columns, _mat, _b_ub = probe.build_lp(chart, dom, band, support)
target = [float(x) for x in prepared.p_beta]
m = len(target)
ncol = len(columns)
print(f"row={chart}/{dom} rows(m)={m} source_columns(ncol)={ncol} "
      f"target_negative_entries={sum(1 for x in target if x < 0)}", flush=True)

# A_src (m x ncol) from columns[j].terms
rows_i = []; cols_j = []; vals = []
for j, col in enumerate(columns):
    for (r, coeff) in col.terms:
        rows_i.append(r); cols_j.append(j); vals.append(float(coeff))
A_src = sparse.csc_matrix((vals, (rows_i, cols_j)), shape=(m, ncol))

# Feasibility: x >= 0, A_src x <= target. Clarabel: min 0 s.t. Az + s = b, s in K.
#   A_src x + s1 = target,  s1 in Nonneg(m)      (residual >= 0)
#   -x       + s2 = 0,      s2 in Nonneg(ncol)   (x >= 0)
q = np.zeros(ncol)
P = sparse.csc_matrix((ncol, ncol))
A = sparse.vstack([A_src, -sparse.identity(ncol, format="csc")], format="csc")
b = np.concatenate([np.asarray(target, dtype=float), np.zeros(ncol)])
cones = [clarabel.NonnegativeConeT(m), clarabel.NonnegativeConeT(ncol)]

settings = clarabel.DefaultSettings()
settings.verbose = False
settings.max_iter = 300
solver = clarabel.DefaultSolver(P, q, A, b, cones, settings)
sol = solver.solve()
status = str(sol.status)
x = np.array(sol.x)
resid = np.asarray(target) - A_src.dot(x)
print(f"CLARABEL_STATUS={status} min_residual={resid.min():.3e} min_x={x.min():.3e} "
      f"neg_resid={int((resid < -1e-7).sum())} neg_x={int((x < -1e-7).sum())}", flush=True)
if status in ("Solved", "AlmostSolved"):
    print("VERDICT: FEASIBLE (float) -> row likely certifies DIRECTLY over full source cone; "
          "exact-verify via parallel modular solve on the active columns.")
elif "Infeasible" in status:
    print("VERDICT: INFEASIBLE (float) -> full source cone does NOT contain target; face-split genuinely needed.")
else:
    print(f"VERDICT: inconclusive ({status}) -> retune / face-split.")
