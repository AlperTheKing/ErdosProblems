"""Run the V2 diagonal-exposure LP with the HiGHS dual simplex backend."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from scipy.optimize import linprog as scipy_linprog


PATH = (
    Path(__file__).resolve().parent
    / "CODEX_R10_ZERO_NU_DIAGONAL_EXPOSURE_PROBE_V2.py"
)
spec = importlib.util.spec_from_file_location("zero_nu_diagonal_v2", PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(PATH)
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)


def dual_simplex(*args, **kwargs):
    kwargs["method"] = "highs-ds"
    kwargs["options"] = {
        "dual_feasibility_tolerance": 1.0e-8,
        "primal_feasibility_tolerance": 1.0e-8,
    }
    return scipy_linprog(*args, **kwargs)


core.linprog = dual_simplex
core.main()
