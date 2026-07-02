"""Symbolic check for the OC-PMS six-active mask-125 face.

Mask 125 is the seven-cut face with all constraints active except `w6=w7`.
Mask 126 is its left/right mirror.

On mask 125:
  w5=w9=t, w6=t, w7=u, u<=t
  w2=w3=w4=b
  w1=b+t-u

The active D equations give
  r=w8=(b*(t+u)+t^2-a*t)/(b+t).

The domain r>=1 gives an interval
  1 <= a <= Amax=(b*(t+u)+t^2-b-t)/t.

After substituting t=u+s (s>=0), the PMS margin numerator is cubic in a.
This script verifies that its Bernstein coefficients on [1,Amax] have
nonnegative shifted coefficients after b=1+B, u=1+U, s=S.
"""

import sympy as sp


def main() -> None:
    a, b, u, s = sp.symbols("a b u s", positive=True)
    B, U, S = sp.symbols("B U S", nonnegative=True)
    t = u + s
    x = b + s
    r = (b * (t + u) + t**2 - a * t) / (b + t)

    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = (
        a,
        x,
        b,
        b,
        b,
        t,
        t,
        u,
        r,
        t,
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
    degree = sp.Poly(num, a).degree()
    if degree != 3:
        raise SystemExit(f"expected cubic in a, got degree {degree}")

    amax = (b * (t + u) + t**2 - b - t) / t
    h = amax - 1
    dnum = sp.diff(num, a)
    bernstein = [
        num.subs(a, 1),
        num.subs(a, 1) + h * dnum.subs(a, 1) / 3,
        num.subs(a, amax) - h * dnum.subs(a, amax) / 3,
        num.subs(a, amax),
    ]

    for i, coeff in enumerate(bernstein):
        coeff_num, coeff_den = sp.together(coeff).as_numer_denom()
        shifted = sp.Poly(sp.expand(coeff_num.subs({b: B + 1, u: U + 1, s: S})), B, U, S)
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
