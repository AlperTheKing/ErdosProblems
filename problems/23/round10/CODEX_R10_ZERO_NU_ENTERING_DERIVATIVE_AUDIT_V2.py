"""Correct residual-identity adapter for the independent entering audit."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


PATH = (
    Path(__file__).resolve().parent
    / "CODEX_R10_ZERO_NU_ENTERING_DERIVATIVE_AUDIT.py"
)
spec = importlib.util.spec_from_file_location(
    "codex_r10_zero_nu_entering_audit_core", PATH
)
if spec is None or spec.loader is None:
    raise RuntimeError(PATH)
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)


def residual_multiplier_derivative(model, direction: np.ndarray) -> np.ndarray:
    monomial_values = np.asarray(
        [
            core.monomial_value(beta, core.A)
            for beta in model.multiplier_monomials
        ],
        dtype=np.int64,
    )
    monomial_derivatives = np.asarray(
        [
            core.monomial_derivative(beta, core.A, direction)
            for beta in model.multiplier_monomials
        ],
        dtype=np.int64,
    )
    total = int(np.sum(core.A))
    total_derivative = int(np.sum(direction))
    residual_values = np.zeros(len(model.cuts), dtype=np.int64)
    residual_derivatives = np.zeros(len(model.cuts), dtype=np.int64)
    for cut, (_mask, monochromatic_edges) in enumerate(model.cuts):
        q_value = 0
        q_derivative = 0
        for edge_index in monochromatic_edges:
            left, right = model.edges[edge_index]
            q_value += int(core.A[left]) * int(core.A[right])
            q_derivative += (
                int(direction[left]) * int(core.A[right])
                + int(core.A[left]) * int(direction[right])
            )
        residual_values[cut] = total * total - 25 * q_value
        residual_derivatives[cut] = (
            2 * total * total_derivative - 25 * q_derivative
        )
    pair = (
        residual_values[:, None] * monomial_derivatives[None, :]
        + residual_derivatives[:, None] * monomial_values[None, :]
    )
    return np.bincount(
        model.multiplier_orbit_ids.reshape(-1),
        weights=pair.reshape(-1),
        minlength=2611,
    ).astype(np.int64)


core.multiplier_derivative = residual_multiplier_derivative
core.main()
