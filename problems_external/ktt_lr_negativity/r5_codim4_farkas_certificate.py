#!/usr/bin/env python3
"""Exact Farkas certificates for the negative tuple's forced closure.

Nonnegative forms are the fifteen partition gaps and thirty hive slacks.  For
each extra forced hive row j this script finds and verifies an identity

    slack_j + sum_q a_q q + sum_{t in T} b_t slack_t + c*weight = 0,

where a_q >= 0 and T={10,12,14,19}.  Therefore vanishing of the four target
slacks forces slack_j=0.  The certificate is homogeneous; normalization and
floating-point optimization play no role in the exact replay.
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


TARGET_ROWS = (10, 12, 14, 19)
EXTRA_FORCED_ROWS = (3, 4, 15)


def forms():
    A, D, tags = fixed_A(5)
    gap_forms = []
    for row in partition_rows():
        gap_forms.append(tuple(-value for value in row) + (0,) * 6)
    slack_forms = [
        tuple(D[i]) + tuple(-value for value in A[i])
        for i in range(len(A))
    ]
    weight = tuple([1] * 5 + [1] * 5 + [-1] * 5 + [0] * 6)
    return A, tags, gap_forms, slack_forms, weight


def rationalize(value):
    return Fraction(str(float(value))).limit_denominator(1_000_000)


def solve_one(target_row, gap_forms, slack_forms, weight):
    nonnegative = []
    labels = []
    for i, form in enumerate(gap_forms):
        nonnegative.append(form)
        labels.append(("gap", i))
    for i, form in enumerate(slack_forms):
        if i not in TARGET_ROWS:
            nonnegative.append(form)
            labels.append(("slack", i))
    free = [slack_forms[i] for i in TARGET_ROWS] + [weight]
    all_columns = nonnegative + free
    matrix = np.asarray(all_columns, dtype=float).T
    rhs = -np.asarray(slack_forms[target_row], dtype=float)
    objective = np.asarray([1.0] * len(nonnegative) + [0.0] * len(free))
    bounds = [(0.0, None)] * len(nonnegative) + [(None, None)] * len(free)
    result = linprog(
        objective,
        A_eq=matrix,
        b_eq=rhs,
        bounds=bounds,
        method="highs",
    )
    assert result.success, result.message
    coefficients = tuple(rationalize(value) for value in result.x)

    total = [Fraction(value) for value in slack_forms[target_row]]
    for coefficient, form in zip(coefficients, all_columns):
        for i, value in enumerate(form):
            total[i] += coefficient * value
    assert all(value == 0 for value in total), (target_row, total)
    assert all(coefficients[i] >= 0 for i in range(len(nonnegative)))

    terms = []
    for coefficient, label in zip(coefficients[:len(nonnegative)], labels):
        if coefficient:
            terms.append((label, coefficient))
    for coefficient, row in zip(
        coefficients[len(nonnegative):len(nonnegative) + len(TARGET_ROWS)],
        TARGET_ROWS,
    ):
        if coefficient:
            terms.append((("target_slack", row), coefficient))
    if coefficients[-1]:
        terms.append((("weight", None), coefficients[-1]))
    return terms


def main():
    A, tags, gap_forms, slack_forms, weight = forms()
    print("PASS")
    print(f"target_rows={TARGET_ROWS}")
    for row in EXTRA_FORCED_ROWS:
        terms = solve_one(row, gap_forms, slack_forms, weight)
        print(f"forced_row={row} tag={tags[row]} identity_terms={terms}")
    closure = list(TARGET_ROWS) + list(EXTRA_FORCED_ROWS)
    print(f"closure_rows={tuple(sorted(closure))}")
    print(f"closure_rank={rank_q([A[i] for i in closure])}")


if __name__ == "__main__":
    main()
