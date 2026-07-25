#!/usr/bin/env python3
"""Fast exact local-overlap census for saturated 3-ray hive normal cones."""

from fractions import Fraction
from functools import reduce
from itertools import combinations
from math import gcd
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "engine"))
from hive_poly import build  # noqa: E402


def primitive(v):
    g = reduce(gcd, (abs(x) for x in v if x), 0)
    return tuple(x // g for x in v) if g else tuple(v)


def hive_normals(n):
    A, _b, _d, interior, ok = build((0,) * n, (0,) * n, (0,) * n)
    assert ok
    return list(dict.fromkeys(primitive(a) for a in A)), interior


def det3(rows, js):
    a, b, c = (rows[0][j] for j in js)
    d, e, f = (rows[1][j] for j in js)
    h, i, j = (rows[2][j] for j in js)
    return a * (e * j - f * i) - b * (d * j - f * h) + c * (d * i - e * h)


def saturation_index(rows):
    cols = sorted({j for r in rows for j, x in enumerate(r) if x})
    g = 0
    for js in combinations(cols, 3):
        g = gcd(g, abs(det3(rows, js)))
        if g == 1:
            return 1
    return g


def gram_data(rows):
    dot = lambda u, v: sum(x * y for x, y in zip(u, v))
    a, b, c = (dot(r, r) for r in rows)
    p, q, r = dot(rows[0], rows[1]), dot(rows[0], rows[2]), dot(rows[1], rows[2])
    det = a * b * c + 2 * p * q * r - a * r * r - b * q * q - c * p * p
    return a, b, c, p, q, r, det


def bv_alpha_saturated(rows):
    a, b, c, p, q, r, det = gram_data(rows)
    if not det or saturation_index(rows) != 1:
        return None
    cof = (
        (b * c - r * r, q * r - p * c, p * r - b * q),
        (q * r - p * c, a * c - q * q, p * q - a * r),
        (p * r - b * q, p * q - a * r, a * b - p * p),
    )
    ans = Fraction(1, 8)
    for i, j in combinations(range(3), 2):
        ans += Fraction(cof[i][j], 24) * (
            Fraction(1, cof[i][i]) + Fraction(1, cof[j][j])
        )
    return ans


def canonical_gram(rows):
    # Permutation-invariant encoding of the labeled Gram matrix.
    gd = gram_data(rows)[:6]
    a, b, c, p, q, r = gd
    mats = []
    for perm in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
        G = ((a, p, q), (p, b, r), (q, r, c))
        mats.append(tuple(G[perm[i]][perm[j]] for i in range(3) for j in range(3)))
    return min(mats)


def support_signature(rows):
    ss = [set(j for j, x in enumerate(row) if x) for row in rows]
    return (tuple(sorted(map(len, ss))),
            tuple(sorted(len(ss[i] & ss[j]) for i, j in combinations(range(3), 2))),
            len(ss[0] & ss[1] & ss[2]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    normals, interior = hive_normals(args.n)
    counts = {"dependent": 0, "nonsaturated": 0, "saturated": 0, "negative": 0, "zero": 0}
    grams = {}
    minima = []
    for ids in combinations(range(len(normals)), 3):
        rows = tuple(normals[i] for i in ids)
        if gram_data(rows)[-1] == 0:
            counts["dependent"] += 1
            continue
        idx = saturation_index(rows)
        if idx != 1:
            counts["nonsaturated"] += 1
            continue
        counts["saturated"] += 1
        alpha = bv_alpha_saturated(rows)
        counts["negative"] += alpha < 0
        counts["zero"] += alpha == 0
        key = canonical_gram(rows)
        grams.setdefault(key, {"alpha": alpha, "count": 0, "example": (ids, rows)})["count"] += 1
        minima.append((alpha, ids, rows, support_signature(rows), key))
    minima.sort(key=lambda z: z[0])
    print(json.dumps({
        "n": args.n,
        "ambient_dimension": len(interior),
        "normal_count": len(normals),
        **counts,
        "unique_saturated_gram_types": len(grams),
        "alpha_values": sorted({str(v["alpha"]) for v in grams.values()}),
        "minimum": str(minima[0][0]) if minima else None,
        "minimizers": [
            {"alpha": str(x[0]), "ids": x[1], "rows": x[2], "signature": x[3], "gram": x[4]}
            for x in minima[:args.top]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
