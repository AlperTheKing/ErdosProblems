#!/usr/bin/env python3
"""Clarabel Phase-I LP solver for the face-split column-generation restricted master.

User directive 2026-07-07: use Clarabel (conic IPM, parallelizes far better than HiGHS simplex)
for the CG's float LP phase. Float is fine here — the LP only PRICES columns; exactness comes
from the parallel modular reconstruction of the selected columns (tmp/claude_modular_solve_parallel.py).

Phase-I feasibility LP over selected quotient columns A_J (m equality rows, nvar structural vars):
    min 1'u+ + 1'u-   s.t.   A_J x + u+ - u- = b,   x,u+,u- >= 0.
optimum 0  => restricted cone feasible; optimum > 0 => dual y is a separator for pricing.

Clarabel standard form: min (1/2)z'Pz + q'z  s.t.  A z + s = b,  s in K.
Variables z = [x (nvar); u+ (m); u- (m)].  P = 0 (LP).
Constraints:  [A_J | I | -I] z = b        -> ZeroCone(m)      (the equalities)
              -I_(nvar+2m) z <= 0          -> NonnegativeCone  (z >= 0)
The equality-row dual gives the pricing vector y (Clarabel returns z-duals per cone block).

drop-in: solve_phase1_clarabel(A_data, A_indices, A_indptr, m, nvar, b, threads) -> dict.
"""
from __future__ import annotations
import numpy as np
from scipy import sparse
import clarabel


def solve_phase1_clarabel(A_J, b, nvar, *, threads=0, tol=1e-9, max_iter=200, verbose=False):
    """A_J: scipy sparse (m x nvar) equality matrix over the structural x-columns. b: length-m rhs.
    Returns {obj, x (nvar), y (m equality duals for pricing), feasible, status, iters}."""
    A_J = sparse.csc_matrix(A_J)
    m, ncol = A_J.shape
    assert ncol == nvar, f"A_J cols {ncol} != nvar {nvar}"
    N = nvar + 2 * m  # z = [x; u+; u-]

    # objective: minimize sum(u+) + sum(u-)
    q = np.concatenate([np.zeros(nvar), np.ones(m), np.ones(m)])
    P = sparse.csc_matrix((N, N))

    I_m = sparse.identity(m, format="csc")
    eq = sparse.hstack([A_J, I_m, -I_m], format="csc")          # [A_J | I | -I]  (m x N)
    nn = -sparse.identity(N, format="csc")                       # -I_N            (N x N)
    A = sparse.vstack([eq, nn], format="csc")
    rhs = np.concatenate([np.asarray(b, dtype=float), np.zeros(N)])
    cones = [clarabel.ZeroConeT(m), clarabel.NonnegativeConeT(N)]

    settings = clarabel.DefaultSettings()
    settings.verbose = bool(verbose)
    settings.tol_gap_abs = tol
    settings.tol_gap_rel = tol
    settings.tol_feas = tol
    settings.max_iter = int(max_iter)
    if threads and hasattr(settings, "max_threads"):
        settings.max_threads = int(threads)

    solver = clarabel.DefaultSolver(P, q, A, rhs, cones, settings)
    sol = solver.solve()
    z = np.array(sol.x)
    # duals: sol.z is per-constraint; first m entries correspond to the equality (Zero) block
    zdual = np.array(sol.z)
    y = zdual[:m]
    x = z[:nvar]
    obj = float(sol.obj_val)
    status = str(sol.status)
    feasible = obj <= 1e-6
    return {"obj": obj, "x": x, "y": y, "feasible": feasible, "status": status,
            "iters": getattr(sol, "iterations", None)}


def _selftest():
    # small LP with known feasible cone: b in cone(columns) => phase1 optimum 0.
    # A_J = [[1,0],[0,1]], b=[2,3] -> x=[2,3] feasible, obj 0.
    A = sparse.csc_matrix(np.array([[1.0, 0.0], [0.0, 1.0]]))
    r1 = solve_phase1_clarabel(A, [2.0, 3.0], 2)
    # infeasible-direction case: A_J=[[1],[0]] (col only covers row0), b=[0,5] -> need u for row1, obj=5.
    A2 = sparse.csc_matrix(np.array([[1.0], [0.0]]))
    r2 = solve_phase1_clarabel(A2, [0.0, 5.0], 1)
    print("feasible-case obj", round(r1["obj"], 6), "x", np.round(r1["x"], 4).tolist(), "status", r1["status"])
    print("separator-case obj", round(r2["obj"], 6), "y", np.round(r2["y"], 4).tolist(), "status", r2["status"])
    ok = abs(r1["obj"]) < 1e-5 and abs(r2["obj"] - 5.0) < 1e-4
    print("SELFTEST", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    _selftest()
