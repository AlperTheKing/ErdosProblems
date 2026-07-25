#!/usr/bin/env python3
"""Exact lattice-point counting for {A x <= b} in R^D by DFS with staged bounds.

Bounds for coordinate k come only from rows whose support lies inside the first
k+1 coordinates, so the enumeration is a genuine (complete) tree search.  The
constructor asserts that every coordinate is two-sidedly bounded at its level;
otherwise it refuses to answer.  All integer arithmetic.
"""

import itertools
from hiveR import fixed_A, build_hive, interior


class Counter:
    def __init__(self, A, order=None):
        self.A = A
        self.D = len(A[0])
        self.order = list(range(self.D)) if order is None else list(order)
        pos = {c: i for i, c in enumerate(self.order)}
        # stage[k] = rows whose support lies in order[0..k] and uses order[k]
        self.stage = [[] for _ in range(self.D)]
        for ri, row in enumerate(A):
            sup = [j for j in range(self.D) if row[j] != 0]
            k = max(pos[j] for j in sup)
            self.stage[k].append(ri)
        for k in range(self.D):
            up = any(A[ri][self.order[k]] > 0 for ri in self.stage[k])
            lo = any(A[ri][self.order[k]] < 0 for ri in self.stage[k])
            if not (up and lo):
                raise ValueError("coordinate %d not two-sidedly bounded at its stage"
                                 % self.order[k])

    def count(self, b, scale=1):
        bb = [x * scale for x in b]
        x = [0] * self.D
        return self._rec(0, x, bb)

    def _rec(self, k, x, bb):
        A, order = self.A, self.order
        c = order[k]
        lo, hi = None, None
        for ri in self.stage[k]:
            row = A[ri]
            rem = bb[ri] - sum(row[j] * x[j] for j in order[:k])
            a = row[c]
            if a > 0:
                v = rem // a
                hi = v if hi is None or v < hi else hi
            else:
                v = -(rem // (-a))          # a < 0:  a*x <= rem  <=>  x >= ceil(rem/a)
                lo = v if lo is None or v > lo else lo
        if lo is None or hi is None or lo > hi:
            return 0
        if k == self.D - 1:
            return hi - lo + 1
        tot = 0
        for v in range(lo, hi + 1):
            x[c] = v
            tot += self._rec(k + 1, x, bb)
        x[c] = 0
        return tot


_CACHE = {}


def counter_for(r):
    if r not in _CACHE:
        A, Dm, tags = fixed_A(r)
        INT = interior(r)
        # order interior entries by (x+y, x) -- the natural hive fill order
        order = sorted(range(len(INT)), key=lambda i: (INT[i][0] + INT[i][1], INT[i][0]))
        for perm in [order, list(range(len(INT)))]:
            try:
                _CACHE[r] = (Counter(A, perm), A, Dm)
                break
            except ValueError:
                continue
        else:
            raise ValueError("no staged order found for r=%d" % r)
    return _CACHE[r]


def lr_count(lam, mu, nu, r, n=1):
    """#( n*Q(lam,mu,nu) cap Z^D ) exactly."""
    C, A, Dm = counter_for(r)
    H = build_hive(lam, mu, nu, r)
    if not H["ok"]:
        return 0
    return C.count(H["b"], n)


if __name__ == "__main__":
    import sys
    r = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    p = lambda s: [int(t) for t in s.replace(" ", ",").split(",") if t.strip()]
    print(lr_count(p(sys.argv[1]), p(sys.argv[2]), p(sys.argv[3]), r))
