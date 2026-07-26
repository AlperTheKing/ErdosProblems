"""Run the diagonal-exposure steering LP with the installed HiGHS 1.14 API."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import highspy
import numpy as np
import scipy.sparse as sp


PATH = (
    Path(__file__).resolve().parent
    / "CODEX_R10_ZERO_NU_DIAGONAL_EXPOSURE_PROBE_V2.py"
)
spec = importlib.util.spec_from_file_location(
    "zero_nu_diagonal_highs_core", PATH
)
if spec is None or spec.loader is None:
    raise RuntimeError(PATH)
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)


def highs_linprog(
    objective,
    *,
    A_ub,
    b_ub,
    A_eq,
    b_eq,
    bounds,
    **_ignored,
):
    a_ub = sp.csr_matrix(A_ub)
    a_eq = sp.csr_matrix(A_eq)
    # Deterministic row equilibration preserves the feasible set.
    ub_scale = 1.0 / np.maximum(
        1.0, np.asarray(abs(a_ub).max(axis=1).toarray()).reshape(-1)
    )
    eq_scale = 1.0 / np.maximum(
        1.0, np.asarray(abs(a_eq).max(axis=1).toarray()).reshape(-1)
    )
    a = sp.vstack(
        (sp.diags(ub_scale) @ a_ub, sp.diags(eq_scale) @ a_eq),
        format="csc",
    )
    ub_rhs = ub_scale * np.asarray(b_ub, dtype=float)
    eq_rhs = eq_scale * np.asarray(b_eq, dtype=float)
    inf = highspy.kHighsInf
    row_lower = np.r_[np.full(len(ub_rhs), -inf), eq_rhs]
    row_upper = np.r_[ub_rhs, eq_rhs]
    col_lower = np.asarray(
        [-inf if lower is None else lower for lower, _upper in bounds],
        dtype=float,
    )
    col_upper = np.asarray(
        [inf if upper is None else upper for _lower, upper in bounds],
        dtype=float,
    )

    lp = highspy.HighsLp()
    lp.num_col_ = a.shape[1]
    lp.num_row_ = a.shape[0]
    lp.col_cost_ = np.asarray(objective, dtype=float)
    lp.col_lower_ = col_lower
    lp.col_upper_ = col_upper
    lp.row_lower_ = row_lower
    lp.row_upper_ = row_upper
    lp.sense_ = highspy.ObjSense.kMinimize
    matrix = highspy.HighsSparseMatrix()
    matrix.format_ = highspy.MatrixFormat.kColwise
    matrix.num_col_ = a.shape[1]
    matrix.num_row_ = a.shape[0]
    matrix.start_ = a.indptr.tolist()
    matrix.index_ = a.indices.tolist()
    matrix.value_ = a.data.tolist()
    lp.a_matrix_ = matrix

    solver = highspy.Highs()
    solver.setOptionValue("output_flag", False)
    solver.setOptionValue("solver", "ipm")
    solver.setOptionValue("run_crossover", "on")
    solver.setOptionValue("presolve", "on")
    solver.setOptionValue("primal_feasibility_tolerance", 1.0e-9)
    solver.setOptionValue("dual_feasibility_tolerance", 1.0e-9)
    solver.passModel(lp)
    solver.run()
    status = solver.getModelStatus()
    success = status == highspy.HighsModelStatus.kOptimal
    solution = solver.getSolution()
    x = np.asarray(solution.col_value, dtype=float)
    return SimpleNamespace(
        success=success,
        status=int(status),
        fun=float(np.dot(objective, x)) if success else None,
        x=x,
        message=str(status),
    )


core.linprog = highs_linprog
core.main()
