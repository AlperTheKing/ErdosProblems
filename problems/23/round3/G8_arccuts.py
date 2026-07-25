"""G8: is psi(And(k),x) = min over ARC cuts?

And(k) = K_{p/q}, p=3k-1, q=k: vertices Z_p, i~j iff q <= (i-j) mod p <= p-q.
An "arc cut" is S = {i, i+1, ..., i+m-1} (cyclically consecutive).
Compare min over the p(p-1) arc cuts with min over all 2^(p-1) cuts, on random
rational weightings (exact Fractions) and on the numeric maximisers.
"""
import sys, random
from fractions import Fraction
from itertools import combinations


def kpq(k):
    p, q = 3 * k - 1, k
    edges = []
    for i in range(p):
        for j in range(i + 1, p):
            d = (j - i) % p
            if q <= d <= p - q:
                edges.append((i, j))
    return p, q, edges


def mono_val(edges, side, x):
    s = 0
    for (u, v) in edges:
        if side[u] == side[v]:
            s += x[u] * x[v]
    return s


def all_cuts_min(p, edges, x):
    best = None
    arg = None
    for mask in range(1 << (p - 1)):
        side = [0] * p
        for v in range(1, p):
            side[v] = (mask >> (v - 1)) & 1
        s = mono_val(edges, side, x)
        if best is None or s < best:
            best = s; arg = tuple(side)
    return best, arg


def arc_cuts_min(p, edges, x):
    best = None; arg = None
    for i in range(p):
        for m in range(1, p):
            side = [0] * p
            for t in range(m):
                side[(i + t) % p] = 1
            s = mono_val(edges, side, x)
            if best is None or s < best:
                best = s; arg = (i, m)
    return best, arg


if __name__ == "__main__":
    random.seed(11)
    for k in (2, 3, 4, 5):
        p, q, edges = kpq(k)
        print(f"K_{{{p}/{q}}} = And({k}): p={p} |E|={len(edges)}")
        bad = 0
        trials = 200 if p <= 11 else 40
        for t in range(trials):
            if t == 0:
                x = [Fraction(1, p)] * p
            else:
                w = [random.randint(0, 12) for _ in range(p)]
                if sum(w) == 0:
                    continue
                tot = sum(w)
                x = [Fraction(wi, tot) for wi in w]
            a, arga = all_cuts_min(p, edges, x)
            b, argb = arc_cuts_min(p, edges, x)
            if b != a:
                bad += 1
                if bad <= 3:
                    print(f"   ARC-CUT GAP: x={[str(xi) for xi in x]}  allcuts={a} arccuts={b}"
                          f"  best cut={arga}")
        print(f"   trials={trials}  arc-cut failures={bad}")
        sys.stdout.flush()
