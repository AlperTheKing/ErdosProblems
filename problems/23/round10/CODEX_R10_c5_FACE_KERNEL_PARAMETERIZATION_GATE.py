"""Independent gate for the sealed exact plateau-face kernel basis.

This gate does not import the producer.  It checks the pinned archive and
inputs, the block ordering, exact integer annihilation H*Z=0, and full kernel
dimension at a fresh prime.  The embedded float64 QR data are diagnosed
separately and are never used to establish any exact claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION.py"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
LOG_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_GATE.log"

EXPECTED_SHA256 = {
    "data": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "source": "1793A01A3358E75226C424128616E1C84D543314601A8500E2273BBDA63C7409",
    "equality": "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
}
FRESH_PRIME = 1_000_033
EXPECTED_SHAPE = (8647, 2518)
EXPECTED_H_SHAPE = (6129, 8647)
EXPECTED_NNZ = 347_912


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


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


def modular_row_rank(matrix: sp.csr_matrix, prime: int) -> int:
    """Sparse exact row elimination over F_prime."""
    pivots: dict[int, dict[int, int]] = {}
    matrix = matrix.tocsr()
    for row_index in range(matrix.shape[0]):
        start = int(matrix.indptr[row_index])
        stop = int(matrix.indptr[row_index + 1])
        row = {
            int(column): int(value) % prime
            for column, value in zip(
                matrix.indices[start:stop], matrix.data[start:stop]
            )
            if int(value) % prime
        }
        while row:
            pivot = min(row)
            base = pivots.get(pivot)
            if base is None:
                inverse = pow(row[pivot], prime - 2, prime)
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
    observed_hashes = {
        "data": sha256(DATA_PATH),
        "source": sha256(SOURCE_PATH),
        "equality": sha256(EQUALITY_PATH),
        "blowup": sha256(BLOWUP_PATH),
    }
    assert observed_hashes == EXPECTED_SHA256, observed_hashes

    data = np.load(DATA_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    assert data["format_version"].tolist() == [1]
    assert data["row_source_sha256"].tolist() == [
        "4B281944B064A143CE035250D7226088662299ED8CDF5998A0263AEDCA76142A"
    ]
    assert data["equality_data_sha256"].tolist() == [
        EXPECTED_SHA256["equality"]
    ]
    assert data["blowup_data_sha256"].tolist() == [
        EXPECTED_SHA256["blowup"]
    ]

    z = unpack_csr(data, "exact_basis")
    h = unpack_csr(blowup, "gram_face")
    assert z.shape == EXPECTED_SHAPE
    assert h.shape == EXPECTED_H_SHAPE
    assert z.nnz == EXPECTED_NNZ
    assert z.has_sorted_indices and h.has_sorted_indices
    assert not np.any(z.data == 0)

    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    face_dimensions = equality["gram_face_dimensions"].astype(np.int64)
    face_ranks = equality["gram_constraint_ranks"].astype(np.int64)
    face_offsets = data["face_column_offsets"].astype(np.int64)
    metadata = data["selected_direction_metadata"].astype(np.int64)
    assert len(q_offsets) == len(q_dimensions) == len(face_dimensions) == 52
    assert np.array_equal(data["gram_offsets"], blowup["gram_offsets"])
    assert np.array_equal(data["gram_qdims"], blowup["gram_qdims"])
    assert np.array_equal(data["gram_face_dimensions"], face_dimensions)
    assert face_offsets[0] == 0
    assert np.array_equal(
        face_offsets,
        np.concatenate(([0], np.cumsum(face_dimensions)[:-1])),
    )
    assert int(face_dimensions.sum()) == EXPECTED_SHAPE[1]
    assert int(face_ranks.sum()) == EXPECTED_H_SHAPE[0]
    assert metadata.shape == (EXPECTED_SHAPE[1], 5)

    # The sparse matrix must be block diagonal in the declared Gram ordering.
    q_ends = q_offsets + q_dimensions
    face_ends = face_offsets + face_dimensions
    coo = z.tocoo()
    row_blocks = np.searchsorted(q_ends, coo.row, side="right")
    column_blocks = np.searchsorted(face_ends, coo.col, side="right")
    assert np.array_equal(row_blocks, column_blocks)
    assert np.all(metadata[:, 0] == np.repeat(np.arange(52), face_dimensions))
    assert np.all(metadata[:, 1:3] >= 0)
    assert np.all(metadata[:, 3:] > 0)

    # This bound makes the int64 sparse product an exact integer calculation.
    h_row_l1 = np.asarray(abs(h).sum(axis=1)).reshape(-1)
    multiplication_bound = int(h_row_l1.max()) * int(np.abs(z.data).max())
    assert multiplication_bound < np.iinfo(np.int64).max
    hz = h @ z
    hz.eliminate_zeros()
    assert hz.nnz == 0

    h_rank_total = 0
    z_rank_total = 0
    h_row_offset = 0
    block_stats: list[dict[str, int]] = []
    for block in range(52):
        q0 = int(q_offsets[block])
        q1 = int(q_ends[block])
        f0 = int(face_offsets[block])
        f1 = int(face_ends[block])
        r0 = h_row_offset
        r1 = r0 + int(face_ranks[block])
        hb = h[r0:r1, q0:q1].tocsr()
        zb = z[q0:q1, f0:f1].tocsr()
        h_rank = modular_row_rank(hb, FRESH_PRIME)
        z_rank = modular_row_rank(zb.T.tocsr(), FRESH_PRIME)
        assert h_rank == int(face_ranks[block])
        assert z_rank == int(face_dimensions[block])
        assert int(q_dimensions[block]) - h_rank == z_rank
        h_rank_total += h_rank
        z_rank_total += z_rank
        h_row_offset = r1
        block_stats.append(
            {
                "block": block,
                "qdim": int(q_dimensions[block]),
                "rank_H": h_rank,
                "rank_Z": z_rank,
            }
        )
    assert h_row_offset == h.shape[0]
    assert h_rank_total == 6129
    assert z_rank_total == 2518

    # Diagnose, but do not use, the embedded QR data.
    solver_values = data["solver_basis_data"].astype(np.float64)
    solver_offsets = data["solver_basis_offsets"].astype(np.int64)
    assert solver_offsets.shape == (53,)
    assert solver_offsets[0] == 0
    assert solver_offsets[-1] == solver_values.size
    maximum_orthogonality = 0.0
    maximum_h_residual = 0.0
    h_row_offset = 0
    for block in range(52):
        qdim = int(q_dimensions[block])
        fdim = int(face_dimensions[block])
        size = qdim * fdim
        start = int(solver_offsets[block])
        stop = int(solver_offsets[block + 1])
        assert stop - start == size
        r0 = h_row_offset
        r1 = r0 + int(face_ranks[block])
        if fdim:
            qb = solver_values[start:stop].reshape(qdim, fdim)
            orth = float(np.max(np.abs(qb.T @ qb - np.eye(fdim))))
            residual = (
                float(np.max(np.abs(h[r0:r1, int(q_offsets[block]):int(q_ends[block])].astype(float) @ qb)))
                if r1 > r0
                else 0.0
            )
            maximum_orthogonality = max(maximum_orthogonality, orth)
            maximum_h_residual = max(maximum_h_residual, residual)
        h_row_offset = r1
    embedded_qr_solver_safe = maximum_h_residual <= 1e-8
    assert maximum_orthogonality < 1e-12
    assert not embedded_qr_solver_safe

    output = {
        "status": "PASS",
        "scope": "exact Z only; no SDP built or solved",
        "hashes": observed_hashes,
        "shape": list(z.shape),
        "nnz": int(z.nnz),
        "coefficient_min": int(z.data.min()),
        "coefficient_max": int(z.data.max()),
        "maximum_coefficient_bits": int(np.abs(z.data).max()).bit_length(),
        "exact_HZ_nnz": int(hz.nnz),
        "int64_product_bound": multiplication_bound,
        "fresh_prime": FRESH_PRIME,
        "rank_H": h_rank_total,
        "rank_Z": z_rank_total,
        "kernel_dimension": z_rank_total,
        "block_stats": block_stats,
        "embedded_qr": {
            "maximum_orthogonality_inf": maximum_orthogonality,
            "maximum_H_residual_inf": maximum_h_residual,
            "solver_safe_at_1e-8": embedded_qr_solver_safe,
            "role": "diagnostic only; excluded from exact gate",
        },
    }
    LOG_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(output, indent=2, sort_keys=True))
    print("EXACT_KERNEL_PARAMETERIZATION_GATE_PASS")
    print(f"LOG={LOG_PATH}")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")


if __name__ == "__main__":
    main()
