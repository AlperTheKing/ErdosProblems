"""Overflow-safe exact gate for the block-0 rank-22 PSD exposure.

The four proposed coefficient directions are combined in q-orbit space before
the quotient pullback, and every matrix product uses Python integers.  This is
essential: forming the ten large generators separately in NumPy int64 can
overflow before cancellations occur.  No optimizer is called.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
ROW_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
SPACE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "row_source": "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    "space": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
}
SLICE = np.asarray(
    [
        [0, 6, 0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, 0, 12, -4, -2, -3, 0, 4, -8],
        [6, 0, 0, 0, -4, -1, -3, 0, 2, -4],
        [0, 0, 6, 0, -5, -1, -3, 0, 2, -4],
    ],
    dtype=object,
)
SLICE_CENTER_WEIGHTS = np.asarray([-4, -1, -1, 3], dtype=object)
CENTER = np.asarray(
    [-2, -8, 6, -4, -1, 0, -1, 0, 0, 0], dtype=object
)
PRIMES = (1_000_081, 1_000_099)


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


def select_rows_mod_prime(
    matrix: np.ndarray, prime: int
) -> tuple[list[int], list[int]]:
    dense = np.asarray(matrix, dtype=object)
    reduced = np.empty(dense.shape, dtype=np.int64)
    for row in range(dense.shape[0]):
        reduced[row] = [int(value) % prime for value in dense[row]]
    source_rows = np.arange(reduced.shape[0], dtype=np.int32)
    rank = 0
    pivot_columns: list[int] = []
    selected_rows: list[int] = []
    for column in range(reduced.shape[1]):
        candidates = np.flatnonzero(reduced[rank:, column])
        if candidates.size == 0:
            continue
        pivot = rank + int(candidates[0])
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
            source_rows[[rank, pivot]] = source_rows[[pivot, rank]]
        inverse = pow(int(reduced[rank, column]), -1, prime)
        reduced[rank] = (reduced[rank] * inverse) % prime
        affected = np.flatnonzero(reduced[rank + 1 :, column]) + rank + 1
        for start in range(0, len(affected), 256):
            rows = affected[start : start + 256]
            factors = reduced[rows, column].copy()
            reduced[rows] = (
                reduced[rows]
                - factors[:, None] * reduced[rank][None, :]
            ) % prime
        selected_rows.append(int(source_rows[rank]))
        pivot_columns.append(column)
        rank += 1
        if rank == reduced.shape[1]:
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


def exact_ldl(matrix: list[list[int]]) -> list[Fraction]:
    order = len(matrix)
    lower = [
        [Fraction(0) for _column in range(order)]
        for _row in range(order)
    ]
    diagonal: list[Fraction] = []
    for row in range(order):
        pivot = Fraction(matrix[row][row])
        for prior in range(row):
            pivot -= (
                lower[row][prior]
                * lower[row][prior]
                * diagonal[prior]
            )
        if pivot <= 0:
            raise AssertionError(
                f"principal restriction is not PD at pivot {row}: {pivot}"
            )
        diagonal.append(pivot)
        lower[row][row] = Fraction(1)
        for below in range(row + 1, order):
            value = Fraction(matrix[below][row])
            for prior in range(row):
                value -= (
                    lower[below][prior]
                    * lower[row][prior]
                    * diagonal[prior]
                )
            lower[below][row] = value / pivot
    return diagonal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.output.suffix.lower() != ".npz":
        parser.error("--output must end in .npz")
    if not args.output.parent.is_dir():
        parser.error("output parent does not exist")
    if args.output.exists():
        parser.error("refusing to overwrite output")
    return args


def main() -> None:
    args = parse_args()
    observed = {
        "base": sha256(BASE_PATH),
        "blowup": sha256(BLOWUP_PATH),
        "row_source": sha256(ROW_SOURCE_PATH),
        "space": sha256(SPACE_PATH),
    }
    if observed != EXPECTED_SHA256:
        raise AssertionError(f"pinned input mismatch: {observed}")
    builder = load_module("zero_nu_rank22_v2_base", BASE_PATH)
    row_source = load_module("zero_nu_rank22_v2_rows", ROW_SOURCE_PATH)
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    space = np.load(SPACE_PATH, allow_pickle=False)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=object,
    )
    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=object,
    )
    if q_pencil.shape != (10, 1946) or lambda_basis.shape != (10, 388):
        raise AssertionError("sealed pencil dimensions changed")
    if not np.array_equal(SLICE_CENTER_WEIGHTS @ SLICE, 3 * CENTER):
        raise AssertionError("slice-center relation failed")

    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, denominator, _pivots, free = (
        row_source.integer_kernel_parameter(grouped[0], len(orbit.basis))
    )
    quotient = np.asarray(
        [[int(value) for value in row] for row in quotient_dm.to_list()],
        dtype=object,
    )
    if quotient.shape != (286, 154) or denominator != 24 or len(free) != 154:
        raise AssertionError("unexpected exact block-0 quotient")
    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    common = math.lcm(*(int(value) for value in multiplicities))
    if common != 44:
        raise AssertionError("unexpected orbit-multiplicity LCM")

    def pullback(coefficients: np.ndarray) -> np.ndarray:
        ambient = (
            coefficients[ids]
            * np.asarray(common // multiplicities[ids], dtype=object)
        )
        output = quotient.T @ (ambient @ quotient)
        if not np.array_equal(output, output.T):
            raise AssertionError("quotient pullback lost symmetry")
        return output

    slice_q = SLICE @ q_pencil
    slice_matrices = np.asarray(
        [pullback(coefficients) for coefficients in slice_q], dtype=object
    )
    stacked = slice_matrices.reshape(4 * 154, 154)
    modular = [select_rows_mod_prime(stacked, prime) for prime in PRIMES]
    ranks = [len(result[0]) for result in modular]
    if ranks != [22, 22]:
        raise AssertionError(f"unexpected slice ranks {ranks}")
    selected = stacked[modular[0][0], :]
    selected_dm = DomainMatrix.from_list_sympy(
        selected.shape[0], selected.shape[1], selected.tolist()
    ).convert_to(ZZ)
    common_kernel_dm = selected_dm.nullspace()
    if common_kernel_dm.shape != (132, 154):
        raise AssertionError(f"unexpected common kernel {common_kernel_dm.shape}")
    common_kernel = np.asarray(
        [
            primitive([int(value) for value in row])
            for row in common_kernel_dm.to_list()
        ],
        dtype=object,
    )
    kernel_residual = stacked @ common_kernel.T
    if any(int(value) for value in kernel_residual.flat):
        raise AssertionError("full exact common-kernel replay failed")

    center_q = CENTER @ q_pencil
    center_lambda = CENTER @ lambda_basis
    center_matrix = pullback(center_q)
    if not np.array_equal(
        SLICE_CENTER_WEIGHTS @ slice_matrices, 3 * center_matrix
    ):
        raise AssertionError("matrix-level slice-center relation failed")
    center_modular = [
        select_rows_mod_prime(center_matrix, prime) for prime in PRIMES
    ]
    center_ranks = [len(result[0]) for result in center_modular]
    if center_ranks != [22, 22]:
        raise AssertionError(f"unexpected center ranks {center_ranks}")
    if any(int(value) for value in (center_matrix @ common_kernel.T).flat):
        raise AssertionError("center does not annihilate common kernel")

    principal_indices = center_modular[0][0]
    if len(principal_indices) != 22:
        raise AssertionError("wrong principal restriction order")
    principal = center_matrix[
        np.ix_(principal_indices, principal_indices)
    ]
    ldl = exact_ldl(
        [[int(value) for value in row] for row in principal]
    )
    if len(ldl) != 22:
        raise AssertionError("incomplete exact LDL")

    payload = {
        "format_version": np.asarray([2], dtype=np.int32),
        "role": np.asarray(
            ["overflow-safe exact rank-22 block-0 PSD facial exposure"]
        ),
        "input_names": np.asarray(list(observed)),
        "input_sha256": np.asarray(list(observed.values())),
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "slice_coefficients_decimal": np.asarray(
            [[str(int(value)) for value in row] for row in SLICE]
        ),
        "slice_center_weights_decimal": np.asarray(
            [str(int(value)) for value in SLICE_CENTER_WEIGHTS]
        ),
        "center_coefficients_decimal": np.asarray(
            [str(int(value)) for value in CENTER]
        ),
        "center_lambda_decimal": np.asarray(
            [str(int(value)) for value in center_lambda]
        ),
        "center_q_decimal": np.asarray(
            [str(int(value)) for value in center_q]
        ),
        "common_kernel_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in common_kernel
            ]
        ),
        "principal_indices": np.asarray(principal_indices, dtype=np.int32),
        "ldl_pivots": np.asarray(
            [
                f"{value.numerator}/{value.denominator}"
                for value in ldl
            ]
        ),
    }
    np.savez_compressed(args.output, **payload)
    print(
        json.dumps(
            {
                "status": "PASS",
                "arithmetic": "Python integers before every quotient product",
                "slice_dimension": 4,
                "slice_ranks": ranks,
                "common_kernel_dimension": 132,
                "center_coefficients": [int(value) for value in CENTER],
                "center_ranks": center_ranks,
                "principal_indices": principal_indices,
                "positive_LDL_pivots": len(ldl),
                "minimum_LDL_pivot": str(min(ldl)),
                "minimum_LDL_pivot_float": float(min(ldl)),
                "maximum_center_entry_bits": max(
                    abs(int(value)).bit_length()
                    for value in center_matrix.flat
                ),
                "output": str(args.output),
                "output_sha256": sha256(args.output),
                "scope": (
                    "exact PSD facial exposure only; "
                    "no live multiplier coefficient is exposed here"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
