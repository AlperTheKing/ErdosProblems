"""Numerical steering for a block-0-only second facial exposure.

No conic solver is called.  This script intersects the exact affine-dual
linear conditions (read as float64) with the requirement that the Gram
functional vanish on every sealed face coordinate outside block 0.  It then
compares that ten-dimensional space with the already-exported SCS dual.

Every conclusion here is numerical only.  A separate exact reconstruction and
modular gate are required before any facial reduction is claimed.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import scipy.linalg as la
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
CANONICAL_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE.py"
ROW_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
NUMERICAL_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
DUAL_PATH = HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_csr(archive, name: str, dtype) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(dtype),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive[f"{name}_shape"])),
        dtype=dtype,
    )


def raw_psd_matrix(dual, block: int) -> np.ndarray:
    positions = np.flatnonzero(dual["psd_block_indices"] == block)
    if positions.size != 1:
        raise AssertionError((block, positions))
    position = int(positions[0])
    order = int(dual["psd_orders"][position])
    offsets = dual["psd_flat_offsets"].astype(np.int64)
    return dual["dual_psd_matrices_flat"][
        int(offsets[position]) : int(offsets[position + 1])
    ].reshape((order, order))


def main() -> None:
    base_module = load_module("codex_r10_block0_probe_base", BASE_PATH)
    canonical = load_module("codex_r10_block0_probe_canonical", CANONICAL_PATH)
    base = base_module.build_model()
    row = np.load(ROW_PATH, allow_pickle=False)
    numerical = np.load(NUMERICAL_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    dual = np.load(DUAL_PATH, allow_pickle=False)

    affine_nu = unpack_csr(row, "affine_nu", np.float64)
    affine_q = unpack_csr(row, "affine_gram", np.float64)
    numerical_basis = unpack_csr(
        numerical, "numerical_basis", np.float64
    )
    affine_y = (affine_q @ numerical_basis).tocsr()
    rhs = row["affine_rhs"].astype(np.float64)

    pure_constraints = np.vstack((affine_nu.toarray().T, rhs[None, :]))
    pure_basis = la.null_space(pure_constraints, rcond=1e-12)
    functionals = np.asarray(affine_y.T @ pure_basis)
    face_offsets = numerical["face_column_offsets"].astype(np.int64)
    block0_end = int(face_offsets[1])
    outside = functionals[block0_end:, :]
    restricted_coefficients = la.null_space(outside, rcond=1e-11)
    restricted_basis = pure_basis @ restricted_coefficients
    restricted_functionals = np.asarray(affine_y.T @ restricted_basis)

    print(
        f"pure_dual_nullity={pure_basis.shape[1]}"
        f" outside_rank={outside.shape[1] - restricted_coefficients.shape[1]}"
        f" block0_only_nullity={restricted_coefficients.shape[1]}"
    )
    print(
        "restricted_residuals"
        f" pure={np.max(np.abs(pure_constraints @ restricted_basis)):.3e}"
        f" outside={np.max(np.abs(restricted_functionals[block0_end:])):.3e}"
    )

    raw_lambda = dual["dual_affine_equalities"].astype(np.float64)
    projected_lambda = restricted_basis @ (
        restricted_basis.T @ raw_lambda
    )
    lambda_scale = max(1.0, np.linalg.norm(raw_lambda))
    print(
        "raw_lambda_projection"
        f" relative={np.linalg.norm(raw_lambda - projected_lambda) / lambda_scale:.3e}"
        f" pure={np.max(np.abs(pure_constraints @ raw_lambda)):.3e}"
        f" outside={np.max(np.abs(np.asarray(affine_y.T @ raw_lambda)[block0_end:])):.3e}"
    )

    free = canonical.free_coordinates(blowup, base)
    if len(free[0]) != 154:
        raise AssertionError(len(free[0]))
    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    q0 = int(q_offsets[0])
    qdim = int(q_dimensions[0])
    fdim = int(numerical["gram_face_dimensions"][0])
    local_basis = numerical_basis[q0 : q0 + qdim, :fdim]
    ids = base.gram_orbits[0].entry_ids[np.ix_(free[0], free[0])].astype(
        np.int64
    )
    raw_matrix = raw_psd_matrix(dual, 0)
    raw_coordinate = np.bincount(
        ids.reshape(-1),
        weights=raw_matrix.reshape(-1),
        minlength=qdim,
    )
    raw_functional = np.asarray(local_basis.T @ raw_coordinate).reshape(-1)
    lambda_functional = np.asarray(affine_y.T @ raw_lambda).reshape(-1)
    for sign in (1.0, -1.0):
        residual = np.linalg.norm(
            lambda_functional[:fdim] - sign * raw_functional
        )
        print(f"stationarity_sign={sign:+.0f} residual={residual:.12e}")

    projected_functional = np.asarray(
        affine_y.T @ projected_lambda
    ).reshape(-1)
    print(
        "projected_functional"
        f" raw_relative={np.linalg.norm(projected_functional[:fdim] - raw_functional) / np.linalg.norm(raw_functional):.3e}"
        f" outside_inf={np.max(np.abs(projected_functional[fdim:])):.3e}"
    )

    eigenvalues = np.linalg.eigvalsh((raw_matrix + raw_matrix.T) / 2)
    print(
        "raw_block0"
        f" trace={np.trace(raw_matrix):.15g}"
        f" rank_1e-8={np.sum(eigenvalues > 1e-8 * eigenvalues[-1])}"
        f" eig_min={eigenvalues[0]:.3e}"
        f" eig_22={eigenvalues[-22]:.12e}"
        f" eig_23={eigenvalues[-23]:.12e}"
        f" eig_max={eigenvalues[-1]:.12e}"
    )

    coordinates, *_ = la.lstsq(
        restricted_functionals[:fdim, :],
        raw_functional,
        cond=1e-12,
    )
    fitted = restricted_functionals[:fdim, :] @ coordinates
    print(
        "ten_space_fit"
        f" relative={np.linalg.norm(fitted - raw_functional) / np.linalg.norm(raw_functional):.3e}"
        f" coordinates={','.join(f'{value:.16g}' for value in coordinates)}"
    )


if __name__ == "__main__":
    main()
