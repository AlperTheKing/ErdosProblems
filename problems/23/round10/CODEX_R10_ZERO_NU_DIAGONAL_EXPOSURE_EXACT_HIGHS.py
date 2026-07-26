"""Run the exact-Z diagonal-exposure LP through the HiGHS 1.14 adapter."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


core = load(
    "zero_nu_diagonal_exact_core",
    HERE / "CODEX_R10_ZERO_NU_DIAGONAL_EXPOSURE_PROBE.py",
)
adapter = load(
    "zero_nu_diagonal_highs_adapter",
    HERE / "CODEX_R10_ZERO_NU_DIAGONAL_EXPOSURE_PROBE_HIGHS.py",
)
core.linprog = adapter.highs_linprog
core.main()
