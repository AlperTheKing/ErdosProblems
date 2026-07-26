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
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
CONSTRUCTOR = HERE / "CODEX_R10_g11_d22_sdp.py"
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


def import_constructor():
    spec = importlib.util.spec_from_file_location("r10_d22_constructor_audited", CONSTRUCTOR)
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
    print("AUDIT_PASS")


if __name__ == "__main__":
    main()
