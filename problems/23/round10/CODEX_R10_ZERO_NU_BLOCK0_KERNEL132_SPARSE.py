"""Produce a sparse integer basis for the exact block-0 exposure kernel.

The basis is obtained from an exact nullspace of 22 independently selected
rows of the rank-22 exposing matrix, then primitive-normalized row by row.
Its transpose directly parameterizes the new order-132 PSD quotient.  No
optimizer is called.
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


def primitive(row: list[int]) -> list[int]:
    divisor = math.gcd(*(abs(value) for value in row))
    if not divisor:
        raise AssertionError("zero nullspace row")
    row = [value // divisor for value in row]
    if next(value for value in row if value) < 0:
        row = [-value for value in row]
    return row


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
        raise AssertionError("pinned input mismatch")
    builder = load("kernel132_sparse_base", BASE)
    row_helpers = load("kernel132_sparse_rows", ROWS)
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
    old_dm, old_denominator, _old_pivots, _old_free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    old_numerator = np.asarray(
        [[int(value) for value in row] for row in old_dm.to_list()],
        dtype=object,
    )
    ids = orbit.entry_ids.astype(np.int64)
    counts = np.bincount(ids.reshape(-1))
    common = math.lcm(*(int(value) for value in counts))

    def pullback(coefficients: list[int]) -> np.ndarray:
        q = np.asarray(coefficients, dtype=object) @ q_pencil
        ambient = q[ids] * np.asarray(common // counts[ids], dtype=object)
        output = old_numerator.T @ (ambient @ old_numerator)
        if not np.array_equal(output, output.T):
            raise AssertionError("nonsymmetric pullback")
        return output

    center = pullback(CENTER)
    center_eliminations = [echelon(center, prime) for prime in PRIMES]
    if [len(item[0]) for item in center_eliminations] != [22, 22]:
        raise AssertionError("center rank mismatch")
    selected = center[center_eliminations[0][0], :]
    kernel_dm = DomainMatrix.from_list_sympy(
        selected.shape[0], selected.shape[1], selected.tolist()
    ).convert_to(ZZ).nullspace()
    if kernel_dm.shape != (132, 154):
        raise AssertionError(f"wrong exact kernel shape {kernel_dm.shape}")
    kernel_rows = np.asarray(
        [
            primitive([int(value) for value in row])
            for row in kernel_dm.to_list()
        ],
        dtype=object,
    )
    kernel_columns = kernel_rows.T
    kernel_ranks = [
        len(echelon(kernel_rows, prime)[0]) for prime in PRIMES
    ]
    if kernel_ranks != [132, 132]:
        raise AssertionError(f"kernel ranks {kernel_ranks}")
    if any(int(value) for value in (center @ kernel_columns).flat):
        raise AssertionError("center-kernel residual")
    slice_matrices = [pullback(vector) for vector in SLICE]
    for matrix in slice_matrices:
        if any(
            int(value)
            for value in (matrix @ kernel_columns).flat
        ):
            raise AssertionError("slice-kernel residual")
    stacked_ranks = [
        len(echelon(np.vstack(slice_matrices), prime)[0])
        for prime in PRIMES
    ]
    if stacked_ranks != [22, 22]:
        raise AssertionError(f"slice stack ranks {stacked_ranks}")
    ambient_columns = old_numerator @ kernel_columns
    if any(
        int(value)
        for value in (
            np.asarray(grouped[0], dtype=object) @ ambient_columns
        ).flat
    ):
        raise AssertionError("old ambient-face residual")

    payload = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            ["sparse integer basis for exact block-0 kernel132"]
        ),
        "input_names": np.asarray([path.name for path in observed]),
        "input_sha256": np.asarray(list(observed.values())),
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "center_coefficients": np.asarray(CENTER, dtype=np.int64),
        "center_selected_rows": np.asarray(
            center_eliminations[0][0], dtype=np.int32
        ),
        "center_pivot_columns": np.asarray(
            center_eliminations[0][1], dtype=np.int32
        ),
        "kernel_rows_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in kernel_rows
            ]
        ),
        "kernel_ranks": np.asarray(kernel_ranks, dtype=np.int32),
        "old_quotient_denominator": np.asarray(
            [old_denominator], dtype=np.int64
        ),
        "ambient_columns_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in ambient_columns
            ]
        ),
    }
    np.savez_compressed(args.output, **payload)
    print(
        json.dumps(
            {
                "status": "PASS",
                "kernel_shape": list(kernel_rows.shape),
                "kernel_ranks": kernel_ranks,
                "kernel_nnz": sum(
                    int(value) != 0 for value in kernel_rows.flat
                ),
                "kernel_max_abs": max(
                    abs(int(value)) for value in kernel_rows.flat
                ),
                "ambient_shape": list(ambient_columns.shape),
                "ambient_denominator": old_denominator,
                "ambient_max_abs": max(
                    abs(int(value)) for value in ambient_columns.flat
                ),
                "slice_stack_ranks": stacked_ranks,
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
