"""ROOT-AGENT (Claude): a sharpening of the recorded A1 bound ARCBOUND <= W/3 on Andrasfai graphs.

CLAIM (mine). For And(k) = Gamma_m with m = 3k-1 and adjacency "circdist >= k", and any x >= 0,
        ARCBOUND(x)  <=  (k-1)/(3k-1) * W,        W = sum over edges of x_u x_v.
Since (k-1)/(3k-1) < 1/3 for every finite k, and -> 1/3 as k -> infinity, this is a strict
improvement on the recorded W/3 at every k, recovering it only in the limit. It is TIGHT at C5.

PROOF. Two observations.
 (1) An interval of length k is INDEPENDENT: two vertices inside it are at circular distance <= k-1,
     below the adjacency threshold k. So for the interval cut A_i = {i, ..., i+k-1}, no monochromatic
     edge lies inside A_i, and every monochromatic edge lies inside the complementary interval
     B_i of length m - k = 2k-1. Hence ARCBOUND <= min_i e(B_i), where e(B) is the weight of the
     edges with both ends in B.
 (2) Every edge lies in EXACTLY k-1 of the m intervals B_i, independent of its length. An edge has
     circdist d with k <= d <= 2k-1 (the maximum circular distance on Z_{3k-1} is (3k-2)/2, and
     adjacency needs d >= k). A (2k-1)-interval contains both ends iff it contains one of the two
     arcs joining them: the short arc has d+1 vertices and fits in (2k-1)-(d+1)+1 = 2k-1-d
     positions; the long arc has m-d+1 = 3k-d vertices and fits in (2k-1)-(3k-d)+1 = d-k positions.
     Both counts are nonnegative exactly in the range k <= d <= 2k-1, and they sum to
     (2k-1-d) + (d-k) = k-1, with no dependence on d.
 Therefore sum_i e(B_i) = (k-1) * W, and the minimum is at most the average:
        ARCBOUND <= min_i e(B_i) <= (k-1)W/m = (k-1)W/(3k-1).   QED

Both steps are combinatorial identities, so this script verifies them exactly and then checks the
inequality itself on random exact weightings.

HONEST LIMIT, stated up front: this is an AVERAGING bound over the m rotations, and registry A6
records that fixed averaging certificates cannot reach 1/25. Consistent with that, at the
C5-concentration on Gamma_11 it gives 3W/11 = 3/55 = 0.0545 against the truth 1/25 = 0.04, so it
does NOT close the frontier lemma. What it does is shrink the open window in W.
"""
from fractions import Fraction as F

import numpy as np


def gamma_k(k):
    m = 3 * k - 1
    E = [(u, v) for u in range(m) for v in range(u + 1, m)
         if min((u - v) % m, (v - u) % m) >= k]
    return m, E


print(f"{'k':>3s} {'m':>4s} {'|E|':>5s} {'k-interval independent':>23s} "
      f"{'edges in exactly k-1 B_i':>26s} {'(k-1)/(3k-1)':>14s} {'vs 1/3':>10s}")
for k in range(2, 9):
    m, E = gamma_k(k)
    # (1) intervals of length k are independent
    indep = True
    for i in range(m):
        I = {(i + t) % m for t in range(k)}
        if any(u in I and v in I for (u, v) in E):
            indep = False
    # (2) every edge lies in exactly k-1 of the m intervals of length 2k-1
    counts = set()
    for (u, v) in E:
        c = 0
        for i in range(m):
            B = {(i + t) % m for t in range(2 * k - 1)}
            if u in B and v in B:
                c += 1
        counts.add(c)
    ok2 = (counts == {k - 1})
    r = F(k - 1, 3 * k - 1)
    print(f"{k:3d} {m:4d} {len(E):5d} {str(indep):>23s} "
          f"{(str(sorted(counts)) + ' = {' + str(k-1) + '}') if ok2 else str(sorted(counts)):>26s} "
          f"{str(r):>14s} {'<' if r < F(1,3) else '>=':>10s}")

print("\nnow the inequality itself, on exact random weightings")
rng = np.random.default_rng(20260726)
for k in (2, 3, 4, 5):
    m, E = gamma_k(k)
    worst = None
    viol = 0
    for trial in range(4000):
        a = rng.integers(0, 10, size=m)
        if a.sum() == 0:
            continue
        x = [F(int(t), int(a.sum())) for t in a]
        W = sum(x[u] * x[v] for (u, v) in E)
        arc = None
        for i in range(m):
            A_ = {(i + t) % m for t in range(k)}
            val = sum(x[u] * x[v] for (u, v) in E if (u in A_) == (v in A_))
            if arc is None or val < arc:
                arc = val
        bound = F(k - 1, 3 * k - 1) * W
        if arc > bound:
            viol += 1
        ratio = (arc / W) if W > 0 else F(0)
        if worst is None or ratio > worst:
            worst = ratio
    print(f"  And({k}) = Gamma_{m}: 4000 exact weightings, violations of ARCBOUND <= "
          f"{F(k-1,3*k-1)}*W: {viol};  max observed ARCBOUND/W = {worst} = {float(worst):.6f} "
          f"(bound {float(F(k-1,3*k-1)):.6f})")

print("\ntightness at C5 (k = 2), and the slack at the Gamma_11 extremal point")
m, E = gamma_k(2)
x = [F(1, 5)] * 5
W = sum(x[u] * x[v] for (u, v) in E)
arc = min(sum(x[u] * x[v] for (u, v) in E if ((u in {(i+t) % 5 for t in range(2)}) ==
                                             (v in {(i+t) % 5 for t in range(2)})))
          for i in range(5))
print(f"  C5 uniform: W = {W}, ARCBOUND = {arc}, bound = {F(1,5)*W} -> tight: {arc == F(1,5)*W}")
m, E = gamma_k(4)
c5 = [0, 3, 7, 10, 4]
x = [F(0)] * 11
for v in c5:
    x[v] = F(1, 5)
W = sum(x[u] * x[v] for (u, v) in E)
print(f"  Gamma_11 at a C5-concentration: W = {W}, bound 3W/11 = {F(3,11)*W} = "
      f"{float(F(3,11)*W):.6f} vs truth 1/25 = 0.04  -> slack, so this bound alone cannot close it")
print(f"  open window in W for Gamma_11 narrows from W > 3/25 = {float(F(3,25)):.5f} "
      f"to W > 11/75 = {float(F(11,75)):.5f}")
