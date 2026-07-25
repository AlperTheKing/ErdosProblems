#!/usr/bin/env python3
"""Finite exact normal/determinant atlas for size-5 hive polytopes.

This is deliberately only a structural gate.  It does not enumerate boundary
partitions or search for a KTT counterexample.  All arithmetic is over Z.
"""

from collections import Counter
from itertools import combinations
import json
from math import gcd


N = 5


def primitive(row):
    g = 0
    for x in row:
        g = gcd(g, abs(x))
    assert g > 0
    return tuple(x // g for x in row)


def build_normal_rows():
    interior = [
        (x, y)
        for x in range(1, N)
        for y in range(1, N)
        if x + y <= N - 1
    ]
    index = {p: i for i, p in enumerate(interior)}
    rows = []
    boundary_only = 0

    def add(plus, minus):
        nonlocal boundary_only
        row = [0] * len(interior)
        for p in plus:
            if p in index:
                row[index[p]] -= 1
        for p in minus:
            if p in index:
                row[index[p]] += 1
        if not any(row):
            boundary_only += 1
        else:
            rows.append(primitive(row))

    for x in range(N + 1):
        for y in range(N + 1):
            if x + y <= N - 2:
                add([(x + 1, y), (x, y + 1)],
                    [(x, y), (x + 1, y + 1)])
            if y >= 1 and x + y <= N - 1:
                add([(x, y), (x + 1, y)],
                    [(x, y + 1), (x + 1, y - 1)])
            if x >= 1 and x + y <= N - 1:
                add([(x, y), (x, y + 1)],
                    [(x + 1, y), (x - 1, y + 1)])
    return interior, rows, boundary_only


def det_bareiss(matrix):
    """Exact determinant of a square integer matrix."""
    a = [list(row) for row in matrix]
    n = len(a)
    if n == 0:
        return 1
    sign = 1
    previous = 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                assert numerator % previous == 0
                a[i][j] = numerator // previous
        previous = pivot
        for i in range(k + 1, n):
            a[i][k] = 0
    return sign * a[n - 1][n - 1]


def main():
    interior, rows, boundary_only = build_normal_rows()
    assert len(interior) == 6
    assert len(rows) == 30
    unique = sorted(set(rows))
    assert len(unique) == 27
    multiplicities = Counter(rows)
    assert Counter(multiplicities.values()) == Counter({1: 24, 2: 3})

    hist = Counter()
    for basis in combinations(unique, 6):
        hist[abs(det_bareiss(basis))] += 1
    assert sum(hist.values()) == 296010

    result = {
        "r": N,
        "ambient_dimension": len(interior),
        "interior_coordinates": [list(p) for p in interior],
        "nonconstant_rhombus_rows": len(rows),
        "boundary_only_rhombi": boundary_only,
        "unique_primitive_oriented_normals": len(unique),
        "normal_multiplicity_histogram": {
            str(k): v for k, v in sorted(Counter(multiplicities.values()).items())
        },
        "six_subsets": sum(hist.values()),
        "absolute_determinant_histogram": {
            str(k): v for k, v in sorted(hist.items())
        },
        "maximum_absolute_determinant": max(hist),
        "nonzero_basis_count": sum(v for k, v in hist.items() if k),
        "unique_normals": [list(row) for row in unique],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
