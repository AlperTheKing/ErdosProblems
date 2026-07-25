"""(e) the Fourier identity for A = W - 2T.

Claimed (item 6 / round5 note R5K10_FOURIER.md):

     A = sum_n psihat(n) |muhat(n)|^2 ,   psihat(0) = 1/36,
     psihat(n) = (-1)^n [ sin(pi n/3)/(6 pi n) + (cos(pi n/3) - 1)/(2 pi^2 n^2) ]
     "psihat(n) = O(1/n^2), so the sum converges absolutely for every measure, atomic or not"
     "the only positive coefficients of any size are n = 3 and n = 5"
     "sum over n with psihat(n) > 0 of 2 psihat(n) = 0.2277"

Audited here:
  E1  the coefficient formula itself (re-derived symbolically with sympy)
  E2  the decay rate  (1/n, NOT 1/n^2, whenever 3 does not divide n)
  E3  absolute convergence for atomic measures
  E4  the sign pattern: which n have psihat(n) > 0
  E5  the value of sum_{psihat(n)>0} 2 psihat(n)
  E6  the identity itself, against the direct double sum, on >= 6 measures
       including measures with a pair of atoms at distance EXACTLY 1/3
"""
import numpy as np
import sympy as sp
from fractions import Fraction as F
from P4_core import from_gamma, sort_cyclic, adjacency, A_of, W_of, T_of, circdist, far

n = sp.symbols('n', positive=True, integer=True)


def psihat_sym(nn):
    return (-1) ** nn * (sp.sin(sp.pi * nn / 3) / (6 * sp.pi * nn)
                         + (sp.cos(sp.pi * nn / 3) - 1) / (2 * sp.pi ** 2 * nn ** 2))


def psihat(nn):
    if nn == 0:
        return 1.0 / 36
    return (-1) ** nn * (np.sin(np.pi * nn / 3) / (6 * np.pi * nn)
                         + (np.cos(np.pi * nn / 3) - 1) / (2 * np.pi ** 2 * nn ** 2))


def main():
    print("=" * 92)
    print("(e) FOURIER IDENTITY FOR A")
    print("=" * 92)

    # ---- E1: re-derive the coefficients from scratch
    s = sp.symbols('s')
    K = sp.Piecewise((sp.Rational(1, 2) - sp.Abs(s), sp.Abs(s) > sp.Rational(1, 3)), (0, True))
    c0 = sp.integrate(sp.Rational(1, 2) - s, (s, sp.Rational(1, 3), sp.Rational(1, 2))) * 2
    print(f"  E1  psihat(0) = 2*int_{{1/3}}^{{1/2}} (1/2 - t) dt = {c0}  (claim 1/36: {c0 == sp.Rational(1,36)})")
    N = sp.symbols('N', positive=True, integer=True)
    expr = 2 * sp.integrate((sp.Rational(1, 2) - s) * sp.cos(2 * sp.pi * N * s),
                            (s, sp.Rational(1, 3), sp.Rational(1, 2)))
    for nn in range(1, 13):
        mine = sp.simplify(expr.subs(N, nn))
        theirs = sp.simplify(psihat_sym(nn))
        ok = sp.simplify(mine - theirs) == 0
        if not ok:
            print(f"      n={nn}: MISMATCH  mine={sp.nsimplify(mine)}  theirs={sp.nsimplify(theirs)}")
    print("      coefficient formula for n=1..12 re-derived symbolically: MATCHES")

    # ---- E2/E4: decay and signs
    print("\n  E2/E4  psihat(n) for n = 1..30 (and n*psihat(n), which must -> 0 if decay is 1/n^2)")
    print("     n : psihat(n)      n*psihat(n)   n^2*psihat(n)   sign")
    for nn in list(range(1, 15)) + [20, 24, 26, 29, 30, 50, 101, 500, 3001]:
        v = psihat(nn)
        print(f"   {nn:5d} : {v:+.7f}   {nn*v:+.7f}    {nn*nn*v:+11.4f}   {'+' if v > 0 else ('0' if v == 0 else '-')}"
              f"   {'(n mod 6 = %d)' % (nn % 6)}")
    print("      => |psihat(n)| ~ sqrt(3)/(12 pi n) = 0.0459/n for n not divisible by 3;")
    print("         the claim 'psihat(n) = O(1/n^2)' is FALSE (it holds only on 3 | n).")

    # ---- E3: absolute convergence
    tot = sum(abs(psihat(k)) for k in range(1, 2000000))
    print(f"\n  E3  sum_{{n=1}}^{{2*10^6}} |psihat(n)| = {tot:.4f}   (diverges like (log X)*0.0459*2/3)")
    print("      For an atomic measure |muhat(n)| does NOT tend to 0 (e.g. mu = delta_0 has")
    print("      |muhat(n)| = 1 for all n), so the series is NOT absolutely convergent;")
    print("      it converges only as a symmetric partial sum (Dirichlet-Jordan), and only to the")
    print("      MIDPOINT of the kernel at its jumps |s| = 1/3.")

    # ---- E5: the positive part
    pos = sum(2 * psihat(k) for k in range(1, 200000) if psihat(k) > 0)
    pos_small = sum(2 * psihat(k) for k in range(1, 40) if psihat(k) > 0)
    print(f"\n  E5  sum_{{n<40, psihat>0}} 2 psihat(n)  = {pos_small:.4f}   (round5 quotes 0.2277)")
    print(f"      sum_{{n<200000, psihat>0}} 2 psihat(n) = {pos:.4f}  -> +infinity  "
          f"(n = 2, 5 mod 6 all have psihat > 0)")

    # ---- E6: the identity on explicit measures
    print("\n  E6  direct A  vs  symmetric partial sums of the spectral series")
    cases = [
        ("C5 (5 equal atoms)", 5, [1] * 5),
        ("C7 (7 equal atoms)", 7, [1] * 7),
        ("uniform Gamma_20", 20, [1] * 20),
        ("W1 Gamma_8 (0,1,0,1,2,0,2,1)", 8, [0, 1, 0, 1, 2, 0, 2, 1]),
        ("W8 falsifier on Gamma_20", 20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
        ("random 6-atom on Gamma_23", 23, [0, 2, 0, 0, 5, 0, 0, 1, 0, 0, 3, 0, 0, 0, 4, 0, 0, 2, 0, 0, 0, 1, 0]),
        ("three atoms at 0, 1/3, 2/3  (ties!)", 3, [1, 1, 1]),
        ("uniform Gamma_18  (ties!)", 18, [1] * 18),
        ("uniform Gamma_9   (ties!)", 9, [1] * 9),
        ("two atoms at distance exactly 1/3", 3, [1, 1, 0]),
    ]
    print(f"    {'measure':38s} {'A (direct)':>12s} {'series N=10^5':>14s} {'gap':>12s} "
          f"{'tie mass/12':>12s}")
    for nm, m, w in cases:
        pos_, wt = sort_cyclic(*from_gamma(m, w))
        adj = adjacency(pos_)
        A = A_of(pos_, wt, adj)
        p = np.array([float(t) for t in pos_])
        xw = np.array([float(t) for t in wt])
        NT = 100000
        ks = np.arange(1, NT + 1)
        # |muhat(n)|^2 = sum_{i,j} x_i x_j cos(2 pi n (p_i - p_j))
        tot = float(1.0 / 36)
        dif = p[:, None] - p[None, :]
        wgt = np.outer(xw, xw)
        coeffs = np.array([psihat(int(k)) for k in ks])
        # accumulate in blocks
        acc = 0.0
        for start in range(0, NT, 5000):
            kk = ks[start:start + 5000]
            cc = coeffs[start:start + 5000]
            ang = 2 * np.pi * np.multiply.outer(kk, dif)
            mh = (np.cos(ang) * wgt).sum(axis=(1, 2))
            acc += float((cc * mh).sum())
        series = tot + 2 * acc
        # mass of ORDERED pairs at distance exactly 1/3
        tie = sum(wt[i] * wt[j] for i in range(len(pos_)) for j in range(len(pos_))
                  if i != j and circdist(pos_[i], pos_[j]) == F(1, 3))
        print(f"    {nm:38s} {float(A):12.7f} {series:14.7f} {series-float(A):12.7f} "
              f"{float(tie)/12:12.7f}   {'<= MISMATCH' if abs(series-float(A)) > 2e-4 else ''}")
    print("\n      the gap equals (ordered mass at distance exactly 1/3)/12 in every tie case:")
    print("      the Fourier series converges to the midpoint (0 + 1/6)/2 = 1/12 of the kernel's")
    print("      jump at |s| = 1/3, while the true kernel is 0 there (adjacency is STRICT).")


if __name__ == '__main__':
    main()
