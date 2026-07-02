from __future__ import annotations

import sympy as sp


def power_to_bernstein(poly: sp.Expr, var: sp.Symbol, degree: int) -> list[sp.Expr]:
    P = sp.Poly(poly, var)
    out = [sp.Integer(0)] * (degree + 1)
    for k in range(degree + 1):
        ak = P.coeff_monomial(var**k)
        if ak == 0:
            continue
        for i in range(k, degree + 1):
            out[i] += ak * sp.Rational(sp.binomial(i, k), sp.binomial(degree, k))
    return [sp.factor(c) for c in out]


def main() -> None:
    X, P, R = sp.symbols("X P R", nonnegative=True)
    x = X + 2
    v = 1 + P * (x - 2)
    c = v + R * (x - v)
    e = c
    b = d = x + 1 - c
    f = sp.Integer(1)
    a = (v + x * x - x - 1) / c
    y = sp.Integer(1)
    u = x - v
    m = x * x + v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * x * A / Z + v * B / (e * Y) - (a + b + c + d + e + f)))
    num, den = sp.together(Phi).as_numer_denom()
    print("den_origin", den.subs({X: 0, P: 0, R: 0}))
    coeffs = [sp.factor(-num)]
    for var in (P, R):
        nxt = []
        for coeff in coeffs:
            degree = sp.Poly(coeff, var).degree()
            nxt.extend(power_to_bernstein(coeff, var, degree))
        coeffs = nxt
    bad = []
    for idx, coeff in enumerate(coeffs):
        poly = sp.Poly(sp.factor(coeff), X)
        if any(c0 < 0 for c0 in poly.all_coeffs()):
            bad.append((idx, sp.factor(coeff)))
            if len(bad) >= 3:
                break
    print("coeff_count", len(coeffs), "bad", len(bad))
    for row in bad:
        print("BAD", row[0], row[1])


if __name__ == "__main__":
    main()
