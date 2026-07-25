#!/usr/bin/env python3
"""Exact non-binary obstruction in the size-four hive-normal matroid.

The four displayed primitive rhombus normals span a rank-two restriction in
which every pair is independent.  Thus the restriction is U_{2,4}.  Since a
binary rank-two vector space has only three nonzero projective points,
U_{2,4} is not binary.  In particular the full hive-normal matroid is neither
graphic, cographic, nor regular.

This script also verifies that all four vectors occur in the independently
generated size-four hive-normal atlas.
"""

from itertools import combinations
from pathlib import Path
import sys

from sympy import Matrix


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "alcoved_probe"))
from hive_normals import rows_for_r  # noqa: E402


VECTORS = (
    (-1, -1, 1),
    (-1, 0, 0),
    (-1, 1, -1),
    (0, -1, 1),
)


def rank(rows):
    return Matrix(rows).rank()


def main():
    _, rows = rows_for_r(4)
    atlas = set(rows)

    assert all(v in atlas for v in VECTORS)
    assert rank(VECTORS) == 2
    assert all(rank((VECTORS[i], VECTORS[j])) == 2
               for i, j in combinations(range(4), 2))

    # Two exact relations make the rank-two plane transparent.
    v1, v2, v3, v4 = VECTORS
    assert tuple(v2[i] + v4[i] for i in range(3)) == v1
    assert tuple(v2[i] - v4[i] for i in range(3)) == v3

    print("size4_distinct_normals=%d" % len(atlas))
    print("restriction_vectors=%r" % (VECTORS,))
    print("restriction_rank=2")
    print("pair_ranks=2")
    print("restriction_matroid=U_2_4")
    print("binary=false")
    print("graphic=false")
    print("cographic=false")
    print("regular=false")
    print("status=PASS")


if __name__ == "__main__":
    main()
