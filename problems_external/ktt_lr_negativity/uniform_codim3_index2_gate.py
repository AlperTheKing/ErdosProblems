#!/usr/bin/env python3
"""Exact BV-alpha gate for index-two simplicial hive normal triples.

If the three outward normals span an index-two sublattice, their polar lattice
in dual coordinates is L = image(N: Z^d -> Z^3), the kernel of one nonzero
parity form a.y=0 mod 2.  The primitive coordinate rays are t_i e_i, with
t_i=2 iff a_i=1.  The support of a gives a canonical unimodular subdivision:

  |supp(a)|=1: already unimodular;
  |supp(a)|=2: split the corresponding boundary edge at e_i+e_j;
  |supp(a)|=3: use the three edge midpoints, giving four triangles.

The script evaluates the Lee--Liu codimension-2/3 formulas on every cell and
uses the BV valuation (subtracting internal two-cones).  All arithmetic is Q.
"""

from fractions import Fraction
from itertools import combinations
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uniform_codim3_fast_gate as base  # noqa: E402


def inv_gram(rows):
    a, b, c, p, q, r, det = base.gram_data(rows)
    cof = (
        (b * c - r * r, q * r - p * c, p * r - b * q),
        (q * r - p * c, a * c - q * q, p * q - a * r),
        (p * r - b * q, p * q - a * r, a * b - p * p),
    )
    return tuple(tuple(Fraction(cof[i][j], det) for j in range(3)) for i in range(3))


def dot(M, x, y):
    return sum(Fraction(x[i]) * M[i][j] * y[j] for i in range(3) for j in range(3))


def alpha2(M, rays):
    u, v = rays
    uv, uu, vv = dot(M, u, v), dot(M, u, u), dot(M, v, v)
    return Fraction(1, 4) + Fraction(1, 12) * uv * (1 / uu + 1 / vv)


def alpha3(M, rays):
    ans = Fraction(1, 8)
    for i, j in combinations(range(3), 2):
        uv = dot(M, rays[i], rays[j])
        ans += Fraction(1, 24) * uv * (
            1 / dot(M, rays[i], rays[i]) + 1 / dot(M, rays[j], rays[j])
        )
    return ans


def parity_vector(rows):
    for mask in range(1, 8):
        a = tuple((mask >> i) & 1 for i in range(3))
        if all(sum(a[i] * rows[i][j] for i in range(3)) % 2 == 0 for j in range(len(rows[0]))):
            return a
    raise AssertionError("index-two triple has no parity covector")


def relative_index(rays):
    # L has index two in Z^3, so relative determinant is |det|/2.
    return abs(base.det3(tuple(tuple(r[j] for r in rays) for j in range(3)), (0, 1, 2))) // 2


def alpha_index2(rows):
    M = inv_gram(rows)
    a = parity_vector(rows)
    e = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    ray = tuple(tuple((2 if a[i] else 1) * x for x in e[i]) for i in range(3))
    supp = tuple(i for i, x in enumerate(a) if x)
    if len(supp) == 1:
        cells, internal = (ray,), ()
    elif len(supp) == 2:
        i, j = supp
        k = next(x for x in range(3) if x not in supp)
        v = tuple(e[i][x] + e[j][x] for x in range(3))
        cells = ((ray[i], v, ray[k]), (v, ray[j], ray[k]))
        internal = ((v, ray[k]),)
    else:
        v01, v02, v12 = (1, 1, 0), (1, 0, 1), (0, 1, 1)
        cells = (
            (ray[0], v01, v02),
            (ray[1], v01, v12),
            (ray[2], v02, v12),
            (v01, v02, v12),
        )
        internal = ((v01, v02), (v01, v12), (v02, v12))
    assert all(relative_index(cell) == 1 for cell in cells)
    return sum(alpha3(M, cell) for cell in cells) - sum(alpha2(M, face) for face in internal), a, cells, internal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    normals, interior = base.hive_normals(args.n)
    vals = []
    for ids in combinations(range(len(normals)), 3):
        rows = tuple(normals[i] for i in ids)
        if base.gram_data(rows)[-1] and base.saturation_index(rows) == 2:
            alpha, parity, cells, internal = alpha_index2(rows)
            vals.append((alpha, ids, rows, parity, cells, internal))
    vals.sort(key=lambda z: z[0])
    print(json.dumps({
        "n": args.n,
        "ambient_dimension": len(interior),
        "index2_count": len(vals),
        "negative": sum(x[0] < 0 for x in vals),
        "zero": sum(x[0] == 0 for x in vals),
        "minimum": str(vals[0][0]) if vals else None,
        "minimizers": [
            {"alpha": str(x[0]), "ids": x[1], "rows": x[2], "parity": x[3],
             "cells": x[4], "internal_faces": x[5]}
            for x in vals[:args.top]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
