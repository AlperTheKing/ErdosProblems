"""Exact semantic-dual verifier for the fixed Gamma_11 plateau-face SDP.

Default execution is build-only: it pins and rebuilds the fixed
``c=25``, degree-4, 56-cut, D22-invariant cone and prints the exact
candidate schema.  It never invokes a conic solver and never reconstructs
from a numerical NPZ.

An explicit ``--verify CANDIDATE.json`` checks a separately reconstructed
rational semantic dual.  Fractions must be JSON integers or strings of the
form ``p/q``; binary floats are rejected.  Three exact outcomes are
distinguished:

* ``zero_bound``: dual feasible with lambda^T b = 0;
* ``exposing_face``: the same dual plus an exact feasible t=0 primal witness
  and exact complementarity;
* ``separating``: dual feasible with lambda^T b < 0, proving infeasibility.

The verifier works with the semantic constraints, not SCS's scaled svec
coordinates.  It uses the sealed exact basis Z of ker(H), so q-stationarity
is checked as Z^T(A_q^T lambda - C^*) = 0 exactly.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
ROW_REDUCTION_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
EXACT_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)
DUAL_EXPORT_PATH = (
    HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_SCS_DUAL.py"
)

EXPECTED_SHA256 = {
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "equality": "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F",
    "row_reduction": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "exact_kernel": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "dual_export": "B0C4A2EB4D50C21A6DEB1F0D83D1327546793D6B1D9B10DE9E92DABC7E6C168A",
}
EXPECTED_QUOTIENT_ORDERS = [
    154, 32, 35, 40, 5, 32, 6, 8, 33, 6, 6, 7, 6,
    1, 4, 7, 8, 6, 5, 1, 4, 1, 1, 4, 6, 5, 4, 0,
    4, 6, 0, 1, 1, 0, 0, 0, 1, 0, 11, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 0, 0, 1, 0,
]
EXPECTED_SCALAR_BLOCKS = [
    13, 19, 21, 22, 31, 32, 36, 39,
    40, 41, 43, 44, 45, 46, 47, 50,
]
EXPECTED_PSD_BLOCKS = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
    14, 15, 16, 17, 18, 20, 23, 24, 25, 26, 28, 29, 38,
]
PIVOT_PRIME = 1_000_003
FRACTION_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?")


@dataclass
class BlockSpec:
    index: int
    order: int
    offset: int
    qdim: int
    entry_ids: np.ndarray
    kernel_rows: list[tuple[int, ...]]


@dataclass
class ExactContext:
    hashes: dict[str, str]
    base: Any
    blowup: Any
    equality: Any
    row_reduction: Any
    exact_kernel: Any
    affine_nu: sp.csr_matrix
    affine_q: sp.csr_matrix
    affine_rhs: np.ndarray
    gram_face: sp.csr_matrix
    exact_basis: sp.csr_matrix
    live: np.ndarray
    forced: np.ndarray
    blocks: list[BlockSpec]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
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
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=np.int64,
    )


def independent_pivot_columns(
    rows: list[tuple[int, ...]], width: int
) -> list[int]:
    echelon: dict[int, dict[int, int]] = {}
    for source in rows:
        if len(source) != width:
            raise AssertionError("kernel row width mismatch")
        row = {
            column: int(value) % PIVOT_PRIME
            for column, value in enumerate(source)
            if int(value) % PIVOT_PRIME
        }
        while row:
            pivot = min(row)
            base = echelon.get(pivot)
            if base is None:
                inverse = pow(row[pivot], PIVOT_PRIME - 2, PIVOT_PRIME)
                echelon[pivot] = {
                    column: value * inverse % PIVOT_PRIME
                    for column, value in row.items()
                    if value * inverse % PIVOT_PRIME
                }
                break
            factor = row[pivot]
            for column, value in base.items():
                updated = (
                    row.get(column, 0) - factor * value
                ) % PIVOT_PRIME
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return sorted(echelon)


def build_context() -> ExactContext:
    paths = {
        "base": BASE_PATH,
        "blowup": BLOWUP_PATH,
        "equality": EQUALITY_PATH,
        "row_reduction": ROW_REDUCTION_PATH,
        "exact_kernel": EXACT_KERNEL_PATH,
        "dual_export": DUAL_EXPORT_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input hash mismatch: {hashes}")

    builder = load_module("codex_r10_exact_dual_base", BASE_PATH)
    base = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    row_reduction = np.load(ROW_REDUCTION_PATH, allow_pickle=False)
    exact_kernel = np.load(EXACT_KERNEL_PATH, allow_pickle=False)

    if len(base.cuts) != 56:
        raise AssertionError("the rebuilt model does not have 56 cuts")
    if not np.array_equal(
        blowup["cut_masks"],
        np.asarray([mask for mask, _side in base.cuts], dtype=np.int32),
    ):
        raise AssertionError("cut ordering mismatch")
    if not np.array_equal(
        blowup["multiplier_monomials"],
        np.asarray(base.multiplier_monomials, dtype=np.int8),
    ):
        raise AssertionError("multiplier monomial ordering mismatch")

    live = row_reduction["live_multiplier_orbits"].astype(np.int32)
    forced = row_reduction["forced_multiplier_orbits"].astype(np.int32)
    if live.shape != (526,) or forced.shape != (2085,):
        raise AssertionError("multiplier face dimensions mismatch")
    if not np.array_equal(live, equality["live_multiplier_orbits"]):
        raise AssertionError("live multiplier ordering mismatch")
    if not np.array_equal(forced, equality["forced_multiplier_orbits"]):
        raise AssertionError("forced multiplier ordering mismatch")
    if sorted(map(int, np.concatenate((live, forced)))) != list(range(2611)):
        raise AssertionError("forced/live multiplier partition mismatch")

    affine_nu = unpack_csr(row_reduction, "affine_nu")
    affine_q = unpack_csr(row_reduction, "affine_gram")
    affine_rhs = row_reduction["affine_rhs"].astype(np.int64)
    gram_face = unpack_csr(blowup, "gram_face")
    exact_basis = unpack_csr(exact_kernel, "exact_basis")
    if affine_nu.shape != (388, 526):
        raise AssertionError("A_nu shape mismatch")
    if affine_q.shape != (388, 8647) or affine_rhs.shape != (388,):
        raise AssertionError("A_q/b shape mismatch")
    if gram_face.shape != (6129, 8647):
        raise AssertionError("H shape mismatch")
    if exact_basis.shape != (8647, 2518):
        raise AssertionError("Z shape mismatch")
    if tuple(map(int, row_reduction["rank_h_by_prime"])) != (6129, 6129):
        raise AssertionError("sealed H-rank gate mismatch")
    if tuple(map(int, exact_kernel["rank_by_prime"])) != (2518, 2518):
        raise AssertionError("sealed Z-rank gate mismatch")
    hz = gram_face @ exact_basis
    if hz.nnz:
        raise AssertionError("exact HZ=0 gate failed")

    grouped: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append(tuple(int(value) for value in row))
    offsets = blowup["gram_offsets"].astype(np.int64)
    qdims = blowup["gram_qdims"].astype(np.int64)
    blocks: list[BlockSpec] = []
    quotient_orders: list[int] = []
    for block, orbit in enumerate(base.gram_orbits):
        rows = grouped.get(block, [])
        pivots = independent_pivot_columns(rows, len(orbit.basis))
        if len(pivots) != len(rows):
            raise AssertionError(f"block {block}: dependent kernel rows")
        pivot_set = set(pivots)
        free = [
            index for index in range(len(orbit.basis))
            if index not in pivot_set
        ]
        order = len(free)
        quotient_orders.append(order)
        ids = orbit.entry_ids[np.ix_(free, free)].astype(np.int64)
        blocks.append(
            BlockSpec(
                index=block,
                order=order,
                offset=int(offsets[block]),
                qdim=int(qdims[block]),
                entry_ids=ids,
                kernel_rows=rows,
            )
        )
    if quotient_orders != EXPECTED_QUOTIENT_ORDERS:
        raise AssertionError("quotient block ordering mismatch")
    scalar_blocks = [block.index for block in blocks if block.order == 1]
    psd_blocks = [block.index for block in blocks if block.order > 1]
    if scalar_blocks != EXPECTED_SCALAR_BLOCKS:
        raise AssertionError("scalar block ordering mismatch")
    if psd_blocks != EXPECTED_PSD_BLOCKS:
        raise AssertionError("PSD block ordering mismatch")
    if sum(
        block.order * (block.order + 1) // 2
        for block in blocks if block.order > 1
    ) != 15438:
        raise AssertionError("PSD upper-triangle dimension mismatch")

    return ExactContext(
        hashes=hashes,
        base=base,
        blowup=blowup,
        equality=equality,
        row_reduction=row_reduction,
        exact_kernel=exact_kernel,
        affine_nu=affine_nu,
        affine_q=affine_q,
        affine_rhs=affine_rhs,
        gram_face=gram_face,
        exact_basis=exact_basis,
        live=live,
        forced=forced,
        blocks=blocks,
    )


def parse_fraction(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(f"{name}: floats and booleans are forbidden")
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str) or FRACTION_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name}: expected an integer or canonical p/q string")
    result = Fraction(value)
    if str(result) != value and not (
        result.denominator == 1 and value == f"{result.numerator}/1"
    ):
        raise ValueError(f"{name}: fraction is not in lowest canonical form")
    return result


def fraction_vector(value: Any, name: str, length: int) -> list[Fraction]:
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{name}: expected a list of length {length}")
    return [
        parse_fraction(item, f"{name}[{index}]")
        for index, item in enumerate(value)
    ]


def symmetric_from_upper(
    upper: Any, name: str, order: int
) -> list[list[Fraction]]:
    values = fraction_vector(
        upper, f"{name}.upper_triangle", order * (order + 1) // 2
    )
    matrix = [[Fraction(0) for _ in range(order)] for _ in range(order)]
    cursor = 0
    for row in range(order):
        for column in range(row, order):
            matrix[row][column] = values[cursor]
            matrix[column][row] = values[cursor]
            cursor += 1
    return matrix


def exact_psd(
    source: list[list[Fraction]], name: str
) -> tuple[int, list[Fraction]]:
    order = len(source)
    if any(len(row) != order for row in source):
        raise ValueError(f"{name}: matrix is not square")
    matrix = [row[:] for row in source]
    pivots: list[Fraction] = []
    start = 0
    while start < order:
        for index in range(start, order):
            if matrix[index][index] < 0:
                raise ValueError(
                    f"{name}: negative exact diagonal at {index}"
                )
        pivot_index = next(
            (
                index for index in range(start, order)
                if matrix[index][index] > 0
            ),
            None,
        )
        if pivot_index is None:
            if any(
                matrix[row][column] != 0
                for row in range(start, order)
                for column in range(start, order)
            ):
                raise ValueError(
                    f"{name}: zero diagonal with a nonzero residual entry"
                )
            break
        if pivot_index != start:
            matrix[start], matrix[pivot_index] = (
                matrix[pivot_index], matrix[start]
            )
            for row in range(order):
                matrix[row][start], matrix[row][pivot_index] = (
                    matrix[row][pivot_index], matrix[row][start]
                )
        pivot = matrix[start][start]
        pivots.append(pivot)
        for row in range(start + 1, order):
            for column in range(row, order):
                updated = (
                    matrix[row][column]
                    - matrix[row][start] * matrix[start][column] / pivot
                )
                matrix[row][column] = updated
                matrix[column][row] = updated
        start += 1
    return len(pivots), pivots


def csr_matvec_fraction(
    matrix: sp.csr_matrix, vector: list[Fraction]
) -> list[Fraction]:
    if matrix.shape[1] != len(vector):
        raise ValueError("exact matrix-vector dimension mismatch")
    output: list[Fraction] = []
    for row in range(matrix.shape[0]):
        total = Fraction(0)
        for cursor in range(matrix.indptr[row], matrix.indptr[row + 1]):
            total += int(matrix.data[cursor]) * vector[
                int(matrix.indices[cursor])
            ]
        output.append(total)
    return output


def csr_transpose_matvec_fraction(
    matrix: sp.csr_matrix, vector: list[Fraction]
) -> list[Fraction]:
    if matrix.shape[0] != len(vector):
        raise ValueError("exact transpose matrix-vector dimension mismatch")
    output = [Fraction(0) for _ in range(matrix.shape[1])]
    for row, coefficient in enumerate(vector):
        if coefficient == 0:
            continue
        for cursor in range(matrix.indptr[row], matrix.indptr[row + 1]):
            output[int(matrix.indices[cursor])] += (
                int(matrix.data[cursor]) * coefficient
            )
    return output


def add_vectors(
    left: list[Fraction], right: list[Fraction]
) -> list[Fraction]:
    if len(left) != len(right):
        raise ValueError("exact vector dimension mismatch")
    return [a + b for a, b in zip(left, right)]


def matrix_inner(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> Fraction:
    if len(left) != len(right):
        raise ValueError("matrix inner-product order mismatch")
    return sum(
        (
            left[row][column] * right[row][column]
            for row in range(len(left))
            for column in range(len(left))
        ),
        Fraction(0),
    )


def parse_dual_blocks(
    context: ExactContext, dual: dict[str, Any]
) -> tuple[
    dict[int, Fraction],
    dict[int, list[list[Fraction]]],
]:
    scalar_payload = dual.get("scalar_quotient_duals")
    if not isinstance(scalar_payload, list):
        raise ValueError("dual.scalar_quotient_duals must be a list")
    scalar: dict[int, Fraction] = {}
    for position, item in enumerate(scalar_payload):
        if not isinstance(item, dict):
            raise ValueError(f"scalar dual {position} is not an object")
        block = int(item.get("block", -1))
        if block in scalar:
            raise ValueError(f"duplicate scalar block {block}")
        scalar[block] = parse_fraction(
            item.get("value"), f"scalar dual block {block}"
        )
    if list(scalar) != EXPECTED_SCALAR_BLOCKS:
        raise ValueError("scalar dual block ordering mismatch")

    psd_payload = dual.get("psd_duals")
    if not isinstance(psd_payload, list):
        raise ValueError("dual.psd_duals must be a list")
    psd: dict[int, list[list[Fraction]]] = {}
    expected_orders = {block.index: block.order for block in context.blocks}
    for position, item in enumerate(psd_payload):
        if not isinstance(item, dict):
            raise ValueError(f"PSD dual {position} is not an object")
        block = int(item.get("block", -1))
        if block in psd:
            raise ValueError(f"duplicate PSD block {block}")
        order = int(item.get("order", -1))
        if order != expected_orders.get(block):
            raise ValueError(f"PSD dual block {block}: wrong order {order}")
        psd[block] = symmetric_from_upper(
            item.get("upper_triangle"), f"PSD dual block {block}", order
        )
    if list(psd) != EXPECTED_PSD_BLOCKS:
        raise ValueError("PSD dual block ordering mismatch")
    return scalar, psd


def verify_primal(
    context: ExactContext,
    payload: Any,
) -> tuple[
    list[Fraction],
    list[Fraction],
    dict[int, Fraction],
    dict[int, list[list[Fraction]]],
    dict[str, Any],
]:
    if not isinstance(payload, dict):
        raise ValueError("exposing_face requires primal_witness")
    nu = fraction_vector(payload.get("nu_live"), "primal.nu_live", 526)
    q = fraction_vector(payload.get("q_full"), "primal.q_full", 8647)
    if any(value < 0 for value in nu):
        raise ValueError("primal witness has a negative live multiplier")

    retained = add_vectors(
        csr_matvec_fraction(context.affine_nu, nu),
        csr_matvec_fraction(context.affine_q, q),
    )
    retained_rhs = [Fraction(int(value)) for value in context.affine_rhs]
    if retained != retained_rhs:
        raise ValueError("primal retained 388-row affine gate failed")
    if any(csr_matvec_fraction(context.gram_face, q)):
        raise ValueError("primal exact Hq=0 gate failed")

    equality = context.equality
    normalization = unpack_csr(equality, "normalization_live")
    target_nu = unpack_csr(equality, "target_nu_live")
    target_q = unpack_csr(equality, "target_gram")
    if csr_matvec_fraction(normalization, nu) != [
        Fraction(int(value)) for value in equality["normalization_rhs"]
    ]:
        raise ValueError("primal original 56 normalization rows failed")
    if add_vectors(
        csr_matvec_fraction(target_nu, nu),
        csr_matvec_fraction(target_q, q),
    ) != [Fraction(int(value)) for value in equality["target_rhs"]]:
        raise ValueError("primal original 392 target rows failed")

    scalar_values: dict[int, Fraction] = {}
    quotient_matrices: dict[int, list[list[Fraction]]] = {}
    quotient_ranks: dict[int, int] = {}
    for block in context.blocks:
        if block.order == 0:
            continue
        matrix = [
            [
                q[block.offset + int(block.entry_ids[row, column])]
                for column in range(block.order)
            ]
            for row in range(block.order)
        ]
        if block.order == 1:
            value = matrix[0][0]
            if value < 0:
                raise ValueError(
                    f"primal scalar block {block.index} is negative"
                )
            scalar_values[block.index] = value
        else:
            rank, _pivots = exact_psd(
                matrix, f"primal quotient block {block.index}"
            )
            quotient_matrices[block.index] = matrix
            quotient_ranks[block.index] = rank

        orbit = context.base.gram_orbits[block.index]
        local = q[block.offset : block.offset + block.qdim]
        ambient = [
            [
                local[int(orbit.entry_ids[row, column])]
                for column in range(len(orbit.basis))
            ]
            for row in range(len(orbit.basis))
        ]
        for kernel_row in block.kernel_rows:
            for row in range(len(ambient)):
                if sum(
                    (
                        ambient[row][column] * kernel_row[column]
                        for column in range(len(kernel_row))
                    ),
                    Fraction(0),
                ) != 0:
                    raise ValueError(
                        f"primal block {block.index}: Q U^T failed"
                    )

    return (
        nu,
        q,
        scalar_values,
        quotient_matrices,
        {
            "live_multipliers": 526,
            "H_rows": 6129,
            "retained_affine_rows": 388,
            "original_affine_rows": 448,
            "quotient_ranks": quotient_ranks,
        },
    )


def verify_candidate(
    context: ExactContext, candidate_path: Path
) -> dict[str, Any]:
    with candidate_path.open("r", encoding="utf-8") as handle:
        candidate = json.load(handle)
    if not isinstance(candidate, dict):
        raise ValueError("candidate root must be a JSON object")
    if candidate.get("format") != "R10-c5-face-exact-semantic-dual-v1":
        raise ValueError("wrong exact dual format")
    if candidate.get("pinned_sha256") != context.hashes:
        raise ValueError("candidate pinned hashes do not match the verifier")
    mode = candidate.get("mode")
    if mode not in {"zero_bound", "exposing_face", "separating"}:
        raise ValueError("mode must be zero_bound, exposing_face, or separating")
    dual = candidate.get("dual")
    if not isinstance(dual, dict):
        raise ValueError("candidate.dual must be an object")

    lam = fraction_vector(
        dual.get("affine_equalities"), "dual.affine_equalities", 388
    )
    alpha = fraction_vector(
        dual.get("live_nu_minus_margin"),
        "dual.live_nu_minus_margin",
        526,
    )
    beta = parse_fraction(
        dual.get("margin_nonnegative"), "dual.margin_nonnegative"
    )
    scalar, psd = parse_dual_blocks(context, dual)
    if any(value < 0 for value in alpha):
        raise ValueError("a live-nu dual is negative")
    if beta < 0:
        raise ValueError("the margin-nonnegative dual is negative")
    if any(value < 0 for value in scalar.values()):
        raise ValueError("a scalar quotient dual is negative")

    dual_psd_ranks: dict[int, int] = {}
    dual_psd_pivots: dict[int, list[str]] = {}
    for block, matrix in psd.items():
        rank, pivots = exact_psd(matrix, f"dual PSD block {block}")
        dual_psd_ranks[block] = rank
        dual_psd_pivots[block] = [str(value) for value in pivots]

    nu_stationarity = csr_transpose_matvec_fraction(
        context.affine_nu, lam
    )
    if nu_stationarity != alpha:
        raise ValueError("exact nu-stationarity failed")

    cone_adjoint = [Fraction(0) for _ in range(8647)]
    for block in context.blocks:
        if block.order == 0:
            continue
        if block.order == 1:
            cone_adjoint[
                block.offset + int(block.entry_ids[0, 0])
            ] += scalar[block.index]
            continue
        matrix = psd[block.index]
        for row in range(block.order):
            for column in range(block.order):
                cone_adjoint[
                    block.offset + int(block.entry_ids[row, column])
                ] += matrix[row][column]
    q_stationarity = csr_transpose_matvec_fraction(
        context.affine_q, lam
    )
    q_residual = [
        left - right
        for left, right in zip(q_stationarity, cone_adjoint)
    ]
    projected = csr_transpose_matvec_fraction(
        context.exact_basis, q_residual
    )
    if any(projected):
        raise ValueError(
            "exact q-stationarity modulo H failed: Z^T residual != 0"
        )

    cone_weight = (
        sum(alpha, Fraction(0))
        + sum(scalar.values(), Fraction(0))
        + sum(
            (
                matrix[index][index]
                for matrix in psd.values()
                for index in range(len(matrix))
            ),
            Fraction(0),
        )
    )
    if cone_weight - beta != 1:
        raise ValueError(
            "exact margin normalization failed: cone_weight - beta != 1"
        )
    gap = sum(
        (
            int(context.affine_rhs[index]) * lam[index]
            for index in range(388)
        ),
        Fraction(0),
    )
    if mode in {"zero_bound", "exposing_face"} and gap != 0:
        raise ValueError(f"{mode} requires exact lambda^T b = 0")
    if mode == "separating" and gap >= 0:
        raise ValueError("separating requires exact lambda^T b < 0")

    result: dict[str, Any] = {
        "status": "PASS",
        "mode": mode,
        "exact_dual_objective": str(gap),
        "stationarity": {
            "nu_rows": 526,
            "q_kernel_rows": 2518,
            "margin_rows": 1,
        },
        "cones": {
            "live_nonnegative": 526,
            "margin_nonnegative": 1,
            "scalar_nonnegative": 16,
            "PSD_blocks": 26,
            "PSD_ranks": dual_psd_ranks,
            "normalizing_cone_weight": str(cone_weight),
            "margin_dual": str(beta),
        },
        "logical_result": (
            "no t>=0 primal point exists"
            if mode == "separating"
            else "every feasible primal point has t=0"
        ),
    }
    if mode != "exposing_face":
        return result

    (
        primal_nu,
        _primal_q,
        primal_scalar,
        primal_psd,
        primal_stats,
    ) = verify_primal(context, candidate.get("primal_witness"))
    multiplier_products = [
        alpha[index] * primal_nu[index] for index in range(526)
    ]
    if any(multiplier_products):
        raise ValueError("exact multiplier complementarity failed")
    scalar_products = {
        block: scalar[block] * primal_scalar[block]
        for block in EXPECTED_SCALAR_BLOCKS
    }
    if any(scalar_products.values()):
        raise ValueError("exact scalar-block complementarity failed")
    psd_products = {
        block: matrix_inner(psd[block], primal_psd[block])
        for block in EXPECTED_PSD_BLOCKS
    }
    if any(psd_products.values()):
        raise ValueError("exact PSD complementarity failed")
    result["primal_witness"] = primal_stats
    result["exposed_face"] = {
        "forced_live_multiplier_positions": [
            index for index, value in enumerate(alpha) if value > 0
        ],
        "forced_zero_scalar_blocks": [
            block for block, value in scalar.items() if value > 0
        ],
        "dual_PSD_ranks": dual_psd_ranks,
        "complementarity": "PASS",
    }
    result["logical_result"] = (
        "exact primal feasibility and exact zero dual gap establish max t=0; "
        "the listed complementary constraints expose a proper subface"
    )
    return result


def schema_summary(context: ExactContext) -> dict[str, Any]:
    return {
        "status": "PASS",
        "scope": (
            "build-only exact semantic-dual verifier; "
            "no numerical NPZ processed"
        ),
        "fixed_cone": {
            "c": 25,
            "multiplier_degree": 4,
            "cuts": 56,
            "symmetry": "D22",
            "affine_rows": 388,
            "live_multiplier_orbits": 526,
            "forced_multiplier_orbits": 2085,
            "gram_face": [6129, 8647],
            "exact_kernel_basis": [8647, 2518],
            "scalar_quotient_blocks": EXPECTED_SCALAR_BLOCKS,
            "PSD_quotient_blocks": EXPECTED_PSD_BLOCKS,
            "PSD_upper_triangle_entries": 15438,
        },
        "candidate_format": {
            "format": "R10-c5-face-exact-semantic-dual-v1",
            "mode": "zero_bound | exposing_face | separating",
            "pinned_sha256": context.hashes,
            "dual": {
                "affine_equalities": "388 exact fractions",
                "live_nu_minus_margin": "526 nonnegative exact fractions",
                "margin_nonnegative": "one nonnegative exact fraction",
                "scalar_quotient_duals": (
                    "16 ordered {block,value} records"
                ),
                "psd_duals": (
                    "26 ordered {block,order,upper_triangle} records"
                ),
            },
            "primal_witness": (
                "required only for exposing_face: "
                "526 exact nu_live and 8647 exact q_full"
            ),
        },
        "exact_equations": [
            "A_nu^T lambda = alpha",
            "Z^T(A_q^T lambda - C^*(gamma,S)) = 0",
            "sum(alpha)+sum(gamma)+sum(trace(S))-beta = 1",
            "lambda^T b = 0 (zero/exposing) or < 0 (separating)",
        ],
        "claim": "No candidate processed; no certificate claim.",
        "solver_called": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        type=Path,
        help="explicit exact JSON candidate to verify",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = build_context()
    if args.verify is None:
        print(json.dumps(schema_summary(context), indent=2, sort_keys=True))
        print(
            "EXACT_DUAL_VERIFIER_BUILD_ONLY_PASS "
            "solver_called=false input_processed=false"
        )
        return 0
    candidate_path = args.verify.resolve()
    if not candidate_path.is_file():
        raise FileNotFoundError(candidate_path)
    result = verify_candidate(context, candidate_path)
    result["candidate_path"] = str(candidate_path)
    result["candidate_sha256"] = sha256(candidate_path)
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"EXACT_DUAL_{result['mode'].upper()}_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
