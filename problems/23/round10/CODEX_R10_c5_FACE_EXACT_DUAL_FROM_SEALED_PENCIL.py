"""Construct an exact zero-bound dual from the sealed ten-dimensional pencil.

This add-only runner independently rebuilds and gates the sealed lambda/q
pencil, maps it to canonical block-0 quotient matrices, proves their common
73-dimensional generic common support, and rationalizes a positive-definite member there.
No conic solver is called.  Existing outputs are never overwritten.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import scipy.sparse as sp
from sympy import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
CORE_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_DUAL_RECONSTRUCT.py"
PENCIL_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
PENCIL_SOURCE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE.py"
EXPECTED_SHA256 = {
    "core": "F702C89667CC929E9CF95D6DEB1CCA7F6B3F562CB9049A48CEF6C311F8C2B2F9",
    "pencil": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
    "pencil_source": "04BA61538D85FA16C8A6E525022A1FAC991691E16B09A80304118E153D9EF94D",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def exact_transpose_product(
    matrix: sp.csr_matrix, vector: list[int]
) -> list[int]:
    output = [0] * matrix.shape[1]
    for row, coefficient in enumerate(vector):
        if coefficient == 0:
            continue
        for cursor in range(matrix.indptr[row], matrix.indptr[row + 1]):
            output[int(matrix.indices[cursor])] += (
                int(matrix.data[cursor]) * coefficient
            )
    return output


def reconstruct_state():
    paths = {
        "core": CORE_PATH,
        "pencil": PENCIL_PATH,
        "pencil_source": PENCIL_SOURCE_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned source mismatch: {hashes}")
    core = load_module("codex_r10_exact_dual_sealed_core", CORE_PATH)
    verifier = load_module(
        "codex_r10_exact_dual_sealed_verifier", core.VERIFIER_PATH
    )
    row_source = load_module(
        "codex_r10_exact_dual_sealed_rows", core.ROW_SOURCE_PATH
    )
    context = verifier.build_context()
    archive = np.load(core.NPZ_PATH, allow_pickle=False)
    sealed = np.load(PENCIL_PATH, allow_pickle=False)
    if sealed["format_version"].tolist() != [1]:
        raise AssertionError("sealed pencil format mismatch")
    if sealed["role"].tolist() != [
        "exact 10D block0-only affine-dual pencil; PSD combination not yet certified"
    ]:
        raise AssertionError("sealed pencil role mismatch")
    if sealed["dual_sha256"].tolist() != [core.EXPECTED_SHA256["npz"]]:
        raise AssertionError("sealed pencil dual pin mismatch")
    if sealed["constraint_shape"].tolist() != [2463, 388]:
        raise AssertionError("sealed pencil constraint shape mismatch")
    if sealed["ranks"].tolist() != [378, 378]:
        raise AssertionError("sealed pencil rank metadata mismatch")

    face_map = (context.affine_q @ context.exact_basis).tocsr()
    constraints = sp.vstack(
        [
            context.affine_nu.T,
            sp.csr_matrix(context.affine_rhs.reshape(1, -1)),
            face_map[:, 582:].T,
        ],
        format="csr",
        dtype=np.int64,
    )
    independent_ranks = [
        len(core.independent_row_indices_mod(constraints, prime))
        for prime in core.RANK_PRIMES
    ]
    if independent_ranks != [378, 378, 378]:
        raise AssertionError(
            f"independent support ranks drifted: {independent_ranks}"
        )
    lambda_rows = [
        [int(value) for value in row]
        for row in sealed["lambda_basis_decimal"]
    ]
    q_pencil = [
        [int(value) for value in row]
        for row in sealed["block0_q_pencil_decimal"]
    ]
    if len(lambda_rows) != 10 or any(len(row) != 388 for row in lambda_rows):
        raise AssertionError("sealed lambda basis shape mismatch")
    if len(q_pencil) != 10 or any(len(row) != 1946 for row in q_pencil):
        raise AssertionError("sealed q-pencil shape mismatch")
    for index, lambda_row in enumerate(lambda_rows):
        if not core.exact_sparse_matvec_zero(constraints, lambda_row):
            raise AssertionError(
                f"sealed lambda basis row {index} fails exact constraints"
            )
        expected_q = exact_transpose_product(
            context.affine_q[:, :1946].tocsr(), lambda_row
        )
        if expected_q != q_pencil[index]:
            raise AssertionError(
                f"sealed q-pencil row {index} fails exact replay"
            )
    lambda_sparse = sp.csr_matrix(
        np.asarray(lambda_rows, dtype=np.int64)
    )
    lambda_basis_ranks = [
        len(core.independent_row_indices_mod(lambda_sparse, prime))
        for prime in core.RANK_PRIMES
    ]
    if lambda_basis_ranks != [10, 10, 10]:
        raise AssertionError("sealed lambda basis loses exact rank")

    block = context.blocks[0]
    orbit = context.base.gram_orbits[0]
    ambient_z, ambient_denominator, _pivots, free = (
        row_source.integer_kernel_parameter(
            [list(map(int, row)) for row in block.kernel_rows],
            len(orbit.basis),
        )
    )
    if ambient_denominator != 24 or len(free) != 154:
        raise AssertionError("block-0 ambient quotient drift")
    entry_ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(
        entry_ids.reshape(-1), minlength=1946
    ).astype(np.int64)
    multiplicity_lcm = 1
    for value in multiplicities:
        multiplicity_lcm = np.lcm(
            multiplicity_lcm, int(value)
        ).item()
    pencil_denominator = (
        int(multiplicity_lcm)
        * ambient_denominator
        * ambient_denominator
    )
    numerator_matrices = []
    for pencil_row in q_pencil:
        ambient_numerator = [
            [
                pencil_row[int(entry_ids[row, column])]
                * (
                    int(multiplicity_lcm)
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
        quotient = (
            ambient_z.transpose()
            .matmul(ambient_domain)
            .matmul(ambient_z)
        )
        numerator_matrices.append(
            np.asarray(
                [
                    [int(value) for value in row]
                    for row in quotient.to_list()
                ],
                dtype=object,
            )
        )

    selected_support_rows, support_rows = core.common_support_rows(
        numerator_matrices, core.RANK_PRIMES[0]
    )
    stacked = np.vstack(numerator_matrices)
    maximum = max(abs(int(value)) for value in stacked.flat)
    if maximum >= (1 << 62):
        raise OverflowError("exact quotient pencil exceeds int64")
    stacked_sparse = sp.csr_matrix(stacked.astype(np.int64))
    support_ranks = [
        len(core.independent_row_indices_mod(stacked_sparse, prime))
        for prime in core.RANK_PRIMES
    ]
    if support_ranks != [73, 73, 73]:
        raise AssertionError(f"common support ranks drifted: {support_ranks}")
    support_coordinates = core.independent_columns_mod(
        support_rows, core.RANK_PRIMES[0]
    )
    if len(support_coordinates) != 73:
        raise AssertionError("common support coordinate count mismatch")

    raw_lambda = archive["dual_affine_equalities"].astype(np.float64)
    lambda_matrix = np.asarray(lambda_rows, dtype=np.float64)
    norms = np.linalg.norm(lambda_matrix, axis=1)
    normalized = lambda_matrix / norms[:, None]
    normalized_coordinates, *_ = np.linalg.lstsq(
        normalized.T, raw_lambda, rcond=None
    )
    projection = normalized.T @ normalized_coordinates
    projection_inf = float(np.max(np.abs(projection - raw_lambda)))
    if abs(
        projection_inf
        - float(sealed["dual_projection_residual_inf"][0])
    ) > 1e-13:
        raise AssertionError("independent projection replay differs")
    raw_coefficients = normalized_coordinates / norms
    anchor = int(np.argmax(np.abs(raw_coefficients)))
    ratios = raw_coefficients / abs(raw_coefficients[anchor])

    attempts = []
    reconstruction = None
    for maximum_denominator in (
        10,
        100,
        1_000,
        10_000,
        100_000,
        1_000_000,
        10_000_000,
        100_000_000,
    ):
        coefficients = [
            Fraction(float(value)).limit_denominator(maximum_denominator)
            for value in ratios
        ]
        reduced = core.matrix_linear_combination(
            numerator_matrices,
            coefficients,
            pencil_denominator,
            support_coordinates,
        )
        minimum_float = float(
            np.linalg.eigvalsh(
                np.asarray(
                    [[float(value) for value in row] for row in reduced]
                )
            )[0]
        )
        record: dict[str, Any] = {
            "maximum_denominator": maximum_denominator,
            "minimum_reduced_eigenvalue_float": minimum_float,
        }
        if minimum_float <= 1e-10:
            record["exact_test"] = "skipped_nonpositive_steering"
            attempts.append(record)
            continue
        try:
            rank, pivots = verifier.exact_psd(
                reduced,
                f"sealed reduced dual denominator {maximum_denominator}",
            )
        except ValueError as error:
            record["exact_test"] = f"FAIL: {error}"
            attempts.append(record)
            continue
        record["exact_test"] = "PASS"
        record["exact_rank"] = rank
        record["minimum_exact_pivot"] = str(min(pivots))
        attempts.append(record)
        if rank == 73:
            reconstruction = (
                maximum_denominator, coefficients, reduced, pivots
            )
            break
    if reconstruction is None:
        raise RuntimeError("no exact PSD member found in the sealed pencil")
    return {
        "hashes": {
            "npz": core.EXPECTED_SHA256["npz"],
            **hashes,
        },
        "verifier": verifier,
        "context": context,
        "lambda_constraints": constraints,
        "lambda_ranks": independent_ranks,
        "lambda_rows": lambda_rows,
        "numerator_matrices": numerator_matrices,
        "pencil_denominator": pencil_denominator,
        "multiplicity_lcm": int(multiplicity_lcm),
        "ambient_denominator": ambient_denominator,
        "support_ranks": support_ranks,
        "selected_support_rows": selected_support_rows,
        "support_coordinates": support_coordinates,
        "projection_relative_residual": float(
            np.linalg.norm(projection - raw_lambda)
            / np.linalg.norm(raw_lambda)
        ),
        "projection_inf_residual": projection_inf,
        "ratios": ratios,
        "attempt_records": attempts,
        "reconstruction": reconstruction,
        "lambda_basis_ranks": lambda_basis_ranks,
        "q_pencil_exact_replay": True,
        "core": core,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", action="store_true")
    parser.add_argument("--candidate-output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument("--data-output", type=Path)
    args = parser.parse_args()
    outputs = [
        args.candidate_output, args.metadata_output, args.data_output
    ]
    if args.reconstruct and any(path is None for path in outputs):
        parser.error("--reconstruct requires all three explicit outputs")
    if not args.reconstruct and any(path is not None for path in outputs):
        parser.error("output paths require --reconstruct")
    if args.reconstruct:
        for path in outputs:
            resolved = path.resolve()
            if resolved.exists():
                parser.error(f"refusing to overwrite {resolved}")
            if not resolved.parent.is_dir():
                parser.error(f"missing output directory {resolved.parent}")
    return args


def main() -> int:
    args = parse_args()
    if not args.reconstruct:
        print(
            "EXACT_DUAL_FROM_SEALED_PENCIL_BUILD_ONLY_PASS "
            "solver_called=false input_processed=false"
        )
        return 0
    state = reconstruct_state()
    core = state["core"]
    candidate, metadata = core.build_candidate(state)
    metadata["sealed_pencil_gate"] = {
        "pencil_sha256": EXPECTED_SHA256["pencil"],
        "source_sha256": EXPECTED_SHA256["pencil_source"],
        "lambda_basis_ranks_mod_primes": state["lambda_basis_ranks"],
        "q_pencil_exact_replay": state["q_pencil_exact_replay"],
        "projection_inf_residual": state["projection_inf_residual"],
    }
    candidate_path = args.candidate_output.resolve()
    metadata_path = args.metadata_output.resolve()
    data_path = args.data_output.resolve()
    candidate_path.write_text(
        json.dumps(candidate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    metadata["candidate_sha256"] = sha256(candidate_path)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lambda_basis = np.asarray(state["lambda_rows"], dtype=np.int64)
    coefficients = state["reconstruction"][1]
    np.savez_compressed(
        data_path,
        format_version=np.asarray([1], dtype=np.int32),
        role=np.asarray(
            ["exact zero-bound dual from independently gated sealed pencil"]
        ),
        sealed_pencil_sha256=np.asarray([EXPECTED_SHA256["pencil"]]),
        candidate_sha256=np.asarray([metadata["candidate_sha256"]]),
        lambda_basis=lambda_basis,
        support_ranks_mod_primes=np.asarray(
            state["support_ranks"], dtype=np.int32
        ),
        support_coordinates=np.asarray(
            state["support_coordinates"], dtype=np.int32
        ),
        coefficient_numerators=np.asarray(
            [value.numerator for value in coefficients], dtype=np.int64
        ),
        coefficient_denominators=np.asarray(
            [value.denominator for value in coefficients], dtype=np.int64
        ),
        pencil_common_denominator=np.asarray(
            [state["pencil_denominator"]], dtype=np.int64
        ),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    print(f"CANDIDATE={candidate_path}")
    print(f"SHA256_CANDIDATE={sha256(candidate_path)}")
    print(f"METADATA={metadata_path}")
    print(f"SHA256_METADATA={sha256(metadata_path)}")
    print(f"DATA={data_path}")
    print(f"SHA256_DATA={sha256(data_path)}")
    print(
        "EXACT_ZERO_BOUND_WITH_NECESSARY_FACE_RECONSTRUCTED "
        "separator=false exposing_face=false verifier_required=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
