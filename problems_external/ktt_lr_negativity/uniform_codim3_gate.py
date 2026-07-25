#!/usr/bin/env python3
"""Exact rank-local gate for simplicial codimension-three hive cones.

For three linearly independent outward rhombus normals n_1,n_2,n_3, let
G=(<n_i,n_j>).  If the rows n_i form a saturated basis of their rank-three
lattice, the primitive generators u_i of the polar pointed feasible cone have
Gram matrix G^{-1}.  Lee--Liu, Lemma 3.2, then gives

  alpha_BV = 1/8 + (1/24) sum_{i<j} <u_i,u_j>
                    (1/<u_i,u_i> + 1/<u_j,u_j>).

This program enumerates the fixed local rhombus stencils of a size-n hive and
computes the formula over Q.  A negative saturated triple is an exact
counterexample to the claim that every three-ray hive normal cone is locally
BV-positive; realization as a face is a separate gate.
"""

from fractions import Fraction
from functools import reduce
from itertools import combinations
from math import gcd
import argparse
import json
import os
import sys

from sympy import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "engine"))
from hive_poly import build  # noqa: E402


def primitive(v):
    g = reduce(gcd, (abs(x) for x in v if x), 0)
    return tuple(x // g for x in v) if g else tuple(v)


def hive_normals(n):
    A, _b, d, interior, ok = build((0,) * n, (0,) * n, (0,) * n)
    assert ok
    normals = []
    seen = set()
    for a in A:
        p = primitive(a)
        if p not in seen:
            seen.add(p)
            normals.append(p)
    return normals, interior


def saturation_index(rows):
    """Index of row span in its saturation: gcd of maximal minors."""
    cols = sorted({j for r in rows for j, x in enumerate(r) if x})
    g = 0
    for js in combinations(cols, 3):
        det = abs(int(Matrix([[r[j] for j in js] for r in rows]).det()))
        g = gcd(g, det)
        if g == 1:
            return 1
    return g


def bv_alpha_saturated(rows):
    N = Matrix(rows)
    G = N * N.T
    if G.det() == 0:
        return None
    if saturation_index(rows) != 1:
        return None
    M = G.inv()
    a = Fraction(1, 8)
    for i, j in combinations(range(3), 2):
        mij = Fraction(M[i, j])
        a += Fraction(1, 24) * mij * (
            Fraction(1, M[i, i]) + Fraction(1, M[j, j])
        )
    return a


def support_signature(rows):
    supp = [set(j for j, x in enumerate(r) if x) for r in rows]
    return {
        "sizes": sorted(len(s) for s in supp),
        "pair_intersections": sorted(len(supp[i] & supp[j]) for i, j in combinations(range(3), 2)),
        "triple_intersection": len(supp[0] & supp[1] & supp[2]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    normals, interior = hive_normals(args.n)
    hist = {}
    vals = []
    dependent = nonsaturated = 0
    for ids in combinations(range(len(normals)), 3):
        rows = [normals[i] for i in ids]
        N = Matrix(rows)
        if N.rank() < 3:
            dependent += 1
            continue
        idx = saturation_index(rows)
        if idx != 1:
            nonsaturated += 1
            continue
        a = bv_alpha_saturated(rows)
        hist[str(a)] = hist.get(str(a), 0) + 1
        vals.append((a, ids, rows, support_signature(rows)))
    vals.sort(key=lambda z: z[0])
    out = {
        "n": args.n,
        "ambient_dimension": len(interior),
        "normal_count": len(normals),
        "dependent_triples": dependent,
        "nonsaturated_independent_triples": nonsaturated,
        "saturated_independent_triples": len(vals),
        "negative_saturated_triples": sum(a < 0 for a, *_ in vals),
        "zero_saturated_triples": sum(a == 0 for a, *_ in vals),
        "minimum": None if not vals else str(vals[0][0]),
        "minimizers": [
            {"alpha": str(a), "ids": ids, "rows": rows, "signature": sig}
            for a, ids, rows, sig in vals[: args.top]
        ],
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k, v in out.items():
            if k != "minimizers":
                print(f"{k}={v}")
        for row in out["minimizers"]:
            print(row)


if __name__ == "__main__":
    main()
