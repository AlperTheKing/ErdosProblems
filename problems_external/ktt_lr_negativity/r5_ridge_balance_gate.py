#!/usr/bin/env python3
"""Exact codimension-two balance-space gate for full-dimensional r=5 hives.

For each possible ridge type {i,j}, the primitive restriction of normal n_j
to facet i is represented by primitive(n_i wedge n_j).  Minkowski boundary
balance in every facet therefore gives an integer linear map B on total
normalized ridge-volume vectors.  This script computes rank(B) exactly.
"""

from itertools import combinations
from math import gcd

from sympy import Matrix

from r5_local_gate import build_normal_rows


def primitive_wedge(a, b):
    w = [
        a[i] * b[j] - a[j] * b[i]
        for i, j in combinations(range(len(a)), 2)
    ]
    g = 0
    for x in w:
        g = gcd(g, abs(x))
    if g == 0:
        return None
    return tuple(x // g for x in w)


def main():
    normals = sorted(set(build_normal_rows()[1]))
    assert len(normals) == 27
    wedge_dimension = 15
    pairs = []
    wedges = []
    for i, j in combinations(range(len(normals)), 2):
        w = primitive_wedge(normals[i], normals[j])
        if w is not None:
            pairs.append((i, j))
            wedges.append(w)

    # Nine pairs are opposite, hence cannot support a bounded ridge.
    assert len(pairs) == 342
    balance = [[0] * len(pairs) for _ in range(len(normals) * wedge_dimension)]
    for col, ((i, j), w) in enumerate(zip(pairs, wedges)):
        for t, value in enumerate(w):
            balance[i * wedge_dimension + t][col] = value
            balance[j * wedge_dimension + t][col] = -value

    rank = Matrix(balance).rank()  # exact rational elimination
    kernel_dimension = len(pairs) - rank
    assert rank == 120
    assert kernel_dimension == 222
    print("PASS")
    print(f"normals={len(normals)} ridge_types={len(pairs)}")
    print(f"balance_shape={len(balance)}x{len(pairs)}")
    print(f"balance_rank={rank} kernel_dimension={kernel_dimension}")


if __name__ == "__main__":
    main()
