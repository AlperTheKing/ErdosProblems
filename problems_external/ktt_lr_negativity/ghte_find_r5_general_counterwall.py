#!/usr/bin/env python3
"""Bounded exact gate for a non-2<->2 or nonunit side-five hive wall.

The gate samples at most 20,000 seven-row circuits of the fixed side-five
rhombus-normal configuration.  For each circuit it solves only the direct
closure question: can precisely those seven rhombi be tight at one otherwise
strict full-dimensional hive vertex?  A candidate is reported only after an
exact rational reconstruction, exact cddlib wall/facet check, and exact
opposite-chamber fan comparison.

This is a falsification gate, not a rank census and not evidence for a
rank-uniform theorem when it returns no witness.
"""

from fractions import Fraction
from math import gcd
import random

import numpy as np
from scipy.optimize import linprog

from ghte_realize_nonunit_r5_wall import (
    RANK,
    boundary_matrix,
    exact_polytope,
    integral_boundary,
    primitive,
    rational_affine_point,
)


MAX_CIRCUITS = 20000


def cofactor_relation(A, rows):
    columns = np.asarray([[A[row][coordinate] for row in rows]
                          for coordinate in range(6)], dtype=float)
    coefficients = []
    for omitted in range(7):
        minor = np.delete(columns, omitted, axis=1)
        determinant = int(round(np.linalg.det(minor)))
        coefficients.append(((-1) ** omitted) * determinant)
    if any(value == 0 for value in coefficients):
        return None
    if any(sum(coefficients[index] * A[row][coordinate]
               for index, row in enumerate(rows)) != 0
           for coordinate in range(6)):
        return None
    divisor = gcd(0, *(abs(value) for value in coefficients))
    coefficients = tuple(value // divisor for value in coefficients)
    if next(value for value in coefficients if value) < 0:
        coefficients = tuple(-value for value in coefficients)
    return coefficients


def equality_row(A, D, row):
    return [-value for value in D[row]] + list(A[row])


def strict_circuit_point(A, D, rows):
    variable_count = 3 * RANK + 6
    tight_rows = set(rows)
    equalities = []
    rhs = []

    normalization = [0] * variable_count
    for index in range(2 * RANK, 3 * RANK):
        normalization[index] = 1
    equalities.append(normalization)
    rhs.append(1)

    size = [0] * variable_count
    for index in range(2 * RANK):
        size[index] = 1
    for index in range(2 * RANK, 3 * RANK):
        size[index] = -1
    equalities.append(size)
    rhs.append(0)

    for row in rows:
        equalities.append(equality_row(A, D, row))
        rhs.append(0)

    inequalities = []
    inequality_rhs = []
    for row in range(len(A)):
        if row in tight_rows:
            continue
        inequalities.append(equality_row(A, D, row) + [1])
        inequality_rhs.append(0)

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

    result = linprog(
        [0] * variable_count + [-1],
        A_ub=np.asarray(inequalities, dtype=float),
        b_ub=np.asarray(inequality_rhs, dtype=float),
        A_eq=np.asarray([row + [0] for row in equalities], dtype=float),
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


def crossing_direction(omega):
    size = (1,) * (2 * RANK) + (-1,) * RANK
    for first in range(3 * RANK):
        for second in range(first + 1, 3 * RANK):
            direction = [0] * (3 * RANK)
            direction[first] = size[second]
            direction[second] = -size[first]
            value = sum(omega[index] * direction[index]
                        for index in range(3 * RANK))
            if value:
                if value < 0:
                    direction = [-entry for entry in direction]
                    value = -value
                return tuple(direction), value
    return None


def perturb(boundary, direction, sign, multiplier):
    flat = [multiplier * value for part in boundary for value in part]
    flat = [value + sign * delta for value, delta in zip(flat, direction)]
    return tuple(tuple(flat[part * RANK:(part + 1) * RANK])
                 for part in range(3))


def certify(A, D, rows, coefficients, point):
    p, x, slacks = point
    wall_boundary, scale = integral_boundary(p)
    wall = exact_polytope(wall_boundary, allow_nonsimple=True)
    if wall is None:
        return None
    target_ids = {(primitive(A[row]), row) for row in rows}
    nonsimple = [tight for tight in wall["tight_sets"] if len(tight) != 6]
    if len(nonsimple) != 1 or set(nonsimple[0]) != target_ids:
        return None

    omega = tuple(
        sum(coefficients[index] * D[row][coordinate]
            for index, row in enumerate(rows))
        for coordinate in range(3 * RANK)
    )
    if not any(omega) or sum(omega[index] * p[index]
                             for index in range(3 * RANK)) != 0:
        return None
    crossing = crossing_direction(omega)
    if crossing is None:
        return None
    direction, omega_step = crossing

    positive = frozenset(
        tuple(sorted(target_ids - {(primitive(A[row]), row)}))
        for row, coefficient in zip(rows, coefficients) if coefficient > 0
    )
    negative = frozenset(
        tuple(sorted(target_ids - {(primitive(A[row]), row)}))
        for row, coefficient in zip(rows, coefficients) if coefficient < 0
    )

    for multiplier in (10, 100, 1000, 10000, 100000):
        minus_boundary = perturb(wall_boundary, direction, -1, multiplier)
        plus_boundary = perturb(wall_boundary, direction, 1, multiplier)
        minus = exact_polytope(minus_boundary, allow_nonsimple=False)
        plus = exact_polytope(plus_boundary, allow_nonsimple=False)
        if minus is None or plus is None or minus["facets"] != plus["facets"]:
            continue
        minus_cones = frozenset(minus["tight_sets"])
        plus_cones = frozenset(plus["tight_sets"])
        minus_only = minus_cones - plus_cones
        plus_only = plus_cones - minus_cones
        if not ((minus_only == positive and plus_only == negative)
                or (minus_only == negative and plus_only == positive)):
            continue
        return {
            "rows": rows,
            "normals": tuple(A[row] for row in rows),
            "coefficients": coefficients,
            "sign_split": (len(positive), len(negative)),
            "wall_boundary": wall_boundary,
            "wall_vertex": tuple(scale * value for value in x),
            "minimum_strict_slack": min(value for value in slacks if value > 0),
            "crossing_direction": direction,
            "omega_step": omega_step,
            "multiplier": multiplier,
            "minus_boundary": minus_boundary,
            "plus_boundary": plus_boundary,
            "facets": minus["facets"],
            "minus_only": tuple(sorted(minus_only)),
            "plus_only": tuple(sorted(plus_only)),
            "wall_tight_sets": wall["tight_sets"],
        }
    return None


def main():
    A, D = boundary_matrix()
    rng = random.Random(2026072207)
    seen = set()
    circuits = 0
    strict = 0
    while len(seen) < MAX_CIRCUITS:
        rows = tuple(sorted(rng.sample(range(len(A)), 7)))
        if rows in seen:
            continue
        seen.add(rows)
        if len({primitive(A[row]) for row in rows}) != 7:
            continue
        coefficients = cofactor_relation(A, rows)
        if coefficients is None:
            continue
        circuits += 1
        point = strict_circuit_point(A, D, rows)
        if point is None:
            continue
        strict += 1
        result = certify(A, D, rows, coefficients, point)
        if result is None:
            continue
        print("PASS")
        print("sampled_subsets", len(seen), "circuits", circuits,
              "strict_circuits", strict)
        for key, value in result.items():
            print(key, value)
        return 0
    print("NO_COUNTERWALL", len(seen), circuits, strict)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
