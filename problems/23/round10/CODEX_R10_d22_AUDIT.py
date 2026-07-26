"""Independent structural audit of CODEX_R10_g11_d22_sdp.py.

This script deliberately rebuilds the graph, interval cuts, monomials, D_22
actions, orbit partitions, and coefficient maps without importing the Round 7
graph/SOS helpers.  It then imports the constructor under audit and compares
the independently built objects with its reduced matrices.

No SDP is solved here.  All structural comparisons use integers.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import pickle
import re
import subprocess
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable, Sequence

import numpy as np
import sympy as sy


HERE = Path(__file__).resolve().parent
CONSTRUCTOR = HERE / "CODEX_R10_g11_d22_sdp.py"
FACE_CONSTRUCTOR = HERE / "CODEX_R10_g11_d22_face.py"
FACE_EXPORTER = HERE / "CODEX_R10_g11_d22_face_export.py"
NUMERIC_EXPORT = HERE / "CODEX_R10_g11_d22_numeric.pkl"
EQUALITY_COLLECTOR_SOURCE = HERE / "CODEX_R10_c5_FACE_EQUALITY.cpp"
EQUALITY_COLLECTOR_EXE = HERE / "CODEX_R10_c5_FACE_EQUALITY.exe"
EQUALITY_COLLECTOR_LOG = HERE / "CODEX_R10_c5_FACE_EQUALITY_q5_q50.log"
BLOWUP_FACE_SOURCE = HERE / "CODEX_R10_BLOWUP_FACE.py"
BLOWUP_FACE_DATA = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
BLOWUP_FACE_SUMMARY = HERE / "CODEX_R10_BLOWUP_FACE_summary.json"
FULL_FACE_SOURCE = HERE / "CODEX_R10_c5_FACE_EQUALITY.py"
FULL_FACE_DATA = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
FULL_FACE_SUMMARY = HERE / "CODEX_R10_c5_FACE_EQUALITY_summary.json"
N = 11
D = 4
DT = 6
GroupElement = tuple[int, int]
Exponent = tuple[int, ...]
Pair = tuple[int, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def weak_compositions(total: int, parts: int) -> list[Exponent]:
    """All weak compositions, generated independently by stars and bars."""
    if parts == 1:
        return [(total,)]
    out: list[Exponent] = []
    # A bar tuple partitions total identical stars into `parts` bins.
    for bars in __import__("itertools").combinations(range(total + parts - 1), parts - 1):
        stops = (-1,) + bars + (total + parts - 1,)
        out.append(tuple(stops[i + 1] - stops[i] - 1 for i in range(parts)))
    return sorted(out)


def multinomial(alpha: Exponent) -> int:
    value = math.factorial(sum(alpha))
    for power in alpha:
        value //= math.factorial(power)
    return value


def permutation(element: GroupElement) -> tuple[int, ...]:
    sign, shift = element
    return tuple((sign * vertex + shift) % N for vertex in range(N))


GROUP: tuple[GroupElement, ...] = tuple(
    (sign, shift) for sign in (1, -1) for shift in range(N)
)
PERMUTATIONS = {element: permutation(element) for element in GROUP}


def image_exponent(alpha: Exponent, element: GroupElement) -> Exponent:
    out = [0] * N
    p = PERMUTATIONS[element]
    for old, power in enumerate(alpha):
        out[p[old]] = power
    return tuple(out)


def image_set(side: frozenset[int], element: GroupElement) -> frozenset[int]:
    p = PERMUTATIONS[element]
    return frozenset(p[vertex] for vertex in side)


def image_vector(vector: tuple[int, ...], element: GroupElement) -> tuple[int, ...]:
    out = [0] * N
    p = PERMUTATIONS[element]
    for old, value in enumerate(vector):
        out[p[old]] = value
    return tuple(out)


def canonical_vector(vector: tuple[int, ...]) -> tuple[int, ...]:
    return min(image_vector(vector, element) for element in GROUP)


def independent_complete_c5_classes(
    support_vertices: Iterable[int], edges: Sequence[tuple[int, int]]
) -> tuple[tuple[int, ...], ...] | None:
    """Recognize a complete nonempty C5 blow-up by restricted twin classes."""
    vertices = frozenset(support_vertices)
    if len(vertices) < 5:
        return None
    edge_set = set(edges)
    twin_groups: dict[frozenset[int], list[int]] = defaultdict(list)
    for vertex in sorted(vertices):
        neighbours = frozenset(
            other
            for other in vertices
            if tuple(sorted((vertex, other))) in edge_set
        )
        twin_groups[neighbours].append(vertex)
    if len(twin_groups) != 5:
        return None
    classes = tuple(sorted(tuple(group) for group in twin_groups.values()))
    quotient_edges = []
    for left in range(5):
        for right in range(left + 1, 5):
            bits = {
                tuple(sorted((u, v))) in edge_set
                for u in classes[left]
                for v in classes[right]
            }
            if len(bits) != 1:
                return None
            if bits.pop():
                quotient_edges.append((left, right))
    degrees = Counter(index for edge in quotient_edges for index in edge)
    if len(quotient_edges) != 5 or set(degrees.values()) != {2}:
        return None
    return classes


def independent_cut_identically_tight(
    classes: Sequence[Sequence[int]],
    side: frozenset[int],
    edges: Sequence[tuple[int, int]],
) -> bool:
    """Exact zero-polynomial test for q_S-1 on a balanced blow-up plateau."""
    edge_set = set(edges)
    quotient_edges = [
        (left, right)
        for left in range(5)
        for right in range(left + 1, 5)
        if tuple(sorted((classes[left][0], classes[right][0]))) in edge_set
    ]
    assert len(quotient_edges) == 5
    fixed: dict[int, int] = {}
    split = []
    for class_index, part in enumerate(classes):
        inside = sum(vertex in side for vertex in part)
        if inside == 0:
            fixed[class_index] = 0
        elif inside == len(part):
            fixed[class_index] = 1
        else:
            split.append(class_index)
    # q_S-1 is multi-affine in the split-class side masses, so it is the zero
    # polynomial iff it vanishes at every Boolean corner.
    for assignment in __import__("itertools").product((0, 1), repeat=len(split)):
        bits = dict(fixed)
        bits.update(zip(split, assignment))
        if sum(bits[left] == bits[right] for left, right in quotient_edges) != 1:
            return False
    return True


def canonical_side(side: Iterable[int]) -> frozenset[int]:
    side = frozenset(side)
    return frozenset(range(N)) - side if 0 in side else side


def mask(side: frozenset[int]) -> int:
    assert 0 not in side
    return sum(1 << (vertex - 1) for vertex in side)


def gamma11_edges() -> list[tuple[int, int]]:
    return [
        (u, v)
        for u in range(N)
        for v in range(u + 1, N)
        if min(v - u, N - (v - u)) in (4, 5)
    ]


def monochromatic_edges(
    side: frozenset[int], edges: list[tuple[int, int]]
) -> frozenset[int]:
    return frozenset(
        index for index, (u, v) in enumerate(edges) if ((u in side) == (v in side))
    )


def interval_cuts(edges: list[tuple[int, int]]) -> list[tuple[int, frozenset[int]]]:
    by_mask: dict[int, frozenset[int]] = {}
    for length in range(6):
        starts = range(N) if length else range(1)
        for start in starts:
            side = canonical_side((start + offset) % N for offset in range(length))
            by_mask[mask(side)] = monochromatic_edges(side, edges)
    return sorted(by_mask.items())


def orbit(seed, action) -> frozenset:
    return frozenset(action(seed, element) for element in GROUP)


def partition(objects, action) -> list[frozenset]:
    unseen = set(objects)
    result = []
    while unseen:
        seed = min(unseen)
        members = orbit(seed, action)
        assert members <= unseen | (set(objects) - unseen)
        result.append(members)
        unseen -= members
    return result


def sparse_row(matrix, row: int) -> dict[int, int]:
    vector = matrix.getrow(row)
    return {
        int(column): int(round(value))
        for column, value in zip(vector.indices, vector.data)
        if value
    }


def full_row_rank_mod_prime(rows: list[list[int]], prime: int = 1_000_003) -> int:
    """Exact modular row rank; full modular row rank certifies full Q-rank."""
    if not rows:
        return 0
    work = [[value % prime for value in row] for row in rows]
    number_rows = len(work)
    number_columns = len(work[0])
    pivot_row = 0
    for column in range(number_columns):
        pivot = next(
            (row for row in range(pivot_row, number_rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], prime - 2, prime)
        work[pivot_row] = [(value * inverse) % prime for value in work[pivot_row]]
        for row in range(number_rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (a - factor * b) % prime
                for a, b in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == number_rows:
            break
    return pivot_row


def exhaustive_primitive_equality_orbits(
    q: int,
    edges: list[tuple[int, int]],
    cuts: list[tuple[int, frozenset[int]]],
) -> set[tuple[int, ...]]:
    """Raw-composition equality rays, independent of the C5 support reduction."""
    assert q % 5 == 0
    target = q * q // 25
    result: set[tuple[int, ...]] = set()
    for vector in weak_compositions(q, N):
        if math.gcd(*vector) != 1:
            continue
        edge_products = tuple(vector[u] * vector[v] for u, v in edges)
        minimum = min(
            sum(edge_products[edge_index] for edge_index in mono_edges)
            for _, mono_edges in cuts
        )
        if minimum == target:
            result.add(canonical_vector(vector))
    return result


def multiply_sparse_polynomials(
    left: dict[tuple[int, ...], int], right: dict[tuple[int, ...], int]
) -> dict[tuple[int, ...], int]:
    output: Counter[tuple[int, ...]] = Counter()
    for left_exp, left_value in left.items():
        for right_exp, right_value in right.items():
            output[tuple(a + b for a, b in zip(left_exp, right_exp))] += (
                left_value * right_value
            )
    return {exponent: value for exponent, value in output.items() if value}


def independent_plateau_coefficient_rows(
    basis: Sequence[Exponent],
    parity_mask: Exponent,
    classes: Sequence[Sequence[int]],
) -> set[tuple[int, ...]]:
    """Exact coefficient rows after eliminating one variable per C5 class."""
    vertices = frozenset(vertex for part in classes for vertex in part)
    if any(power and vertex not in vertices for vertex, power in enumerate(parity_mask)):
        return set()
    pivots = {
        max(part): tuple(vertex for vertex in part if vertex != max(part))
        for part in classes
    }
    free_vertices = tuple(
        vertex for part in classes for vertex in part if vertex != max(part)
    )
    free_index = {vertex: index for index, vertex in enumerate(free_vertices)}
    zero = (0,) * len(free_vertices)
    coefficient_rows: dict[tuple[int, ...], list[int]] = {}

    for column, beta in enumerate(basis):
        gamma = tuple(
            (beta[vertex] - parity_mask[vertex]) // 2 for vertex in range(N)
        )
        assert all(value >= 0 for value in gamma)
        if any(power and vertex not in vertices for vertex, power in enumerate(gamma)):
            continue
        polynomial: dict[tuple[int, ...], int] = {zero: 1}
        for vertex, power in enumerate(gamma):
            if not power:
                continue
            if vertex in free_index:
                shifted = {}
                for exponent, value in polynomial.items():
                    image = list(exponent)
                    image[free_index[vertex]] += power
                    shifted[tuple(image)] = value
                polynomial = shifted
                continue
            affine: dict[tuple[int, ...], int] = {zero: 1}
            for free_vertex in pivots[vertex]:
                exponent = [0] * len(free_vertices)
                exponent[free_index[free_vertex]] = 1
                affine[tuple(exponent)] = -1
            for _ in range(power):
                polynomial = multiply_sparse_polynomials(polynomial, affine)
        for exponent, value in polynomial.items():
            coefficient_rows.setdefault(exponent, [0] * len(basis))[column] = value
    return {
        tuple(row) for row in coefficient_rows.values() if any(value for value in row)
    }


def sparse_independent_row_indices(
    rows: Sequence[dict[int, int]], prime: int
) -> list[int]:
    """Select an exact row basis over F_prime using sparse forward elimination."""
    pivots: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row_index, source in enumerate(rows):
        row = {
            int(column): int(value) % prime
            for column, value in source.items()
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
                selected.append(row_index)
                break
            factor = row[pivot]
            for column, value in pivots[pivot].items():
                reduced = (row.get(column, 0) - factor * value) % prime
                if reduced:
                    row[column] = reduced
                else:
                    row.pop(column, None)
    return selected


def unpack_archive_csr(
    archive: dict[str, np.ndarray], name: str
) -> tuple[tuple[int, int], list[dict[int, int]], int]:
    data = np.asarray(archive[f"{name}_data"], dtype=np.int64)
    indices = np.asarray(archive[f"{name}_indices"], dtype=np.int64)
    indptr = np.asarray(archive[f"{name}_indptr"], dtype=np.int64)
    shape = tuple(int(value) for value in archive[f"{name}_shape"])
    assert len(shape) == 2 and len(indptr) == shape[0] + 1
    assert indptr[0] == 0 and indptr[-1] == len(data) == len(indices)
    rows: list[dict[int, int]] = []
    for row_index in range(shape[0]):
        start, stop = map(int, indptr[row_index : row_index + 2])
        columns = [int(value) for value in indices[start:stop]]
        values = [int(value) for value in data[start:stop]]
        assert columns == sorted(columns) and len(columns) == len(set(columns))
        assert all(0 <= column < shape[1] for column in columns)
        assert all(value for value in values)
        rows.append(dict(zip(columns, values)))
    return (shape[0], shape[1]), rows, len(data)


def assert_archive_csr_equals(
    archive: dict[str, np.ndarray], name: str, expected
) -> None:
    matrix = expected.tocsr().astype(np.int64)
    matrix.sum_duplicates()
    matrix.sort_indices()
    shape = tuple(int(value) for value in archive[f"{name}_shape"])
    assert shape == matrix.shape
    assert np.array_equal(archive[f"{name}_data"], matrix.data)
    assert np.array_equal(archive[f"{name}_indices"], matrix.indices)
    assert np.array_equal(archive[f"{name}_indptr"], matrix.indptr)


def import_constructor():
    spec = importlib.util.spec_from_file_location("r10_d22_constructor_audited", CONSTRUCTOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def import_face_constructor():
    spec = importlib.util.spec_from_file_location("r10_d22_face_audited", FACE_CONSTRUCTOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def import_face_exporter():
    spec = importlib.util.spec_from_file_location("r10_d22_face_export_audited", FACE_EXPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    hash_before = sha256(CONSTRUCTOR)

    # ---- Independent graph and cut reconstruction ----------------------------
    edges = gamma11_edges()
    assert len(edges) == 22
    degrees = Counter(vertex for edge in edges for vertex in edge)
    assert set(degrees.values()) == {4}
    edge_set = set(edges)
    assert not any(
        tuple(sorted((u, v))) in edge_set
        and tuple(sorted((u, w))) in edge_set
        and tuple(sorted((v, w))) in edge_set
        for u in range(N)
        for v in range(u + 1, N)
        for w in range(v + 1, N)
    )
    for element in GROUP:
        p = PERMUTATIONS[element]
        assert {tuple(sorted((p[u], p[v]))) for u, v in edges} == edge_set

    cuts = interval_cuts(edges)
    assert len(cuts) == 56

    independent_blowups: dict[frozenset[int], tuple[tuple[int, ...], ...]] = {}
    for support_mask in range(1 << N):
        support_vertices = frozenset(
            vertex for vertex in range(N) if (support_mask >> vertex) & 1
        )
        classes = independent_complete_c5_classes(support_vertices, edges)
        if classes is not None:
            independent_blowups[support_vertices] = classes
    blowup_support_sizes = Counter(map(len, independent_blowups))
    assert blowup_support_sizes == Counter({5: 33, 6: 66, 7: 33})

    # A class-respecting arc with exactly one monochromatic quotient edge is
    # identically tight for every balanced weighting on that plateau.
    class_respecting_tight_counts = []
    for support_vertices, classes in independent_blowups.items():
        quotient_edges = [
            (left, right)
            for left in range(5)
            for right in range(left + 1, 5)
            if tuple(sorted((classes[left][0], classes[right][0]))) in edge_set
        ]
        assert len(quotient_edges) == 5
        tight_count = 0
        for cut_mask, _mono_edges in cuts:
            side = frozenset(
                vertex
                for vertex in range(1, N)
                if (cut_mask >> (vertex - 1)) & 1
            )
            class_bits = []
            for part in classes:
                inside = set(part) & side
                if inside and len(inside) != len(part):
                    break
                class_bits.append(bool(inside))
            else:
                monochromatic = sum(
                    class_bits[left] == class_bits[right]
                    for left, right in quotient_edges
                )
                tight_count += monochromatic == 1
        assert tight_count > 0
        class_respecting_tight_counts.append(tight_count)
    assert Counter(class_respecting_tight_counts) == Counter(
        {16: 11, 17: 33, 20: 33, 21: 22, 24: 11, 25: 22}
    )

    # ---- Independent finite audit of the generalized equality collector ------
    collector_source_hash_before = sha256(EQUALITY_COLLECTOR_SOURCE)
    collector_exe_hash_before = sha256(EQUALITY_COLLECTOR_EXE)
    exhaustive_orbits_by_q = {
        q: exhaustive_primitive_equality_orbits(q, edges, cuts) for q in (5, 10)
    }
    assert {q: len(orbits) for q, orbits in exhaustive_orbits_by_q.items()} == {
        5: 3,
        10: 6,
    }
    witness = (2, 1, 1, 0, 2, 0, 1, 1, 2, 0, 0)
    witness_products = tuple(witness[u] * witness[v] for u, v in edges)
    witness_values = tuple(
        sum(witness_products[edge_index] for edge_index in mono_edges)
        for _, mono_edges in cuts
    )
    assert sum(witness) == 10 and min(witness_values) == 4
    assert sum(value == 4 for value in witness_values) == 19
    assert canonical_vector(witness) in exhaustive_orbits_by_q[10]

    collector_run = subprocess.run(
        [str(EQUALITY_COLLECTOR_EXE), "5", "10", "1"],
        cwd=HERE,
        check=False,
        capture_output=True,
        text=True,
    )
    assert collector_run.returncode == 0, collector_run.stderr
    assert "STRICT_VIOLATION_ENCOUNTERED" not in collector_run.stdout
    collector_orbits_by_q: dict[int, set[tuple[int, ...]]] = defaultdict(set)
    for match in re.finditer(r"^EQ q=(\d+) x=\[([0-9,]+)\]$", collector_run.stdout, re.M):
        q = int(match.group(1))
        vector = tuple(int(value) for value in match.group(2).split(","))
        assert len(vector) == N and sum(vector) == q and math.gcd(*vector) == 1
        assert vector == canonical_vector(vector)
        collector_orbits_by_q[q].add(vector)
    assert dict(collector_orbits_by_q) == exhaustive_orbits_by_q
    assert collector_source_hash_before == sha256(EQUALITY_COLLECTOR_SOURCE)
    assert collector_exe_hash_before == sha256(EQUALITY_COLLECTOR_EXE)

    collector_log_hash_before = sha256(EQUALITY_COLLECTOR_LOG)
    collector_log = EQUALITY_COLLECTOR_LOG.read_text(encoding="ascii")
    assert "STRICT_VIOLATION_ENCOUNTERED" not in collector_log
    assert collector_log.endswith(
        "END_PRIMITIVE_EQUALITY_ORBITS\n"
        "EXACT_FINITE_COLLECTION_ONLY: no all-real theorem claim\n"
    )
    q_done = [
        tuple(map(int, match.groups()))
        for match in re.finditer(
            r"^Q_DONE q=(\d+) target=(\d+) primitive_orbits_at_q=(\d+) "
            r"cumulative_orbits=(\d+) ",
            collector_log,
            re.M,
        )
    ]
    assert [row[0] for row in q_done] == list(range(5, 51, 5))
    logged_orbits: set[tuple[int, ...]] = set()
    logged_counts: Counter[int] = Counter()
    equality_ray_support_sizes: Counter[int] = Counter()
    for match in re.finditer(r"^EQ q=(\d+) x=\[([0-9,]+)\]$", collector_log, re.M):
        reported_q = int(match.group(1))
        vector = tuple(int(value) for value in match.group(2).split(","))
        assert len(vector) == N and sum(vector) == reported_q
        assert reported_q % 5 == 0 and 5 <= reported_q <= 50
        assert math.gcd(*vector) == 1 and vector == canonical_vector(vector)
        products = tuple(vector[u] * vector[v] for u, v in edges)
        minimum = min(
            sum(products[edge_index] for edge_index in mono_edges)
            for _, mono_edges in cuts
        )
        assert 25 * minimum == reported_q * reported_q
        support_vertices = frozenset(i for i, value in enumerate(vector) if value)
        classes = independent_blowups.get(support_vertices)
        assert classes is not None
        class_masses = tuple(
            sum(vector[vertex] for vertex in part) for part in classes
        )
        assert len(set(class_masses)) == 1 and class_masses[0] * 5 == reported_q
        equality_ray_support_sizes[len(support_vertices)] += 1
        assert vector not in logged_orbits
        logged_orbits.add(vector)
        logged_counts[reported_q] += 1
    assert len(logged_orbits) == 439
    assert equality_ray_support_sizes == Counter({5: 3, 6: 94, 7: 342})
    cumulative = 0
    for q, target, at_q, reported_cumulative in q_done:
        assert target == q * q // 25 and at_q == logged_counts[q]
        cumulative += at_q
        assert reported_cumulative == cumulative
    assert cumulative == len(logged_orbits)
    for q in (5, 10):
        assert {vector for vector in logged_orbits if sum(vector) == q} == (
            exhaustive_orbits_by_q[q]
        )
    assert collector_log_hash_before == sha256(EQUALITY_COLLECTOR_LOG)

    cut_sides = {
        cut_mask: frozenset(
            vertex
            for vertex in range(1, N)
            if (cut_mask >> (vertex - 1)) & 1
        )
        for cut_mask, _mono in cuts
    }
    cut_index = {cut_mask: index for index, (cut_mask, _mono) in enumerate(cuts)}

    def cut_image(index: int, element: GroupElement) -> int:
        side = canonical_side(image_set(cut_sides[cuts[index][0]], element))
        return cut_index[mask(side)]

    cut_orbits = partition(range(len(cuts)), cut_image)
    assert sorted(map(len, cut_orbits)) == [1, 11, 11, 11, 11, 11]

    # ---- Independent monomials and D_22 orbit data ---------------------------
    mons_d = weak_compositions(D, N)
    mons_t = weak_compositions(DT, N)
    assert len(mons_d) == math.comb(N + D - 1, D) == 1001
    assert len(mons_t) == math.comb(N + DT - 1, DT) == 8008
    index_d = {alpha: index for index, alpha in enumerate(mons_d)}
    index_t = {alpha: index for index, alpha in enumerate(mons_t)}

    def mon_d_image(index: int, element: GroupElement) -> int:
        return index_d[image_exponent(mons_d[index], element)]

    def mon_t_image(index: int, element: GroupElement) -> int:
        return index_t[image_exponent(mons_t[index], element)]

    mon_d_orbits = partition(range(len(mons_d)), mon_d_image)
    mon_t_orbits = partition(range(len(mons_t)), mon_t_image)
    assert len(mon_d_orbits) == 56
    assert len(mon_t_orbits) == 392

    pair_canonical: dict[Pair, Pair] = {}
    for cut_i in range(len(cuts)):
        for mon_i in range(len(mons_d)):
            images = [
                (cut_image(cut_i, element), mon_d_image(mon_i, element))
                for element in GROUP
            ]
            pair_canonical[(cut_i, mon_i)] = min(images)
    pair_keys = sorted(set(pair_canonical.values()))
    assert len(pair_keys) == 2611
    pair_key_index = {key: index for index, key in enumerate(pair_keys)}

    # ---- Import and align with the constructor under audit -------------------
    constructor = import_constructor()
    model = constructor.build_model()
    assert model.edges == edges
    assert model.cuts == cuts
    assert set(model.multiplier_monomials) == set(mons_d)
    assert set(model.target_monomials) == set(mons_t)

    constructor_d_to_independent = [
        index_d[alpha] for alpha in model.multiplier_monomials
    ]
    module_oid_to_pair_key: dict[int, Pair] = {}
    pair_key_to_module_oid: dict[Pair, int] = {}
    for cut_i in range(len(cuts)):
        for module_mon_i, independent_mon_i in enumerate(constructor_d_to_independent):
            oid = int(model.multiplier_orbit_ids[cut_i, module_mon_i])
            key = pair_canonical[(cut_i, independent_mon_i)]
            old_key = module_oid_to_pair_key.setdefault(oid, key)
            old_oid = pair_key_to_module_oid.setdefault(key, oid)
            assert old_key == key and old_oid == oid
    assert len(module_oid_to_pair_key) == len(pair_keys)

    # ---- Normalization map: direct full rows and orbit representatives --------
    normalization_rows: dict[Exponent, Counter[Pair]] = {}
    for beta in mons_d:
        beta_i = index_d[beta]
        normalization_rows[beta] = Counter(
            pair_canonical[(cut_i, beta_i)] for cut_i in range(len(cuts))
        )
    for mon_orbit in mon_d_orbits:
        rows = {tuple(sorted(normalization_rows[mons_d[i]].items())) for i in mon_orbit}
        assert len(rows) == 1
        assert len({multinomial(mons_d[i]) for i in mon_orbit}) == 1

    # The constructor chooses one minimum-index representative in its own order.
    module_d_index = {alpha: i for i, alpha in enumerate(model.multiplier_monomials)}
    module_d_action = np.empty((len(GROUP), len(module_d_index)), dtype=np.int32)
    for gi, element in enumerate(GROUP):
        for alpha, i in module_d_index.items():
            module_d_action[gi, i] = module_d_index[image_exponent(alpha, element)]
    _ids, module_d_reps, _members = constructor.orbit_ids(module_d_action)
    assert len(module_d_reps) == model.multiplier_normalization.shape[0]
    for row, module_mon_i in enumerate(module_d_reps):
        beta = model.multiplier_monomials[module_mon_i]
        actual = Counter(
            {
                module_oid_to_pair_key[column]: value
                for column, value in sparse_row(model.multiplier_normalization, row).items()
            }
        )
        assert actual == normalization_rows[beta]
        assert 25 * multinomial(beta) == 25 * constructor.multinom(beta)

    # ---- Multiplier-to-target coefficient map --------------------------------
    target_multiplier_rows: dict[Exponent, Counter[Pair]] = {}
    for alpha in mons_t:
        counts: Counter[Pair] = Counter()
        for cut_i, (_cut_mask, mono) in enumerate(cuts):
            for edge_i in mono:
                u, v = edges[edge_i]
                if alpha[u] and alpha[v]:
                    beta = list(alpha)
                    beta[u] -= 1
                    beta[v] -= 1
                    counts[pair_canonical[(cut_i, index_d[tuple(beta)])]] += 1
        target_multiplier_rows[alpha] = counts
    for target_orbit in mon_t_orbits:
        rows = {
            tuple(sorted(target_multiplier_rows[mons_t[i]].items()))
            for i in target_orbit
        }
        assert len(rows) == 1
        assert len({multinomial(mons_t[i]) for i in target_orbit}) == 1

    for row, module_target_i in enumerate(model.target_representatives):
        alpha = model.target_monomials[module_target_i]
        actual = Counter(
            {
                module_oid_to_pair_key[column]: value
                for column, value in sparse_row(model.multiplier_target, row).items()
            }
        )
        assert actual == target_multiplier_rows[alpha]

    # ---- Independent parity-block/orbit and Gram coefficient reconstruction ---
    parity_blocks: dict[Exponent, list[Exponent]] = defaultdict(list)
    for beta in mons_t:
        parity_blocks[tuple(power & 1 for power in beta)].append(beta)
    parity_masks = sorted(parity_blocks)
    assert len(parity_masks) == 848

    def parity_image(mask_value: Exponent, element: GroupElement) -> Exponent:
        return image_exponent(mask_value, element)

    parity_orbits = partition(parity_masks, parity_image)
    assert len(parity_orbits) == 52
    parity_orbit_key = {
        member: min(members) for members in parity_orbits for member in members
    }
    parity_types = Counter(
        (sum(min(members)), len(parity_blocks[min(members)]), len(members))
        for members in parity_orbits
    )
    assert parity_types == Counter(
        {
            (0, 286, 1): 1,
            (2, 66, 11): 5,
            (4, 11, 11): 10,
            (4, 11, 22): 10,
            (6, 1, 11): 10,
            (6, 1, 22): 16,
        }
    )

    # Each global Gram scalar is keyed by (parity-mask orbit, stabilizer-entry
    # orbit).  Build every coefficient row in the full 8008-row system.
    gram_rows: dict[Exponent, Counter[tuple[Exponent, tuple[Exponent, Exponent]]]] = {
        alpha: Counter() for alpha in mons_t
    }
    independent_entry_keys: dict[
        Exponent, dict[tuple[int, int], tuple[Exponent, Exponent]]
    ] = {}
    independent_entry_counts: dict[Exponent, int] = {}
    transporter: dict[tuple[Exponent, Exponent], GroupElement] = {}

    for members in parity_orbits:
        rep_mask = min(members)
        basis = parity_blocks[rep_mask]
        stabilizer = [
            element
            for element in GROUP
            if image_exponent(rep_mask, element) == rep_mask
        ]
        entry_key: dict[tuple[int, int], tuple[Exponent, Exponent]] = {}
        for i, left in enumerate(basis):
            for j in range(i, len(basis)):
                right = basis[j]
                images = []
                for element in stabilizer:
                    a = image_exponent(left, element)
                    b = image_exponent(right, element)
                    images.append(tuple(sorted((a, b))))
                key = min(images)
                entry_key[(i, j)] = key
                entry_key[(j, i)] = key
        independent_entry_keys[rep_mask] = entry_key
        independent_entry_counts[rep_mask] = len(set(entry_key.values()))

        for member in members:
            candidates = [
                element
                for element in GROUP
                if image_exponent(rep_mask, element) == member
            ]
            assert candidates
            chosen = min(candidates)
            transporter[(rep_mask, member)] = chosen
            acted_basis = [image_exponent(beta, chosen) for beta in basis]
            assert set(acted_basis) == set(parity_blocks[member])
            for i, left in enumerate(acted_basis):
                for j, right in enumerate(acted_basis):
                    alpha = tuple((a + b) // 2 for a, b in zip(left, right))
                    global_key = (rep_mask, entry_key[(i, j)])
                    gram_rows[alpha][global_key] += 1

    for target_orbit in mon_t_orbits:
        rows = {tuple(sorted(gram_rows[mons_t[i]].items())) for i in target_orbit}
        assert len(rows) == 1

    # Compare each constructor representative Gram block and coefficient map.
    module_parity_orbit_keys = set()
    for gram_orbit in model.gram_orbits:
        rep_mask = min(gram_orbit.parity_members)
        module_parity_orbit_keys.add(rep_mask)
        assert set(gram_orbit.parity_members) == next(
            members for members in parity_orbits if rep_mask in members
        )
        assert gram_orbit.parity_rep == rep_mask
        assert set(gram_orbit.basis) == set(parity_blocks[rep_mask])
        assert set(gram_orbit.stabilizer) == {
            element
            for element in GROUP
            if image_exponent(rep_mask, element) == rep_mask
        }

        module_basis_pos = {
            beta: index for index, beta in enumerate(gram_orbit.basis)
        }
        module_entry_id_to_key = {}
        key_to_module_entry_id = {}
        entry_keys = independent_entry_keys[rep_mask]
        independent_basis_pos = {
            beta: index for index, beta in enumerate(parity_blocks[rep_mask])
        }
        for i, left in enumerate(gram_orbit.basis):
            for j, right in enumerate(gram_orbit.basis):
                independent_i = independent_basis_pos[left]
                independent_j = independent_basis_pos[right]
                key = entry_keys[(independent_i, independent_j)]
                oid = int(gram_orbit.entry_ids[i, j])
                assert module_entry_id_to_key.setdefault(oid, key) == key
                assert key_to_module_entry_id.setdefault(key, oid) == oid
        assert len(module_entry_id_to_key) == independent_entry_counts[rep_mask]

        for row, module_target_i in enumerate(model.target_representatives):
            alpha = model.target_monomials[module_target_i]
            expected = Counter(
                {
                    global_key[1]: value
                    for global_key, value in gram_rows[alpha].items()
                    if global_key[0] == rep_mask
                }
            )
            actual = Counter(
                {
                    module_entry_id_to_key[column]: value
                    for column, value in sparse_row(gram_orbit.coefficient_map, row).items()
                }
            )
            assert actual == expected
    assert module_parity_orbit_keys == set(independent_entry_keys)
    assert sum(independent_entry_counts.values()) == 8647

    # ---- Stable generalized face archive: maps, F1, ordering, and H -----------
    full_face_source_hash_before = sha256(FULL_FACE_SOURCE)
    full_face_data_hash_before = sha256(FULL_FACE_DATA)
    full_face_summary_hash_before = sha256(FULL_FACE_SUMMARY)
    with np.load(FULL_FACE_DATA, allow_pickle=False) as loaded_archive:
        full_archive = {name: loaded_archive[name].copy() for name in loaded_archive.files}
    full_summary = json.loads(FULL_FACE_SUMMARY.read_text(encoding="utf-8"))
    assert int(full_archive["format_version"][0]) == 1
    assert int(full_archive["q_max"][0]) == 50
    archive_points = {
        tuple(int(value) for value in row)
        for row in full_archive["equality_representatives"]
    }
    assert archive_points == logged_orbits and len(archive_points) == 439
    assert full_summary["collector_equals_symbolic_plateau"] is True
    assert full_summary["balanced_c5_colourability_pass"] == 439

    # Recompute F1 directly from the exact rays and independently rebuilt arcs.
    independent_forced_oids: set[int] = set()
    model_monomial_supports = [
        frozenset(vertex for vertex, power in enumerate(beta) if power)
        for beta in model.multiplier_monomials
    ]
    for point in archive_points:
        point_support = frozenset(i for i, value in enumerate(point) if value)
        point_products = tuple(point[u] * point[v] for u, v in edges)
        point_target = sum(point) ** 2 // 25
        for cut_i, (_cut_mask, mono_edges) in enumerate(cuts):
            cut_value = sum(point_products[edge_i] for edge_i in mono_edges)
            if cut_value == point_target:
                continue
            assert cut_value > point_target
            independent_forced_oids.update(
                int(model.multiplier_orbit_ids[cut_i, mon_i])
                for mon_i, monomial_support in enumerate(model_monomial_supports)
                if monomial_support <= point_support
            )
    archived_forced = set(int(value) for value in full_archive["forced_multiplier_orbits"])
    archived_live = set(int(value) for value in full_archive["live_multiplier_orbits"])
    assert independent_forced_oids == archived_forced
    assert len(archived_forced) == 2085 and len(archived_live) == 526
    assert archived_forced.isdisjoint(archived_live)
    assert archived_forced | archived_live == set(range(2611))
    live_order = np.asarray(sorted(archived_live), dtype=np.int32)
    assert np.array_equal(full_archive["live_multiplier_orbits"], live_order)

    # The exported live coefficient maps and both right-hand sides are exact
    # slices of the independently audited base model.
    assert_archive_csr_equals(
        full_archive,
        "normalization_live",
        model.multiplier_normalization[:, live_order],
    )
    assert_archive_csr_equals(
        full_archive,
        "target_nu_live",
        model.multiplier_target[:, live_order],
    )
    expected_target_gram = __import__("scipy.sparse", fromlist=["hstack"]).hstack(
        [orbit.coefficient_map for orbit in model.gram_orbits], format="csr"
    )
    assert_archive_csr_equals(full_archive, "target_gram", expected_target_gram)
    expected_normalization_rhs = np.asarray(
        [25 * multinomial(model.multiplier_monomials[index]) for index in module_d_reps],
        dtype=np.int64,
    )
    expected_target_rhs = np.asarray(
        [multinomial(model.target_monomials[index]) for index in model.target_representatives],
        dtype=np.int64,
    )
    assert np.array_equal(full_archive["normalization_rhs"], expected_normalization_rhs)
    assert np.array_equal(full_archive["target_rhs"], expected_target_rhs)

    expected_gram_offsets = []
    expected_gram_qdims = []
    expected_gram_masks = []
    gram_offset = 0
    for orbit in model.gram_orbits:
        expected_gram_offsets.append(gram_offset)
        qdim = int(orbit.variable.size)
        expected_gram_qdims.append(qdim)
        expected_gram_masks.append(orbit.parity_rep)
        gram_offset += qdim
    assert gram_offset == 8647
    assert np.array_equal(
        full_archive["gram_offsets"], np.asarray(expected_gram_offsets, dtype=np.int32)
    )
    assert np.array_equal(
        full_archive["gram_qdims"], np.asarray(expected_gram_qdims, dtype=np.int32)
    )
    assert np.array_equal(
        full_archive["gram_rep_masks"], np.asarray(expected_gram_masks, dtype=np.int8)
    )

    blowup_source_hash_before = sha256(BLOWUP_FACE_SOURCE)
    blowup_data_hash_before = sha256(BLOWUP_FACE_DATA)
    blowup_summary_hash_before = sha256(BLOWUP_FACE_SUMMARY)
    with np.load(BLOWUP_FACE_DATA, allow_pickle=False) as loaded_blowup:
        blowup_archive = {name: loaded_blowup[name].copy() for name in loaded_blowup.files}
    blowup_summary = json.loads(BLOWUP_FACE_SUMMARY.read_text(encoding="utf-8"))
    for key, expected in (
        ("complete_c5_blowup_supports", 132),
        ("blowup_plateau_forced_multiplier_orbits", 2085),
        ("evaluation_span_dimensions_total", 402),
        ("blowup_gram_face_rank", 6129),
        ("blowup_gram_face_nnz", 71973),
        ("blowup_gram_face_dimension", 2518),
    ):
        assert blowup_summary[key] == expected
    assert np.array_equal(blowup_archive["forced_multiplier_orbits"], full_archive["forced_multiplier_orbits"])
    assert np.array_equal(blowup_archive["live_multiplier_orbits"], full_archive["live_multiplier_orbits"])
    assert np.array_equal(blowup_archive["gram_offsets"], full_archive["gram_offsets"])
    assert np.array_equal(blowup_archive["gram_qdims"], full_archive["gram_qdims"])
    assert np.array_equal(blowup_archive["gram_rep_masks"], full_archive["gram_rep_masks"])

    full_h_shape, full_h_rows, full_h_nnz = unpack_archive_csr(full_archive, "gram_face")
    symbolic_h_shape, symbolic_h_rows, symbolic_h_nnz = unpack_archive_csr(
        blowup_archive, "gram_face"
    )
    assert full_h_shape == symbolic_h_shape == (6129, 8647)
    assert full_h_nnz == 157515 and symbolic_h_nnz == 71973
    constraint_ranks = [int(value) for value in full_archive["gram_constraint_ranks"]]
    kernel_dims = [int(value) for value in full_archive["gram_kernel_dims"]]
    face_dimensions = [int(value) for value in full_archive["gram_face_dimensions"]]
    assert sum(constraint_ranks) == 6129 and sum(kernel_dims) == 402
    assert sum(face_dimensions) == 2518
    assert all(
        rank + dimension == qdim
        for rank, dimension, qdim in zip(
            constraint_ranks, face_dimensions, expected_gram_qdims
        )
    )

    stored_symbolic_kernels: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for encoded in blowup_archive["kernel_rows_json"]:
        block_index, row = json.loads(str(encoded))
        stored_symbolic_kernels[int(block_index)].append(tuple(int(value) for value in row))

    # Independently expand the continuous balanced-blow-up plateaus in every
    # representative parity block, then compare their exact Qv=0 rowspace with
    # both the symbolic sparse H and the final finite-grid H.
    parity_members_by_rep = {min(members): members for members in parity_orbits}
    independent_prime = 1_000_003
    h_row_offset = 0
    candidate_row_counts = []
    for block_index, orbit in enumerate(model.gram_orbits):
        rep_mask = orbit.parity_rep
        basis = list(parity_blocks[rep_mask])
        assert tuple(orbit.basis) == tuple(basis)
        candidates: set[tuple[int, ...]] = set()
        for member in parity_members_by_rep[rep_mask]:
            element = next(
                group_element
                for group_element in GROUP
                if image_exponent(rep_mask, group_element) == member
            )
            acted_basis = [image_exponent(beta, element) for beta in basis]
            for classes in independent_blowups.values():
                candidates.update(
                    independent_plateau_coefficient_rows(
                        acted_basis, member, classes
                    )
                )
        candidate_row_counts.append(len(candidates))
        stored_kernels = stored_symbolic_kernels.get(block_index, [])
        assert set(stored_kernels) <= candidates
        candidate_sparse = [
            {column: value for column, value in enumerate(row) if value}
            for row in sorted(candidates)
        ]
        stored_sparse = [
            {column: value for column, value in enumerate(row) if value}
            for row in stored_kernels
        ]
        candidate_rank = len(
            sparse_independent_row_indices(candidate_sparse, independent_prime)
        )
        stored_rank = len(
            sparse_independent_row_indices(stored_sparse, independent_prime)
        )
        union_rank = len(
            sparse_independent_row_indices(
                stored_sparse + candidate_sparse, independent_prime
            )
        )
        assert candidate_rank == stored_rank == union_rank == kernel_dims[block_index]

        # Rebuild every invariant Qv=0 equation from the symbolic kernel rows.
        symbolic_equation_keys: set[tuple[tuple[int, int], ...]] = set()
        for vector in stored_kernels:
            nonzero = [(index, value) for index, value in enumerate(vector) if value]
            for matrix_row in range(len(basis)):
                coefficients: Counter[int] = Counter()
                for matrix_column, value in nonzero:
                    coefficients[
                        expected_gram_offsets[block_index]
                        + int(orbit.entry_ids[matrix_row, matrix_column])
                    ] += value
                key = tuple(sorted((column, value) for column, value in coefficients.items() if value))
                if key:
                    symbolic_equation_keys.add(key)

        block_rank = constraint_ranks[block_index]
        full_block_rows = full_h_rows[h_row_offset : h_row_offset + block_rank]
        symbolic_block_rows = symbolic_h_rows[h_row_offset : h_row_offset + block_rank]
        block_start = expected_gram_offsets[block_index]
        block_stop = block_start + expected_gram_qdims[block_index]
        assert all(
            all(block_start <= column < block_stop for column in row)
            for row in full_block_rows + symbolic_block_rows
        )
        assert {
            tuple(sorted(row.items())) for row in symbolic_block_rows
        } <= symbolic_equation_keys

        # A nonzero modular minor proves exact Q-rank.  Equality of the combined
        # modular rank checks that the denser final H and the independently
        # generated symbolic H impose the same blockwise rowspace.
        full_rank_mod = len(
            sparse_independent_row_indices(full_block_rows, independent_prime)
        )
        symbolic_rank_mod = len(
            sparse_independent_row_indices(symbolic_block_rows, independent_prime)
        )
        combined_rank_mod = len(
            sparse_independent_row_indices(
                symbolic_block_rows + full_block_rows, independent_prime
            )
        )
        assert full_rank_mod == symbolic_rank_mod == combined_rank_mod == block_rank
        h_row_offset += block_rank
    assert h_row_offset == 6129
    assert candidate_row_counts == [
        int(block["candidate_rows"]) for block in blowup_summary["per_block"]
    ]
    assert kernel_dims == [
        int(block["evaluation_span_dimension"])
        for block in blowup_summary["per_block"]
    ]
    assert constraint_ranks == [
        int(block["gram_constraint_rank"]) for block in blowup_summary["per_block"]
    ]

    # ---- Exercise the constructor's actual numerical expansion permutation ----
    rng = np.random.default_rng(23022)
    model.multiplier_variable.value = rng.integers(
        0, 1001, size=model.multiplier_variable.size
    ).astype(float)
    expected_rep_matrices: dict[Exponent, np.ndarray] = {}
    gram_value_by_global_key = {}
    for gram_orbit in model.gram_orbits:
        gram_orbit.variable.value = rng.integers(
            -1000, 1001, size=int(gram_orbit.variable.size)
        ).astype(float)
        expected_rep_matrices[gram_orbit.parity_rep] = np.asarray(
            gram_orbit.matrix.value, dtype=float
        )
        independent_basis_pos = {
            beta: index
            for index, beta in enumerate(parity_blocks[gram_orbit.parity_rep])
        }
        for i, left in enumerate(gram_orbit.basis):
            for j, right in enumerate(gram_orbit.basis):
                key = independent_entry_keys[gram_orbit.parity_rep][
                    (independent_basis_pos[left], independent_basis_pos[right])
                ]
                value = float(
                    gram_orbit.variable.value[int(gram_orbit.entry_ids[i, j])]
                )
                global_key = (gram_orbit.parity_rep, key)
                assert gram_value_by_global_key.setdefault(global_key, value) == value

    orbit_by_member = {
        member: gram_orbit
        for gram_orbit in model.gram_orbits
        for member in gram_orbit.parity_members
    }
    expanded_gram_coefficients = Counter()
    for block in constructor.parity_blocks(N, DT):
        member = tuple(power & 1 for power in block[0])
        gram_orbit = orbit_by_member[member]
        rep_matrix = expected_rep_matrices[gram_orbit.parity_rep]
        element = gram_orbit.image_elements[member]
        independent_p = [
            block.index(image_exponent(beta, element))
            for beta in gram_orbit.basis
        ]
        constructor_p = constructor.image_permutation(
            gram_orbit.basis, block, element
        ).tolist()
        assert constructor_p == independent_p
        p = independent_p
        assert sorted(p) == list(range(len(block)))
        actual = np.empty_like(rep_matrix)
        actual[np.ix_(p, p)] = rep_matrix
        for i, left in enumerate(block):
            for j, right in enumerate(block):
                alpha = tuple((a + b) // 2 for a, b in zip(left, right))
                expanded_gram_coefficients[alpha] += actual[i, j]

        # Any other transporter differs by a representative stabilizer.  The
        # tied representative matrix must therefore produce the same block.
        for alternative in GROUP:
            if image_exponent(gram_orbit.parity_rep, alternative) != member:
                continue
            q = [
                block.index(image_exponent(beta, alternative))
                for beta in gram_orbit.basis
            ]
            alternative_matrix = np.empty_like(rep_matrix)
            alternative_matrix[np.ix_(q, q)] = rep_matrix
            assert np.array_equal(alternative_matrix, actual)

    for alpha in mons_t:
        reduced_value = sum(
            coefficient * gram_value_by_global_key[key]
            for key, coefficient in gram_rows[alpha].items()
        )
        assert expanded_gram_coefficients[alpha] == reduced_value

    # ---- Independent audit of the exported numerical warm start -------------
    numeric_hash_before = sha256(NUMERIC_EXPORT)
    with NUMERIC_EXPORT.open("rb") as handle:
        certificate = pickle.load(handle)
    assert certificate["NUMERICAL_ONLY"] is True
    assert certificate["n"] == N and certificate["d"] == 2
    assert certificate["c"] == 25
    assert certificate["E"] == edges and certificate["cuts"] == cuts

    numeric_nu = certificate["nu"]
    numeric_normalization = np.zeros(len(mons_d))
    for beta_i, beta in enumerate(mons_d):
        numeric_normalization[beta_i] = sum(
            float(numeric_nu.get((cut_i, beta), 0.0))
            for cut_i in range(len(cuts))
        )
    numeric_normalization_rhs = np.asarray(
        [25 * multinomial(beta) for beta in mons_d], dtype=float
    )
    numeric_normalization_residual = float(
        np.max(np.abs(numeric_normalization - numeric_normalization_rhs))
    )

    numeric_target = np.asarray([multinomial(alpha) for alpha in mons_t], dtype=float)
    for (cut_i, beta), value in numeric_nu.items():
        for edge_i in cuts[cut_i][1]:
            u, v = edges[edge_i]
            alpha = list(beta)
            alpha[u] += 1
            alpha[v] += 1
            numeric_target[index_t[tuple(alpha)]] -= float(value)

    q_by_mask: dict[Exponent, tuple[list[Exponent], np.ndarray]] = {}
    numeric_gram = np.zeros(len(mons_t))
    minimum_eigenvalue = float("inf")
    maximum_eigenvalue = 0.0
    maximum_symmetry_error = 0.0
    negative_eigenvalue_blocks = 0
    for raw_basis, raw_matrix in certificate["Q"]:
        basis = [tuple(beta) for beta in raw_basis]
        matrix = np.asarray(raw_matrix, dtype=float)
        assert matrix.shape == (len(basis), len(basis))
        block_mask = tuple(power & 1 for power in basis[0])
        assert block_mask not in q_by_mask
        q_by_mask[block_mask] = (basis, matrix)
        symmetry_error = float(np.max(np.abs(matrix - matrix.T)))
        maximum_symmetry_error = max(maximum_symmetry_error, symmetry_error)
        symmetric = (matrix + matrix.T) / 2
        eigenvalues = (
            np.asarray([symmetric[0, 0]])
            if len(basis) == 1
            else np.linalg.eigvalsh(symmetric)
        )
        minimum_eigenvalue = min(minimum_eigenvalue, float(eigenvalues[0]))
        maximum_eigenvalue = max(maximum_eigenvalue, float(eigenvalues[-1]))
        if eigenvalues[0] < -1e-8:
            negative_eigenvalue_blocks += 1
        for i, left in enumerate(basis):
            for j, right in enumerate(basis):
                alpha = tuple((a + b) // 2 for a, b in zip(left, right))
                numeric_gram[index_t[alpha]] += matrix[i, j]
    assert set(q_by_mask) == set(parity_masks)
    numeric_identity_residual = float(np.max(np.abs(numeric_target - numeric_gram)))

    # Verify that the expanded data are exact D_22 copies, independently of
    # whether the floating iterate satisfies the cone constraints closely.
    maximum_nu_copy_error = 0.0
    for cut_i in range(len(cuts)):
        for beta_i, beta in enumerate(mons_d):
            source = float(numeric_nu.get((cut_i, beta), 0.0))
            for element in GROUP:
                image_cut = cut_image(cut_i, element)
                image_beta = image_exponent(beta, element)
                target_value = float(numeric_nu.get((image_cut, image_beta), 0.0))
                maximum_nu_copy_error = max(
                    maximum_nu_copy_error, abs(source - target_value)
                )

    maximum_q_copy_error = 0.0
    for source_mask, (source_basis, source_matrix) in q_by_mask.items():
        for element in GROUP:
            target_mask = image_exponent(source_mask, element)
            target_basis, target_matrix = q_by_mask[target_mask]
            target_position = {beta: i for i, beta in enumerate(target_basis)}
            p = [target_position[image_exponent(beta, element)] for beta in source_basis]
            maximum_q_copy_error = max(
                maximum_q_copy_error,
                float(np.max(np.abs(target_matrix[np.ix_(p, p)] - source_matrix))),
            )
    assert maximum_nu_copy_error == 0.0
    assert maximum_q_copy_error == 0.0

    # ---- Equality face forced by all induced C5 concentrations ---------------
    induced_c5s = []
    for vertices in __import__("itertools").combinations(range(N), 5):
        vertex_set = frozenset(vertices)
        cycle_edges = [
            edge_i
            for edge_i, (u, v) in enumerate(edges)
            if u in vertex_set and v in vertex_set
        ]
        cycle_degrees = Counter(
            vertex for edge_i in cycle_edges for vertex in edges[edge_i]
        )
        if len(cycle_edges) == 5 and set(cycle_degrees.values()) == {2}:
            induced_c5s.append((vertex_set, cycle_edges))
    assert len(induced_c5s) == 33

    c5_orbit_representatives = {
        min(
            tuple(sorted(image_set(vertices, element))) for element in GROUP
        )
        for vertices, _cycle_edges in induced_c5s
    }
    assert len(c5_orbit_representatives) == 3

    zero_mask = (0,) * N
    central_basis, central_matrix = q_by_mask[zero_mask]
    central_evaluation_rows = [
        [
            int(
                all(
                    power == 0
                    for vertex, power in enumerate(beta)
                    if vertex not in vertices
                )
            )
            for beta in central_basis
        ]
        for vertices, _cycle_edges in induced_c5s
    ]
    central_exact_rank = full_row_rank_mod_prime(central_evaluation_rows)
    assert central_exact_rank == 33
    central_kernel_product = central_matrix @ np.asarray(
        central_evaluation_rows, dtype=float
    ).T
    central_max_abs_qk = float(np.max(np.abs(central_kernel_product)))
    central_matrix_infinity_norm_qk = float(
        np.linalg.norm(central_kernel_product, ord=np.inf)
    )

    forced_coefficient_occurrences = 0
    forced_coefficient_keys = set()
    forced_multiplier_orbit_keys = set()
    maximum_forced_coefficient = 0.0
    maximum_c5_normalization_error = 0.0
    maximum_c5_surplus = 0.0
    maximum_c5_target_abs = 0.0
    maximum_c5_gram_match_error = 0.0
    maximum_kernel_residual = 0.0
    maximum_block_energy_abs = 0.0
    nonzero_kernel_vectors = 0
    representative_kernel_vectors = set()
    stabilizer_kernel_vector_orbits = set()

    for vertices, cycle_edges in induced_c5s:
        supported_d = [
            beta
            for beta in mons_d
            if all(power == 0 for vertex, power in enumerate(beta) if vertex not in vertices)
        ]
        assert len(supported_d) == 70
        cut_cycle_counts = [
            sum(edge_i in mono for edge_i in cycle_edges)
            for _cut_mask, mono in cuts
        ]
        assert set(cut_cycle_counts) <= {1, 3, 5} and min(cut_cycle_counts) == 1
        nu_on_c5 = []
        for cut_i, count in enumerate(cut_cycle_counts):
            value = sum(
                float(numeric_nu.get((cut_i, beta), 0.0)) for beta in supported_d
            )
            nu_on_c5.append(value)
            if count > 1:
                for beta in supported_d:
                    key = (cut_i, beta)
                    forced_coefficient_occurrences += 1
                    forced_coefficient_keys.add(key)
                    forced_multiplier_orbit_keys.add(
                        pair_canonical[(cut_i, index_d[beta])]
                    )
                    maximum_forced_coefficient = max(
                        maximum_forced_coefficient,
                        abs(float(numeric_nu.get(key, 0.0))),
                    )

        normalization_value = sum(nu_on_c5)
        surplus = sum(
            value * (count - 1)
            for value, count in zip(nu_on_c5, cut_cycle_counts)
        )
        target_value = 5**6 - sum(
            value * count for value, count in zip(nu_on_c5, cut_cycle_counts)
        )
        maximum_c5_normalization_error = max(
            maximum_c5_normalization_error, abs(normalization_value - 25 * 5**4)
        )
        maximum_c5_surplus = max(maximum_c5_surplus, abs(surplus))
        maximum_c5_target_abs = max(maximum_c5_target_abs, abs(target_value))

        gram_value = 0.0
        block_count = 0
        for member_mask, (basis, matrix) in q_by_mask.items():
            vector = np.asarray(
                [
                    1.0
                    if all(
                        power == 0
                        for vertex, power in enumerate(beta)
                        if vertex not in vertices
                    )
                    else 0.0
                    for beta in basis
                ]
            )
            if not np.any(vector):
                continue
            block_count += 1
            nonzero_kernel_vectors += 1
            gram_orbit = orbit_by_member[member_mask]
            element = gram_orbit.image_elements[member_mask]
            member_position = {beta: i for i, beta in enumerate(basis)}
            p = [
                member_position[image_exponent(beta, element)]
                for beta in gram_orbit.basis
            ]
            representative_vector = tuple(int(vector[index]) for index in p)
            representative_kernel_vectors.add(
                (gram_orbit.parity_rep, representative_vector)
            )
            representative_position = {
                beta: i for i, beta in enumerate(gram_orbit.basis)
            }
            stabilizer_images = []
            for stabilizer_element in gram_orbit.stabilizer:
                stabilizer_permutation = [
                    representative_position[image_exponent(beta, stabilizer_element)]
                    for beta in gram_orbit.basis
                ]
                transformed = [0] * len(representative_vector)
                for source_i, target_i in enumerate(stabilizer_permutation):
                    transformed[target_i] = representative_vector[source_i]
                stabilizer_images.append(tuple(transformed))
            stabilizer_kernel_vector_orbits.add(
                (gram_orbit.parity_rep, min(stabilizer_images))
            )
            image = matrix @ vector
            energy = float(vector @ image)
            gram_value += energy
            maximum_kernel_residual = max(
                maximum_kernel_residual, float(np.max(np.abs(image)))
            )
            maximum_block_energy_abs = max(maximum_block_energy_abs, abs(energy))
        assert block_count == 16
        maximum_c5_gram_match_error = max(
            maximum_c5_gram_match_error, abs(target_value - gram_value)
        )

    assert nonzero_kernel_vectors == 33 * 16
    assert len(forced_multiplier_orbit_keys) == 1147
    assert abs(
        numeric_normalization_residual
        - certificate["diagnostics"]["normalization_max_abs_residual"]
    ) < 1e-10
    assert abs(
        numeric_identity_residual
        - certificate["diagnostics"]["target_max_abs_residual"]
    ) < 1e-10
    assert numeric_hash_before == sha256(NUMERIC_EXPORT)

    # ---- Independent build-only audit of the exact-face scaffold ------------
    face_hash_before = sha256(FACE_CONSTRUCTOR)
    face_constructor = import_face_constructor()
    face = face_constructor.build_face_model()
    assert face.margin.value is None
    assert all(variable.value is None for variable in face.problem.variables())
    assert face.problem.is_dcp()
    assert face.base.edges == edges and face.base.cuts == cuts
    assert np.array_equal(face.base.multiplier_orbit_ids, model.multiplier_orbit_ids)
    assert {
        tuple(cycle) for cycle in face.cycles
    } == {
        tuple(sorted(vertices)) for vertices, _cycle_edges in induced_c5s
    }

    expected_forced_oids = sorted(
        pair_key_to_module_oid[key] for key in forced_multiplier_orbit_keys
    )
    assert face.forced_zero_multiplier_orbits == expected_forced_oids
    assert len(expected_forced_oids) == 1147

    expected_rows_by_rep: dict[Exponent, list[list[int]]] = defaultdict(list)
    for rep_mask, row in representative_kernel_vectors:
        expected_rows_by_rep[rep_mask].append(list(row))

    face_rank_total = 0
    face_complement_total = 0
    face_rank_by_order = Counter()
    face_kernel_blocks = 0
    face_margin_blocks = 0
    for face_orbit, face_data in zip(face.base.gram_orbits, face.orbit_data):
        rep_mask = face_orbit.parity_rep
        expected_rows = expected_rows_by_rep[rep_mask]
        expected_rank = full_row_rank_mod_prime(expected_rows)
        assert len(face_data.kernel) == expected_rank
        face_rank_total += expected_rank
        face_rank_by_order[len(face_orbit.basis)] += expected_rank
        complement_order = len(face_orbit.basis) - expected_rank
        face_complement_total += complement_order
        face_kernel_blocks += int(expected_rank > 0)
        face_margin_blocks += int(len(face_orbit.basis) > 1 and complement_order > 0)

        rational = lambda value: sy.Rational(value.numerator, value.denominator)
        projector = sy.Matrix(
            [[rational(value) for value in row] for row in face_data.projector]
        )
        order = len(face_orbit.basis)
        assert projector == projector.T
        if expected_rank:
            kernel = sy.Matrix(
                [[rational(value) for value in row] for row in face_data.kernel]
            )
            gram = kernel * kernel.T
            gram_inverse = gram.inv()
            assert gram * gram_inverse == sy.eye(expected_rank)
            formula = sy.eye(order) - kernel.T * gram_inverse * kernel
            assert projector == formula
            assert kernel * projector == sy.zeros(expected_rank, order)
            for expected_row in expected_rows:
                assert sy.Matrix([expected_row]) * projector == sy.zeros(1, order)
        else:
            assert projector == sy.eye(order)
        assert sy.trace(projector) == complement_order

    assert face_rank_total == 74
    assert face_rank_by_order == Counter({286: 33, 66: 30, 11: 11})
    assert face_complement_total == 788
    assert face_margin_blocks == 26
    assert len(face.problem.constraints) == (
        len(face.base.problem.constraints) + 1 + face_kernel_blocks + face_margin_blocks
    )
    assert face_hash_before == sha256(FACE_CONSTRUCTOR)

    # ---- No-solve synthetic audit of face exporter formulas -----------------
    exporter_hash_before = sha256(FACE_EXPORTER)
    exporter = import_face_exporter()
    exporter.validate_output_paths(exporter.DEFAULT_OUTPUT, exporter.DEFAULT_REPORT)
    guard_cases = [
        (exporter.RAW_NUMERIC_PATH, exporter.DEFAULT_REPORT),
        (exporter.DEFAULT_OUTPUT, exporter.RAW_NUMERIC_PATH),
        (exporter.FACE_PATH, exporter.DEFAULT_REPORT),
        (exporter.DEFAULT_OUTPUT, exporter.FACE_PATH),
        (FACE_EXPORTER, exporter.DEFAULT_REPORT),
        (exporter.DEFAULT_OUTPUT, FACE_EXPORTER),
        (exporter.DEFAULT_OUTPUT, exporter.DEFAULT_OUTPUT),
    ]
    guard_rejections = 0
    for output_path, report_path in guard_cases:
        try:
            exporter.validate_output_paths(output_path, report_path)
        except SystemExit:
            guard_rejections += 1
        else:
            raise AssertionError(f"unsafe exporter paths accepted: {output_path}, {report_path}")
    assert guard_rejections == len(guard_cases)

    synthetic_rng = np.random.default_rng(23023)
    synthetic_nu = synthetic_rng.integers(
        0, 1001, size=face.base.multiplier_variable.size
    ).astype(float)
    face.base.multiplier_variable.value = synthetic_nu
    for orbit in face.base.gram_orbits:
        orbit.variable.value = synthetic_rng.integers(
            -1000, 1001, size=int(orbit.variable.size)
        ).astype(float)
    face.margin.value = 0.125
    face.problem._status = "synthetic-no-solve"
    face.problem._solver_stats = SimpleNamespace(
        solver_name="NO_SOLVER",
        num_iters=0,
        setup_time=0.0,
        solve_time=0.0,
    )

    synthetic_normalization_rhs = np.asarray(
        [
            25 * multinomial(face.base.multiplier_monomials[index])
            for index in module_d_reps
        ],
        dtype=float,
    )
    independent_normalization_residual = float(
        np.max(
            np.abs(
                face.base.multiplier_normalization @ synthetic_nu
                - synthetic_normalization_rhs
            )
        )
    )
    synthetic_target_value = face.base.multiplier_target @ synthetic_nu
    for orbit in face.base.gram_orbits:
        synthetic_target_value = (
            synthetic_target_value
            + orbit.coefficient_map @ np.asarray(orbit.variable.value, dtype=float)
        )
    synthetic_target_rhs = np.asarray(
        [
            multinomial(face.base.target_monomials[index])
            for index in face.base.target_representatives
        ],
        dtype=float,
    )
    independent_target_residual = float(
        np.max(np.abs(synthetic_target_value - synthetic_target_rhs))
    )

    synthetic_diagnostics = exporter.post_solve_diagnostics(face)
    assert synthetic_diagnostics["status"] == "synthetic-no-solve"
    assert synthetic_diagnostics["solver_name"] == "NO_SOLVER"
    assert synthetic_diagnostics["normalization_max_abs_residual"] == (
        independent_normalization_residual
    )
    assert synthetic_diagnostics["target_max_abs_residual"] == (
        independent_target_residual
    )
    assert synthetic_diagnostics["normalization_max_abs_residual"] == float(
        np.max(np.abs(face.base.problem.constraints[0].violation()))
    )
    assert synthetic_diagnostics["target_max_abs_residual"] == float(
        np.max(np.abs(face.base.problem.constraints[-1].violation()))
    )
    assert np.array_equal(
        synthetic_diagnostics["reduced_multiplier_values"], synthetic_nu
    )

    synthetic_payload = exporter.expand_payload(
        face_constructor, face, synthetic_diagnostics
    )
    assert synthetic_payload["NUMERICAL_ONLY"] is True
    assert synthetic_payload["c"] == Fraction(25, 1)
    assert synthetic_payload["E"] == edges and synthetic_payload["cuts"] == cuts
    assert synthetic_payload["face"]["cycles"] == face.cycles
    assert synthetic_payload["face"]["forced_zero_multiplier_orbits"] == (
        face.forced_zero_multiplier_orbits
    )
    for stored, orbit, data in zip(
        synthetic_payload["face"]["gram_orbits"],
        face.base.gram_orbits,
        face.orbit_data,
    ):
        assert stored["parity_rep"] == orbit.parity_rep
        assert stored["parity_members"] == orbit.parity_members
        assert stored["kernel"] == data.kernel and stored["projector"] == data.projector
        assert all(isinstance(value, Fraction) for row in stored["kernel"] for value in row)
        assert all(isinstance(value, Fraction) for row in stored["projector"] for value in row)

    payload_q_by_mask = {
        tuple(power & 1 for power in block[0]): (block, np.asarray(matrix, dtype=float))
        for block, matrix in synthetic_payload["Q"]
    }
    assert set(payload_q_by_mask) == set(parity_masks)
    face_orbit_by_member = {
        member: orbit
        for orbit in face.base.gram_orbits
        for member in orbit.parity_members
    }
    for member_mask, (block, expanded_matrix) in payload_q_by_mask.items():
        orbit = face_orbit_by_member[member_mask]
        representative_matrix = np.asarray(orbit.matrix.value, dtype=float)
        element = orbit.image_elements[member_mask]
        target_position = {beta: i for i, beta in enumerate(block)}
        p = [
            target_position[image_exponent(beta, element)] for beta in orbit.basis
        ]
        independent_expansion = np.empty_like(representative_matrix)
        independent_expansion[np.ix_(p, p)] = representative_matrix
        assert np.array_equal(expanded_matrix, independent_expansion)

    for cut_i in range(len(cuts)):
        for monomial_i, beta in enumerate(face.base.multiplier_monomials):
            expected = float(
                synthetic_nu[face.base.multiplier_orbit_ids[cut_i, monomial_i]]
            )
            assert float(synthetic_payload["nu"].get((cut_i, beta), 0.0)) == expected
    assert exporter_hash_before == sha256(FACE_EXPORTER)

    assert full_face_source_hash_before == sha256(FULL_FACE_SOURCE)
    assert full_face_data_hash_before == sha256(FULL_FACE_DATA)
    assert full_face_summary_hash_before == sha256(FULL_FACE_SUMMARY)
    assert blowup_source_hash_before == sha256(BLOWUP_FACE_SOURCE)
    assert blowup_data_hash_before == sha256(BLOWUP_FACE_DATA)
    assert blowup_summary_hash_before == sha256(BLOWUP_FACE_SUMMARY)
    hash_after = sha256(CONSTRUCTOR)
    assert hash_before == hash_after, "constructor changed during the audit"

    print(f"constructor_sha256={hash_before}")
    print(
        "graph=Gamma_11 vertices=11 edges=22 degree=4 triangle_free=True "
        "group_order=22"
    )
    print(
        "cuts=56 cut_orbits=6 cut_orbit_sizes="
        + repr(sorted(map(len, cut_orbits)))
    )
    print(
        f"degree4_monomials={len(mons_d)} degree4_orbits={len(mon_d_orbits)} "
        f"pair_orbits={len(pair_keys)}"
    )
    print(
        f"degree6_monomials={len(mons_t)} degree6_orbits={len(mon_t_orbits)} "
        f"parity_blocks={len(parity_masks)} parity_block_orbits={len(parity_orbits)}"
    )
    print(f"gram_orbit_scalars={sum(independent_entry_counts.values())}")
    print("normalization_map=EXACT_MATCH")
    print("multiplier_target_map=EXACT_MATCH")
    print("gram_target_map=EXACT_MATCH")
    print("representative_equations=LOSSLESS_FOR_D22_INVARIANT_DATA")
    print("stabilizer_tying=EXACT_PARAMETERIZATION")
    print("numeric_expansion_permutation=EXACT_MATCH_AND_TRANSPORTER_INDEPENDENT")
    print(f"numeric_export_sha256={numeric_hash_before}")
    print(
        f"numeric_full_normalization_residual={numeric_normalization_residual:.12e} "
        f"numeric_full_identity_residual={numeric_identity_residual:.12e}"
    )
    print(
        f"numeric_min_eigenvalue={minimum_eigenvalue:.12e} "
        f"numeric_max_eigenvalue={maximum_eigenvalue:.12e} "
        f"negative_eigenvalue_blocks_lt_minus_1e-8={negative_eigenvalue_blocks} "
        f"maximum_symmetry_error={maximum_symmetry_error:.12e}"
    )
    print(
        f"numeric_nu_D22_copy_error={maximum_nu_copy_error:.12e} "
        f"numeric_Q_D22_copy_error={maximum_q_copy_error:.12e}"
    )
    print(
        f"induced_C5s=33 C5_orbits=3 forced_coefficient_occurrences="
        f"{forced_coefficient_occurrences} forced_unique_coefficients="
        f"{len(forced_coefficient_keys)} max_forced_coefficient="
        f"{maximum_forced_coefficient:.12e} forced_multiplier_orbits="
        f"{len(forced_multiplier_orbit_keys)}/2611"
    )
    print(
        f"central_kernel_exact_rank={central_exact_rank} "
        f"central_max_abs_QK={central_max_abs_qk:.12e} "
        f"central_matrix_inf_norm_QK={central_matrix_infinity_norm_qk:.12e} "
        f"all_block_representative_kernel_vectors={len(representative_kernel_vectors)} "
        f"mod_stabilizer={len(stabilizer_kernel_vector_orbits)}"
    )
    print(
        f"C5_max_normalization_error={maximum_c5_normalization_error:.12e} "
        f"C5_max_surplus={maximum_c5_surplus:.12e} "
        f"C5_max_target_abs={maximum_c5_target_abs:.12e} "
        f"C5_max_gram_match_error={maximum_c5_gram_match_error:.12e} "
        f"C5_all_blocks_max_entry_Qv={maximum_kernel_residual:.12e} "
        f"C5_max_block_energy_abs={maximum_block_energy_abs:.12e}"
    )
    print(f"face_constructor_sha256={face_hash_before}")
    print(
        f"face_F1_exact_match={len(expected_forced_oids)}/2611 "
        f"face_F2_rank_total={face_rank_total} "
        f"face_rank_by_order={dict(face_rank_by_order)} "
        f"face_complement_total={face_complement_total} "
        f"face_kernel_blocks={face_kernel_blocks} "
        f"face_margin_blocks={face_margin_blocks} exact_projectors=PASS"
    )
    print("FACE_BUILD_AUDIT_ONLY: no solve launched")
    print(
        f"equality_collector_source_sha256={collector_source_hash_before} "
        f"equality_collector_exe_sha256={collector_exe_hash_before} "
        f"equality_collector_log_sha256={collector_log_hash_before}"
    )
    print(
        "equality_collector_raw_composition_crosscheck="
        f"q5:{len(exhaustive_orbits_by_q[5])},q10:{len(exhaustive_orbits_by_q[10])} "
        "nonC5_witness_tight_arcs=19 PASS"
    )
    print("equality_collector_q5_q50_emitted_rays=439 all_rays_exact=PASS")
    print(
        f"complete_C5_blowup_supports={len(independent_blowups)} "
        f"support_sizes={dict(sorted(blowup_support_sizes.items()))} "
        f"all_439_rays_balanced_blowups=PASS ray_support_sizes="
        f"{dict(sorted(equality_ray_support_sizes.items()))}"
    )
    print(
        f"full_face_source_sha256={full_face_source_hash_before} "
        f"full_face_data_sha256={full_face_data_hash_before} "
        f"full_face_summary_sha256={full_face_summary_hash_before}"
    )
    print(
        "full_face_maps=EXACT_MATCH F1=2085 live=526 "
        "normalization=56x526 target_nu=392x526 target_gram=392x8647"
    )
    print(
        f"full_face_H={full_h_shape[0]}x{full_h_shape[1]} nnz={full_h_nnz} "
        f"rank_mod_{independent_prime}=6129"
    )
    print(
        f"symbolic_blowup_H={symbolic_h_shape[0]}x{symbolic_h_shape[1]} "
        f"nnz={symbolic_h_nnz} same_blockwise_rowspace=PASS "
        "symbolic_kernel_rank=402"
    )
    print("EQUALITY_COLLECTOR_AUDIT_ONLY: no SDP solve launched")
    print(f"face_exporter_sha256={exporter_hash_before}")
    print(
        f"face_export_path_guards={guard_rejections}/{len(guard_cases)} "
        f"original_equality_indices=PASS synthetic_residuals=PASS "
        f"expanded_gram_permutation=PASS exact_face_metadata=PASS"
    )
    print("FACE_EXPORT_SYNTHETIC_AUDIT_ONLY: no solver or file write")
    print("NUMERICAL_EXPORT_AUDIT_ONLY: exact rational reconstruction still required")
    print("AUDIT_PASS")


if __name__ == "__main__":
    main()
