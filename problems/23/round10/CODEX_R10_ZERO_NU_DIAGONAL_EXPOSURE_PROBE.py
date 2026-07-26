"""LP probe for a diagonal exact exposing functional on the sealed C5 face.

This is a steering computation only.  It uses the exact integer affine and
kernel matrices, but solves a floating LP to ask whether a nonnegative
combination of quotient diagonal evaluations can expose the fourteen
near-zero multiplier orbits.  It does not run an SDP and writes no files.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
REDUCED_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
TARGET_ORBITS = np.asarray(
    [
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
    ],
    dtype=np.int32,
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_exact_basis(archive) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive["exact_basis_data"].astype(np.float64),
            archive["exact_basis_indices"].astype(np.int32),
            archive["exact_basis_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive["exact_basis_shape"])),
    )


def main() -> None:
    reduced = load_module("codex_r10_zero_nu_reduced", REDUCED_PATH)
    model = reduced.build_model()
    z = unpack_exact_basis(model.exact_kernel)
    affine_nu = reduced.unpack_csr(
        model.row_reduction, "affine_nu", np.float64
    )
    affine_q = reduced.unpack_csr(
        model.row_reduction, "affine_gram", np.float64
    )
    affine_y = (affine_q @ z).tocsr()

    diagonal_rows: list[int] = []
    diagonal_labels: list[tuple[int, int, int]] = []
    offsets = model.blowup["gram_offsets"].astype(np.int64)
    for block, (orbit, free) in enumerate(
        zip(model.base.gram_orbits, model.free_by_block)
    ):
        q0 = int(offsets[block])
        for local_index, coordinate in enumerate(free):
            qid = q0 + int(orbit.entry_ids[coordinate, coordinate])
            diagonal_rows.append(qid)
            diagonal_labels.append((block, local_index, qid))
    diagonal = z[np.asarray(diagonal_rows, dtype=np.int64), :].tocsr()

    live = model.live.astype(np.int32)
    target_positions = np.asarray(
        [
            position
            for position, orbit in enumerate(live)
            if int(orbit) in set(map(int, TARGET_ORBITS))
        ],
        dtype=np.int32,
    )
    if len(target_positions) != len(TARGET_ORBITS):
        raise AssertionError("target orbit is not live")

    number_lambda = affine_nu.shape[0]
    number_weights = diagonal.shape[0]
    # affine_y.T lambda - diagonal.T weights = 0
    exposure_rows = sp.hstack(
        (affine_y.T, -diagonal.T), format="csr"
    )
    rhs_row = sp.hstack(
        (
            sp.csr_matrix(
                model.affine_rhs.astype(np.float64).reshape(1, -1)
            ),
            sp.csr_matrix((1, number_weights)),
        ),
        format="csr",
    )
    target_column_sum = np.asarray(
        affine_nu[:, target_positions].sum(axis=1)
    ).reshape(-1)
    normalization_row = sp.hstack(
        (
            sp.csr_matrix(target_column_sum.reshape(1, -1)),
            sp.csr_matrix((1, number_weights)),
        ),
        format="csr",
    )
    a_eq = sp.vstack(
        (exposure_rows, rhs_row, normalization_row), format="csr"
    )
    b_eq = np.r_[
        np.zeros(affine_y.shape[1] + 1, dtype=np.float64),
        1.0,
    ]
    a_ub = sp.hstack(
        (-affine_nu.T, sp.csr_matrix((len(live), number_weights))),
        format="csr",
    )
    objective = np.zeros(number_lambda + number_weights, dtype=np.float64)
    other_positions = np.setdiff1d(
        np.arange(len(live), dtype=np.int32), target_positions
    )
    objective[:number_lambda] = np.asarray(
        affine_nu[:, other_positions].sum(axis=1)
    ).reshape(-1)
    objective[number_lambda:] = 1.0e-6
    result = linprog(
        objective,
        A_ub=a_ub,
        b_ub=np.zeros(len(live), dtype=np.float64),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(None, None)] * number_lambda
        + [(0.0, None)] * number_weights,
        method="highs",
        options={
            "dual_feasibility_tolerance": 1.0e-9,
            "primal_feasibility_tolerance": 1.0e-9,
            "ipm_optimality_tolerance": 1.0e-10,
        },
    )
    print(
        f"lambda={number_lambda} diagonal_weights={number_weights}"
        f" exact_face_coordinates={affine_y.shape[1]}"
    )
    print(
        f"success={result.success} status={result.status}"
        f" objective={result.fun if result.success else 'nan'}"
        f" message={result.message}"
    )
    if not result.success:
        return
    lam = result.x[:number_lambda]
    weights = result.x[number_lambda:]
    coefficients = np.asarray(affine_nu.T @ lam).reshape(-1)
    print(
        f"residual={np.max(np.abs(a_eq @ result.x - b_eq)):.3e}"
        f" min_coefficient={coefficients.min():.3e}"
        f" target_coefficients="
        f"{[(int(live[p]), float(coefficients[p])) for p in target_positions]}"
    )
    print(
        "coefficient_support="
        + str(
            [
                (int(live[index]), float(coefficients[index]))
                for index in np.flatnonzero(coefficients > 1.0e-8)
            ]
        )
    )
    print(
        "diagonal_support="
        + str(
            [
                (diagonal_labels[index], float(weights[index]))
                for index in np.flatnonzero(weights > 1.0e-8)
            ]
        )
    )


if __name__ == "__main__":
    main()
