"""Numerically refine the special low-rank member of the exact 10D pencil.

This calls no conic solver.  It alternates between the numerical kernel of a
pencil member and the least-singular coefficient vector annihilating that
kernel.  Output is steering data only.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
ROW_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
SPACE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = load("zero_nu_lowrank_base", BASE_PATH)
    row_helpers = load("zero_nu_lowrank_rows", ROW_PATH)
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    space = np.load(SPACE_PATH, allow_pickle=False)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    grouped = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    basis_dm, _denominator, _pivots, free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    basis = np.asarray(
        [
            [int(value) for value in row]
            for row in basis_dm.to_list()
        ],
        dtype=np.float64,
    )
    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    common = np.lcm.reduce(multiplicities)
    pencil = []
    for coefficients in q_pencil:
        ambient = (
            coefficients[ids] * (common // multiplicities[ids])
        ).astype(np.float64)
        pencil.append(basis.T @ ambient @ basis)
    pencil = np.asarray(pencil)

    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=np.float64,
    )
    alpha = (
        space["dual_coordinates_in_row_normalized_basis"]
        / np.linalg.norm(lambda_basis, axis=1)
    )
    alpha /= alpha[0]
    for iteration in range(20):
        matrix = np.tensordot(alpha, pencil, axes=(0, 0))
        eigenvalues, eigenvectors = np.linalg.eigh(
            (matrix + matrix.T) / 2.0
        )
        kernel = eigenvectors[:, :132]
        annihilation = np.column_stack(
            [(item @ kernel).reshape(-1) for item in pencil]
        )
        singular_values = np.linalg.svd(
            annihilation, compute_uv=False
        )
        _u, _s, vt = np.linalg.svd(
            annihilation, full_matrices=False
        )
        updated = vt[-1]
        if updated[0] * alpha[0] < 0:
            updated = -updated
        updated /= updated[0]
        change = float(np.max(np.abs(updated - alpha)))
        alpha = updated
        print(
            f"iter={iteration} change={change:.3e}"
            f" annihilation_sigma_min={singular_values[-1]:.3e}"
            f" eigen_132={eigenvalues[131]:.3e}"
            f" eigen_133={eigenvalues[132]:.3e}"
        )
        if change < 1.0e-13:
            break
    matrix = np.tensordot(alpha, pencil, axes=(0, 0))
    eigenvalues = np.linalg.eigvalsh((matrix + matrix.T) / 2.0)
    print("alpha=" + repr(alpha.tolist()))
    print(
        "spectrum="
        f"min={eigenvalues[0]:.12e}"
        f" e132={eigenvalues[131]:.12e}"
        f" e133={eigenvalues[132]:.12e}"
        f" max={eigenvalues[-1]:.12e}"
    )
    for denominator in (10, 100, 1000, 10000, 100000, 1000000):
        print(
            f"rational_{denominator}="
            + str(
                [
                    str(
                        Fraction(float(value)).limit_denominator(
                            denominator
                        )
                    )
                    for value in alpha
                ]
            )
        )


if __name__ == "__main__":
    main()
