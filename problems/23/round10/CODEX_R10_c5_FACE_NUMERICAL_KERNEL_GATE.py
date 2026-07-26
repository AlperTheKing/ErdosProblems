"""Independent ordering and residual gate for the numerical-only QR basis.

This file does not import the producer and makes no exact claim from float64
data.  Exact kernel completeness belongs to the separately sealed exact-Z
archive and its modular gate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
EXACT_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
LOG_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_GATE.log"

EXPECTED_SHA256 = {
    "data": "CBD479AF7071FC95ABF02AB2193738C75359E39672F1421E0C7D1B2FCFB199D3",
    "source": "4347BC891DBBF48A55CFA8FCD4FD40D9FBA4C93E6F55EB9E1AACE32177616043",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "equality": "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F",
    "exact": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


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


def unpack_float_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.float64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=np.float64,
    )


def main() -> None:
    observed_hashes = {
        "data": sha256(DATA_PATH),
        "source": sha256(SOURCE_PATH),
        "blowup": sha256(BLOWUP_PATH),
        "equality": sha256(EQUALITY_PATH),
        "exact": sha256(EXACT_PATH),
    }
    assert observed_hashes == EXPECTED_SHA256, observed_hashes

    data = np.load(DATA_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    exact = np.load(EXACT_PATH, allow_pickle=False)
    assert data["format_version"].tolist() == [1]
    assert data["role"].tolist() == [
        "numerical-only direct-H QR; never an exact certificate"
    ]
    assert data["blowup_data_sha256"].tolist() == [
        EXPECTED_SHA256["blowup"]
    ]
    assert data["equality_data_sha256"].tolist() == [
        EXPECTED_SHA256["equality"]
    ]
    assert data["exact_data_sha256"].tolist() == [
        EXPECTED_SHA256["exact"]
    ]

    h = unpack_integer_csr(blowup, "gram_face").astype(np.float64)
    g = unpack_float_csr(data, "numerical_basis")
    assert h.shape == (6129, 8647)
    assert g.shape == (8647, 2518)
    assert g.nnz == 2_925_200
    assert g.has_sorted_indices
    assert np.all(np.isfinite(g.data))

    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    face_ranks = equality["gram_constraint_ranks"].astype(np.int64)
    face_dimensions = equality["gram_face_dimensions"].astype(np.int64)
    face_offsets = exact["face_column_offsets"].astype(np.int64)
    assert np.array_equal(data["gram_offsets"], q_offsets)
    assert np.array_equal(data["gram_qdims"], q_dimensions)
    assert np.array_equal(data["gram_constraint_ranks"], face_ranks)
    assert np.array_equal(data["gram_face_dimensions"], face_dimensions)
    assert np.array_equal(data["face_column_offsets"], face_offsets)
    assert int(face_ranks.sum()) == h.shape[0]
    assert int(face_dimensions.sum()) == g.shape[1]
    assert np.all(q_dimensions - face_ranks == face_dimensions)

    # Every stored nonzero must remain inside its declared row/column block.
    q_ends = q_offsets + q_dimensions
    face_ends = face_offsets + face_dimensions
    coo = g.tocoo()
    row_blocks = np.searchsorted(q_ends, coo.row, side="right")
    column_blocks = np.searchsorted(face_ends, coo.col, side="right")
    assert np.array_equal(row_blocks, column_blocks)

    global_residual = float(np.max(np.abs(h @ g)))
    gram_error = g.T @ g - sp.eye(g.shape[1], format="csr")
    global_orthogonality = (
        float(np.max(np.abs(gram_error.data))) if gram_error.nnz else 0.0
    )
    assert global_residual < 1e-12
    assert global_orthogonality < 1e-12

    h_row_offset = 0
    maximum_block_residual = 0.0
    maximum_block_orthogonality = 0.0
    blocks: list[dict[str, object]] = []
    for block in range(52):
        q0 = int(q_offsets[block])
        q1 = q0 + int(q_dimensions[block])
        f0 = int(face_offsets[block])
        f1 = f0 + int(face_dimensions[block])
        r0 = h_row_offset
        r1 = r0 + int(face_ranks[block])
        gb = g[q0:q1, f0:f1].toarray()
        hb = h[r0:r1, q0:q1]
        residual = (
            float(np.max(np.abs(hb @ gb)))
            if gb.shape[1] and hb.shape[0]
            else 0.0
        )
        orthogonality = (
            float(
                np.max(
                    np.abs(gb.T @ gb - np.eye(int(face_dimensions[block])))
                )
            )
            if gb.shape[1]
            else 0.0
        )
        assert residual < 1e-12
        assert orthogonality < 1e-12
        maximum_block_residual = max(maximum_block_residual, residual)
        maximum_block_orthogonality = max(
            maximum_block_orthogonality, orthogonality
        )
        blocks.append(
            {
                "block": block,
                "shape": list(gb.shape),
                "H_residual_inf": residual,
                "orthogonality_inf": orthogonality,
            }
        )
        h_row_offset = r1
    assert h_row_offset == h.shape[0]

    output = {
        "status": "PASS",
        "role": "numerical-only; exact claims forbidden",
        "scope": "ordering/residual/orthogonality gate; no SDP built or solved",
        "hashes": observed_hashes,
        "shape": list(g.shape),
        "nnz": int(g.nnz),
        "csr_bytes": int(
            g.data.nbytes + g.indices.nbytes + g.indptr.nbytes
        ),
        "H_residual_inf": global_residual,
        "orthogonality_inf": global_orthogonality,
        "maximum_block_H_residual_inf": maximum_block_residual,
        "maximum_block_orthogonality_inf": maximum_block_orthogonality,
        "block_ordering": "PASS",
        "blocks": blocks,
    }
    LOG_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(output, indent=2, sort_keys=True))
    print("NUMERICAL_KERNEL_GATE_PASS: numerical-only, no SDP run")
    print(f"LOG={LOG_PATH}")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")


if __name__ == "__main__":
    main()
