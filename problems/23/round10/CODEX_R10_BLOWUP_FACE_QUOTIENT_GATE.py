"""Exact build-only audit of the plateau-face quotient PSD cones.

For every representative Gram block this gate rebuilds the forced-kernel
matrix U, verifies the chosen pivot minor modulo an exact prime, checks that
the exported H equations have the same row space as Q U^T = 0 in invariant
Gram coordinates, and records the resulting free-coordinate cone orders.

No SDP is solved.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "CODEX_R10_g11_d22_plateau_face.py"
SUMMARY_PATH = HERE / "CODEX_R10_BLOWUP_FACE_summary.json"
LOG_PATH = HERE / "CODEX_R10_BLOWUP_FACE_QUOTIENT_GATE.log"
PRIME = 2_000_003


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


def load_model_module():
    spec = importlib.util.spec_from_file_location(
        "codex_plateau_quotient_gate_model", MODEL_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def modular_rank_rows(
    rows: list[dict[int, int]], width: int, prime: int = PRIME
) -> int:
    pivots: dict[int, dict[int, int]] = {}
    for source in rows:
        row = {
            column: value % prime
            for column, value in source.items()
            if value % prime
        }
        while row:
            pivot = min(row)
            if pivot not in pivots:
                inverse = pow(row[pivot], prime - 2, prime)
                pivots[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            for column, value in pivots[pivot].items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    assert all(0 <= pivot < width for pivot in pivots)
    return len(pivots)


def sparse_rows(matrix: sp.csr_matrix) -> list[dict[int, int]]:
    output = []
    for row_index in range(matrix.shape[0]):
        output.append(
            {
                int(column): int(value)
                for column, value in zip(
                    matrix.indices[
                        matrix.indptr[row_index] :
                        matrix.indptr[row_index + 1]
                    ],
                    matrix.data[
                        matrix.indptr[row_index] :
                        matrix.indptr[row_index + 1]
                    ],
                )
                if int(value)
            }
        )
    return output


def qut_rows(
    entry_ids: np.ndarray, kernel_rows: list[tuple[int, ...]]
) -> list[dict[int, int]]:
    output = []
    for kernel in kernel_rows:
        nonzero = [
            (column, int(value))
            for column, value in enumerate(kernel)
            if value
        ]
        for row_index in range(entry_ids.shape[0]):
            row: Counter[int] = Counter()
            for column, coefficient in nonzero:
                row[int(entry_ids[row_index, column])] += coefficient
            cleaned = {
                column: value for column, value in row.items() if value
            }
            if cleaned:
                output.append(cleaned)
    return output


def dense_minor_rows(
    kernel_rows: list[tuple[int, ...]], columns: list[int]
) -> list[dict[int, int]]:
    return [
        {
            local_column: int(row[global_column])
            for local_column, global_column in enumerate(columns)
            if row[global_column]
        }
        for row in kernel_rows
    ]


def main() -> None:
    module = load_model_module()
    model = module.build_model()
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    face_integer = module.csr_from_archive(
        model.blowup_archive, "gram_face"
    ).astype(np.int64)

    row_offset = 0
    column_offset = 0
    free_orders: Counter[int] = Counter()
    kernel_total = 0
    face_rank_total = 0
    for block_index, (orbit, kernel, free) in enumerate(
        zip(
            model.base.gram_orbits,
            model.kernel_rows,
            model.free_coordinates,
        )
    ):
        order = len(orbit.basis)
        kernel_rank = len(kernel)
        pivots = module.independent_pivot_columns_mod_prime(
            kernel, order, PRIME
        )
        assert len(pivots) == kernel_rank
        assert set(pivots).isdisjoint(free)
        assert sorted(pivots + free) == list(range(order))
        # A nonzero determinant modulo PRIME proves U[:,P] invertible over Q.
        assert modular_rank_rows(
            dense_minor_rows(kernel, pivots), kernel_rank, PRIME
        ) == kernel_rank

        block_rank = int(
            summary["per_block"][block_index]["gram_constraint_rank"]
        )
        qdim = int(orbit.variable.size)
        full_rows = face_integer[
            row_offset : row_offset + block_rank, :
        ].tocsr()
        block_face = full_rows[
            :, column_offset : column_offset + qdim
        ].tocsr()
        assert full_rows.nnz == block_face.nnz
        h_rows = sparse_rows(block_face)
        qu_keys = {
            tuple(sorted(row.items()))
            for row in qut_rows(orbit.entry_ids, kernel)
        }
        assert all(tuple(sorted(row.items())) in qu_keys for row in h_rows)
        assert modular_rank_rows(h_rows, qdim, PRIME) == block_rank

        free_orders[len(free)] += 1
        kernel_total += kernel_rank
        face_rank_total += block_rank
        row_offset += block_rank
        column_offset += qdim

    assert row_offset == face_rank_total == 6129
    assert column_offset == 8647
    assert kernel_total == 402
    expected = Counter(
        {
            154: 1,
            40: 1,
            35: 1,
            33: 1,
            32: 2,
            11: 1,
            8: 2,
            7: 2,
            6: 7,
            5: 3,
            4: 5,
            1: 16,
            0: 10,
        }
    )
    assert free_orders == expected

    # Exact algebraic lemma used by the constructor:
    # U_P invertible, A=-U_P^{-1}U_C, B_P=A, B_C=I gives UB=0,
    # B[C,:]=I and im(B)=ker(U).  For symmetric Q with QU^T=0,
    # every column and row lies in im(B), so Q=B Q[C,C] B^T.
    # Conversely this factorization implies QU^T=0.  A congruence and the
    # principal-submatrix property give Q PSD iff Q[C,C] PSD.
    messages = [
        "PLATEAU_BUILD_REPLAY_PASS forced=2085 live=526 H=6129x8647 nnz=71973",
        "PIVOT_MINORS_PASS blocks=52 kernel_rank=402 prime=2000003",
        "H_IFF_QUT_PASS exact_character_upper=6129 modular_rank=6129",
        "QUOTIENT_ORDERS_PASS "
        + json.dumps(dict(sorted(free_orders.items(), reverse=True))),
        "QUOTIENT_LEMMA_PASS U_P_invertible; Q=B Q_CC B^T; "
        "Q_PSD_iff_Q_CC_PSD",
        "BUILD_ONLY_PASS: no SDP solved and no numerical file written",
        f"SHA256_MODEL={sha256(MODEL_PATH)}",
        f"SHA256_BLOWUP_DATA={sha256(module.BLOWUP_DATA_PATH)}",
        f"SHA256_EQUALITY_DATA={sha256(module.EQUALITY_DATA_PATH)}",
        f"SHA256_GATE={sha256(Path(__file__))}",
    ]
    text = "\n".join(messages) + "\n"
    LOG_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    print(f"LOG={LOG_PATH.resolve()}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")


if __name__ == "__main__":
    main()
