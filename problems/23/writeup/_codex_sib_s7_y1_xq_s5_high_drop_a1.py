"""Exact positivity for the XQ_S5_HIGH one-step drop:a1 face.

XQ_S5_HIGH is the x=q, y=1, s5-capacity support

    a=1, s1=s3=s4=s5=s6=s7=0, u=1.

Dropping only a=1 and keeping the other equations, the positive-domain
Groebner reduction forces

    u=1, v=e=c=x-1, b=d=2,
    a=(x^2+x-1-f*(x+1))/(x-1).

The domain is x>=2 and 1<=f<=x^2/(x+1).  Put x=X+2 and
f=1+R*(x^2/(x+1)-1), with 0<=R<=1.  The resulting Phi numerator and
denominator are Bernstein-positive in R with coefficient-positive polynomials
in X>=0.
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
    eqs = [slacks[name] for name in active if name != "a1"]
    G = sp.groebner(eqs, a, b, c, d, e, f, u, v, x, order="lex")
    basis = {sp.factor(poly.as_expr()) for poly in G.polys}
    assert sp.factor(f * (d - 2)) in basis
    assert sp.factor((-c + x - 1) * (-f * x - f + x**2 + x - 1)) in basis
    assert sp.factor(a * c + f * x + f - x**2 - x + 1) in basis
    assert sp.factor(b + c - x - 1) in basis
    assert sp.factor(e - x + 1) in basis
    assert sp.factor(u - 1) in basis
    assert sp.factor(v - x + 1) in basis

    # Since f>0, d=2.  If c != x-1, the product equation forces
    # f(x+1)=x^2+x-1, and then a*c=0 from the first displayed equation,
    # impossible in the positive domain.  Hence c=x-1.
    X, R = sp.symbols("X R")
    xx = X + 2
    fmax = xx**2 / (xx + 1)
    ff = 1 + R * (fmax - 1)
    aa = sp.factor((xx**2 + xx - 1 - ff * (xx + 1)) / (xx - 1))
    bb = dd = sp.Integer(2)
    cc = ee = vv = xx - 1
    uu = sp.Integer(1)

    assert sp.factor(fmax - 1 - (X**2 + 3 * X + 1) / (X + 3)) == 0
    assert sp.factor(aa - 1 - (1 - R) * (X**2 + 3 * X + 1) / (X + 1)) == 0

    Phi = sp.factor(phi_expr(aa, bb, cc, dd, ee, ff, xx, uu, vv))
    num, den = sp.together(Phi).as_numer_denom()
    assert_bernstein_coeff_positive(sp.factor(num), R, X, "Phi numerator")
    assert_bernstein_coeff_positive(sp.factor(den), R, X, "Phi denominator")

    print("PASS y=1 XQ_S5_HIGH drop:a1 face is Bernstein-positive")


if __name__ == "__main__":
    main()