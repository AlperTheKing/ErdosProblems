#!/usr/bin/env python3
"""
cone_atlas.py -- exact structural analysis of the FIXED r=4 hive constraint matrix.

The r=4 hive polytope is Q(lam,mu,nu) = { h in R^3 : A h <= b(lam,mu,nu) } where A
is the SAME 18 x 3 integer matrix for every triple (only b moves).  Everything about
which lattice 3-polytopes can occur as Q is therefore controlled by A alone.

This script computes, exactly (integers only):

  1. the 15 distinct row directions of A;
  2. every 3-subset of distinct rows: determinant, and -- when the subset cuts out a
     POINTED simplicial cone -- the primitive generators of that cone and its
     lattice multiplicity (index) m = |det(primitive generators)|;
  3. the maximum multiplicity m_max over all such triples;
  4. the same for the DUAL side: multiplicity of every pointed cone
     {x : n_i . x <= 0, i in S} for |S| = 3.

CONSEQUENCE (see verdict in the run log): a lattice 3-simplex Q with edge lattice
lengths l1,l2,l3 at a vertex v has normalized volume V = m(v) * l1*l2*l3 where m(v)
is the multiplicity of the vertex cone.  If Q is an EMPTY simplex (exactly 4 lattice
points) then every edge has lattice length 1, so V = m(v) <= m_max.  A Reeve simplex
T(p,q) is empty with V = q, so q <= m_max.
"""
import itertools
from fractions import Fraction
from math import gcd
import sys

sys.path.insert(0, ".")
from hive4 import build_hive4, _det3


def primitive(v):
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    if g == 0:
        return tuple(v)
    return tuple(x // g for x in v)


def cross(u, v):
    return (u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0])


def cone_generators(rows):
    """
    For 3 linearly independent rows n1,n2,n3, the cone C = {x : n_i.x <= 0} is
    simplicial and pointed.  Its extreme rays are the directions g_k with
    n_i . g_k = 0 for i != k and n_k . g_k < 0.  Return the primitive generators.
    """
    n1, n2, n3 = rows
    gens = []
    for k, (a, bb) in enumerate([(n2, n3), (n3, n1), (n1, n2)]):
        d = cross(a, bb)
        if all(x == 0 for x in d):
            return None
        d = primitive(d)
        nk = rows[k]
        s = sum(x * y for x, y in zip(nk, d))
        if s == 0:
            return None
        if s > 0:
            d = tuple(-x for x in d)
        gens.append(d)
    return gens


def main():
    H = build_hive4([5, 3, 1], [6, 4, 2], [9, 6, 4, 2])
    A = H["A"]
    rows = sorted({tuple(r) for r in A})
    print("distinct row directions (%d):" % len(rows))
    for r in rows:
        print("   ", r)
    # every row primitive?
    print("all rows primitive:", all(primitive(r) == r for r in rows))

    dets = {}
    mults = {}
    worst = []
    for S in itertools.combinations(rows, 3):
        D = _det3([list(x) for x in S])
        dets[abs(D)] = dets.get(abs(D), 0) + 1
        if D == 0:
            continue
        g = cone_generators(list(S))
        if g is None:
            continue
        m = abs(_det3([list(x) for x in g]))
        mults[m] = mults.get(m, 0) + 1
        worst.append((m, S, tuple(g), abs(D)))
    print()
    print("|det| histogram over all C(15,3)=%d triples of distinct rows:" % len(list(itertools.combinations(rows, 3))))
    for k in sorted(dets):
        print("   |det| = %d : %d triples" % (k, dets[k]))
    print()
    print("cone multiplicity histogram over pointed simplicial triples:")
    for k in sorted(mults):
        print("   m = %d : %d cones" % (k, mults[k]))
    m_max = max(mults)
    print()
    print("m_max = %d" % m_max)
    print("examples attaining m_max:")
    for m, S, g, D in worst:
        if m == m_max:
            print("   rows=%s  |det|=%d  gens=%s" % (list(S), D, list(g)))

    # dual check: multiplicities of cones spanned by triples of rows (normal fan side)
    nmults = {}
    for S in itertools.combinations(rows, 3):
        D = _det3([list(x) for x in S])
        if D == 0:
            continue
        nmults[abs(D)] = nmults.get(abs(D), 0) + 1
    print()
    print("normal-side |det| histogram (nonsingular triples):", dict(sorted(nmults.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
