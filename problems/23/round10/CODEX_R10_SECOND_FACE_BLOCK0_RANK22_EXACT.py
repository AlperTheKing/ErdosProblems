"""Seal an exact rank-22 exposing ray inside the block-0 dual pencil.

Starting from the sealed ten-dimensional exact affine-dual pencil, this
script:

1. reconstructs the exact quotient bilinear-form pencil;
2. fixes four small integer coefficient vectors spanning the numerically
   identified low-rank slice;
3. proves that their stacked row space has exact rank 22;
4. constructs and replays a 132-dimensional exact common kernel;
5. selects a small rational center in the slice and proves it is positive
   definite on a 22-dimensional complement by exact LDL; and
6. replays zero live-multiplier duals, zero RHS pairing, and zero functionals
   on every sealed face coordinate outside block 0.

No conic solver is called.  The conclusion is a necessary second face for any
feasible point on the sealed first face.  This script does not prove that the
new face is nonempty.
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
import scipy.sparse as sp
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
ROW_HELPER_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
SPACE_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_EXPOSURE_SPACE_data.npz"
ROW_DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
EXACT_Z_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"

EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "row_helper": "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "space": "1D58496FFB434DBA7BA655C4519098AFA4E77BD7F4976D84BE87D8F2E5677723",
    "row_data": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "exact_z": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
}

RANK_PRIMES = (1_000_037, 1_000_039, 1_000_081)
SLICE_COEFFICIENTS = np.asarray(
    [
        [0, 6, 0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, 0, 12, -4, -2, -3, 0, 4, -8],
        [6, 0, 0, 0, -4, -1, -3, 0, 2, -4],
        [0, 0, 6, 0, -5, -1, -3, 0, 2, -4],
    ],
    dtype=np.int64,
)
CENTER_COEFFICIENTS = np.asarray(
    [-2, -8, 6, -4, -1, 0, -1, 0, 0, 0],
    dtype=np.int64,
)
CENTER_SLICE_RELATION = np.asarray([-4, -1, -1, 3], dtype=np.int64)


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


def select_rows_mod_prime(
    matrix: np.ndarray, prime: int
) -> tuple[list[int], list[int]]:
    source = np.asarray(matrix, dtype=object)
    reduced = np.empty(source.shape, dtype=np.int64)
    for row in range(source.shape[0]):
        reduced[row] = [int(value) % prime for value in source[row]]
    source_rows = np.arange(reduced.shape[0], dtype=np.int32)
    rank = 0
    pivot_columns: list[int] = []
    selected_rows: list[int] = []
    for column in range(reduced.shape[1]):
        candidates = np.flatnonzero(reduced[rank:, column])
        if not candidates.size:
            continue
        pivot = rank + int(candidates[0])
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
            source_rows[[rank, pivot]] = source_rows[[pivot, rank]]
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


def exact_ldl(matrix: np.ndarray) -> list[Fraction]:
    order = matrix.shape[0]
    lower = [
        [Fraction(0) for _column in range(order)]
        for _row in range(order)
    ]
    diagonal: list[Fraction] = []
    for row in range(order):
        pivot = Fraction(int(matrix[row, row]))
        for prior in range(row):
            pivot -= (
                lower[row][prior]
                * lower[row][prior]
                * diagonal[prior]
            )
        if pivot <= 0:
            raise AssertionError(
                f"nonpositive exact LDL pivot {row}: {pivot}"
            )
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


def exact_zero_product(left: np.ndarray, right: np.ndarray) -> bool:
    product = left.astype(object) @ right.astype(object)
    return not any(int(value) for value in product.reshape(-1))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    args.data = args.data.resolve()
    args.report = args.report.resolve()
    for path in (args.data, args.report):
        if not path.parent.is_dir():
            parser.error(f"missing output directory: {path.parent}")
        if path.exists():
            parser.error(f"refusing to overwrite: {path}")
    if args.data.suffix.lower() != ".npz":
        parser.error("--data must end in .npz")
    if args.report.suffix.lower() != ".md":
        parser.error("--report must end in .md")
    return args


def main() -> None:
    args = parse_args()
    sources = {
        "base": BASE_PATH,
        "row_helper": ROW_HELPER_PATH,
        "blowup": BLOWUP_PATH,
        "space": SPACE_PATH,
        "row_data": ROW_DATA_PATH,
        "exact_z": EXACT_Z_PATH,
    }
    hashes = {name: sha256(path) for name, path in sources.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned source mismatch: {hashes}")

    builder = load_module("codex_r10_rank22_base", BASE_PATH)
    row_helpers = load_module("codex_r10_rank22_rows", ROW_HELPER_PATH)
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    space = np.load(SPACE_PATH, allow_pickle=False)
    row_data = np.load(ROW_DATA_PATH, allow_pickle=False)
    exact_archive = np.load(EXACT_Z_PATH, allow_pickle=False)

    lambda_basis = np.asarray(
        [
            [int(value) for value in row]
            for row in space["lambda_basis_decimal"]
        ],
        dtype=np.int64,
    )
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )
    if lambda_basis.shape != (10, 388) or q_pencil.shape != (10, 1946):
        raise AssertionError("sealed pencil shape mismatch")

    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, quotient_denominator, _old_pivots, old_free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    quotient_numerator = np.asarray(
        [
            [int(value) for value in row]
            for row in quotient_dm.to_list()
        ],
        dtype=np.int64,
    )
    if (
        quotient_numerator.shape != (286, 154)
        or quotient_denominator != 24
        or len(old_free) != 154
    ):
        raise AssertionError("old quotient parameterization mismatch")

    entry_ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(entry_ids.reshape(-1))
    if sorted(set(map(int, multiplicities))) != [11, 22, 44]:
        raise AssertionError("entry multiplicities changed")
    multiplicity_lcm = math.lcm(*map(int, multiplicities))
    pencil = []
    for q_coefficients in q_pencil:
        ambient_scaled = (
            q_coefficients[entry_ids]
            * (multiplicity_lcm // multiplicities[entry_ids])
        ).astype(np.int64)
        quotient_scaled = quotient_numerator.T @ (
            ambient_scaled @ quotient_numerator
        )
        if not np.array_equal(quotient_scaled, quotient_scaled.T):
            raise AssertionError("nonsymmetric quotient generator")
        pencil.append(quotient_scaled)
    pencil = np.asarray(pencil, dtype=np.int64)

    if not np.array_equal(
        CENTER_SLICE_RELATION @ SLICE_COEFFICIENTS,
        3 * CENTER_COEFFICIENTS,
    ):
        raise AssertionError("center does not lie in the integer slice")
    slice_matrices = np.tensordot(
        SLICE_COEFFICIENTS, pencil, axes=(1, 0)
    ).astype(np.int64)
    stacked = np.vstack(slice_matrices)
    modular = [
        select_rows_mod_prime(stacked, prime) for prime in RANK_PRIMES
    ]
    ranks = [len(item[0]) for item in modular]
    if ranks != [22, 22, 22]:
        raise AssertionError(f"rank-22 slice failed: {ranks}")
    if not all(item[1] == modular[0][1] for item in modular[1:]):
        raise AssertionError("slice pivot columns differ across primes")

    selected_rows = modular[0][0]
    pivot_columns = modular[0][1]
    selected = stacked[selected_rows]
    common_kernel_dm = DomainMatrix.from_list_sympy(
        selected.shape[0], selected.shape[1], selected.tolist()
    ).convert_to(ZZ).nullspace()
    common_kernel = np.asarray(
        [
            primitive([int(value) for value in row])
            for row in common_kernel_dm.to_list()
        ],
        dtype=object,
    )
    if common_kernel.shape != (132, 154):
        raise AssertionError(f"common kernel shape {common_kernel.shape}")
    if not exact_zero_product(stacked, common_kernel.T):
        raise AssertionError("slice does not kill exact common kernel")
    kernel_ranks = [
        len(select_rows_mod_prime(common_kernel, prime)[0])
        for prime in RANK_PRIMES
    ]
    if kernel_ranks != [132, 132, 132]:
        raise AssertionError(f"common-kernel ranks {kernel_ranks}")

    center_matrix = np.tensordot(
        CENTER_COEFFICIENTS, pencil, axes=(0, 0)
    ).astype(np.int64)
    if not exact_zero_product(center_matrix, common_kernel.T):
        raise AssertionError("center does not kill common kernel")
    center_reduced = center_matrix[np.ix_(pivot_columns, pivot_columns)]
    ldl = exact_ldl(center_reduced)

    center_lambda = CENTER_COEFFICIENTS @ lambda_basis
    center_q = CENTER_COEFFICIENTS @ q_pencil
    affine_nu = unpack_csr(row_data, "affine_nu")
    affine_q = unpack_csr(row_data, "affine_gram")
    rhs = row_data["affine_rhs"].astype(np.int64)
    live_stationarity = np.asarray(
        affine_nu.T @ center_lambda
    ).reshape(-1)
    rhs_pairing = int(rhs @ center_lambda)
    if np.any(live_stationarity) or rhs_pairing:
        raise AssertionError("live/RHS dual conditions failed")
    global_q = np.asarray(affine_q.T @ center_lambda).reshape(-1)
    if not np.array_equal(global_q[:1946], center_q):
        raise AssertionError("stored block0 functional mismatch")
    exact_z = unpack_csr(exact_archive, "exact_basis")
    face_functional = np.asarray(exact_z.T @ global_q).reshape(-1)
    if np.any(face_functional[582:]):
        raise AssertionError("functional leaks outside block0 face")

    maximum_kernel_bits = max(
        abs(int(value)).bit_length()
        for value in common_kernel.reshape(-1)
    )
    ldl_numerators = [str(value.numerator) for value in ldl]
    ldl_denominators = [str(value.denominator) for value in ldl]
    payload = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            [
                "exact rank-22 block0 exposing ray; necessary face only, "
                "nonemptiness not certified"
            ]
        ),
        **{
            f"{name}_sha256": np.asarray([value])
            for name, value in hashes.items()
        },
        "rank_primes": np.asarray(RANK_PRIMES, dtype=np.int64),
        "slice_ranks": np.asarray(ranks, dtype=np.int32),
        "common_kernel_ranks": np.asarray(
            kernel_ranks, dtype=np.int32
        ),
        "slice_coefficients": SLICE_COEFFICIENTS,
        "center_coefficients": CENTER_COEFFICIENTS,
        "center_slice_relation": CENTER_SLICE_RELATION,
        "quotient_denominator": np.asarray(
            [quotient_denominator], dtype=np.int64
        ),
        "multiplicity_lcm": np.asarray(
            [multiplicity_lcm], dtype=np.int64
        ),
        "selected_slice_rows": np.asarray(
            selected_rows, dtype=np.int32
        ),
        "pivot_columns": np.asarray(pivot_columns, dtype=np.int32),
        "common_kernel_decimal": np.asarray(
            [
                [str(int(value)) for value in row]
                for row in common_kernel
            ]
        ),
        "center_matrix": center_matrix,
        "center_reduced": center_reduced,
        "ldl_diagonal_numerators": np.asarray(ldl_numerators),
        "ldl_diagonal_denominators": np.asarray(ldl_denominators),
        "center_lambda": center_lambda.astype(np.int64),
        "center_block0_q": center_q.astype(np.int64),
        "live_dual_alpha": np.zeros(526, dtype=np.int8),
        "rhs_dual_beta": np.asarray([0], dtype=np.int8),
        "old_block0_ambient_order": np.asarray([286], dtype=np.int32),
        "old_block0_kernel_dimension": np.asarray([132], dtype=np.int32),
        "old_block0_quotient_order": np.asarray([154], dtype=np.int32),
        "exposure_rank": np.asarray([22], dtype=np.int32),
        "exposure_kernel_dimension": np.asarray([132], dtype=np.int32),
        "new_block0_ambient_kernel_dimension": np.asarray(
            [154], dtype=np.int32
        ),
        "new_block0_face_order": np.asarray([132], dtype=np.int32),
    }
    np.savez_compressed(args.data, **payload)
    data_hash = sha256(args.data)

    report = "\n".join(
        [
            "# Exact second face in block 0",
            "",
            "## Result",
            "",
            (
                "The sealed ten-dimensional pure-Gram block-0 dual pencil "
                "contains the exact four-dimensional slice generated by"
            ),
            "",
            f"```text\n{SLICE_COEFFICIENTS.tolist()}\n```",
            "",
            (
                "The four exact quotient matrices have stacked rank `22` "
                f"at the three fresh primes `{list(RANK_PRIMES)}`. An exact "
                "132-vector common kernel was reconstructed and every "
                "integer matrix-kernel product is zero."
            ),
            "",
            (
                "The primitive center coefficient vector is "
                f"`{CENTER_COEFFICIENTS.tolist()}`. It satisfies "
                "`3 center = -4 vA - vB - vC + 3 vD`."
            ),
            "",
            (
                "On the 22 pivot coordinates, exact LDL has 22 strictly "
                "positive rational pivots. Hence the center quotient "
                "functional is PSD of exact rank 22."
            ),
            "",
            "## Semantic replay",
            "",
            "- all 526 live multiplier dual coefficients are exactly zero;",
            "- the affine RHS pairing is exactly zero;",
            (
                "- the functional on every exact sealed face coordinate "
                "outside block 0 is exactly zero;"
            ),
            (
                "- the block-0 functional is represented by the exact PSD "
                "matrix stored in the data artifact, scaled by the positive "
                f"factor `{multiplicity_lcm}*{quotient_denominator}^2`."
            ),
            "",
            "Therefore every feasible point on the sealed first face must "
            "lie on this second face. The block-0 quotient order drops from "
            "`154` to `132`; equivalently, the ambient block-0 kernel "
            "dimension grows from `132` to `154`.",
            "",
            "## Scope boundary",
            "",
            (
                "This is an exact necessary-face certificate. It does not "
                "establish that the new face is nonempty, and it is not yet "
                "a full infeasibility certificate for the original SDP."
            ),
            "",
            f"Data SHA-256: `{data_hash}`",
            "",
        ]
    )
    args.report.write_text(report, encoding="utf-8", newline="\n")
    summary = {
        "status": "PASS",
        "slice_dimension": 4,
        "slice_rank": 22,
        "common_kernel_dimension": 132,
        "center_exact_LDL_positive_pivots": len(ldl),
        "center_coefficients": CENTER_COEFFICIENTS.tolist(),
        "live_stationarity_max": int(
            np.max(np.abs(live_stationarity), initial=0)
        ),
        "rhs_pairing": rhs_pairing,
        "outside_block0_face_max": int(
            np.max(np.abs(face_functional[582:]), initial=0)
        ),
        "common_kernel_max_bits": maximum_kernel_bits,
        "data": str(args.data),
        "data_sha256": data_hash,
        "report": str(args.report),
        "scope": "necessary face; nonemptiness not certified",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
