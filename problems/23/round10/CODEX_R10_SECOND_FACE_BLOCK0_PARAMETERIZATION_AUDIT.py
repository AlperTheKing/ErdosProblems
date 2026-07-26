"""Independent exact audit of the 582-to-436 second-face artifact.

The audit rebuilds all 3,388 annihilation constraints from the pinned raw
model artifacts, compares their canonical CSR representation entrywise,
checks rank and kernel dimension at primes disjoint from the producer, and
gates the 132-coordinate principal chart used for the PSD cone.  Arithmetic
that reaches a theorem claim is integer-exact.  No optimizer is called.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
CANONICAL_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EXACT_Z_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
ROW_DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
SPACE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
EXPOSURE_PATH = (
    HERE / "CODEX_R10_SECOND_FACE_BLOCK0_RANK22_EXACT_data.npz"
)
PRODUCER_PATH = HERE / "CODEX_R10_SECOND_FACE_BLOCK0_PARAMETERIZATION.py"
EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "canonical": "2FD5C5D55D87828DD8FF8121FB2644C61DAC78166736B2B066A9A582140C1799",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "exact_z": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "row_data": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "space": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
    "exposure": "49E4158C0CC2CBFF26989C8C87D850316E49E1F0F8E12104EA3D66AF847AB091",
}
AUDIT_PRIMES = (2_000_003, 2_000_029, 2_000_039)
INT64_LIMIT = (1 << 63) - 1


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


def unpack_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.int64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=np.int64,
    )


def canonical_csr(matrix: sp.csr_matrix) -> sp.csr_matrix:
    output = matrix.tocsr(copy=True)
    output.sum_duplicates()
    output.eliminate_zeros()
    output.sort_indices()
    return output


def assert_csr_equal(left: sp.csr_matrix, right: sp.csr_matrix) -> None:
    left = canonical_csr(left)
    right = canonical_csr(right)
    if left.shape != right.shape:
        raise AssertionError(f"CSR shape mismatch: {left.shape}/{right.shape}")
    if not np.array_equal(left.indptr, right.indptr):
        raise AssertionError("CSR row-pointer mismatch")
    if not np.array_equal(left.indices, right.indices):
        raise AssertionError("CSR column-index mismatch")
    if not np.array_equal(left.data, right.data):
        difference = left - right
        difference.eliminate_zeros()
        maximum = max(
            (abs(int(value)) for value in difference.data),
            default=0,
        )
        raise AssertionError(
            f"CSR value mismatch: nnz={difference.nnz}, max={maximum}"
        )


def modular_rank(matrix: sp.csr_matrix, prime: int) -> int:
    pivots: dict[int, dict[int, int]] = {}
    matrix = canonical_csr(matrix)
    for row_index in range(matrix.shape[0]):
        start = int(matrix.indptr[row_index])
        stop = int(matrix.indptr[row_index + 1])
        row = {
            int(column): int(value) % prime
            for column, value in zip(
                matrix.indices[start:stop], matrix.data[start:stop]
            )
            if int(value) % prime
        }
        while row:
            pivot = min(row)
            base = pivots.get(pivot)
            if base is None:
                inverse = pow(row[pivot], -1, prime)
                pivots[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            for column, value in base.items():
                updated = (
                    row.get(column, 0) - factor * value
                ) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return len(pivots)


def safe_product(
    left: sp.csr_matrix, right: sp.csr_matrix, name: str
) -> tuple[sp.csr_matrix, int]:
    left = canonical_csr(left)
    right = canonical_csr(right)
    row_nnz = max(
        (
            int(left.indptr[index + 1] - left.indptr[index])
            for index in range(left.shape[0])
        ),
        default=0,
    )
    left_max = max(
        (abs(int(value)) for value in left.data),
        default=0,
    )
    right_max = max(
        (abs(int(value)) for value in right.data),
        default=0,
    )
    conservative_bound = row_nnz * left_max * right_max
    if conservative_bound >= INT64_LIMIT:
        raise AssertionError(
            f"{name}: conservative int64 bound {conservative_bound}"
        )
    product = canonical_csr(left @ right)
    return product, conservative_bound


def build_annihilation_q(
    ids: np.ndarray, range_rows: np.ndarray
) -> sp.csr_matrix:
    output_rows: list[int] = []
    output_columns: list[int] = []
    output_values: list[int] = []
    for matrix_row in range(154):
        for range_index in range(22):
            coefficients: dict[int, int] = {}
            for matrix_column in range(154):
                orbit_id = int(ids[matrix_row, matrix_column])
                value = int(range_rows[range_index, matrix_column])
                coefficients[orbit_id] = (
                    coefficients.get(orbit_id, 0) + value
                )
            output_row = matrix_row * 22 + range_index
            for orbit_id in sorted(coefficients):
                value = coefficients[orbit_id]
                if value:
                    output_rows.append(output_row)
                    output_columns.append(orbit_id)
                    output_values.append(value)
    return canonical_csr(
        sp.csr_matrix(
            (
                np.asarray(output_values, dtype=np.int64),
                (
                    np.asarray(output_rows, dtype=np.int32),
                    np.asarray(output_columns, dtype=np.int32),
                ),
            ),
            shape=(3388, 1946),
            dtype=np.int64,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True, type=Path)
    args = parser.parse_args()
    args.artifact = args.artifact.resolve()
    if not args.artifact.is_file():
        parser.error(f"artifact does not exist: {args.artifact}")
    return args


def main() -> None:
    args = parse_args()
    paths = {
        "base": BASE_PATH,
        "canonical": CANONICAL_PATH,
        "blowup": BLOWUP_PATH,
        "exact_z": EXACT_Z_PATH,
        "row_data": ROW_DATA_PATH,
        "space": SPACE_PATH,
        "exposure": EXPOSURE_PATH,
    }
    observed = {name: sha256(path) for name, path in paths.items()}
    if observed != EXPECTED_SHA256:
        raise AssertionError(f"live source hash mismatch: {observed}")

    artifact = np.load(args.artifact, allow_pickle=False)
    for name, digest in observed.items():
        sealed = str(artifact[f"{name}_sha256"][0])
        if sealed != digest:
            raise AssertionError(
                f"artifact source hash mismatch for {name}: {sealed}"
            )

    builder = load_module("face2_audit_base", BASE_PATH)
    canonical = load_module("face2_audit_canonical", CANONICAL_PATH)
    model = builder.build_model()
    if len(model.cuts) != 56:
        raise AssertionError("fixed model no longer has 56 cuts")
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    exact_archive = np.load(EXACT_Z_PATH, allow_pickle=False)
    exposure = np.load(EXPOSURE_PATH, allow_pickle=False)
    exact_z = unpack_csr(exact_archive, "exact_basis")
    block_z = canonical_csr(exact_z[:1946, :582])
    free = canonical.free_coordinates(blowup, model)[0]
    if len(free) != 154:
        raise AssertionError(f"old block-0 order changed: {len(free)}")
    ids = model.gram_orbits[0].entry_ids[
        np.ix_(free, free)
    ].astype(np.int64)
    if not np.array_equal(ids, ids.T):
        raise AssertionError("block-0 quotient entry map is not symmetric")
    center = exposure["center_matrix"].astype(np.int64)
    if center.shape != (154, 154) or not np.array_equal(center, center.T):
        raise AssertionError("exposure matrix is not symmetric order 154")
    exposure_pivots = exposure["pivot_columns"].astype(np.int32)
    if exposure_pivots.shape != (22,):
        raise AssertionError("exposure pivot count changed")
    range_rows = center[exposure_pivots]
    range_row_csr = sp.csr_matrix(range_rows)
    range_row_ranks = [
        modular_rank(range_row_csr, prime) for prime in AUDIT_PRIMES
    ]
    if range_row_ranks != [22, 22, 22]:
        raise AssertionError(
            f"exposure range-row ranks {range_row_ranks}"
        )

    annihilation_q = build_annihilation_q(ids, range_rows)
    constraints, constraint_product_bound = safe_product(
        annihilation_q, block_z, "annihilation_q times block_z"
    )
    stored_constraints = unpack_csr(
        artifact, "second_face_constraints"
    )
    assert_csr_equal(constraints, stored_constraints)
    if constraints.shape != (3388, 582):
        raise AssertionError(f"constraint shape {constraints.shape}")

    constraint_ranks = [
        modular_rank(constraints, prime) for prime in AUDIT_PRIMES
    ]
    if constraint_ranks != [146, 146, 146]:
        raise AssertionError(
            f"fresh-prime constraint ranks {constraint_ranks}"
        )
    basis = unpack_csr(artifact, "second_face_basis")
    if basis.shape != (582, 436):
        raise AssertionError(f"basis shape {basis.shape}")
    maximum_basis = max(
        (abs(int(value)) for value in basis.data),
        default=0,
    )
    if maximum_basis >= INT64_LIMIT:
        raise AssertionError("basis entry is outside int64")
    residual, kernel_product_bound = safe_product(
        constraints, basis, "constraints times basis"
    )
    if residual.nnz:
        raise AssertionError(
            f"exact all-row kernel residual has {residual.nnz} entries"
        )
    basis_ranks = [
        modular_rank(basis, prime) for prime in AUDIT_PRIMES
    ]
    if basis_ranks != [436, 436, 436]:
        raise AssertionError(f"fresh-prime basis ranks {basis_ranks}")
    if 582 - constraint_ranks[0] != basis_ranks[0]:
        raise AssertionError("basis does not span the full exact kernel")

    stored_constraint_ranks = [
        int(value) for value in artifact["constraint_ranks"]
    ]
    stored_basis_ranks = [
        int(value) for value in artifact["kernel_ranks"]
    ]
    if stored_constraint_ranks != [146, 146, 146]:
        raise AssertionError("producer constraint ranks changed")
    if stored_basis_ranks != [436, 436, 436]:
        raise AssertionError("producer kernel ranks changed")
    if int(artifact["second_face_constraint_rank"][0]) != 146:
        raise AssertionError("sealed constraint-rank field changed")
    if int(artifact["new_block0_face_dimension"][0]) != 436:
        raise AssertionError("sealed face-dimension field changed")

    exposure_kernel = np.asarray(
        [
            [int(value) for value in row]
            for row in exposure["common_kernel_decimal"]
        ],
        dtype=np.int64,
    )
    if exposure_kernel.shape != (132, 154):
        raise AssertionError(
            f"exposure kernel shape {exposure_kernel.shape}"
        )
    exposure_kernel_csr = sp.csr_matrix(exposure_kernel)
    center_csr = sp.csr_matrix(center)
    center_kernel, center_kernel_bound = safe_product(
        center_csr,
        exposure_kernel_csr.T.tocsr(),
        "center times exposure kernel",
    )
    if center_kernel.nnz:
        raise AssertionError("exposure kernel does not annihilate center")
    center_ranks = [
        modular_rank(center_csr, prime) for prime in AUDIT_PRIMES
    ]
    exposure_kernel_ranks = [
        modular_rank(exposure_kernel_csr, prime)
        for prime in AUDIT_PRIMES
    ]
    if center_ranks != [22, 22, 22]:
        raise AssertionError(f"center ranks {center_ranks}")
    if exposure_kernel_ranks != [132, 132, 132]:
        raise AssertionError(
            f"exposure kernel ranks {exposure_kernel_ranks}"
        )
    principal = [
        int(value) for value in artifact["new_principal_indices"]
    ]
    if len(principal) != 132 or len(set(principal)) != 132:
        raise AssertionError("principal chart does not have 132 indices")
    chart = sp.csr_matrix(exposure_kernel[:, principal])
    chart_ranks = [
        modular_rank(chart, prime) for prime in AUDIT_PRIMES
    ]
    if chart_ranks != [132, 132, 132]:
        raise AssertionError(f"principal chart ranks {chart_ranks}")

    producer_primes = {
        int(value) for value in artifact["rank_primes"]
    }
    if producer_primes.intersection(AUDIT_PRIMES):
        raise AssertionError("audit primes are not disjoint")

    output = {
        "status": "PASS",
        "artifact": str(args.artifact),
        "artifact_sha256": sha256(args.artifact),
        "producer_source_sha256": sha256(PRODUCER_PATH),
        "source_hashes": observed,
        "constraints": {
            "shape": [3388, 582],
            "rows_compared_entrywise": 3388,
            "nnz": int(constraints.nnz),
            "fresh_primes": list(AUDIT_PRIMES),
            "fresh_prime_ranks": constraint_ranks,
            "exact_rank": 146,
        },
        "kernel": {
            "shape": [582, 436],
            "nnz": int(basis.nnz),
            "maximum_absolute_entry": maximum_basis,
            "fresh_prime_ranks": basis_ranks,
            "exact_residual_nnz": int(residual.nnz),
            "dimension": 436,
        },
        "exposure": {
            "center_ranks": center_ranks,
            "range_row_ranks": range_row_ranks,
            "kernel_ranks": exposure_kernel_ranks,
            "center_kernel_residual_nnz": int(center_kernel.nnz),
            "principal_chart_ranks": chart_ranks,
            "principal_chart_order": 132,
        },
        "int64_conservative_bounds": {
            "constraint_product": constraint_product_bound,
            "kernel_replay_product": kernel_product_bound,
            "center_kernel_product": center_kernel_bound,
            "limit": INT64_LIMIT,
        },
        "logical_result": (
            "For symmetric block-0 matrices on the first face, the 3388 "
            "constraints are equivalent to support in ker(S). The invertible "
            "132-coordinate chart makes its principal PSD cone exactly "
            "equivalent to the original constrained PSD cone."
        ),
        "solver_called": False,
        "third_face_searched": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
