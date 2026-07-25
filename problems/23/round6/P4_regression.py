"""MANDATORY REGRESSION (round5/claude_witness_regression.py) run on

  (i)  the certificate pair that item 7 proposes  ->  it PASSES the nine witnesses, which is why
       the round-5 sampling never saw the failure;
  (ii) the new witnesses W8 and W9, which break it;
  (iii) a REPLACEMENT rule that survives everything I could throw at it:
            R(mu) = min( min over arcs of length exactly 1/2 , min over arcs of length exactly 1/3 )
       i.e. the two arc-length families taken as MINIMA rather than as averages.

Both (i) and (iii) are evaluated exactly.  Nothing is claimed for (iii) beyond "not refuted by
these tests"; it is a suggestion, not a theorem.
"""
import sys
import random
from fractions import Fraction as F

sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round5")
from claude_witness_regression import WITNESSES, gamma, mono as r5_mono, arcbound as r5_arcbound

from P4_core import (from_gamma, sort_cyclic, adjacency, A_of, m_values, bound_k, arcbound,
                     psi, g_of, W_of, TARGET)
from P4_slide import min_m_circle, min_half_arcs

random.seed(11)

NEW = [
    ("W8 P4 falsifier (Gamma_20)", 20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
    ("W9 P4 falsifier, g const 3/8", 20, [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]),
]


def certificates(m, w):
    """returns (A, min_k bound_k, min over half-arcs, min over third-arcs, ARCBOUND, psi)"""
    pos, wt = sort_cyclic(*from_gamma(m, w))
    adj = adjacency(pos)
    A = A_of(pos, wt, adj)
    bs = [b for b in (bound_k(pos, wt, k, adj) for k in range(0, 13)) if b is not None]
    mv = m_values(pos, wt, adj)
    mh = min_half_arcs(pos, wt, adj)
    m3, _ = min_m_circle(pos, wt, adj)
    ab = arcbound(pos, wt, adj)
    ps = psi(pos, wt, adj) if len(pos) <= 20 else None
    return A, (min(bs) if bs else None), min(mv), mh, m3, ab, ps


def line(nm, m, w):
    A, bmin, mmin, mh, m3, ab, ps = certificates(m, w)
    item7 = min(A, bmin) if bmin is not None else A
    repl = min(mh, m3)
    fmt = lambda v: (f"{float(v):9.6f}" + ("*" if v > TARGET else " ")) if v is not None else "   n/a  "
    print(f"  {nm:30s} A={fmt(A)} min_k b_k={fmt(bmin)} minm={fmt(mmin)} "
          f"halfmin={fmt(mh)} thirdmin={fmt(m3)} | item7={fmt(item7)} repl={fmt(repl)} "
          f"ARCB={fmt(ab)} psi={fmt(ps)}")
    return item7 > TARGET, repl > TARGET


if __name__ == '__main__':
    print("=" * 132)
    print("REGRESSION: the nine recorded witnesses  (* = exceeds 1/25)")
    print("=" * 132)
    bad7 = badR = 0
    for nm, m, w, why in WITNESSES:
        a, b = line(nm, m, w)
        bad7 += a
        badR += b
    print(f"\n  item-7 certificate pair fails on {bad7}/9 recorded witnesses")
    print(f"  replacement rule       fails on {badR}/9 recorded witnesses")

    print("\n" + "=" * 132)
    print("THE NEW WITNESSES")
    print("=" * 132)
    for nm, m, w in NEW:
        a, b = line(nm, m, w)
        bad7 += a
        badR += b

    print("\n" + "=" * 132)
    print("RANDOM EXACT MEASURES (2000 draws, Gamma_5..Gamma_40, up to 12 atoms)")
    print("=" * 132)
    f7 = fR = 0
    worst7 = worstR = (F(0), None)
    for t in range(2000):
        m = random.choice([5, 7, 8, 10, 11, 13, 14, 16, 17, 18, 20, 23, 25, 26, 29, 32, 35, 40])
        k = random.randint(3, min(12, m))
        idx = random.sample(range(m), k)
        w = [0] * m
        for i in idx:
            w[i] = random.randint(1, 9)
        try:
            A, bmin, mmin, mh, m3, ab, ps = certificates(m, w)
        except Exception:
            continue
        item7 = min(A, bmin) if bmin is not None else A
        repl = min(mh, m3)
        if item7 > TARGET:
            f7 += 1
            if item7 > worst7[0]:
                worst7 = (item7, (m, tuple(w)))
        if repl > TARGET:
            fR += 1
            if repl > worstR[0]:
                worstR = (repl, (m, tuple(w)))
    print(f"  item-7 pair min(A, min_k bound_k) > 1/25 on {f7}/2000 random measures; "
          f"worst = {float(worst7[0]):.6f} at {worst7[1]}")
    print(f"  replacement min(half-min, third-min) > 1/25 on {fR}/2000 random measures; "
          f"worst = {float(worstR[0]):.6f} at {worstR[1]}")
