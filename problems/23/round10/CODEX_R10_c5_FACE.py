"""Exact C5 equality-face reduction for the Gamma_11 D22 degree-4 certificate.

This is an independent reconstruction of the fixed R10 certificate model:

    sum_S nu_S = 25 L^4,
    T = L^6 - sum_S nu_S q_S,
    T(y^2) is SOS,

where S ranges over the 56 cyclic-interval cuts of Gamma_11 and each nu_S
is a homogeneous degree-4 polynomial with coefficientwise nonnegative
coefficients.

For every induced C5 C, evaluate at x = 1_C.  Every cut has k_S(C) in
{1,3,5} monochromatic C5 edges.  The normalization gives

    T(1_C) = -sum_S nu_S(1_C) (k_S(C)-1).

Both sides of the certificate force this value to be zero.  Consequently:

F1. If k_S(C)>1, every coefficient nu_{S,beta} with supp(beta) subset C
    is zero.
F2. In every parity Gram block Q_p, Q_p v_{p,C}=0, where v_{p,C} has a 1
    at a degree-6 y-monomial beta exactly when supp(beta) subset C.

The script rebuilds Gamma_11, its cuts, its induced C5s, all D22 actions,
the reduced multiplier variables, and the reduced Gram variables without
importing CODEX_R10_g11_d22_sdp.py.  It exports an exact integer sparse
linear system that can be added to that model without changing c, degree,
cut family, or cone:

    nu[forced_nu_ids] = 0,
    H @ concatenate(Qorbit_variables) = 0.

It also exports the exact normalization and target coefficient maps after
removing the forced multiplier variables.  All saved matrix entries and
right-hand sides are integers, hence exact rationals.

No SDP is solved here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Callable, Iterable, Sequence, TypeVar

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
N = 11
MULTIPLIER_DEGREE = 4
TARGET_DEGREE = 6
C_FIXED = 25
GROUP = tuple((sign, shift) for sign in (1, -1) for shift in range(N))
PRIME = 2_000_003

Exponent = tuple[int, ...]
GroupElement = tuple[int, int]
T = TypeVar("T")


def monomials(number_variables: int, degree: int) -> list[Exponent]:
    """All homogeneous exponent tuples, rebuilt directly."""
    output: list[Exponent] = []

    def visit(index: int, remaining: int, prefix: list[int]) -> None:
        if index == number_variables - 1:
            output.append(tuple(prefix + [remaining]))
            return
        for value in range(remaining + 1):
            visit(index + 1, remaining - value, prefix + [value])

    visit(0, degree, [])
    return output


def multinomial(exponent: Exponent) -> int:
    result = math.factorial(sum(exponent))
    for value in exponent:
        result //= math.factorial(value)
    return result


def gamma_11_edges() -> list[tuple[int, int]]:
    """Gamma_11: circular distance strictly greater than 1/3."""
    return [
        (u, v)
        for u in range(N)
        for v in range(u + 1, N)
        if 3 * min(v - u, N - (v - u)) > N
    ]


def vertex_image(vertex: int, element: GroupElement) -> int:
    sign, shift = element
    return (sign * vertex + shift) % N


def exponent_image(exponent: Exponent, element: GroupElement) -> Exponent:
    image = [0] * N
    for vertex, power in enumerate(exponent):
        image[vertex_image(vertex, element)] = power
    return tuple(image)


def subset_image(subset: Iterable[int], element: GroupElement) -> tuple[int, ...]:
    return tuple(sorted(vertex_image(vertex, element) for vertex in subset))


def canonical_cut_mask(side: Iterable[int]) -> int:
    side_set = set(side)
    if 0 in side_set:
        side_set = set(range(N)) - side_set
    return sum(1 << (vertex - 1) for vertex in side_set)


def cut_side(mask: int) -> frozenset[int]:
    return frozenset(
        vertex for vertex in range(1, N) if (mask >> (vertex - 1)) & 1
    )


def interval_cuts(
    edges: Sequence[tuple[int, int]],
) -> list[tuple[int, frozenset[int]]]:
    masks = {canonical_cut_mask(())}
    for length in range(1, 6):
        for start in range(N):
            masks.add(
                canonical_cut_mask(
                    (start + offset) % N for offset in range(length)
                )
            )
    assert len(masks) == 56
    output = []
    for mask in sorted(masks):
        side = cut_side(mask)
        mono = frozenset(
            edge_index
            for edge_index, (u, v) in enumerate(edges)
            if (u in side) == (v in side)
        )
        output.append((mask, mono))
    return output


def induced_c5s(edges: Sequence[tuple[int, int]]) -> list[tuple[int, ...]]:
    edge_set = {tuple(sorted(edge)) for edge in edges}
    output = []
    for vertices in combinations(range(N), 5):
        degrees = [
            sum(tuple(sorted((u, v))) in edge_set for v in vertices if v != u)
            for u in vertices
        ]
        if degrees == [2, 2, 2, 2, 2]:
            output.append(vertices)
    return output


def orbit_partition(
    objects: Sequence[T], image: Callable[[T, GroupElement], T]
) -> tuple[list[int], list[int], list[list[int]], list[list[int]]]:
    """IDs, representative indices, member indices, and action table."""
    index = {item: i for i, item in enumerate(objects)}
    action = [
        [index[image(item, element)] for item in objects] for element in GROUP
    ]
    ids = [-1] * len(objects)
    representatives: list[int] = []
    members: list[list[int]] = []
    for seed in range(len(objects)):
        if ids[seed] >= 0:
            continue
        orbit = sorted({action[gi][seed] for gi in range(len(GROUP))})
        orbit_id = len(representatives)
        representatives.append(min(orbit))
        members.append(orbit)
        for member in orbit:
            assert ids[member] in (-1, orbit_id)
            ids[member] = orbit_id
    assert min(ids, default=0) >= 0
    return ids, representatives, members, action


def cut_action_table(
    cuts: Sequence[tuple[int, frozenset[int]]],
) -> list[list[int]]:
    index = {mask: cut_index for cut_index, (mask, _mono) in enumerate(cuts)}
    output = []
    for element in GROUP:
        row = []
        for mask, _mono in cuts:
            image_mask = canonical_cut_mask(
                vertex_image(vertex, element) for vertex in cut_side(mask)
            )
            assert image_mask in index
            row.append(index[image_mask])
        output.append(row)
    return output


def pair_orbits(
    cut_action: Sequence[Sequence[int]],
    monomial_action: Sequence[Sequence[int]],
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    ids = np.full(
        (len(cut_action[0]), len(monomial_action[0])), -1, dtype=np.int32
    )
    representatives: list[tuple[int, int]] = []
    for cut_index in range(ids.shape[0]):
        for monomial_index in range(ids.shape[1]):
            if ids[cut_index, monomial_index] >= 0:
                continue
            orbit_id = len(representatives)
            representatives.append((cut_index, monomial_index))
            orbit = {
                (
                    cut_action[group_index][cut_index],
                    monomial_action[group_index][monomial_index],
                )
                for group_index in range(len(GROUP))
            }
            for image_cut, image_monomial in orbit:
                assert ids[image_cut, image_monomial] in (-1, orbit_id)
                ids[image_cut, image_monomial] = orbit_id
    assert np.all(ids >= 0)
    return ids, representatives


def support(exponent: Exponent) -> frozenset[int]:
    return frozenset(i for i, power in enumerate(exponent) if power)


def parity(exponent: Exponent) -> Exponent:
    return tuple(power & 1 for power in exponent)


def parity_blocks(
    number_variables: int, degree: int
) -> tuple[list[Exponent], dict[Exponent, list[Exponent]]]:
    blocks: dict[Exponent, list[Exponent]] = {}
    for exponent in monomials(number_variables, degree):
        blocks.setdefault(parity(exponent), []).append(exponent)
    masks = sorted(blocks)
    return masks, blocks


def stabilizer(mask: Exponent) -> list[GroupElement]:
    return [
        element for element in GROUP if exponent_image(mask, element) == mask
    ]


def entry_orbits(
    basis: Sequence[Exponent], group: Sequence[GroupElement]
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    index = {item: i for i, item in enumerate(basis)}
    permutations = [
        [index[exponent_image(item, element)] for item in basis]
        for element in group
    ]
    ids = np.full((len(basis), len(basis)), -1, dtype=np.int32)
    representatives: list[tuple[int, int]] = []
    for i in range(len(basis)):
        for j in range(i, len(basis)):
            if ids[i, j] >= 0:
                continue
            orbit_id = len(representatives)
            representatives.append((i, j))
            orbit = {
                tuple(sorted((permutation[i], permutation[j])))
                for permutation in permutations
            }
            for row, column in orbit:
                assert ids[row, column] in (-1, orbit_id)
                ids[row, column] = ids[column, row] = orbit_id
    assert np.all(ids >= 0)
    return ids, representatives


def independent_zero_one_rows(
    candidates: Sequence[Sequence[int]],
) -> tuple[list[list[int]], list[int]]:
    """Select an exact Q-row basis while retaining original zero-one rows."""
    echelon: list[list[Fraction]] = []
    pivots: list[int] = []
    selected: list[list[int]] = []
    selected_indices: list[int] = []
    for candidate_index, candidate in enumerate(candidates):
        row = [Fraction(value) for value in candidate]
        for base, pivot in zip(echelon, pivots):
            if row[pivot]:
                factor = row[pivot] / base[pivot]
                row = [a - factor * b for a, b in zip(row, base)]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        scale = row[pivot]
        row = [value / scale for value in row]
        echelon.append(row)
        pivots.append(pivot)
        selected.append(list(candidate))
        selected_indices.append(candidate_index)
    return selected, selected_indices


def coordinates_in_echelon_span(
    vector: Sequence[Fraction],
    echelon: Sequence[Sequence[Fraction]],
    pivots: Sequence[int],
) -> list[Fraction]:
    remainder = list(vector)
    coefficients: list[Fraction] = []
    for base, pivot in zip(echelon, pivots):
        coefficient = remainder[pivot] / base[pivot]
        coefficients.append(coefficient)
        if coefficient:
            remainder = [
                value - coefficient * base_value
                for value, base_value in zip(remainder, base)
            ]
    assert all(value == 0 for value in remainder)
    return coefficients


def echelon_basis(
    rows: Sequence[Sequence[int]],
) -> tuple[list[list[Fraction]], list[int]]:
    output: list[list[Fraction]] = []
    pivots: list[int] = []
    for source in rows:
        row = [Fraction(value) for value in source]
        for base, pivot in zip(output, pivots):
            if row[pivot]:
                factor = row[pivot] / base[pivot]
                row = [a - factor * b for a, b in zip(row, base)]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        scale = row[pivot]
        output.append([value / scale for value in row])
        pivots.append(pivot)
    return output, pivots


def transform_row(
    row: Sequence[int | Fraction],
    basis: Sequence[Exponent],
    element: GroupElement,
) -> list[Fraction]:
    index = {item: i for i, item in enumerate(basis)}
    output = [Fraction(0)] * len(basis)
    for i, item in enumerate(basis):
        output[index[exponent_image(item, element)]] = Fraction(row[i])
    return output


def compose(left: GroupElement, right: GroupElement) -> GroupElement:
    """left after right."""
    left_sign, left_shift = left
    right_sign, right_shift = right
    return (
        left_sign * right_sign,
        (left_sign * right_shift + left_shift) % N,
    )


def invariant_symmetric_dimension(
    basis: Sequence[Exponent],
    kernel_rows: Sequence[Sequence[int]],
    group: Sequence[GroupElement],
) -> tuple[int, int, dict[GroupElement, int]]:
    """Exact dimension of invariant symmetric forms on kernel complement."""
    echelon, pivots = echelon_basis(kernel_rows)
    character_kernel: dict[GroupElement, int] = {}
    character_basis: dict[GroupElement, int] = {}
    for element in group:
        trace = Fraction(0)
        for row_index, row in enumerate(echelon):
            transformed = transform_row(row, basis, element)
            coefficients = coordinates_in_echelon_span(
                transformed, echelon, pivots
            )
            trace += coefficients[row_index]
        assert trace.denominator == 1
        character_kernel[element] = int(trace)
        character_basis[element] = sum(
            exponent_image(item, element) == item for item in basis
        )

    character_complement = {
        element: character_basis[element] - character_kernel[element]
        for element in group
    }
    numerator = 0
    for element in group:
        square = compose(element, element)
        numerator += (
            character_complement[element] ** 2
            + character_complement[square]
        )
    denominator = 2 * len(group)
    assert numerator % denominator == 0
    face_dimension = numerator // denominator

    original_numerator = sum(
        character_basis[element] ** 2
        + character_basis[compose(element, element)]
        for element in group
    )
    assert original_numerator % denominator == 0
    original_dimension = original_numerator // denominator
    return original_dimension, face_dimension, character_kernel


def gram_kernel_equations(
    entry_ids: np.ndarray, kernel_rows: Sequence[Sequence[int]]
) -> list[dict[int, int]]:
    equations: list[dict[int, int]] = []
    for vector in kernel_rows:
        nonzero = [j for j, value in enumerate(vector) if value]
        for i in range(entry_ids.shape[0]):
            counts: Counter[int] = Counter(
                int(entry_ids[i, j]) for j in nonzero
            )
            if counts:
                equations.append(dict(counts))
    unique: dict[tuple[tuple[int, int], ...], dict[int, int]] = {}
    for equation in equations:
        key = tuple(sorted(equation.items()))
        unique.setdefault(key, equation)
    return list(unique.values())


def independent_rows_mod_prime(
    rows: Sequence[dict[int, int]], expected_rank: int, prime: int
) -> list[int]:
    """Select original integer rows independent mod p; expected rank proves Q-rank."""
    pivot_rows: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row_index, source in enumerate(rows):
        row = {
            column: value % prime
            for column, value in source.items()
            if value % prime
        }
        while row:
            pivot = min(row)
            if pivot not in pivot_rows:
                inverse = pow(row[pivot], prime - 2, prime)
                row = {
                    column: (value * inverse) % prime
                    for column, value in row.items()
                    if (value * inverse) % prime
                }
                pivot_rows[pivot] = row
                selected.append(row_index)
                break
            factor = row[pivot]
            base = pivot_rows[pivot]
            for column, value in base.items():
                new_value = (row.get(column, 0) - factor * value) % prime
                if new_value:
                    row[column] = new_value
                else:
                    row.pop(column, None)
    if len(selected) != expected_rank:
        raise AssertionError(
            f"mod-{prime} row rank {len(selected)} != exact character rank "
            f"{expected_rank}"
        )
    return selected


def csr_from_dict_rows(
    rows: Sequence[dict[int, int]], number_columns: int
) -> sp.csr_matrix:
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[int] = []
    for row_index, row in enumerate(rows):
        for column, value in sorted(row.items()):
            row_indices.append(row_index)
            column_indices.append(column)
            values.append(value)
    return sp.csr_matrix(
        (np.asarray(values, dtype=np.int64), (row_indices, column_indices)),
        shape=(len(rows), number_columns),
        dtype=np.int64,
    )


def pack_csr(payload: dict[str, np.ndarray], name: str, matrix: sp.csr_matrix) -> None:
    matrix = matrix.tocsr()
    payload[f"{name}_data"] = matrix.data.astype(np.int64)
    payload[f"{name}_indices"] = matrix.indices.astype(np.int32)
    payload[f"{name}_indptr"] = matrix.indptr.astype(np.int64)
    payload[f"{name}_shape"] = np.asarray(matrix.shape, dtype=np.int64)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1 << 20)
            if not chunk:
                return digest.hexdigest().upper()
            digest.update(chunk)


def build() -> tuple[dict[str, object], dict[str, np.ndarray]]:
    edges = gamma_11_edges()
    assert len(edges) == 22
    edge_set = set(edges)
    for element in GROUP:
        assert {
            tuple(
                sorted(
                    (vertex_image(u, element), vertex_image(v, element))
                )
            )
            for u, v in edges
        } == edge_set

    cuts = interval_cuts(edges)
    c5s = induced_c5s(edges)
    assert len(c5s) == 33
    c5_ids, c5_reps, c5_members, _c5_action = orbit_partition(
        c5s, subset_image
    )
    del c5_ids
    assert sorted(len(members) for members in c5_members) == [11, 11, 11]

    multiplier_monomials = monomials(N, MULTIPLIER_DEGREE)
    target_monomials = monomials(N, TARGET_DEGREE)
    multiplier_ids, multiplier_reps, multiplier_members, multiplier_action = (
        orbit_partition(multiplier_monomials, exponent_image)
    )
    del multiplier_ids, multiplier_members
    target_ids, target_reps, target_members, target_action = orbit_partition(
        target_monomials, exponent_image
    )
    del target_ids, target_members
    cut_action = cut_action_table(cuts)
    multiplier_pair_ids, multiplier_pair_reps = pair_orbits(
        cut_action, multiplier_action
    )
    number_multiplier_orbits = len(multiplier_pair_reps)
    assert number_multiplier_orbits == 2611

    edge_index = {edge: index for index, edge in enumerate(edges)}
    c5_edge_indices = []
    for cycle in c5s:
        cycle_set = set(cycle)
        indices = frozenset(
            index
            for index, (u, v) in enumerate(edges)
            if u in cycle_set and v in cycle_set
        )
        assert len(indices) == 5
        c5_edge_indices.append(indices)

    forced_full = np.zeros(
        (len(cuts), len(multiplier_monomials)), dtype=bool
    )
    cut_c5_k = np.zeros((len(cuts), len(c5s)), dtype=np.int8)
    for cut_index, (_mask, mono) in enumerate(cuts):
        for cycle_index, cycle_edges in enumerate(c5_edge_indices):
            k_value = len(mono & cycle_edges)
            assert k_value in (1, 3, 5)
            cut_c5_k[cut_index, cycle_index] = k_value
            if k_value > 1:
                cycle_set = set(c5s[cycle_index])
                for monomial_index, exponent in enumerate(multiplier_monomials):
                    if support(exponent) <= cycle_set:
                        forced_full[cut_index, monomial_index] = True

    forced_multiplier_orbits = sorted(
        {
            int(multiplier_pair_ids[cut_index, monomial_index])
            for cut_index in range(len(cuts))
            for monomial_index in range(len(multiplier_monomials))
            if forced_full[cut_index, monomial_index]
        }
    )
    for cut_index in range(len(cuts)):
        for monomial_index in range(len(multiplier_monomials)):
            if (
                int(multiplier_pair_ids[cut_index, monomial_index])
                in forced_multiplier_orbits
            ):
                assert forced_full[cut_index, monomial_index]
    live_multiplier_orbits = sorted(
        set(range(number_multiplier_orbits)) - set(forced_multiplier_orbits)
    )

    # Exact normalization map on D22 representatives.
    norm_rows: list[int] = []
    norm_cols: list[int] = []
    norm_values: list[int] = []
    norm_rhs: list[int] = []
    for row, monomial_index in enumerate(multiplier_reps):
        counts: Counter[int] = Counter(
            int(multiplier_pair_ids[cut_index, monomial_index])
            for cut_index in range(len(cuts))
        )
        for column, value in counts.items():
            norm_rows.append(row)
            norm_cols.append(column)
            norm_values.append(value)
        norm_rhs.append(
            C_FIXED * multinomial(multiplier_monomials[monomial_index])
        )
    normalization = sp.csr_matrix(
        (
            np.asarray(norm_values, dtype=np.int64),
            (norm_rows, norm_cols),
        ),
        shape=(len(multiplier_reps), number_multiplier_orbits),
        dtype=np.int64,
    )

    target_index = {item: index for index, item in enumerate(target_monomials)}
    multiplier_index = {
        item: index for index, item in enumerate(multiplier_monomials)
    }
    target_rep_to_row = {
        target_monomials[index]: row for row, index in enumerate(target_reps)
    }
    target_nu_rows: list[int] = []
    target_nu_cols: list[int] = []
    target_nu_values: list[int] = []
    for row, target_index_rep in enumerate(target_reps):
        alpha = target_monomials[target_index_rep]
        counts: Counter[int] = Counter()
        for cut_index, (_mask, mono) in enumerate(cuts):
            for edge_id in mono:
                u, v = edges[edge_id]
                if alpha[u] == 0 or alpha[v] == 0:
                    continue
                beta = list(alpha)
                beta[u] -= 1
                beta[v] -= 1
                monomial_index = multiplier_index[tuple(beta)]
                counts[
                    int(multiplier_pair_ids[cut_index, monomial_index])
                ] += 1
        for column, value in counts.items():
            target_nu_rows.append(row)
            target_nu_cols.append(column)
            target_nu_values.append(value)
    target_nu = sp.csr_matrix(
        (
            np.asarray(target_nu_values, dtype=np.int64),
            (target_nu_rows, target_nu_cols),
        ),
        shape=(len(target_reps), number_multiplier_orbits),
        dtype=np.int64,
    )

    parity_masks, blocks = parity_blocks(N, TARGET_DEGREE)
    parity_ids, parity_reps, parity_members, parity_action = orbit_partition(
        parity_masks, exponent_image
    )
    del parity_ids, parity_action

    gram_target_rows: list[int] = []
    gram_target_cols: list[int] = []
    gram_target_values: list[int] = []
    face_rows_global: list[dict[int, int]] = []
    gram_offsets: list[int] = []
    gram_qdims: list[int] = []
    gram_orders: list[int] = []
    gram_kernel_dims: list[int] = []
    gram_candidate_counts: list[int] = []
    gram_raw_equation_counts: list[int] = []
    gram_unique_equation_counts: list[int] = []
    gram_face_dimensions: list[int] = []
    gram_constraint_ranks: list[int] = []
    gram_stabilizer_orders: list[int] = []
    gram_rep_masks: list[list[int]] = []
    gram_entry_reps_flat: list[tuple[int, int, int]] = []
    kernel_cycle_indices_flat: list[tuple[int, int]] = []
    q_offset = 0

    for parity_orbit_id, parity_rep_index in enumerate(parity_reps):
        rep = parity_masks[parity_rep_index]
        basis = blocks[rep]
        group = stabilizer(rep)
        entry_ids, entry_reps = entry_orbits(basis, group)
        qdim = len(entry_reps)

        candidate_rows: list[list[int]] = []
        candidate_cycle_indices: list[int] = []
        rep_support = support(rep)
        for cycle_index, cycle in enumerate(c5s):
            cycle_set = set(cycle)
            if not rep_support <= cycle_set:
                continue
            row = [
                int(support(exponent) <= cycle_set) for exponent in basis
            ]
            assert any(row)
            candidate_rows.append(row)
            candidate_cycle_indices.append(cycle_index)
        kernel_rows, selected_candidate_indices = independent_zero_one_rows(
            candidate_rows
        )
        for local_kernel_index, candidate_index in enumerate(
            selected_candidate_indices
        ):
            kernel_cycle_indices_flat.append(
                (
                    parity_orbit_id,
                    candidate_cycle_indices[candidate_index],
                )
            )

        original_dimension, face_dimension, _character_kernel = (
            invariant_symmetric_dimension(basis, kernel_rows, group)
        )
        assert original_dimension == qdim
        exact_constraint_rank = qdim - face_dimension

        raw_equations = gram_kernel_equations(entry_ids, kernel_rows)
        selected_equations = independent_rows_mod_prime(
            raw_equations, exact_constraint_rank, PRIME
        )
        for equation_index in selected_equations:
            face_rows_global.append(
                {
                    q_offset + column: value
                    for column, value in raw_equations[equation_index].items()
                }
            )

        # Rebuild each orbit member's coefficient contribution to target reps.
        member_masks = [parity_masks[index] for index in parity_members[parity_orbit_id]]
        image_elements = {
            member: next(
                element
                for element in GROUP
                if exponent_image(rep, element) == member
            )
            for member in member_masks
        }
        counts: Counter[tuple[int, int]] = Counter()
        for member in member_masks:
            acted_basis = [
                exponent_image(item, image_elements[member]) for item in basis
            ]
            assert set(acted_basis) == set(blocks[member])
            for i, left in enumerate(acted_basis):
                for j, right in enumerate(acted_basis):
                    alpha = tuple(
                        (left[v] + right[v]) // 2 for v in range(N)
                    )
                    row = target_rep_to_row.get(alpha)
                    if row is not None:
                        counts[(row, int(entry_ids[i, j]))] += 1
        for (row, local_column), value in counts.items():
            gram_target_rows.append(row)
            gram_target_cols.append(q_offset + local_column)
            gram_target_values.append(value)

        gram_offsets.append(q_offset)
        gram_qdims.append(qdim)
        gram_orders.append(len(basis))
        gram_kernel_dims.append(len(kernel_rows))
        gram_candidate_counts.append(len(candidate_rows))
        gram_raw_equation_counts.append(len(kernel_rows) * len(basis))
        gram_unique_equation_counts.append(len(raw_equations))
        gram_face_dimensions.append(face_dimension)
        gram_constraint_ranks.append(exact_constraint_rank)
        gram_stabilizer_orders.append(len(group))
        gram_rep_masks.append(list(rep))
        gram_entry_reps_flat.extend(
            (parity_orbit_id, i, j) for i, j in entry_reps
        )
        q_offset += qdim

    number_gram_orbits = q_offset
    assert number_gram_orbits == 8647
    gram_target = sp.csr_matrix(
        (
            np.asarray(gram_target_values, dtype=np.int64),
            (gram_target_rows, gram_target_cols),
        ),
        shape=(len(target_reps), number_gram_orbits),
        dtype=np.int64,
    )
    gram_face = csr_from_dict_rows(face_rows_global, number_gram_orbits)
    assert gram_face.shape[0] == sum(gram_constraint_ranks)

    live = np.asarray(live_multiplier_orbits, dtype=np.int32)
    normalization_live = normalization[:, live]
    target_nu_live = target_nu[:, live]
    target_rhs = np.asarray(
        [multinomial(target_monomials[index]) for index in target_reps],
        dtype=np.int64,
    )

    summary: dict[str, object] = {
        "graph": "Gamma_11=And(4)",
        "vertices": N,
        "edges": len(edges),
        "group_order": len(GROUP),
        "cuts": len(cuts),
        "induced_c5s": len(c5s),
        "induced_c5_orbit_sizes": [
            len(members) for members in c5_members
        ],
        "induced_c5_representatives": [
            list(c5s[index]) for index in c5_reps
        ],
        "cut_c5_k_distribution": {
            str(value): int(np.sum(cut_c5_k == value))
            for value in (1, 3, 5)
        },
        "multiplier_degree": MULTIPLIER_DEGREE,
        "multiplier_monomials": len(multiplier_monomials),
        "multiplier_full_entries": int(forced_full.size),
        "forced_multiplier_full_entries": int(forced_full.sum()),
        "multiplier_orbits": number_multiplier_orbits,
        "forced_multiplier_orbits": len(forced_multiplier_orbits),
        "live_multiplier_orbits": len(live_multiplier_orbits),
        "normalization_equations": normalization_live.shape[0],
        "target_degree": TARGET_DEGREE,
        "target_monomials": len(target_monomials),
        "target_orbit_equations": len(target_reps),
        "parity_blocks_full": len(parity_masks),
        "parity_block_orbits": len(parity_reps),
        "gram_orbit_scalars": number_gram_orbits,
        "gram_kernel_candidate_vectors": sum(gram_candidate_counts),
        "gram_kernel_independent_vectors": sum(gram_kernel_dims),
        "gram_kernel_raw_equations": sum(gram_raw_equation_counts),
        "gram_kernel_unique_equations": sum(gram_unique_equation_counts),
        "gram_kernel_independent_equations": int(gram_face.shape[0]),
        "gram_face_orbit_dimensions": sum(gram_face_dimensions),
        "total_face_linear_variables": (
            len(live_multiplier_orbits) + sum(gram_face_dimensions)
        ),
        "remaining_certificate_equations": (
            normalization_live.shape[0] + len(target_reps)
        ),
        "prime_exact_row_basis": PRIME,
        "psd_order_counts": dict(Counter(gram_orders)),
        "kernel_dimension_by_psd_order": {
            str(order): int(
                sum(
                    kernel_dimension
                    for block_order, kernel_dimension in zip(
                        gram_orders, gram_kernel_dims
                    )
                    if block_order == order
                )
            )
            for order in sorted(set(gram_orders), reverse=True)
        },
        "face_dimension_by_psd_order": {
            str(order): int(
                sum(
                    face_dimension
                    for block_order, face_dimension in zip(
                        gram_orders, gram_face_dimensions
                    )
                    if block_order == order
                )
            )
            for order in sorted(set(gram_orders), reverse=True)
        },
    }

    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "n": np.asarray([N], dtype=np.int32),
        "c_fixed": np.asarray([C_FIXED], dtype=np.int32),
        "multiplier_degree": np.asarray(
            [MULTIPLIER_DEGREE], dtype=np.int32
        ),
        "target_degree": np.asarray([TARGET_DEGREE], dtype=np.int32),
        "edges": np.asarray(edges, dtype=np.int32),
        "cut_masks": np.asarray([mask for mask, _mono in cuts], dtype=np.int32),
        "c5s": np.asarray(c5s, dtype=np.int32),
        "c5_representative_indices": np.asarray(c5_reps, dtype=np.int32),
        "cut_c5_k": cut_c5_k,
        "forced_multiplier_orbits": np.asarray(
            forced_multiplier_orbits, dtype=np.int32
        ),
        "live_multiplier_orbits": live,
        "multiplier_orbit_representatives": np.asarray(
            multiplier_pair_reps, dtype=np.int32
        ),
        "normalization_rhs": np.asarray(norm_rhs, dtype=np.int64),
        "target_rhs": target_rhs,
        "gram_rep_masks": np.asarray(gram_rep_masks, dtype=np.int8),
        "gram_offsets": np.asarray(gram_offsets, dtype=np.int32),
        "gram_qdims": np.asarray(gram_qdims, dtype=np.int32),
        "gram_orders": np.asarray(gram_orders, dtype=np.int32),
        "gram_kernel_dims": np.asarray(gram_kernel_dims, dtype=np.int32),
        "gram_kernel_candidate_counts": np.asarray(
            gram_candidate_counts, dtype=np.int32
        ),
        "gram_face_dimensions": np.asarray(
            gram_face_dimensions, dtype=np.int32
        ),
        "gram_constraint_ranks": np.asarray(
            gram_constraint_ranks, dtype=np.int32
        ),
        "gram_stabilizer_orders": np.asarray(
            gram_stabilizer_orders, dtype=np.int32
        ),
        "gram_entry_orbit_representatives": np.asarray(
            gram_entry_reps_flat, dtype=np.int32
        ),
        "kernel_cycle_indices": np.asarray(
            kernel_cycle_indices_flat, dtype=np.int32
        ).reshape((-1, 2)),
    }
    pack_csr(payload, "normalization_live", normalization_live)
    pack_csr(payload, "target_nu_live", target_nu_live)
    pack_csr(payload, "target_gram", gram_target)
    pack_csr(payload, "gram_face", gram_face)
    return summary, payload


def write_report(path: Path, summary: dict[str, object], data_name: str) -> None:
    text = f"""# Exact induced-C5 face for the Gamma_11 D22 certificate

## Scope

This file concerns only the registered fixed `c=25`, degree-4 multiplier,
56 cyclic-interval-cut certificate.  It does not establish feasibility and
does not claim `ARCBOUND_Gamma_11 <= L^2/25`.

## Exact derivation

Let `C` be any induced 5-cycle and put `x=1_C`, so `L(x)=5`.  For a cut `S`,
let `k_S(C)` be the number of its monochromatic edges on `C`.  Odd-cycle
parity gives `k_S(C) in {{1,3,5}}`.  The multiplier normalization and target
identity give

`T(1_C) = 5^6 - sum_S nu_S(1_C) k_S(C)
          = -sum_S nu_S(1_C)(k_S(C)-1)`.

Every `nu_S(1_C)` is nonnegative, while the SOS condition gives `T(1_C)>=0`.
Thus equality holds term by term.  If `k_S(C)>1`, then `nu_S(1_C)=0`; because
`nu_S` has nonnegative coefficients, every coefficient indexed by a
degree-4 monomial whose support lies in `C` must vanish.

Also `T(y^2)=sum_p z_p(y)^T Q_p z_p(y)=0` at `y=1_C`.  Each summand is
nonnegative, hence `Q_p v_(p,C)=0`, where the coordinate at a degree-6
monomial `beta` is `1` iff `supp(beta) subset C`, and `0` otherwise.  Sign
choices on `C` change this vector only by a common sign inside a parity block,
so they add no further kernel vectors.

## Independently rebuilt counts

```text
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Exact sparse reduction

`{data_name}` contains integer CSR matrices:

- `normalization_live`: the 56 normalization-orbit equations after deleting
  the forced multiplier orbit columns;
- `target_nu_live`: the multiplier contribution to the 392 target-orbit
  equations after the same deletion;
- `target_gram`: the Gram contribution to those 392 equations;
- `gram_face`: an exact independent row basis of the representative-block
  equations `Q_p v_(p,C)=0`.

The variable order is `nu[live_multiplier_orbits]` followed by the 52 Gram
orbit-variable vectors concatenated in `gram_offsets` order.  The exact
system is

```text
normalization_live * nu_live = normalization_rhs
target_nu_live * nu_live + target_gram * q = target_rhs
gram_face * q = 0
```

with `nu_live >= 0`, `nu[forced_multiplier_orbits]=0`, and the original 52
representative PSD constraints unchanged.  The Gram-face rows are selected
from integer equations by modular elimination.  Their rank is exact, not
heuristic: the invariant symmetric-form character formula supplies the
rational upper bound block by block, and the displayed modular pivots reach
that bound, furnishing a nonzero integer minor.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=HERE / "CODEX_R10_c5_FACE_data.npz",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=HERE / "CODEX_R10_c5_FACE_REPORT.md",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=HERE / "CODEX_R10_c5_FACE_summary.json",
    )
    args = parser.parse_args()

    summary, payload = build()
    np.savez_compressed(args.data, **payload)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_report(args.report, summary, args.data.name)

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"DATA={args.data.resolve()}")
    print(f"REPORT={args.report.resolve()}")
    print(f"SUMMARY={args.summary.resolve()}")
    print(f"SHA256_SCRIPT={sha256(Path(__file__))}")
    print(f"SHA256_DATA={sha256(args.data)}")
    print(f"SHA256_REPORT={sha256(args.report)}")
    print(f"SHA256_SUMMARY={sha256(args.summary)}")
    print("EXACT_FACE_ONLY: no SDP run and no theorem claim")


if __name__ == "__main__":
    main()
