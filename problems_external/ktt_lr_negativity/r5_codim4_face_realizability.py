#!/usr/bin/env python3
"""Realizability test for the most negative rank-5 codimension-4 BV cone.

The target normal IDs (0,7,23,25) are the minimizer independently found by
``r5_codim4_bv_independent_v2.py``.  This program asks for partition boundary
data p=(lambda,mu,nu), a point x in the relative interior of the target face,
and a point z in the strict interior of the whole hive polytope.  With
sum(nu)=1 it maximizes a common strict slack epsilon:

  A_s x = D_s p                 (s in target rows),
  A_i x <= D_i p - epsilon      (all other rows),
  A_i z <= D_i p - epsilon      (all rows),

together with the partition cone, weight balance, and boundary-only rhombi.
An exact rational replay, followed by clearing denominators, certifies any
reported witness.  The floating-point LP is only a candidate generator.
"""

from fractions import Fraction
from math import gcd
import os
import sys

import numpy as np
from scipy.optimize import linprog


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "r5_rational"))
from hiveR import boundary_map, fixed_A, rows_symbolic  # noqa: E402


RANK = 5
TARGET_NORMAL_IDS = (0, 7, 23, 25)
TARGET_ROWS = (12, 14, 10, 19)


def partition_rows():
    rows = []
    for offset in (0, 5, 10):
        for i in range(4):
            row = [0] * 15
            row[offset + i] = -1
            row[offset + i + 1] = 1
            rows.append(row)
        row = [0] * 15
        row[offset + 4] = -1
        rows.append(row)
    return rows


def boundary_only_rows():
    boundary = boundary_map(RANK)
    rows = []
    tags = []
    for coefficients, boundary_coefficients, tag in rows_symbolic(RANK):
        if any(coefficients):
            continue
        row = [0] * 15
        for vertex, coefficient in boundary_coefficients.items():
            for i, value in enumerate(boundary[vertex]):
                row[i] += coefficient * value
        rows.append(row)  # const = row.p <= 0
        tags.append(tag)
    return rows, tags


def formulate():
    A, D, tags = fixed_A(RANK)
    A = np.asarray(A, dtype=float)
    D = np.asarray(D, dtype=float)
    # variables: p[0:15], x[15:21], z[21:27], epsilon[27]
    number_variables = 28
    inequalities = []
    bounds = []

    def add_inequality(p=None, x=None, z=None, epsilon=0.0, rhs=0.0):
        row = np.zeros(number_variables)
        if p is not None:
            row[:15] = p
        if x is not None:
            row[15:21] = x
        if z is not None:
            row[21:27] = z
        row[27] = epsilon
        inequalities.append(row)
        bounds.append(rhs)

    for row in partition_rows():
        add_inequality(p=row)
    boundary_rows, boundary_tags = boundary_only_rows()
    for row in boundary_rows:
        add_inequality(p=row)

    target = set(TARGET_ROWS)
    for i in range(len(A)):
        if i not in target:
            add_inequality(p=-D[i], x=A[i], epsilon=1.0)
        add_inequality(p=-D[i], z=A[i], epsilon=1.0)

    equalities = []
    equality_bounds = []

    weight = np.zeros(number_variables)
    weight[:5] = 1
    weight[5:10] = 1
    weight[10:15] = -1
    equalities.append(weight)
    equality_bounds.append(0.0)

    normalize = np.zeros(number_variables)
    normalize[10:15] = 1
    equalities.append(normalize)
    equality_bounds.append(1.0)

    for i in TARGET_ROWS:
        row = np.zeros(number_variables)
        row[:15] = -D[i]
        row[15:21] = A[i]
        equalities.append(row)
        equality_bounds.append(0.0)

    objective = np.zeros(number_variables)
    objective[27] = -1.0
    variable_bounds = [(None, None)] * 27 + [(0.0, None)]
    return (
        objective,
        np.asarray(inequalities),
        np.asarray(bounds),
        np.asarray(equalities),
        np.asarray(equality_bounds),
        variable_bounds,
        tags,
        boundary_tags,
    )


def fractions_from_float(vector, maximum_denominator=1_000_000):
    return tuple(
        Fraction(str(float(value))).limit_denominator(maximum_denominator)
        for value in vector
    )


def dot(row, vector):
    return sum(Fraction(value) * vector[i] for i, value in enumerate(row))


def lcm(left, right):
    return left // gcd(left, right) * right


def exact_replay(solution):
    objective, Aub, bub, Aeq, beq, _, tags, boundary_tags = formulate()
    assert all(dot(row, solution) <= Fraction(str(float(rhs))) for row, rhs in zip(Aub, bub))
    assert all(dot(row, solution) == Fraction(str(float(rhs))) for row, rhs in zip(Aeq, beq))
    epsilon = solution[27]
    assert epsilon > 0

    A, D, _ = fixed_A(RANK)
    p = solution[:15]
    x = solution[15:21]
    z = solution[21:27]
    slacks_x = [dot(D[i], p) - dot(A[i], x) for i in range(len(A))]
    slacks_z = [dot(D[i], p) - dot(A[i], z) for i in range(len(A))]
    assert all(slacks_x[i] == 0 for i in TARGET_ROWS)
    assert all(slacks_x[i] >= epsilon for i in range(len(A)) if i not in TARGET_ROWS)
    assert all(value >= epsilon for value in slacks_z)

    common = 1
    for value in solution:
        common = lcm(common, value.denominator)
    integer_p = tuple(int(value * common) for value in p)
    integer_x = tuple(int(value * common) for value in x)
    integer_z = tuple(int(value * common) for value in z)
    integer_epsilon = int(epsilon * common)
    assert integer_epsilon > 0
    return {
        "lambda": integer_p[:5],
        "mu": integer_p[5:10],
        "nu": integer_p[10:15],
        "face_point": integer_x,
        "interior_point": integer_z,
        "epsilon": integer_epsilon,
        "scale": common,
        "target_rows": TARGET_ROWS,
        "target_tags": tuple(tags[i] for i in TARGET_ROWS),
        "minimum_other_face_slack": min(
            int(slacks_x[i] * common)
            for i in range(len(A)) if i not in TARGET_ROWS
        ),
        "minimum_interior_slack": min(int(value * common) for value in slacks_z),
        "boundary_only_tags": tuple(boundary_tags),
    }


def main():
    objective, Aub, bub, Aeq, beq, variable_bounds, _, _ = formulate()
    result = linprog(
        objective,
        A_ub=Aub,
        b_ub=bub,
        A_eq=Aeq,
        b_eq=beq,
        bounds=variable_bounds,
        method="highs",
    )
    print(f"lp_status={result.status} message={result.message}")
    assert result.success
    print(f"float_epsilon={result.x[27]:.16g}")
    solution = fractions_from_float(result.x)
    witness = exact_replay(solution)
    print("PASS")
    for key, value in witness.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
