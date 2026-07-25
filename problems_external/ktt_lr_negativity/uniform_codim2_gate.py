#!/usr/bin/env python3
"""Exact structural checks for rank-uniform codimension-two hive cones.

This script is an independent finite audit of the local classification used in
UNIFORM_CODIM2_POSITIVITY.md.  It is not the proof: the proof uses only the
four-point support of a rhombus row.  The computations below check the exact
saturation index and the Berline--Vergne constant for ranks 3 through 20.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import gcd


def primitive(row):
    g = 0
    for x in row:
        g = gcd(g, abs(x))
    if g == 0:
        return None
    return tuple(x // g for x in row)


def normal_rows(n):
    interior = [
        (x, y)
        for x in range(1, n)
        for y in range(1, n)
        if x + y <= n - 1
    ]
    index = {p: i for i, p in enumerate(interior)}
    rows = []

    def add(plus, minus):
        row = [0] * len(interior)
        for p in plus:
            if p in index:
                row[index[p]] -= 1
        for p in minus:
            if p in index:
                row[index[p]] += 1
        row = primitive(row)
        if row is not None:
            rows.append(row)

    for x in range(n + 1):
        for y in range(n + 1):
            if x + y <= n - 2:
                add([(x + 1, y), (x, y + 1)],
                    [(x, y), (x + 1, y + 1)])
            if y >= 1 and x + y <= n - 1:
                add([(x, y), (x + 1, y)],
                    [(x, y + 1), (x + 1, y - 1)])
            if x >= 1 and x + y <= n - 1:
                add([(x, y), (x, y + 1)],
                    [(x + 1, y), (x - 1, y + 1)])
    return sorted(set(rows))


def pair_index(u, v):
    g = 0
    for i, j in combinations(range(len(u)), 2):
        g = gcd(g, abs(u[i] * v[j] - u[j] * v[i]))
    return g


def alpha(u, v):
    """BV constant for the two-dimensional transverse feasible cone.

    For index 1 this is the standard unimodular formula.  For index 2 the
    unique nonzero half-open parallelogram point is (a+b)/2, and direct local
    Euler--Maclaurin expansion halves the metric correction.  Normal and
    feasible ray inner products have opposite signs.
    """
    q = pair_index(u, v)
    assert q in (1, 2)
    a = sum(x * x for x in u)
    b = sum(x * x for x in v)
    c = sum(x * y for x, y in zip(u, v))
    return Fraction(1, 4) - Fraction(c, 12 * q) * (Fraction(1, a) + Fraction(1, b))


def main():
    global_types = set()
    for n in range(3, 21):
        rows = normal_rows(n)
        hist = Counter()
        minimum = None
        for u, v in combinations(rows, 2):
            q = pair_index(u, v)
            if q == 0:  # opposite normals
                continue
            aa = sum(x * x for x in u)
            bb = sum(x * x for x in v)
            cc = sum(x * y for x, y in zip(u, v))
            typ = (q, min(aa, bb), max(aa, bb), cc)
            global_types.add(typ)
            value = alpha(u, v)
            hist[(q, value)] += 1
            minimum = value if minimum is None else min(minimum, value)
        assert minimum is not None and minimum >= Fraction(1, 9)
        if n == 5:
            assert sum(count for (q, _), count in hist.items() if q == 1) == 339
            assert hist[(2, Fraction(5, 18))] == 3
            assert minimum == Fraction(1, 9)
        print(f"r={n} normals={len(rows)} min_alpha={minimum} index_hist="
              f"{dict(sorted(Counter(q for q, _ in hist.elements()).items()))}")
    print(f"PASS invariant_types={len(global_types)} min={min(alpha_from_type(t) for t in global_types)}")
    for typ in sorted(global_types):
        print(typ, alpha_from_type(typ))


def alpha_from_type(typ):
    q, a, b, c = typ
    return Fraction(1, 4) - Fraction(c, 12 * q) * (Fraction(1, a) + Fraction(1, b))


if __name__ == "__main__":
    main()
