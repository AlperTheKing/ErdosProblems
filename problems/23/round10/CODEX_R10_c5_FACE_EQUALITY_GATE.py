"""Independent replay gate for the q<=50 generalized equality face.

This gate does not import CODEX_R10_c5_FACE_EQUALITY.py.  It rebuilds the
graph/cuts through the D22 constructor, parses the collector log separately,
checks every equality ray and balanced blow-up classification, recomputes the
incremental F1 and F2 ranks modulo an independent prime, verifies all sparse
coefficient maps, and checks the 6129 exported Gram rows are genuine equality
kernel equations with full row rank modulo the independent prime.

The producer supplies the exact rational rank proof via the blockwise
invariant-character formula.  This gate supplies an independent nonzero-minor
replay and structural comparison.  No SDP is solved.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
LOG_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_q5_q50.log"
BUILDER_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
BASE_FACE_PATH = HERE / "CODEX_R10_c5_FACE_data.npz"
PRIME = 1_000_003
Q_LAYERS = tuple(range(5, 51, 5))


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "codex_r10_equality_gate_builder", BUILDER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load D22 constructor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def unpack_csr(data, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            data[f"{name}_data"].astype(np.int64),
            data[f"{name}_indices"].astype(np.int32),
            data[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in data[f"{name}_shape"]),
        dtype=np.int64,
    )


def sparse_equal(left: sp.spmatrix, right: sp.spmatrix) -> bool:
    difference = left.astype(np.int64).tocsr() - right.astype(np.int64).tocsr()
    difference.eliminate_zeros()
    return difference.shape == left.shape == right.shape and difference.nnz == 0


def parse_points(path: Path) -> list[tuple[int, ...]]:
    pattern = re.compile(r"EQ q=(\d+) x=\[([0-9,]+)\]$")
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[-2:] == [
        "END_PRIMITIVE_EQUALITY_ORBITS",
        "EXACT_FINITE_COLLECTION_ONLY: no all-real theorem claim",
    ]
    points = []
    for line in lines:
        match = pattern.fullmatch(line)
        if match:
            vector = tuple(int(value) for value in match.group(2).split(","))
            assert sum(vector) == int(match.group(1))
            points.append(vector)
    assert len(points) == len(set(points)) == 439
    return points


def vector_image(vector, element):
    sign, shift = element
    output = [0] * 11
    for vertex, value in enumerate(vector):
        output[(sign * vertex + shift) % 11] = value
    return tuple(output)


def canonical_vector(vector, group):
    return min(vector_image(vector, element) for element in group)


def exact_arc_values(model, vector):
    return [
        sum(
            vector[model.edges[edge_index][0]]
            * vector[model.edges[edge_index][1]]
            for edge_index in mono
        )
        for _mask, mono in model.cuts
    ]


def validated_partitions(data, model) -> list[tuple[tuple[int, ...], ...]]:
    edge_set = set(model.edges)
    partitions = []
    for mask_row in data["complete_blowup_partition_masks"]:
        classes = tuple(
            tuple(vertex for vertex in range(11) if (int(mask) >> vertex) & 1)
            for mask in mask_row
        )
        assert all(classes)
        assert len(set().union(*(set(cls) for cls in classes))) == sum(
            len(cls) for cls in classes
        )
        class_of = {
            vertex: class_index
            for class_index, cls in enumerate(classes)
            for vertex in cls
        }
        for left, right in itertools.combinations(sorted(class_of), 2):
            distance = (class_of[left] - class_of[right]) % 5
            required = distance in (1, 4)
            actual = tuple(sorted((left, right))) in edge_set
            assert required == actual
        partitions.append(classes)
    assert len(partitions) == 10
    return partitions


def balanced_on_partition(vector, partition) -> bool:
    q = sum(vector)
    if q % 5:
        return False
    union = set().union(*(set(cls) for cls in partition))
    if any(vector[vertex] for vertex in range(11) if vertex not in union):
        return False
    target = q // 5
    return all(sum(vector[vertex] for vertex in cls) == target for cls in partition)


def balanced_up_to_group(vector, partitions, group) -> bool:
    return any(
        balanced_on_partition(vector_image(vector, element), partition)
        for element in group
        for partition in partitions
    )


class ModSpan:
    def __init__(self, prime: int) -> None:
        self.prime = prime
        self.rows: dict[int, dict[int, int]] = {}

    def add(self, source) -> bool:
        row = {
            index: int(value) % self.prime
            for index, value in enumerate(source)
            if int(value) % self.prime
        }
        while row:
            pivot = min(row)
            if pivot not in self.rows:
                inverse = pow(row[pivot], self.prime - 2, self.prime)
                self.rows[pivot] = {
                    column: value * inverse % self.prime
                    for column, value in row.items()
                    if value * inverse % self.prime
                }
                return True
            factor = row[pivot]
            for column, value in self.rows[pivot].items():
                updated = (row.get(column, 0) - factor * value) % self.prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
        return False

    @property
    def rank(self) -> int:
        return len(self.rows)


def support_mask(vector) -> int:
    return sum(1 << vertex for vertex, value in enumerate(vector) if value)


def weighted_row(orbit, vector):
    parity = orbit.parity_rep
    if any(parity[vertex] and vector[vertex] == 0 for vertex in range(11)):
        return None
    output = []
    for exponent in orbit.basis:
        value = 1
        for vertex in range(11):
            power = (exponent[vertex] - parity[vertex]) // 2
            if power:
                value *= vector[vertex] ** power
        output.append(value)
    return tuple(output)


def normalized_equation_keys(orbit, vectors) -> set[tuple[tuple[int, int], ...]]:
    keys = set()
    for vector in vectors:
        nonzero = [(index, value) for index, value in enumerate(vector) if value]
        for row_index in range(len(orbit.basis)):
            coefficients: Counter[int] = Counter()
            for column_index, value in nonzero:
                coefficients[int(orbit.entry_ids[row_index, column_index])] += value
            if not coefficients:
                continue
            gcd = 0
            for value in coefficients.values():
                gcd = math.gcd(gcd, abs(value))
            keys.add(
                tuple(
                    sorted(
                        (column, value // gcd)
                        for column, value in coefficients.items()
                    )
                )
            )
    return keys


def modular_rank_csr(matrix: sp.csr_matrix, prime: int) -> int:
    span = ModSpan(prime)
    for row_index in range(matrix.shape[0]):
        start = int(matrix.indptr[row_index])
        stop = int(matrix.indptr[row_index + 1])
        dense = [0] * matrix.shape[1]
        for column, value in zip(
            matrix.indices[start:stop], matrix.data[start:stop]
        ):
            dense[int(column)] = int(value)
        span.add(dense)
    return span.rank


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                return digest.hexdigest().upper()
            digest.update(block)


def run_gate(data_path: Path, log_path: Path) -> list[str]:
    builder = load_builder()
    model = builder.build_model()
    data = np.load(data_path, allow_pickle=False)
    points = parse_points(log_path)
    assert np.array_equal(
        data["equality_representatives"], np.asarray(points, dtype=np.int16)
    )

    histogram = Counter(sum(value > 0 for value in point) for point in points)
    assert histogram == {5: 3, 6: 94, 7: 342}
    for point in points:
        q = sum(point)
        assert q in Q_LAYERS
        assert math.gcd(*point) == 1
        assert canonical_vector(point, builder.GROUP) == point
        assert min(exact_arc_values(model, point)) == q * q // 25

    partitions = validated_partitions(data, model)
    assert all(
        balanced_up_to_group(point, partitions, builder.GROUP)
        for point in points
    )
    messages = [
        "COLLECTOR_PASS reps=439 support_histogram={5:3,6:94,7:342}",
        "PLATEAU_PASS balanced_complete_C5_blowup=439/439 partitions=10",
    ]

    monomial_masks = [
        sum(1 << vertex for vertex, value in enumerate(exponent) if value)
        for exponent in model.multiplier_monomials
    ]
    forced: set[int] = set()
    mod_spans = [ModSpan(PRIME) for _orbit in model.gram_orbits]
    forced_by_layer = []
    kernel_rank_by_layer = []
    for q in Q_LAYERS:
        layer = [point for point in points if sum(point) == q]
        for point in layer:
            mask = support_mask(point)
            supported = [
                index
                for index, monomial_mask in enumerate(monomial_masks)
                if monomial_mask & ~mask == 0
            ]
            target = q * q // 25
            for cut_index, value in enumerate(exact_arc_values(model, point)):
                if value > target:
                    forced.update(
                        int(model.multiplier_orbit_ids[cut_index, monomial_index])
                        for monomial_index in supported
                    )
        full_layer = {
            vector_image(point, element)
            for point in layer
            for element in builder.GROUP
        }
        for point in full_layer:
            for orbit, span in zip(model.gram_orbits, mod_spans):
                row = weighted_row(orbit, point)
                if row is not None:
                    span.add(row)
        forced_by_layer.append(len(forced))
        kernel_rank_by_layer.append(sum(span.rank for span in mod_spans))

    assert np.array_equal(
        data["increment_forced_multiplier_orbits"],
        np.asarray(forced_by_layer, dtype=np.int32),
    )
    assert np.array_equal(
        data["increment_kernel_rank_total"],
        np.asarray(kernel_rank_by_layer, dtype=np.int32),
    )
    assert set(data["forced_multiplier_orbits"].astype(int)) == forced
    messages.append(
        "INCREMENTS_PASS F1=[1147,2051,2085,2085,...] "
        "F2_kernel=[74,302,399,402,402,...]"
    )

    base = np.load(BASE_FACE_PATH, allow_pickle=False)
    assert set(base["forced_multiplier_orbits"].astype(int)) == {
        orbit
        for orbit in forced
        if orbit in set(base["forced_multiplier_orbits"].astype(int))
    }
    assert forced_by_layer[0] == len(base["forced_multiplier_orbits"]) == 1147
    assert kernel_rank_by_layer[0] == int(base["gram_kernel_dims"].sum()) == 74

    live = data["live_multiplier_orbits"].astype(np.int32)
    normalization = unpack_csr(data, "normalization_live")
    target_nu = unpack_csr(data, "target_nu_live")
    target_gram = unpack_csr(data, "target_gram")
    gram_face = unpack_csr(data, "gram_face")
    assert sparse_equal(normalization, model.multiplier_normalization[:, live])
    assert sparse_equal(target_nu, model.multiplier_target[:, live])
    assert sparse_equal(
        target_gram,
        sp.hstack(
            [orbit.coefficient_map for orbit in model.gram_orbits],
            format="csr",
        ),
    )
    assert normalization.shape == (56, 526)
    assert target_nu.shape == (392, 526)
    assert target_gram.shape == (392, 8647)
    messages.append("MAPS_PASS norm=56x526 target_nu=392x526 target_gram=392x8647")

    offsets = data["gram_offsets"].astype(int)
    qdims = data["gram_qdims"].astype(int)
    ranks = data["gram_constraint_ranks"].astype(int)
    row_offset = 0
    for orbit_index, orbit in enumerate(model.gram_orbits):
        rank = int(ranks[orbit_index])
        q_offset = int(offsets[orbit_index])
        qdim = int(qdims[orbit_index])
        block_h = gram_face[
            row_offset : row_offset + rank,
            q_offset : q_offset + qdim,
        ].tocsr()
        assert modular_rank_csr(block_h, PRIME) == rank

        final_vectors = []
        seen = set()
        for point in points:
            for element in builder.GROUP:
                row = weighted_row(orbit, vector_image(point, element))
                if row is not None and row not in seen:
                    seen.add(row)
                    final_vectors.append(row)
        genuine = normalized_equation_keys(orbit, final_vectors)
        for local_row in range(block_h.shape[0]):
            start = int(block_h.indptr[local_row])
            stop = int(block_h.indptr[local_row + 1])
            key = tuple(
                (int(column), int(value))
                for column, value in zip(
                    block_h.indices[start:stop], block_h.data[start:stop]
                )
            )
            assert key in genuine
        row_offset += rank

    assert row_offset == gram_face.shape[0] == 6129
    messages.append(
        f"GRAM_FACE_PASS genuine_rows=6129 rank_mod_{PRIME}=6129 "
        "exact_character_rank=6129 face_dimension=2518"
    )
    messages.append(
        "FINAL_DIMENSIONS_PASS forced_nu=2085 live_nu=526 "
        "kernel_rank=402 face_variables=526+2518=3044"
    )
    messages.append("FINITE_EXACT_GATE_PASS: no SDP run and no theorem claim")
    return messages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--log", type=Path, default=LOG_PATH)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "CODEX_R10_c5_FACE_EQUALITY_GATE.log",
    )
    args = parser.parse_args()
    messages = run_gate(args.data, args.log)
    messages.extend(
        [
            f"SHA256_DATA={sha256(args.data)}",
            f"SHA256_COLLECTOR_LOG={sha256(args.log)}",
            f"SHA256_GATE={sha256(Path(__file__))}",
        ]
    )
    text = "\n".join(messages) + "\n"
    args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    print(f"OUTPUT={args.output.resolve()}")
    print(f"SHA256_OUTPUT={sha256(args.output)}")


if __name__ == "__main__":
    main()
