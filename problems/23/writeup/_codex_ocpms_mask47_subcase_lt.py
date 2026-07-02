"""Symbolic probe for the hard complement of mask-47.

Mask 47 has active constraints:
  w5=w9, w6=w7, linL, linR, D0=m.

The already-closed subcase is q>=p and p*x>=q*y.  This script probes the
complement q>=p and p*x<q*y, where D19>=m supplies a second upper bound on
the free variable r.

Parametrization:
  q=p+s, s>=0
  x=1+h, y=x+d, d>=0

The condition p*x<q*y is automatic for s+d>0.  With D0 active,
  a=(x*p+y*q+q*p-r*(y+p))/p.

Feasible r bounds:
  r >= 1
  a>=1      gives r <= Ua
  D19>=m    gives r <= Ud

This first probe checks the branch where the D19 bound is active/tighter:
  1 <= r <= Ud.

It verifies the PMS margin numerator in the Bernstein basis on [1, Ud].
If coefficient positivity fails, the printed negative terms identify the
next required split/reservoir.
"""

import sympy as sp


def quartic_power_to_bernstein(poly, theta):
    ptheta = sp.Poly(poly, theta)
    degree = ptheta.degree()
    if degree > 4:
        raise ValueError(f"expected degree <=4, got {degree}")
    c = [ptheta.coeff_monomial(theta**i) for i in range(5)]
    return [
        sp.factor(c[0]),
        sp.factor(c[0] + c[1] / 4),
        sp.factor(c[0] + c[1] / 2 + c[2] / 6),
        sp.factor(c[0] + 3 * c[1] / 4 + c[2] / 2 + c[3] / 4),
        sp.factor(sum(c)),
    ]


def pms_numerator_for_mask47(p, s, x, y, r):
    q = p + s
    a = (x * p + y * q + q * p - r * (y + p)) / p
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = (
        a,
        x,
        y,
        y,
        x,
        p,
        q,
        q,
        r,
        p,
    )

    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    a27 = (
        w0 * w5
        + w0 * w6
        + w3 * w6
        + w3 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    a19 = (
        w0 * w5
        + w0 * w6
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )
    z79 = w0 * w5 * w6 + w3 * w4 * w8 + w3 * w6 * w8 + w4 * w5 * w8 + w5 * w6 * w8
    a79 = (
        w0 * w5
        + w0 * w6
        + w3 * w4
        + w3 * w6
        + w3 * w8
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )

    core = w0 + w3 + w4 + w5 + w6 + w8
    endpoints = w1 + w2 + w7 + w9
    f0 = 2 * (core + endpoints) ** 2 + 75 * core - 225 * w1 * w9 - 225 * w2 * w7 - 200 * w7 * w9
    reservoir = (
        75 * (sp.Rational(7, 3) - a19 / z19) * w1 * w9
        + 75 * (sp.Rational(7, 3) - a27 / z27) * w2 * w7
        + 75 * (2 - a79 / z79) * w7 * w9
    )
    num, den = sp.together(f0 + reservoir).as_numer_denom()
    return sp.factor(num), sp.factor(den)


def main() -> None:
    p, s, h, d, r = sp.symbols("p s h d r", positive=True)
    P, S, H, D = sp.symbols("P S H D", nonnegative=True)
    theta = sp.symbols("theta")

    x = 1 + h
    y = x + d
    q = p + s

    num, den = pms_numerator_for_mask47(p, s, x, y, r)
    print("denominator", sp.factor(den))
    print("degree_in_r", sp.Poly(num, r).degree())

    # D19-m = const - r*(q*y-p*x).  In this branch q*y-p*x>0.
    dgap = sp.expand(q * y - p * x)
    const = sp.expand(s * (p * q + p * x + q * y))
    Ud = sp.factor(const / dgap)
    print("Ud", Ud)

    transformed = sp.expand(num.subs(r, 1 + theta * (Ud - 1)))
    bernstein = quartic_power_to_bernstein(transformed, theta)

    verdict = True
    for i, coeff in enumerate(bernstein):
        coeff_num, coeff_den = sp.together(coeff).as_numer_denom()
        shifted = sp.Poly(
            sp.expand(coeff_num.subs({p: P + 1, s: S, h: H, d: D})),
            P,
            S,
            H,
            D,
        )
        neg = [(monom, c) for monom, c in shifted.terms() if c < 0]
        print(
            "B",
            i,
            "den",
            sp.factor(coeff_den),
            "terms",
            len(shifted.terms()),
            "negative",
            len(neg),
            "min_coeff",
            min(c for _, c in shifted.terms()),
        )
        if neg:
            verdict = False
            print("first_negative", neg[0])
    print("VERDICT", "PASS" if verdict else "FAIL")


if __name__ == "__main__":
    main()
