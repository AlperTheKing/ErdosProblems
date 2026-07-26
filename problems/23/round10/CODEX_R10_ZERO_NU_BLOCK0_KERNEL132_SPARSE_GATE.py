"""Independent fresh-prime gate for the sparse block-0 kernel132 artifact."""

from __future__ import annotations

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
PRODUCER = HERE / "CODEX_R10_ZERO_NU_BLOCK0_KERNEL132_SPARSE.py"
DATA = HERE / "CODEX_R10_ZERO_NU_BLOCK0_KERNEL132_SPARSE_data.npz"
EXPECTED = {
    BASE: "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    BLOWUP: "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    ROWS: "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    SPACE: "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
    PRODUCER: "677E36938C4059DDE370E4825DDE3501A23834FDDEA1501366F8608507CB66D0",
    DATA: "840E253D2F161666DD457F54B5A92FFF464081425D5055CBCB6D1E1D5309EFEB",
}
CENTER = [-2, -8, 6, -4, -1, 0, -1, 0, 0, 0]
SLICE = [
    [0, 6, 0, 0, -1, 0, 0, 0, 0, 0],
    [0, 0, 0, 12, -4, -2, -3, 0, 4, -8],
    [6, 0, 0, 0, -4, -1, -3, 0, 2, -4],
    [0, 0, 6, 0, -5, -1, -3, 0, 2, -4],
]
PRIMES = (1_000_117, 1_000_121, 1_000_133)


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


def rank_mod_prime(matrix: np.ndarray, prime: int) -> int:
    pivots: dict[int, dict[int, int]] = {}
    for source in matrix:
        row = {
            column: int(value) % prime
            for column, value in enumerate(source)
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
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return len(pivots)


def main() -> None:
    observed = {path: sha256(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise AssertionError(
            {str(path): value for path, value in observed.items()}
        )
    builder = load("kernel132_gate_base", BASE)
    row_helpers = load("kernel132_gate_rows", ROWS)
    model = builder.build_model()
    blowup = np.load(BLOWUP, allow_pickle=False)
    sealed = np.load(SPACE, allow_pickle=False)
    artifact = np.load(DATA, allow_pickle=False)
    kernel_rows = np.asarray(
        [
            [int(value) for value in row]
            for row in artifact["kernel_rows_decimal"]
        ],
        dtype=object,
    )
    ambient_saved = np.asarray(
        [
            [int(value) for value in row]
            for row in artifact["ambient_columns_decimal"]
        ],
        dtype=object,
    )
    if kernel_rows.shape != (132, 154):
        raise AssertionError("wrong saved kernel shape")
    for row in kernel_rows:
        values = [int(value) for value in row]
        if math.gcd(*(abs(value) for value in values)) != 1:
            raise AssertionError("nonprimitive kernel row")
        if next(value for value in values if value) < 0:
            raise AssertionError("kernel sign normalization changed")
    kernel_ranks = [
        rank_mod_prime(kernel_rows, prime) for prime in PRIMES
    ]
    if kernel_ranks != [132, 132, 132]:
        raise AssertionError(f"kernel ranks {kernel_ranks}")

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
    old_dm, denominator, _pivots, free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    old_numerator = np.asarray(
        [[int(value) for value in row] for row in old_dm.to_list()],
        dtype=object,
    )
    if denominator != 24 or old_numerator.shape != (286, 154):
        raise AssertionError("wrong old quotient")
    ids = orbit.entry_ids.astype(np.int64)
    counts = np.bincount(ids.reshape(-1))
    common = math.lcm(*(int(value) for value in counts))

    def pullback(coefficients: list[int]) -> np.ndarray:
        q = np.asarray(coefficients, dtype=object) @ q_pencil
        ambient = q[ids] * np.asarray(common // counts[ids], dtype=object)
        return old_numerator.T @ (ambient @ old_numerator)

    center = pullback(CENTER)
    slice_matrices = [pullback(vector) for vector in SLICE]
    center_ranks = [
        rank_mod_prime(center, prime) for prime in PRIMES
    ]
    slice_ranks = [
        rank_mod_prime(np.vstack(slice_matrices), prime)
        for prime in PRIMES
    ]
    if center_ranks != [22, 22, 22] or slice_ranks != [22, 22, 22]:
        raise AssertionError((center_ranks, slice_ranks))
    kernel_columns = kernel_rows.T
    if any(int(value) for value in (center @ kernel_columns).flat):
        raise AssertionError("center-kernel exact residual")
    for matrix in slice_matrices:
        if any(
            int(value)
            for value in (matrix @ kernel_columns).flat
        ):
            raise AssertionError("slice-kernel exact residual")
    ambient = old_numerator @ kernel_columns
    if not np.array_equal(ambient, ambient_saved):
        raise AssertionError("saved ambient composition mismatch")
    if any(
        int(value)
        for value in (
            np.asarray(grouped[0], dtype=object) @ ambient
        ).flat
    ):
        raise AssertionError("ambient C5-face residual")
    if len(free) != 154:
        raise AssertionError("old quotient free dimension changed")

    print(
        json.dumps(
            {
                "status": "PASS",
                "fresh_primes": list(PRIMES),
                "center_ranks": center_ranks,
                "slice_stack_ranks": slice_ranks,
                "kernel_ranks": kernel_ranks,
                "kernel_shape": list(kernel_rows.shape),
                "kernel_nnz": sum(
                    int(value) != 0 for value in kernel_rows.flat
                ),
                "kernel_max_abs": max(
                    abs(int(value)) for value in kernel_rows.flat
                ),
                "ambient_shape": list(ambient.shape),
                "ambient_denominator": denominator,
                "exact_residuals": 0,
                "scope": "exact fixed rank-22 face only",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
