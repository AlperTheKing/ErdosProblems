"""Exact reconstruction maps on the induced-C5 equality face.

Input
-----
CODEX_R10_c5_FACE_data.npz, containing the exact integer face system

    H q = 0,
    A_norm nu = b_norm,
    A_nu nu + A_gram q = b_target.

Output
------
CODEX_R10_c5_FACE_RECON_data.npz, containing exact rational sparse maps

    q = P z                                      (8647 x 7176),
    A_face [nu_live; z] = b                      (448 x 8640),
    delta[pivot_columns] = R (b - A_face w)      (448 x 448).

Here R is the exact inverse of the 448x448 pivot-column submatrix of A_face.
Thus ``repair_equalities`` turns any rational trial vector into one satisfying
all 56 normalization and 392 target equations exactly.  Cone preservation is
not automatic: an incoming numerical face point must have enough multiplier
and PSD margin before the correction can be accepted.

No SDP is built or solved.  The final certificate gate remains expansion to
Fractions followed by Q4_verify and an independent replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
FACE_DATA = HERE / "CODEX_R10_c5_FACE_data.npz"
DEFAULT_OUTPUT = HERE / "CODEX_R10_c5_FACE_RECON_data.npz"
DEFAULT_SUMMARY = HERE / "CODEX_R10_c5_FACE_RECON_summary.json"


RationalRow = dict[int, Fraction]


@dataclass
class RationalCSR:
    shape: tuple[int, int]
    indptr: np.ndarray
    indices: np.ndarray
    values: list[Fraction]

    def rows(self) -> list[RationalRow]:
        output: list[RationalRow] = []
        for row_index in range(self.shape[0]):
            start = int(self.indptr[row_index])
            stop = int(self.indptr[row_index + 1])
            output.append(
                {
                    int(column): value
                    for column, value in zip(
                        self.indices[start:stop], self.values[start:stop]
                    )
                    if value
                }
            )
        return output

    def matvec(self, vector: Iterable[Fraction]) -> list[Fraction]:
        values = list(vector)
        if len(values) != self.shape[1]:
            raise ValueError("vector length does not match rational matrix")
        output = []
        for row_index in range(self.shape[0]):
            total = Fraction(0)
            start = int(self.indptr[row_index])
            stop = int(self.indptr[row_index + 1])
            for column, value in zip(
                self.indices[start:stop], self.values[start:stop]
            ):
                total += value * values[int(column)]
            output.append(total)
        return output

    def to_float_csr(self) -> sp.csr_matrix:
        return sp.csr_matrix(
            (
                np.asarray([float(value) for value in self.values]),
                self.indices.astype(np.int32),
                self.indptr.astype(np.int64),
            ),
            shape=self.shape,
        )


def unpack_integer_csr(data, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            data[f"{name}_data"].astype(np.int64),
            data[f"{name}_indices"].astype(np.int32),
            data[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in data[f"{name}_shape"]),
        dtype=np.int64,
    )


def rational_rows_from_integer_csr(matrix: sp.csr_matrix) -> list[RationalRow]:
    output = []
    for row_index in range(matrix.shape[0]):
        start = int(matrix.indptr[row_index])
        stop = int(matrix.indptr[row_index + 1])
        output.append(
            {
                int(column): Fraction(int(value))
                for column, value in zip(
                    matrix.indices[start:stop], matrix.data[start:stop]
                )
                if value
            }
        )
    return output


def subtract_multiple(
    target: RationalRow, source: RationalRow, factor: Fraction
) -> None:
    if not factor:
        return
    for column, value in source.items():
        updated = target.get(column, Fraction(0)) - factor * value
        if updated:
            target[column] = updated
        else:
            target.pop(column, None)


def exact_sparse_rref(
    source_rows: list[RationalRow],
    track_transform: bool = False,
) -> tuple[list[RationalRow], list[int], list[RationalRow] | None]:
    """Exact sparse RREF; returns nonzero rows, pivot columns, and row transform."""
    rows: list[RationalRow] = []
    pivots: list[int] = []
    transforms: list[RationalRow] | None = [] if track_transform else None

    for source_index, source in enumerate(source_rows):
        row = dict(source)
        transform = {source_index: Fraction(1)} if track_transform else None
        for base_index, (base, pivot) in enumerate(zip(rows, pivots)):
            factor = row.get(pivot, Fraction(0))
            if factor:
                subtract_multiple(row, base, factor)
                if transform is not None and transforms is not None:
                    subtract_multiple(transform, transforms[base_index], factor)
        if not row:
            continue
        pivot = min(row)
        scale = row[pivot]
        row = {
            column: value / scale
            for column, value in row.items()
            if value / scale
        }
        if transform is not None:
            transform = {
                column: value / scale
                for column, value in transform.items()
                if value / scale
            }
        rows.append(row)
        pivots.append(pivot)
        if transforms is not None and transform is not None:
            transforms.append(transform)

    for later in range(len(rows) - 1, -1, -1):
        pivot = pivots[later]
        for earlier in range(later):
            factor = rows[earlier].get(pivot, Fraction(0))
            if factor:
                subtract_multiple(rows[earlier], rows[later], factor)
                if transforms is not None:
                    subtract_multiple(
                        transforms[earlier], transforms[later], factor
                    )

    for row_index, pivot in enumerate(pivots):
        assert rows[row_index].get(pivot) == 1
        assert all(
            rows[other].get(pivot, Fraction(0)) == 0
            for other in range(len(rows))
            if other != row_index
        )
    return rows, pivots, transforms


def rational_csr_from_rows(
    rows: list[RationalRow], number_columns: int
) -> RationalCSR:
    indptr = [0]
    indices: list[int] = []
    values: list[Fraction] = []
    for row in rows:
        for column, value in sorted(row.items()):
            if value:
                indices.append(column)
                values.append(value)
        indptr.append(len(indices))
    return RationalCSR(
        shape=(len(rows), number_columns),
        indptr=np.asarray(indptr, dtype=np.int64),
        indices=np.asarray(indices, dtype=np.int32),
        values=values,
    )


def pack_rational_csr(
    payload: dict[str, np.ndarray], name: str, matrix: RationalCSR
) -> dict[str, int | str]:
    numerators = [value.numerator for value in matrix.values]
    denominators = [value.denominator for value in matrix.values]
    maximum_numerator_bits = max(
        (abs(value).bit_length() for value in numerators), default=0
    )
    maximum_denominator_bits = max(
        (value.bit_length() for value in denominators), default=0
    )
    fits_int64 = max(maximum_numerator_bits, maximum_denominator_bits) <= 62
    if fits_int64:
        payload[f"{name}_numerators"] = np.asarray(
            numerators, dtype=np.int64
        )
        payload[f"{name}_denominators"] = np.asarray(
            denominators, dtype=np.int64
        )
        storage = "int64"
    else:
        payload[f"{name}_numerators"] = np.asarray(
            [str(value) for value in numerators]
        )
        payload[f"{name}_denominators"] = np.asarray(
            [str(value) for value in denominators]
        )
        storage = "decimal-string"
    payload[f"{name}_indptr"] = matrix.indptr.astype(np.int64)
    payload[f"{name}_indices"] = matrix.indices.astype(np.int32)
    payload[f"{name}_shape"] = np.asarray(matrix.shape, dtype=np.int64)
    payload[f"{name}_storage"] = np.asarray([storage])
    return {
        "shape": list(matrix.shape),
        "nnz": len(matrix.values),
        "storage": storage,
        "max_numerator_bits": maximum_numerator_bits,
        "max_denominator_bits": maximum_denominator_bits,
    }


def load_rational_csr(data, name: str) -> RationalCSR:
    numerators = data[f"{name}_numerators"]
    denominators = data[f"{name}_denominators"]
    values = [
        Fraction(int(numerator), int(denominator))
        for numerator, denominator in zip(numerators, denominators)
    ]
    return RationalCSR(
        shape=tuple(int(value) for value in data[f"{name}_shape"]),
        indptr=data[f"{name}_indptr"].astype(np.int64),
        indices=data[f"{name}_indices"].astype(np.int32),
        values=values,
    )


def gram_parameterization(
    face_matrix: sp.csr_matrix,
    offsets: np.ndarray,
    dimensions: np.ndarray,
    ranks: np.ndarray,
) -> tuple[list[RationalRow], list[int], list[int], list[int]]:
    """Return q=Pz rows and per-block pivot/free global q columns."""
    parameter_rows: list[RationalRow] = [
        {} for _ in range(face_matrix.shape[1])
    ]
    all_pivots: list[int] = []
    all_free: list[int] = []
    block_free_offsets: list[int] = []
    face_row_offset = 0
    z_offset = 0

    for block_index, (q_offset, q_dimension, rank) in enumerate(
        zip(offsets, dimensions, ranks)
    ):
        q_offset = int(q_offset)
        q_dimension = int(q_dimension)
        rank = int(rank)
        block = face_matrix[
            face_row_offset : face_row_offset + rank,
            q_offset : q_offset + q_dimension,
        ].tocsr()
        rref, pivots, _transform = exact_sparse_rref(
            rational_rows_from_integer_csr(block)
        )
        assert len(pivots) == rank
        pivot_set = set(pivots)
        free = [
            column for column in range(q_dimension) if column not in pivot_set
        ]
        free_local_index = {
            column: index for index, column in enumerate(free)
        }
        block_free_offsets.append(z_offset)

        for column in free:
            parameter_rows[q_offset + column] = {
                z_offset + free_local_index[column]: Fraction(1)
            }
        for row, pivot in zip(rref, pivots):
            assert all(
                column in pivot_set or column in free_local_index
                for column in row
            )
            parameter_rows[q_offset + pivot] = {
                z_offset + free_local_index[column]: -value
                for column, value in row.items()
                if column in free_local_index and value
            }

        all_pivots.extend(q_offset + column for column in pivots)
        all_free.extend(q_offset + column for column in free)
        z_offset += len(free)
        face_row_offset += rank

    assert face_row_offset == face_matrix.shape[0]
    assert z_offset == face_matrix.shape[1] - face_matrix.shape[0] == 7176
    return parameter_rows, all_pivots, all_free, block_free_offsets


def multiply_integer_by_rational_rows(
    left: sp.csr_matrix,
    right_rows: list[RationalRow],
    right_columns: int,
) -> list[RationalRow]:
    assert left.shape[1] == len(right_rows)
    output: list[RationalRow] = []
    for row_index in range(left.shape[0]):
        accumulator: RationalRow = {}
        start = int(left.indptr[row_index])
        stop = int(left.indptr[row_index + 1])
        for middle, coefficient in zip(
            left.indices[start:stop], left.data[start:stop]
        ):
            coefficient = Fraction(int(coefficient))
            for column, value in right_rows[int(middle)].items():
                updated = (
                    accumulator.get(column, Fraction(0))
                    + coefficient * value
                )
                if updated:
                    accumulator[column] = updated
                else:
                    accumulator.pop(column, None)
        assert all(0 <= column < right_columns for column in accumulator)
        output.append(accumulator)
    return output


def build_reconstruction(
    face_path: Path,
) -> tuple[dict[str, np.ndarray], dict[str, object]]:
    face = np.load(face_path, allow_pickle=False)
    normalization = unpack_integer_csr(face, "normalization_live")
    target_nu = unpack_integer_csr(face, "target_nu_live")
    target_gram = unpack_integer_csr(face, "target_gram")
    gram_face = unpack_integer_csr(face, "gram_face")
    offsets = face["gram_offsets"].astype(np.int32)
    qdims = face["gram_qdims"].astype(np.int32)
    ranks = face["gram_constraint_ranks"].astype(np.int32)

    parameter_rows, gram_pivots, gram_free, block_free_offsets = (
        gram_parameterization(gram_face, offsets, qdims, ranks)
    )
    gram_parameter = rational_csr_from_rows(parameter_rows, len(gram_free))

    # Verify H P = 0 exactly without floating point.
    hp_rows = multiply_integer_by_rational_rows(
        gram_face, parameter_rows, len(gram_free)
    )
    assert all(not row for row in hp_rows)

    gram_target_face_rows = multiply_integer_by_rational_rows(
        target_gram, parameter_rows, len(gram_free)
    )
    nu_count = normalization.shape[1]
    face_gram_count = len(gram_free)
    total_variables = nu_count + face_gram_count

    certificate_rows: list[RationalRow] = []
    for row_index in range(normalization.shape[0]):
        start = int(normalization.indptr[row_index])
        stop = int(normalization.indptr[row_index + 1])
        certificate_rows.append(
            {
                int(column): Fraction(int(value))
                for column, value in zip(
                    normalization.indices[start:stop],
                    normalization.data[start:stop],
                )
                if value
            }
        )
    for row_index, gram_row in enumerate(gram_target_face_rows):
        start = int(target_nu.indptr[row_index])
        stop = int(target_nu.indptr[row_index + 1])
        row = {
            int(column): Fraction(int(value))
            for column, value in zip(
                target_nu.indices[start:stop], target_nu.data[start:stop]
            )
            if value
        }
        for column, value in gram_row.items():
            assert nu_count + column not in row
            row[nu_count + column] = value
        certificate_rows.append(row)

    certificate_map = rational_csr_from_rows(
        certificate_rows, total_variables
    )
    rref, certificate_pivots, repair_rows = exact_sparse_rref(
        certificate_rows, track_transform=True
    )
    assert repair_rows is not None
    certificate_rank = len(rref)
    if certificate_rank != len(certificate_rows) or len(certificate_rows) != 448:
        raise AssertionError(
            f"certificate map rank={certificate_rank}, rows={len(certificate_rows)}"
        )
    assert len(certificate_pivots) == 448

    # E*A has identity in pivot columns, so E is the inverse pivot repair map.
    for row_index, pivot in enumerate(certificate_pivots):
        assert rref[row_index].get(pivot) == 1
        assert all(
            rref[other].get(pivot, Fraction(0)) == 0
            for other in range(len(rref))
            if other != row_index
        )
    repair_map = rational_csr_from_rows(repair_rows, len(certificate_rows))

    rhs = np.concatenate(
        [face["normalization_rhs"], face["target_rhs"]]
    ).astype(np.int64)
    repaired_zero = [Fraction(0)] * total_variables
    correction = repair_map.matvec(Fraction(int(value)) for value in rhs)
    for value_index, pivot in enumerate(certificate_pivots):
        repaired_zero[pivot] += correction[value_index]
    assert certificate_map.matvec(repaired_zero) == [
        Fraction(int(value)) for value in rhs
    ]

    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "source_face_sha256": np.asarray([sha256(face_path)]),
        "live_multiplier_orbits": face["live_multiplier_orbits"].astype(
            np.int32
        ),
        "gram_face_pivot_columns": np.asarray(
            gram_pivots, dtype=np.int32
        ),
        "gram_face_free_columns": np.asarray(gram_free, dtype=np.int32),
        "gram_block_free_offsets": np.asarray(
            block_free_offsets, dtype=np.int32
        ),
        "certificate_rhs": rhs,
        "certificate_pivot_columns": np.asarray(
            certificate_pivots, dtype=np.int32
        ),
        "face_variable_counts": np.asarray(
            [nu_count, face_gram_count, total_variables], dtype=np.int32
        ),
    }
    matrix_metadata = {
        "gram_parameter": pack_rational_csr(
            payload, "gram_parameter", gram_parameter
        ),
        "certificate_map": pack_rational_csr(
            payload, "certificate_map", certificate_map
        ),
        "repair_map": pack_rational_csr(
            payload, "repair_map", repair_map
        ),
    }
    summary: dict[str, object] = {
        "source_face_sha256": sha256(face_path),
        "gram_original_variables": gram_face.shape[1],
        "gram_face_equation_rank": gram_face.shape[0],
        "gram_face_coordinates": len(gram_free),
        "live_multiplier_variables": nu_count,
        "total_face_variables": total_variables,
        "normalization_rows": normalization.shape[0],
        "target_rows": target_nu.shape[0],
        "certificate_rows": len(certificate_rows),
        "certificate_exact_rank": certificate_rank,
        "certificate_pivot_columns": certificate_pivots,
        "certificate_pivot_multiplier_count": sum(
            pivot < nu_count for pivot in certificate_pivots
        ),
        "certificate_pivot_gram_count": sum(
            pivot >= nu_count for pivot in certificate_pivots
        ),
        "matrix_metadata": matrix_metadata,
        "exact_checks": [
            "H*P=0",
            "rank(P)=7176 by identity rows at gram_face_free_columns",
            "rank(A_face)=448 by exact rational RREF",
            "repair_map=A_face[:,pivot_columns]^-1",
            "A_face*repair(rhs)=rhs",
        ],
        "warning": (
            "Equality repair alone does not prove multiplier nonnegativity or "
            "PSD; exact cone checks and Q4_verify remain mandatory."
        ),
    }
    return payload, summary


def expand_face_gram(reconstruction_data, z: Iterable[Fraction]) -> list[Fraction]:
    return load_rational_csr(
        reconstruction_data, "gram_parameter"
    ).matvec(z)


def compress_face_gram(reconstruction_data, q: Iterable[Fraction]) -> list[Fraction]:
    q_values = list(q)
    free = reconstruction_data["gram_face_free_columns"]
    if len(q_values) != 8647:
        raise ValueError("expected 8647 full Gram orbit scalars")
    return [q_values[int(column)] for column in free]


def repair_equalities(
    reconstruction_data, trial: Iterable[Fraction]
) -> list[Fraction]:
    trial_values = list(trial)
    certificate_map = load_rational_csr(
        reconstruction_data, "certificate_map"
    )
    repair_map = load_rational_csr(reconstruction_data, "repair_map")
    if len(trial_values) != certificate_map.shape[1]:
        raise ValueError("trial vector has the wrong face dimension")
    rhs = [
        Fraction(int(value))
        for value in reconstruction_data["certificate_rhs"]
    ]
    current = certificate_map.matvec(trial_values)
    residual = [
        target - value for target, value in zip(rhs, current)
    ]
    correction = repair_map.matvec(residual)
    output = list(trial_values)
    for value, pivot in zip(
        correction, reconstruction_data["certificate_pivot_columns"]
    ):
        output[int(pivot)] += value
    assert certificate_map.matvec(output) == rhs
    return output


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                return digest.hexdigest().upper()
            digest.update(block)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--face", type=Path, default=FACE_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    payload, summary = build_reconstruction(args.face)
    np.savez_compressed(args.output, **payload)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"OUTPUT={args.output.resolve()}")
    print(f"SUMMARY={args.summary.resolve()}")
    print(f"SHA256_SCRIPT={sha256(Path(__file__))}")
    print(f"SHA256_OUTPUT={sha256(args.output)}")
    print(f"SHA256_SUMMARY={sha256(args.summary)}")
    print("EXACT_RECON_MAP_ONLY: no SDP run and no theorem claim")


if __name__ == "__main__":
    main()
