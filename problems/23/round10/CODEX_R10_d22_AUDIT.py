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
import math
import pickle
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable

import numpy as np
import sympy as sy


HERE = Path(__file__).resolve().parent
CONSTRUCTOR = HERE / "CODEX_R10_g11_d22_sdp.py"
FACE_CONSTRUCTOR = HERE / "CODEX_R10_g11_d22_face.py"
FACE_EXPORTER = HERE / "CODEX_R10_g11_d22_face_export.py"
NUMERIC_EXPORT = HERE / "CODEX_R10_g11_d22_numeric.pkl"
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
