"""Equilibrated diagonal-exposure LP, correcting the V4 call adapter."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog as scipy_linprog


PATH = (
    Path(__file__).resolve().parent
    / "CODEX_R10_ZERO_NU_DIAGONAL_EXPOSURE_PROBE_V2.py"
)
spec = importlib.util.spec_from_file_location("zero_nu_diagonal_v2_scaled5", PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(PATH)
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)


def row_scale(matrix, rhs):
    matrix = sp.csr_matrix(matrix)
    maxima = np.asarray(abs(matrix).max(axis=1).toarray()).reshape(-1)
    factors = 1.0 / np.maximum(1.0, maxima)
    return sp.diags(factors) @ matrix, factors * np.asarray(rhs)


def scaled_lp(objective, **kwargs):
    kwargs["A_eq"], kwargs["b_eq"] = row_scale(
        kwargs["A_eq"], kwargs["b_eq"]
    )
    kwargs["A_ub"], kwargs["b_ub"] = row_scale(
        kwargs["A_ub"], kwargs["b_ub"]
    )
    kwargs["method"] = "highs-ds"
    kwargs["options"] = {
        "dual_feasibility_tolerance": 1.0e-9,
        "primal_feasibility_tolerance": 1.0e-9,
        "disp": True,
    }
    return scipy_linprog(objective, **kwargs)


core.linprog = scaled_lp
core.main()
