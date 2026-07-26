"""Exact affine-row reduction on the Gamma_11 plateau face.

The plateau model has 526 live multiplier-orbit variables, 8647 invariant
Gram-entry variables, and the exact Gram-face equations

    H q = 0,             rank(H) = 6129.

The original affine system consists of 56 multiplier normalizations followed
by 392 target-coefficient equations.  This program:

1. computes the rank of those 448 rows modulo row(H) over two primes;
2. extracts the same normalization-first independent row selector both times;
3. reconstructs the 60 dependency vectors over Q by CRT;
4. verifies the dependencies exactly, including their Gram parts, using the
   exact kernel quotient Q = B R B^T block by block; and
5. exports the 388-row affine system on *only* the 526 live multipliers.

The exact upper and lower rank bounds are separate:

* the 60 triangular exact dependencies prove rank <= 388;
* either modular nonzero minor proves rank over Q >= 388.

No solver is imported or run.  In particular, this artifact only removes
redundant equalities and forced-zero multiplier coordinates; it does not alter
c=25, multiplier degree 4, the 56 cuts, H, or the quotient PSD cones.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
DEFAULT_OUTPUT = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
DEFAULT_SUMMARY = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_summary.json"
DEFAULT_REPORT = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_REPORT.md"

EXPECTED_BASE_SHA256 = (
    "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE"
)
EXPECTED_EQUALITY_SHA256 = (
    "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F"
)
EXPECTED_BLOWUP_SHA256 = (
    "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730"
)
PRIMES = (1_000_003, 2_000_003)
LIVE_COUNT = 526
GRAM_COUNT = 8647
NORMALIZATION_COUNT = 56
TARGET_COUNT = 392
AFFINE_COUNT = NORMALIZATION_COUNT + TARGET_COUNT


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_integer_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.int64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=np.int64,
    )


def pack_integer_csr(
    payload: dict[str, np.ndarray], name: str, matrix: sp.spmatrix
) -> dict[str, object]:
    csr = matrix.astype(np.int64).tocsr()
    csr.eliminate_zeros()
    payload[f"{name}_data"] = csr.data.astype(np.int64)
    payload[f"{name}_indices"] = csr.indices.astype(np.int32)
    payload[f"{name}_indptr"] = csr.indptr.astype(np.int64)
    payload[f"{name}_shape"] = np.asarray(csr.shape, dtype=np.int64)
    return {"shape": list(csr.shape), "nnz": int(csr.nnz)}


def row_dict(matrix: sp.csr_matrix, row: int, offset: int = 0) -> dict[int, int]:
    start = int(matrix.indptr[row])
    stop = int(matrix.indptr[row + 1])
    return {
        offset + int(column): int(value)
        for column, value in zip(
            matrix.indices[start:stop], matrix.data[start:stop]
        )
        if int(value)
    }


def subtract_mod(
    target: dict[int, int],
    source: dict[int, int],
    factor: int,
    prime: int,
) -> None:
    if not factor:
        return
    for column, value in source.items():
        updated = (target.get(column, 0) - factor * value) % prime
        if updated:
            target[column] = updated
        else:
            target.pop(column, None)


@dataclass
class PrimeResult:
    prime: int
    rank_h: int
    keep_rows: list[int]
    drop_rows: list[int]
    dependencies: dict[int, dict[int, int]]
    pivot_columns: list[int]
    seconds: float


class TrackedModularSpan:
    """Sparse row span with labels only on the 448 affine source rows."""

    def __init__(self, prime: int) -> None:
        self.prime = prime
        self.rows: dict[int, dict[int, int]] = {}
        self.labels: dict[int, dict[int, int]] = {}

    def add(
        self, source: dict[int, int], label: dict[int, int]
    ) -> tuple[bool, dict[int, int]]:
        prime = self.prime
        row = {
            column: value % prime
            for column, value in source.items()
            if value % prime
        }
        current_label = {
            column: value % prime
            for column, value in label.items()
            if value % prime
        }
        while row:
            pivot = min(row)
            base = self.rows.get(pivot)
            if base is None:
                inverse = pow(row[pivot], prime - 2, prime)
                self.rows[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                self.labels[pivot] = {
                    column: value * inverse % prime
                    for column, value in current_label.items()
                    if value * inverse % prime
                }
                return True, current_label
            factor = row[pivot]
            subtract_mod(row, base, factor, prime)
            subtract_mod(
                current_label, self.labels[pivot], factor, prime
            )
        return False, current_label


def affine_rows(
    normalization: sp.csr_matrix,
    target_nu: sp.csr_matrix,
    target_gram: sp.csr_matrix,
) -> list[dict[int, int]]:
    rows = [
        row_dict(normalization, row)
        for row in range(NORMALIZATION_COUNT)
    ]
    for row in range(TARGET_COUNT):
        combined = row_dict(target_nu, row)
        combined.update(row_dict(target_gram, row, LIVE_COUNT))
        rows.append(combined)
    assert len(rows) == AFFINE_COUNT
    return rows


def modular_selector(
    gram_face: sp.csr_matrix,
    rows: list[dict[int, int]],
    prime: int,
) -> PrimeResult:
    start = time.perf_counter()
    span = TrackedModularSpan(prime)
    for row in range(gram_face.shape[0]):
        independent, _label = span.add(
            row_dict(gram_face, row, LIVE_COUNT), {}
        )
        if not independent:
            raise AssertionError(
                f"H loses row rank modulo {prime} at row {row}"
            )
    rank_h = len(span.rows)
    keep: list[int] = []
    drop: list[int] = []
    dependencies: dict[int, dict[int, int]] = {}
    for row, source in enumerate(rows):
        independent, label = span.add(source, {row: 1})
        if independent:
            keep.append(row)
        else:
            drop.append(row)
            dependencies[row] = label
    return PrimeResult(
        prime=prime,
        rank_h=rank_h,
        keep_rows=keep,
        drop_rows=drop,
        dependencies=dependencies,
        pivot_columns=sorted(span.rows),
        seconds=time.perf_counter() - start,
    )


def crt_pair(first: int, second: int, p: int, q: int) -> int:
    return (
        first + p * (((second - first) * pow(p, -1, q)) % q)
    ) % (p * q)


def rational_reconstruct(residue: int, modulus: int) -> Fraction | None:
    """Wang rational reconstruction with sqrt(modulus/2) bounds."""
    residue %= modulus
    r0, s0 = modulus, 0
    r1, s1 = residue, 1
    bound = math.isqrt(modulus // 2)
    while r1 >= bound:
        quotient = r0 // r1
        r0, r1 = r1, r0 - quotient * r1
        s0, s1 = s1, s0 - quotient * s1
    if s1 == 0 or abs(s1) >= bound:
        return None
    numerator, denominator = (
        (-r1, -s1) if s1 < 0 else (r1, s1)
    )
    value = Fraction(numerator, denominator)
    if math.gcd(value.denominator, modulus) != 1:
        return None
    if (
        value.numerator
        * pow(value.denominator, -1, modulus)
        - residue
    ) % modulus:
        return None
    return value


def reconstruct_dependencies(
    first: PrimeResult, second: PrimeResult
) -> dict[int, dict[int, Fraction]]:
    if first.keep_rows != second.keep_rows:
        raise AssertionError("the two primes select different affine rows")
    if first.drop_rows != second.drop_rows:
        raise AssertionError("the two primes find different dependent rows")
    p, q = first.prime, second.prime
    modulus = p * q
    output: dict[int, dict[int, Fraction]] = {}
    for dropped in first.drop_rows:
        left = first.dependencies[dropped]
        right = second.dependencies[dropped]
        relation: dict[int, Fraction] = {}
        for column in sorted(set(left) | set(right)):
            residue = crt_pair(
                left.get(column, 0), right.get(column, 0), p, q
            )
            value = rational_reconstruct(residue, modulus)
            if value is None:
                raise AssertionError(
                    f"rational reconstruction failed at ({dropped},{column})"
                )
            if value:
                relation[column] = value
        if relation.get(dropped) != 1:
            raise AssertionError(
                f"dependency {dropped} is not normalized at its omitted row"
            )
        if any(
            column in first.drop_rows and column != dropped
            for column in relation
        ):
            raise AssertionError(
                f"dependency {dropped} uses another omitted row"
            )
        output[dropped] = relation
    return output


def dependency_matrix(
    drop_rows: list[int],
    dependencies: dict[int, dict[int, Fraction]],
) -> sp.csr_matrix:
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    for relation_row, dropped in enumerate(drop_rows):
        relation = dependencies[dropped]
        denominator_lcm = math.lcm(
            *(value.denominator for value in relation.values())
        )
        integer_values = {
            column: value.numerator
            * (denominator_lcm // value.denominator)
            for column, value in relation.items()
        }
        common_gcd = math.gcd(
            *(abs(value) for value in integer_values.values())
        )
        integer_values = {
            column: value // common_gcd
            for column, value in integer_values.items()
        }
        if integer_values[dropped] < 0:
            integer_values = {
                column: -value for column, value in integer_values.items()
            }
        for column, value in sorted(integer_values.items()):
            rows.append(relation_row)
            columns.append(column)
            values.append(value)
    return sp.csr_matrix(
        (values, (rows, columns)),
        shape=(len(drop_rows), AFFINE_COUNT),
        dtype=np.int64,
    )


def independent_columns_mod_prime(
    rows: list[list[int]], width: int, prime: int
) -> list[int]:
    echelon: dict[int, dict[int, int]] = {}
    for source in rows:
        if len(source) != width:
            raise AssertionError("kernel row has the wrong width")
        row = {
            column: value % prime
            for column, value in enumerate(source)
            if value % prime
        }
        while row:
            pivot = min(row)
            base = echelon.get(pivot)
            if base is None:
                inverse = pow(row[pivot], prime - 2, prime)
                echelon[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            subtract_mod(row, base, factor, prime)
    return sorted(echelon)


def integer_kernel_parameter(
    kernel_rows: list[list[int]], order: int
) -> tuple[DomainMatrix, int, list[int], list[int]]:
    """Return Z,d with B=Z/d, U B=0, and B[free,:]=I."""
    rank = len(kernel_rows)
    if rank == 0:
        identity = [
            [1 if row == column else 0 for column in range(order)]
            for row in range(order)
        ]
        return (
            DomainMatrix.from_list_sympy(
                order, order, identity
            ).convert_to(ZZ),
            1,
            [],
            list(range(order)),
        )

    pivots = independent_columns_mod_prime(
        kernel_rows, order, PRIMES[1]
    )
    if len(pivots) != rank:
        raise AssertionError("kernel pivot minor loses modular rank")
    pivot_set = set(pivots)
    free = [
        column for column in range(order) if column not in pivot_set
    ]
    up = DomainMatrix.from_list_sympy(
        rank,
        rank,
        [[row[column] for column in pivots] for row in kernel_rows],
    ).convert_to(ZZ)
    uc = DomainMatrix.from_list_sympy(
        rank,
        len(free),
        [[row[column] for column in free] for row in kernel_rows],
    ).convert_to(ZZ)
    inverse_numerator, denominator = up.inv_den(method="rref")
    denominator = int(denominator)
    product = inverse_numerator.matmul(uc).to_list()
    if denominator < 0:
        denominator = -denominator
        product = [[-int(value) for value in row] for row in product]

    numerator = [[0] * len(free) for _ in range(order)]
    for row, coordinate in enumerate(pivots):
        numerator[coordinate] = [
            -int(value) for value in product[row]
        ]
    for column, coordinate in enumerate(free):
        numerator[coordinate][column] = denominator
    z = DomainMatrix.from_list_sympy(
        order, len(free), numerator
    ).convert_to(ZZ)

    u = DomainMatrix.from_list_sympy(
        rank, order, kernel_rows
    ).convert_to(ZZ)
    if u.matmul(z).to_dok():
        raise AssertionError("exact quotient basis does not satisfy U Z=0")
    return z, denominator, pivots, free


def exact_gram_dependency_gate(
    builder,
    base,
    blowup,
    gram_dependencies: sp.csr_matrix,
) -> dict[str, object]:
    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block_index, row = json.loads(str(encoded))
        grouped[int(block_index)].append([int(value) for value in row])

    offsets = blowup["gram_offsets"].astype(np.int64)
    qdims = blowup["gram_qdims"].astype(np.int64)
    checked_pairs = 0
    maximum_kernel_denominator_bits = 0
    quotient_orders: list[int] = []

    for block_index, orbit in enumerate(base.gram_orbits):
        order = len(orbit.basis)
        kernel = grouped.get(block_index, [])
        z, denominator, _pivots, free = integer_kernel_parameter(
            kernel, order
        )
        z_sparse = z.to_sparse()
        maximum_kernel_denominator_bits = max(
            maximum_kernel_denominator_bits,
            abs(denominator).bit_length(),
        )
        quotient_orders.append(len(free))
        q_offset = int(offsets[block_index])
        qdim = int(qdims[block_index])
        local = gram_dependencies[
            :, q_offset : q_offset + qdim
        ].tocsr()
        if not local.nnz or not free:
            continue

        counts = np.bincount(
            orbit.entry_ids.reshape(-1), minlength=qdim
        ).astype(np.int64)
        if np.any(counts <= 0):
            raise AssertionError("empty invariant Gram-entry orbit")
        count_lcm = math.lcm(*(int(value) for value in counts))
        entry_ids = orbit.entry_ids

        for relation_index in range(local.shape[0]):
            start = int(local.indptr[relation_index])
            stop = int(local.indptr[relation_index + 1])
            if start == stop:
                continue
            coefficients = {
                int(column): int(value)
                for column, value in zip(
                    local.indices[start:stop], local.data[start:stop]
                )
                if int(value)
            }
            w_entries: dict[int, dict[int, int]] = {}
            for row in range(order):
                for column in range(order):
                    entry_id = int(entry_ids[row, column])
                    value = coefficients.get(entry_id, 0)
                    if value:
                        w_entries.setdefault(row, {})[column] = (
                            value * count_lcm // int(counts[entry_id])
                        )
            w = DomainMatrix.from_dict_sympy(
                order, order, w_entries
            ).convert_to(ZZ)
            pullback = z_sparse.transpose().matmul(w.matmul(z_sparse))
            if pullback.to_dok():
                raise AssertionError(
                    "a reconstructed dependency does not annihilate the "
                    f"exact quotient in block {block_index}, relation "
                    f"{relation_index}"
                )
            checked_pairs += 1

    return {
        "blocks": len(base.gram_orbits),
        "nonzero_relation_block_pairs_checked": checked_pairs,
        "quotient_dimension_total": sum(
            order * (order + 1) // 2 for order in quotient_orders
        ),
        "maximum_kernel_denominator_bits": (
            maximum_kernel_denominator_bits
        ),
    }


def sparse_is_zero(matrix: sp.spmatrix) -> bool:
    csr = matrix.tocsr()
    csr.eliminate_zeros()
    return csr.nnz == 0


def build_reduction() -> tuple[
    dict[str, np.ndarray], dict[str, object]
]:
    hashes = {
        "base": sha256(BASE_PATH),
        "equality": sha256(EQUALITY_PATH),
        "blowup": sha256(BLOWUP_PATH),
    }
    expected = {
        "base": EXPECTED_BASE_SHA256,
        "equality": EXPECTED_EQUALITY_SHA256,
        "blowup": EXPECTED_BLOWUP_SHA256,
    }
    if hashes != expected:
        raise AssertionError(f"pinned source hash mismatch: {hashes}")

    builder = load_module("codex_r10_row_reduction_base", BASE_PATH)
    base = builder.build_model()
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)

    live = equality["live_multiplier_orbits"].astype(np.int32)
    forced = equality["forced_multiplier_orbits"].astype(np.int32)
    if len(live) != LIVE_COUNT or len(forced) != 2085:
        raise AssertionError("unexpected F1 partition")
    if sorted(map(int, np.concatenate((live, forced)))) != list(
        range(2611)
    ):
        raise AssertionError("F1 live/forced IDs do not partition the variables")

    normalization = unpack_integer_csr(equality, "normalization_live")
    target_nu = unpack_integer_csr(equality, "target_nu_live")
    target_gram = unpack_integer_csr(equality, "target_gram")
    gram_face = unpack_integer_csr(blowup, "gram_face")
    if normalization.shape != (NORMALIZATION_COUNT, LIVE_COUNT):
        raise AssertionError("wrong normalization shape")
    if target_nu.shape != (TARGET_COUNT, LIVE_COUNT):
        raise AssertionError("wrong multiplier target shape")
    if target_gram.shape != (TARGET_COUNT, GRAM_COUNT):
        raise AssertionError("wrong Gram target shape")
    if gram_face.shape != (6129, GRAM_COUNT):
        raise AssertionError("wrong H shape")

    rows = affine_rows(normalization, target_nu, target_gram)
    prime_results = [
        modular_selector(gram_face, rows, prime) for prime in PRIMES
    ]
    first, second = prime_results
    if first.rank_h != second.rank_h != 6129:
        raise AssertionError("unexpected H ranks")
    if first.rank_h != 6129 or second.rank_h != 6129:
        raise AssertionError("H is not full row rank over both primes")
    if first.keep_rows != second.keep_rows:
        raise AssertionError("row selectors differ between primes")
    if len(first.keep_rows) != 388 or len(first.drop_rows) != 60:
        raise AssertionError("unexpected face-restricted affine rank")
    if first.keep_rows[:NORMALIZATION_COUNT] != list(
        range(NORMALIZATION_COUNT)
    ):
        raise AssertionError("normalization-first selector dropped a normalization")

    dependencies = reconstruct_dependencies(first, second)
    dependency = dependency_matrix(first.drop_rows, dependencies)
    dependency_pivots = dependency[
        np.arange(len(first.drop_rows)), first.drop_rows
    ].A1.astype(np.int64)
    if np.any(dependency_pivots <= 0):
        raise AssertionError("dependency pivot coefficients are not positive")

    affine_nu = sp.vstack(
        [normalization, target_nu], format="csr"
    ).astype(np.int64)
    affine_gram = sp.vstack(
        [
            sp.csr_matrix(
                (NORMALIZATION_COUNT, GRAM_COUNT), dtype=np.int64
            ),
            target_gram,
        ],
        format="csr",
    ).astype(np.int64)
    affine_rhs = np.concatenate(
        [
            equality["normalization_rhs"],
            equality["target_rhs"],
        ]
    ).astype(np.int64)

    if not sparse_is_zero(dependency @ affine_nu):
        raise AssertionError("dependency does not cancel live multipliers")
    if np.any(np.asarray(dependency @ affine_rhs).reshape(-1)):
        raise AssertionError("dependency does not cancel the affine RHS")
    gram_dependencies = (dependency @ affine_gram).astype(np.int64).tocsr()
    quotient_check = exact_gram_dependency_gate(
        builder, base, blowup, gram_dependencies
    )

    keep = np.asarray(first.keep_rows, dtype=np.int32)
    drop = np.asarray(first.drop_rows, dtype=np.int32)
    keep_target = (keep[keep >= NORMALIZATION_COUNT] - NORMALIZATION_COUNT)
    drop_target = (drop - NORMALIZATION_COUNT)
    reduced_nu = affine_nu[keep, :].tocsr()
    reduced_gram = affine_gram[keep, :].tocsr()
    reduced_rhs = affine_rhs[keep]

    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "base_sha256": np.asarray([hashes["base"]]),
        "equality_data_sha256": np.asarray([hashes["equality"]]),
        "blowup_data_sha256": np.asarray([hashes["blowup"]]),
        "primes": np.asarray(PRIMES, dtype=np.int64),
        "rank_h_by_prime": np.asarray(
            [result.rank_h for result in prime_results], dtype=np.int32
        ),
        "rank_augmented_by_prime": np.asarray(
            [
                result.rank_h + len(result.keep_rows)
                for result in prime_results
            ],
            dtype=np.int32,
        ),
        "affine_rank_mod_h_by_prime": np.asarray(
            [len(result.keep_rows) for result in prime_results],
            dtype=np.int32,
        ),
        "live_multiplier_orbits": live,
        "forced_multiplier_orbits": forced,
        "keep_global_rows": keep,
        "drop_global_rows": drop,
        "keep_target_rows": keep_target.astype(np.int32),
        "drop_target_rows": drop_target.astype(np.int32),
        "dependency_pivot_coefficients": dependency_pivots,
        "affine_rhs": reduced_rhs.astype(np.int64),
    }
    matrix_metadata = {
        "affine_nu": pack_integer_csr(
            payload, "affine_nu", reduced_nu
        ),
        "affine_gram": pack_integer_csr(
            payload, "affine_gram", reduced_gram
        ),
        "dependency": pack_integer_csr(
            payload, "dependency", dependency
        ),
        "dependency_gram": pack_integer_csr(
            payload, "dependency_gram", gram_dependencies
        ),
    }

    support_sizes = np.diff(dependency.indptr)
    maximum_coefficient = max(
        (abs(int(value)) for value in dependency.data), default=0
    )
    summary: dict[str, object] = {
        "source_sha256": hashes,
        "face_variables": {
            "live_multiplier_orbits": LIVE_COUNT,
            "forced_multiplier_orbits_removed": len(forced),
            "invariant_gram_variables": GRAM_COUNT,
            "gram_face_rank": 6129,
            "gram_face_dimension": 2518,
            "linear_face_variables": 3044,
        },
        "affine_rows": {
            "normalization_original": NORMALIZATION_COUNT,
            "target_original": TARGET_COUNT,
            "original_total": AFFINE_COUNT,
            "normalization_retained": NORMALIZATION_COUNT,
            "target_retained": len(keep_target),
            "retained_total": len(keep),
            "target_omitted": len(drop_target),
            "exact_rank_mod_H": len(keep),
        },
        "keep_global_rows": first.keep_rows,
        "drop_global_rows": first.drop_rows,
        "keep_target_rows": keep_target.tolist(),
        "drop_target_rows": drop_target.tolist(),
        "modular_checks": [
            {
                "prime": result.prime,
                "rank_H": result.rank_h,
                "rank_H_plus_affine": result.rank_h
                + len(result.keep_rows),
                "affine_rank_mod_H": len(result.keep_rows),
                "seconds": result.seconds,
            }
            for result in prime_results
        ],
        "dependency_certificate": {
            "count": len(drop),
            "triangular_pivot_coefficients": (
                "positive integers after primitive denominator clearing"
            ),
            "minimum_pivot_coefficient": int(dependency_pivots.min()),
            "maximum_pivot_coefficient": int(dependency_pivots.max()),
            "coefficient_storage": "int64",
            "maximum_absolute_coefficient": maximum_coefficient,
            "minimum_support_size": int(support_sizes.min()),
            "maximum_support_size": int(support_sizes.max()),
            "lambda_times_live_nu_map": "exact zero",
            "lambda_times_rhs": "exact zero",
            "gram_quotient_check": quotient_check,
        },
        "matrix_metadata": matrix_metadata,
        "exact_rank_argument": (
            "The 60 exact triangular dependencies give rank <=388. "
            "The retained rows increase rank(H) by 388 modulo each listed "
            "prime, so a rational 388-minor is nonzero and rank >=388."
        ),
        "model_instruction": (
            "Instantiate nu_live in R^526 directly; use affine_nu@nu_live + "
            "affine_gram@q = affine_rhs, Hq=0, nu_live>=t, t>=0, and the "
            "unchanged exact quotient PSD cones. Do not instantiate or "
            "zero-fix the 2085 forced multiplier coordinates."
        ),
        "scope": (
            "Exact affine reduction on the registered c=25, degree-4, "
            "56-cut D22 plateau face. No SDP solved and no theorem claim."
        ),
    }
    return payload, summary


def write_report(path: Path, summary: dict[str, object]) -> None:
    affine = summary["affine_rows"]
    dependency = summary["dependency_certificate"]
    modular = summary["modular_checks"]
    lines = [
        "# Exact affine-row reduction on the Gamma_11 plateau face",
        "",
        "## Result",
        "",
        (
            f"The 448 original affine rows have exact rank "
            f"{affine['exact_rank_mod_H']} modulo the 6,129-row Gram face H."
        ),
        (
            f"All {affine['normalization_retained']} normalization rows and "
            f"{affine['target_retained']} of {affine['target_original']} "
            "target rows are retained; 60 target rows are omitted."
        ),
        "",
        "The fully facially reduced linear model has 526 live multiplier "
        "variables plus the 2,518-dimensional Gram face, hence 3,044 linear "
        "face variables. The 2,085 forced-zero multiplier coordinates are "
        "not instantiated.",
        "",
        "## Exact rank certificate",
        "",
        (
            "Each omitted row has a reconstructed integer relation whose "
            "coefficient on that omitted row is positive and whose other "
            "coefficients use retained rows only."
        ),
        (
            f"The 60 relations have support sizes "
            f"{dependency['minimum_support_size']} through "
            f"{dependency['maximum_support_size']} and maximum absolute "
            f"coefficient {dependency['maximum_absolute_coefficient']}."
        ),
        (
            "Exact integer multiplication gives lambda*A_nu=0 and "
            "lambda*b=0. For the Gram part, every relation was pulled back "
            "blockwise through the exact quotient Q=B R B^T and vanished "
            "identically."
        ),
        (
            "Thus the triangular dependency family proves rank <=388. "
            "The independent modular minors prove rank >=388 over Q."
        ),
        "",
        "```text",
    ]
    for item in modular:
        lines.append(
            f"p={item['prime']} rank(H)={item['rank_H']} "
            f"rank([H;A])={item['rank_H_plus_affine']} "
            f"rank(A mod H)={item['affine_rank_mod_H']}"
        )
    lines.extend(
        [
            "```",
            "",
            "## Solver-model selector",
            "",
            "Use the exported matrices exactly as",
            "",
            "```text",
            "nu_live in R^526",
            "affine_nu * nu_live + affine_gram * q = affine_rhs  # 388 rows",
            "H * q = 0                                           # unchanged",
            "nu_live >= t",
            "t >= 0",
            "quotient Gram principal blocks >= t I               # unchanged",
            "```",
            "",
            "Do not create the 2,085 forced multiplier variables and do not "
            "add 2,085 zero-fixing equalities. The constant c=25, degree 4, "
            "all 56 cuts, D22 invariance, H, and quotient PSD cones are "
            "unchanged.",
            "",
            "## Scope",
            "",
            "No SDP was solved. This is an exact facial/row reduction and "
            "does not itself constitute a Q4 certificate or theorem proof.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload, summary = build_reduction()
    np.savez_compressed(args.output, **payload)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_report(args.report, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"OUTPUT={args.output.resolve()}")
    print(f"SUMMARY={args.summary.resolve()}")
    print(f"REPORT={args.report.resolve()}")
    print(f"SHA256_SCRIPT={sha256(Path(__file__))}")
    print(f"SHA256_OUTPUT={sha256(args.output)}")
    print(f"SHA256_SUMMARY={sha256(args.summary)}")
    print(f"SHA256_REPORT={sha256(args.report)}")
    print("EXACT_ROW_REDUCTION_PASS: no SDP run and no theorem claim")


if __name__ == "__main__":
    main()
