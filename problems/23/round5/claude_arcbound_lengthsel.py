"""ROOT-AGENT (Claude): can CHOOSING the interval length from x beat the uniform-rotation average?

R3-C29 proved ARCBOUND(And(k)) <= (k-1)W/(3k-1) by averaging the interval cut A_i = {i..i+k-1} over
the m rotations. That is a FIXED averaging certificate in the sense of registry A6, and A6 is dead:
no fixed distribution over cuts can reach 1/25. Consistent with that, the bound leaves slack exactly
at a C5-concentration inside Gamma_11 (3/55 = 0.0545 vs the truth 0.04).

But the rotation average is only fixed once the interval LENGTH is fixed. Summing the cut value over
the m rotations of an interval of length L,

        sum_i q_{S_i}(x) = sum over edges of x_u x_v * f(L, d),
        f(L,d) = cnt_L(d) + cnt_{m-L}(d),   cnt_A(d) = max(0, A-d) + max(0, A-m+d),

because an edge is monochromatic for the cut iff both ends lie in the interval or both lie in its
complement. f(L,d) is CONSTANT in d only at L = k (value k-1); at other lengths it is genuinely
d-dependent, so different lengths penalise different edge-distances. Choosing L as a function of x is
a weight-reading rule, NOT a fixed distribution over cuts, so A6 does not apply to

        ARCBOUND(x)  <=  B(x) := (1/m) * min over L of  sum over edges of x_u x_v * f(L, d_e).

This script computes the exact profiles f(L,.), then tests whether B(x) <= (sum x)^2/25 -- which, if
true, would prove Codex's frontier lemma outright. The honest expectation is that it fails somewhere;
the point is to find out WHERE, exactly, since that locates what a weight-reading rule must still do.
"""
from fractions import Fraction as F

import numpy as np


def gamma_k(k):
    m = 3 * k - 1
    E = [(u, v) for u in range(m) for v in range(u + 1, m)
         if min((u - v) % m, (v - u) % m) >= k]
    return m, E


def cnt(Aa, d, m):
    return max(0, Aa - d) + max(0, Aa - m + d)


def prof(L, m):
    return {d: cnt(L, d, m) + cnt(m - L, d, m) for d in range(1, m // 2 + 1)}


for k in (2, 3, 4):
    m, E = gamma_k(k)
    print(f"\n=== And({k}) = Gamma_{m}, adjacency distances {sorted({min((u-v)%m,(v-u)%m) for u,v in E})} ===")
    print(f"  {'L':>3s}  f(L,d) over the adjacency distances")
    dists = sorted({min((u - v) % m, (v - u) % m) for u, v in E})
    for L in range(1, m):
        p = prof(L, m)
        print(f"  {L:3d}  {[p[d] for d in dists]}"
              + ("   <- constant, the R3-C29 family" if len({p[d] for d in dists}) == 1 else ""))

print("\n=== does the length-selected bound B(x) <= (sum x)^2/25 hold? ===")
rng = np.random.default_rng(20260726)
for k in (2, 3, 4, 5):
    m, E = gamma_k(k)
    dist = {(u, v): min((u - v) % m, (v - u) % m) for (u, v) in E}
    profs = [prof(L, m) for L in range(1, m)]
    viol = 0
    worst = None
    tested = 0
    for trial in range(6000):
        a = rng.integers(0, 9, size=m)
        q = int(a.sum())
        if q == 0:
            continue
        tested += 1
        # exact B(x) with x = a/q, in integers: B = min_L sum_e a_u a_v f / (m q^2)
        best = None
        for p in profs:
            s = sum(int(a[u]) * int(a[v]) * p[dist[(u, v)]] for (u, v) in E)
            if best is None or s < best:
                best = s
        # true ARCBOUND for comparison, over every interval cut
        arc = None
        for L in range(1, m):
            for i in range(m):
                S = {(i + t) % m for t in range(L)}
                val = sum(int(a[u]) * int(a[v]) for (u, v) in E if (u in S) == (v in S))
                if arc is None or val < arc:
                    arc = val
        lhs = F(best, m)
        rhs = F(q * q, 25)
        if lhs > rhs:
            viol += 1
            r = lhs / rhs
            if worst is None or r > worst[0]:
                worst = (r, a.tolist(), lhs, rhs, arc)
    print(f"  And({k}): {tested} exact weightings;  B(x) > (sum x)^2/25 in {viol}")
    if worst:
        r, a, lhs, rhs, arc = worst
        print(f"    worst ratio {float(r):.4f} at a = {a}")
        print(f"      B = {lhs}, target = {rhs}, and the TRUE ARCBOUND = {arc} "
              f"(<= target: {F(arc,1) <= rhs})")
