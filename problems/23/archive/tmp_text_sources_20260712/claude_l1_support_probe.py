import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup"))
import numpy as np
from scipy import sparse
import clarabel
import _codex_eq_odl1_rung2_scipy_core_probe as probe

chart = int(sys.argv[1]); dom = int(sys.argv[2])
prepared, columns, _m, _b = probe.build_lp(chart, dom, "near_2s_minus_1", "negative")
target = [float(x) for x in prepared.p_beta]; m = len(target); ncol = len(columns)
ri = []; cj = []; vv = []
for j, c in enumerate(columns):
    for (r, co) in c.terms:
        ri.append(r); cj.append(j); vv.append(float(co))
A = sparse.csc_matrix((vv, (ri, cj)), shape=(m, ncol))
# min 1'x s.t. A x <= target, x>=0  (L1 promotes sparsity)
q = np.ones(ncol); P = sparse.csc_matrix((ncol, ncol))
Amat = sparse.vstack([A, -sparse.identity(ncol, format="csc")], format="csc")
b = np.concatenate([np.array(target), np.zeros(ncol)])
cones = [clarabel.NonnegativeConeT(m), clarabel.NonnegativeConeT(ncol)]
s = clarabel.DefaultSettings(); s.verbose = False; s.max_iter = 400
sol = clarabel.DefaultSolver(P, q, Amat, b, cones, s).solve()
x = np.array(sol.x)
print("L1PROBE row=%d/%d status=%s ncol=%d" % (chart, dom, sol.status, ncol))
for th in (1e-3, 1e-4, 1e-5, 1e-6):
    print("  support |x|>%g: %d" % (th, int((x > th).sum())))
print("  sum_x=%.3f" % float(x.sum()))
