"""Build an exact integer parameterization of the rank-22 exposure kernel.

The old block-0 quotient has order 154.  This program rebuilds the exact
rank-22 exposing matrix from the sealed ten-dimensional pencil and writes
``K/d`` with ``S K = 0`` and ``(K/d)[free,:] = I_132``.  It also composes
this parameterization with the old ambient quotient basis.  No optimizer is
called.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


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
CENTER = [-2, -8, 6, -4, -1, 0, -1, 0, 0, 0]
SLICE = [
    [0, 6, 0, 0, -1, 0, 0, 0, 0, 0],
    [0, 0, 0, 12, -4, -2, -3, 0, 4, -8],
    [6, 0, 0, 0, -4, -1, -3, 0, 2, -4],
    [0, 0, 6, 0, -5, -1, -3, 0, 2, -4],
]
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


def independent_rows_mod_prime(
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
            rows = affected[start : start + 256]
            factors = reduced[rows, column].copy()
            reduced[rows] = (
                reduced[rows]
                - factors[:, None] * reduced[rank][None, :]
            ) % prime
        selected.append(int(sources[rank]))
        pivots.append(column)
        rank += 1
        if rank == reduced.shape[1]:
            break
    return selected, pivots


def matrix_rank_mod_prime(matrix: np.ndarray, prime: int) -> int:
    return len(independent_rows_mod_prime(matrix, prime)[0])


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
    observed = {path: sha256(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise AssertionError(
            {str(path): value for path, value in observed.items()}
        )
    builder = load("kernel132_producer_base", BASE)
    row_helpers = load("kernel132_producer_rows", ROWS)
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
    old_dm, old_denominator, old_pivots, old_free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    old_numerator = np.asarray(
        [[int(value) for value in row] for row in old_dm.to_list()],
        dtype=object,
    )
    if (
        old_numerator.shape != (286, 154)
        or old_denominator != 24
        or len(old_free) != 154
    ):
        raise AssertionError("wrong old block-0 quotient")
    ids = orbit.entry_ids.astype(np.int64)
    counts = np.bincount(ids.reshape(-1))
    multiplicity_lcm = math.lcm(*(int(value) for value in counts))

    def pullback(coefficients: list[int]) -> np.ndarray:
        q = np.asarray(coefficients, dtype=object) @ q_pencil
        ambient = (
            q[ids]
            * np.asarray(multiplicity_lcm // counts[ids], dtype=object)
        )
        matrix = old_numerator.T @ (ambient @ old_numerator)
        if not np.array_equal(matrix, matrix.T):
            raise AssertionError("nonsymmetric quotient pullback")
        return matrix

    center = pullback(CENTER)
    center_modular = [
        independent_rows_mod_prime(center, prime) for prime in PRIMES
    ]
    center_ranks = [len(item[0]) for item in center_modular]
    if center_ranks != [22, 22]:
        raise AssertionError(f"center ranks {center_ranks}")
    selected_rows = center[center_modular[0][0], :]
    kernel_dm, kernel_denominator, kernel_pivots, kernel_free = (
        row_helpers.integer_kernel_parameter(
            [
                [int(value) for value in row]
                for row in selected_rows
            ],
            154,
        )
    )
    kernel_numerator = np.asarray(
        [[int(value) for value in row] for row in kernel_dm.to_list()],
        dtype=object,
    )
    if kernel_numerator.shape != (154, 132) or len(kernel_free) != 132:
        raise AssertionError("wrong exposure-kernel parameterization")
    if any(int(value) for value in (center @ kernel_numerator).flat):
        raise AssertionError("S*K is not exact zero")
    expected_free = np.zeros((132, 132), dtype=object)
    for index in range(132):
        expected_free[index, index] = kernel_denominator
    if not np.array_equal(kernel_numerator[kernel_free, :], expected_free):
        raise AssertionError("K[free,:] is not denominator times identity")
    kernel_ranks = [
        matrix_rank_mod_prime(kernel_numerator.T, prime)
        for prime in PRIMES
    ]
    if kernel_ranks != [132, 132]:
        raise AssertionError(f"kernel ranks {kernel_ranks}")

    slice_matrices = [pullback(vector) for vector in SLICE]
    for matrix in slice_matrices:
        if any(
            int(value)
            for value in (matrix @ kernel_numerator).flat
        ):
            raise AssertionError("slice generator does not annihilate K")
    ambient_numerator = old_numerator @ kernel_numerator
    ambient_denominator = old_denominator * kernel_denominator
    old_kernel = np.asarray(grouped[0], dtype=object)
    if any(
        int(value)
        for value in (old_kernel @ ambient_numerator).flat
    ):
        raise AssertionError("old ambient face does not annihilate composed K")

    payload = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            [
                "exact rank-22 exposure kernel K/d; "
                "new block-0 quotient order 132"
            ]
        ),
        "input_names": np.asarray([path.name for path in observed]),
        "input_sha256": np.asarray(list(observed.values())),
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "center_coefficients": np.asarray(CENTER, dtype=np.int64),
        "center_ranks": np.asarray(center_ranks, dtype=np.int32),
        "center_selected_rows": np.asarray(
            center_modular[0][0], dtype=np.int32
        ),
        "center_pivot_columns": np.asarray(
            center_modular[0][1], dtype=np.int32
        ),
        "kernel_numerator_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in kernel_numerator
            ]
        ),
        "kernel_denominator_decimal": np.asarray(
            [str(int(kernel_denominator))]
        ),
        "kernel_pivots": np.asarray(kernel_pivots, dtype=np.int32),
        "kernel_free": np.asarray(kernel_free, dtype=np.int32),
        "kernel_ranks": np.asarray(kernel_ranks, dtype=np.int32),
        "old_quotient_numerator_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in old_numerator
            ]
        ),
        "old_quotient_denominator_decimal": np.asarray(
            [str(int(old_denominator))]
        ),
        "ambient_numerator_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in ambient_numerator
            ]
        ),
        "ambient_denominator_decimal": np.asarray(
            [str(int(ambient_denominator))]
        ),
        "old_ambient_pivots": np.asarray(old_pivots, dtype=np.int32),
        "old_ambient_free": np.asarray(old_free, dtype=np.int32),
    }
    np.savez_compressed(args.output, **payload)
    print(
        json.dumps(
            {
                "status": "PASS",
                "center_ranks": center_ranks,
                "kernel_shape": list(kernel_numerator.shape),
                "kernel_denominator": kernel_denominator,
                "kernel_ranks": kernel_ranks,
                "kernel_max_bits": max(
                    abs(int(value)).bit_length()
                    for value in kernel_numerator.flat
                ),
                "ambient_shape": list(ambient_numerator.shape),
                "ambient_denominator": ambient_denominator,
                "ambient_max_bits": max(
                    abs(int(value)).bit_length()
                    for value in ambient_numerator.flat
                ),
                "output": str(args.output),
                "output_sha256": sha256(args.output),
                "scope": "exact fixed rank-22 face only",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
