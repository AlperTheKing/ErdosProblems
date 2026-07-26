"""Well-scaled LP probe for a diagonal exposure of the 14 near-zero nu orbits.

The direct-H orthonormal basis is used only to steer the LP.  Any candidate
must later be rebuilt with the sealed exact integer kernel basis.  No SDP is
called and this script writes no files.
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
TARGET_ORBITS = {
    1594, 2075, 2123, 2101, 1597, 2105, 1706,
    2582, 2439, 2038, 2498, 1361, 1633, 1636,
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_basis(archive) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive["numerical_basis_data"].astype(np.float64),
            archive["numerical_basis_indices"].astype(np.int32),
            archive["numerical_basis_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive["numerical_basis_shape"])),
    )


def main() -> None:
    reduced = load_module("codex_r10_zero_nu_reduced_v2", REDUCED_PATH)
    model = reduced.build_model()
    g = unpack_basis(model.numerical_kernel)
    affine_nu = reduced.unpack_csr(
        model.row_reduction, "affine_nu", np.float64
    )
    affine_q = reduced.unpack_csr(
        model.row_reduction, "affine_gram", np.float64
    )
    affine_y = (affine_q @ g).tocsr()

    offsets = model.blowup["gram_offsets"].astype(np.int64)
    diagonal_rows = []
    labels = []
    for block, (orbit, free) in enumerate(
        zip(model.base.gram_orbits, model.free_by_block)
    ):
        q0 = int(offsets[block])
        for local_index, coordinate in enumerate(free):
            diagonal_rows.append(
                q0 + int(orbit.entry_ids[coordinate, coordinate])
            )
            labels.append((block, local_index, diagonal_rows[-1]))
    diagonal = g[np.asarray(diagonal_rows, dtype=np.int64), :].tocsr()

    live = model.live.astype(np.int32)
    target = np.asarray(
        [
            position
            for position, orbit in enumerate(live)
            if int(orbit) in TARGET_ORBITS
        ],
        dtype=np.int32,
    )
    other = np.setdiff1d(np.arange(len(live), dtype=np.int32), target)
    if len(target) != 14:
        raise AssertionError("target/live mismatch")

    nl = affine_nu.shape[0]
    nw = diagonal.shape[0]
    a_eq = sp.vstack(
        (
            sp.hstack((affine_y.T, -diagonal.T), format="csr"),
            sp.hstack(
                (
                    sp.csr_matrix(
                        model.affine_rhs.astype(float).reshape(1, -1)
                    ),
                    sp.csr_matrix((1, nw)),
                ),
                format="csr",
            ),
            sp.hstack(
                (
                    sp.csr_matrix(
                        np.asarray(
                            affine_nu[:, target].sum(axis=1)
                        ).reshape(1, -1)
                    ),
                    sp.csr_matrix((1, nw)),
                ),
                format="csr",
            ),
        ),
        format="csr",
    )
    b_eq = np.r_[np.zeros(affine_y.shape[1] + 1), 1.0]
    a_ub = sp.hstack(
        (-affine_nu.T, sp.csr_matrix((len(live), nw))), format="csr"
    )
    objective = np.zeros(nl + nw)
    objective[:nl] = np.asarray(
        affine_nu[:, other].sum(axis=1)
    ).reshape(-1)
    objective[nl:] = 1.0e-8
    result = linprog(
        objective,
        A_ub=a_ub,
        b_ub=np.zeros(len(live)),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(None, None)] * nl + [(0.0, None)] * nw,
        method="highs-ipm",
        options={
            "dual_feasibility_tolerance": 1.0e-9,
            "primal_feasibility_tolerance": 1.0e-9,
            "ipm_optimality_tolerance": 1.0e-10,
        },
    )
    print(
        f"lambda={nl} diagonal_weights={nw}"
        f" face_coordinates={affine_y.shape[1]}"
    )
    print(
        f"success={result.success} status={result.status}"
        f" objective={result.fun if result.success else 'nan'}"
        f" message={result.message}"
    )
    if not result.success:
        return
    lam = result.x[:nl]
    weights = result.x[nl:]
    coefficients = np.asarray(affine_nu.T @ lam).reshape(-1)
    print(
        f"residual={np.max(np.abs(a_eq @ result.x - b_eq)):.3e}"
        f" min_coefficient={coefficients.min():.3e}"
    )
    print(
        "target="
        + str([(int(live[p]), float(coefficients[p])) for p in target])
    )
    print(
        "coefficient_support="
        + str(
            [
                (int(live[i]), float(coefficients[i]))
                for i in np.flatnonzero(coefficients > 1.0e-8)
            ]
        )
    )
    print(
        "diagonal_support="
        + str(
            [
                (labels[i], float(weights[i]))
                for i in np.flatnonzero(weights > 1.0e-8)
            ]
        )
    )


if __name__ == "__main__":
    main()
