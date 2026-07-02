"""Exact closure of the XQ_A one-step drop:u1 face.

In the x=q, y=1 chart, the XQ_A support is

    f=1, u=1, s3=s4=s5=s6=s7=0.

This script drops only u=1, keeping f=1 and s3=s4=s5=s6=s7=0.
The positive branch has

    c=e, b=d=x+1-c, a=(v+x^2-x-1)/c, u=x-v.

The domain is x>=2, 1<=v<=x-1, and v<=c<=x.  Put

    x=X+2, v=1+P*(x-2), c=v+R*(x-v), 0<=P,R<=1.

After substitution, the denominator has fixed negative sign.  Therefore
Phi>=0 is equivalent to nonnegativity of the negated numerator.  Bernstein
coefficients in (P,R) reduce this to univariate positivity in X>=0, which is
checked exactly by Sturm root counts.
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


def assert_positive_on_nonnegative_X(expr: sp.Expr, X: sp.Symbol, label: str) -> None:
    poly = sp.Poly(sp.factor(expr), X)
    assert poly.eval(0) > 0, (label, "value_at_0", sp.factor(expr))
    roots = sp.polys.polytools.count_roots(poly, 0, sp.oo)
    assert roots == 0, (label, "nonnegative_roots", roots, sp.factor(expr))


def assert_bernstein_sturm_positive(
    expr: sp.Expr, bounded: tuple[sp.Symbol, ...], X: sp.Symbol, label: str
) -> None:
    coeffs = [sp.factor(expr)]
    for var in bounded:
        next_coeffs: list[sp.Expr] = []
        for coeff in coeffs:
            degree = sp.Poly(coeff, var).degree()
            next_coeffs.extend(power_to_bernstein(coeff, var, degree))
        coeffs = next_coeffs

    for idx, coeff in enumerate(coeffs):
        assert_positive_on_nonnegative_X(coeff, X, f"{label}:bernstein[{idx}]")


def main() -> None:
    a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v")
    X, P, R = sp.symbols("X P R")

    y = sp.Integer(1)
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = (
        b * d
        + c * d
        + d * f
        + a * c
        + a * e
        + b * f
        + b * e
        + c * f
        + c * e
        + e * f
    )
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N**2 - 25 * m) - 75 * (
        x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)
    )

    # Algebraic reduction of the positive branch.
    s3 = b + c - x - y
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m
    assert sp.factor(s4 - s5) == a * (c - e)
    assert sp.factor((s4 - s6).subs(e, c)) == f * (b - d)
    # Since a,f>=1, c=e and then d=b.  With s3=0, b=d=x+1-c.

    branch = {
        f: 1,
        e: c,
        b: x + 1 - c,
        d: x + 1 - c,
        u: x - v,
        a: (v + x**2 - x - 1) / c,
    }
    assert sp.factor(s3.subs(branch)) == 0
    assert sp.factor(s4.subs(branch)) == 0
    assert sp.factor(s5.subs(branch)) == 0
    assert sp.factor(s6.subs(branch)) == 0
    assert sp.factor(s7.subs(branch)) == 0

    xx = X + 2
    vv = 1 + P * (xx - 2)
    cc = vv + R * (xx - vv)
    Phi_branch = sp.factor(Phi.subs(branch).subs({x: xx, v: vv, c: cc}))
    num, den = sp.together(Phi_branch).as_numer_denom()

    first = P * X + X**2 + 4 * X + 5
    exit_factor = P * R * X - P * X - R * X - R - 1
    H = (
        P**2 * R * X**2
        - P**2 * X**2
        + P * R * X**3
        + 2 * P * R * X**2
        + P * R * X
        - P * X**3
        - 3 * P * X**2
        - 3 * P * X
        - R * X**3
        - 4 * R * X**2
        - 5 * R * X
        - 2 * R
        - 2 * X**2
        - 9 * X
        - 11
    )
    assert sp.factor(den - first * exit_factor**2 * H) == 0
    assert sp.factor(-exit_factor - (P * X * (1 - R) + R * X + R + 1)) == 0

    neg_H = (
        P**2 * (1 - R) * X**2
        + P * (1 - R) * X**3
        + P * (3 - 2 * R) * X**2
        + P * (3 - R) * X
        + R * X**3
        + 4 * R * X**2
        + 5 * R * X
        + 2 * R
        + 2 * X**2
        + 9 * X
        + 11
    )
    assert sp.factor(H + neg_H) == 0
    assert_bernstein_sturm_positive(neg_H, (P, R), X, "-H")

    # Since den<0 on the domain, Phi>=0 is equivalent to -num>=0.
    assert_bernstein_sturm_positive(sp.factor(-num), (P, R), X, "-Phi numerator")

    print("PASS y=1 XQ_A drop:u1 face is Bernstein/Sturm-positive")


if __name__ == "__main__":
    main()
