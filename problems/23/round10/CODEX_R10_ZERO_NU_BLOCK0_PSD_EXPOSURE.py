"""Exact PSD member of the ten-dimensional block0-only dual pencil.

The numerical dual is used only to choose rational coefficients in the exact
integer pencil.  Positivity and all affine stationarity equations are then
checked over the rationals.  No conic solver is called.
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
ROW_HELPER_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
SPACE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "space": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
}
PRIMES = (1_000_003, 1_000_033)
RATIONAL_CENTER_DENOMINATOR = 1 << 20
EXPECTED_COMMON_RANK = 22
EXPECTED_COMMON_KERNEL = 132


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
        reduced[row] = [
            int(value) % prime for value in dense[row]
        ]
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
        affected = np.flatnonzero(
            reduced[rank + 1 :, column]
        ) + rank + 1
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
                f"centered pencil is not positive definite at pivot {row}: "
                f"{pivot}"
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
        parser.error("output directory does not exist")
    if args.output.exists():
        parser.error("refusing to overwrite existing output")
    return args


def main() -> None:
    args = parse_args()
    hashes = {
        "base": sha256(BASE_PATH),
        "blowup": sha256(BLOWUP_PATH),
        "space": sha256(SPACE_PATH),
    }
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input mismatch: {hashes}")

    builder = load_module("codex_r10_zero_nu_psd_base", BASE_PATH)
    row_helpers = load_module(
        "codex_r10_zero_nu_psd_row_helpers", ROW_HELPER_PATH
    )
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    space = np.load(SPACE_PATH, allow_pickle=False)
    lambda_basis = [
        [int(value) for value in row]
        for row in space["lambda_basis_decimal"]
    ]
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    if len(lambda_basis) != 10 or q_pencil.shape != (10, 1946):
        raise AssertionError("exact pencil shape mismatch")

    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    ambient_order = len(orbit.basis)
    quotient_numerator_dm, quotient_denominator, _pivots, free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], ambient_order
        )
    )
    quotient_numerator = np.asarray(
        [
            [int(value) for value in row]
            for row in quotient_numerator_dm.to_list()
        ],
        dtype=np.int64,
    )
    if quotient_numerator.shape != (286, 154) or len(free) != 154:
        raise AssertionError("block0 quotient shape mismatch")
    entry_ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(entry_ids.reshape(-1))
    multiplicity_lcm = math.lcm(*map(int, multiplicities))
    if sorted(set(map(int, multiplicities))) != [11, 22, 44]:
        raise AssertionError("unexpected block0 entry multiplicities")

    psd_pencil: list[np.ndarray] = []
    for q_coefficients in q_pencil:
        ambient = (
            q_coefficients[entry_ids]
            * (multiplicity_lcm // multiplicities[entry_ids])
        ).astype(np.int64)
        quotient = (
            quotient_numerator.T
            @ (ambient @ quotient_numerator)
        )
        if not np.array_equal(quotient, quotient.T):
            raise AssertionError("nonsymmetric quotient functional")
        psd_pencil.append(quotient)
    stacked = np.vstack(psd_pencil).astype(np.int64)
    modular = [
        select_rows_mod_prime(stacked, prime) for prime in PRIMES
    ]
    ranks = [len(result[0]) for result in modular]
    if ranks != [EXPECTED_COMMON_RANK, EXPECTED_COMMON_RANK]:
        raise AssertionError(f"unexpected common ranks {ranks}")
    selected = stacked[modular[0][0], :]
    common_kernel_dm = DomainMatrix.from_list_sympy(
        selected.shape[0], selected.shape[1], selected.tolist()
    ).convert_to(ZZ).nullspace()
    common_kernel = [
        primitive([int(value) for value in row])
        for row in common_kernel_dm.to_list()
    ]
    if len(common_kernel) != EXPECTED_COMMON_KERNEL:
        raise AssertionError("common-kernel dimension mismatch")
    for matrix in psd_pencil:
        for vector in common_kernel:
            if any(
                value
                for value in matrix.astype(object)
                @ np.asarray(vector, dtype=object)
            ):
                raise AssertionError("common-kernel replay failed")

    range_numerator_dm, range_denominator, _range_pivots, range_free = (
        row_helpers.integer_kernel_parameter(
            common_kernel, 154
        )
    )
    if len(range_free) != EXPECTED_COMMON_RANK:
        raise AssertionError("common range dimension mismatch")
    range_numerator = np.asarray(
        [
            [int(value) for value in row]
            for row in range_numerator_dm.to_list()
        ],
        dtype=object,
    )
    reduced_pencil = []
    for matrix in psd_pencil:
        reduced_pencil.append(
            range_numerator.T
            @ (matrix.astype(object) @ range_numerator)
        )

    normalized_coordinates = space[
        "dual_coordinates_in_row_normalized_basis"
    ].astype(np.float64)
    lambda_norms = np.asarray(
        [
            np.linalg.norm(np.asarray(row, dtype=np.float64))
            for row in lambda_basis
        ]
    )
    primitive_coordinates = normalized_coordinates / lambda_norms
    center_weights = np.rint(
        RATIONAL_CENTER_DENOMINATOR * primitive_coordinates
    ).astype(np.int64)
    if not np.any(center_weights):
        raise AssertionError("zero rational center")
    centered_reduced = np.zeros((22, 22), dtype=object)
    for weight, matrix in zip(center_weights, reduced_pencil):
        centered_reduced += int(weight) * matrix
    centered_reduced_list = [
        [int(value) for value in row] for row in centered_reduced
    ]
    ldl = exact_ldl(centered_reduced_list)

    centered_lambda = [
        sum(
            int(weight) * int(lambda_basis[index][column])
            for index, weight in enumerate(center_weights)
        )
        for column in range(388)
    ]
    centered_q = [
        sum(
            int(weight) * int(q_pencil[index, column])
            for index, weight in enumerate(center_weights)
        )
        for column in range(1946)
    ]
    centered_psd = np.zeros((154, 154), dtype=object)
    for weight, matrix in zip(center_weights, psd_pencil):
        centered_psd += int(weight) * matrix.astype(object)
    for vector in common_kernel:
        if any(
            value
            for value in centered_psd
            @ np.asarray(vector, dtype=object)
        ):
            raise AssertionError("centered PSD kernel replay failed")

    payload = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            [
                "exact block0 PSD facial exposure; "
                "no multiplier orbit is exposed at this stage"
            ]
        ),
        "base_sha256": np.asarray([hashes["base"]]),
        "blowup_sha256": np.asarray([hashes["blowup"]]),
        "exposure_space_sha256": np.asarray([hashes["space"]]),
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "stacked_pencil_ranks": np.asarray(ranks, dtype=np.int32),
        "stacked_selected_rows": np.asarray(
            modular[0][0], dtype=np.int32
        ),
        "quotient_denominator": np.asarray(
            [quotient_denominator], dtype=np.int64
        ),
        "entry_multiplicity_lcm": np.asarray(
            [multiplicity_lcm], dtype=np.int64
        ),
        "range_denominator": np.asarray(
            [range_denominator], dtype=np.int64
        ),
        "rational_center_denominator": np.asarray(
            [RATIONAL_CENTER_DENOMINATOR], dtype=np.int64
        ),
        "center_weights": center_weights,
        "centered_lambda_decimal": np.asarray(
            [str(value) for value in centered_lambda]
        ),
        "centered_block0_q_decimal": np.asarray(
            [str(value) for value in centered_q]
        ),
        "common_kernel_decimal": np.asarray(
            [[str(value) for value in row] for row in common_kernel]
        ),
        "common_range_numerator_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in range_numerator
            ]
        ),
        "centered_psd_numerator_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in centered_psd
            ]
        ),
        "centered_reduced_numerator_decimal": np.asarray(
            [
                [str(value) for value in row]
                for row in centered_reduced_list
            ]
        ),
        "ldl_pivots": np.asarray(
            [
                f"{value.numerator}/{value.denominator}"
                for value in ldl
            ]
        ),
    }
    np.savez_compressed(args.output, **payload)
    summary = {
        "status": "PASS",
        "ambient_order": ambient_order,
        "old_quotient_order": 154,
        "stacked_pencil_rank": EXPECTED_COMMON_RANK,
        "common_kernel_dimension": len(common_kernel),
        "center_weights": list(map(int, center_weights)),
        "exact_LDL_positive_pivots": len(ldl),
        "minimum_LDL_pivot_float": min(map(float, ldl)),
        "maximum_centered_lambda_bits": max(
            abs(value).bit_length() for value in centered_lambda
        ),
        "maximum_centered_PSD_bits": max(
            abs(int(value)).bit_length() for value in centered_psd.flat
        ),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "scope": (
            "exact first facial exposure; "
            "all live multiplier coefficients are zero"
        ),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
