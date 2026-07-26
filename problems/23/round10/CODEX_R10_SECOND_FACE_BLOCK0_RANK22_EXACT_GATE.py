"""Independent replay of the exact rank-22 block-0 exposure artifact.

The replay rebuilds the quotient pencil from pinned upstream data, uses three
fresh primes not used by the producer, checks the stored 132-dimensional
kernel over the integers, reruns exact LDL positivity, and replays the affine
dual semantics.  It calls no conic solver.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
PRODUCER_PATH = HERE / "CODEX_R10_SECOND_FACE_BLOCK0_RANK22_EXACT.py"
DATA_PATH = HERE / "CODEX_R10_SECOND_FACE_BLOCK0_RANK22_EXACT_data.npz"
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
ROW_HELPER_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
SPACE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
ROW_DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
EXACT_Z_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"

EXPECTED_SHA256 = {
    "producer": "7DBD97A18E24108A70DDE16CAA61B46B38D8194209C3E85907F67623B2ED3780",
    "data": "49E4158C0CC2CBFF26989C8C87D850316E49E1F0F8E12104EA3D66AF847AB091",
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "row_helper": "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "space": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
    "row_data": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "exact_z": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
}
FRESH_PRIMES = (1_000_099, 1_000_117, 1_000_121)


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


def unpack_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.int64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive[f"{name}_shape"])),
        dtype=np.int64,
    )


def modular_rank(matrix: np.ndarray, prime: int) -> int:
    source = np.asarray(matrix, dtype=object)
    reduced = np.empty(source.shape, dtype=np.int64)
    for row in range(source.shape[0]):
        reduced[row] = [int(value) % prime for value in source[row]]
    rank = 0
    for column in range(reduced.shape[1]):
        positions = np.flatnonzero(reduced[rank:, column])
        if not positions.size:
            continue
        pivot = rank + int(positions[0])
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
        inverse = pow(int(reduced[rank, column]), -1, prime)
        reduced[rank] = reduced[rank] * inverse % prime
        affected = np.flatnonzero(reduced[:, column])
        affected = affected[affected != rank]
        for start in range(0, len(affected), 128):
            rows = affected[start : start + 128]
            factors = reduced[rows, column].copy()
            reduced[rows] = (
                reduced[rows]
                - factors[:, None] * reduced[rank][None, :]
            ) % prime
        rank += 1
        if rank == min(reduced.shape):
            break
    return rank


def exact_ldl(matrix: np.ndarray) -> list[Fraction]:
    order = matrix.shape[0]
    lower = [[Fraction(0) for _ in range(order)] for _ in range(order)]
    diagonal: list[Fraction] = []
    for i in range(order):
        value = Fraction(int(matrix[i, i]))
        for k in range(i):
            value -= lower[i][k] ** 2 * diagonal[k]
        if value <= 0:
            raise AssertionError(f"nonpositive LDL pivot {i}: {value}")
        diagonal.append(value)
        lower[i][i] = Fraction(1)
        for j in range(i + 1, order):
            entry = Fraction(int(matrix[j, i]))
            for k in range(i):
                entry -= lower[j][k] * lower[i][k] * diagonal[k]
            lower[j][i] = entry / value
    return diagonal


def exact_zero(left: np.ndarray, right: np.ndarray) -> bool:
    product = left.astype(object) @ right.astype(object)
    return not any(int(value) for value in product.reshape(-1))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args()
    if args.log is not None:
        args.log = args.log.resolve()
        if not args.log.parent.is_dir():
            parser.error("log directory does not exist")
        if args.log.exists():
            parser.error("refusing to overwrite existing log")
    return args


def main() -> None:
    args = parse_args()
    paths = {
        "producer": PRODUCER_PATH,
        "data": DATA_PATH,
        "base": BASE_PATH,
        "row_helper": ROW_HELPER_PATH,
        "blowup": BLOWUP_PATH,
        "space": SPACE_PATH,
        "row_data": ROW_DATA_PATH,
        "exact_z": EXACT_Z_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned hash mismatch: {hashes}")

    data = np.load(DATA_PATH, allow_pickle=False)
    for name in ("base", "row_helper", "blowup", "space", "row_data", "exact_z"):
        if str(data[f"{name}_sha256"][0]) != hashes[name]:
            raise AssertionError(f"embedded hash mismatch: {name}")
    slice_coefficients = data["slice_coefficients"].astype(np.int64)
    center_coefficients = data["center_coefficients"].astype(np.int64)
    center_relation = data["center_slice_relation"].astype(np.int64)
    if not np.array_equal(
        center_relation @ slice_coefficients, 3 * center_coefficients
    ):
        raise AssertionError("center/slice relation failed")

    builder = load_module("codex_r10_rank22_gate_base", BASE_PATH)
    row_helpers = load_module("codex_r10_rank22_gate_rows", ROW_HELPER_PATH)
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    space = np.load(SPACE_PATH, allow_pickle=False)
    row_data = np.load(ROW_DATA_PATH, allow_pickle=False)
    exact_archive = np.load(EXACT_Z_PATH, allow_pickle=False)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=np.int64,
    )

    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, quotient_denominator, _pivots, free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    quotient = np.asarray(
        [
            [int(value) for value in row]
            for row in quotient_dm.to_list()
        ],
        dtype=np.int64,
    )
    if quotient_denominator != 24 or len(free) != 154:
        raise AssertionError("quotient reconstruction failed")
    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    common = int(np.lcm.reduce(multiplicities))
    pencil = []
    for coefficients in q_pencil:
        ambient = (
            coefficients[ids] * (common // multiplicities[ids])
        ).astype(np.int64)
        pencil.append(quotient.T @ (ambient @ quotient))
    pencil = np.asarray(pencil, dtype=np.int64)
    slice_matrices = np.tensordot(
        slice_coefficients, pencil, axes=(1, 0)
    ).astype(np.int64)
    stacked = np.vstack(slice_matrices)
    slice_ranks = [modular_rank(stacked, prime) for prime in FRESH_PRIMES]
    if slice_ranks != [22, 22, 22]:
        raise AssertionError(f"fresh slice ranks {slice_ranks}")

    common_kernel = np.asarray(
        [
            [int(value) for value in row]
            for row in data["common_kernel_decimal"]
        ],
        dtype=object,
    )
    kernel_ranks = [
        modular_rank(common_kernel, prime) for prime in FRESH_PRIMES
    ]
    if kernel_ranks != [132, 132, 132]:
        raise AssertionError(f"fresh kernel ranks {kernel_ranks}")
    if not exact_zero(stacked, common_kernel.T):
        raise AssertionError("integer slice-kernel product is nonzero")

    center_matrix = np.tensordot(
        center_coefficients, pencil, axes=(0, 0)
    ).astype(np.int64)
    if not np.array_equal(center_matrix, data["center_matrix"]):
        raise AssertionError("stored center matrix differs")
    if not exact_zero(center_matrix, common_kernel.T):
        raise AssertionError("center-kernel product is nonzero")
    pivot_columns = data["pivot_columns"].astype(int).tolist()
    center_reduced = center_matrix[np.ix_(pivot_columns, pivot_columns)]
    if not np.array_equal(center_reduced, data["center_reduced"]):
        raise AssertionError("stored center restriction differs")
    ldl = exact_ldl(center_reduced)
    stored_ldl = [
        Fraction(int(numerator), int(denominator))
        for numerator, denominator in zip(
            data["ldl_diagonal_numerators"],
            data["ldl_diagonal_denominators"],
        )
    ]
    if ldl != stored_ldl or len(ldl) != 22:
        raise AssertionError("exact LDL replay differs")

    center_lambda = center_coefficients @ lambda_basis
    center_q = center_coefficients @ q_pencil
    if not np.array_equal(center_lambda, data["center_lambda"]):
        raise AssertionError("stored center lambda differs")
    if not np.array_equal(center_q, data["center_block0_q"]):
        raise AssertionError("stored center q differs")
    affine_nu = unpack_csr(row_data, "affine_nu")
    affine_q = unpack_csr(row_data, "affine_gram")
    rhs = row_data["affine_rhs"].astype(np.int64)
    live = np.asarray(affine_nu.T @ center_lambda).reshape(-1)
    rhs_pairing = int(rhs @ center_lambda)
    global_q = np.asarray(affine_q.T @ center_lambda).reshape(-1)
    if np.any(live) or rhs_pairing:
        raise AssertionError("affine dual replay failed")
    if not np.array_equal(global_q[:1946], center_q):
        raise AssertionError("block0 q replay failed")
    exact_z = unpack_csr(exact_archive, "exact_basis")
    face_functional = np.asarray(exact_z.T @ global_q).reshape(-1)
    if np.any(face_functional[582:]):
        raise AssertionError("outside-block0 face functional is nonzero")

    result = {
        "status": "PASS",
        "fresh_primes": list(FRESH_PRIMES),
        "slice_ranks": slice_ranks,
        "common_kernel_ranks": kernel_ranks,
        "exact_LDL_positive_pivots": len(ldl),
        "center_coefficients": center_coefficients.tolist(),
        "live_stationarity_max": int(np.max(np.abs(live), initial=0)),
        "rhs_pairing": rhs_pairing,
        "outside_block0_face_max": int(
            np.max(np.abs(face_functional[582:]), initial=0)
        ),
        "exposure_rank": 22,
        "new_quotient_face_order": 132,
        "scope": "necessary face; nonemptiness not certified",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.log is not None:
        args.log.write_text(encoded + "\n", encoding="utf-8", newline="\n")
    print(encoded)


if __name__ == "__main__":
    main()
