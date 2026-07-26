"""Exact modular rank gate for the c_7=0 slice of the sealed dual pencil.

No solver is called.  Matrix products are reduced between multiplications;
the chosen primes and dimensions keep every unreduced int64 dot product below
2^63.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
ROW_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
PENCIL_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "row": "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "pencil": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
}
PRIMES = (1_000_003, 1_000_033)
OMITTED_GENERATOR = 7


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


def rank_mod(matrix: np.ndarray, prime: int) -> int:
    reduced = np.asarray(matrix, dtype=np.int64).copy() % prime
    rank = 0
    for column in range(reduced.shape[1]):
        candidates = np.flatnonzero(reduced[rank:, column])
        if candidates.size == 0:
            continue
        pivot = rank + int(candidates[0])
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
        inverse = pow(int(reduced[rank, column]), prime - 2, prime)
        reduced[rank] = (reduced[rank] * inverse) % prime
        affected = np.flatnonzero(
            reduced[rank + 1 :, column]
        ) + rank + 1
        for start in range(0, len(affected), 128):
            rows = affected[start : start + 128]
            factors = reduced[rows, column].copy()
            reduced[rows] = (
                reduced[rows]
                - factors[:, None] * reduced[rank][None, :]
            ) % prime
        rank += 1
        if rank == reduced.shape[1]:
            break
    return rank


def main() -> int:
    paths = {
        "base": BASE_PATH,
        "row": ROW_PATH,
        "blowup": BLOWUP_PATH,
        "pencil": PENCIL_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input mismatch: {hashes}")
    builder = load_module("codex_r10_c7_gate_base", BASE_PATH)
    row_source = load_module("codex_r10_c7_gate_rows", ROW_PATH)
    base = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    sealed = np.load(PENCIL_PATH, allow_pickle=False)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in sealed["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    if q_pencil.shape != (10, 1946):
        raise AssertionError("q-pencil shape mismatch")
    grouped = []
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        if int(block) == 0:
            grouped.append([int(value) for value in row])
    orbit = base.gram_orbits[0]
    z_domain, denominator, _pivots, free = (
        row_source.integer_kernel_parameter(
            grouped, len(orbit.basis)
        )
    )
    z = np.asarray(
        [
            [int(value) for value in row]
            for row in z_domain.to_list()
        ],
        dtype=np.int64,
    )
    if z.shape != (286, 154) or denominator != 24 or len(free) != 154:
        raise AssertionError("block-0 quotient parameter mismatch")
    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    common = int(np.lcm.reduce(multiplicities))
    if sorted(set(map(int, multiplicities))) != [11, 22, 44]:
        raise AssertionError("entry multiplicity mismatch")

    results = {}
    for prime in PRIMES:
        z_mod = z % prime
        matrices = []
        for q_row in q_pencil:
            ambient = (
                q_row[ids]
                * (common // multiplicities[ids])
            ) % prime
            intermediate = (ambient @ z_mod) % prime
            quotient = (z_mod.T @ intermediate) % prime
            matrices.append(quotient)
        full_stack = np.vstack(matrices)
        slice_stack = np.vstack(
            [
                matrix for index, matrix in enumerate(matrices)
                if index != OMITTED_GENERATOR
            ]
        )
        results[str(prime)] = {
            "full_rank": rank_mod(full_stack, prime),
            "c7_zero_slice_rank": rank_mod(slice_stack, prime),
        }
    output = {
        "status": "PASS",
        "scope": "exact modular pencil-rank gate; no PSD claim",
        "omitted_generator": OMITTED_GENERATOR,
        "ranks": results,
        "full_common_kernel_dimension": (
            154 - results[str(PRIMES[0])]["full_rank"]
        ),
        "c7_zero_common_kernel_dimension": (
            154 - results[str(PRIMES[0])]["c7_zero_slice_rank"]
        ),
        "solver_called": False,
        "hashes": hashes,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    print("EXACT_DUAL_C7_SLICE_GATE_PASS solver_called=false")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
