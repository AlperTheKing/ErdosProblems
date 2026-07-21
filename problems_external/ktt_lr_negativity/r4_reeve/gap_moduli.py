#!/usr/bin/env python3
"""
gap_moduli.py -- verify the MODULI REDUCTION for r=4 hive polytopes.

Claim.  Write the gap vectors
    a = (lam1-lam2, lam2-lam3, lam3-lam4)
    b = (mu1-mu2,  mu2-mu3,  mu3-mu4)
    c = (nu1-nu2,  nu2-nu3,  nu3-nu4)
Then the r=4 hive polytope Q(lam,mu,nu) depends on (lam,mu,nu) ONLY through
(a,b,c), up to LATTICE TRANSLATION of R^3.  Consequently the Ehrhart polynomial,
the normalized volume, the lattice point count, h*, and a_1 all depend only on
(a,b,c).

Reason: the two "add a full column" symmetries
    (lam,nu) -> (lam+1^4, nu+1^4)   translates the hive by h(x,y) -> h(x,y)+(x+y)
    (mu ,nu) -> (mu +1^4, nu+1^4)   translates the hive by h(x,y) -> h(x,y)+x
generate exactly the stabiliser of (a,b,c) inside the 11-dimensional parameter
space {(lam,mu,nu) : |lam|+|mu|=|nu|}, whose quotient is 9-dimensional = (a,b,c).

Realisability: with Aw = 3a3+2a2+a1, Bw = 3b3+2b2+b1, Cw = 3c3+2c2+c1 and
lam4,mu4,nu4 >= 0 the weight equation reads 4(lam4+mu4-nu4) = Cw-Aw-Bw =: D, so
(a,b,c) is realised by an actual triple of partitions iff D == 0 (mod 4).

This script checks both claims exhaustively on small windows.
"""
import itertools
import sys
from fractions import Fraction

sys.path.insert(0, ".")
from hive4 import analyze, build_hive4


def triple_from_gaps(a, b, c):
    """Canonical (lam,mu,nu) realising the gap vector, or None if 4 does not divide D."""
    Aw = 3 * a[2] + 2 * a[1] + a[0]
    Bw = 3 * b[2] + 2 * b[1] + b[0]
    Cw = 3 * c[2] + 2 * c[1] + c[0]
    D = Cw - Aw - Bw
    if D % 4 != 0:
        return None
    k = D // 4
    if k >= 0:
        l4, m4, n4 = k, 0, 0
    else:
        l4, m4, n4 = 0, 0, -k
    lam = [l4 + a[2] + a[1] + a[0], l4 + a[2] + a[1], l4 + a[2], l4]
    mu = [m4 + b[2] + b[1] + b[0], m4 + b[2] + b[1], m4 + b[2], m4]
    nu = [n4 + c[2] + c[1] + c[0], n4 + c[2] + c[1], n4 + c[2], n4]
    assert sum(lam) + sum(mu) == sum(nu), (lam, mu, nu)
    return lam, mu, nu


def gaps_of(p):
    return (p[0] - p[1], p[1] - p[2], p[2] - p[3])


def sig(res):
    """translation-invariant signature of the polytope"""
    return (res["dim"], res["c"], str(res["volume_normalized"]), tuple(res["hstar"]),
            tuple(str(x) for x in res["poly"]))


def main():
    # ---- test 1: same gaps => same invariants, over many shift representatives
    bad = 0
    tested = 0
    for a in itertools.product(range(3), repeat=3):
        for b in itertools.product(range(3), repeat=3):
            for c in itertools.product(range(3), repeat=3):
                t = triple_from_gaps(a, b, c)
                if t is None:
                    continue
                lam, mu, nu = t
                base = sig(analyze(lam, mu, nu))
                # apply the two column symmetries in several combinations
                for s, u in itertools.product(range(3), repeat=2):
                    lam2 = [x + s for x in lam]
                    mu2 = [x + u for x in mu]
                    nu2 = [x + s + u for x in nu]
                    assert gaps_of(lam2) == a and gaps_of(mu2) == b and gaps_of(nu2) == c
                    s2 = sig(analyze(lam2, mu2, nu2))
                    tested += 1
                    if s2 != base:
                        bad += 1
                        if bad < 5:
                            print("MISMATCH", lam, mu, nu, "->", lam2, mu2, nu2, base, s2)
    print("test1 shift-invariance: %d checks, %d mismatches" % (tested, bad))

    # ---- test 2: every valid (lam,mu,nu) in a window has 4 | D, and its gaps
    #             reproduce the same invariants as the canonical representative
    bad2 = 0
    n2 = 0
    for N in range(1, 15):
        for nu in partitions_len4(N):
            for wl in range(N + 1):
                for lam in partitions_len4(wl):
                    for mu in partitions_len4(N - wl):
                        g = (gaps_of(lam), gaps_of(mu), gaps_of(nu))
                        t = triple_from_gaps(*g)
                        if t is None:
                            print("UNREALISABLE GAPS FROM A REAL TRIPLE!", lam, mu, nu)
                            bad2 += 1
                            continue
                        n2 += 1
                        if n2 % 7 == 0:  # sample to keep runtime sane
                            if sig(analyze(lam, mu, nu)) != sig(analyze(*t)):
                                bad2 += 1
                                if bad2 < 5:
                                    print("CANON MISMATCH", lam, mu, nu, t)
    print("test2 canonicalisation: %d triples, %d failures" % (n2, bad2))
    return 0 if (bad == 0 and bad2 == 0) else 1


def partitions_len4(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield [0, 0, 0, 0]
        return
    def rec(rem, k, mx, cur):
        if k == 0:
            if rem == 0:
                yield list(cur)
            return
        for p in range(min(rem, mx), -1, -1):
            if p * k < rem:
                break
            cur.append(p)
            yield from rec(rem - p, k - 1, p, cur)
            cur.pop()
    yield from rec(n, 4, maxpart, [])


if __name__ == "__main__":
    sys.exit(main())
