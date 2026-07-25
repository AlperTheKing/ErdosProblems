#!/usr/bin/env python3
"""Exact audit of every negative saturated rank-5 normal quadruple.

Pipeline:

1. Rebuild the 27 oriented rank-5 hive normals.
2. Use the independent defining-recursion BV implementation to identify all
   saturated quadruples with alpha^BV<0.
3. Expand each normal tuple to every tuple of original rhombus rows (there are
   duplicated normal directions).
4. Starting from the four vanishing target slacks, compute consequences in the
   cone of 15 nonnegative partition gaps and 30 nonnegative rhombus slacks.
   Every new zero is backed by an exactly replayed Farkas identity

       q_j + sum a_k q_k + sum b_z q_z + c*weight = 0,  a_k >= 0.

5. Certify that each negative row quadruple forces hive normals of rank at
   least five.  Hence none is the normal cone of a codimension-four face of a
   full-dimensional rank-5 hive polytope.

Floating point is used only to locate sparse Farkas coefficients; every
identity and every BV sign is checked over Fraction before it affects PASS.
"""

from fractions import Fraction
from itertools import combinations, product
import os
import sys

import numpy as np
from scipy.optimize import linprog


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "r5_rational"))
from hiveR import fixed_A, rank_q  # noqa: E402

import r5_codim4_bv_independent as bv  # noqa: E402
from r5_codim4_bv_independent_v2 import alpha_two_directions  # noqa: E402
from r5_codim4_face_realizability import partition_rows  # noqa: E402


def make_nonnegative_forms():
    A, D, tags = fixed_A(5)
    forms = []
    labels = []
    for i, row in enumerate(partition_rows()):
        forms.append(tuple(-value for value in row) + (0,) * 6)
        labels.append(("gap", i))
    for i, (a, d) in enumerate(zip(A, D)):
        forms.append(tuple(d) + tuple(-value for value in a))
        labels.append(("slack", i))
    weight = tuple([1] * 5 + [1] * 5 + [-1] * 5 + [0] * 6)
    return A, tags, tuple(forms), tuple(labels), weight


def exact_sum(columns, coefficients, target):
    total = [Fraction(value) for value in target]
    for coefficient, column in zip(coefficients, columns):
        for i, value in enumerate(column):
            total[i] += coefficient * value
    return tuple(total)


def force_certificate(candidate, zero, forms, weight):
    """Return an exact certificate that q_candidate is forced zero, or None."""
    nonzero = tuple(i for i in range(len(forms)) if i not in zero)
    zero = tuple(sorted(zero))
    columns = [forms[i] for i in nonzero] + [forms[i] for i in zero] + [weight]
    number_nonnegative = len(nonzero)
    matrix = np.asarray(columns, dtype=float).T
    rhs = -np.asarray(forms[candidate], dtype=float)
    objective = np.asarray(
        [1.0] * number_nonnegative + [0.0] * (len(columns) - number_nonnegative)
    )
    bounds = (
        [(0.0, None)] * number_nonnegative
        + [(None, None)] * (len(columns) - number_nonnegative)
    )
    result = linprog(
        objective,
        A_eq=matrix,
        b_eq=rhs,
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        return None
    coefficients = tuple(
        Fraction(str(float(value))).limit_denominator(1_000_000)
        for value in result.x
    )
    if any(coefficients[i] < 0 for i in range(number_nonnegative)):
        return None
    if any(exact_sum(columns, coefficients, forms[candidate])):
        return None
    support = []
    for coefficient, index in zip(coefficients[:number_nonnegative], nonzero):
        if coefficient:
            support.append((index, coefficient, "nonnegative"))
    offset = number_nonnegative
    for coefficient, index in zip(coefficients[offset:offset + len(zero)], zero):
        if coefficient:
            support.append((index, coefficient, "zero"))
    if coefficients[-1]:
        support.append((-1, coefficients[-1], "weight"))
    return tuple(support)


def closure_to_rank_five(target_rows, A, forms, labels, weight):
    zero = {15 + row for row in target_rows}
    certificates = []
    assert rank_q([A[row] for row in target_rows]) == 4
    while True:
        zero_hive_rows = sorted(index - 15 for index in zero if index >= 15)
        current_rank = rank_q([A[row] for row in zero_hive_rows])
        if current_rank >= 5:
            return zero, certificates, current_rank

        found = False
        # Rank-raising hive slacks are tried first; partition gaps and
        # rank-preserving slacks remain available as intermediate consequences.
        candidates = [
            index for index in range(15, 45) if index not in zero
            and rank_q([A[row] for row in zero_hive_rows] + [A[index - 15]]) > current_rank
        ]
        candidates += [
            index for index in range(45) if index not in zero and index not in candidates
        ]
        for candidate in candidates:
            certificate = force_certificate(candidate, zero, forms, weight)
            if certificate is None:
                continue
            zero.add(candidate)
            certificates.append((candidate, labels[candidate], certificate))
            found = True
            break
        if not found:
            return zero, certificates, current_rank


def negative_normal_tuples(normals):
    records = []
    for ids in combinations(range(len(normals)), 4):
        rows = tuple(normals[i] for i in ids)
        if bv.saturation_index(rows) != 1:
            continue
        ray_gram = bv.inverse(bv.normal_gram(rows))
        alpha = alpha_two_directions(ray_gram, ids)
        if alpha < 0:
            records.append((ids, alpha))
    return records


def main():
    bv.self_test()
    normals, _ = bv.rank5_hive_normals()
    A, tags, forms, labels, weight = make_nonnegative_forms()
    by_normal = {normal: [] for normal in normals}
    for row, normal in enumerate(map(tuple, A)):
        by_normal[normal].append(row)
    assert all(by_normal[normal] for normal in normals)

    negative = negative_normal_tuples(normals)
    assert len(negative) == 132
    expanded = []
    for ids, alpha in negative:
        choices = [by_normal[normals[i]] for i in ids]
        for target_rows in product(*choices):
            expanded.append((ids, alpha, tuple(target_rows)))
    assert len(expanded) == 164

    failures = []
    largest_certificate_chain = 0
    examples = []
    for ids, alpha, target_rows in expanded:
        zero, certificates, closure_rank = closure_to_rank_five(
            target_rows, A, forms, labels, weight
        )
        largest_certificate_chain = max(largest_certificate_chain, len(certificates))
        if closure_rank < 5:
            failures.append((ids, alpha, target_rows, zero, certificates, closure_rank))
        if len(examples) < 12:
            zero_hive = tuple(sorted(index - 15 for index in zero if index >= 15))
            examples.append((ids, alpha, target_rows, zero_hive, closure_rank, certificates))

    assert not failures, failures[:1]
    print("PASS")
    print(f"normal_sha256={bv.EXPECTED_NORMAL_SHA256}")
    print(f"negative_saturated_normal_quadruples={len(negative)}")
    print(f"expanded_original_row_quadruples={len(expanded)}")
    print(f"all_forced_closure_rank_at_least=5")
    print(f"largest_certificate_chain={largest_certificate_chain}")
    print("examples=")
    for record in examples:
        print(f"  {record}")


if __name__ == "__main__":
    main()
