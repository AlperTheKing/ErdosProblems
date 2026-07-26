"""Exact balanced-C5-blow-up face for the Gamma_11 degree-4 certificate.

This script performs no optimization.  It:

1. enumerates every vertex support U for which Gamma_11[U] is a complete
   blow-up of C5 with five nonempty classes;
2. quotients the resulting class maps by Aut(C5) and the supports by D22;
3. derives every multiplier coefficient forced to vanish by those plateaus;
4. derives, in exact integer/rational algebra, the complete degree-0..3
   evaluation span in each representative parity block; and
5. computes the corresponding exact invariant-Gram face codimension.

The output concerns only the balanced complete-C5-blow-up plateaus.  It does
not claim that these are the complete equality set of ARCBOUND_Gamma_11.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence, TypeVar

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
N = 11
MULTIPLIER_DEGREE = 4
TARGET_DEGREE = 6
GROUP = tuple((sign, shift) for sign in (1, -1) for shift in range(N))
PRIME = 2_000_003
CLAUDE_Q10 = (2, 1, 1, 0, 2, 0, 1, 1, 2, 0, 0)

Exponent = tuple[int, ...]
GroupElement = tuple[int, int]
Partition = tuple[tuple[int, ...], ...]
T = TypeVar("T")


def monomials(number_variables: int, degree: int) -> list[Exponent]:
    output: list[Exponent] = []

    def visit(index: int, remaining: int, prefix: list[int]) -> None:
        if index == number_variables - 1:
            output.append(tuple(prefix + [remaining]))
            return
        for value in range(remaining + 1):
            visit(index + 1, remaining - value, prefix + [value])

    visit(0, degree, [])
    return output


def gamma_11_edges() -> list[tuple[int, int]]:
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
    return [
        (
            mask,
            frozenset(
                edge_index
                for edge_index, (u, v) in enumerate(edges)
                if (u in cut_side(mask)) == (v in cut_side(mask))
            ),
        )
        for mask in sorted(masks)
    ]


def canonical_cycle_order(classes: Sequence[Sequence[int]]) -> Partition:
    """Canonicalize an ordered C5 class tuple modulo its dihedral group."""
    ordered = tuple(tuple(sorted(part)) for part in classes)
    candidates = []
    for shift in range(5):
        candidates.append(
            tuple(ordered[(shift + offset) % 5] for offset in range(5))
        )
        candidates.append(
            tuple(ordered[(shift - offset) % 5] for offset in range(5))
        )
    return min(candidates)


def complete_c5_blowup_partition(
    vertices: Iterable[int], edges: Sequence[tuple[int, int]]
) -> Partition | None:
    """Return the unique five-class map modulo Aut(C5), if it exists."""
    support = frozenset(vertices)
    if len(support) < 5:
        return None
    adjacency = {vertex: set() for vertex in support}
    for u, v in edges:
        if u in support and v in support:
            adjacency[u].add(v)
            adjacency[v].add(u)

    twin_groups: dict[frozenset[int], list[int]] = defaultdict(list)
    for vertex in sorted(support):
        twin_groups[frozenset(adjacency[vertex])].append(vertex)
    if len(twin_groups) != 5:
        return None
    classes = [tuple(group) for group in twin_groups.values()]

    quotient = [[False] * 5 for _ in range(5)]
    for i in range(5):
        for j in range(i + 1, 5):
            edge_bits = {
                tuple(sorted((u, v))) in set(edges)
                for u in classes[i]
                for v in classes[j]
            }
            if len(edge_bits) != 1:
                return None
            quotient[i][j] = quotient[j][i] = edge_bits.pop()
    if any(sum(row) != 2 for row in quotient):
        return None

    order = [0]
    previous = -1
    current = 0
    for _ in range(4):
        choices = [
            j
            for j in range(5)
            if quotient[current][j] and j != previous
        ]
        if len(order) == 1:
            next_class = min(choices)
        else:
            choices = [j for j in choices if j not in order]
            if len(choices) != 1:
                return None
            next_class = choices[0]
        order.append(next_class)
        previous, current = current, next_class
    if not quotient[order[-1]][order[0]]:
        return None
    return canonical_cycle_order([classes[index] for index in order])


def partition_image(partition: Partition, element: GroupElement) -> Partition:
    return canonical_cycle_order(
        [
            tuple(sorted(vertex_image(vertex, element) for vertex in part))
            for part in partition
        ]
    )


def enumerate_blowups(edges: Sequence[tuple[int, int]]) -> list[Partition]:
    output: list[Partition] = []
    for mask in range(1 << N):
        if mask.bit_count() < 5:
            continue
        vertices = [vertex for vertex in range(N) if (mask >> vertex) & 1]
        partition = complete_c5_blowup_partition(vertices, edges)
        if partition is not None:
            output.append(partition)
    assert len({tuple(sorted(sum(partition, ()))) for partition in output}) == len(
        output
    )
    return sorted(output)


def partition_orbits(partitions: Sequence[Partition]) -> list[list[int]]:
    index = {partition: i for i, partition in enumerate(partitions)}
    unseen = set(range(len(partitions)))
    output: list[list[int]] = []
    while unseen:
        seed = min(unseen)
        orbit = sorted(
            {
                index[partition_image(partitions[seed], element)]
                for element in GROUP
            }
        )
        output.append(orbit)
        unseen.difference_update(orbit)
    return output


def class_sums(partition: Partition, weights: Sequence[int]) -> tuple[int, ...]:
    return tuple(sum(weights[vertex] for vertex in part) for part in partition)


def cut_is_identically_tight(
    partition: Partition, side: frozenset[int]
) -> bool:
    """Test q_S=1 identically on the class-sum-one plateau.

    Write t_i for the mass of class i on the chosen side.  If a class is
    unsplit, t_i is the constant 0 or 1; otherwise it is a free variable.
    The restricted polynomial is

        q_S - 1 = 4 - 2 sum_i t_i + 2 sum_i t_i t_{i+1}.
    """
    split = [
        bool(set(part) & side) and bool(set(part) - side) for part in partition
    ]
    variable_index = {
        class_index: index
        for index, class_index in enumerate(
            i for i, is_split in enumerate(split) if is_split
        )
    }
    number_variables = len(variable_index)
    zero = (0,) * number_variables
    polynomial: Counter[tuple[int, ...]] = Counter({zero: 4})

    def affine_t(class_index: int) -> dict[tuple[int, ...], int]:
        if class_index in variable_index:
            exponent = [0] * number_variables
            exponent[variable_index[class_index]] = 1
            return {tuple(exponent): 1}
        return {zero: int(all(vertex in side for vertex in partition[class_index]))}

    terms = [affine_t(i) for i in range(5)]
    for term in terms:
        for exponent, coefficient in term.items():
            polynomial[exponent] -= 2 * coefficient
    for i in range(5):
        for left_exp, left_coefficient in terms[i].items():
            for right_exp, right_coefficient in terms[(i + 1) % 5].items():
                exponent = tuple(
                    left_exp[j] + right_exp[j] for j in range(number_variables)
                )
                polynomial[exponent] += 2 * left_coefficient * right_coefficient
    return all(value == 0 for value in polynomial.values())


def orbit_partition(
    objects: Sequence[T], image
) -> tuple[list[int], list[int], list[list[int]], list[list[int]]]:
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
    assert all(value >= 0 for value in ids)
    return ids, representatives, members, action


def cut_action_table(
    cuts: Sequence[tuple[int, frozenset[int]]],
) -> list[list[int]]:
    index = {mask: i for i, (mask, _mono) in enumerate(cuts)}
    output = []
    for element in GROUP:
        row = []
        for mask, _mono in cuts:
            image_side = {
                vertex_image(vertex, element) for vertex in cut_side(mask)
            }
            row.append(index[canonical_cut_mask(image_side)])
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


def polynomial_multiply(
    left: dict[tuple[int, ...], int],
    right: dict[tuple[int, ...], int],
) -> dict[tuple[int, ...], int]:
    output: Counter[tuple[int, ...]] = Counter()
    for left_exp, left_coefficient in left.items():
        for right_exp, right_coefficient in right.items():
            exponent = tuple(
                a + b for a, b in zip(left_exp, right_exp)
            )
            output[exponent] += left_coefficient * right_coefficient
    return {key: value for key, value in output.items() if value}


def restricted_monomial_polynomial(
    gamma: Exponent, partition: Partition
) -> dict[tuple[int, ...], int]:
    """Substitute one class pivot x_p=1-sum(other x) in x^gamma."""
    vertices = set(sum(partition, ()))
    if not support(gamma) <= vertices:
        return {}
    pivots = [part[-1] for part in partition]
    free_vertices = [
        vertex
        for part, pivot in zip(partition, pivots)
        for vertex in part
        if vertex != pivot
    ]
    free_index = {vertex: index for index, vertex in enumerate(free_vertices)}
    zero = (0,) * len(free_vertices)
    polynomial: dict[tuple[int, ...], int] = {zero: 1}
    for vertex, power in enumerate(gamma):
        if power == 0:
            continue
        if vertex in free_index:
            exponent = [0] * len(free_vertices)
            exponent[free_index[vertex]] = power
            polynomial = polynomial_multiply(
                polynomial, {tuple(exponent): 1}
            )
            continue
        class_index = next(
            i for i, pivot in enumerate(pivots) if pivot == vertex
        )
        affine: dict[tuple[int, ...], int] = {zero: 1}
        for free_vertex in partition[class_index][:-1]:
            exponent = [0] * len(free_vertices)
            exponent[free_index[free_vertex]] = 1
            affine[tuple(exponent)] = -1
        for _ in range(power):
            polynomial = polynomial_multiply(polynomial, affine)
    return polynomial


def plateau_coefficient_rows(
    basis: Sequence[Exponent],
    parity_mask: Exponent,
    partition: Partition,
) -> list[tuple[int, ...]]:
    """Integer basis candidates spanning all plateau evaluations."""
    if not support(parity_mask) <= set(sum(partition, ())):
        return []
    coefficient_rows: dict[tuple[int, ...], list[int]] = {}
    for column, beta in enumerate(basis):
        gamma = tuple(
            (beta[i] - parity_mask[i]) // 2 for i in range(N)
        )
        assert all(value >= 0 for value in gamma)
        for exponent, coefficient in restricted_monomial_polynomial(
            gamma, partition
        ).items():
            if exponent not in coefficient_rows:
                coefficient_rows[exponent] = [0] * len(basis)
            coefficient_rows[exponent][column] = coefficient
    return sorted(
        {
            tuple(row)
            for row in coefficient_rows.values()
            if any(row)
        }
    )


def exact_echelon_basis(
    candidates: Iterable[Sequence[int | Fraction]],
) -> tuple[list[list[Fraction]], list[int], list[tuple[int, ...]]]:
    """Exact Q-row basis; retained originals are integer candidate rows."""
    echelon: list[list[Fraction]] = []
    pivots: list[int] = []
    originals: list[tuple[int, ...]] = []
    for source in candidates:
        original = tuple(int(value) for value in source)
        row = [Fraction(value) for value in original]
        for base, pivot in zip(echelon, pivots):
            if row[pivot]:
                factor = row[pivot]
                row = [
                    value - factor * base_value
                    for value, base_value in zip(row, base)
                ]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        scale = row[pivot]
        row = [value / scale for value in row]
        for old_index in range(len(echelon)):
            if echelon[old_index][pivot]:
                factor = echelon[old_index][pivot]
                echelon[old_index] = [
                    value - factor * row_value
                    for value, row_value in zip(echelon[old_index], row)
                ]
        insert = next(
            (i for i, old_pivot in enumerate(pivots) if old_pivot > pivot),
            len(pivots),
        )
        echelon.insert(insert, row)
        pivots.insert(insert, pivot)
        originals.insert(insert, original)
    return echelon, pivots, originals


def coordinates_in_span(
    vector: Sequence[int | Fraction],
    echelon: Sequence[Sequence[Fraction]],
    pivots: Sequence[int],
) -> list[Fraction]:
    remainder = [Fraction(value) for value in vector]
    coefficients = []
    for base, pivot in zip(echelon, pivots):
        coefficient = remainder[pivot]
        coefficients.append(coefficient)
        if coefficient:
            remainder = [
                value - coefficient * base_value
                for value, base_value in zip(remainder, base)
            ]
    assert all(value == 0 for value in remainder)
    return coefficients


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
    left_sign, left_shift = left
    right_sign, right_shift = right
    return (
        left_sign * right_sign,
        (left_sign * right_shift + left_shift) % N,
    )


def invariant_face_dimension(
    basis: Sequence[Exponent],
    kernel_echelon: Sequence[Sequence[Fraction]],
    kernel_pivots: Sequence[int],
    group: Sequence[GroupElement],
) -> tuple[int, int]:
    character_kernel: dict[GroupElement, int] = {}
    character_basis: dict[GroupElement, int] = {}
    for element in group:
        trace = Fraction(0)
        for row_index, row in enumerate(kernel_echelon):
            transformed = transform_row(row, basis, element)
            coefficients = coordinates_in_span(
                transformed, kernel_echelon, kernel_pivots
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
    denominator = 2 * len(group)
    original_numerator = sum(
        character_basis[element] ** 2
        + character_basis[compose(element, element)]
        for element in group
    )
    face_numerator = sum(
        character_complement[element] ** 2
        + character_complement[compose(element, element)]
        for element in group
    )
    assert original_numerator % denominator == 0
    assert face_numerator % denominator == 0
    return original_numerator // denominator, face_numerator // denominator


def gram_kernel_equations(
    entry_ids: np.ndarray, kernel_rows: Sequence[Sequence[int]]
) -> list[dict[int, int]]:
    equations: list[dict[int, int]] = []
    for vector in kernel_rows:
        nonzero = [
            (index, int(value))
            for index, value in enumerate(vector)
            if value
        ]
        for i in range(entry_ids.shape[0]):
            row: Counter[int] = Counter()
            for j, coefficient in nonzero:
                row[int(entry_ids[i, j])] += coefficient
            if row:
                equations.append(dict(row))
    unique = {}
    for equation in equations:
        key = tuple(sorted((column, value) for column, value in equation.items() if value))
        if key:
            unique.setdefault(key, equation)
    return list(unique.values())


def modular_rank(rows: Sequence[dict[int, int]], columns: int, prime: int) -> int:
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
                new_value = (row.get(column, 0) - factor * value) % prime
                if new_value:
                    row[column] = new_value
                else:
                    row.pop(column, None)
    assert all(0 <= pivot < columns for pivot in pivots)
    return len(pivots)


def independent_rows_mod_prime(
    rows: Sequence[dict[int, int]], columns: int, prime: int
) -> list[int]:
    """Select original integer rows independent over F_p."""
    pivots: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row_index, source in enumerate(rows):
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
                selected.append(row_index)
                break
            factor = row[pivot]
            for column, value in pivots[pivot].items():
                new_value = (row.get(column, 0) - factor * value) % prime
                if new_value:
                    row[column] = new_value
                else:
                    row.pop(column, None)
    assert all(0 <= pivot < columns for pivot in pivots)
    return selected


def csr_from_dict_rows(
    rows: Sequence[dict[int, int]], columns: int
) -> sp.csr_matrix:
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[int] = []
    for row_index, row in enumerate(rows):
        for column, value in sorted(row.items()):
            if value:
                row_indices.append(row_index)
                column_indices.append(column)
                values.append(value)
    return sp.csr_matrix(
        (
            np.asarray(values, dtype=np.int64),
            (row_indices, column_indices),
        ),
        shape=(len(rows), columns),
        dtype=np.int64,
    )


def pack_csr(
    payload: dict[str, np.ndarray], name: str, matrix: sp.csr_matrix
) -> None:
    matrix = matrix.tocsr().astype(np.int64)
    payload[f"{name}_data"] = matrix.data
    payload[f"{name}_indices"] = matrix.indices.astype(np.int32)
    payload[f"{name}_indptr"] = matrix.indptr.astype(np.int64)
    payload[f"{name}_shape"] = np.asarray(matrix.shape, dtype=np.int64)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


def build() -> tuple[dict[str, object], dict[str, np.ndarray]]:
    edges = gamma_11_edges()
    edge_set = set(edges)
    assert len(edges) == 22
    for element in GROUP:
        assert {
            tuple(sorted((vertex_image(u, element), vertex_image(v, element))))
            for u, v in edges
        } == edge_set

    cuts = interval_cuts(edges)
    partitions = enumerate_blowups(edges)
    partition_groups = partition_orbits(partitions)
    size_distribution = Counter(
        len(sum(partition, ())) for partition in partitions
    )
    orbit_size_distribution = Counter(len(orbit) for orbit in partition_groups)
    representatives = [partitions[orbit[0]] for orbit in partition_groups]

    q10_support = tuple(i for i, value in enumerate(CLAUDE_Q10) if value)
    q10_partition = complete_c5_blowup_partition(q10_support, edges)
    assert q10_partition is not None
    q10_sums = class_sums(q10_partition, CLAUDE_Q10)
    assert q10_sums == (2, 2, 2, 2, 2)
    assert q10_partition in partitions

    multiplier_monomials = monomials(N, MULTIPLIER_DEGREE)
    _, _, _, multiplier_action = orbit_partition(
        multiplier_monomials, exponent_image
    )
    cut_action = cut_action_table(cuts)
    multiplier_pair_ids, multiplier_pair_reps = pair_orbits(
        cut_action, multiplier_action
    )
    assert len(multiplier_pair_reps) == 2611

    forced_blowup = set()
    forced_c5 = set()
    identically_tight_pairs = 0
    nonidentically_tight_pairs = 0
    for partition in partitions:
        vertices = set(sum(partition, ()))
        supported_monomials = [
            index
            for index, exponent in enumerate(multiplier_monomials)
            if support(exponent) <= vertices
        ]
        for cut_index, (mask, _mono) in enumerate(cuts):
            tight = cut_is_identically_tight(partition, cut_side(mask))
            if tight:
                identically_tight_pairs += 1
                continue
            nonidentically_tight_pairs += 1
            target = forced_c5 if len(vertices) == 5 else forced_blowup
            target.update(
                int(multiplier_pair_ids[cut_index, monomial_index])
                for monomial_index in supported_monomials
            )
            forced_blowup.update(
                int(multiplier_pair_ids[cut_index, monomial_index])
                for monomial_index in supported_monomials
            )
    # Recompute the size-five baseline separately because forced_blowup already
    # includes every plateau.
    forced_c5 = set()
    for partition in partitions:
        vertices = set(sum(partition, ()))
        if len(vertices) != 5:
            continue
        supported_monomials = [
            index
            for index, exponent in enumerate(multiplier_monomials)
            if support(exponent) <= vertices
        ]
        for cut_index, (mask, _mono) in enumerate(cuts):
            if cut_is_identically_tight(partition, cut_side(mask)):
                continue
            forced_c5.update(
                int(multiplier_pair_ids[cut_index, monomial_index])
                for monomial_index in supported_monomials
            )
    assert len(forced_c5) == 1147
    assert forced_c5 <= forced_blowup

    parity_masks, blocks = parity_blocks(N, TARGET_DEGREE)
    _, parity_reps, parity_members, _ = orbit_partition(
        parity_masks, exponent_image
    )
    total_gram_scalars = 0
    total_face_dimension = 0
    total_constraint_rank = 0
    total_kernel_dimension = 0
    per_block = []
    kernel_rows_flat: list[tuple[int, tuple[int, ...]]] = []
    gram_offsets: list[int] = []
    gram_qdims: list[int] = []
    gram_rep_masks: list[Exponent] = []
    gram_entry_reps_flat: list[tuple[int, int, int]] = []
    gram_face_rows: list[dict[int, int]] = []
    gram_offset = 0

    for parity_orbit_id, representative_index in enumerate(parity_reps):
        representative = parity_masks[representative_index]
        basis = blocks[representative]
        group = stabilizer(representative)
        entry_ids, entry_reps = entry_orbits(basis, group)
        qdim = len(entry_reps)
        total_gram_scalars += qdim

        candidates: set[tuple[int, ...]] = set()
        for member_index in parity_members[parity_orbit_id]:
            member = parity_masks[member_index]
            element = next(
                element
                for element in GROUP
                if exponent_image(representative, element) == member
            )
            acted_basis = [
                exponent_image(item, element) for item in basis
            ]
            for partition in partitions:
                candidates.update(
                    plateau_coefficient_rows(
                        acted_basis, member, partition
                    )
                )

        echelon, pivots, original_rows = exact_echelon_basis(
            sorted(candidates)
        )
        # The all-plateau collection is D22-closed, so its transported span
        # must be stable under the representative stabilizer.
        for element in group:
            for row in original_rows:
                coordinates_in_span(
                    transform_row(row, basis, element), echelon, pivots
                )

        original_dimension, face_dimension = invariant_face_dimension(
            basis, echelon, pivots, group
        )
        assert original_dimension == qdim
        constraint_rank = qdim - face_dimension
        equations = gram_kernel_equations(entry_ids, original_rows)
        exact_modular_rank = modular_rank(equations, qdim, PRIME)
        assert exact_modular_rank == constraint_rank

        total_kernel_dimension += len(original_rows)
        total_face_dimension += face_dimension
        total_constraint_rank += constraint_rank
        for row in original_rows:
            kernel_rows_flat.append((parity_orbit_id, row))
        per_block.append(
            {
                "parity_orbit": parity_orbit_id,
                "parity_weight": sum(representative),
                "degree_in_x": (TARGET_DEGREE - sum(representative)) // 2,
                "order": len(basis),
                "stabilizer_order": len(group),
                "gram_scalars": qdim,
                "candidate_rows": len(candidates),
                "evaluation_span_dimension": len(original_rows),
                "gram_face_dimension": face_dimension,
                "gram_constraint_rank": constraint_rank,
            }
        )

    assert total_gram_scalars == 8647

    summary: dict[str, object] = {
        "graph": "Gamma_11=And(4)",
        "vertices": N,
        "edges": len(edges),
        "cuts": len(cuts),
        "group_order": len(GROUP),
        "complete_c5_blowup_supports": len(partitions),
        "class_maps_before_AutC5_quotient": 10 * len(partitions),
        "D22_x_AutC5_orbits": len(partition_groups),
        "support_size_distribution": {
            str(key): value for key, value in sorted(size_distribution.items())
        },
        "D22_orbit_size_distribution": {
            str(key): value
            for key, value in sorted(orbit_size_distribution.items())
        },
        "orbit_representatives": [
            {
                "classes": [list(part) for part in representative],
                "class_sizes": [len(part) for part in representative],
                "support": sorted(sum(representative, ())),
                "D22_orbit_size": len(partition_groups[index]),
            }
            for index, representative in enumerate(representatives)
        ],
        "q10_witness": {
            "weights": list(CLAUDE_Q10),
            "support": list(q10_support),
            "classes": [list(part) for part in q10_partition],
            "class_sums": list(q10_sums),
            "included": True,
        },
        "plateau_cut_pairs_identically_tight": identically_tight_pairs,
        "plateau_cut_pairs_nontight_polynomial": nonidentically_tight_pairs,
        "multiplier_orbits": len(multiplier_pair_reps),
        "c5_only_forced_multiplier_orbits": len(forced_c5),
        "blowup_plateau_forced_multiplier_orbits": len(forced_blowup),
        "incremental_forced_multiplier_orbits": len(forced_blowup - forced_c5),
        "parity_block_orbits": len(parity_reps),
        "gram_orbit_scalars": total_gram_scalars,
        "evaluation_span_dimensions_total": total_kernel_dimension,
        "blowup_gram_face_rank": total_constraint_rank,
        "blowup_gram_face_dimension": total_face_dimension,
        "c5_only_gram_face_rank": 1471,
        "incremental_gram_face_rank": total_constraint_rank - 1471,
        "per_block": per_block,
        "scope": (
            "All complete nonempty C5-blow-up plateaus in Gamma_11; "
            "not a classification of the full ARCBOUND equality set."
        ),
    }
    payload = {
        "forced_c5": np.asarray(sorted(forced_c5), dtype=np.int32),
        "forced_blowup": np.asarray(sorted(forced_blowup), dtype=np.int32),
        "partitions_json": np.asarray(
            [json.dumps(partition) for partition in partitions]
        ),
        "partition_orbits_json": np.asarray(
            [json.dumps(orbit) for orbit in partition_groups]
        ),
        "kernel_rows_json": np.asarray(
            [
                json.dumps([block_index, list(row)])
                for block_index, row in kernel_rows_flat
            ]
        ),
    }
    return summary, payload


def write_report(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Exact balanced-C5-blow-up face in Gamma_11",
        "",
        "## Scope",
        "",
        "This is an exact face computation for the registered fixed-c=25,",
        "degree-4, 56-arc certificate. It enumerates every induced support",
        "that is a complete C5 blow-up with five nonempty classes. It does",
        "**not** claim that these plateaus exhaust the full ARCBOUND equality set.",
        "",
        "## Exact enumeration",
        "",
        "```json",
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "complete_c5_blowup_supports",
                    "class_maps_before_AutC5_quotient",
                    "D22_x_AutC5_orbits",
                    "support_size_distribution",
                    "D22_orbit_size_distribution",
                    "orbit_representatives",
                    "q10_witness",
                )
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "For a nonempty complete blow-up, equal open-neighbourhood classes",
        "are exactly its five blow-up classes. Hence each accepted support has",
        "one class map modulo Aut(C5), and the support enumeration is complete.",
        "",
        "## Forced multiplier face",
        "",
        "On a class-sum-one plateau, Theorem B gives q_S(x)>=1. The",
        "normalization and SOS identity force",
        "`sum_S nu_S(x)(q_S(x)-1)=0`. If the restriction of q_S-1 is not",
        "the zero polynomial, it is strictly positive at an interior plateau",
        "point; coefficientwise nonnegativity then kills every coefficient of",
        "nu_S whose monomial support lies in that blow-up support.",
        "",
        "```text",
        f"C5-only forced multiplier orbits = {summary['c5_only_forced_multiplier_orbits']}",
        f"all blow-up forced multiplier orbits = {summary['blowup_plateau_forced_multiplier_orbits']}",
        f"increment = {summary['incremental_forced_multiplier_orbits']}",
        "```",
        "",
        "## Exact parity-block evaluation spans",
        "",
        "For parity mask p, write a degree-6 Gram monomial as",
        "`y^p x^gamma`, where `|gamma|=(6-|p|)/2`, hence degree 0..3.",
        "The factor y^p is common and nonzero on an interior plateau whenever",
        "`supp(p)` lies in the support. In every class one pivot variable is",
        "eliminated by `x_pivot=1-sum(other class variables)`. Expanding all",
        "`x^gamma` gives integer coefficient rows whose rational span is",
        "exactly the span of all plateau evaluations (the interior is Zariski",
        "dense in the product of simplices).",
        "",
        "```text",
        f"C5-only Gram-face rank = {summary['c5_only_gram_face_rank']}",
        f"all blow-up Gram-face rank = {summary['blowup_gram_face_rank']}",
        f"increment = {summary['incremental_gram_face_rank']}",
        f"remaining invariant Gram dimension = {summary['blowup_gram_face_dimension']}",
        "```",
        "",
        "Every evaluation span is closed under the relevant stabilizer in exact",
        "rational arithmetic. The invariant symmetric-face dimension is computed",
        "by the character formula, and integer Qv=0 equations attain the",
        f"resulting codimension modulo the exact prime {PRIME}.",
        "",
        "## Per-block data",
        "",
        "```json",
        json.dumps(summary["per_block"], indent=2, sort_keys=True),
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        type=Path,
        default=HERE / "CODEX_R10_BLOWUP_FACE_summary.json",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=HERE / "CODEX_R10_BLOWUP_FACE_data.npz",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=HERE / "CODEX_R10_BLOWUP_FACE_REPORT.md",
    )
    args = parser.parse_args()
    summary, payload = build()
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    np.savez_compressed(args.data, **payload)
    write_report(args.report, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"SUMMARY={args.summary.resolve()}")
    print(f"DATA={args.data.resolve()}")
    print(f"REPORT={args.report.resolve()}")
    print(f"SHA256_SCRIPT={sha256(Path(__file__))}")
    print(f"SHA256_SUMMARY={sha256(args.summary)}")
    print(f"SHA256_DATA={sha256(args.data)}")
    print(f"SHA256_REPORT={sha256(args.report)}")
    print("EXACT_BLOWUP_FACE_ONLY: no SDP run and no equality-set completeness claim")


if __name__ == "__main__":
    main()
