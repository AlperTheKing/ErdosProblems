"""Numerical linear-algebra probe for an exact second facial dual.

This does not call a conic solver.  It uses the sealed SCS primal only to
choose candidate kernel subspaces, then solves homogeneous complementarity
equations by dense SVD:

* dual multiplier coefficients vanish on the 512 numerically positive live
  multiplier orbits;
* the affine RHS pairing vanishes;
* each dual quotient matrix is supported on a candidate primal kernel.

Any output is steering only.  An exact certificate must be reconstructed and
gated separately.
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
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
ROW_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
NUMERICAL_KERNEL_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
SCS_PATH = HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_numeric.npz"

ZERO_ORBITS = {
    1594,
    2075,
    2123,
    2101,
    1597,
    2105,
    1706,
    2582,
    2439,
    2038,
    2498,
    1361,
    1633,
    1636,
}


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


def quotient_matrices(base, blowup, free, q):
    offsets = blowup["gram_offsets"].astype(np.int64)
    dimensions = blowup["gram_qdims"].astype(np.int64)
    output = {}
    for block, orbit in enumerate(base.gram_orbits):
        if not free[block]:
            continue
        local = q[
            int(offsets[block]) : int(offsets[block] + dimensions[block])
        ]
        ambient = local[orbit.entry_ids]
        output[block] = ambient[np.ix_(free[block], free[block])]
    return output


def dual_cone_columns(
    base,
    blowup,
    free,
    numerical_basis,
    primal_matrices,
    kernel_dimensions,
):
    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    face_offsets = np.r_[
        0,
        np.cumsum(
            [
                numerical_basis[
                    int(q_offsets[block]) : int(
                        q_offsets[block] + q_dimensions[block]
                    )
                ].shape[1]
                for block in range(len(base.gram_orbits))
            ]
        ),
    ]
    # The global numerical basis is block diagonal in the sealed ordering.
    face_offsets = np.load(
        NUMERICAL_KERNEL_PATH, allow_pickle=False
    )["face_column_offsets"].astype(np.int64)
    face_dimensions = np.load(
        NUMERICAL_KERNEL_PATH, allow_pickle=False
    )["gram_face_dimensions"].astype(np.int64)

    columns = []
    metadata = []
    kernel_bases = {}
    for block, kernel_dimension in sorted(kernel_dimensions.items()):
        matrix = primal_matrices[block]
        eigenvalues, eigenvectors = np.linalg.eigh(
            (matrix + matrix.T) / 2
        )
        kernel = eigenvectors[:, :kernel_dimension]
        kernel_bases[block] = kernel
        q0 = int(q_offsets[block])
        qdim = int(q_dimensions[block])
        f0 = int(face_offsets[block])
        fdim = int(face_dimensions[block])
        local_basis = numerical_basis[q0 : q0 + qdim, f0 : f0 + fdim]
        ids = base.gram_orbits[block].entry_ids[
            np.ix_(free[block], free[block])
        ].astype(np.int64)
        for left in range(kernel_dimension):
            for right in range(left, kernel_dimension):
                dual_matrix = np.outer(kernel[:, left], kernel[:, right])
                if left != right:
                    dual_matrix += np.outer(
                        kernel[:, right], kernel[:, left]
                    )
                coordinate = np.bincount(
                    ids.reshape(-1),
                    weights=dual_matrix.reshape(-1),
                    minlength=qdim,
                )
                global_column = np.zeros(2518, dtype=float)
                global_column[f0 : f0 + fdim] = np.asarray(
                    local_basis.T @ coordinate
                ).reshape(-1)
                columns.append(global_column)
                metadata.append((block, left, right))
    return np.stack(columns, axis=1), metadata, kernel_bases


def probe_variant(
    name,
    kernel_dimensions,
    affine_nu,
    affine_y,
    rhs,
    null_basis,
    base,
    blowup,
    free,
    numerical_basis,
    primal_matrices,
    live,
):
    cone, metadata, kernel_bases = dual_cone_columns(
        base,
        blowup,
        free,
        numerical_basis,
        primal_matrices,
        kernel_dimensions,
    )
    affine_columns = np.asarray(affine_y.T @ null_basis)
    system = np.c_[affine_columns, -cone]
    norms = np.linalg.norm(system, axis=0)
    if np.any(norms == 0):
        raise AssertionError("zero complementarity column")
    normalized = system / norms[None, :]
    gram = normalized.T @ normalized
    eigenvalues, eigenvectors = np.linalg.eigh((gram + gram.T) / 2)
    smallest = max(0.0, float(eigenvalues[0]))
    vector = eigenvectors[:, 0] / norms
    z = vector[: null_basis.shape[1]]
    cone_values = vector[null_basis.shape[1] :]
    lam = null_basis @ z
    alpha = np.asarray(affine_nu.T @ lam).reshape(-1)
    if np.sum(alpha[[int(orbit) in ZERO_ORBITS for orbit in live]]) < 0:
        lam = -lam
        alpha = -alpha
        cone_values = -cone_values

    dual_eigenvalues = {}
    offset = 0
    for block, dimension in sorted(kernel_dimensions.items()):
        reduced = np.zeros((dimension, dimension), dtype=float)
        for left in range(dimension):
            for right in range(left, dimension):
                value = cone_values[offset]
                reduced[left, right] = value
                reduced[right, left] = value
                offset += 1
        dual_eigenvalues[block] = np.linalg.eigvalsh(reduced).tolist()
    residual = np.linalg.norm(system @ vector)
    positive_positions = [
        index for index, orbit in enumerate(live) if int(orbit) not in ZERO_ORBITS
    ]
    zero_positions = [
        index for index, orbit in enumerate(live) if int(orbit) in ZERO_ORBITS
    ]
    print(
        f"VARIANT {name} variables={system.shape[1]}"
        f" sqrt_gram_eigen={smallest**0.5:.12e}"
        f" residual={residual:.12e}"
        f" lambda_norm={np.linalg.norm(lam):.12e}"
        f" rhs={float(rhs @ lam):.12e}"
        f" alpha_positive_inf={float(np.max(np.abs(alpha[positive_positions]))):.12e}"
        f" alpha_zero_min={float(np.min(alpha[zero_positions])):.12e}"
        f" alpha_zero_max={float(np.max(alpha[zero_positions])):.12e}"
    )
    print(
        "DUAL_EIGS "
        + " ".join(
            f"{block}:{','.join(f'{value:.3e}' for value in values)}"
            for block, values in dual_eigenvalues.items()
        )
    )


def main() -> None:
    builder = load_module("codex_r10_dual_probe_builder", BASE_PATH)
    canonical = load_module("codex_r10_dual_probe_canonical", CANONICAL_PATH)
    base = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    row = np.load(ROW_PATH, allow_pickle=False)
    numerical = np.load(NUMERICAL_KERNEL_PATH, allow_pickle=False)
    scs = np.load(SCS_PATH, allow_pickle=False)
    affine_nu = unpack_csr(row, "affine_nu", np.float64)
    affine_q = unpack_csr(row, "affine_gram", np.float64)
    numerical_basis = unpack_csr(
        numerical, "numerical_basis", np.float64
    )
    affine_y = (affine_q @ numerical_basis).tocsr()
    rhs = row["affine_rhs"].astype(float)
    live = row["live_multiplier_orbits"].astype(np.int32)
    positive = [
        index for index, orbit in enumerate(live) if int(orbit) not in ZERO_ORBITS
    ]
    complementarity = np.vstack(
        (
            affine_nu[:, positive].toarray().T,
            rhs[None, :],
        )
    )
    null_basis = la.null_space(complementarity, rcond=1e-12)
    print(
        f"lambda_constraints={complementarity.shape}"
        f" lambda_nullity={null_basis.shape[1]}"
        f" residual={np.max(np.abs(complementarity @ null_basis)):.3e}"
    )
    free = canonical.free_coordinates(blowup, base)
    primal = quotient_matrices(
        base, blowup, free, scs["q_full"].astype(float)
    )

    variants = {
        "strict": {0: 14, 1: 2, 2: 4, 3: 3, 5: 3, 6: 1, 16: 1, 36: 1},
        "medium": {0: 18, 1: 2, 2: 4, 3: 3, 5: 3, 6: 1, 16: 1, 36: 1},
        "wide": {0: 22, 1: 2, 2: 4, 3: 5, 5: 3, 6: 1, 16: 1, 36: 1},
        "wide_extra": {
            0: 22,
            1: 2,
            2: 4,
            3: 5,
            5: 3,
            6: 1,
            8: 1,
            12: 2,
            16: 1,
            32: 1,
            36: 1,
            45: 1,
        },
    }
    for name, dimensions in variants.items():
        probe_variant(
            name,
            dimensions,
            affine_nu,
            affine_y,
            rhs,
            null_basis,
            base,
            blowup,
            free,
            numerical_basis,
            primal,
            live,
        )


if __name__ == "__main__":
    main()
