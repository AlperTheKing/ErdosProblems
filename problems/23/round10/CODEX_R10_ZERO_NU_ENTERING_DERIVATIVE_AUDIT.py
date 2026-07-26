"""Independent exact audit of the proposed entering-derivative exposure.

At

    a = (0,0,1,0,1,0,1,0,0,1,1),
    h1 = e0-e4,  h2 = e3-e9,

the two first-derivative multiplier functionals cancel on every live
multiplier orbit.  The remaining Gram functional is a sum of rank-one PSD
evaluations from parity blocks that enter vertices 0 or 3.

This audit independently rebuilds those facts and tests every rank-one row
against the sealed exact integer kernel basis.  No conic solver is called.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
KERNEL_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"

A = np.asarray([0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1], dtype=np.int64)
H1 = np.asarray([1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0], dtype=np.int64)
H2 = np.asarray([0, 0, 0, 1, 0, 0, 0, 0, 0, -1, 0], dtype=np.int64)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def monomial_value(exponent: tuple[int, ...], point: np.ndarray) -> int:
    value = 1
    for power, coordinate in zip(exponent, point):
        value *= int(coordinate) ** int(power)
    return value


def monomial_derivative(
    exponent: tuple[int, ...], point: np.ndarray, direction: np.ndarray
) -> int:
    total = 0
    for variable, power in enumerate(exponent):
        if power == 0 or direction[variable] == 0:
            continue
        term = int(power) * int(direction[variable])
        for index, other_power in enumerate(exponent):
            reduced_power = int(other_power) - (1 if index == variable else 0)
            term *= int(point[index]) ** reduced_power
        total += term
    return total


def multiplier_derivative(model, direction: np.ndarray) -> np.ndarray:
    monomial_values = np.asarray(
        [monomial_value(beta, A) for beta in model.multiplier_monomials],
        dtype=np.int64,
    )
    monomial_derivatives = np.asarray(
        [
            monomial_derivative(beta, A, direction)
            for beta in model.multiplier_monomials
        ],
        dtype=np.int64,
    )
    q_values = np.zeros(len(model.cuts), dtype=np.int64)
    q_derivatives = np.zeros(len(model.cuts), dtype=np.int64)
    for cut, (_mask, monochromatic_edges) in enumerate(model.cuts):
        for edge_index in monochromatic_edges:
            left, right = model.edges[edge_index]
            q_values[cut] += int(A[left]) * int(A[right])
            q_derivatives[cut] += (
                int(direction[left]) * int(A[right])
                + int(A[left]) * int(direction[right])
            )
    pair = (
        q_values[:, None] * monomial_derivatives[None, :]
        + q_derivatives[:, None] * monomial_values[None, :]
    )
    return np.bincount(
        model.multiplier_orbit_ids.reshape(-1),
        weights=pair.reshape(-1),
        minlength=2611,
    ).astype(np.int64)


def exact_kernel(archive) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive["exact_basis_data"].astype(np.int64),
            archive["exact_basis_indices"].astype(np.int32),
            archive["exact_basis_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive["exact_basis_shape"])),
        dtype=np.int64,
    )


def direct_gram_derivative(model, direction: np.ndarray) -> np.ndarray:
    offsets = np.cumsum(
        [0] + [int(orbit.variable.size) for orbit in model.gram_orbits],
        dtype=np.int64,
    )
    output = np.zeros(int(offsets[-1]), dtype=np.int64)
    for block, orbit in enumerate(model.gram_orbits):
        local = np.zeros(int(orbit.variable.size), dtype=np.int64)
        for member in orbit.parity_members:
            element = orbit.image_elements[member]
            acted_basis = [
                model_builder.exponent_image(item, element)
                for item in orbit.basis
            ]
            for row, left in enumerate(acted_basis):
                for column, right in enumerate(acted_basis):
                    exponent = tuple(
                        (int(x) + int(y)) // 2
                        for x, y in zip(left, right)
                    )
                    derivative = monomial_derivative(exponent, A, direction)
                    if derivative:
                        local[int(orbit.entry_ids[row, column])] += derivative
        output[int(offsets[block]) : int(offsets[block + 1])] = local
    return output


def entering_rank_one_rows(model):
    """Return exact q-coordinate rows for the positive entering terms."""
    offsets = np.cumsum(
        [0] + [int(orbit.variable.size) for orbit in model.gram_orbits],
        dtype=np.int64,
    )
    zero_vertices = set(map(int, np.flatnonzero(A == 0)))
    factors = []
    for entering_vertex in (0, 3):
        for block, orbit in enumerate(model.gram_orbits):
            for member in orbit.parity_members:
                if member[entering_vertex] != 1:
                    continue
                element = orbit.image_elements[member]
                acted_basis = [
                    model_builder.exponent_image(item, element)
                    for item in orbit.basis
                ]
                vector = np.zeros(len(orbit.basis), dtype=np.int64)
                for index, exponent in enumerate(acted_basis):
                    if exponent[entering_vertex] != 1:
                        continue
                    if any(
                        exponent[zero] != 0
                        for zero in zero_vertices
                        if zero != entering_vertex
                    ):
                        continue
                    vector[index] = 1
                if not np.any(vector):
                    continue
                matrix = np.outer(vector, vector)
                local = np.bincount(
                    orbit.entry_ids.reshape(-1),
                    weights=matrix.reshape(-1),
                    minlength=int(orbit.variable.size),
                ).astype(np.int64)
                row = sp.csr_matrix(
                    (
                        local[local != 0],
                        (
                            np.zeros(np.count_nonzero(local), dtype=np.int32),
                            int(offsets[block]) + np.flatnonzero(local),
                        ),
                    ),
                    shape=(1, int(offsets[-1])),
                    dtype=np.int64,
                )
                factors.append(
                    (
                        entering_vertex,
                        block,
                        tuple(map(int, vector)),
                        row,
                    )
                )
    return factors


def main() -> None:
    global model_builder
    model_builder = load_module(
        "codex_r10_zero_nu_entering_base", BASE_PATH
    )
    model = model_builder.build_model()
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    kernel_archive = np.load(KERNEL_PATH, allow_pickle=False)
    z = exact_kernel(kernel_archive)
    live = equality["live_multiplier_orbits"].astype(np.int32)

    multiplier_1 = multiplier_derivative(model, H1)
    multiplier_2 = multiplier_derivative(model, H2)
    multiplier_sum = multiplier_1 + multiplier_2
    if np.count_nonzero(multiplier_sum[live]) != 0:
        raise AssertionError("live multiplier derivatives do not cancel")

    direct = direct_gram_derivative(model, H1)
    direct += direct_gram_derivative(model, H2)
    factors = entering_rank_one_rows(model)
    if len(factors) != 32:
        raise AssertionError(f"expected 32 entering factors, got {len(factors)}")
    entering = sum((item[3] for item in factors), sp.csr_matrix((1, 8647)))
    if entering.nnz == 0:
        raise AssertionError("entering Gram functional is zero in ambient space")

    factor_residuals = []
    for _vertex, _block, _vector, row in factors:
        product = row @ z
        factor_residuals.append(
            int(np.max(np.abs(product.data))) if product.nnz else 0
        )
    direct_on_face = sp.csr_matrix(direct.reshape(1, -1)) @ z
    entering_on_face = entering @ z
    difference_on_face = (
        sp.csr_matrix(direct.reshape(1, -1)) - entering
    ) @ z
    maxima = {
        "factor_times_Z": max(factor_residuals),
        "direct_times_Z": (
            int(np.max(np.abs(direct_on_face.data)))
            if direct_on_face.nnz
            else 0
        ),
        "entering_times_Z": (
            int(np.max(np.abs(entering_on_face.data)))
            if entering_on_face.nnz
            else 0
        ),
        "difference_times_Z": (
            int(np.max(np.abs(difference_on_face.data)))
            if difference_on_face.nnz
            else 0
        ),
    }
    if any(maxima.values()):
        raise AssertionError(f"exact face residual: {maxima}")

    print("ZERO_NU_ENTERING_DERIVATIVE_AUDIT_PASS")
    print(f"base_sha256={sha256(BASE_PATH)}")
    print(f"equality_sha256={sha256(EQUALITY_PATH)}")
    print(f"kernel_sha256={sha256(KERNEL_PATH)}")
    print(
        "multiplier_live_nonzeros="
        f"{np.count_nonzero(multiplier_sum[live])}"
        f" individual_live_nonzeros="
        f"{np.count_nonzero(multiplier_1[live])},"
        f"{np.count_nonzero(multiplier_2[live])}"
    )
    print(
        f"entering_rank_one_factors={len(factors)}"
        f" ambient_functional_nnz={entering.nnz}"
        f" ambient_functional_l1={int(np.sum(np.abs(entering.data)))}"
    )
    print(f"exact_face_residuals={maxima}")
    print(
        "conclusion=valid_nonzero_ambient_PSD_sum_but_redundant_on_"
        "sealed_face; added_face_rank=0"
    )


if __name__ == "__main__":
    main()
