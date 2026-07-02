"""Symbolic check for one mask-47 OC-PMS face subcase.

Mask 47 has active constraints:
  w5=w9, w6=w7, linL, linR, D0=m.

Use variables:
  p=w5=w9, q=w6=w7, x=w1, y=w2, r=w8, a=w0.

The active equations give:
  w3=y, w4=x,
  a=(x*p+y*q+q*p-r*(y+p))/p.

This verifier closes the subcase:
  q>=p and p*x>=q*y.

Write q=p+s and x=y*q/p+h, where s,h>=0.  Then D19 is automatic, D27
follows from a>=1, and the feasible interval is 1 <= r <= U from a=1.
The PMS margin numerator is quartic in r.  We verify its Bernstein
coefficients on [1,U] have nonnegative shifted coefficients after
p=1+P, s=S, y=1+Y, h=H.
"""

import sympy as sp


def quartic_power_to_bernstein(poly, theta):
    p = sp.Poly(poly, theta)
    c = [p.coeff_monomial(theta**i) for i in range(5)]
    return [
        sp.factor(c[0]),
        sp.factor(c[0] + c[1] / 4),
        sp.factor(c[0] + c[1] / 2 + c[2] / 6),
        sp.factor(c[0] + 3 * c[1] / 4 + c[2] / 2 + c[3] / 4),
        sp.factor(sum(c)),
    ]


def main() -> None:
    p, s, y, h, r = sp.symbols("p s y h r", positive=True)
    P, S, Y, H = sp.symbols("P S Y H", nonnegative=True)

    q = p + s
    x = y * q / p + h
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

    num, _den = sp.together(f0 + reservoir).as_numer_denom()
    degree = sp.Poly(num, r).degree()
    if degree != 4:
        raise SystemExit(f"expected quartic in r, got degree {degree}")

    U = sp.solve(sp.Eq(a, 1), r)[0]
    theta = sp.symbols("theta")
    transformed = sp.expand(num.subs(r, 1 + theta * (U - 1)))
    bernstein = quartic_power_to_bernstein(transformed, theta)

    for i, coeff in enumerate(bernstein):
        coeff_num, coeff_den = sp.together(coeff).as_numer_denom()
        shifted = sp.Poly(sp.expand(coeff_num.subs({p: P + 1, s: S, y: Y + 1, h: H})), P, S, Y, H)
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
            print("first_negative", neg[0])
            raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
