#!/usr/bin/env python3
"""Exact-replay LP for a proposed rank-5 hive face active-row closure."""

from fractions import Fraction
import os
import sys

import numpy as np
from scipy.optimize import linprog


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "r5_rational"))
from hiveR import fixed_A  # noqa: E402
from r5_codim4_face_realizability import partition_rows  # noqa: E402


def solve_closure(active_rows):
    A0, D0, tags = fixed_A(5)
    A = np.asarray(A0, dtype=float)
    D = np.asarray(D0, dtype=float)
    active = set(active_rows)
    # variables p15,x6,z6,epsilon
    inequalities = []
    for gap in partition_rows():
        inequalities.append(list(gap) + [0.0] * 13)
    for i in range(30):
        if i not in active:
            inequalities.append(list(-D[i]) + list(A[i]) + [0.0] * 6 + [1.0])
        inequalities.append(list(-D[i]) + [0.0] * 6 + list(A[i]) + [1.0])
    equalities = []
    equalities.append([1.0] * 5 + [1.0] * 5 + [-1.0] * 5 + [0.0] * 13)
    equalities.append([0.0] * 10 + [1.0] * 5 + [0.0] * 13)
    for i in active_rows:
        equalities.append(list(-D[i]) + list(A[i]) + [0.0] * 7)
    objective = [0.0] * 27 + [-1.0]
    result = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.zeros(len(inequalities)),
        A_eq=np.asarray(equalities),
        b_eq=np.asarray([0.0, 1.0] + [0.0] * len(active_rows)),
        bounds=[(None, None)] * 27 + [(0.0, None)],
        method="highs",
    )
    if not result.success or result.x[27] <= 1e-9:
        return None, result
    point = tuple(
        Fraction(str(float(value))).limit_denominator(1_000_000)
        for value in result.x
    )
    assert all(
        sum(Fraction(value) * point[i] for i, value in enumerate(row)) <= 0
        for row in inequalities
    )
    rhs = [Fraction(0), Fraction(1)] + [Fraction(0)] * len(active_rows)
    assert all(
        sum(Fraction(value) * point[i] for i, value in enumerate(row)) == value_rhs
        for row, value_rhs in zip(equalities, rhs)
    )
    return point, result


def main():
    active = (1, 2, 8, 9, 11, 12, 15)
    point, result = solve_closure(active)
    print(f"status={result.status} float_epsilon={None if result.x is None else result.x[27]}")
    if point is None:
        print("NO_STRICT_WITNESS")
        return
    print("PASS")
    print(f"active_rows={active}")
    print(f"lambda={point[:5]}")
    print(f"mu={point[5:10]}")
    print(f"nu={point[10:15]}")
    print(f"face_point={point[15:21]}")
    print(f"interior_point={point[21:27]}")
    print(f"epsilon={point[27]}")


if __name__ == "__main__":
    main()
