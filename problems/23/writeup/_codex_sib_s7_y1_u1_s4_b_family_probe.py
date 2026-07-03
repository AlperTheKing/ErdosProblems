"""Exact positivity probe for the y=1,u=1,s4,b=1 family.

Set y=1, u=1, b=1, s4=0.  With m=x(1+v)+v and c=x+s,
write

    K = m-1-2c,
    A = a-1 = Q*K/c,
    f = (m-c-Q*K)/(1+c).

Then s4=0 is identical, and a>=1, f>=1 are built in when
0<=Q<=1 and 0<=s<=((m-1)/2)-x.  The other inactive slacks reduce to

    e >= max(v,c),
    d >= 1.
"""

from __future__ import annotations

from math import comb

import sympy as sp


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(poly, var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    return [
        sum(power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i)) for i in range(k + 1))
        for k in range(degree + 1)
    ]


def phi_expr(a: sp.Expr, c: sp.Expr, d: sp.Expr, e: sp.Expr, f: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    b = u = y = sp.Integer(1)
    m = x * (1 + v) + v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    Aterm = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Bterm = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    assert sp.factor(Y - m) == 0
    return 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * Aterm / Z + y * v * Bterm / (e * Y) - (a + b + c + d + e + f))


def coeff_stats(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> tuple[int, sp.Expr, int]:
    numerator, denominator = sp.together(expr).as_numer_denom()
    den_poly = sp.Poly(denominator, *variables)
    den_coeffs = den_poly.coeffs()
    assert den_coeffs
    assert all(c > 0 for c in den_coeffs)
    poly = sp.Poly(numerator, *variables)
    coeffs = [sp.Integer(c) if c.is_Integer else c for c in poly.coeffs()]
    neg = sum(1 for c in coeffs if c < 0)
    return len(coeffs), min(coeffs), neg


def assert_bernstein_positive(name: str, expr: sp.Expr, bounded: tuple[sp.Symbol, ...], unbounded: tuple[sp.Symbol, ...]) -> None:
    numerator, _ = sp.together(expr).as_numer_denom()
    coeffs = [numerator]
    for var in bounded:
        nxt: list[sp.Expr] = []
        for coeff in coeffs:
            nxt.extend(bernstein_coeffs(coeff, var))
        coeffs = nxt

    total_terms = 0
    min_coeff = None
    for coeff in coeffs:
        terms, this_min, neg = coeff_stats(coeff, unbounded)
        assert neg == 0, (name, terms, this_min, neg)
        total_terms += terms
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)
    print(f"{name}: coeffs={len(coeffs)} terms={total_terms} min={min_coeff}", flush=True)


def b_family_values(x: sp.Expr, v: sp.Expr, s: sp.Expr, q: sp.Expr):
    m = x * (1 + v) + v
    c = x + s
    K = sp.factor(m - 1 - 2 * c)
    a = 1 + q * K / c
    f = sp.cancel((m - c - q * K) / (1 + c))
    assert sp.factor(a * c + f * (1 + c) - m) == 0
    return a, c, f, K


def assert_x_ge_v_side() -> None:
    V, H, R, Q, D, E = sp.symbols("V H R Q D E", nonnegative=True)
    X = V + H
    x = 1 + X
    v = 1 + V
    s_max = sp.factor((x + 1) * (v - 1) / 2)
    s = R * s_max
    a, c, f, K = b_family_values(x, v, s, Q)
    # c>=v throughout this side.
    assert sp.factor(c - v - (H + s)) == 0
    assert_bernstein_positive(
        "b_x_ge_v",
        phi_expr(a, c, 1 + D, c + E, f, x, v),
        (R, Q),
        (V, H, D, E),
    )


def assert_v_ge_x_side() -> None:
    X, H, R, Q, D, E = sp.symbols("X H R Q D E", nonnegative=True)
    V = X + H
    x = 1 + X
    v = 1 + V
    s_max = sp.factor((x + 1) * (v - 1) / 2)

    # Low chamber: 0<=s<=H, so c<=v.
    s_low = R * H
    a_low, c_low, f_low, _ = b_family_values(x, v, s_low, Q)
    assert sp.factor(v - c_low - H * (1 - R)) == 0
    assert_bernstein_positive(
        "b_v_ge_x_low",
        phi_expr(a_low, c_low, 1 + D, v + E, f_low, x, v),
        (R, Q),
        (X, H, D, E),
    )

    # High chamber: H<=s<=s_max, so c>=v.
    width = sp.factor(s_max - H)
    s_high = H + R * width
    a_high, c_high, f_high, _ = b_family_values(x, v, s_high, Q)
    assert sp.factor(c_high - v - R * width) == 0
    assert_bernstein_positive(
        "b_v_ge_x_high",
        phi_expr(a_high, c_high, 1 + D, c_high + E, f_high, x, v),
        (R, Q),
        (X, H, D, E),
    )


def main() -> None:
    print("START b=1 broad s4 probe", flush=True)
    assert_x_ge_v_side()
    assert_v_ge_x_side()
    print("PASS y=1,u=1,s4,b=1 probe is Bernstein-positive")


if __name__ == "__main__":
    main()