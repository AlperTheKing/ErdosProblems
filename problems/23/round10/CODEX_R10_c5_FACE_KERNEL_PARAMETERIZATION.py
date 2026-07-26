"""Exact full kernel parameterization of the Gamma_11 plateau Gram face.

For every representative Gram block, this program enumerates stabilizer
Reynolds averages of exact quotient units B E_ab B^T, clears denominators,
primitive-normalizes the resulting invariant Gram-orbit vector, and selects a
complete independent set modulo a prime.

The block-diagonal integer matrix Zq has shape 8647 x 2518 and satisfies

    H Zq = 0

exactly.  A second-prime replay proves rank(Zq)=2518 over Q.  The archive also
contains a blockwise float64 QR basis spanning the same numerical columns.
That QR basis is steering/preconditioning data only; the integer Zq is the
exact artifact used for reconstruction and replay.

No SDP is built or solved.
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
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
ROW_SOURCE = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
DEFAULT_OUTPUT = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
DEFAULT_SUMMARY = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_summary.json"
DEFAULT_REPORT = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_REPORT.md"

EXPECTED_ROW_SOURCE_SHA256 = (
    "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A"
)
EXPECTED_EQUALITY_SHA256 = (
    "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F"
)
EXPECTED_BLOWUP_SHA256 = (
    "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730"
)
PRIMES = (1_000_003, 2_000_003)
GRAM_ROWS = 8647
FACE_COLUMNS = 2518


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


def pack_csr(
    payload: dict[str, np.ndarray], name: str, matrix: sp.spmatrix
) -> dict[str, object]:
    csr = matrix.astype(np.int64).tocsr()
    csr.eliminate_zeros()
    payload[f"{name}_data"] = csr.data.astype(np.int64)
    payload[f"{name}_indices"] = csr.indices.astype(np.int32)
    payload[f"{name}_indptr"] = csr.indptr.astype(np.int64)
    payload[f"{name}_shape"] = np.asarray(csr.shape, dtype=np.int64)
    return {"shape": list(csr.shape), "nnz": int(csr.nnz)}


class VectorModularSpan:
    """Column span in F_p^n using vectorized dense reductions."""

    def __init__(self, prime: int) -> None:
        self.prime = prime
        self.pivots: list[int] = []
        self.basis: list[np.ndarray] = []

    def add(self, source: np.ndarray) -> bool:
        prime = self.prime
        row = np.mod(source, prime).astype(np.int64, copy=True)
        for pivot, base in zip(self.pivots, self.basis):
            factor = int(row[pivot])
            if factor:
                row = np.mod(row - factor * base, prime)
        nonzero = np.flatnonzero(row)
        if not len(nonzero):
            return False
        pivot = int(nonzero[0])
        row = np.mod(
            row * pow(int(row[pivot]), prime - 2, prime), prime
        )
        self.pivots.append(pivot)
        self.basis.append(row)
        return True


def modular_column_rank(matrix: np.ndarray, prime: int) -> int:
    span = VectorModularSpan(prime)
    for column in range(matrix.shape[1]):
        span.add(matrix[:, column])
    return len(span.pivots)


def first_entry_representatives(entry_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    count = int(entry_ids.max()) + 1
    rows = np.full(count, -1, dtype=np.int32)
    columns = np.full(count, -1, dtype=np.int32)
    for row in range(entry_ids.shape[0]):
        for column in range(row, entry_ids.shape[1]):
            entry_id = int(entry_ids[row, column])
            if rows[entry_id] < 0:
                rows[entry_id] = row
                columns[entry_id] = column
    if np.any(rows < 0) or np.any(columns < 0):
        raise AssertionError("missing invariant-entry representative")
    return rows, columns


def inverse_permutations(builder, orbit) -> list[np.ndarray]:
    output = []
    order = len(orbit.basis)
    for element in orbit.stabilizer:
        permutation = builder.image_permutation(
            orbit.basis, orbit.basis, element
        )
        inverse = np.empty_like(permutation)
        inverse[permutation] = np.arange(order, dtype=np.int32)
        output.append(inverse)
    return output


def reynolds_tables(
    z: np.ndarray,
    representative_rows: np.ndarray,
    representative_columns: np.ndarray,
    inverses: list[np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    left = np.stack(
        [z[inverse[representative_rows], :] for inverse in inverses]
    )
    right = np.stack(
        [z[inverse[representative_columns], :] for inverse in inverses]
    )
    return left, right


def primitive_candidate(
    left_table: np.ndarray,
    right_table: np.ndarray,
    left: int,
    right: int,
) -> tuple[np.ndarray, int] | None:
    vector = np.sum(
        left_table[:, :, left] * right_table[:, :, right], axis=0
    )
    if left != right:
        vector += np.sum(
            left_table[:, :, right] * right_table[:, :, left], axis=0
        )
    common_gcd = int(np.gcd.reduce(np.abs(vector)))
    if common_gcd == 0:
        return None
    vector = vector // common_gcd
    return vector.astype(np.int64), common_gcd


def build_parameterization() -> tuple[
    dict[str, np.ndarray], dict[str, object]
]:
    hashes = {
        "row_source": sha256(ROW_SOURCE),
        "equality": sha256(EQUALITY_PATH),
        "blowup": sha256(BLOWUP_PATH),
    }
    expected = {
        "row_source": EXPECTED_ROW_SOURCE_SHA256,
        "equality": EXPECTED_EQUALITY_SHA256,
        "blowup": EXPECTED_BLOWUP_SHA256,
    }
    if hashes != expected:
        raise AssertionError(f"pinned input hash mismatch: {hashes}")

    helpers = load_module("codex_r10_kernel_helpers", ROW_SOURCE)
    builder = helpers.load_module(
        "codex_r10_kernel_base", helpers.BASE_PATH
    )
    base = builder.build_model()
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    gram_face = unpack_csr(blowup, "gram_face")
    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    face_dimensions = equality["gram_face_dimensions"].astype(np.int64)
    face_ranks = equality["gram_constraint_ranks"].astype(np.int64)

    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])

    global_rows: list[int] = []
    global_columns: list[int] = []
    global_values: list[int] = []
    selected_metadata: list[list[int]] = []
    block_column_offsets: list[int] = []
    solver_basis_offsets = [0]
    solver_basis_values: list[np.ndarray] = []
    block_summaries: list[dict[str, object]] = []
    z_offset = 0
    face_row_offset = 0
    total_candidates = 0
    total_zero_candidates = 0
    build_start = time.perf_counter()

    for block_index, orbit in enumerate(base.gram_orbits):
        block_start = time.perf_counter()
        order = len(orbit.basis)
        q_offset = int(q_offsets[block_index])
        q_dimension = int(q_dimensions[block_index])
        face_dimension = int(face_dimensions[block_index])
        face_rank = int(face_ranks[block_index])
        if q_dimension - face_rank != face_dimension:
            raise AssertionError("block face dimension is inconsistent")
        block_column_offsets.append(z_offset)

        exact_z, kernel_denominator, _pivots, free = (
            helpers.integer_kernel_parameter(
                grouped.get(block_index, []), order
            )
        )
        if len(free) * (len(free) + 1) // 2 < face_dimension:
            raise AssertionError("quotient symmetric space is too small")
        if face_dimension == 0:
            solver_basis_offsets.append(solver_basis_offsets[-1])
            block_summaries.append(
                {
                    "block": block_index,
                    "q_dimension": q_dimension,
                    "face_dimension": 0,
                    "kernel_rank": len(grouped.get(block_index, [])),
                    "quotient_order": len(free),
                    "candidates_tested": 0,
                    "zero_reynolds_candidates": 0,
                    "nnz": 0,
                    "coefficient_min": 0,
                    "coefficient_max": 0,
                    "coefficient_bits": 0,
                    "raw_condition_2": None,
                    "column_normalized_condition_2": None,
                    "solver_basis_orthogonality_inf": 0.0,
                    "solver_basis_H_residual_inf": 0.0,
                    "seconds": time.perf_counter() - block_start,
                }
            )
            face_row_offset += face_rank
            continue

        z_integer = np.asarray(
            [[int(value) for value in row] for row in exact_z.to_list()],
            dtype=np.int64,
        )
        representative_rows, representative_columns = (
            first_entry_representatives(orbit.entry_ids)
        )
        left_table, right_table = reynolds_tables(
            z_integer,
            representative_rows,
            representative_columns,
            inverse_permutations(builder, orbit),
        )
        span = VectorModularSpan(PRIMES[0])
        selected: list[np.ndarray] = []
        selected_pairs: list[tuple[int, int, int]] = []
        tested = 0
        zero_candidates = 0
        quotient_order = len(free)
        for left in range(quotient_order):
            for right in range(left, quotient_order):
                tested += 1
                candidate = primitive_candidate(
                    left_table, right_table, left, right
                )
                if candidate is None:
                    zero_candidates += 1
                    continue
                vector, cleared_gcd = candidate
                if not span.add(vector):
                    continue
                selected.append(vector)
                selected_pairs.append((left, right, cleared_gcd))
                if len(selected) == face_dimension:
                    break
            if len(selected) == face_dimension:
                break
        if len(selected) != face_dimension:
            raise AssertionError(
                f"block {block_index}: found {len(selected)} of "
                f"{face_dimension} required directions"
            )

        block_matrix = np.column_stack(selected).astype(np.int64)
        if modular_column_rank(block_matrix, PRIMES[1]) != face_dimension:
            raise AssertionError(
                f"block {block_index} loses rank modulo {PRIMES[1]}"
            )
        block_h = gram_face[
            face_row_offset : face_row_offset + face_rank,
            q_offset : q_offset + q_dimension,
        ].tocsr()
        hz = block_h @ block_matrix
        if np.any(hz):
            raise AssertionError(f"block {block_index}: HZ is not exact zero")

        for local_column, vector in enumerate(selected):
            nonzero = np.flatnonzero(vector)
            global_rows.extend(q_offset + int(row) for row in nonzero)
            global_columns.extend(
                [z_offset + local_column] * len(nonzero)
            )
            global_values.extend(int(vector[row]) for row in nonzero)
            left, right, cleared_gcd = selected_pairs[local_column]
            selected_metadata.append(
                [
                    block_index,
                    left,
                    right,
                    cleared_gcd,
                    int(kernel_denominator),
                ]
            )

        block_float = block_matrix.astype(np.float64)
        singular_values = np.linalg.svd(
            block_float, compute_uv=False
        )
        column_norms = np.linalg.norm(block_float, axis=0)
        normalized_singular_values = np.linalg.svd(
            block_float / column_norms, compute_uv=False
        )
        solver_q, _solver_r = np.linalg.qr(
            block_float, mode="reduced"
        )
        solver_basis_values.append(solver_q.reshape(-1))
        solver_basis_offsets.append(
            solver_basis_offsets[-1] + solver_q.size
        )
        orthogonality = float(
            np.max(
                np.abs(
                    solver_q.T @ solver_q
                    - np.eye(face_dimension)
                )
            )
        )
        h_residual = float(
            np.max(np.abs(block_h.astype(float) @ solver_q))
        ) if face_rank else 0.0
        nonzero_values = block_matrix[np.nonzero(block_matrix)]
        coefficient_min = int(nonzero_values.min())
        coefficient_max = int(nonzero_values.max())
        coefficient_bits = max(
            abs(coefficient_min).bit_length(),
            abs(coefficient_max).bit_length(),
        )
        block_summaries.append(
            {
                "block": block_index,
                "q_dimension": q_dimension,
                "face_dimension": face_dimension,
                "kernel_rank": len(grouped.get(block_index, [])),
                "quotient_order": quotient_order,
                "candidates_tested": tested,
                "zero_reynolds_candidates": zero_candidates,
                "nnz": int(np.count_nonzero(block_matrix)),
                "coefficient_min": coefficient_min,
                "coefficient_max": coefficient_max,
                "coefficient_bits": coefficient_bits,
                "raw_condition_2": float(
                    singular_values[0] / singular_values[-1]
                ),
                "column_normalized_condition_2": float(
                    normalized_singular_values[0]
                    / normalized_singular_values[-1]
                ),
                "solver_basis_orthogonality_inf": orthogonality,
                "solver_basis_H_residual_inf": h_residual,
                "seconds": time.perf_counter() - block_start,
            }
        )
        total_candidates += tested
        total_zero_candidates += zero_candidates
        z_offset += face_dimension
        face_row_offset += face_rank

    if z_offset != FACE_COLUMNS or face_row_offset != gram_face.shape[0]:
        raise AssertionError("global block offsets are inconsistent")
    exact_basis = sp.csr_matrix(
        (global_values, (global_rows, global_columns)),
        shape=(GRAM_ROWS, FACE_COLUMNS),
        dtype=np.int64,
    )
    global_hz = gram_face @ exact_basis
    global_hz.eliminate_zeros()
    if global_hz.nnz:
        raise AssertionError("global HZ is not exact zero")

    nonzero_values = exact_basis.data
    maximum_coefficient = int(np.max(np.abs(nonzero_values)))
    maximum_coefficient_bits = maximum_coefficient.bit_length()
    solver_data = (
        np.concatenate(solver_basis_values)
        if solver_basis_values
        else np.asarray([], dtype=np.float64)
    )
    solver_memory_bytes = int(solver_data.nbytes)
    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "row_source_sha256": np.asarray([hashes["row_source"]]),
        "equality_data_sha256": np.asarray([hashes["equality"]]),
        "blowup_data_sha256": np.asarray([hashes["blowup"]]),
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "rank_by_prime": np.asarray(
            [FACE_COLUMNS, FACE_COLUMNS], dtype=np.int32
        ),
        "gram_offsets": q_offsets.astype(np.int32),
        "gram_qdims": q_dimensions.astype(np.int32),
        "gram_face_dimensions": face_dimensions.astype(np.int32),
        "face_column_offsets": np.asarray(
            block_column_offsets, dtype=np.int32
        ),
        "selected_direction_metadata": np.asarray(
            selected_metadata, dtype=np.int64
        ),
        "solver_basis_data": solver_data,
        "solver_basis_offsets": np.asarray(
            solver_basis_offsets, dtype=np.int64
        ),
    }
    exact_metadata = pack_csr(
        payload, "exact_basis", exact_basis
    )
    nonempty_blocks = [
        item for item in block_summaries if item["face_dimension"]
    ]
    summary: dict[str, object] = {
        "source_sha256": hashes,
        "exact_basis": {
            **exact_metadata,
            "rank": FACE_COLUMNS,
            "rank_primes": list(PRIMES),
            "H_times_Z": "exact zero",
            "coefficient_min": int(nonzero_values.min()),
            "coefficient_max": int(nonzero_values.max()),
            "maximum_absolute_coefficient": maximum_coefficient,
            "maximum_coefficient_bits": maximum_coefficient_bits,
        },
        "solver_preconditioner": {
            "format": (
                "concatenated row-major dense block QR bases; offsets stored "
                "in solver_basis_offsets"
            ),
            "float64_values": int(solver_data.size),
            "memory_bytes": solver_memory_bytes,
            "maximum_block_orthogonality_inf": max(
                item["solver_basis_orthogonality_inf"]
                for item in nonempty_blocks
            ),
            "maximum_block_H_residual_inf": max(
                item["solver_basis_H_residual_inf"]
                for item in nonempty_blocks
            ),
            "minimum_raw_condition_2": min(
                item["raw_condition_2"] for item in nonempty_blocks
            ),
            "maximum_raw_condition_2": max(
                item["raw_condition_2"] for item in nonempty_blocks
            ),
            "minimum_column_normalized_condition_2": min(
                item["column_normalized_condition_2"]
                for item in nonempty_blocks
            ),
            "maximum_column_normalized_condition_2": max(
                item["column_normalized_condition_2"]
                for item in nonempty_blocks
            ),
            "warning": (
                "The float64 QR blocks are numerical steering data only. "
                "Exact reconstruction and replay use exact_basis."
            ),
        },
        "enumeration": {
            "candidates_tested": total_candidates,
            "zero_reynolds_candidates": total_zero_candidates,
            "seconds": time.perf_counter() - build_start,
        },
        "per_block": block_summaries,
        "scope": (
            "Exact build-only H-kernel parameterization with a numerical QR "
            "preconditioner. No SDP solved and no theorem claim."
        ),
    }
    return payload, summary


def write_report(path: Path, summary: dict[str, object]) -> None:
    exact = summary["exact_basis"]
    solver = summary["solver_preconditioner"]
    enumeration = summary["enumeration"]
    central = summary["per_block"][0]
    lines = [
        "# Exact full parameterization of the plateau Gram face",
        "",
        "## Exact artifact",
        "",
        (
            f"`Zq` has shape {exact['shape']}, {exact['nnz']} nonzeros, "
            f"rank {exact['rank']}, and satisfies `H Zq=0` exactly."
        ),
        (
            f"Its coefficient range is [{exact['coefficient_min']}, "
            f"{exact['coefficient_max']}], with at most "
            f"{exact['maximum_coefficient_bits']} bits."
        ),
        (
            f"Full rank was replayed modulo {exact['rank_primes']}."
        ),
        "",
        "## Central block",
        "",
        (
            f"The central block basis has shape "
            f"{central['q_dimension']} x {central['face_dimension']}, "
            f"{central['nnz']} nonzeros, and was selected after "
            f"{central['candidates_tested']} Reynolds candidates."
        ),
        (
            f"Its primitive coefficient range is "
            f"[{central['coefficient_min']}, {central['coefficient_max']}]."
        ),
        (
            f"Raw condition number: {central['raw_condition_2']:.6e}; "
            "column-normalized condition number: "
            f"{central['column_normalized_condition_2']:.6e}."
        ),
        "",
        "## Numerical solver preconditioner",
        "",
        (
            "The archive also stores a blockwise float64 QR basis spanning "
            "the exact columns numerically."
        ),
        (
            f"It uses {solver['memory_bytes']} bytes; maximum block "
            f"orthogonality error is "
            f"{solver['maximum_block_orthogonality_inf']:.3e}, and maximum "
            f"`H Q` residual is "
            f"{solver['maximum_block_H_residual_inf']:.3e}."
        ),
        "",
        "The QR blocks are numerical steering data only. Exact rational "
        "reconstruction must return to the integer `Zq`/kernel quotient and "
        "pass the exact gates.",
        "",
        "## Enumeration",
        "",
        (
            f"Tested {enumeration['candidates_tested']} Reynolds candidates "
            f"in {enumeration['seconds']:.3f} seconds; "
            f"{enumeration['zero_reynolds_candidates']} averaged to zero."
        ),
        "",
        "## Scope",
        "",
        "No SDP was built or solved. This artifact removes `Hq=0` by exact "
        "parameterization but does not itself prove feasibility.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    payload, summary = build_parameterization()
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
    print("EXACT_KERNEL_PARAMETERIZATION_PASS: no SDP run and no theorem claim")


if __name__ == "__main__":
    main()
