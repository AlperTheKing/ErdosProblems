#!/usr/bin/env python3
"""Robust driver for the independent rank-5 codimension-4 BV census.

The underlying implementation is in ``r5_codim4_bv_independent.py``.  This
driver retries generic one-variable specializations when an intermediate
Schur-complement coordinate vanishes.
"""

from collections import Counter
from itertools import combinations

import r5_codim4_bv_independent as core


def alpha_two_directions(ray_gram, ids):
    values = []
    for prime in (17, 23, 29, 31, 37, 41, 43, 47, 53, 59):
        direction = tuple(prime ** i for i in range(4))
        try:
            value = core.mu_alpha(ray_gram, direction)
        except AssertionError as error:
            # Only a zero transverse coordinate is an allowed retry.  Any
            # failed regularity cancellation or other assertion remains fatal.
            if error.args:
                raise
            continue
        values.append(value)
        if len(values) == 2:
            break
    assert len(values) == 2, ids
    assert values[0] == values[1], (ids, values)
    return values[0]


def main():
    core.self_test()
    normals, interior = core.rank5_hive_normals()
    counts = Counter()
    records = []
    for ids in combinations(range(len(normals)), 4):
        rows = tuple(normals[i] for i in ids)
        index = core.saturation_index(rows)
        if not index:
            counts["dependent"] += 1
            continue
        if index != 1:
            counts[f"index_{index}"] += 1
            continue
        counts["saturated"] += 1
        normal_gram = core.normal_gram(rows)
        ray_gram = core.inverse(normal_gram)
        alpha = alpha_two_directions(ray_gram, ids)
        counts["negative"] += alpha < 0
        counts["zero"] += alpha == 0
        records.append((alpha, ids, rows, normal_gram, ray_gram))

    records.sort(key=lambda record: (record[0], record[1]))
    print("PASS")
    print(f"interior={interior}")
    print(f"normal_sha256={core.EXPECTED_NORMAL_SHA256}")
    print(f"counts={dict(counts)}")
    print(f"minimum={records[0][0]}")
    print("lowest_records=")
    for alpha, ids, rows, normal_gram, ray_gram in records[:20]:
        print(f"  alpha={alpha} ids={ids}")
        print(f"    rows={rows}")
        print(f"    normal_gram={normal_gram}")
        print(f"    ray_gram={ray_gram}")


if __name__ == "__main__":
    main()
