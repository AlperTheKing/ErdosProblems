"""Build a stable numerical-only parameterization of the plateau Gram face.

The exact certificate basis is stored separately.  This program computes an
orthonormal float64 basis of each declared block kernel directly from H^T by
full Householder QR.  Its only role is numerical steering/canonicalization;
it is not evidence for an exact identity or theorem.

No optimization problem is solved.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import scipy.linalg as la
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
EXACT_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
OUTPUT_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
SUMMARY_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_summary.json"
REPORT_PATH = HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_REPORT.md"

EXPECTED_SHA256 = {
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


def build() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    observed_hashes = {
        "blowup": sha256(BLOWUP_PATH),
        "equality": sha256(EQUALITY_PATH),
        "exact": sha256(EXACT_PATH),
    }
    if observed_hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input hash mismatch: {observed_hashes}")

    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    exact = np.load(EXACT_PATH, allow_pickle=False)
    h = unpack_csr(blowup, "gram_face").astype(np.float64)
    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    face_ranks = equality["gram_constraint_ranks"].astype(np.int64)
    face_dimensions = equality["gram_face_dimensions"].astype(np.int64)
    face_offsets = exact["face_column_offsets"].astype(np.int64)
    if h.shape != (6129, 8647):
        raise AssertionError(f"unexpected H shape {h.shape}")
    if int(face_dimensions.sum()) != 2518:
        raise AssertionError("unexpected total face dimension")

    blocks: list[sp.csr_matrix] = []
    block_summary: list[dict[str, object]] = []
    h_row_offset = 0
    started = time.perf_counter()
    for block in range(52):
        q0 = int(q_offsets[block])
        qdim = int(q_dimensions[block])
        rank = int(face_ranks[block])
        nullity = int(face_dimensions[block])
        r0 = h_row_offset
        r1 = r0 + rank
        hb = h[r0:r1, q0 : q0 + qdim].tocsr()
        block_started = time.perf_counter()
        if rank == 0:
            gb = np.eye(qdim, dtype=np.float64)
            minimum_r_diagonal = None
            maximum_r_diagonal = None
        elif nullity == 0:
            gb = np.zeros((qdim, 0), dtype=np.float64)
            minimum_r_diagonal = None
            maximum_r_diagonal = None
        else:
            dense_transpose = hb.toarray().T
            q_full, r_full = la.qr(
                dense_transpose,
                mode="full",
                overwrite_a=True,
                check_finite=False,
            )
            diagonal = np.abs(np.diag(r_full[:rank, :rank]))
            gb = q_full[:, rank:]
            minimum_r_diagonal = float(diagonal.min())
            maximum_r_diagonal = float(diagonal.max())
        if gb.shape != (qdim, nullity):
            raise AssertionError(
                f"block {block}: got {gb.shape}, expected {(qdim, nullity)}"
            )
        residual = (
            float(np.max(np.abs(hb @ gb))) if rank and nullity else 0.0
        )
        orthogonality = (
            float(np.max(np.abs(gb.T @ gb - np.eye(nullity))))
            if nullity
            else 0.0
        )
        if residual > 1e-12 or orthogonality > 1e-12:
            raise AssertionError(
                f"block {block}: residual={residual}, orth={orthogonality}"
            )
        blocks.append(sp.csr_matrix(gb))
        block_summary.append(
            {
                "block": block,
                "qdim": qdim,
                "rank_H": rank,
                "nullity": nullity,
                "nnz": int(np.count_nonzero(gb)),
                "H_residual_inf": residual,
                "orthogonality_inf": orthogonality,
                "minimum_R_diagonal": minimum_r_diagonal,
                "maximum_R_diagonal": maximum_r_diagonal,
                "seconds": time.perf_counter() - block_started,
            }
        )
        h_row_offset = r1
    if h_row_offset != h.shape[0]:
        raise AssertionError("H row offsets do not close")

    g = sp.block_diag(blocks, format="csr")
    if g.shape != (8647, 2518):
        raise AssertionError(f"unexpected G shape {g.shape}")
    global_residual = float(np.max(np.abs(h @ g)))
    gram_error = g.T @ g - sp.eye(g.shape[1], format="csr")
    global_orthogonality = (
        float(np.max(np.abs(gram_error.data))) if gram_error.nnz else 0.0
    )
    if global_residual > 1e-12 or global_orthogonality > 1e-12:
        raise AssertionError(
            f"global residual={global_residual}, orth={global_orthogonality}"
        )

    payload = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            ["numerical-only direct-H QR; never an exact certificate"]
        ),
        "blowup_data_sha256": np.asarray([observed_hashes["blowup"]]),
        "equality_data_sha256": np.asarray([observed_hashes["equality"]]),
        "exact_data_sha256": np.asarray([observed_hashes["exact"]]),
        "gram_offsets": q_offsets.astype(np.int32),
        "gram_qdims": q_dimensions.astype(np.int32),
        "gram_constraint_ranks": face_ranks.astype(np.int32),
        "gram_face_dimensions": face_dimensions.astype(np.int32),
        "face_column_offsets": face_offsets.astype(np.int32),
        "numerical_basis_data": g.data.astype(np.float64),
        "numerical_basis_indices": g.indices.astype(np.int32),
        "numerical_basis_indptr": g.indptr.astype(np.int64),
        "numerical_basis_shape": np.asarray(g.shape, dtype=np.int64),
    }
    summary = {
        "role": "numerical-only direct-H QR; never an exact certificate",
        "scope": "kernel steering/canonicalization only; no SDP solved",
        "source_sha256": observed_hashes,
        "basis": {
            "shape": list(g.shape),
            "nnz": int(g.nnz),
            "data_bytes": int(g.data.nbytes),
            "csr_bytes": int(
                g.data.nbytes + g.indices.nbytes + g.indptr.nbytes
            ),
            "H_residual_inf": global_residual,
            "orthogonality_inf": global_orthogonality,
        },
        "per_block": block_summary,
        "seconds": time.perf_counter() - started,
    }
    return payload, summary


def write_report(summary: dict[str, object]) -> None:
    basis = summary["basis"]
    lines = [
        "# Stable numerical plateau-face kernel",
        "",
        "This archive is numerical steering data only. It is not an exact",
        "certificate and is never used to establish an exact identity.",
        "",
        f"- shape: `{basis['shape']}`",
        f"- nonzeros: `{basis['nnz']}`",
        f"- CSR memory: `{basis['csr_bytes']}` bytes",
        f"- `||H G||_inf`: `{basis['H_residual_inf']:.16e}`",
        f"- `||G^T G-I||_inf`: `{basis['orthogonality_inf']:.16e}`",
        "",
        "Each block was computed independently by full Householder QR of",
        "`H_block^T`; the trailing columns are the numerical nullspace.",
        "No optimization problem was solved.",
        "",
    ]
    REPORT_PATH.write_text(
        "\n".join(lines), encoding="utf-8", newline="\n"
    )


def main() -> None:
    payload, summary = build()
    np.savez_compressed(OUTPUT_PATH, **payload)
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_report(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"OUTPUT={OUTPUT_PATH}")
    print(f"SUMMARY={SUMMARY_PATH}")
    print(f"REPORT={REPORT_PATH}")
    print(f"SHA256_SCRIPT={sha256(Path(__file__))}")
    print(f"SHA256_OUTPUT={sha256(OUTPUT_PATH)}")
    print(f"SHA256_SUMMARY={sha256(SUMMARY_PATH)}")
    print(f"SHA256_REPORT={sha256(REPORT_PATH)}")
    print("NUMERICAL_KERNEL_BUILD_PASS: no SDP run")


if __name__ == "__main__":
    main()
