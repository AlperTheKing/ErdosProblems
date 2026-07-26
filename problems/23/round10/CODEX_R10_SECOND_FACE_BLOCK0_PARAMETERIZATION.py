"""Exact parameterization and dimension of the certified second face.

The order-154 quotient block R must annihilate the rank-22 exposure range.
This script expresses that condition in the sealed 582-dimensional invariant
block-0 coordinates, reconstructs a primitive sparse 436-column integer
kernel, verifies all 3,388 exact annihilation rows, and computes the retained
affine rank.  It also certifies a 132-index principal chart for the new PSD
block.

No solver is called.  Nonemptiness of the second face is not asserted.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix


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
EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "canonical": "2FD5C5D55D87828DD8FF8121FB2644C61DAC78166736B2B066A9A582140C1799",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "exact_z": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "row_data": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "space": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
    "exposure": "49E4158C0CC2CBFF26989C8C87D850316E49E1F0F8E12104EA3D66AF847AB091",
}
PRIMES = (1_000_133, 1_000_151, 1_000_159)


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
        shape=tuple(map(int, archive[f"{name}_shape"])),
        dtype=np.int64,
    )


def pack_csr(payload: dict[str, np.ndarray], name: str, matrix: sp.csr_matrix):
    matrix = matrix.tocsr()
    payload[f"{name}_data"] = matrix.data.astype(np.int64)
    payload[f"{name}_indices"] = matrix.indices.astype(np.int32)
    payload[f"{name}_indptr"] = matrix.indptr.astype(np.int64)
    payload[f"{name}_shape"] = np.asarray(matrix.shape, dtype=np.int64)


def modular_echelon(
    matrix: sp.csr_matrix, prime: int
) -> tuple[list[int], list[int]]:
    pivots: dict[int, dict[int, int]] = {}
    selected_rows: list[int] = []
    matrix = matrix.tocsr()
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
                selected_rows.append(row_index)
                break
            factor = row[pivot]
            for column, value in base.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return selected_rows, sorted(pivots)


def primitive(values: list[int]) -> list[int]:
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(int(value)))
    if divisor:
        values = [int(value) // divisor for value in values]
    first = next((value for value in values if value), 0)
    if first < 0:
        values = [-value for value in values]
    return values


def build_annihilation_q(ids: np.ndarray, range_rows: np.ndarray):
    rows = []
    columns = []
    values = []
    for matrix_row in range(ids.shape[0]):
        orbit_ids = ids[matrix_row]
        for range_row in range(range_rows.shape[0]):
            coefficients = np.zeros(1946, dtype=np.int64)
            np.add.at(coefficients, orbit_ids, range_rows[range_row])
            nonzero = np.flatnonzero(coefficients)
            output_row = matrix_row * range_rows.shape[0] + range_row
            rows.extend([output_row] * len(nonzero))
            columns.extend(nonzero.tolist())
            values.extend(coefficients[nonzero].tolist())
    return sp.csr_matrix(
        (values, (rows, columns)),
        shape=(ids.shape[0] * range_rows.shape[0], 1946),
        dtype=np.int64,
    )


def safe_exact_product(left: sp.csr_matrix, right: sp.csr_matrix):
    absolute_left = left.copy().astype(np.float64)
    absolute_right = right.copy().astype(np.float64)
    absolute_left.data = np.abs(absolute_left.data)
    absolute_right.data = np.abs(absolute_right.data)
    bound = absolute_left @ absolute_right
    maximum_bound = float(np.max(bound.data, initial=0.0))
    if 2.0 * maximum_bound >= float(2**63 - 1):
        raise AssertionError(f"int64 product bound unsafe: {maximum_bound}")
    product = (left @ right).tocsr()
    product.eliminate_zeros()
    return product, maximum_bound


def exact_dense_zero(left: sp.csr_matrix, right: np.ndarray) -> bool:
    absolute_left = left.copy().astype(np.float64)
    absolute_left.data = np.abs(absolute_left.data)
    absolute_right = np.abs(right.astype(np.float64))
    bound = np.asarray(absolute_left @ absolute_right)
    maximum_bound = float(np.max(bound, initial=0.0))
    if 2.0 * maximum_bound >= float(2**63 - 1):
        product = left.astype(object) @ right.astype(object)
    else:
        product = left @ right.astype(np.int64)
    return not np.any(np.asarray(product))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    args.data = args.data.resolve()
    args.report = args.report.resolve()
    for path in (args.data, args.report):
        if not path.parent.is_dir():
            parser.error(f"missing output directory: {path.parent}")
        if path.exists():
            parser.error(f"refusing to overwrite: {path}")
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
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned source mismatch: {hashes}")

    builder = load_module("codex_r10_face2_parameter_base", BASE_PATH)
    canonical = load_module(
        "codex_r10_face2_parameter_canonical", CANONICAL_PATH
    )
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    exact_archive = np.load(EXACT_Z_PATH, allow_pickle=False)
    row_data = np.load(ROW_DATA_PATH, allow_pickle=False)
    space = np.load(SPACE_PATH, allow_pickle=False)
    exposure = np.load(EXPOSURE_PATH, allow_pickle=False)

    exact_z = unpack_csr(exact_archive, "exact_basis")
    block_z = exact_z[:1946, :582].tocsr()
    free = canonical.free_coordinates(blowup, model)[0]
    ids = model.gram_orbits[0].entry_ids[
        np.ix_(free, free)
    ].astype(np.int64)
    center = exposure["center_matrix"].astype(np.int64)
    exposure_pivots = exposure["pivot_columns"].astype(int)
    range_rows = center[exposure_pivots]
    annihilation_q = build_annihilation_q(ids, range_rows)
    constraints, product_bound = safe_exact_product(
        annihilation_q, block_z
    )
    if constraints.shape != (3388, 582):
        raise AssertionError(constraints.shape)

    modular = [modular_echelon(constraints, prime) for prime in PRIMES]
    ranks = [len(item[0]) for item in modular]
    if ranks != [146, 146, 146]:
        raise AssertionError(f"second-face ranks {ranks}")
    selected_rows = modular[0][0]
    selected = constraints[selected_rows].toarray().astype(np.int64)
    nullspace_dm = DomainMatrix.from_list_sympy(
        selected.shape[0], selected.shape[1], selected.tolist()
    ).convert_to(ZZ).nullspace()
    kernel_rows = [
        primitive([int(value) for value in row])
        for row in nullspace_dm.to_list()
    ]
    if len(kernel_rows) != 436:
        raise AssertionError(f"kernel size {len(kernel_rows)}")
    kernel = np.asarray(kernel_rows, dtype=object)
    maximum_kernel_bits = max(
        abs(int(value)).bit_length() for value in kernel.reshape(-1)
    )
    if maximum_kernel_bits >= 63:
        raise AssertionError(
            f"kernel coefficients exceed int64: {maximum_kernel_bits} bits"
        )
    kernel_int = kernel.astype(np.int64)
    kernel_ranks = [
        len(modular_echelon(sp.csr_matrix(kernel_int), prime)[0])
        for prime in PRIMES
    ]
    if kernel_ranks != [436, 436, 436]:
        raise AssertionError(f"kernel ranks {kernel_ranks}")
    if not exact_dense_zero(constraints, kernel.T):
        raise AssertionError("all-row exact kernel replay failed")
    kernel_csr = sp.csr_matrix(kernel_int.T)
    if kernel_csr.shape != (582, 436):
        raise AssertionError(kernel_csr.shape)

    exposure_kernel = np.asarray(
        [
            [int(value) for value in row]
            for row in exposure["common_kernel_decimal"]
        ],
        dtype=np.int64,
    )
    principal_modular = [
        modular_echelon(sp.csr_matrix(exposure_kernel), prime)
        for prime in PRIMES
    ]
    principal_indices = principal_modular[0][1]
    if (
        len(principal_indices) != 132
        or not all(item[1] == principal_indices for item in principal_modular)
    ):
        raise AssertionError("new principal chart changed across primes")

    affine_nu = unpack_csr(row_data, "affine_nu")
    affine_q = unpack_csr(row_data, "affine_gram")
    affine_y, affine_product_bound = safe_exact_product(affine_q, exact_z)
    affine_block0, affine_block0_bound = safe_exact_product(
        affine_y[:, :582], kernel_csr
    )
    affine_new = sp.hstack(
        (
            affine_nu,
            affine_block0,
            affine_y[:, 582:],
        ),
        format="csr",
    )
    if affine_new.shape != (388, 2898):
        raise AssertionError(affine_new.shape)
    affine_ranks = [
        len(modular_echelon(affine_new, prime)[0])
        for prime in PRIMES
    ]
    if affine_ranks != [384, 384, 384]:
        raise AssertionError(f"restricted affine ranks {affine_ranks}")

    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=np.int64,
    )
    slice_coefficients = exposure["slice_coefficients"].astype(np.int64)
    affine_dependencies = slice_coefficients @ lambda_basis
    if any(
        len(modular_echelon(sp.csr_matrix(affine_dependencies), prime)[0])
        != 4
        for prime in PRIMES
    ):
        raise AssertionError("affine dependency rank is not four")
    if not exact_dense_zero(
        affine_new.T.tocsr(), affine_dependencies.T
    ):
        raise AssertionError("restricted affine dependencies failed")
    rhs = row_data["affine_rhs"].astype(np.int64)
    if np.any(affine_dependencies @ rhs):
        raise AssertionError("affine dependencies do not kill RHS")

    augmented = sp.hstack(
        (affine_new, sp.csr_matrix(rhs.reshape(-1, 1))),
        format="csr",
    )
    augmented_ranks = [
        len(modular_echelon(augmented, prime)[0])
        for prime in PRIMES
    ]
    if augmented_ranks != [384, 384, 384]:
        raise AssertionError(f"augmented ranks {augmented_ranks}")


    payload: dict[str, np.ndarray] = {

        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            [
                "exact 582-to-436 second-face parameterization; "
                "build-only, nonemptiness not certified"
            ]
        ),
        **{
            f"{name}_sha256": np.asarray([value])
            for name, value in hashes.items()
        },
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "constraint_ranks": np.asarray(ranks, dtype=np.int32),
        "kernel_ranks": np.asarray(kernel_ranks, dtype=np.int32),
        "selected_constraint_rows": np.asarray(
            selected_rows, dtype=np.int32
        ),
        "exposure_range_rows": range_rows,
        "new_principal_indices": np.asarray(
            principal_indices, dtype=np.int32
        ),
        "restricted_affine_ranks": np.asarray(
            affine_ranks, dtype=np.int32
        ),
        "restricted_augmented_ranks": np.asarray(
            augmented_ranks, dtype=np.int32
        ),
        "affine_dependencies": affine_dependencies,
        "old_block0_face_dimension": np.asarray([582], dtype=np.int32),
        "second_face_constraint_rank": np.asarray([146], dtype=np.int32),
        "new_block0_face_dimension": np.asarray([436], dtype=np.int32),
        "new_block0_psd_order": np.asarray([132], dtype=np.int32),
        "total_gram_face_dimension": np.asarray([2372], dtype=np.int32),
        "total_variables_without_margin": np.asarray([2898], dtype=np.int32),
        "restricted_affine_rank": np.asarray([384], dtype=np.int32),
        "linear_solution_dimension": np.asarray([2514], dtype=np.int32),
        "product_absolute_bound": np.asarray([product_bound]),
        "affine_product_absolute_bound": np.asarray(
            [affine_product_bound]
        ),
        "affine_block0_product_absolute_bound": np.asarray(
            [affine_block0_bound]
        ),
    }
    pack_csr(payload, "second_face_constraints", constraints)
    pack_csr(payload, "second_face_basis", kernel_csr)
    np.savez_compressed(args.data, **payload)
    data_hash = sha256(args.data)

    report = "\n".join(
        [
            "# Exact parameterization of the second block-0 face",
            "",
            "## Exact dimensions",
            "",
            (
                "The 3,388 equations `R range(S)=0` have exact rank `146`. "
                "A primitive integer kernel basis of shape `582 x 436` "
                "satisfies all 3,388 rows exactly."
            ),
            "",
            (
                f"The sparse basis has `{kernel_csr.nnz}` nonzeros and "
                f"maximum coefficient bit length `{maximum_kernel_bits}`."
            ),
            "",
            (
                "The new block-0 quotient PSD order is `132`. The artifact "
                "stores 132 principal indices whose submatrix is exactly "
                "equivalent to PSD on this face."
            ),
            "",
            "## Direct finite conic model",
            "",
            "- 526 nonnegative live multiplier variables;",
            "- 2,372 exact Gram-face coordinates in total;",
            "- 2,898 variables after fixing the certified margin to zero;",
            "- 384 independent affine equalities;",
            "- linear solution-space dimension 2,514;",
            (
                "- block 0 is an order-132 PSD cone represented in a "
                "436-dimensional invariant linear subspace; all other "
                "first-face quotient blocks are unchanged."
            ),
            "",
            (
                "The four exact rank-drop slice duals are precisely four "
                "independent dependencies among the 388 old affine rows "
                "after restriction; the augmented affine rank is also 384."
            ),
            "",
            "## Scope",
            "",
            (
                "This is a direct finite conic model of the certified "
                "necessary face. It does not certify that the face is "
                "nonempty."
            ),
            "",
            f"Data SHA-256: `{data_hash}`",
            "",
        ]
    )
    args.report.write_text(report, encoding="utf-8", newline="\n")
    summary = {
        "status": "PASS",
        "constraint_shape": list(map(int, constraints.shape)),
        "constraint_rank": 146,
        "basis_shape": list(map(int, kernel_csr.shape)),
        "basis_nnz": int(kernel_csr.nnz),
        "basis_max_bits": maximum_kernel_bits,
        "new_block0_face_dimension": 436,
        "new_block0_psd_order": 132,
        "principal_indices": principal_indices,
        "restricted_affine_rank": 384,
        "total_variables_without_margin": 2898,
        "linear_solution_dimension": 2514,
        "data": str(args.data),
        "data_sha256": data_hash,
        "report": str(args.report),
        "scope": "direct finite conic model; nonemptiness not certified",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
