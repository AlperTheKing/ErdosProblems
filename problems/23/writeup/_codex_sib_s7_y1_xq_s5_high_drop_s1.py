"""Exact positivity for the XQ_S5_HIGH one-step drop:s1 face.

Drop s1 from the XQ_S5_HIGH support while keeping

    a=1, s3=s4=s5=s6=s7=0, u=1, x=q.

The Groebner reduction gives

    a=1, u=1, v=x-1,
    b=d=f*(x+1)-x^2+2,
    c=e=x^2+x-1-f*(x+1).

Feasibility gives x>=2 and x^2-1 <= f*(x+1) <= x^2.  Put

    x=X+2,  f*(x+1)=x^2-1+R, 0<=R<=1.

Then b=d=1+R and c=e=x-R.  The substituted Phi numerator and denominator are
both negative; -numerator and -denominator are Bernstein-positive in R with
coefficient-positive polynomials in X>=0.
"""

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


def assert_coeff_positive(expr: sp.Expr, X: sp.Symbol, label: str) -> None:
    poly = sp.Poly(sp.factor(expr), X)
    bad = [coef for coef in poly.all_coeffs() if coef <= 0]
    assert not bad, (label, sp.factor(expr), bad[:3])


def assert_bernstein_coeff_positive(expr: sp.Expr, R: sp.Symbol, X: sp.Symbol, label: str) -> None:
    degree = sp.Poly(expr, R).degree()
    for idx, coeff in enumerate(power_to_bernstein(expr, R, degree)):
        assert_coeff_positive(coeff, X, f"{label}:bernstein[{idx}]")


def phi_expr(a, b, c, d, e, f, x, u, v):
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (N**2 - 25 * m) - 75 * (x * (u + v) * A / Z + v * B / (e * Y) - (a + b + c + d + e + f))


def main() -> None:
    a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v")
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    Y = a * c + b * f + c * f
    slacks = {
        "a1": a - 1,
        "s1": e - v,
        "s3": b + c - x - y,
        "s4": Y - m,
        "s5": a * e + b * f + c * f - m,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
        "u1": u - 1,
        "xq": x - u - v,
    }
    active = ("a1", "s1", "s3", "s4", "s5", "s6", "s7", "u1", "xq")
    eqs = [slacks[name] for name in active if name != "s1"]
    G = sp.groebner(eqs, a, b, c, d, e, f, u, v, x, order="lex")
    basis = {sp.factor(poly.as_expr()) for poly in G.polys}
    assert sp.factor(a - 1) in basis
    assert sp.factor(b - f * x - f + x**2 - 2) in basis
    assert sp.factor(c + f * x + f - x**2 - x + 1) in basis
    assert sp.factor(f * (d - f * x - f + x**2 - 2)) in basis
    assert sp.factor(e + f * x + f - x**2 - x + 1) in basis
    assert sp.factor(u - 1) in basis
    assert sp.factor(v - x + 1) in basis

    X, R = sp.symbols("X R")
    xx = X + 2
    T = xx**2 - 1 + R
    aa = sp.Integer(1)
    bb = dd = 1 + R
    cc = ee = xx - R
    ff = T / (xx + 1)
    uu = sp.Integer(1)
    vv = xx - 1

    assert sp.factor(ff - 1 - (R + X**2 + 3 * X) / (X + 3)) == 0
    assert sp.factor(ee - vv - (1 - R)) == 0

    Phi = sp.factor(phi_expr(aa, bb, cc, dd, ee, ff, xx, uu, vv))
    num, den = sp.together(Phi).as_numer_denom()
    assert_bernstein_coeff_positive(sp.factor(-num), R, X, "-Phi numerator")
    assert_bernstein_coeff_positive(sp.factor(-den), R, X, "-Phi denominator")

    print("PASS y=1 XQ_S5_HIGH drop:s1 face is Bernstein-positive")


if __name__ == "__main__":
    main()