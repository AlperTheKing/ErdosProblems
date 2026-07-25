#!/usr/bin/env python3
"""Realize and certify a nonunit circuit wall in an actual side-five hive.

The targeted rhombus rows are 21, 28, 20, 26.  Their primitive relation is

    A[21] - 2*A[28] - A[20] + 2*A[26] = 0,

and the matching support functional is

    (mu[3]-mu[4]) - (nu[3]-nu[4]).

We enumerate only the finite choices of a three-row transverse link.  A
floating LP selects a strict rational witness; every reported polyhedral and
lattice assertion is then rebuilt over exact rationals with cddlib/SymPy.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
import sys

import cdd.gmp as cg
import numpy as np
from scipy.optimize import linprog
from sympy import Matrix, Rational

sys.path.insert(0, "problems_external/ktt_lr_negativity/engine")
import hive_poly  # noqa: E402


RANK = 5
CIRCUIT_ROWS = (21, 28, 20, 26)
CIRCUIT_COEFFICIENTS = (1, -2, -1, 2)


def primitive(vector, canonical=False):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(int(value)))
    answer = tuple(int(value) // divisor for value in vector)
    if canonical and next(value for value in answer if value) < 0:
        answer = tuple(-value for value in answer)
    return answer


def boundary_matrix():
    zero = (0,) * RANK
    A, base, dimension, _, _ = hive_poly.build(zero, zero, zero)
    assert dimension == 6 and all(value == 0 for value in base)
    columns = []
    for coordinate in range(3 * RANK):
        values = [0] * (3 * RANK)
        values[coordinate] = 1
        boundary = tuple(
            tuple(values[part * RANK:(part + 1) * RANK])
            for part in range(3)
        )
        test_A, b, _, _, _ = hive_poly.build(*boundary)
        assert test_A == A
        columns.append(b)
    D = [[columns[column][row] for column in range(3 * RANK)]
         for row in range(len(A))]
    return A, D


def equality_row(A, D, row):
    # A[row]*x - D[row]*p = 0.
    return [-value for value in D[row]] + list(A[row])


def rational_affine_point(equalities, rhs, floating_point):
    augmented = Matrix([
        [Rational(value) for value in row] + [Rational(value)]
        for row, value in zip(equalities, rhs)
    ])
    reduced, pivots = augmented.rref()
    variable_count = len(floating_point)
    if any(pivot == variable_count for pivot in pivots):
        return None
    pivot_variables = {pivot for pivot in pivots if pivot < variable_count}
    free_variables = [index for index in range(variable_count)
                      if index not in pivot_variables]
    answer = [None] * variable_count
    for index in free_variables:
        answer[index] = Fraction(float(floating_point[index])).limit_denominator(10**6)
    for row_index, pivot in reversed(list(enumerate(pivots))):
        if pivot >= variable_count:
            continue
        value = Fraction(reduced[row_index, variable_count])
        for index in free_variables:
            value -= Fraction(reduced[row_index, index]) * answer[index]
        answer[pivot] = value
    assert all(value is not None for value in answer)
    return tuple(answer)


def strict_wall_point(A, D, link_rows):
    variable_count = 3 * RANK + 6
    tight_rows = set(CIRCUIT_ROWS) | set(link_rows)
    equalities = []
    rhs = []

    # Normalize |nu|=1, impose LR size, and impose the target support wall.
    normalization = [0] * variable_count
    for index in range(2 * RANK, 3 * RANK):
        normalization[index] = 1
    equalities.append(normalization)
    rhs.append(1)

    size = [0] * variable_count
    for index in range(0, 2 * RANK):
        size[index] = 1
    for index in range(2 * RANK, 3 * RANK):
        size[index] = -1
    equalities.append(size)
    rhs.append(0)

    wall = [0] * variable_count
    for coefficient, row in zip(CIRCUIT_COEFFICIENTS, CIRCUIT_ROWS):
        for index in range(3 * RANK):
            wall[index] += coefficient * D[row][index]
    equalities.append(wall)
    rhs.append(0)

    for row in sorted(tight_rows):
        equalities.append(equality_row(A, D, row))
        rhs.append(0)

    # Add delta as the final LP variable and maximize a common strict margin.
    inequalities = []
    inequality_rhs = []
    for row in range(len(A)):
        if row in tight_rows:
            continue
        inequality = equality_row(A, D, row) + [1]
        inequalities.append(inequality)
        inequality_rhs.append(0)

    # Strictly decreasing positive partitions keep both perturbations inside
    # the partition cone.
    for part in range(3):
        offset = part * RANK
        for index in range(RANK - 1):
            inequality = [0] * (variable_count + 1)
            inequality[offset + index] = -1
            inequality[offset + index + 1] = 1
            inequality[-1] = 1
            inequalities.append(inequality)
            inequality_rhs.append(0)
        inequality = [0] * (variable_count + 1)
        inequality[offset + RANK - 1] = -1
        inequality[-1] = 1
        inequalities.append(inequality)
        inequality_rhs.append(0)

    objective = [0] * variable_count + [-1]
    lp_equalities = [row + [0] for row in equalities]
    result = linprog(
        objective,
        A_ub=np.asarray(inequalities, dtype=float),
        b_ub=np.asarray(inequality_rhs, dtype=float),
        A_eq=np.asarray(lp_equalities, dtype=float),
        b_eq=np.asarray(rhs, dtype=float),
        bounds=[(None, None)] * variable_count + [(0, None)],
        method="highs",
    )
    if not result.success or result.x[-1] <= 10**-7:
        return None
    exact = rational_affine_point(equalities, rhs, result.x[:-1])
    if exact is None:
        return None

    p = exact[:3 * RANK]
    x = exact[3 * RANK:]
    slacks = []
    for row in range(len(A)):
        slack = sum(Fraction(D[row][index]) * p[index]
                    for index in range(3 * RANK)) - sum(
                        Fraction(A[row][index]) * x[index]
                        for index in range(6)
                    )
        slacks.append(slack)
    if any(slacks[row] != 0 for row in tight_rows):
        return None
    if any(slacks[row] <= 0 for row in range(len(A)) if row not in tight_rows):
        return None
    return p, x, tuple(slacks)


def exact_polytope(boundary, allow_nonsimple):
    A, b, ambient, _, ok = hive_poly.build(*boundary)
    if not ok or ambient != 6:
        return None
    matrix = cg.matrix_from_array(
        [[Fraction(b[row])] + [Fraction(-value) for value in A[row]]
         for row in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    if matrix.lin_set:
        return None
    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    if not generators.array or any(row[0] != 1 for row in generators.array):
        return None
    vertices = [tuple(Fraction(value) for value in row[1:])
                for row in generators.array]

    facet_records = []
    for inequality in matrix.array:
        normal = primitive(tuple(-Fraction(value) for value in inequality[1:]))
        support = Fraction(inequality[0])
        sources = []
        for source, (raw_normal, raw_support) in enumerate(zip(A, b)):
            divisor = gcd(0, *[abs(value) for value in raw_normal])
            if primitive(raw_normal) == normal and Fraction(raw_support, divisor) == support:
                sources.append(source)
        if len(sources) != 1:
            return None
        facet_records.append((normal, sources[0], tuple(Fraction(value) for value in inequality)))
    facet_ids = tuple(sorted((normal, source) for normal, source, _ in facet_records))

    tight_sets = []
    for vertex in vertices:
        tight = tuple(sorted(
            (normal, source)
            for normal, source, inequality in facet_records
            if inequality[0] + sum(inequality[index + 1] * vertex[index]
                                   for index in range(6)) == 0
        ))
        if not allow_nonsimple and len(tight) != 6:
            return None
        tight_sets.append(tight)
    return {
        "facets": facet_ids,
        "tight_sets": tuple(sorted(tight_sets)),
        "vertices": tuple(vertices),
    }


def integral_boundary(p):
    scale = 1
    for value in p:
        scale = lcm(scale, value.denominator)
    values = [int(scale * value) for value in p]
    boundary = tuple(tuple(values[part * RANK:(part + 1) * RANK])
                     for part in range(3))
    common = gcd(0, *[abs(value) for value in values])
    if common > 1:
        boundary = tuple(tuple(value // common for value in part)
                         for part in boundary)
        scale //= common
    return boundary, scale


def perturb(boundary, sign, multiplier):
    parts = [list(multiplier * value for value in part) for part in boundary]
    # Preserve |lambda|+|mu|=|nu| and change omega by sign.
    parts[1][3] += sign
    parts[2][0] += sign
    return tuple(tuple(part) for part in parts)


def verify_realization(A, D, link_rows, point):
    p, x, slacks = point
    wall_boundary, scale = integral_boundary(p)
    wall = exact_polytope(wall_boundary, allow_nonsimple=True)
    if wall is None:
        return None
    target_sources = set(CIRCUIT_ROWS) | set(link_rows)
    target_ids = {
        (primitive(A[row]), row) for row in target_sources
    }
    nonsimple = [tight for tight in wall["tight_sets"] if len(tight) != 6]
    if len(nonsimple) != 1 or len(nonsimple[0]) != 7:
        return None
    if set(nonsimple[0]) != target_ids:
        return None

    for multiplier in (10, 100, 1000, 10000):
        left_boundary = perturb(wall_boundary, -1, multiplier)
        right_boundary = perturb(wall_boundary, 1, multiplier)
        left = exact_polytope(left_boundary, allow_nonsimple=False)
        right = exact_polytope(right_boundary, allow_nonsimple=False)
        if left is None or right is None or left["facets"] != right["facets"]:
            continue
        left_cones = frozenset(left["tight_sets"])
        right_cones = frozenset(right["tight_sets"])
        left_only = left_cones - right_cones
        right_only = right_cones - left_cones
        if len(left_only) != 2 or len(right_only) != 2:
            continue
        changed = left_only | right_only
        if set().union(*(set(cone) for cone in changed)) != target_ids:
            continue
        common = set(next(iter(changed)))
        for cone in changed:
            common &= set(cone)
        link_ids = {(primitive(A[row]), row) for row in link_rows}
        if common != link_ids:
            continue
        return {
            "link_rows": link_rows,
            "wall_boundary": wall_boundary,
            "wall_scale": scale,
            "wall_vertex": tuple(scale * value for value in x),
            "minimum_strict_slack": min(value for value in slacks if value > 0),
            "multiplier": multiplier,
            "left_boundary": left_boundary,
            "right_boundary": right_boundary,
            "facets": left["facets"],
            "left_only": tuple(sorted(left_only)),
            "right_only": tuple(sorted(right_only)),
            "wall_tight_sets": wall["tight_sets"],
        }
    return None


def main():
    A, D = boundary_matrix()
    relation = tuple(
        sum(CIRCUIT_COEFFICIENTS[index] * A[row][coordinate]
            for index, row in enumerate(CIRCUIT_ROWS))
        for coordinate in range(6)
    )
    assert relation == (0,) * 6

    circuit_normals = {primitive(A[row]) for row in CIRCUIT_ROWS}
    candidate_rows = [
        row for row in range(len(A))
        if row not in CIRCUIT_ROWS and primitive(A[row]) not in circuit_normals
    ]
    tested = 0
    lp_feasible = 0
    for link_rows in combinations(candidate_rows, 3):
        link_matrix = Matrix([A[row] for row in link_rows])
        full_matrix = Matrix([A[row] for row in CIRCUIT_ROWS + link_rows])
        if link_matrix.rank() != 3 or full_matrix.rank() != 6:
            continue
        tested += 1
        point = strict_wall_point(A, D, link_rows)
        if point is None:
            continue
        lp_feasible += 1
        result = verify_realization(A, D, link_rows, point)
        if result is None:
            continue
        print("PASS")
        print("tested_links", tested, "strict_lp_links", lp_feasible)
        print("circuit_rows", CIRCUIT_ROWS)
        print("circuit_normals", tuple(A[row] for row in CIRCUIT_ROWS))
        print("primitive_relation", CIRCUIT_COEFFICIENTS)
        for key, value in result.items():
            print(key, value)
        return 0
    print("NO_REALIZATION", tested, lp_feasible)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
