"""Reconstruct the block-0-only exact zero-bound dual from the SCS archive.

The numerical archive is steering only.  This guarded program rebuilds the
exact ten-dimensional equality-dual pencil, constructs its canonical block-0
PSD representative, proves the common support exactly, rationalizes only the
ten pencil coefficients, and writes a new exact semantic JSON candidate.

Default execution is build-only.  Reconstruction requires ``--reconstruct``
and three new explicit output paths.  Existing files are never overwritten.
No conic solver is called.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import scipy.sparse as sp
from sympy import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
NPZ_PATH = (
    HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz"
)
VERIFIER_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER.py"
ROW_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
EXPECTED_SHA256 = {
    "npz": "6DFD3A35C8B93144D45479BEE1E00BB72F82797BBF6CC6CA59A7D56E573C1982",
    "verifier": "9366CCD624C32CAC644D9E6DE79F17EA758450893EAE77D935A2AFFE42F72A60",
    "row_source": "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
}
RANK_PRIMES = (1_000_003, 2_000_003, 998_244_353)
BLOCK_ZERO_FACE_DIMENSION = 582
EXPECTED_LAMBDA_RANK = 378
EXPECTED_LAMBDA_NULLITY = 10
EXPECTED_SUPPORT_RANK = 73


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def primitive_integer_row(values: list[int]) -> list[int]:
    common = 0
    for value in values:
        common = math.gcd(common, abs(int(value)))
    if common == 0:
        raise ValueError("zero nullspace row")
    output = [int(value) // common for value in values]
    first = next(value for value in output if value)
    if first < 0:
        output = [-value for value in output]
    return output


def independent_row_indices_mod(
    matrix: sp.csr_matrix, prime: int
) -> list[int]:
    echelon: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row_index in range(matrix.shape[0]):
        row = {
            int(matrix.indices[cursor]):
            int(matrix.data[cursor]) % prime
            for cursor in range(
                matrix.indptr[row_index], matrix.indptr[row_index + 1]
            )
            if int(matrix.data[cursor]) % prime
        }
        while row:
            pivot = min(row)
            base = echelon.get(pivot)
            if base is None:
                inverse = pow(row[pivot], prime - 2, prime)
                echelon[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                selected.append(row_index)
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
    return selected


def exact_sparse_matvec_zero(
    matrix: sp.csr_matrix, vector: list[int]
) -> bool:
    for row in range(matrix.shape[0]):
        total = 0
        for cursor in range(matrix.indptr[row], matrix.indptr[row + 1]):
            total += (
                int(matrix.data[cursor])
                * int(vector[int(matrix.indices[cursor])])
            )
        if total:
            return False
    return True


def fraction_json(value: Fraction) -> int | str:
    if value.denominator == 1:
        return int(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def upper_triangle_json(
    matrix: list[list[Fraction]],
) -> list[int | str]:
    return [
        fraction_json(matrix[row][column])
        for row in range(len(matrix))
        for column in range(row, len(matrix))
    ]


def common_support_rows(
    numerator_matrices: list[np.ndarray],
    prime: int,
) -> tuple[list[int], np.ndarray]:
    stacked = np.vstack(numerator_matrices)
    maximum = max(abs(int(value)) for value in stacked.flat)
    if maximum >= (1 << 62):
        raise OverflowError("support pencil does not fit exact int64")
    sparse = sp.csr_matrix(stacked.astype(np.int64))
    selected = independent_row_indices_mod(sparse, prime)
    rows = stacked[selected, :]
    return selected, rows


def independent_columns_mod(
    matrix: np.ndarray, prime: int
) -> list[int]:
    maximum = max(abs(int(value)) for value in matrix.flat)
    if maximum >= (1 << 62):
        raise OverflowError("support row basis does not fit exact int64")
    transposed = sp.csr_matrix(matrix.T.astype(np.int64))
    return independent_row_indices_mod(transposed, prime)


def matrix_linear_combination(
    matrices: list[np.ndarray],
    coefficients: list[Fraction],
    denominator: int,
    indices: list[int] | None = None,
) -> list[list[Fraction]]:
    if indices is None:
        indices = list(range(matrices[0].shape[0]))
    return [
        [
            sum(
                (
                    coefficients[index]
                    * int(matrices[index][row, column])
                    for index in range(len(matrices))
                ),
                Fraction(0),
            )
            / denominator
            for column in indices
        ]
        for row in indices
    ]


def exact_trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum(
        (matrix[index][index] for index in range(len(matrix))),
        Fraction(0),
    )


def build_pencil():
    paths = {
        "npz": NPZ_PATH,
        "verifier": VERIFIER_PATH,
        "row_source": ROW_SOURCE_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input hash mismatch: {hashes}")
    verifier = load_module(
        "codex_r10_exact_dual_reconstruct_verifier", VERIFIER_PATH
    )
    row_source = load_module(
        "codex_r10_exact_dual_reconstruct_rows", ROW_SOURCE_PATH
    )
    context = verifier.build_context()
    archive = np.load(NPZ_PATH, allow_pickle=False)

    face_map = (context.affine_q @ context.exact_basis).tocsr()
    if face_map.shape != (388, 2518):
        raise AssertionError("exact face-affine map shape mismatch")
    outside = face_map[:, BLOCK_ZERO_FACE_DIMENSION:].T.tocsr()
    lambda_constraints = sp.vstack(
        [
            context.affine_nu.T,
            sp.csr_matrix(context.affine_rhs.reshape(1, -1)),
            outside,
        ],
        format="csr",
        dtype=np.int64,
    )
    if lambda_constraints.shape != (2463, 388):
        raise AssertionError("lambda support system shape mismatch")
    ranks = [
        len(independent_row_indices_mod(lambda_constraints, prime))
        for prime in RANK_PRIMES
    ]
    if ranks != [EXPECTED_LAMBDA_RANK] * len(RANK_PRIMES):
        raise AssertionError(f"lambda support ranks drifted: {ranks}")
    selected_rows = independent_row_indices_mod(
        lambda_constraints, RANK_PRIMES[0]
    )
    selected_dense = (
        lambda_constraints[selected_rows, :].toarray().astype(np.int64)
    )
    selected_domain = DomainMatrix.from_list_sympy(
        EXPECTED_LAMBDA_RANK,
        388,
        selected_dense.tolist(),
    ).convert_to(ZZ)
    null_domain = selected_domain.nullspace()
    if null_domain.shape != (EXPECTED_LAMBDA_NULLITY, 388):
        raise AssertionError(
            f"exact lambda nullspace shape drifted: {null_domain.shape}"
        )
    lambda_rows = [
        primitive_integer_row([int(value) for value in row])
        for row in null_domain.to_list()
    ]
    for row in lambda_rows:
        if not exact_sparse_matvec_zero(lambda_constraints, row):
            raise AssertionError("exact lambda basis fails the full system")

    block = context.blocks[0]
    orbit = context.base.gram_orbits[0]
    grouped_rows = [list(map(int, row)) for row in block.kernel_rows]
    ambient_z, ambient_denominator, _pivots, free = (
        row_source.integer_kernel_parameter(
            grouped_rows, len(orbit.basis)
        )
    )
    if len(free) != 154 or free != [
        index
        for index in range(len(orbit.basis))
        if index not in set(_pivots)
    ]:
        raise AssertionError("block-0 quotient ordering mismatch")
    if ambient_denominator != 24:
        raise AssertionError("block-0 exact kernel denominator drift")
    entry_ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(
        entry_ids.reshape(-1), minlength=block.qdim
    ).astype(np.int64)
    if np.any(multiplicities == 0):
        raise AssertionError("empty block-0 entry orbit")
    multiplicity_lcm = 1
    for value in multiplicities:
        multiplicity_lcm = math.lcm(multiplicity_lcm, int(value))
    z_domain = ambient_z
    numerator_matrices: list[np.ndarray] = []
    pencil_denominator = (
        multiplicity_lcm * ambient_denominator * ambient_denominator
    )
    for lambda_row in lambda_rows:
        coefficient = np.asarray(
            context.affine_q.T
            @ np.asarray(lambda_row, dtype=np.int64)
        ).reshape(-1)
        local = [int(value) for value in coefficient[: block.qdim]]
        ambient_numerator = [
            [
                local[int(entry_ids[row, column])]
                * (
                    multiplicity_lcm
                    // int(
                        multiplicities[
                            int(entry_ids[row, column])
                        ]
                    )
                )
                for column in range(len(orbit.basis))
            ]
            for row in range(len(orbit.basis))
        ]
        ambient_domain = DomainMatrix.from_list_sympy(
            len(orbit.basis),
            len(orbit.basis),
            ambient_numerator,
        ).convert_to(ZZ)
        quotient_domain = (
            z_domain.transpose()
            .matmul(ambient_domain)
            .matmul(z_domain)
        )
        numerator_matrices.append(
            np.asarray(
                [
                    [int(value) for value in row]
                    for row in quotient_domain.to_list()
                ],
                dtype=object,
            )
        )

    selected_support_rows, support_rows = common_support_rows(
        numerator_matrices, RANK_PRIMES[0]
    )
    support_ranks = []
    stacked = np.vstack(numerator_matrices)
    maximum_stacked = max(abs(int(value)) for value in stacked.flat)
    if maximum_stacked >= (1 << 62):
        raise OverflowError("exact support pencil exceeds int64")
    stacked_sparse = sp.csr_matrix(stacked.astype(np.int64))
    for prime in RANK_PRIMES:
        support_ranks.append(
            len(independent_row_indices_mod(stacked_sparse, prime))
        )
    if support_ranks != [EXPECTED_SUPPORT_RANK] * len(RANK_PRIMES):
        raise AssertionError(
            f"common-support rank drifted: {support_ranks}"
        )
    support_coordinates = independent_columns_mod(
        support_rows, RANK_PRIMES[0]
    )
    if len(support_coordinates) != EXPECTED_SUPPORT_RANK:
        raise AssertionError("support coordinate count mismatch")
    for prime in RANK_PRIMES:
        rank = len(
            independent_row_indices_mod(
                sp.csr_matrix(
                    support_rows[:, support_coordinates]
                    .astype(np.int64)
                    .T
                ),
                prime,
            )
        )
        if rank != EXPECTED_SUPPORT_RANK:
            raise AssertionError(
                f"support pivot loses rank modulo {prime}"
            )

    raw_lambda = archive["dual_affine_equalities"].astype(np.float64)
    lambda_columns = np.asarray(lambda_rows, dtype=np.float64).T
    column_norms = np.linalg.norm(lambda_columns, axis=0)
    normalized_columns = lambda_columns / column_norms[None, :]
    normalized_coefficients, *_ = np.linalg.lstsq(
        normalized_columns, raw_lambda, rcond=None
    )
    raw_coefficients = normalized_coefficients / column_norms
    projected_lambda = lambda_columns @ raw_coefficients
    projection_relative_residual = float(
        np.linalg.norm(projected_lambda - raw_lambda)
        / np.linalg.norm(raw_lambda)
    )
    anchor = int(np.argmax(np.abs(raw_coefficients)))
    ratios = raw_coefficients / abs(raw_coefficients[anchor])

    reconstruction = None
    denominator_attempts = [
        10,
        100,
        1_000,
        10_000,
        100_000,
        1_000_000,
        10_000_000,
        100_000_000,
    ]
    attempt_records = []
    for maximum_denominator in denominator_attempts:
        coefficients = [
            Fraction(float(value)).limit_denominator(maximum_denominator)
            for value in ratios
        ]
        reduced = matrix_linear_combination(
            numerator_matrices,
            coefficients,
            pencil_denominator,
            support_coordinates,
        )
        minimum_float = float(
            np.linalg.eigvalsh(
                np.asarray(
                    [
                        [float(value) for value in row]
                        for row in reduced
                    ]
                )
            )[0]
        )
        record: dict[str, Any] = {
            "maximum_denominator": maximum_denominator,
            "minimum_reduced_eigenvalue_float": minimum_float,
        }
        if minimum_float <= 1e-10:
            record["exact_test"] = "skipped_nonpositive_steering"
            attempt_records.append(record)
            continue
        try:
            exact_rank, exact_pivots = verifier.exact_psd(
                reduced,
                f"reduced dual at denominator {maximum_denominator}",
            )
        except ValueError as error:
            record["exact_test"] = f"FAIL: {error}"
            attempt_records.append(record)
            continue
        record["exact_test"] = "PASS"
        record["exact_rank"] = exact_rank
        record["minimum_exact_pivot"] = str(min(exact_pivots))
        attempt_records.append(record)
        if exact_rank == EXPECTED_SUPPORT_RANK:
            reconstruction = (
                maximum_denominator,
                coefficients,
                reduced,
                exact_pivots,
            )
            break
    if reconstruction is None:
        raise RuntimeError(
            "no rational coefficient attempt is positive definite "
            "on the exact common support"
        )
    return {
        "hashes": hashes,
        "verifier": verifier,
        "context": context,
        "archive": archive,
        "lambda_constraints": lambda_constraints,
        "lambda_ranks": ranks,
        "selected_lambda_rows": selected_rows,
        "lambda_rows": lambda_rows,
        "numerator_matrices": numerator_matrices,
        "pencil_denominator": pencil_denominator,
        "multiplicity_lcm": multiplicity_lcm,
        "ambient_denominator": ambient_denominator,
        "support_ranks": support_ranks,
        "selected_support_rows": selected_support_rows,
        "support_coordinates": support_coordinates,
        "projection_relative_residual": projection_relative_residual,
        "raw_coefficients": raw_coefficients,
        "ratios": ratios,
        "attempt_records": attempt_records,
        "reconstruction": reconstruction,
    }


def build_candidate(state) -> tuple[dict[str, Any], dict[str, Any]]:
    verifier = state["verifier"]
    context = state["context"]
    (
        maximum_denominator,
        coefficients,
        _reduced,
        reduced_pivots,
    ) = state["reconstruction"]
    full_matrix = matrix_linear_combination(
        state["numerator_matrices"],
        coefficients,
        state["pencil_denominator"],
    )
    full_rank, full_pivots = verifier.exact_psd(
        full_matrix, "full block-0 dual"
    )
    if full_rank != EXPECTED_SUPPORT_RANK:
        raise AssertionError(f"full block-0 rank is {full_rank}")
    trace = exact_trace(full_matrix)
    if trace <= 0:
        raise AssertionError("block-0 dual has nonpositive trace")
    scale = Fraction(2, 1) / trace
    full_matrix = [
        [scale * value for value in row] for row in full_matrix
    ]
    scaled_trace = exact_trace(full_matrix)
    if scaled_trace != 2:
        raise AssertionError("dual trace normalization failed")
    beta = scaled_trace - 1
    if beta != 1:
        raise AssertionError("margin dual normalization failed")

    lambda_unscaled = [
        sum(
            (
                coefficients[index]
                * state["lambda_rows"][index][coordinate]
                for index in range(EXPECTED_LAMBDA_NULLITY)
            ),
            Fraction(0),
        )
        for coordinate in range(388)
    ]
    lam = [scale * value for value in lambda_unscaled]
    if sum(
        (
            Fraction(int(context.affine_rhs[index])) * lam[index]
            for index in range(388)
        ),
        Fraction(0),
    ) != 0:
        raise AssertionError("scaled exact objective is not zero")

    psd_payload = []
    for block in context.blocks:
        if block.order <= 1:
            continue
        matrix = (
            full_matrix
            if block.index == 0
            else [
                [Fraction(0) for _ in range(block.order)]
                for _ in range(block.order)
            ]
        )
        psd_payload.append(
            {
                "block": block.index,
                "order": block.order,
                "upper_triangle": upper_triangle_json(matrix),
            }
        )
    scalar_payload = [
        {"block": block, "value": 0}
        for block in verifier.EXPECTED_SCALAR_BLOCKS
    ]
    candidate = {
        "format": "R10-c5-face-exact-semantic-dual-v1",
        "mode": "zero_bound",
        "pinned_sha256": context.hashes,
        "dual": {
            "affine_equalities": [fraction_json(value) for value in lam],
            "live_nu_minus_margin": [0] * 526,
            "margin_nonnegative": fraction_json(beta),
            "scalar_quotient_duals": scalar_payload,
            "psd_duals": psd_payload,
        },
    }
    metadata = {
        "classification": "zero_bound_with_necessary_face",
        "logical_scope": (
            "Every feasible primal has t=0 and block-0 quotient range "
            "contained in the exact 81-dimensional generic-pencil kernel of this dual. "
            "Primal feasibility is not established."
        ),
        "input_npz_sha256": state["hashes"]["npz"],
        "lambda_support_system": {
            "shape": list(state["lambda_constraints"].shape),
            "ranks_mod_primes": state["lambda_ranks"],
            "nullity": EXPECTED_LAMBDA_NULLITY,
            "maximum_basis_coefficient_bits": max(
                abs(int(value)).bit_length()
                for row in state["lambda_rows"]
                for value in row
            ),
        },
        "block_zero_pencil": {
            "matrices": EXPECTED_LAMBDA_NULLITY,
            "order": 154,
            "common_support_ranks_mod_primes": state["support_ranks"],
            "common_kernel_dimension": 154 - EXPECTED_SUPPORT_RANK,
            "support_coordinates": state["support_coordinates"],
            "ambient_kernel_denominator": state["ambient_denominator"],
            "entry_multiplicity_lcm": state["multiplicity_lcm"],
            "pencil_denominator": state["pencil_denominator"],
        },
        "numerical_projection": {
            "relative_lambda_residual": (
                state["projection_relative_residual"]
            ),
            "raw_coefficient_ratios": state["ratios"].tolist(),
        },
        "rational_reconstruction": {
            "accepted_maximum_denominator": maximum_denominator,
            "coefficients": [str(value) for value in coefficients],
            "attempts": state["attempt_records"],
            "full_exact_rank": full_rank,
            "minimum_reduced_exact_pivot": str(min(reduced_pivots)),
            "minimum_full_exact_pivot": str(min(full_pivots)),
            "trace_after_scaling": str(scaled_trace),
            "margin_dual": str(beta),
            "exact_objective": "0",
        },
        "claim_boundary": (
            "Not a separator and not an exposing-face/nonemptiness claim."
        ),
    }
    return candidate, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reconstruct",
        action="store_true",
        help="execute the exact pencil reconstruction",
    )
    parser.add_argument(
        "--candidate-output",
        type=Path,
        help="new exact semantic-dual JSON path",
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        help="new reconstruction metadata JSON path",
    )
    parser.add_argument(
        "--data-output",
        type=Path,
        help="new exact pencil NPZ path",
    )
    args = parser.parse_args()
    outputs = [
        args.candidate_output,
        args.metadata_output,
        args.data_output,
    ]
    if args.reconstruct and any(path is None for path in outputs):
        parser.error(
            "--reconstruct requires --candidate-output, "
            "--metadata-output, and --data-output"
        )
    if not args.reconstruct and any(path is not None for path in outputs):
        parser.error("output paths require --reconstruct")
    if args.reconstruct:
        for path in outputs:
            resolved = path.resolve()
            if resolved.exists():
                parser.error(f"refusing to overwrite {resolved}")
            if not resolved.parent.is_dir():
                parser.error(f"output directory does not exist: {resolved.parent}")
        if args.candidate_output.suffix.lower() != ".json":
            parser.error("--candidate-output must end in .json")
        if args.metadata_output.suffix.lower() != ".json":
            parser.error("--metadata-output must end in .json")
        if args.data_output.suffix.lower() != ".npz":
            parser.error("--data-output must end in .npz")
    return args


def main() -> int:
    args = parse_args()
    if not args.reconstruct:
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "scope": "build-only; no numerical archive processed",
                    "fixed_support_system": [2463, 388],
                    "expected_rank": EXPECTED_LAMBDA_RANK,
                    "expected_nullity": EXPECTED_LAMBDA_NULLITY,
                    "expected_common_support_rank": EXPECTED_SUPPORT_RANK,
                    "solver_called": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        print(
            "EXACT_DUAL_RECONSTRUCT_BUILD_ONLY_PASS "
            "solver_called=false input_processed=false"
        )
        return 0

    state = build_pencil()
    candidate, metadata = build_candidate(state)
    candidate_path = args.candidate_output.resolve()
    metadata_path = args.metadata_output.resolve()
    data_path = args.data_output.resolve()
    candidate_text = json.dumps(candidate, indent=2, sort_keys=True) + "\n"
    candidate_path.write_text(candidate_text, encoding="utf-8", newline="\n")
    metadata["candidate_sha256"] = sha256(candidate_path)
    metadata_text = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    metadata_path.write_text(metadata_text, encoding="utf-8", newline="\n")

    lambda_basis = np.asarray(state["lambda_rows"], dtype=object)
    maximum_basis = max(abs(int(value)) for value in lambda_basis.flat)
    if maximum_basis >= (1 << 62):
        raise OverflowError("lambda basis does not fit int64 NPZ")
    coefficient_numerators = np.asarray(
        [value.numerator for value in state["reconstruction"][1]],
        dtype=np.int64,
    )
    coefficient_denominators = np.asarray(
        [value.denominator for value in state["reconstruction"][1]],
        dtype=np.int64,
    )
    np.savez_compressed(
        data_path,
        format_version=np.asarray([1], dtype=np.int32),
        role=np.asarray(
            ["exact 10D zero-bound dual pencil; semantic verification required"]
        ),
        input_npz_sha256=np.asarray([state["hashes"]["npz"]]),
        candidate_sha256=np.asarray([metadata["candidate_sha256"]]),
        lambda_constraint_shape=np.asarray(
            state["lambda_constraints"].shape, dtype=np.int64
        ),
        lambda_ranks_mod_primes=np.asarray(
            state["lambda_ranks"], dtype=np.int32
        ),
        lambda_basis=lambda_basis.astype(np.int64),
        pencil_common_denominator=np.asarray(
            [state["pencil_denominator"]], dtype=np.int64
        ),
        support_ranks_mod_primes=np.asarray(
            state["support_ranks"], dtype=np.int32
        ),
        support_coordinates=np.asarray(
            state["support_coordinates"], dtype=np.int32
        ),
        coefficient_numerators=coefficient_numerators,
        coefficient_denominators=coefficient_denominators,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    print(f"CANDIDATE={candidate_path}")
    print(f"SHA256_CANDIDATE={sha256(candidate_path)}")
    print(f"METADATA={metadata_path}")
    print(f"SHA256_METADATA={sha256(metadata_path)}")
    print(f"DATA={data_path}")
    print(f"SHA256_DATA={sha256(data_path)}")
    print(
        "EXACT_DUAL_ZERO_BOUND_RECONSTRUCTED "
        "separator=false exposing_face=false exact_verification_required=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
