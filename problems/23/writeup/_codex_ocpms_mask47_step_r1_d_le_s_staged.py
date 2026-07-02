"""Staged common-denominator probe for mask-47 current r=1 step.

This is the same certificate target as _codex_ocpms_mask47_step_r1_d_le_s.py,
but avoids calling together() on the full difference.  Each rational summand is
converted separately, then a common numerator is assembled term-by-term.
"""

import sympy as sp


def rational_terms(w, sign=1):
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
    return [
        sign * f0,
        sign * 75 * (sp.Rational(7, 3) - a19 / z19) * w1 * w9,
        sign * 75 * (sp.Rational(7, 3) - a27 / z27) * w2 * w7,
        sign * 75 * (2 - a79 / z79) * w7 * w9,
    ]


def main() -> None:
    P, D, E, H = sp.symbols("P D E H", nonnegative=True)
    p = P + 1
    d = D
    e = E
    h = H
    s = d + e
    q = p + s
    x = 1 + h
    y = x + d
    r = sp.Integer(1)
    a = (x * p + y * q + q * p - y - p) / p
    r_prev = 1 + p / (y + p)

    current = (a, x, y, y, x, p, q, q, r, p)
    previous = (a - 1, x, y, y, x, p, q, q, r_prev, p)
    raw_terms = rational_terms(current, 1) + rational_terms(previous, -1)

    nums = []
    dens = []
    for i, term in enumerate(raw_terms):
        num, den = sp.together(term).as_numer_denom()
        nums.append(sp.expand(num))
        dens.append(sp.expand(den))
        print("term", i, "num_terms", len(sp.Poly(nums[-1], P, D, E, H).terms()))

    common = sp.prod(dens)
    poly = sp.Poly(0, P, D, E, H)
    for i, (num, den) in enumerate(zip(nums, dens)):
        addon = sp.Poly(sp.expand(num * (common / den)), P, D, E, H)
        poly += addon
        print("assembled", i, "terms", len(poly.terms()))

    terms = poly.terms()
    neg = [(monom, c) for monom, c in terms if c < 0]
    print("common_den_terms", len(sp.Poly(common, P, D, E, H).terms()))
    print("terms", len(terms), "negative", len(neg), "min_coeff", min(c for _, c in terms))
    if neg:
        print("first_negative", neg[0])
        raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
