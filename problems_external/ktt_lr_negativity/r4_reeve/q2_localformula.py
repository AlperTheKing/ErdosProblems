#!/usr/bin/env python3
"""
q2_localformula.py -- is a_1 < 0 possible AT ALL at r=4?  (decisive route)

By Berline-Vergne / McMullen local Ehrhart theory, for a lattice 3-polytope P

        a_1(P) = SUM over edges e  of   ell(e) * mu(transverse cone of e),

where ell(e) is the lattice length of e and mu depends ONLY on the 2-dim
transverse cone of e, i.e. only on the pair {n_1,n_2} of outward facet normals
meeting along e (the primitive edge direction is +-n_1 x n_2).

For r = 4 the rhombus matrix is FIXED: every hive polytope has all its facet
normals inside a 15-element set N.  Hence there are at most C(15,2) = 105
possible edge types, and a_1 is the SAME fixed nonnegative-combination-or-not
linear functional of the vector

        Lambda(P)_{n1,n2} = total lattice length of edges of type {n1,n2}.

If every coefficient mu is >= 0, then a_1 >= 0 for EVERY r=4 hive polytope and
KTT negativity is IMPOSSIBLE in the r=4 cell.  If some mu < 0, that edge type is
the explicit recipe for a counterexample.

This script determines the mu's by exact linear algebra from many sampled
polytopes (over-determined, so the fit is itself a consistency test).
All arithmetic exact.
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402
from q2_relaxed_simplex import NORMALS  # noqa: E402

PAIRS = list(itertools.combinations(range(len(NORMALS)), 2))
PIDX = {p: i for i, p in enumerate(PAIRS)}


def reduce_rep(A, b):
    """collapse duplicate normals to the tightest offset."""
    t = {}
    for row, rhs in zip(A, b):
        k = tuple(row)
        t[k] = rhs if k not in t else min(t[k], rhs)
    return t


def edge_data(A, b, verts):
    """
    Return  {pair_index: total lattice length}  and False if any edge endpoint
    is non-integral (then P is not a lattice polytope and the fit is skipped).
    """
    t = reduce_rep(A, b)
    lam = {}
    # keep ONLY genuine facets (face of dimension 2); a redundant constraint
    # that happens to be tight along an edge would otherwise mis-type it.
    keys = [k for k in t
            if hive4._affine_rank([v for v in verts if hive4._dot(k, v) == t[k]]) == 2]
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            n1, n2 = keys[i], keys[j]
            on = [v for v in verts
                  if hive4._dot(n1, v) == t[n1] and hive4._dot(n2, v) == t[n2]]
            if len(on) < 2:
                continue
            # the face must be 1-dimensional: all such vertices collinear, take extremes
            if hive4._affine_rank(on) != 1:
                continue
            # endpoints = the two extreme points
            p0 = on[0]
            far = max(on, key=lambda v: sum((a - c) ** 2 for a, c in zip(v, p0)))
            p1 = far
            p2 = max(on, key=lambda v: sum((a - c) ** 2 for a, c in zip(v, p1)))
            d = [p2[k] - p1[k] for k in range(3)]
            if any(x.denominator != 1 for x in p1) or any(x.denominator != 1 for x in p2):
                return None
            g = 0
            for x in d:
                g = gcd(g, abs(int(x)))
            if g == 0:
                continue
            try:
                i1 = NORMALS.index(list(n1))
                i2 = NORMALS.index(list(n2))
            except ValueError:
                return None
            key = PIDX[(min(i1, i2), max(i1, i2))]
            lam[key] = lam.get(key, 0) + g
    return lam


def analyse(A, b):
    verts = hive4.vertices(A, b)
    if not verts or hive4._affine_rank(verts) != 3:
        return None
    if max(hive4.denominators(verts)) != 1:
        return None
    box = hive4.bounding_box(verts)
    L = [1] + [hive4.lattice_count(A, b, n, box) for n in range(1, 4)]
    P = hive4.interpolate(L)
    a1 = P[1]
    lam = edge_data(A, b, verts)
    if lam is None:
        return None
    return lam, a1


def rand_hive(rng, maxpart):
    def rp(k, m):
        p = sorted((rng.randint(0, m) for _ in range(k)), reverse=True)
        return tuple(x for x in p if x > 0)
    lam = rp(4, maxpart); mu = rp(4, maxpart)
    N = sum(lam) + sum(mu)
    if N == 0:
        return None
    nu = list(rp(4, maxpart * 2)) + [0, 0, 0, 0]
    nu = nu[:4]
    d = N - sum(nu)
    if d > 0:
        nu[0] += d
    else:
        k = 3
        while d < 0 and k >= 0:
            take = min(-d, nu[k] - (nu[k + 1] if k < 3 else 0))
            nu[k] -= take; d += take; k -= 1
        if d != 0:
            return None
    if list(nu) != sorted(nu, reverse=True) or nu[3] < 0:
        return None
    H = hive4.build_hive4(lam, mu, tuple(x for x in nu if x > 0))
    if not H["ok"]:
        return None
    return H["A"], H["b"], (lam, mu, tuple(nu))


def rand_relaxed(rng, T):
    """random b over ALL 15 normals -- the relaxation (superset of hive cell)."""
    A = [list(n) for n in NORMALS]
    b = [rng.randint(-T, T) for _ in NORMALS]
    return A, b, None


def solve_exact(rows, rhs, ncol):
    """exact Gaussian elimination; returns (solution or None, pivot cols, consistent)."""
    M = [[Fraction(x) for x in r] + [Fraction(rhs[i])] for i, r in enumerate(rows)]
    piv = []
    r = 0
    for c in range(ncol):
        p = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * bb for a, bb in zip(M[i], M[r])]
        piv.append(c)
        r += 1
        if r == len(M):
            break
    for i in range(r, len(M)):
        if all(x == 0 for x in M[i][:ncol]) and M[i][ncol] != 0:
            return None, piv, False
    sol = [Fraction(0)] * ncol
    for k, c in enumerate(piv):
        sol[c] = M[k][ncol]
    return sol, piv, True


def main(nhive=6000, nrelax=6000, maxpart=14, T=6, seed=777):
    rng = random.Random(seed)
    rows, rhs, tags = [], [], []
    for _ in range(nhive):
        h = rand_hive(rng, maxpart)
        if h is None:
            continue
        res = analyse(h[0], h[1])
        if res is None:
            continue
        lam, a1 = res
        rows.append([lam.get(i, 0) for i in range(len(PAIRS))])
        rhs.append(a1)
        tags.append(("hive", h[2]))
    nh = len(rows)
    for _ in range(nrelax):
        A, b, _ = rand_relaxed(rng, T)
        res = analyse(A, b)
        if res is None:
            continue
        lam, a1 = res
        rows.append([lam.get(i, 0) for i in range(len(PAIRS))])
        rhs.append(a1)
        tags.append(("relax", None))
    print(f"samples usable: {len(rows)}  (hive {nh}, relaxed {len(rows)-nh})")
    used = sorted({c for r in rows for c in range(len(PAIRS)) if r[c] != 0})
    print(f"edge types actually occurring: {len(used)} of {len(PAIRS)}")
    sub = [[r[c] for c in used] for r in rows]
    sol, piv, ok = solve_exact(sub, rhs, len(used))
    print("linear system consistent (a_1 IS a fixed linear form in the edge-length vector):", ok)
    if not ok:
        print("  -> local-formula fit FAILED; do not use this route")
        return 1
    print(f"rank {len(piv)} of {len(used)} unknowns")
    freecols = [c for c in range(len(used)) if c not in piv]
    mus = {}
    for k, c in enumerate(used):
        mus[PAIRS[c]] = sol[k]
    neg = {p: v for p, v in mus.items() if v < 0}
    print("fitted mu values (edge-type coefficients):")
    for p in sorted(mus, key=lambda q: mus[q]):
        print(f"   {NORMALS[p[0]]} & {NORMALS[p[1]]}  ->  mu = {mus[p]}")
    print("NEGATIVE mu (would be the counterexample recipe):", len(neg))
    print("free (undetermined) columns:", [PAIRS[used[c]] for c in freecols])
    json.dump({"n_samples": len(rows), "n_hive": nh, "consistent": ok,
               "rank": len(piv), "n_types": len(used),
               "mu": {str((NORMALS[p[0]], NORMALS[p[1]])): str(v) for p, v in mus.items()},
               "negative_mu": {str(p): str(v) for p, v in neg.items()},
               "free_cols": [str(PAIRS[used[c]]) for c in freecols]},
              open(os.path.join(HERE, "q2_localformula.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
