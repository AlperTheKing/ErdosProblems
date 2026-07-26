"""Overflow-safe independent exact gate for the block-0 rank-22 exposure.

All combinations are formed in q-orbit space before quotient pullback, and
all matrix products use Python integers.  No optimizer is called.
"""

from __future__ import annotations

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
BASE = HERE / "CODEX_R10_g11_d22_sdp.py"
BLOWUP = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
ROWS = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
SPACE = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
EXPECTED = {
    BASE: "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    BLOWUP: "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    ROWS: "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    SPACE: "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
}
SLICE = [
    [0, 6, 0, 0, -1, 0, 0, 0, 0, 0],
    [0, 0, 0, 12, -4, -2, -3, 0, 4, -8],
    [6, 0, 0, 0, -4, -1, -3, 0, 2, -4],
    [0, 0, 6, 0, -5, -1, -3, 0, 2, -4],
]
SLICE_WEIGHTS = [-4, -1, -1, 3]
CENTER = [-2, -8, 6, -4, -1, 0, -1, 0, 0, 0]
PRIMES = (1_000_081, 1_000_099)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def echelon(
    matrix: np.ndarray, prime: int
) -> tuple[list[int], list[int]]:
    reduced = np.asarray(
        [[int(value) % prime for value in row] for row in matrix],
        dtype=np.int64,
    )
    sources = np.arange(len(reduced), dtype=np.int32)
    rank = 0
    selected: list[int] = []
    pivots: list[int] = []
    for column in range(reduced.shape[1]):
        candidates = np.flatnonzero(reduced[rank:, column])
        if not len(candidates):
            continue
        pivot = rank + int(candidates[0])
        reduced[[rank, pivot]] = reduced[[pivot, rank]]
        sources[[rank, pivot]] = sources[[pivot, rank]]
        inverse = pow(int(reduced[rank, column]), -1, prime)
        reduced[rank] = reduced[rank] * inverse % prime
        affected = np.flatnonzero(reduced[rank + 1 :, column]) + rank + 1
        for start in range(0, len(affected), 256):
            indices = affected[start : start + 256]
            factors = reduced[indices, column].copy()
            reduced[indices] = (
                reduced[indices]
                - factors[:, None] * reduced[rank][None, :]
            ) % prime
        selected.append(int(sources[rank]))
        pivots.append(column)
        rank += 1
        if rank == reduced.shape[1]:
            break
    return selected, pivots


def primitive(row: list[int]) -> list[int]:
    divisor = math.gcd(*(abs(value) for value in row))
    if divisor:
        row = [value // divisor for value in row]
    if next((value for value in row if value), 0) < 0:
        row = [-value for value in row]
    return row


def positive_ldl(matrix: np.ndarray) -> list[Fraction]:
    order = len(matrix)
    lower = [
        [Fraction(0) for _ in range(order)] for _ in range(order)
    ]
    diagonal: list[Fraction] = []
    for row in range(order):
        pivot = Fraction(int(matrix[row, row]))
        for prior in range(row):
            pivot -= lower[row][prior] ** 2 * diagonal[prior]
        if pivot <= 0:
            raise AssertionError(f"nonpositive LDL pivot {row}: {pivot}")
        diagonal.append(pivot)
        lower[row][row] = Fraction(1)
        for below in range(row + 1, order):
            value = Fraction(int(matrix[below, row]))
            for prior in range(row):
                value -= (
                    lower[below][prior]
                    * lower[row][prior]
                    * diagonal[prior]
                )
            lower[below][row] = value / pivot
    return diagonal


def main() -> None:
    observed = {path: sha256(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise AssertionError(
            {str(path): value for path, value in observed.items()}
        )
    builder = load("rank22_psd_gate_base", BASE)
    row_helpers = load("rank22_psd_gate_rows", ROWS)
    model = builder.build_model()
    blowup = np.load(BLOWUP, allow_pickle=False)
    sealed = np.load(SPACE, allow_pickle=False)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in sealed["block0_q_pencil_decimal"]
        ],
        dtype=object,
    )
    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, denominator, _pivots, free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    quotient = np.asarray(
        [[int(value) for value in row] for row in quotient_dm.to_list()],
        dtype=object,
    )
    if quotient.shape != (286, 154) or denominator != 24 or len(free) != 154:
        raise AssertionError("wrong block-0 quotient")
    ids = orbit.entry_ids.astype(np.int64)
    counts = np.bincount(ids.reshape(-1))
    common = math.lcm(*(int(value) for value in counts))

    def pullback(coefficients: list[int]) -> np.ndarray:
        q = np.asarray(coefficients, dtype=object) @ q_pencil
        ambient = q[ids] * np.asarray(common // counts[ids], dtype=object)
        matrix = quotient.T @ (ambient @ quotient)
        if not np.array_equal(matrix, matrix.T):
            raise AssertionError("nonsymmetric pullback")
        return matrix

    slice_matrices = [pullback(vector) for vector in SLICE]
    stacked = np.vstack(slice_matrices)
    slice_eliminations = [echelon(stacked, prime) for prime in PRIMES]
    slice_ranks = [len(item[0]) for item in slice_eliminations]
    if slice_ranks != [22, 22]:
        raise AssertionError(f"slice ranks {slice_ranks}")
    selected = stacked[slice_eliminations[0][0], :]
    kernel_dm = DomainMatrix.from_list_sympy(
        selected.shape[0], selected.shape[1], selected.tolist()
    ).convert_to(ZZ).nullspace()
    if kernel_dm.shape != (132, 154):
        raise AssertionError(f"kernel shape {kernel_dm.shape}")
    kernel = np.asarray(
        [
            primitive([int(value) for value in row])
            for row in kernel_dm.to_list()
        ],
        dtype=object,
    )
    if any(int(value) for value in (stacked @ kernel.T).flat):
        raise AssertionError("common-kernel residual")

    combined = np.zeros((154, 154), dtype=object)
    for weight, matrix in zip(SLICE_WEIGHTS, slice_matrices):
        combined += weight * matrix
    center = pullback(CENTER)
    if not np.array_equal(combined, 3 * center):
        raise AssertionError("3*center does not equal the slice combination")
    center_eliminations = [echelon(center, prime) for prime in PRIMES]
    center_ranks = [len(item[0]) for item in center_eliminations]
    if center_ranks != [22, 22]:
        raise AssertionError(f"center ranks {center_ranks}")
    if any(int(value) for value in (center @ kernel.T).flat):
        raise AssertionError("center-kernel residual")
    principal_indices = center_eliminations[0][0]
    principal = center[np.ix_(principal_indices, principal_indices)]
    ldl = positive_ldl(principal)

    print(
        json.dumps(
            {
                "status": "PASS",
                "arithmetic": "Python integers before quotient pullback",
                "slice_ranks": slice_ranks,
                "common_kernel_dimension": 132,
                "center_coefficients": CENTER,
                "center_ranks": center_ranks,
                "principal_indices": principal_indices,
                "positive_LDL_pivots": len(ldl),
                "first_LDL_pivot": str(ldl[0]),
                "minimum_LDL_pivot": str(min(ldl)),
                "last_LDL_pivot": str(ldl[-1]),
                "scope": (
                    "exact rank-22 PSD facial exposure; "
                    "no multiplier coefficient exposed"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
