#!/usr/bin/env python3
"""Find the smallest exact hive wall contradicting unit 2<->2 universality.

Ranks at most three have at most one interior hive coordinate, hence no
full-dimensional normal-fan bistellar wall.  This gate exhausts the minimal
3- and 4-row circuits of A4.  It accepts a circuit only when:

* an exact wall triple has a relative-interior point with precisely those
  raw rhombus rows tight;
* exact simple hive fans exist on both support sides;
* their complete maximal-cone difference is exactly the two circuit
  triangulations joined to common links; and
* no unrelated facet normal changes.

Facet birth/death is allowed: it is exactly what a 1<->k circuit means for a
support-number wall.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
import sys

import cdd.gmp as cg
import numpy as np
from scipy.optimize import linprog
from sympy import Matrix

sys.path.insert(0, "problems_external/ktt_lr_negativity/engine")
import hive_poly  # noqa: E402

from ghte_find_r4_wall_pair import exact_fan, primitive  # noqa: E402


RANK = 4


def boundary_matrix():
    zero = (0,) * RANK
    A, base, dimension, _, _ = hive_poly.build(zero, zero, zero)
    assert dimension == 3 and all(value == 0 for value in base)
    columns = []
    for coordinate in range(3 * RANK):
        values = [0] * (3 * RANK)
        values[coordinate] = 1
        boundary = tuple(tuple(values[part * RANK:(part + 1) * RANK])
                         for part in range(3))
        test_A, b, _, _, _ = hive_poly.build(*boundary)
        assert test_A == A
        columns.append(b)
    D = [[columns[column][row] for column in range(3 * RANK)]
         for row in range(len(A))]
    return A, D


def primitive_relation(A, rows):
    matrix = Matrix.hstack(*(Matrix(A[row]) for row in rows))
    kernel = matrix.nullspace()
    if matrix.rank() != len(rows) - 1 or len(kernel) != 1:
        return None
    if any(value == 0 for value in kernel[0]):
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


def rational_affine_point(equalities, rhs, floating_point):
    augmented = Matrix([row + [value] for row, value in zip(equalities, rhs)])
    reduced, pivots = augmented.rref()
    variable_count = len(floating_point)
    if any(pivot == variable_count for pivot in pivots):
        return None
    pivot_set = {pivot for pivot in pivots if pivot < variable_count}
    free = [index for index in range(variable_count) if index not in pivot_set]
    answer = [None] * variable_count
    for index in free:
        answer[index] = Fraction(float(floating_point[index])).limit_denominator(10**6)
    for row_index, pivot in reversed(list(enumerate(pivots))):
        if pivot >= variable_count:
            continue
        value = Fraction(reduced[row_index, variable_count])
        for index in free:
            value -= Fraction(reduced[row_index, index]) * answer[index]
        answer[pivot] = value
    return tuple(answer)


def strict_face_point(A, D, rows):
    variable_count = 3 * RANK + 3
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
    for row in range(len(A)):
        if row in rows:
            continue
        inequalities.append(equality_row(A, D, row) + [1])
    for part in range(3):
        offset = part * RANK
        for index in range(RANK - 1):
            inequality = [0] * (variable_count + 1)
            inequality[offset + index] = -1
            inequality[offset + index + 1] = 1
            inequality[-1] = 1
            inequalities.append(inequality)
        inequality = [0] * (variable_count + 1)
        inequality[offset + RANK - 1] = -1
        inequality[-1] = 1
        inequalities.append(inequality)

    result = linprog(
        [0] * variable_count + [-1],
        A_ub=np.asarray(inequalities, dtype=float),
        b_ub=np.zeros(len(inequalities)),
        A_eq=np.asarray([row + [0] for row in equalities], dtype=float),
        b_eq=np.asarray(rhs, dtype=float),
        bounds=[(None, None)] * variable_count + [(0, None)],
        method="highs",
    )
    if not result.success or result.x[-1] <= 10**-7:
        return None
    exact = rational_affine_point(equalities, rhs, result.x[:-1])
    p = exact[:3 * RANK]
    x = exact[3 * RANK:]
    slacks = tuple(
        sum(Fraction(D[row][index]) * p[index]
            for index in range(3 * RANK))
        - sum(Fraction(A[row][index]) * x[index] for index in range(3))
        for row in range(len(A))
    )
    if any(slacks[row] != 0 for row in rows):
        return None
    if any(slacks[row] <= 0 for row in range(len(A)) if row not in rows):
        return None
    return p, x, slacks


def integral_boundary(p):
    scale = 1
    for value in p:
        scale = lcm(scale, value.denominator)
    values = [int(scale * value) for value in p]
    common = gcd(0, *(abs(value) for value in values))
    if common > 1:
        values = [value // common for value in values]
        scale //= common
    return tuple(tuple(values[part * RANK:(part + 1) * RANK])
                 for part in range(3)), scale


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
                    direction = [-value for value in direction]
                    step = -step
                return tuple(direction), step
    return None


def perturb(boundary, direction, sign, multiplier):
    flat = [multiplier * value for part in boundary for value in part]
    flat = [value + sign * delta for value, delta in zip(flat, direction)]
    return tuple(tuple(flat[part * RANK:(part + 1) * RANK])
                 for part in range(3))


def wall_is_bounded(boundary):
    A, b, dimension, _, ok = hive_poly.build(*boundary)
    if not ok or dimension != 3:
        return False
    matrix = cg.matrix_from_array(
        [[Fraction(b[row])] + [Fraction(-value) for value in A[row]]
         for row in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    vertices = [row for row in generators.array if row[0] == 1]
    if not vertices or any(row[0] != 1 for row in generators.array):
        return False
    base = Matrix([[Fraction(value) for value in row[1:]] for row in vertices])
    return (base - Matrix.ones(base.rows, 1) * base.row(0)).rank() == 3


def changed_by_links(left_only, right_only, target, positive, negative):
    def split(cones):
        output = {}
        for cone in cones:
            cone = set(cone)
            circuit_part = cone & target
            if len(circuit_part) != len(target) - 1:
                return None
            missing = frozenset(target - circuit_part)
            if len(missing) != 1:
                return None
            link = tuple(sorted(cone - target))
            output.setdefault(link, set()).update(missing)
        return output

    left = split(left_only)
    right = split(right_only)
    if left is None or right is None or not left or set(left) != set(right):
        return None
    orientation = None
    for link in left:
        pair = frozenset(left[link]), frozenset(right[link])
        if pair == (positive, negative):
            current = 1
        elif pair == (negative, positive):
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
    if not wall_is_bounded(wall_boundary):
        return None
    target = frozenset(primitive(A[row]) for row in rows)
    positive = frozenset(primitive(A[row]) for row, coefficient
                         in zip(rows, coefficients) if coefficient > 0)
    negative = frozenset(primitive(A[row]) for row, coefficient
                         in zip(rows, coefficients) if coefficient < 0)
    omega = tuple(
        sum(coefficients[index] * D[row][coordinate]
            for index, row in enumerate(rows))
        for coordinate in range(3 * RANK)
    )
    crossing = crossing_direction(omega)
    if crossing is None:
        return None
    direction, omega_step = crossing

    for multiplier in (10, 100, 1000, 10000, 100000):
        minus_boundary = perturb(wall_boundary, direction, -1, multiplier)
        plus_boundary = perturb(wall_boundary, direction, 1, multiplier)
        minus = exact_fan(*minus_boundary)
        plus = exact_fan(*plus_boundary)
        if minus is None or plus is None:
            continue
        if (set(minus["facets"]) ^ set(plus["facets"])) - set(target):
            continue
        minus_only = minus["cones"] - plus["cones"]
        plus_only = plus["cones"] - minus["cones"]
        link_check = changed_by_links(
            minus_only, plus_only, target, positive, negative
        )
        if link_check is None:
            continue
        links, orientation = link_check
        return {
            "rows": rows,
            "normals": tuple(A[row] for row in rows),
            "coefficients": coefficients,
            "sign_split": (len(positive), len(negative)),
            "wall_boundary": wall_boundary,
            "wall_face_point": tuple(scale * value for value in x),
            "minimum_strict_slack": min(value for value in slacks if value > 0),
            "crossing_direction": direction,
            "omega_step": omega_step,
            "multiplier": multiplier,
            "minus_boundary": minus_boundary,
            "plus_boundary": plus_boundary,
            "minus_facets": minus["facets"],
            "plus_facets": plus["facets"],
            "links": links,
            "orientation": orientation,
            "minus_only": tuple(sorted(minus_only)),
            "plus_only": tuple(sorted(plus_only)),
        }
    return None


def main():
    A, D = boundary_matrix()
    tested = circuits = candidates = strict = 0
    for size in (3, 4):
        for rows in combinations(range(len(A)), size):
            tested += 1
            if len({primitive(A[row]) for row in rows}) != size:
                continue
            coefficients = primitive_relation(A, rows)
            if coefficients is None:
                continue
            circuits += 1
            positive = sum(value > 0 for value in coefficients)
            negative = sum(value < 0 for value in coefficients)
            if not positive or not negative:
                continue
            if (positive, negative) in ((2, 2),) and all(
                    abs(value) == 1 for value in coefficients):
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
            print("tested_subsets", tested, "circuits", circuits,
                  "candidate_circuits", candidates, "strict_faces", strict)
            for key, value in result.items():
                print(key, value)
            return 0
    print("NO_COUNTERWALL", tested, circuits, candidates, strict)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
