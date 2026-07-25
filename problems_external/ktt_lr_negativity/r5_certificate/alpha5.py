#!/usr/bin/env python3
"""Berline--Vergne local weight alpha of a codimension-two (2-dimensional)
normal cone, for the 342 nonparallel r=5 hive normal pairs.

DERIVATION (self-contained, re-derived here, not copied):

Let F be a codimension-two face of a full-dimensional P in R^d, contained in
the facets with primitive outward normals u,v.  The transverse cone is the
tangent cone of P along F modulo lin(F-F), living in W/W_F where W = R^d.
Its lattice is Z^d / (Z^d cap W_F); the dual of that lattice is exactly the
SATURATED lattice L = sat(Zu + Zv) inside the normal plane.  Working in
coordinates dual to a basis (p,q) of L therefore makes the transverse lattice
equal to Z^2 with Gram matrix G^{-1}, G = ((p,p),(p,q);(p,q),(q,q)).

Unimodular 2-dimensional cones use the Berline--Vergne constant

    alpha(cone(x,y)) = 1/4 + (1/12)( <x,y>/<x,x> + <x,y>/<y,y> ),     (*)

and alpha is a valuation, so a subdivision C = C1 u C2 along a ray rho gives
alpha(C) = alpha(C1) + alpha(C2) - 1/2.

Case q = [sat(Zu+Zv) : Zu+Zv] = 1.  Then (u,v) is a basis of L and the
transverse cone is cone(-u*, -v*) with Gram G^{-1}; (*) gives

    alpha = 1/4 - (C/12)(1/A + 1/B),   A=<u,u>, B=<v,v>, C=<u,v>.

Case q = 2.  Then s=(u+v)/2, t=(u-v)/2 are integral, have disjoint supports
(hence are orthogonal), and form a basis of L.  In coordinates dual to (s,t)
the transverse cone is cone((-1,1),(-1,-1)); subdividing along (-1,0) and
applying (*) twice with Gram diag(1/A',1/B'), A'=<s,s>, B'=<t,t>, gives

    alpha = (A' + 2B') / (6 (A' + B')).

Unit tests at the bottom check (*) against the unit square and the unimodular
triangle, where the sum of vertex weights must be the Ehrhart constant term 1.
"""
import os
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import NORMALS5, D  # noqa: E402
from polytope5 import PAIR_TYPES  # noqa: E402


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sat_index(u, v):
    """[sat(Zu+Zv) : Zu+Zv] = gcd of the 2x2 minors."""
    g = 0
    for i in range(len(u)):
        for j in range(i + 1, len(u)):
            g = gcd(g, abs(u[i] * v[j] - u[j] * v[i]))
    return g


def alpha_unimodular(x, y, gram=None):
    """(*) for a unimodular 2-cone with rays x,y in a metric given by gram."""
    if gram is None:
        xy, xx, yy = dot(x, y), dot(x, x), dot(y, y)
    else:
        def ip(a, b):
            return sum(a[i] * gram[i][j] * b[j] for i in range(2) for j in range(2))
        xy, xx, yy = ip(x, y), ip(x, x), ip(y, y)
    return Fraction(1, 4) + Fraction(1, 12) * (Fraction(xy) / xx + Fraction(xy) / yy)


def alpha_pair(u, v):
    """BV local weight of the 2-dimensional normal cone spanned by u and v."""
    q = sat_index(u, v)
    if q == 0:
        raise ValueError('parallel normals')
    if q == 1:
        A, B, C = dot(u, u), dot(v, v), dot(u, v)
        return Fraction(1, 4) - Fraction(C, 12) * (Fraction(1, A) + Fraction(1, B))
    if q == 2:
        s = tuple((a + b) for a, b in zip(u, v))
        t = tuple((a - b) for a, b in zip(u, v))
        if any(x % 2 for x in s) or any(x % 2 for x in t):
            raise ValueError('index 2 but (u+v)/2 not integral')
        s = tuple(x // 2 for x in s)
        t = tuple(x // 2 for x in t)
        if dot(s, t) != 0:
            raise ValueError('index-2 half sums are not orthogonal')
        Ap, Bp = dot(s, s), dot(t, t)
        val = Fraction(Ap + 2 * Bp, 6 * (Ap + Bp))
        # independent recomputation through the subdivision, same arithmetic path
        gram = [[Fraction(1, Ap), Fraction(0)], [Fraction(0), Fraction(1, Bp)]]
        a1 = alpha_unimodular((-1, 1), (-1, 0), gram)
        a2 = alpha_unimodular((-1, 0), (-1, -1), gram)
        chk = a1 + a2 - Fraction(1, 2)
        if chk != val:
            raise AssertionError('index-2 subdivision mismatch %s %s' % (val, chk))
        return val
    raise ValueError('unexpected saturation index %d' % q)


def alpha_vector():
    """alpha for each of the 342 ridge types, in PAIR_TYPES order."""
    return [alpha_pair(NORMALS5[i], NORMALS5[j]) for i, j in PAIR_TYPES]


def _selftest():
    # unit square: 4 vertex cones, alpha must sum to the constant term 1
    tot = (alpha_unimodular((1, 0), (0, 1)) + alpha_unimodular((-1, 0), (0, 1))
           + alpha_unimodular((1, 0), (0, -1)) + alpha_unimodular((-1, 0), (0, -1)))
    assert tot == 1, tot
    # unimodular triangle conv{(0,0),(1,0),(0,1)}
    tot = (alpha_unimodular((1, 0), (0, 1))
           + alpha_unimodular((-1, 0), (-1, 1))
           + alpha_unimodular((0, -1), (1, -1)))
    assert tot == 1, tot
    # 2x1 rectangle: same cones as the square, still 1
    print('alpha selftest: PASS (unit square 1, unimodular triangle 1)')


if __name__ == '__main__':
    from collections import Counter
    _selftest()
    av = alpha_vector()
    idxh = Counter(sat_index(NORMALS5[i], NORMALS5[j]) for i, j in PAIR_TYPES)
    vh = Counter(av)
    print('ridge types            = %d' % len(av))
    print('saturation index hist  = %s' % dict(sorted(idxh.items())))
    print('alpha min              = %s' % min(av))
    print('alpha max              = %s' % max(av))
    print('alpha value histogram  = %s'
          % {str(k): v for k, v in sorted(vh.items())})
    print('all alpha > 0          = %s' % all(a > 0 for a in av))
