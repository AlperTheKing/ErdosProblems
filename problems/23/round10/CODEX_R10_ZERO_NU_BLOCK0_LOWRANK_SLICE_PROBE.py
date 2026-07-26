"""Alternating low-rank refinement on the exact alpha[7]=0 pencil slice."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = load("zero_nu_slice_base", "CODEX_R10_g11_d22_sdp.py")
    rows = load(
        "zero_nu_slice_rows", "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
    )
    model = builder.build_model()
    blowup = np.load(
        HERE / "CODEX_R10_BLOWUP_FACE_data.npz", allow_pickle=False
    )
    space = np.load(
        HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz",
        allow_pickle=False,
    )
    grouped = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, _denominator, _pivots, _free = (
        rows.integer_kernel_parameter(grouped[0], len(orbit.basis))
    )
    quotient = np.asarray(
        [
            [int(value) for value in row]
            for row in quotient_dm.to_list()
        ],
        dtype=np.float64,
    )
    ids = orbit.entry_ids.astype(np.int64)
    counts = np.bincount(ids.reshape(-1))
    common = np.lcm.reduce(counts)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    pencil = np.asarray(
        [
            quotient.T
            @ (
                coefficients[ids]
                * (common // counts[ids])
            )
            @ quotient
            for coefficients in q_pencil
        ]
    )
    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=float,
    )
    alpha = (
        space["dual_coordinates_in_row_normalized_basis"]
        / np.linalg.norm(lambda_basis, axis=1)
    )
    alpha /= alpha[0]
    alpha[7] = 0.0
    active = np.asarray([index for index in range(10) if index != 7])
    for iteration in range(100):
        matrix = np.tensordot(alpha, pencil, axes=(0, 0))
        eigenvalues, eigenvectors = np.linalg.eigh(
            (matrix + matrix.T) / 2.0
        )
        order = np.argsort(np.abs(eigenvalues))
        kernel = eigenvectors[:, order[:132]]
        annihilation = np.column_stack(
            [(pencil[index] @ kernel).reshape(-1) for index in active]
        )
        _u, singular_values, vt = np.linalg.svd(
            annihilation, full_matrices=False
        )
        update_active = vt[-1]
        if update_active[0] * alpha[0] < 0:
            update_active = -update_active
        update_active /= update_active[0]
        updated = np.zeros(10)
        updated[active] = update_active
        change = float(np.max(np.abs(updated - alpha)))
        alpha = updated
        if iteration % 5 == 0 or change < 1.0e-13:
            sorted_abs = np.sort(np.abs(eigenvalues))
            print(
                f"iter={iteration} change={change:.3e}"
                f" sigma_min={singular_values[-1]:.3e}"
                f" abs132={sorted_abs[131]:.3e}"
                f" abs133={sorted_abs[132]:.3e}"
            )
        if change < 1.0e-13:
            break
    matrix = np.tensordot(alpha, pencil, axes=(0, 0))
    eigenvalues = np.linalg.eigvalsh((matrix + matrix.T) / 2.0)
    sorted_abs = np.sort(np.abs(eigenvalues))
    print("alpha=" + repr(alpha.tolist()))
    print(
        f"negative={np.count_nonzero(eigenvalues < -1e-6)}"
        f" abs132={sorted_abs[131]:.12e}"
        f" abs133={sorted_abs[132]:.12e}"
        f" min={eigenvalues[0]:.12e}"
        f" max={eigenvalues[-1]:.12e}"
    )
    for denominator in (10, 100, 1000, 10000, 100000, 1000000):
        values = [
            str(
                Fraction(float(value)).limit_denominator(denominator)
            )
            for value in alpha
        ]
        print(f"rational_{denominator}={values}")


if __name__ == "__main__":
    main()
