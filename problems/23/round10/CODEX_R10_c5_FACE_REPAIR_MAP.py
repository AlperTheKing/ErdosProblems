"""Build a sparse exact coordinate-repair map for the 388-row plateau face.

The exported square repair system uses:

* 322 individual live multiplier-orbit coordinates; and
* 66 primitive integer D22-invariant Gram directions in ker(H).

Each Gram direction is constructed without a projector.  In an exact kernel
quotient Q=B R B^T, start with one symmetric quotient matrix unit E_ab,
average B E_ab B^T over the representative block stabilizer, read its
invariant Gram-entry orbit values, clear the common denominator, and divide
by the integer gcd.  Thus every stored direction preserves both the forced
evaluation kernels and D22 invariance.

The resulting 388x388 integer matrix is nonsingular modulo three primes and
therefore over Q.  A future rationalization program can solve this square
system for the exact affine residual and alter only the selected coordinates.
No dense affine projector is formed or stored.

No SDP is imported or run.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
ROW_REDUCTION_SOURCE = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION.py"
ROW_REDUCTION_DATA = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
DEFAULT_OUTPUT = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP_data.npz"
DEFAULT_SUMMARY = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP_summary.json"
DEFAULT_REPORT = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP_REPORT.md"

EXPECTED_ROW_SOURCE_SHA256 = (
    "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A"
)
EXPECTED_ROW_DATA_SHA256 = (
    "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C"
)
EXPECTED_BLOWUP_SHA256 = (
    "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730"
)
PRIMES = (1_000_003, 2_000_003, 998_244_353)
AFFINE_RANK = 388
LIVE_COUNT = 526
GRAM_COUNT = 8647


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


class ModularColumnSpan:
    def __init__(self, prime: int) -> None:
        self.prime = prime
        self.rows: dict[int, dict[int, int]] = {}

    def add(self, source) -> bool:
        prime = self.prime
        row = {
            index: int(value) % prime
            for index, value in enumerate(source)
            if int(value) % prime
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
                return True
            factor = row[pivot]
            for column, value in base.items():
                updated = (
                    row.get(column, 0) - factor * value
                ) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
        return False


def modular_row_rank(matrix: sp.csr_matrix, prime: int) -> int:
    span = ModularColumnSpan(prime)
    for row in range(matrix.shape[0]):
        dense = np.zeros(matrix.shape[1], dtype=object)
        dense[matrix.indices[matrix.indptr[row] : matrix.indptr[row + 1]]] = (
            matrix.data[matrix.indptr[row] : matrix.indptr[row + 1]]
        )
        span.add(dense)
    return len(span.rows)


def first_entry_representatives(entry_ids: np.ndarray) -> list[tuple[int, int]]:
    count = int(entry_ids.max()) + 1
    representatives: list[tuple[int, int] | None] = [None] * count
    for row in range(entry_ids.shape[0]):
        for column in range(row, entry_ids.shape[1]):
            entry_id = int(entry_ids[row, column])
            if representatives[entry_id] is None:
                representatives[entry_id] = (row, column)
    if any(item is None for item in representatives):
        raise AssertionError("missing Gram-entry representative")
    return [item for item in representatives if item is not None]


def inverse_stabilizer_permutations(builder, orbit) -> list[np.ndarray]:
    inverses = []
    order = len(orbit.basis)
    for element in orbit.stabilizer:
        permutation = builder.image_permutation(
            orbit.basis, orbit.basis, element
        )
        inverse = np.empty_like(permutation)
        inverse[permutation] = np.arange(order, dtype=np.int32)
        inverses.append(inverse)
    return inverses


def primitive_reynolds_direction(
    z_rows: list[list[int]],
    quotient_left: int,
    quotient_right: int,
    representatives: list[tuple[int, int]],
    inverse_permutations: list[np.ndarray],
) -> tuple[np.ndarray, int] | None:
    values: list[int] = []
    diagonal = quotient_left == quotient_right
    for row, column in representatives:
        total = 0
        for inverse in inverse_permutations:
            source_row = int(inverse[row])
            source_column = int(inverse[column])
            if diagonal:
                total += (
                    z_rows[source_row][quotient_left]
                    * z_rows[source_column][quotient_left]
                )
            else:
                total += (
                    z_rows[source_row][quotient_left]
                    * z_rows[source_column][quotient_right]
                    + z_rows[source_row][quotient_right]
                    * z_rows[source_column][quotient_left]
                )
        values.append(total)
    common_gcd = 0
    for value in values:
        common_gcd = math.gcd(common_gcd, abs(value))
    if common_gcd == 0:
        return None
    primitive = [value // common_gcd for value in values]
    limit = np.iinfo(np.int64)
    if any(value < limit.min or value > limit.max for value in primitive):
        raise OverflowError("primitive Gram direction does not fit int64")
    return np.asarray(primitive, dtype=np.int64), common_gcd


@dataclass
class DirectionMetadata:
    block: int
    quotient_left: int
    quotient_right: int
    cleared_gcd: int
    kernel_denominator: int


def build_repair_map() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    hashes = {
        "row_source": sha256(ROW_REDUCTION_SOURCE),
        "row_data": sha256(ROW_REDUCTION_DATA),
        "blowup": sha256(BLOWUP_PATH),
    }
    expected = {
        "row_source": EXPECTED_ROW_SOURCE_SHA256,
        "row_data": EXPECTED_ROW_DATA_SHA256,
        "blowup": EXPECTED_BLOWUP_SHA256,
    }
    if hashes != expected:
        raise AssertionError(f"pinned input hash mismatch: {hashes}")

    row_module = load_module(
        "codex_r10_repair_row_helpers", ROW_REDUCTION_SOURCE
    )
    builder = row_module.load_module(
        "codex_r10_repair_base", row_module.BASE_PATH
    )
    base = builder.build_model()
    row_data = np.load(ROW_REDUCTION_DATA, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    affine_nu = unpack_csr(row_data, "affine_nu")
    affine_gram = unpack_csr(row_data, "affine_gram")
    gram_face = unpack_csr(blowup, "gram_face")
    if affine_nu.shape != (AFFINE_RANK, LIVE_COUNT):
        raise AssertionError("wrong reduced multiplier-map shape")
    if affine_gram.shape != (AFFINE_RANK, GRAM_COUNT):
        raise AssertionError("wrong reduced Gram-map shape")

    span = ModularColumnSpan(PRIMES[0])
    selected_nu: list[int] = []
    for column in range(LIVE_COUNT):
        if span.add(affine_nu[:, column].toarray().reshape(-1)):
            selected_nu.append(column)
    if len(selected_nu) != 322:
        raise AssertionError(
            f"expected live-multiplier column rank 322, got {len(selected_nu)}"
        )

    grouped: dict[int, list[list[int]]] = {}
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped.setdefault(int(block), []).append(
            [int(value) for value in row]
        )

    offsets = blowup["gram_offsets"].astype(np.int64)
    directions: list[tuple[int, np.ndarray]] = []
    metadata: list[DirectionMetadata] = []
    tested_candidates = 0
    zero_reynolds_candidates = 0

    for block_index, orbit in enumerate(base.gram_orbits):
        order = len(orbit.basis)
        z, denominator, _pivots, free = (
            row_module.integer_kernel_parameter(
                grouped.get(block_index, []), order
            )
        )
        quotient_order = len(free)
        if quotient_order == 0:
            continue
        z_rows = [
            [int(value) for value in row] for row in z.to_list()
        ]
        representatives = first_entry_representatives(orbit.entry_ids)
        inverses = inverse_stabilizer_permutations(builder, orbit)
        q_offset = int(offsets[block_index])
        q_dimension = int(orbit.variable.size)

        # The first three coordinate rows of the central quotient provide 64
        # independent affine directions.  Continuing all 11,935 central
        # candidates is unnecessary; the last two ranks appear sparsely in
        # blocks 1 and 5.
        left_limit = min(3, quotient_order) if block_index == 0 else quotient_order
        for left in range(left_limit):
            for right in range(left, quotient_order):
                tested_candidates += 1
                result = primitive_reynolds_direction(
                    z_rows, left, right, representatives, inverses
                )
                if result is None:
                    zero_reynolds_candidates += 1
                    continue
                local_direction, cleared_gcd = result
                affine_column = (
                    affine_gram[
                        :, q_offset : q_offset + q_dimension
                    ]
                    @ local_direction
                )
                if not span.add(affine_column):
                    continue
                directions.append((q_offset, local_direction))
                metadata.append(
                    DirectionMetadata(
                        block=block_index,
                        quotient_left=left,
                        quotient_right=right,
                        cleared_gcd=cleared_gcd,
                        kernel_denominator=denominator,
                    )
                )
                if len(span.rows) == AFFINE_RANK:
                    break
            if len(span.rows) == AFFINE_RANK:
                break
        if len(span.rows) == AFFINE_RANK:
            break

    if len(directions) != 66 or len(span.rows) != AFFINE_RANK:
        raise AssertionError(
            f"repair completion failed: directions={len(directions)}, "
            f"rank={len(span.rows)}"
        )
    block_histogram: dict[int, int] = {}
    for item in metadata:
        block_histogram[item.block] = block_histogram.get(item.block, 0) + 1
    if block_histogram != {0: 64, 1: 1, 5: 1}:
        raise AssertionError(
            f"unexpected repair-direction blocks {block_histogram}"
        )

    direction_rows: list[int] = []
    direction_columns: list[int] = []
    direction_values: list[int] = []
    for direction_index, (offset, local) in enumerate(directions):
        for local_row, value in enumerate(local):
            if int(value):
                direction_rows.append(offset + local_row)
                direction_columns.append(direction_index)
                direction_values.append(int(value))
    gram_directions = sp.csr_matrix(
        (
            direction_values,
            (direction_rows, direction_columns),
        ),
        shape=(GRAM_COUNT, len(directions)),
        dtype=np.int64,
    )

    hd = gram_face @ gram_directions
    hd.eliminate_zeros()
    if hd.nnz:
        raise AssertionError("a stored Gram repair direction leaves ker(H)")
    gram_columns = affine_gram @ gram_directions
    repair_matrix = sp.hstack(
        [affine_nu[:, selected_nu], gram_columns], format="csr"
    ).astype(np.int64)
    ranks = [
        modular_row_rank(repair_matrix, prime) for prime in PRIMES
    ]
    if ranks != [AFFINE_RANK] * len(PRIMES):
        raise AssertionError(f"repair matrix loses rank: {ranks}")

    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "row_reduction_source_sha256": np.asarray([hashes["row_source"]]),
        "row_reduction_data_sha256": np.asarray([hashes["row_data"]]),
        "blowup_data_sha256": np.asarray([hashes["blowup"]]),
        "rank_primes": np.asarray(PRIMES, dtype=np.int64),
        "repair_rank_by_prime": np.asarray(ranks, dtype=np.int32),
        "selected_live_nu_columns": np.asarray(
            selected_nu, dtype=np.int32
        ),
        "selected_live_nu_orbit_ids": row_data[
            "live_multiplier_orbits"
        ][selected_nu].astype(np.int32),
        "gram_direction_metadata": np.asarray(
            [
                [
                    item.block,
                    item.quotient_left,
                    item.quotient_right,
                    item.cleared_gcd,
                    item.kernel_denominator,
                ]
                for item in metadata
            ],
            dtype=np.int64,
        ),
        "affine_rhs": row_data["affine_rhs"].astype(np.int64),
    }
    matrix_metadata = {
        "gram_directions": pack_csr(
            payload, "gram_directions", gram_directions
        ),
        "repair_matrix": pack_csr(
            payload, "repair_matrix", repair_matrix
        ),
    }
    summary: dict[str, object] = {
        "source_sha256": hashes,
        "repair_coordinates": {
            "live_multiplier_coordinates": len(selected_nu),
            "invariant_quotient_directions": len(directions),
            "total": repair_matrix.shape[1],
            "direction_block_histogram": block_histogram,
        },
        "construction": {
            "quotient_formula": "Q=B R B^T",
            "gram_direction_formula": (
                "primitive_integer(Reynolds_stabilizer(B E_ab B^T))"
            ),
            "tested_candidates": tested_candidates,
            "zero_reynolds_candidates": zero_reynolds_candidates,
            "H_times_gram_directions": "exact zero",
            "dense_projector": False,
        },
        "repair_matrix": {
            **matrix_metadata["repair_matrix"],
            "rank_primes": list(PRIMES),
            "rank_by_prime": ranks,
            "exact_rank": AFFINE_RANK,
        },
        "gram_directions": matrix_metadata["gram_directions"],
        "future_algorithm": [
            "Read a positive numerical point and extract 526 live nu values.",
            "For each representative Gram block take Q[C,C], rationally round it, lift with exact B, and Reynolds-average over the stabilizer.",
            "Form the exact residual r=b-A_nu*nu-A_gram*q.",
            "Solve the stored 388x388 integer repair system M*delta=r exactly; do not form a dense projector.",
            "Apply 322 corrections directly to selected nu coordinates and 66 corrections through the stored Gram directions.",
            "Require exact nonnegative nu, Hq=0, all 448 original equations, exact quotient PSD, exact expanded Q4_verify, and an independent replay.",
            "If a cone check fails, increase the rounding denominator. If the exact-binary repaired center itself lacks cone margin, reject the numerical point and request a more accurate positive iterate.",
        ],
        "finite_success_condition": (
            "For a numerical point sufficiently close to a strict relative-"
            "interior feasible point, exact centering followed by denominator "
            "refinement makes the repair tend to zero; openness of nu>0 and "
            "quotient Q>0 gives finite acceptance."
        ),
        "scope": (
            "Static exact repair-map construction only. No SDP run, no dense "
            "projector, no certificate, and no theorem claim."
        ),
    }
    return payload, summary


def write_report(path: Path, summary: dict[str, object]) -> None:
    repair = summary["repair_coordinates"]
    matrix = summary["repair_matrix"]
    lines = [
        "# Sparse exact repair map for a future plateau-face iterate",
        "",
        "## Result",
        "",
        (
            f"A square exact affine repair uses "
            f"{repair['live_multiplier_coordinates']} live multiplier "
            f"coordinates and {repair['invariant_quotient_directions']} "
            "D22-invariant quotient Gram directions."
        ),
        (
            "The Gram directions occur in representative blocks "
            f"{repair['direction_block_histogram']} and satisfy H d=0 exactly."
        ),
        (
            f"The integer repair matrix has shape {matrix['shape']}, "
            f"{matrix['nnz']} nonzeros, and rank 388 modulo each of "
            f"{matrix['rank_primes']}."
        ),
        "",
        "No dense affine projector is formed or stored.",
        "",
        "## Finite exact reconstruction algorithm",
        "",
    ]
    for index, step in enumerate(summary["future_algorithm"], start=1):
        lines.append(f"{index}. {step}")
    lines.extend(
        [
            "",
            "The exact repair solve changes only the 388 selected coordinates. "
            "Every Gram correction remains on the exact kernel face and inside "
            "the D22-invariant coordinate space.",
            "",
            "## Acceptance gates",
            "",
            "- Exact nonnegativity of all live multipliers; forced multipliers "
            "expand as exact zeros.",
            "- Exact Hq=0 and exact satisfaction of the 388 retained rows.",
            "- Direct exact replay of all 448 original affine rows.",
            "- Exact blockwise factorization Q=B Q[C,C] B^T and exact PSD of "
            "every quotient principal matrix.",
            "- Expansion to Fraction-valued D22 copies and "
            "round7/Q4_verify.verify with n=11, d=2, c=25.",
            "- A separate independent exact replay that rebuilds Gamma_11, the "
            "56 cuts, monomials, coefficient identity, and PSD checks.",
            "",
            "A failed denominator attempt is not evidence against the "
            "certificate ansatz. Increase the denominator. If the exactly "
            "repaired binary-float center itself is not inside the relative "
            "interior, obtain a more accurate positive numerical point.",
            "",
            "## Scope",
            "",
            "This is a build-only repair map and acceptance protocol. No SDP "
            "was run and no theorem is claimed.",
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

    payload, summary = build_repair_map()
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
    print("SPARSE_EXACT_REPAIR_MAP_PASS: no solver run and no theorem claim")


if __name__ == "__main__":
    main()
