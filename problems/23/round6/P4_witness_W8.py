"""W8 - the exact falsifier of item 7's OPEN step, re-verified through code that shares NOTHING
with P4_core (different indexing, different formulas, sympy Rationals instead of Fractions).

W8 = Gamma_20, integer weights (0,3,4,0,1,0,0,2,4,4,0,0,0,0,4,4,3,1,0,0), q = 30.

Claim being refuted (item 7 of the round-6 brief):

    for every probability measure on the circle with W in (0.12, 0.2),
        2T < W - 1/25   and   4W^2 + Var_mu(g) < W - 1/25,
    some level bound_k of the hierarchy is at most 1/25.

W8 satisfies both hypotheses and has min_b m(b) = 2/45 > 1/25, and bound_k is a convex
combination of the m(b), hence bound_k >= 2/45 > 1/25 for EVERY k >= 0 (indeed for every
non-negative weighting of the atoms whatsoever).
"""
from sympy import Rational, nsimplify

M = 20
W8 = [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]


def cdist(i, j, m=M):
    d = abs(i - j) % m
    return Rational(min(d, m - d), m)


def build(weights, m=M):
    q = sum(weights)
    return [Rational(w, q) for w in weights]


def main():
    x = build(W8)
    idx = list(range(M))
    # adjacency, from the definition d > 1/3, computed with sympy rationals
    E = [(i, j) for i in idx for j in idx if i < j and cdist(i, j) > Rational(1, 3)]
    W = sum(x[i] * x[j] for i, j in E)
    T = sum(cdist(i, j) * x[i] * x[j] for i, j in E)
    A = W - 2 * T
    g = [sum(x[j] for j in idx if j != i and cdist(i, j) > Rational(1, 3)) for i in idx]
    # m(b) computed as an explicit CUT VALUE: S = N(b), count monochromatic pairs directly
    mval = {}
    for b in idx:
        S = set(j for j in idx if cdist(b, j) > Rational(1, 3))
        mval[b] = sum(x[i] * x[j] for i, j in E if (i in S) == (j in S))
    supp = [i for i in idx if W8[i] > 0]
    minm = min(mval[b] for b in supp)
    var = sum(x[i] * g[i] ** 2 for i in idx) - (2 * W) ** 2

    print("W8 = Gamma_20 weights", W8, " q =", sum(W8))
    print("  support (as points of R/Z):", [Rational(i, M) for i in supp])
    print("  x on the support         :", [x[i] for i in supp])
    print()
    print(f"  W                = {W} = {float(W):.9f}      in (0.12, 0.2)?  {0.12 < float(W) < 0.2}")
    print(f"  T                = {T} = {float(T):.9f}")
    print(f"  2T               = {2*T} = {float(2*T):.9f}")
    print(f"  W - 1/25         = {W - Rational(1,25)} = {float(W - Rational(1,25)):.9f}")
    print(f"  HYPOTHESIS 1  2T < W - 1/25 : {2*T < W - Rational(1,25)}")
    print(f"  A = W - 2T       = {A} = {float(A):.9f}   > 1/25 ? {A > Rational(1,25)}")
    print()
    print(f"  Var_mu(g)        = {var} = {float(var):.9f}")
    print(f"  4W^2 + Var       = {4*W**2 + var} = {float(4*W**2+var):.9f}")
    print(f"  HYPOTHESIS 2  4W^2 + Var < W - 1/25 : {4*W**2 + var < W - Rational(1,25)}")
    print()
    print("  m(b) on the support:")
    for b in supp:
        print(f"     b = {Rational(b,M)}   g(b) = {g[b]}   m(b) = {mval[b]} = {float(mval[b]):.9f}"
              f"   {'> 1/25' if mval[b] > Rational(1,25) else '<= 1/25'}")
    print(f"  min over supp of m(b) = {minm} = {float(minm):.9f}")
    print(f"  CONCLUSION  every bound_k >= min_b m(b) = {minm} > 1/25 = {Rational(1,25)}: "
          f"{minm > Rational(1,25)}")
    print()
    # explicit bound_k for many k, from the definition, independently
    for k in [0, 1, 2, 3, 5, 10, 20, 50, 100]:
        num = sum(x[b] * g[b] ** k * mval[b] for b in idx if x[b] != 0)
        den = sum(x[b] * g[b] ** k for b in idx if x[b] != 0)
        v = num / den
        print(f"  bound_{k:<3d} = {float(v):.9f}  {'FAILS (>1/25)' if v > Rational(1,25) else 'closes'}")
    # the limit k -> infinity: average of m over the argmax-g atoms
    gmax = max(g[b] for b in supp)
    top = [b for b in supp if g[b] == gmax]
    lim = sum(x[b] * mval[b] for b in top) / sum(x[b] for b in top)
    print(f"  bound_inf = {lim} = {float(lim):.9f}  (average of m over argmax g)  "
          f"{'FAILS' if lim > Rational(1,25) else 'closes'}")

    # and the conjecture itself is untouched here
    best = None
    n = len(supp)
    for msk in range(1 << (n - 1)):
        side = {supp[i]: (msk >> i) & 1 for i in range(n - 1)}
        side[supp[-1]] = 0
        c = sum(x[i] * x[j] for i, j in E if W8[i] and W8[j] and side[i] == side[j])
        if best is None or c < best:
            best = c
    print(f"\n  psi(W8) = {best} = {float(best):.9f}   <= 1/25 ? {best <= Rational(1,25)}"
          f"   (so W8 is NOT a counterexample to Erdos 23)")


if __name__ == '__main__':
    main()
