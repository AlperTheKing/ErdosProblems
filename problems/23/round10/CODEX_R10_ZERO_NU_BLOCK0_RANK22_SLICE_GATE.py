"""Independent exact gate for the four-dimensional block-0 rank-22 slice.

This program consumes the sealed ten-dimensional affine-dual pencil, rebuilds
the block-0 quotient matrices from the exact model, and verifies the proposed
four integer coefficient vectors at fresh primes.  It calls no optimizer.
"""

from __future__ import annotations

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
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
ROW_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
SPACE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "space": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
}
SLICE = np.asarray(
    [
        [0, 6, 0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, 0, 12, -4, -2, -3, 0, 4, -8],
        [6, 0, 0, 0, -4, -1, -3, 0, 2, -4],
        [0, 0, 6, 0, -5, -1, -3, 0, 2, -4],
    ],
    dtype=np.int64,
)
PRIMES = (1_000_037, 1_000_039)


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


def rank_mod_prime(matrix: np.ndarray, prime: int) -> int:
    rows = [
        {
            column: int(value) % prime
            for column, value in enumerate(row)
            if int(value) % prime
        }
        for row in matrix
    ]
    rank = 0
    column = 0
    while rank < len(rows) and column < matrix.shape[1]:
        pivot = next(
            (index for index in range(rank, len(rows)) if column in rows[index]),
            None,
        )
        if pivot is None:
            column += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], prime - 2, prime)
        rows[rank] = {
            key: value * inverse % prime
            for key, value in rows[rank].items()
            if value * inverse % prime
        }
        for index in range(len(rows)):
            if index == rank:
                continue
            factor = rows[index].get(column, 0)
            if not factor:
                continue
            for key, value in rows[rank].items():
                updated = (rows[index].get(key, 0) - factor * value) % prime
                if updated:
                    rows[index][key] = updated
                else:
                    rows[index].pop(key, None)
        rank += 1
        column += 1
    return rank


def main() -> None:
    observed = {
        "base": sha256(BASE_PATH),
        "blowup": sha256(BLOWUP_PATH),
        "space": sha256(SPACE_PATH),
    }
    if observed != EXPECTED_SHA256:
        raise AssertionError(f"pinned input mismatch: {observed}")
    builder = load_module("zero_nu_rank22_gate_base", BASE_PATH)
    row_source = load_module("zero_nu_rank22_gate_rows", ROW_SOURCE_PATH)
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    space = np.load(SPACE_PATH, allow_pickle=False)
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
        dtype=np.int64,
    )
    if quotient.shape != (286, 154) or denominator != 24 or len(free) != 154:
        raise AssertionError("unexpected exact block-0 quotient")
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    common = math.lcm(*(int(value) for value in multiplicities))
    generators = np.asarray(
        [
            quotient.T
            @ (
                coefficients[ids]
                * (common // multiplicities[ids])
            )
            @ quotient
            for coefficients in q_pencil
        ],
        dtype=np.int64,
    )
    combinations = np.tensordot(SLICE, generators, axes=(1, 0))
    if np.max(np.abs(combinations - combinations.transpose(0, 2, 1))):
        raise AssertionError("slice matrix lost symmetry")
    stacked = combinations.reshape(4 * 154, 154)
    ranks = [rank_mod_prime(stacked, prime) for prime in PRIMES]
    if ranks != [22, 22]:
        raise AssertionError(f"unexpected fresh-prime ranks {ranks}")
    domain = DomainMatrix.from_list_sympy(
        stacked.shape[0], stacked.shape[1], stacked.tolist()
    ).convert_to(ZZ)
    exact_kernel = domain.nullspace()
    if exact_kernel.shape != (132, 154):
        raise AssertionError(f"unexpected exact kernel {exact_kernel.shape}")
    if domain.matmul(exact_kernel.transpose()).to_dok():
        raise AssertionError("exact common-kernel replay failed")
    print(
        json.dumps(
            {
                "status": "PASS",
                "slice_dimension": 4,
                "stacked_shape": list(stacked.shape),
                "rank_primes": list(PRIMES),
                "ranks": ranks,
                "common_kernel_dimension": 132,
                "quotient_denominator": denominator,
                "orbit_multiplicity_lcm": common,
                "scope": "exact rank/common-kernel gate only; no PSD claim",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
