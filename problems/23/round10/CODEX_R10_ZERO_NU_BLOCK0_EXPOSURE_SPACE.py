"""Build the exact block0-only affine-dual pencil for the sealed C5 face.

The numerical SCS dual indicates an exposure with:

* zero coefficient on all 526 live multipliers;
* zero objective gap;
* zero functionals on Gram blocks 1,...,51; and
* one PSD functional on quotient block 0.

Those support assertions define a homogeneous rational linear system in the
388 retained affine-row multipliers.  This script computes its exact kernel,
checks its rank modulo two primes, and exports the resulting ten-dimensional
integer basis plus its exact block0 q-orbit pencil.  It calls no conic solver.
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
REDUCED_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
DUAL_PATH = HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_dual_numeric.npz"
EXPECTED_SHA256 = {
    "reduced": "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1",
    "dual": "6DFD3A35C8B93144D45479BEE1E00BB72F82797BBF6CC6CA59A7D56E573C1982",
}
PRIMES = (1_000_003, 1_000_033)
EXPECTED_RANK = 378
EXPECTED_NULLITY = 10
BLOCK0_FACE_DIMENSION = 582


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


def unpack_exact_basis(archive) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive["exact_basis_data"].astype(np.int64),
            archive["exact_basis_indices"].astype(np.int32),
            archive["exact_basis_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive["exact_basis_shape"])),
        dtype=np.int64,
    )


def select_rows_mod_prime(
    matrix: sp.csr_matrix, prime: int
) -> tuple[list[int], list[int]]:
    dense = matrix.toarray().astype(np.int64) % prime
    source_rows = np.arange(dense.shape[0], dtype=np.int32)
    rank = 0
    pivot_columns: list[int] = []
    selected_rows: list[int] = []
    for column in range(dense.shape[1]):
        candidates = np.flatnonzero(dense[rank:, column])
        if candidates.size == 0:
            continue
        pivot = rank + int(candidates[0])
        if pivot != rank:
            dense[[rank, pivot]] = dense[[pivot, rank]]
            source_rows[[rank, pivot]] = source_rows[[pivot, rank]]
        inverse = pow(int(dense[rank, column]), -1, prime)
        dense[rank] = (dense[rank] * inverse) % prime
        affected = np.flatnonzero(dense[rank + 1 :, column]) + rank + 1
        if affected.size:
            for start in range(0, len(affected), 256):
                rows = affected[start : start + 256]
                factors = dense[rows, column].copy()
                dense[rows] = (
                    dense[rows]
                    - factors[:, None] * dense[rank][None, :]
                ) % prime
        selected_rows.append(int(source_rows[rank]))
        pivot_columns.append(column)
        rank += 1
        if rank == dense.shape[1]:
            break
    return selected_rows, pivot_columns


def primitive(row: list[int]) -> list[int]:
    divisor = 0
    for value in row:
        divisor = math.gcd(divisor, abs(int(value)))
    if divisor:
        row = [int(value) // divisor for value in row]
    first = next((value for value in row if value), 0)
    if first < 0:
        row = [-value for value in row]
    return row


def exact_sparse_product_zero(
    matrix: sp.csr_matrix, basis: list[list[int]]
) -> tuple[bool, int]:
    maximum = 0
    for row in range(matrix.shape[0]):
        start = int(matrix.indptr[row])
        end = int(matrix.indptr[row + 1])
        indices = matrix.indices[start:end]
        values = matrix.data[start:end]
        for vector in basis:
            value = sum(
                int(coefficient) * int(vector[int(column)])
                for column, coefficient in zip(indices, values)
            )
            maximum = max(maximum, abs(value))
            if value:
                return False, maximum
    return True, maximum


def block0_pencil(
    affine_q: sp.csr_matrix,
    basis: list[list[int]],
    q_dimension: int,
) -> list[list[int]]:
    transpose = affine_q[:, :q_dimension].T.tocsr()
    output: list[list[int]] = []
    for vector in basis:
        row = []
        for qid in range(q_dimension):
            start = int(transpose.indptr[qid])
            end = int(transpose.indptr[qid + 1])
            row.append(
                sum(
                    int(value) * int(vector[int(index)])
                    for index, value in zip(
                        transpose.indices[start:end],
                        transpose.data[start:end],
                    )
                )
            )
        output.append(row)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.output.suffix.lower() != ".npz":
        parser.error("--output must end in .npz")
    if not args.output.parent.is_dir():
        parser.error("output directory does not exist")
    if args.output.exists():
        parser.error("refusing to overwrite existing output")
    return args


def main() -> None:
    args = parse_args()
    hashes = {
        "reduced": sha256(REDUCED_PATH),
        "dual": sha256(DUAL_PATH),
    }
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned source mismatch: {hashes}")
    reduced = load_module("codex_r10_zero_nu_block0_reduced", REDUCED_PATH)
    model = reduced.build_model()
    exact_z = unpack_exact_basis(model.exact_kernel)
    affine_nu = reduced.unpack_csr(
        model.row_reduction, "affine_nu", np.int64
    )
    affine_q = reduced.unpack_csr(
        model.row_reduction, "affine_gram", np.int64
    )
    affine_y = (affine_q @ exact_z).tocsr()
    if affine_y.shape != (388, 2518):
        raise AssertionError("exact affine face shape mismatch")
    constraints = sp.vstack(
        (
            affine_nu.T,
            sp.csr_matrix(
                model.affine_rhs.astype(np.int64).reshape(1, -1)
            ),
            affine_y[:, BLOCK0_FACE_DIMENSION:].T,
        ),
        format="csr",
        dtype=np.int64,
    )
    modular = [
        select_rows_mod_prime(constraints, prime) for prime in PRIMES
    ]
    ranks = [len(item[0]) for item in modular]
    if ranks != [EXPECTED_RANK, EXPECTED_RANK]:
        raise AssertionError(f"unexpected modular ranks {ranks}")
    if modular[0][1] != modular[1][1]:
        raise AssertionError("pivot-column sets differ across primes")

    selected = constraints[modular[0][0], :].toarray().astype(np.int64)
    domain = DomainMatrix.from_list_sympy(
        selected.shape[0],
        selected.shape[1],
        selected.tolist(),
    ).convert_to(ZZ)
    raw_basis = domain.nullspace().to_list()
    basis = [
        primitive([int(value) for value in row]) for row in raw_basis
    ]
    if len(basis) != EXPECTED_NULLITY:
        raise AssertionError(f"unexpected nullity {len(basis)}")
    exact_zero, maximum = exact_sparse_product_zero(constraints, basis)
    if not exact_zero or maximum:
        raise AssertionError(f"exact kernel residual {maximum}")

    q_dimension = int(model.blowup["gram_qdims"][0])
    pencil = block0_pencil(affine_q, basis, q_dimension)
    if any(all(value == 0 for value in row) for row in pencil):
        raise AssertionError("zero block0 pencil generator")

    dual = np.load(DUAL_PATH, allow_pickle=False)
    numerical_lambda = dual["dual_affine_equalities"].astype(np.float64)
    normalized_basis = np.asarray(
        [
            np.asarray(row, dtype=np.float64)
            / np.linalg.norm(np.asarray(row, dtype=np.float64))
            for row in basis
        ]
    )
    coordinates, *_ = np.linalg.lstsq(
        normalized_basis.T, numerical_lambda, rcond=None
    )
    projection = normalized_basis.T @ coordinates
    projection_residual = float(
        np.max(np.abs(projection - numerical_lambda))
    )

    maximum_bits = max(
        abs(value).bit_length() for row in basis for value in row
    )
    pencil_bits = max(
        abs(value).bit_length() for row in pencil for value in row
    )
    payload = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            [
                "exact 10D block0-only affine-dual pencil; "
                "PSD combination not yet certified"
            ]
        ),
        "reduced_sha256": np.asarray([hashes["reduced"]]),
        "dual_sha256": np.asarray([hashes["dual"]]),
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "ranks": np.asarray(ranks, dtype=np.int32),
        "pivot_columns": np.asarray(modular[0][1], dtype=np.int32),
        "selected_constraint_rows": np.asarray(
            modular[0][0], dtype=np.int32
        ),
        "constraint_shape": np.asarray(constraints.shape, dtype=np.int32),
        "block0_face_dimension": np.asarray(
            [BLOCK0_FACE_DIMENSION], dtype=np.int32
        ),
        "block0_q_dimension": np.asarray([q_dimension], dtype=np.int32),
        "lambda_basis_decimal": np.asarray(
            [[str(value) for value in row] for row in basis]
        ),
        "block0_q_pencil_decimal": np.asarray(
            [[str(value) for value in row] for row in pencil]
        ),
        "dual_coordinates_in_row_normalized_basis": coordinates,
        "dual_projection_residual_inf": np.asarray(
            [projection_residual], dtype=np.float64
        ),
    }
    np.savez_compressed(args.output, **payload)
    summary = {
        "status": "PASS",
        "constraint_shape": list(map(int, constraints.shape)),
        "ranks": ranks,
        "nullity": len(basis),
        "lambda_basis_max_bits": maximum_bits,
        "block0_q_dimension": q_dimension,
        "block0_pencil_max_bits": pencil_bits,
        "exact_residual": maximum,
        "dual_projection_residual_inf": projection_residual,
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "scope": "exact linear pencil only; no PSD claim",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
