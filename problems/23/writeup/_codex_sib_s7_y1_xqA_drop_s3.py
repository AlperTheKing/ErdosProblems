"""Exact closure of the XQ_A one-step drop:s3 face.

Work in the x=q, y=u=1 chart.  The XQ_A support has

    f=1, s3=s4=s5=s6=s7=0.

Dropping only s3 and keeping the other equations gives the positive branch

    f=1, c=e, b=d, a=(x^2 - 2 - s)/c,

where s=s3=b+c-x-1.  The domain is

    x>=2, c>=x-1, s>=0, b=x+1-c+s>=1, a>=1.

Put c=x-1+r.  The lower bound for s changes at r=1:

  * 0<=r<=1:        0 <= s <= x^2-x-1-r,
  * 1<=r<=x(x-1)/2: r-1 <= s <= x^2-x-1-r.

This verifier proves Phi is increasing in s on both regions by Bernstein
coefficients in the bounded variables, so the minimum is at s=0.  The s=0
boundary has 0<=r<=1 and is then Bernstein-positive as well.
"""

from __future__ import annotations

import sympy as sp


def power_to_bernstein(poly: sp.Expr, var: sp.Symbol, degree: int) -> list[sp.Expr]:
    """Return Bernstein coefficients on [0,1] for a polynomial in var."""
    P = sp.Poly(poly, var)
    out = [sp.Integer(0)] * (degree + 1)
    for k in range(degree + 1):
        ak = P.coeff_monomial(var**k)
        if ak == 0:
            continue
        for i in range(k, degree + 1):
            out[i] += ak * sp.Rational(sp.binomial(i, k), sp.binomial(degree, k))
    return [sp.factor(c) for c in out]


def assert_coeff_positive_in_X(expr: sp.Expr, X: sp.Symbol, label: str) -> None:
    poly = sp.Poly(sp.factor(expr), X)
    coeffs = poly.all_coeffs()
    bad = [c for c in coeffs if c < 0]
    assert not bad, (label, sp.factor(expr), bad[:3])


def assert_bernstein_X_positive(
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
        assert_coeff_positive_in_X(coeff, X, f"{label}:bernstein[{idx}]")


def main() -> None:
    a, b, c, d, e, f, x, s = sp.symbols("a b c d e f x s")
    X, R, T = sp.symbols("X R T")

    y = sp.Integer(1)
    u = sp.Integer(1)
    v = x - 1
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

    bb = x + 1 - c + s
    branch = {
        f: 1,
        e: c,
        d: bb,
        b: bb,
        a: (x**2 - 2 - s) / c,
    }
    Phi_branch = sp.factor(Phi.subs(branch))
    deriv_num = sp.together(sp.diff(Phi_branch, s)).as_numer_denom()[0]
    phi_num = sp.together(Phi_branch).as_numer_denom()[0]

    xx = X + 2

    # Region r in [0,1], s=T*(x^2-x-1-r).
    r0 = R
    upper0 = sp.expand(xx**2 - xx - 1 - r0)
    expr0 = sp.factor(
        deriv_num.subs({x: xx, c: xx - 1 + r0, s: T * upper0})
    )
    assert_bernstein_X_positive(expr0, (R, T), X, "dPhi/ds r<=1")

    # Region r in [1,x(x-1)/2], s=(r-1)+T*(x^2-x-1-r-(r-1)).
    max_r = xx * (xx - 1) / 2
    r1 = 1 + R * (max_r - 1)
    lower1 = r1 - 1
    upper1 = xx**2 - xx - 1 - r1
    ss1 = lower1 + T * (upper1 - lower1)
    # Clear harmless powers of 2 introduced by max_r.
    expr1 = sp.together(
        deriv_num.subs({x: xx, c: xx - 1 + r1, s: ss1}) * 8
    ).as_numer_denom()[0]
    expr1 = sp.factor(expr1)
    assert_bernstein_X_positive(expr1, (R, T), X, "dPhi/ds r>=1")

    # Boundary s=0.  Feasibility forces 0<=r<=1; prove numerator positive.
    boundary = sp.factor(phi_num.subs({x: xx, c: xx - 1 + R, s: 0}))
    assert_bernstein_X_positive(boundary, (R,), X, "Phi boundary s=0")

    print("PASS y=1 XQ_A drop:s3 face reduces to positive s=0 Bernstein boundary")


if __name__ == "__main__":
    main()
