#!/usr/bin/env python3
"""Diagnostic driver retaining rank-four forced closures for cone valuation."""

from collections import Counter
from itertools import product

import r5_codim4_bv_independent as bv
import r5_codim4_negative_realizability_audit as audit


def main():
    normals, _ = bv.rank5_hive_normals()
    A, tags, forms, labels, weight = audit.make_nonnegative_forms()
    by_normal = {normal: [] for normal in normals}
    for row, normal in enumerate(map(tuple, A)):
        by_normal[normal].append(row)
    negative = audit.negative_normal_tuples(normals)
    expanded = [
        (ids, alpha, tuple(rows))
        for ids, alpha in negative
        for rows in product(*(by_normal[normals[i]] for i in ids))
    ]
    residual = []
    histogram = Counter()
    for ids, alpha, target_rows in expanded:
        zero, certificates, closure_rank = audit.closure_to_rank_five(
            target_rows, A, forms, labels, weight
        )
        histogram[closure_rank] += 1
        if closure_rank < 5:
            zero_hive = tuple(sorted(index - 15 for index in zero if index >= 15))
            zero_normal_ids = tuple(sorted({normals.index(tuple(A[i])) for i in zero_hive}))
            residual.append((
                ids, alpha, target_rows, zero_hive, zero_normal_ids,
                tuple(tags[i] for i in zero_hive), certificates,
            ))
    print("PASS_DIAGNOSTIC")
    print(f"expanded={len(expanded)} closure_rank_histogram={dict(histogram)}")
    print(f"residual_rank4={len(residual)}")
    print(f"unique_residual_normal_cones={len({r[4] for r in residual})}")
    for record in residual:
        print(record)


if __name__ == "__main__":
    main()
