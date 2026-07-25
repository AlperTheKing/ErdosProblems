#!/usr/bin/env python3
"""fam10_gen.py -- triple generation for the FRACTIONAL-VERTEX sweep (family 10).

MEASUREMENT ONLY: no LP dimension oracle, no simplex filter is used to DISCARD
any triple from the tier-0 screen.  The only discard here is c = 0 (empty, from
one exact engine-A call) and c = 1 (Fulton/KTW: c=1 => P == 1 => d = 0, so
h*_1 = h*_d = 0 identically, margin 0, never a hit).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parts_exact(N, k, maxpart=None):
    if maxpart is None:
        maxpart = N
    out = []

    def rec(rem, k, mx, cur):
        if k == 0:
            if rem == 0:
                out.append(tuple(cur))
            return
        if rem < k:
            return
        for p in range(min(mx, rem - (k - 1)), 0, -1):
            cur.append(p)
            rec(rem - p, k - 1, p, cur)
            cur.pop()
    rec(N, k, maxpart, [])
    return out


def parts_upto(N, kmax):
    out = []
    for k in range(1, kmax + 1):
        out.extend(parts_exact(N, k))
    return out


def contained(p, nu):
    for i, x in enumerate(p):
        if i >= len(nu) or x > nu[i]:
            return False
    return True


def gen(r, N, distinct_nu=False):
    """all (lam,mu,nu): nu exactly r parts, |nu|=N, |lam|+|mu|=N, lam,mu <= nu."""
    nus = parts_exact(N, r)
    if distinct_nu:
        nus = [v for v in nus if all(v[i] > v[i + 1] for i in range(len(v) - 1))]
    cache = {}
    trips = []
    for nu in nus:
        for a in range(0, N + 1):
            pa = cache.setdefault(a, parts_upto(a, r) if a else [()])
            pb = cache.setdefault(N - a, parts_upto(N - a, r) if N - a else [()])
            for lam in pa:
                if not contained(lam, nu):
                    continue
                for mu in pb:
                    if not contained(mu, nu):
                        continue
                    if lam > mu:            # c is symmetric in lam <-> mu
                        continue
                    trips.append((lam, mu, nu))
    return trips


if __name__ == "__main__":
    r = int(sys.argv[1])
    for N in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
        print(r, N, len(gen(r, N)), flush=True)
