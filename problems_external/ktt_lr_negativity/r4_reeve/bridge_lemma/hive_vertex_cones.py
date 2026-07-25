#!/usr/bin/env python3
"""Exact tangent-cone extreme rays and multiplicities at every vertex of an
r=4 hive polytope.  A vertex is SIMPLE iff its tangent cone has exactly 3
extreme rays; multiplicity = |det| of the primitive extreme-ray generators.
Redundant tight inequalities are handled correctly (they are not facets of
the tangent cone)."""
import sys
from fractions import Fraction as F
from math import gcd
from itertools import combinations
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems_external\ktt_lr_negativity\r4_reeve")
import hive4


def det3(u, v, w):
    return (u[0]*(v[1]*w[2]-v[2]*w[1]) - u[1]*(v[0]*w[2]-v[2]*w[0])
            + u[2]*(v[0]*w[1]-v[1]*w[0]))


def prim_int(v):
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    if g == 0:
        return None
    return tuple(x//g for x in v)


def prim_frac(v):
    dens = 1
    for x in v:
        x = F(x)
        dens = dens*x.denominator//gcd(dens, x.denominator)
    return prim_int([int(F(x)*dens) for x in v])


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def extreme_rays(normals):
    """Extreme rays of C = {x : n.x <= 0 for n in normals}, assumed pointed."""
    rays = set()
    for a, b in combinations(range(len(normals)), 2):
        c = cross(normals[a], normals[b])
        if c == (0, 0, 0):
            continue
        for s in (1, -1):
            r = prim_int([s*t for t in c])
            if all(sum(n[k]*r[k] for k in range(3)) <= 0 for n in normals):
                # check it is really extreme: the tight set has rank 2
                T = [n for n in normals if sum(n[k]*r[k] for k in range(3)) == 0]
                if rank(T) == 2:
                    rays.add(r)
    return sorted(rays)


def rank(rows):
    M = [[F(x) for x in r] for r in rows]
    rk = 0
    ncol = 3
    for c in range(ncol):
        p = None
        for r in range(rk, len(M)):
            if M[r][c] != 0:
                p = r
                break
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        pv = M[rk][c]
        M[rk] = [x/pv for x in M[rk]]
        for r in range(len(M)):
            if r != rk and M[r][c] != 0:
                f = M[r][c]
                M[r] = [M[r][k]-f*M[rk][k] for k in range(ncol)]
        rk += 1
    return rk


def report(lam, mu, nu, verbose=True):
    H = hive4.build_hive4(lam, mu, nu)
    if not H["ok"]:
        return None
    A, b = H["A"], H["b"]
    verts = hive4.vertices(A, b)
    if not verts:
        return None
    out = []
    for v in verts:
        tight = [prim_int(A[i]) for i in range(len(A)) if hive4._dot(A[i], v) == b[i]]
        tight = sorted(set(tight))
        if rank(tight) < 3:
            out.append((v, tight, None, None, "not-pointed/lowdim"))
            continue
        rays = extreme_rays(tight)
        m = abs(det3(*rays)) if len(rays) == 3 else None
        out.append((v, tight, rays, m, "simple" if len(rays) == 3 else f"nonsimple({len(rays)} rays)"))
    if verbose:
        print(f"lam={lam} mu={mu} nu={nu}  dim-check verts={len(verts)}")
        for v, t, rays, m, tag in out:
            print("  v=", tuple(str(x) for x in v),
                  "integral", all(F(x).denominator == 1 for x in v),
                  "|tightnormals|", len(t), tag,
                  ("rays=%s mult=%s" % (rays, m)) if rays else "")
    return out


if __name__ == "__main__":
    report([12, 8, 4, 0], [12, 8, 4, 0], [18, 14, 10, 6])
