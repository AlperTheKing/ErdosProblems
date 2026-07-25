#!/usr/bin/env python3
"""Compute the forced active closure of the most-negative r=5 normal tuple.

All individual LP optima are replayed exactly after rationalizing a HiGHS
candidate.  A row is marked forced when its maximum possible slack is zero
under partition boundary data, weight balance, normalization, hive
feasibility, and the four target equalities.
"""

from fractions import Fraction
import os
import sys

import numpy as np
from scipy.optimize import linprog


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "r5_rational"))
from hiveR import fixed_A, rank_q  # noqa: E402

from r5_codim4_face_realizability import partition_rows  # noqa: E402


RANK = 5
TARGET_ROWS = (10, 12, 14, 19)


def system():
    A, D, tags = fixed_A(RANK)
    # y=(p[15],x[6])
    inequalities = []
    for row in partition_rows():
        inequalities.append(row + [0] * 6)
    hive_rows = []
    for a, d in zip(A, D):
        row = [-value for value in d] + list(a)
        inequalities.append(row)
        hive_rows.append(row)

    equalities = []
    weight = [1] * 5 + [1] * 5 + [-1] * 5 + [0] * 6
    normalize = [0] * 10 + [1] * 5 + [0] * 6
    equalities.extend((weight, normalize))
    for i in TARGET_ROWS:
        equalities.append(hive_rows[i])
    rhs = [0, 1] + [0] * len(TARGET_ROWS)
    return A, D, tags, inequalities, hive_rows, equalities, rhs


def rationalize(vector):
    return tuple(
        Fraction(str(float(value))).limit_denominator(1_000_000)
        for value in vector
    )


def dot(row, vector):
    return sum(Fraction(value) * vector[i] for i, value in enumerate(row))


def exact_feasible(point, inequalities, equalities, rhs):
    return (
        all(dot(row, point) <= 0 for row in inequalities)
        and all(dot(row, point) == value for row, value in zip(equalities, rhs))
    )


def main():
    A, D, tags, inequalities, hive_rows, equalities, rhs = system()
    Aub = np.asarray(inequalities, dtype=float)
    bub = np.zeros(len(inequalities))
    Aeq = np.asarray(equalities, dtype=float)
    beq = np.asarray(rhs, dtype=float)
    bounds = [(None, None)] * 21

    forced = []
    records = []
    for i, row in enumerate(hive_rows):
        objective = np.asarray(row, dtype=float)  # min row.y = -max slack
        result = linprog(
            objective,
            A_ub=Aub,
            b_ub=bub,
            A_eq=Aeq,
            b_eq=beq,
            bounds=bounds,
            method="highs",
        )
        assert result.success, (i, result.message)
        point = rationalize(result.x)
        assert exact_feasible(point, inequalities, equalities, rhs), i
        exact_value = dot(row, point)
        assert exact_value <= 0
        maximum_slack = -exact_value
        # A float zero cannot prove forcedness, so preserve the exact candidate
        # plus dual data; the separate Farkas script certifies forced rows.
        float_optimum = float(result.fun)
        if abs(float_optimum) < 1e-9:
            forced.append(i)
        records.append((i, tags[i], maximum_slack, float_optimum))

    forced_normals = [A[i] for i in forced]
    print("PASS_CANDIDATE")
    print(f"target_rows={TARGET_ROWS}")
    print(f"forced_rows={tuple(forced)}")
    print(f"forced_tags={tuple(tags[i] for i in forced)}")
    print(f"forced_normal_rank={rank_q(forced_normals)}")
    print("row_slack_maxima=")
    for record in records:
        print(f"  {record}")


if __name__ == "__main__":
    main()
