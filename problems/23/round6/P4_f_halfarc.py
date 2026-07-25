"""Is A really the AVERAGE of the half-arc cuts (which is what makes A >= ARCBOUND legitimate)?

Claim implicit in item 5: A = W - 2T is the mean of mono(S_a) over a uniformly random half-arc
S_a = [a, a+1/2).  Proof sketch: a far pair at distance d is separated by S_a for a set of a of
measure exactly 2d, so E[cross] = 2T and E[mono] = W - 2T.  Verified here by EXACT integration over
a (the cut is piecewise constant in a, with breakpoints at the atoms and their antipodes), on the
witnesses and on random measures.  min <= mean gives ARCBOUND <= A.
"""
import random
from fractions import Fraction as F
from P4_core import (from_gamma, sort_cyclic, adjacency, A_of, mono, arcbound, TARGET)

random.seed(2026)


def half_arc_average(pos, wt, adj):
    """exact mean over a in [0,1) of mono([a, a+1/2))"""
    bps = sorted(set([p % 1 for p in pos] + [(p + F(1, 2)) % 1 for p in pos]))
    tot = F(0)
    n = len(bps)
    for i in range(n):
        a, c = bps[i], bps[(i + 1) % n]
        length = (c - a) if c > a else (c + 1 - a)
        mid = (a + length / 2) % 1
        inS = [((p - mid) % 1) < F(1, 2) for p in pos]
        tot += length * mono(pos, wt, inS, adj)
    return tot


CASES = [("C5", 5, [1] * 5), ("C7", 7, [1] * 7), ("uniform Gamma_18", 18, [1] * 18),
         ("uniform Gamma_20", 20, [1] * 20),
         ("W1 Gamma_8", 8, [0, 1, 0, 1, 2, 0, 2, 1]),
         ("W8", 20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
         ("W9", 20, [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]),
         ("3 atoms at 0,1/3,2/3", 3, [1, 1, 1]),
         ("near-path Gamma_12", 12, [3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0])]

if __name__ == '__main__':
    print(f"  {'measure':24s} {'A = W-2T':>12s} {'mean over half-arcs':>21s} {'equal':>7s} "
          f"{'ARCBOUND':>10s} {'A>=ARCB':>8s}")
    ok = True
    for nm, m, w in CASES:
        pos, wt = sort_cyclic(*from_gamma(m, w))
        adj = adjacency(pos)
        A = A_of(pos, wt, adj)
        av = half_arc_average(pos, wt, adj)
        ab = arcbound(pos, wt, adj)
        ok &= (A == av) and (A >= ab)
        print(f"  {nm:24s} {str(A):>12s} {str(av):>21s} {str(A == av):>7s} "
              f"{str(ab):>10s} {str(A >= ab):>8s}")
    bad = 0
    for _ in range(200):
        m = random.choice([5, 7, 8, 11, 13, 14, 17, 18, 20, 23])
        w = [random.randint(0, 5) for _ in range(m)]
        if sum(w) == 0:
            continue
        pos, wt = sort_cyclic(*from_gamma(m, w))
        adj = adjacency(pos)
        if A_of(pos, wt, adj) != half_arc_average(pos, wt, adj):
            bad += 1
    print(f"\n  200 random measures: A == half-arc average in {200-bad}/200 cases")
    print(f"  => A is a genuine averaged bound, so ARCBOUND <= A holds; verdict: "
          f"{'CONFIRMED' if ok and bad == 0 else 'FAILED'}")
