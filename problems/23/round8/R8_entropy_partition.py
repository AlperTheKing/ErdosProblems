"""The canonical 5-partition certificate.

By THEOREM R8-2 (rigidity, see R8_entropy_rigidity.py) any fixed cut certificate
must be supported on rainbow-1 cuts.  Computation shows that for every graph
tested that has one, there are exactly five, and their monochromatic edge sets
PARTITION E(H).  Writing F_1..F_5 for that partition and

        q_j(a) = sum_{uv in F_j} a_u a_v,

the whole content of the fixed-certificate route on H is the single inequality

        (TERM_H)      q_1 q_2 q_3 q_4 q_5  <=  (sum a)^10 / 5^10 ,   a >= 0,

because psi(H,a) <= min_j q_j <= (prod q_j)^{1/5}.  Note sum_j q_j = W(a) is the
total edge weight, so the AM-GM relaxation of (TERM_H) is exactly W <= (sum a)^2/5.

This script
  * extracts the canonical partition,
  * checks the partition property exactly,
  * searches for a violation of (TERM_H) over all nonnegative integer weightings
    with sum a = q (exact integer arithmetic), and by continuous optimisation.
"""

import itertools
import sys
from fractions import Fraction

from R8_entropy_core import (cycle, blowup, petersen, grotzsch, wagner,
                             andrasfai, bip_weighted)
from R8_entropy_rigidity import rainbow1_cuts


def canonical_partition(g):
    n, edges = g
    pents, hits = rainbow1_cuts(g)
    classes = [sorted(m) for _, m in hits]
    allE = set(edges)
    cover = {}
    for c in classes:
        for e in c:
            cover[e] = cover.get(e, 0) + 1
    is_partition = (len(classes) > 0 and set(cover) == allE
                    and all(v == 1 for v in cover.values()))
    return classes, is_partition, pents


def qvals(classes, a):
    return [sum(a[u] * a[v] for (u, v) in F) for F in classes]


def int_search(g, classes, qmax, report=True):
    """Exhaustive over all a >= 0 with sum a = q <= qmax.  Exact integers.
    Returns the worst ratio  5^10 * prod q_j / q^10  as a Fraction."""
    n, _ = g
    worst = Fraction(0)
    argworst = None
    for q in range(1, qmax + 1):
        tgt = q ** 10
        for a in compositions(q, n):
            p = 1
            for F in classes:
                s = 0
                for (u, v) in F:
                    s += a[u] * a[v]
                p *= s
                if p == 0:
                    break
            r = Fraction(5 ** 10 * p, tgt)
            if r > worst:
                worst, argworst = r, (q, tuple(a))
    return worst, argworst


def compositions(q, n):
    """All nonnegative integer vectors of length n summing to q."""
    if n == 1:
        yield [q]
        return
    for first in range(q + 1):
        for rest in compositions(q - first, n - 1):
            yield [first] + rest


def continuous_max(g, classes, restarts=400, seed=0):
    """Numerical max of 5^10 prod q_j / (sum a)^10 (guidance only)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    n, _ = g
    idx = [np.array(F, dtype=int) for F in classes]
    best, barg = 0.0, None

    def val(a):
        a = np.maximum(a, 0)
        s = a.sum()
        if s <= 0:
            return 0.0
        p = 1.0
        for F in idx:
            p *= float((a[F[:, 0]] * a[F[:, 1]]).sum())
        return p * 5.0 ** 10 / s ** 10

    for _ in range(restarts):
        a = rng.random(n)
        if rng.random() < 0.5:
            a *= (rng.random(n) < 0.6)
        cur = val(a)
        step = 0.3
        for _ in range(4000):
            b = np.maximum(a + rng.normal(0, step, n), 0)
            v = val(b)
            if v > cur:
                a, cur = b, v
            step *= 0.9993
        if cur > best:
            best, barg = cur, a / a.sum()
    return best, barg


if __name__ == "__main__":
    C5 = cycle(5)
    graphs = [
        ("C5", C5, 25),
        ("C5[2]", blowup(C5, [2] * 5), 14),
        ("Wagner=And(3)", wagner(), 18),
        ("Petersen", petersen(), 16),
        ("Grotzsch", grotzsch(), 14),
        ("And(4)", andrasfai(4), 0),
    ]
    for name, g, qmax in graphs:
        classes, is_part, pents = canonical_partition(g)
        n, edges = g
        print(f"\n=== {name}: n={n} |E|={len(edges)} bip={bip_weighted(g,[1]*n)[0]} "
              f"#indC5={len(pents)} #rainbow1={len(classes)} "
              f"partition_of_E={is_part}")
        if not classes:
            print("    NO rainbow-1 cut -> fixed certificate impossible "
                  "(any aggregator).")
            continue
        for j, F in enumerate(classes):
            print(f"    F_{j+1} = {F}")
        if is_part and len(classes) == 5:
            cm, carg = continuous_max(g, classes, restarts=120)
            print(f"    continuous max of 5^10*prod q_j/(sum a)^10 : {cm:.9f}")
            print(f"      at a ~ {None if carg is None else [round(t,4) for t in carg]}")
            if qmax:
                w, arg = int_search(g, classes, qmax)
                print(f"    EXACT integer sweep sum a <= {qmax}: worst ratio "
                      f"{w} = {float(w):.9f}  at {arg}")
                print(f"    -> {'HOLDS (<=1)' if w <= 1 else 'VIOLATED (>1)'} "
                      f"on the swept range")
