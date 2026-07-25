#!/usr/bin/env python3
"""Corrected driver: duplicated normals expand 132 negative tuples to 192 rows."""

from itertools import product

import r5_codim4_bv_independent as bv
import r5_codim4_negative_realizability_audit as audit


def main():
    bv.self_test()
    normals, _ = bv.rank5_hive_normals()
    A, tags, forms, labels, weight = audit.make_nonnegative_forms()
    by_normal = {normal: [] for normal in normals}
    for row, normal in enumerate(map(tuple, A)):
        by_normal[normal].append(row)

    negative = audit.negative_normal_tuples(normals)
    assert len(negative) == 132
    expanded = []
    for ids, alpha in negative:
        for target_rows in product(*(by_normal[normals[i]] for i in ids)):
            expanded.append((ids, alpha, tuple(target_rows)))
    assert len(expanded) == 192

    failures = []
    largest_certificate_chain = 0
    rank_histogram = {}
    examples = []
    for ids, alpha, target_rows in expanded:
        zero, certificates, closure_rank = audit.closure_to_rank_five(
            target_rows, A, forms, labels, weight
        )
        largest_certificate_chain = max(largest_certificate_chain, len(certificates))
        rank_histogram[closure_rank] = rank_histogram.get(closure_rank, 0) + 1
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
    print(f"closure_rank_histogram={rank_histogram}")
    print(f"largest_certificate_chain={largest_certificate_chain}")
    print("examples=")
    for record in examples:
        print(f"  {record}")


if __name__ == "__main__":
    main()
