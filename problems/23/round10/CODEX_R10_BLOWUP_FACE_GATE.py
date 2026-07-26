"""Independent exact gate for the balanced-C5-blow-up face artifact.

The producer is not imported.  This gate independently enumerates the
plateaus by extending induced C5s with full twins, reconstructs the multiplier
zeros, spans every parity-block evaluation family by an exact shifted-simplex
grid through degree three, checks the invariant character codimensions, and
verifies the exported integer CSR matrix in the base D22 Gram-column order.

No optimization problem is solved.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
SOURCE_PATH = HERE / "CODEX_R10_BLOWUP_FACE.py"
DEFAULT_DATA = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
DEFAULT_SUMMARY = HERE / "CODEX_R10_BLOWUP_FACE_summary.json"
DEFAULT_REPORT = HERE / "CODEX_R10_BLOWUP_FACE_REPORT.md"
EQUALITY_LOG = HERE / "CODEX_R10_c5_FACE_EQUALITY_q5_q50.log"
N = 11
PRIMES = (1_000_003, 2_000_003)
CLAUDE_Q10 = (2, 1, 1, 0, 2, 0, 1, 1, 2, 0, 0)

Exponent = tuple[int, ...]
GroupElement = tuple[int, int]
Partition = tuple[tuple[int, ...], ...]


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "codex_blowup_face_gate_builder", BUILDER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BUILDER_PATH}")
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_cycle(classes: Sequence[Sequence[int]]) -> Partition:
    ordered = tuple(tuple(sorted(part)) for part in classes)
    return min(
        [
            tuple(ordered[(shift + step) % 5] for step in range(5))
            for shift in range(5)
        ]
        + [
            tuple(ordered[(shift - step) % 5] for step in range(5))
            for shift in range(5)
        ]
    )


def cycle_order(
    vertices: Sequence[int], edge_set: set[tuple[int, int]]
) -> tuple[int, ...]:
    adjacency = {
        vertex: [
            other
            for other in vertices
            if other != vertex
            and tuple(sorted((vertex, other))) in edge_set
        ]
        for vertex in vertices
    }
    assert all(len(neighbors) == 2 for neighbors in adjacency.values())
    start = min(vertices)
    orders = []
    for second in adjacency[start]:
        order = [start, second]
        while len(order) < 5:
            choices = [
                vertex
                for vertex in adjacency[order[-1]]
                if vertex != order[-2]
            ]
            next_vertex = next(
                vertex for vertex in choices if vertex not in order
            )
            order.append(next_vertex)
        assert tuple(sorted((order[-1], start))) in edge_set
        orders.append(tuple(order))
    return min(orders)


def is_complete_blowup(
    partition: Partition, edge_set: set[tuple[int, int]]
) -> bool:
    vertices = set(sum(partition, ()))
    for u, v in combinations(sorted(vertices), 2):
        left = next(i for i, part in enumerate(partition) if u in part)
        right = next(i for i, part in enumerate(partition) if v in part)
        expected = (left - right) % 5 in (1, 4)
        if ((u, v) in edge_set) != expected:
            return False
    return True


def enumerate_plateaus(
    edges: Sequence[tuple[int, int]]
) -> list[Partition]:
    """Independent Theorem-C enumeration: C5 plus selectable full twins."""
    edge_set = set(edges)
    output: set[Partition] = set()
    for vertices in combinations(range(N), 5):
        induced_edges = [
            (u, v)
            for u, v in edges
            if u in vertices and v in vertices
        ]
        degrees = Counter(vertex for edge in induced_edges for vertex in edge)
        if len(induced_edges) != 5 or any(
            degrees[vertex] != 2 for vertex in vertices
        ):
            continue
        cycle = cycle_order(vertices, edge_set)
        candidates: list[tuple[int, int]] = []
        for vertex in set(range(N)) - set(cycle):
            neighbors = {
                cycle_index
                for cycle_index, cycle_vertex in enumerate(cycle)
                if tuple(sorted((vertex, cycle_vertex))) in edge_set
            }
            for class_index in range(5):
                if neighbors == {
                    (class_index - 1) % 5,
                    (class_index + 1) % 5,
                }:
                    candidates.append((vertex, class_index))
        assert len({vertex for vertex, _class in candidates}) == len(candidates)
        for choice in range(1 << len(candidates)):
            classes = [[cycle[index]] for index in range(5)]
            for candidate_index, (vertex, class_index) in enumerate(candidates):
                if (choice >> candidate_index) & 1:
                    classes[class_index].append(vertex)
            partition = canonical_cycle(classes)
            if is_complete_blowup(partition, edge_set):
                output.add(partition)
    return sorted(output)


def partition_image(
    builder, partition: Partition, element: GroupElement
) -> Partition:
    return canonical_cycle(
        [
            [builder.vertex_image(vertex, element) for vertex in part]
            for part in partition
        ]
    )


def partition_orbits(builder, partitions: Sequence[Partition]) -> list[list[int]]:
    index = {partition: i for i, partition in enumerate(partitions)}
    unseen = set(range(len(partitions)))
    output = []
    while unseen:
        seed = min(unseen)
        orbit = sorted(
            {
                index[partition_image(builder, partitions[seed], element)]
                for element in builder.GROUP
            }
        )
        output.append(orbit)
        unseen.difference_update(orbit)
    return output


def support(exponent: Sequence[int]) -> frozenset[int]:
    return frozenset(i for i, power in enumerate(exponent) if power)


def cut_is_identically_tight(
    partition: Partition, side: frozenset[int]
) -> bool:
    """Independent exact coefficient test for q_S-1 on the plateau."""
    split_classes = [
        index
        for index, part in enumerate(partition)
        if set(part) & side and set(part) - side
    ]
    variable_index = {
        class_index: index
        for index, class_index in enumerate(split_classes)
    }
    zero = (0,) * len(split_classes)

    def t_polynomial(class_index: int) -> dict[tuple[int, ...], int]:
        if class_index in variable_index:
            exponent = [0] * len(split_classes)
            exponent[variable_index[class_index]] = 1
            return {tuple(exponent): 1}
        return {
            zero: int(all(vertex in side for vertex in partition[class_index]))
        }

    t = [t_polynomial(index) for index in range(5)]
    polynomial: Counter[tuple[int, ...]] = Counter({zero: 4})
    for term in t:
        for exponent, value in term.items():
            polynomial[exponent] -= 2 * value
    for index in range(5):
        for left, left_value in t[index].items():
            for right, right_value in t[(index + 1) % 5].items():
                exponent = tuple(a + b for a, b in zip(left, right))
                polynomial[exponent] += 2 * left_value * right_value
    return not any(polynomial.values())


def compositions_up_to(variables: int, degree: int) -> list[tuple[int, ...]]:
    if variables == 0:
        return [()]
    output = []

    def visit(index: int, remaining: int, prefix: list[int]) -> None:
        if index == variables:
            output.append(tuple(prefix))
            return
        for value in range(remaining + 1):
            visit(index + 1, remaining - value, prefix + [value])

    visit(0, degree, [])
    return output


def shifted_simplex_rows(
    basis: Sequence[Exponent],
    parity_mask: Exponent,
    partition: Partition,
) -> set[tuple[int, ...]]:
    vertices = set(sum(partition, ()))
    if not support(parity_mask) <= vertices:
        return set()
    pivots = [part[-1] for part in partition]
    free_vertices = [
        vertex
        for part, pivot in zip(partition, pivots)
        for vertex in part
        if vertex != pivot
    ]
    degree = (6 - sum(parity_mask)) // 2
    denominator = len(free_vertices) + degree + 1
    rows = set()
    for lattice in compositions_up_to(len(free_vertices), degree):
        numerator = [0] * N
        for vertex, value in zip(free_vertices, lattice):
            numerator[vertex] = value + 1
        for part, pivot in zip(partition, pivots):
            numerator[pivot] = denominator - sum(
                numerator[vertex] for vertex in part if vertex != pivot
            )
            assert numerator[pivot] > 0
        row = []
        for beta in basis:
            gamma = tuple(
                (beta[index] - parity_mask[index]) // 2
                for index in range(N)
            )
            if not support(gamma) <= vertices:
                row.append(0)
                continue
            value = 1
            for vertex, power in enumerate(gamma):
                value *= numerator[vertex] ** power
            row.append(value)
        if any(row):
            rows.add(tuple(row))
    return rows


def exact_echelon(
    rows: Iterable[Sequence[int | Fraction]],
) -> tuple[list[list[Fraction]], list[int]]:
    basis: list[list[Fraction]] = []
    pivots: list[int] = []
    for source in rows:
        row = [Fraction(value) for value in source]
        for old, pivot in zip(basis, pivots):
            if row[pivot]:
                factor = row[pivot]
                row = [
                    value - factor * old_value
                    for value, old_value in zip(row, old)
                ]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        scale = row[pivot]
        row = [value / scale for value in row]
        for old_index in range(len(basis)):
            if basis[old_index][pivot]:
                factor = basis[old_index][pivot]
                basis[old_index] = [
                    value - factor * row_value
                    for value, row_value in zip(basis[old_index], row)
                ]
        insertion = next(
            (
                index
                for index, old_pivot in enumerate(pivots)
                if old_pivot > pivot
            ),
            len(pivots),
        )
        basis.insert(insertion, row)
        pivots.insert(insertion, pivot)
    return basis, pivots


def coordinates_in_span(
    vector: Sequence[int | Fraction],
    basis: Sequence[Sequence[Fraction]],
    pivots: Sequence[int],
) -> list[Fraction]:
    remainder = [Fraction(value) for value in vector]
    coefficients = []
    for old, pivot in zip(basis, pivots):
        coefficient = remainder[pivot]
        coefficients.append(coefficient)
        if coefficient:
            remainder = [
                value - coefficient * old_value
                for value, old_value in zip(remainder, old)
            ]
    assert not any(remainder)
    return coefficients


def transformed_row(
    builder,
    row: Sequence[int | Fraction],
    basis: Sequence[Exponent],
    element: GroupElement,
) -> list[Fraction]:
    index = {exponent: i for i, exponent in enumerate(basis)}
    output = [Fraction(0)] * len(basis)
    for source, exponent in enumerate(basis):
        output[index[builder.exponent_image(exponent, element)]] = Fraction(
            row[source]
        )
    return output


def compose(left: GroupElement, right: GroupElement) -> GroupElement:
    return (
        left[0] * right[0],
        (left[0] * right[1] + left[1]) % N,
    )


def invariant_face_dimension(
    builder,
    basis_monomials: Sequence[Exponent],
    evaluation_basis: Sequence[Sequence[Fraction]],
    evaluation_pivots: Sequence[int],
    stabilizer: Sequence[GroupElement],
) -> int:
    character = {}
    for element in stabilizer:
        ambient_trace = sum(
            builder.exponent_image(exponent, element) == exponent
            for exponent in basis_monomials
        )
        kernel_trace = Fraction(0)
        for row_index, row in enumerate(evaluation_basis):
            coordinates = coordinates_in_span(
                transformed_row(builder, row, basis_monomials, element),
                evaluation_basis,
                evaluation_pivots,
            )
            kernel_trace += coordinates[row_index]
        assert kernel_trace.denominator == 1
        character[element] = ambient_trace - int(kernel_trace)
    numerator = sum(
        character[element] ** 2 + character[compose(element, element)]
        for element in stabilizer
    )
    denominator = 2 * len(stabilizer)
    assert numerator % denominator == 0
    return numerator // denominator


def qv_equations(
    entry_ids: np.ndarray, vectors: Sequence[Sequence[int]]
) -> set[tuple[tuple[int, int], ...]]:
    output = set()
    for vector in vectors:
        nonzero = [
            (index, int(value))
            for index, value in enumerate(vector)
            if value
        ]
        for row_index in range(entry_ids.shape[0]):
            equation: Counter[int] = Counter()
            for column_index, coefficient in nonzero:
                equation[int(entry_ids[row_index, column_index])] += coefficient
            key = tuple(
                sorted(
                    (column, value)
                    for column, value in equation.items()
                    if value
                )
            )
            if key:
                output.add(key)
    return output


def modular_rank(matrix: sp.csr_matrix, prime: int) -> int:
    pivots: dict[int, dict[int, int]] = {}
    for row_index in range(matrix.shape[0]):
        row = {
            int(column): int(value) % prime
            for column, value in zip(
                matrix.indices[
                    matrix.indptr[row_index] : matrix.indptr[row_index + 1]
                ],
                matrix.data[
                    matrix.indptr[row_index] : matrix.indptr[row_index + 1]
                ],
            )
            if int(value) % prime
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
                new_value = (row.get(column, 0) - factor * value) % prime
                if new_value:
                    row[column] = new_value
                else:
                    row.pop(column, None)
    return len(pivots)


def run_gate(
    data_path: Path, summary_path: Path, report_path: Path
) -> list[str]:
    builder = load_builder()
    model = builder.build_model()
    data = np.load(data_path, allow_pickle=False)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert report_path.is_file()

    partitions = enumerate_plateaus(model.edges)
    assert len(partitions) == 132
    assert Counter(len(sum(partition, ())) for partition in partitions) == {
        5: 33,
        6: 66,
        7: 33,
    }
    orbits = partition_orbits(builder, partitions)
    assert len(orbits) == 10
    assert Counter(map(len, orbits)) == {11: 8, 22: 2}
    stored_partitions = [
        tuple(tuple(part) for part in json.loads(value))
        for value in data["partitions_json"]
    ]
    assert stored_partitions == partitions

    q10_support = frozenset(i for i, value in enumerate(CLAUDE_Q10) if value)
    q10_partition = next(
        partition
        for partition in partitions
        if set(sum(partition, ())) == q10_support
    )
    assert tuple(
        sum(CLAUDE_Q10[vertex] for vertex in part)
        for part in q10_partition
    ) == (2, 2, 2, 2, 2)

    assert np.array_equal(
        data["cut_masks"],
        np.asarray([mask for mask, _mono in model.cuts], dtype=np.int32),
    )
    assert np.array_equal(
        data["multiplier_monomials"],
        np.asarray(model.multiplier_monomials, dtype=np.int8),
    )
    pair_representatives: list[tuple[int, int] | None] = [
        None
    ] * int(model.multiplier_variable.size)
    for cut_index in range(len(model.cuts)):
        for monomial_index in range(len(model.multiplier_monomials)):
            orbit_id = int(
                model.multiplier_orbit_ids[cut_index, monomial_index]
            )
            if pair_representatives[orbit_id] is None:
                pair_representatives[orbit_id] = (
                    cut_index,
                    monomial_index,
                )
    assert np.array_equal(
        data["multiplier_pair_representatives"],
        np.asarray(pair_representatives, dtype=np.int32),
    )

    forced = set()
    forced_c5 = set()
    for partition in partitions:
        vertices = set(sum(partition, ()))
        supported = [
            index
            for index, exponent in enumerate(model.multiplier_monomials)
            if support(exponent) <= vertices
        ]
        tight_count = 0
        for cut_index, (mask, _mono) in enumerate(model.cuts):
            if cut_is_identically_tight(
                partition, builder.side_from_mask(mask)
            ):
                tight_count += 1
                continue
            ids = {
                int(model.multiplier_orbit_ids[cut_index, monomial_index])
                for monomial_index in supported
            }
            forced.update(ids)
            if len(vertices) == 5:
                forced_c5.update(ids)
        assert tight_count >= 1
    assert len(forced_c5) == 1147 and len(forced) == 2085
    assert np.array_equal(
        data["forced_c5_multiplier_orbits"],
        np.asarray(sorted(forced_c5), dtype=np.int32),
    )
    assert np.array_equal(
        data["forced_multiplier_orbits"],
        np.asarray(sorted(forced), dtype=np.int32),
    )
    assert np.array_equal(
        data["live_multiplier_orbits"],
        np.asarray(sorted(set(range(2611)) - forced), dtype=np.int32),
    )

    offsets = data["gram_offsets"].astype(int)
    qdims = data["gram_qdims"].astype(int)
    rep_masks = data["gram_rep_masks"].astype(int)
    entry_reps = data["gram_entry_representatives"].astype(int)
    expected_offsets = []
    expected_qdims = []
    expected_masks = []
    expected_entries = []
    running = 0
    for block_index, orbit in enumerate(model.gram_orbits):
        expected_offsets.append(running)
        expected_qdims.append(int(orbit.variable.size))
        expected_masks.append(orbit.parity_rep)
        first = [None] * int(orbit.variable.size)
        for i in range(len(orbit.basis)):
            for j in range(i, len(orbit.basis)):
                entry_id = int(orbit.entry_ids[i, j])
                if first[entry_id] is None:
                    first[entry_id] = (block_index, i, j)
        expected_entries.extend(first)
        running += int(orbit.variable.size)
    assert running == 8647
    assert np.array_equal(offsets, np.asarray(expected_offsets))
    assert np.array_equal(qdims, np.asarray(expected_qdims))
    assert np.array_equal(rep_masks, np.asarray(expected_masks))
    assert np.array_equal(entry_reps, np.asarray(expected_entries))

    gram_face = unpack_csr(data, "gram_face")
    assert gram_face.shape == (6129, 8647)
    assert gram_face.nnz == 71973
    stored_kernel: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for value in data["kernel_rows_json"]:
        block_index, row = json.loads(value)
        stored_kernel[int(block_index)].append(tuple(map(int, row)))
    assert sum(map(len, stored_kernel.values())) == 402

    row_start = 0
    exact_character_rank = 0
    for block_index, orbit in enumerate(model.gram_orbits):
        candidates = set()
        for member in orbit.parity_members:
            element = orbit.image_elements[member]
            acted_basis = [
                builder.exponent_image(exponent, element)
                for exponent in orbit.basis
            ]
            for partition in partitions:
                candidates.update(
                    shifted_simplex_rows(
                        acted_basis, member, partition
                    )
                )
        gate_basis, gate_pivots = exact_echelon(sorted(candidates))
        stored_rows = stored_kernel.get(block_index, [])
        for row in stored_rows:
            coordinates_in_span(row, gate_basis, gate_pivots)
        stored_basis, _stored_pivots = exact_echelon(stored_rows)
        assert len(stored_basis) == len(gate_basis)
        for element in orbit.stabilizer:
            for row in gate_basis:
                coordinates_in_span(
                    transformed_row(
                        builder, row, orbit.basis, element
                    ),
                    gate_basis,
                    gate_pivots,
                )
        face_dimension = invariant_face_dimension(
            builder,
            orbit.basis,
            gate_basis,
            gate_pivots,
            orbit.stabilizer,
        )
        block_rank = int(orbit.variable.size) - face_dimension
        exact_character_rank += block_rank
        assert block_rank == int(
            summary["per_block"][block_index]["gram_constraint_rank"]
        )

        full_block_rows = gram_face[
            row_start : row_start + block_rank, :
        ].tocsr()
        block_rows = full_block_rows[
            :, offsets[block_index] : offsets[block_index] + qdims[block_index]
        ].tocsr()
        assert block_rows.shape == (block_rank, qdims[block_index])
        assert full_block_rows.nnz == block_rows.nnz
        valid_equations = qv_equations(orbit.entry_ids, stored_rows)
        for row_index in range(block_rows.shape[0]):
            key = tuple(
                (int(column), int(value))
                for column, value in zip(
                    block_rows.indices[
                        block_rows.indptr[row_index] :
                        block_rows.indptr[row_index + 1]
                    ],
                    block_rows.data[
                        block_rows.indptr[row_index] :
                        block_rows.indptr[row_index + 1]
                    ],
                )
            )
            assert key in valid_equations
        for prime in PRIMES:
            assert modular_rank(block_rows, prime) == block_rank
        row_start += block_rank
    assert row_start == exact_character_rank == 6129

    equality_text = EQUALITY_LOG.read_text(encoding="ascii")
    equality_rays = []
    support_sizes: Counter[int] = Counter()
    partition_by_support = {
        frozenset(sum(partition, ())): partition for partition in partitions
    }
    for match in re.finditer(
        r"^EQ q=(\d+) x=\[([0-9,]+)\]$", equality_text, re.M
    ):
        q = int(match.group(1))
        weights = tuple(int(value) for value in match.group(2).split(","))
        assert len(weights) == N and sum(weights) == q
        assert math.gcd(*weights) == 1
        products = [weights[u] * weights[v] for u, v in model.edges]
        arc_minimum = min(
            sum(products[edge_index] for edge_index in mono)
            for _mask, mono in model.cuts
        )
        assert 25 * arc_minimum == q * q
        ray_support = frozenset(
            index for index, value in enumerate(weights) if value
        )
        partition = partition_by_support[ray_support]
        class_masses = tuple(
            sum(weights[vertex] for vertex in part) for part in partition
        )
        assert class_masses == (q // 5,) * 5
        equality_rays.append(weights)
        support_sizes[len(ray_support)] += 1
    assert len(equality_rays) == 439
    assert support_sizes == {5: 3, 6: 94, 7: 342}

    assert summary["complete_c5_blowup_supports"] == 132
    assert summary["D22_x_AutC5_orbits"] == 10
    assert summary["blowup_plateau_forced_multiplier_orbits"] == 2085
    assert summary["blowup_gram_face_rank"] == 6129
    assert summary["blowup_gram_face_nnz"] == 71973
    assert summary["blowup_gram_face_dimension"] == 2518

    return [
        "ENUMERATION_PASS supports=132 labeled_maps=1320 D22xAutC5_orbits=10 "
        "sizes={5:33,6:66,7:33}",
        "Q10_PASS classes=((0),(4),(8),(1,2),(6,7)) class_sums=(2,2,2,2,2)",
        "F1_PASS C5_only=1147 blowup=2085 increment=938 live=526",
        "F2_PASS evaluation_span=402 H=6129x8647 nnz=71973 "
        "rank_Q=6129 face_dimension=2518 increment_over_C5=4658",
        "ORDERING_PASS base_D22_multiplier_and_Gram_columns_exact_match",
        "FINITE_RAYS_PASS q_le_50=439/439 balanced_complete_C5_blowups "
        "support_sizes={5:3,6:94,7:342}",
        "EXACT_GATE_PASS: no SDP run and no full equality-set claim",
    ]


def validate_paths(
    data: Path, summary: Path, report: Path, log: Path
) -> None:
    inputs = [data.resolve(), summary.resolve(), report.resolve()]
    if len(set(inputs)) != 3 or not all(path.is_file() for path in inputs):
        raise ValueError("the three input artifacts must be distinct files")
    log = log.resolve()
    if not log.is_relative_to(HERE):
        raise ValueError("gate log must remain under problems/23/round10")
    if not log.parent.is_dir():
        raise ValueError("gate-log parent must already exist")
    allowed = (HERE / "CODEX_R10_BLOWUP_FACE_GATE.log").resolve()
    if log.exists() and log != allowed:
        raise ValueError(f"refusing to overwrite protected artifact: {log}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--log",
        type=Path,
        default=HERE / "CODEX_R10_BLOWUP_FACE_GATE.log",
    )
    args = parser.parse_args()
    validate_paths(args.data, args.summary, args.report, args.log)
    messages = run_gate(args.data, args.summary, args.report)
    messages.extend(
        [
            f"SHA256_SOURCE={sha256(SOURCE_PATH)}",
            f"SHA256_DATA={sha256(args.data)}",
            f"SHA256_SUMMARY={sha256(args.summary)}",
            f"SHA256_REPORT={sha256(args.report)}",
            f"SHA256_GATE={sha256(Path(__file__))}",
            f"SHA256_EQUALITY_LOG={sha256(EQUALITY_LOG)}",
        ]
    )
    text = "\n".join(messages) + "\n"
    args.log.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    print(f"LOG={args.log.resolve()}")
    print(f"SHA256_LOG={sha256(args.log)}")


if __name__ == "__main__":
    main()
