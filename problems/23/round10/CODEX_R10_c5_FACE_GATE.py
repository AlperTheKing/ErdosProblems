"""Independent exact gate for CODEX_R10_c5_FACE_data.npz.

The producer is not imported.  This gate compares the artifact with the
existing D22 constructor and the separate exact-face scaffold, verifies all
four exported sparse coefficient maps, checks that every exported Gram-face
row is a genuine C5 kernel equation, and proves its exact rank blockwise.

No optimization problem is solved.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "CODEX_R10_c5_FACE_data.npz"
BUILDER_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
SCAFFOLD_PATH = HERE / "CODEX_R10_g11_d22_face.py"
CHECK_PRIME = 1_000_003


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_csr(data, name: str) -> sp.csr_matrix:
    shape = tuple(int(value) for value in data[f"{name}_shape"])
    return sp.csr_matrix(
        (
            data[f"{name}_data"].astype(np.int64),
            data[f"{name}_indices"].astype(np.int32),
            data[f"{name}_indptr"].astype(np.int64),
        ),
        shape=shape,
        dtype=np.int64,
    )


def sparse_equal(left: sp.spmatrix, right: sp.spmatrix) -> bool:
    left = left.tocsr().astype(np.int64)
    right = right.tocsr().astype(np.int64)
    if left.shape != right.shape:
        return False
    difference = left - right
    difference.eliminate_zeros()
    return difference.nnz == 0


def support_inside(exponent: tuple[int, ...], vertices: set[int]) -> bool:
    return all(
        power == 0 or vertex in vertices
        for vertex, power in enumerate(exponent)
    )


def independently_rebuild_c5s(
    edges: list[tuple[int, int]],
) -> list[tuple[int, ...]]:
    edge_set = set(edges)
    output = []
    for vertices in combinations(range(11), 5):
        induced = [
            edge for edge in edge_set if edge[0] in vertices and edge[1] in vertices
        ]
        if len(induced) != 5:
            continue
        degrees = Counter(vertex for edge in induced for vertex in edge)
        if all(degrees[vertex] == 2 for vertex in vertices):
            output.append(vertices)
    return output


def canonical_equation_rows(
    entry_ids: np.ndarray,
    basis: list[tuple[int, ...]],
    cycles: list[tuple[int, ...]],
) -> set[tuple[tuple[int, int], ...]]:
    output: set[tuple[tuple[int, int], ...]] = set()
    parity_support = {
        vertex for vertex, value in enumerate(basis[0]) if value & 1
    }
    for cycle in cycles:
        vertices = set(cycle)
        if not parity_support <= vertices:
            continue
        nonzero = [
            j
            for j, exponent in enumerate(basis)
            if support_inside(exponent, vertices)
        ]
        for i in range(len(basis)):
            row = Counter(int(entry_ids[i, j]) for j in nonzero)
            if row:
                output.add(tuple(sorted(row.items())))
    return output


def modular_rank(matrix: sp.csr_matrix, prime: int) -> int:
    """Exact lower bound over Q via row elimination in F_prime."""
    pivot_rows: dict[int, dict[int, int]] = {}
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
            if pivot not in pivot_rows:
                inverse = pow(row[pivot], prime - 2, prime)
                normalized = {}
                for column, value in row.items():
                    product = (value * inverse) % prime
                    if product:
                        normalized[column] = product
                pivot_rows[pivot] = normalized
                break
            factor = row[pivot]
            base = pivot_rows[pivot]
            for column, value in base.items():
                new_value = (row.get(column, 0) - factor * value) % prime
                if new_value:
                    row[column] = new_value
                else:
                    row.pop(column, None)
    return len(pivot_rows)


def permutation_on_basis(builder, basis, element) -> list[int]:
    index = {item: i for i, item in enumerate(basis)}
    return [
        index[builder.exponent_image(item, element)] for item in basis
    ]


def exact_kernel_character(
    builder, basis, kernel: list[list[Fraction]], element
) -> int:
    if not kernel:
        return 0
    # The scaffold returns RREF rows.  Locate their pivot columns.
    pivots = []
    for row in kernel:
        pivot = next(index for index, value in enumerate(row) if value)
        assert row[pivot] == 1
        assert all(previous[pivot] == 0 for previous in kernel[: len(pivots)])
        pivots.append(pivot)
    permutation = permutation_on_basis(builder, basis, element)
    trace = Fraction(0)
    for row_index, row in enumerate(kernel):
        transformed = [Fraction(0)] * len(row)
        for source, target in enumerate(permutation):
            transformed[target] = row[source]
        # RREF coordinates are the values at pivot columns.
        trace += transformed[pivots[row_index]]
    assert trace.denominator == 1
    return int(trace)


def compose(left, right):
    left_sign, left_shift = left
    right_sign, right_shift = right
    return (
        left_sign * right_sign,
        (left_sign * right_shift + left_shift) % 11,
    )


def exact_face_dimension_by_character(builder, orbit, kernel) -> int:
    group = orbit.stabilizer
    character: dict[tuple[int, int], int] = {}
    for element in group:
        permutation = permutation_on_basis(builder, orbit.basis, element)
        ambient_trace = sum(i == target for i, target in enumerate(permutation))
        kernel_trace = exact_kernel_character(
            builder, orbit.basis, kernel, element
        )
        character[element] = ambient_trace - kernel_trace
    numerator = sum(
        character[element] ** 2 + character[compose(element, element)]
        for element in group
    )
    denominator = 2 * len(group)
    assert numerator % denominator == 0
    return numerator // denominator


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                return digest.hexdigest().upper()
            digest.update(block)


def run_gate(data_path: Path) -> list[str]:
    messages: list[str] = []
    data = np.load(data_path, allow_pickle=False)
    builder = load_module("codex_r10_face_gate_builder", BUILDER_PATH)
    scaffold = load_module("codex_r10_face_gate_scaffold", SCAFFOLD_PATH)
    face = scaffold.build_face_model()
    base = face.base

    cycles = independently_rebuild_c5s(base.edges)
    assert len(cycles) == 33
    assert np.array_equal(data["c5s"], np.asarray(cycles, dtype=np.int32))
    assert list(data["cut_masks"]) == [mask for mask, _mono in base.cuts]
    assert np.array_equal(data["edges"], np.asarray(base.edges, dtype=np.int32))

    forced = np.asarray(face.forced_zero_multiplier_orbits, dtype=np.int32)
    live = data["live_multiplier_orbits"].astype(np.int32)
    assert np.array_equal(data["forced_multiplier_orbits"], forced)
    assert sorted(set(forced) | set(live)) == list(
        range(int(base.multiplier_variable.size))
    )
    assert not (set(forced) & set(live))
    messages.append(
        f"F1_PASS forced_nu_orbits={len(forced)} live_nu_orbits={len(live)}"
    )

    scaffold_kernel_ranks = np.asarray(
        [len(item.kernel) for item in face.orbit_data], dtype=np.int32
    )
    artifact_kernel_ranks = data["gram_kernel_dims"].astype(np.int32)
    assert np.array_equal(scaffold_kernel_ranks, artifact_kernel_ranks)
    messages.append(
        "F2_SCAFFOLD_PASS per_block_kernel_ranks="
        + json.dumps([int(value) for value in artifact_kernel_ranks])
    )
    messages.append(
        f"F2_TOTAL_PASS total={int(artifact_kernel_ranks.sum())} "
        f"central={int(artifact_kernel_ranks[0])}"
    )

    normalization = unpack_csr(data, "normalization_live")
    target_nu = unpack_csr(data, "target_nu_live")
    target_gram = unpack_csr(data, "target_gram")
    gram_face = unpack_csr(data, "gram_face")

    assert sparse_equal(
        normalization,
        base.multiplier_normalization[:, live],
    )
    assert sparse_equal(target_nu, base.multiplier_target[:, live])
    builder_target_gram = sp.hstack(
        [orbit.coefficient_map for orbit in base.gram_orbits],
        format="csr",
    )
    assert sparse_equal(target_gram, builder_target_gram)
    assert np.array_equal(
        data["normalization_rhs"],
        np.asarray(
            [
                25 * builder.multinom(base.multiplier_monomials[index])
                for index in builder.orbit_ids(
                    builder.action_table(base.multiplier_monomials)[0]
                )[1]
            ],
            dtype=np.int64,
        ),
    )
    assert np.array_equal(
        data["target_rhs"],
        np.asarray(
            [
                builder.multinom(base.target_monomials[index])
                for index in base.target_representatives
            ],
            dtype=np.int64,
        ),
    )
    messages.append(
        "LINEAR_MAPS_PASS normalization=56x1464 "
        "target_nu=392x1464 target_gram=392x8647"
    )

    offsets = data["gram_offsets"].astype(int)
    qdims = data["gram_qdims"].astype(int)
    stored_face_dims = data["gram_face_dimensions"].astype(int)
    stored_ranks = data["gram_constraint_ranks"].astype(int)
    row_offset = 0
    exact_rank_total = 0
    exact_face_total = 0
    for block_index, (orbit, orbit_face) in enumerate(
        zip(base.gram_orbits, face.orbit_data)
    ):
        offset = int(offsets[block_index])
        qdim = int(qdims[block_index])
        rank = int(stored_ranks[block_index])
        block_h = gram_face[
            row_offset : row_offset + rank, offset : offset + qdim
        ].tocsr()
        assert block_h.shape == (rank, qdim)

        canonical_rows = canonical_equation_rows(
            orbit.entry_ids, orbit.basis, cycles
        )
        for h_row in range(block_h.shape[0]):
            start = int(block_h.indptr[h_row])
            stop = int(block_h.indptr[h_row + 1])
            row_key = tuple(
                (int(column), int(value))
                for column, value in zip(
                    block_h.indices[start:stop], block_h.data[start:stop]
                )
            )
            assert row_key in canonical_rows

        modular = modular_rank(block_h, CHECK_PRIME)
        assert modular == rank
        exact_face_dimension = exact_face_dimension_by_character(
            builder, orbit, orbit_face.kernel
        )
        assert exact_face_dimension == int(stored_face_dims[block_index])
        assert rank == qdim - exact_face_dimension
        exact_rank_total += rank
        exact_face_total += exact_face_dimension
        row_offset += rank

    assert row_offset == gram_face.shape[0] == 1471
    assert exact_rank_total == 1471
    assert exact_face_total == 7176
    messages.append(
        f"GRAM_FACE_PASS rows={gram_face.shape[0]} "
        f"rank_mod_{CHECK_PRIME}={modular_rank(gram_face, CHECK_PRIME)} "
        "exact_character_rank=1471 gram_face_dimension=7176"
    )
    messages.append(
        "DIMENSIONS_PASS face_variables=1464+7176=8640 "
        "certificate_equations=56+392"
    )
    messages.append("EXACT_GATE_PASS: no SDP run and no theorem claim")
    return messages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument(
        "--log",
        type=Path,
        default=HERE / "CODEX_R10_c5_FACE_GATE.log",
    )
    args = parser.parse_args()
    messages = run_gate(args.data)
    messages.extend(
        [
            f"SHA256_DATA={sha256(args.data)}",
            f"SHA256_GATE={sha256(Path(__file__))}",
        ]
    )
    text = "\n".join(messages) + "\n"
    args.log.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    print(f"LOG={args.log.resolve()}")
    print(f"SHA256_LOG={sha256(args.log)}")


if __name__ == "__main__":
    main()
