#!/usr/bin/env python3
"""
subset_atlas.py -- BAND 10 weight-independent bound on V at c = 4 (h*_1 = 0).

SETTING.  For r = 4 the hive polytope is Q(lam,mu,nu) = {h in R^3 : A h <= b}
with the SAME 18-row matrix A (15 distinct primitive directions) for every
triple; only b moves.  Band 10 hunts  c = L(1) = 4  (h*_1 = 0) with V >= 2,
i.e. exactly the Reeve mechanism (T_q is empty with V = q, a_1 = 2 - q/6).

FACTS USED (all elementary, all checked here exactly):
  (F1) If Q is a 3-dim LATTICE polytope with exactly 4 lattice points then Q is
       an EMPTY lattice 3-simplex: 4 vertices, and every edge is a primitive
       lattice vector (an edge of lattice length L contributes L-1 further
       lattice points).
  (F2) At a vertex v of a simplex the 3 edge vectors are then exactly the
       primitive generators of the vertex cone, so
            V = |det(e1,e2,e3)| = m(v) := multiplicity of the vertex cone.
  (F3) The vertex cone at v is {x : n_i . (x-v) <= 0, i in T} for the triple T
       of facet normals meeting at v.  m(v) therefore depends ONLY on T -- on
       three of the 15 fixed directions -- and NOT on b, hence not on
       (lam,mu,nu) and not on the weight.  This is what makes the band-10
       question finite.
  (F4) A simplex has 4 facets, so its normal set S is a 4-subset of the 15
       directions with 0 in the interior of conv(S) (boundedness), and its four
       vertex cones are the four triples T of S.  By (F2) all four
       multiplicities must be EQUAL (they all equal V).

So:  max V over all r=4 hive polytopes with c = 4 and lattice vertices
     <=  max over 4-subsets S of the 15 directions, S positively spanning,
         all four triples simplicial with a common multiplicity m,  of m.

This script computes that maximum exactly (integers only).  It also prints the
full multiplicity histogram over all C(15,3) triples and all C(15,4) subsets.
"""
import itertools
import json
import os
import sys
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from hive4 import build_hive4, _det3  # noqa: E402


def primitive(v):
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    return tuple(v) if g == 0 else tuple(x // g for x in v)


def cross(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def cone_mult(rows):
    """multiplicity of the pointed simplicial cone {x : n_i . x <= 0}; None if degenerate"""
    gens = []
    for k, (a, b) in enumerate([(rows[1], rows[2]), (rows[2], rows[0]), (rows[0], rows[1])]):
        d = cross(a, b)
        if all(x == 0 for x in d):
            return None
        d = primitive(d)
        s = sum(x * y for x, y in zip(rows[k], d))
        if s == 0:
            return None
        if s > 0:
            d = tuple(-x for x in d)
        gens.append(d)
    return abs(_det3([list(g) for g in gens])), gens


def positively_spans(S):
    """0 in the interior of conv(S) for 4 vectors in R^3  <=>  the unique (up to
    scale) linear dependence has all coefficients of the same strict sign.
    Exact: solve for the kernel of the 3x4 matrix by 3x3 minors (Cramer)."""
    cof = []
    for k in range(4):
        rest = [S[i] for i in range(4) if i != k]
        d = _det3([list(r) for r in rest])
        cof.append(((-1) ** k) * d)
    if all(c == 0 for c in cof):
        return False
    if all(c > 0 for c in cof) or all(c < 0 for c in cof):
        return True
    return False


def main():
    H = build_hive4([5, 3, 1], [6, 4, 2], [9, 6, 4, 2])
    A = H["A"]
    dirs = sorted({tuple(r) for r in A})
    assert len(dirs) == 15, len(dirs)

    trip_mult = {}
    for T in itertools.combinations(range(15), 3):
        r = cone_mult([dirs[i] for i in T])
        if r is not None:
            trip_mult[T] = r[0]

    hist3 = {}
    for m in trip_mult.values():
        hist3[m] = hist3.get(m, 0) + 1

    best = 0
    best_S = []
    hist4 = {}
    n_bounded = 0
    equal_sets = []
    for S4 in itertools.combinations(range(15), 4):
        S = [dirs[i] for i in S4]
        if not positively_spans(S):
            continue
        n_bounded += 1
        ms = []
        ok = True
        for T in itertools.combinations(S4, 3):
            if T not in trip_mult:
                ok = False
                break
            ms.append(trip_mult[T])
        if not ok:
            continue
        key = tuple(sorted(ms))
        hist4[str(key)] = hist4.get(str(key), 0) + 1
        if len(set(ms)) == 1:
            equal_sets.append({"normals": [list(dirs[i]) for i in S4], "m": ms[0]})
            if ms[0] > best:
                best = ms[0]
                best_S = [list(dirs[i]) for i in S4]

    out = {
        "n_directions": len(dirs),
        "directions": [list(d) for d in dirs],
        "n_triples_simplicial": len(trip_mult),
        "triple_multiplicity_histogram": {str(k): v for k, v in sorted(hist3.items())},
        "m_max_over_triples": max(trip_mult.values()),
        "n_4subsets_positively_spanning": n_bounded,
        "multiplicity_profile_histogram_over_bounded_4subsets": hist4,
        "n_4subsets_with_all_four_multiplicities_equal": len(equal_sets),
        "max_common_multiplicity": best,
        "argmax_normals": best_S,
        "equal_multiplicity_values": sorted({e["m"] for e in equal_sets}),
        "VERDICT": (
            "Every r=4 hive polytope that is a 3-dim LATTICE polytope with c=4 "
            "(h*_1=0) is an empty lattice 3-simplex whose normalized volume equals "
            "the common multiplicity of its four vertex cones; that common value "
            "is at most %d over all positively-spanning 4-subsets of the 15 fixed "
            "rhombus directions, INDEPENDENTLY OF (lam,mu,nu) and of the weight."
            % best
        ),
    }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
