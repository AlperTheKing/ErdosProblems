#!/usr/bin/env python3
"""Exact side-five gate for closed circuit faces of sizes three and four.

For every minimal 3- or 4-row circuit of the fixed A5 configuration that is
not a unit 2<->2 circuit, solve the direct closure LP with exactly the circuit
rhombi flat at a relative-interior hive point.  A hit is accepted only when
exact cddlib reconstruction gives simple fans on both sides and every changed
maximal cone is the corresponding circuit triangulation joined to an actual
common link.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm

import numpy as np
from scipy.optimize import linprog
from sympy import Matrix

from ghte_realize_nonunit_r5_wall import (
    RANK,
    boundary_matrix,
    exact_polytope,
    integral_boundary,
    primitive,
    rational_affine_point,
)


def primitive_relation(A, rows):
    matrix = Matrix.hstack(*(Matrix(A[row]) for row in rows))
    kernel = matrix.nullspace()
    if len(kernel) != 1 or any(value == 0 for value in kernel[0]):
        return None
    # Minimality is equivalent to rank |C|-1 and full support of the unique
    # dependence.
    if matrix.rank() != len(rows) - 1:
        return None
    denominator = 1
    for value in kernel[0]:
        denominator = lcm(denominator, int(value.q))
    integers = [int(value * denominator) for value in kernel[0]]
    divisor = gcd(0, *(abs(value) for value in integers))
    answer = tuple(value // divisor for value in integers)
    if next(value for value in answer if value) < 0:
        answer = tuple(-value for value in answer)
    return answer


def equality_row(A, D, row):
    return [-value for value in D[row]] + list(A[row])


def strict_face_point(A, D, rows):
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
            step = sum(omega[index] * direction[index]
                       for index in range(3 * RANK))
            if step:
                if step < 0:
                    direction = [-entry for entry in direction]
                    step = -step
                return tuple(direction), step
    return None


def perturb(boundary, direction, sign, multiplier):
    flat = [multiplier * value for part in boundary for value in part]
    flat = [value + sign * delta for value, delta in zip(flat, direction)]
    return tuple(tuple(flat[part * RANK:(part + 1) * RANK])
                 for part in range(3))


def changed_by_links(left_only, right_only, target_ids, positive_ids, negative_ids):
    def split(cones):
        by_link = {}
        for cone in cones:
            cone = set(cone)
            circuit_part = cone & target_ids
            if len(circuit_part) != len(target_ids) - 1:
                return None
            missing = tuple(target_ids - circuit_part)
            if len(missing) != 1:
                return None
            link = tuple(sorted(cone - target_ids))
            by_link.setdefault(link, set()).add(missing[0])
        return by_link

    left = split(left_only)
    right = split(right_only)
    if left is None or right is None or set(left) != set(right) or not left:
        return None
    orientation = None
    for link in left:
        pair = (frozenset(left[link]), frozenset(right[link]))
        if pair == (positive_ids, negative_ids):
            current = 1
        elif pair == (negative_ids, positive_ids):
            current = -1
        else:
            return None
        if orientation is None:
            orientation = current
        elif orientation != current:
            return None
    return tuple(sorted(left)), orientation


def certify(A, D, rows, coefficients, point):
    p, x, slacks = point
    wall_boundary, scale = integral_boundary(p)
    wall = exact_polytope(wall_boundary, allow_nonsimple=True)
    if wall is None:
        return None
    target_ids = {(primitive(A[row]), row) for row in rows}
    if not target_ids.issubset(set(wall["facets"])):
        return None
    nonsimple = [tight for tight in wall["tight_sets"] if len(tight) != 6]
    if not nonsimple or any(len(tight) != 7 or not target_ids.issubset(set(tight))
                            for tight in nonsimple):
        return None

    omega = tuple(
        sum(coefficients[index] * D[row][coordinate]
            for index, row in enumerate(rows))
        for coordinate in range(3 * RANK)
    )
    if not any(omega):
        return None
    crossing = crossing_direction(omega)
    if crossing is None:
        return None
    direction, omega_step = crossing

    positive_ids = frozenset((primitive(A[row]), row)
                             for row, coefficient in zip(rows, coefficients)
                             if coefficient > 0)
    negative_ids = frozenset((primitive(A[row]), row)
                             for row, coefficient in zip(rows, coefficients)
                             if coefficient < 0)

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
        link_check = changed_by_links(
            minus_only, plus_only, target_ids, positive_ids, negative_ids
        )
        if link_check is None:
            continue
        links, orientation = link_check
        return {
            "rows": rows,
            "normals": tuple(A[row] for row in rows),
            "coefficients": coefficients,
            "sign_split": (len(positive_ids), len(negative_ids)),
            "wall_boundary": wall_boundary,
            "wall_vertex_relative_interior": tuple(scale * value for value in x),
            "minimum_strict_slack": min(value for value in slacks if value > 0),
            "crossing_direction": direction,
            "omega_step": omega_step,
            "multiplier": multiplier,
            "minus_boundary": minus_boundary,
            "plus_boundary": plus_boundary,
            "links": links,
            "orientation": orientation,
            "facets": minus["facets"],
            "minus_only": tuple(sorted(minus_only)),
            "plus_only": tuple(sorted(plus_only)),
            "wall_nonsimple": tuple(nonsimple),
        }
    return None


def main():
    A, D = boundary_matrix()
    tested_subsets = 0
    circuits = 0
    candidates = 0
    strict = 0
    for size in (3, 4):
        for rows in combinations(range(len(A)), size):
            tested_subsets += 1
            if len({primitive(A[row]) for row in rows}) != size:
                continue
            coefficients = primitive_relation(A, rows)
            if coefficients is None:
                continue
            circuits += 1
            positive_count = sum(value > 0 for value in coefficients)
            negative_count = sum(value < 0 for value in coefficients)
            if positive_count == 0 or negative_count == 0:
                # A positive dependence gives a nonpointed normal cone and
                # can only force an intrinsic affine equality, not a wall
                # between full-dimensional hive fans.
                continue
            sign_split = tuple(sorted((positive_count, negative_count)))
            unit = all(abs(value) == 1 for value in coefficients)
            if sign_split == (2, 2) and unit:
                continue
            candidates += 1
            point = strict_face_point(A, D, rows)
            if point is None:
                continue
            strict += 1
            result = certify(A, D, rows, coefficients, point)
            if result is None:
                continue
            print("PASS")
            print("tested_subsets", tested_subsets, "circuits", circuits,
                  "candidate_circuits", candidates, "strict_faces", strict)
            for key, value in result.items():
                print(key, value)
            return 0
    print("NO_COUNTERWALL", tested_subsets, circuits, candidates, strict)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
