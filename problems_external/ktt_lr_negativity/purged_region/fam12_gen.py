#!/usr/bin/env python3
"""
fam12_gen.py -- generator for LADDER HUNTER 12's family:
STRUCTURED repeated-part / hook-shaped lam and mu against LONG nu.

lam and mu each range over the exhaustive 3-parameter "fat hook" box

    L(a,p,q) = (a^p, 1^q)     a >= 2, p >= 1, q >= 0      (rectangles: q=0;
                                                           hooks: p=1)
    plus the pure columns 1^q.

This single family contains every rectangle, every hook, and every
rectangle-plus-column shape, i.e. exactly the "repeated-part and hook-shaped"
partitions the assignment names, and it is EXHAUSTIVE inside the stated
parameter box.

nu ranges over ALL partitions of |lam|+|mu| with EXACTLY r parts
(r = len(nu), the "long nu" requirement), r in the requested set.

Nothing here filters on simplex-hood or on any LP dimension oracle.
"""
import itertools


def fathooks(maxsize, maxlen):
    """all (a^p, 1^q) with |.| <= maxsize, p+q <= maxlen, a >= 2, plus 1^q."""
    out = set()
    for q in range(1, maxlen + 1):
        if q <= maxsize:
            out.add(tuple([1] * q))
    for a in range(2, maxsize + 1):
        for p in range(1, maxlen + 1):
            for q in range(0, maxlen - p + 1):
                s = a * p + q
                if s > maxsize:
                    break
                out.add(tuple([a] * p + [1] * q))
    return sorted(out, key=lambda t: (sum(t), len(t), t))


def parts_exact(N, r, maxpart=None):
    """all partitions of N into EXACTLY r positive parts (weakly decreasing)."""
    if maxpart is None:
        maxpart = N
    out = []

    def rec(rem, k, mx, cur):
        if k == 0:
            if rem == 0:
                out.append(tuple(cur))
            return
        # each of the k remaining parts >= 1, <= mx
        lo = max(1, -(-rem // k) if False else 1)
        hi = min(mx, rem - (k - 1))
        for v in range(hi, lo - 1, -1):
            if v * k < rem:
                break
            cur.append(v)
            rec(rem - v, k - 1, v, cur)
            cur.pop()

    rec(N, r, maxpart, [])
    return out


def contains(nu, lam):
    """nu >= lam componentwise (necessary for c(nu;lam,mu) > 0)."""
    if len(lam) > len(nu):
        return False
    return all(nu[i] >= lam[i] for i in range(len(lam)))


def all_parts(maxsize, maxlen):
    """every partition with |.| <= maxsize and at most maxlen parts."""
    out = set()
    for N in range(1, maxsize + 1):
        for r in range(1, maxlen + 1):
            out.update(parts_exact(N, r))
    return sorted(out, key=lambda t: (sum(t), len(t), t))


def gen(rset, maxsize, maxlen, maxpart=None, mu_all=False, mu_maxsize=None):
    """returns a sorted list of (lam, mu, nu).

    mu_all=False : BOTH lam and mu range over the fat-hook box (regime A).
    mu_all=True  : lam over the fat-hook box, mu over ALL partitions with at
                   most maxlen parts and |mu| <= mu_maxsize (regime B).  This
                   regime contains the known refuter lam=(2,2,1) (=(2^2,1)),
                   mu=(4,3,2,1), nu=(5,4,3,2,1).
    """
    shapes = fathooks(maxsize, maxlen)
    if mu_all:
        mus = all_parts(mu_maxsize if mu_maxsize else maxsize, maxlen)
    trips = set()
    cache = {}
    for i, lam in enumerate(shapes):
        for mu in (mus if mu_all else shapes[i:]):   # lam<=mu kills the swap
            N = sum(lam) + sum(mu)
            for r in rset:
                if r < max(len(lam), len(mu)):
                    continue
                if len(lam) + len(mu) < r:
                    continue                      # c = 0 forced (rows)
                key = (N, r)
                if key not in cache:
                    cache[key] = parts_exact(N, r, maxpart)
                for nu in cache[key]:
                    if contains(nu, lam) and contains(nu, mu):
                        trips.add((lam, mu, nu))
    return sorted(trips)


if __name__ == "__main__":
    import sys
    rset = [int(x) for x in sys.argv[1].split(",")]
    maxsize = int(sys.argv[2])
    maxlen = int(sys.argv[3])
    mp = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "-" else None
    t = gen(rset, maxsize, maxlen, mp)
    print("shapes:", len(fathooks(maxsize, maxlen)))
    print("triples:", len(t))
