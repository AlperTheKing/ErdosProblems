"""Step certificate probe for mask-47, current r=1, d<=s bucket.

Mask 47 active constraints:
  w5=w9, w6=w7, linL, linR, D0=m.

For the hard complement q>=p and p*x<q*y, write
  q=p+s, x=1+h, y=x+d, s=d+e.

This probe restricts to the boundary where the current point has r=1.
Then a is determined by D0=m:
  a=(x*p+y*q+q*p-y-p)/p.

The previous adjacent point in the a-lift is:
  a_prev=a-1, r_prev=1+p/(y+p).

The exact rational step difference is F(current)-F(previous).  This script
checks whether its numerator, after clearing positive denominators and
shifting p=1+P, has nonnegative coefficients in P,D,E,H.
"""

import sympy as sp


def pms_margin_expr(w):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
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
    return f0 + reservoir


def main() -> None:
    p, d, e, h = sp.symbols("p d e h", positive=True)
    P, D, E, H = sp.symbols("P D E H", nonnegative=True)

    s = d + e
    q = p + s
    x = 1 + h
    y = x + d
    r = sp.Integer(1)
    a = sp.factor((x * p + y * q + q * p - y - p) / p)
    r_prev = sp.factor(1 + p / (y + p))

    current = (a, x, y, y, x, p, q, q, r, p)
    previous = (a - 1, x, y, y, x, p, q, q, r_prev, p)
    diff = pms_margin_expr(current) - pms_margin_expr(previous)
    num, den = sp.together(diff).as_numer_denom()
    shifted_num = sp.expand(num.subs({p: P + 1, d: D, e: E, h: H}))
    poly = sp.Poly(shifted_num, P, D, E, H)
    terms = poly.terms()
    neg = [(monom, c) for monom, c in terms if c < 0]
    print("a", a)
    print("r_prev", r_prev)
    print("den", sp.factor(den))
    print("terms", len(terms), "negative", len(neg), "min_coeff", min(c for _, c in terms))
    if neg:
        print("first_negative", neg[0])
        raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
