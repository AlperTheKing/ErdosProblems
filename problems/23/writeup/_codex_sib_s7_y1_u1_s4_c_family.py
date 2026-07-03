"""Exact positivity certificate for the y=1,u=1,s4,c=1 family.

Set y=1, u=1, c=1, s4=0.  With m=x(1+v)+v and b=x+s,
write

    A = a-1 = Q*(s_max-s),
    f = (m-1-A)/(b+1),
    s_max = xv+v-2,

so a>=1, f>=1, and b>=x are built in.  The remaining feasibility
constraints reduce to e>=v and d+e>=b+1, matching the a=c=1 chamber
geometry but with one additional bounded variable Q.
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


def phi_expr(a: sp.Expr, b: sp.Expr, d: sp.Expr, e: sp.Expr, f: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    c = u = y = sp.Integer(1)
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


def assert_bernstein_positive(
    name: str,
    expr: sp.Expr,
    bounded: tuple[sp.Symbol, ...],
    unbounded: tuple[sp.Symbol, ...],
) -> None:
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


def c_family_values(x: sp.Expr, v: sp.Expr, s: sp.Expr, q: sp.Expr):
    m = x * (1 + v) + v
    s_max = sp.factor(x * v + v - 2)
    b = x + s
    A = q * (s_max - s)
    a = 1 + A
    f = sp.cancel((m - 1 - A) / (b + 1))
    assert sp.factor(a + f * (b + 1) - m) == 0
    return a, b, f, s_max


def assert_x_ge_v_side() -> None:
    V, H, R, Q, P, G = sp.symbols("V H R Q P G", nonnegative=True)
    X = V + H
    x = 1 + X
    v = 1 + V
    s_max = sp.factor(x * v + v - 2)
    s = R * s_max
    a, b, f, _ = c_family_values(x, v, s, Q)
    S = sp.factor(b - v)

    D_seg = P * S
    E_seg = b - 1 - D_seg
    assert_bernstein_positive(
        "c_x_ge_v_segment",
        phi_expr(a, b, 1 + D_seg, 1 + E_seg, f, x, v),
        (R, Q, P),
        (V, H),
    )

    D_ray = S + G
    E_ray = V
    assert_bernstein_positive(
        "c_x_ge_v_ray",
        phi_expr(a, b, 1 + D_ray, 1 + E_ray, f, x, v),
        (R, Q),
        (V, H, G),
    )


def assert_v_ge_x_side() -> None:
    X, H, R, Q, P, G = sp.symbols("X H R Q P G", nonnegative=True)
    V = X + H
    x = 1 + X
    v = 1 + V
    s_max = sp.factor(x * v + v - 2)

    # Low chamber: 0<=s<=H, so v>=b and e=v is the lower boundary.
    s_low = R * H
    a_low, b_low, f_low, _ = c_family_values(x, v, s_low, Q)
    assert_bernstein_positive(
        "c_v_ge_x_low",
        phi_expr(a_low, b_low, 1 + G, 1 + V, f_low, x, v),
        (R, Q),
        (X, H, G),
    )

    # High chamber: H<=s<=s_max, so b>=v.
    high_width = sp.factor(s_max - H)
    s_high = H + R * high_width
    a_high, b_high, f_high, _ = c_family_values(x, v, s_high, Q)
    S = sp.factor(b_high - v)

    D_seg = P * S
    E_seg = b_high - 1 - D_seg
    assert_bernstein_positive(
        "c_v_ge_x_high_segment",
        phi_expr(a_high, b_high, 1 + D_seg, 1 + E_seg, f_high, x, v),
        (R, Q, P),
        (X, H),
    )

    D_ray = S + G
    E_ray = V
    assert_bernstein_positive(
        "c_v_ge_x_high_ray",
        phi_expr(a_high, b_high, 1 + D_ray, 1 + E_ray, f_high, x, v),
        (R, Q),
        (X, H, G),
    )


def main() -> None:
    print("START y=1,u=1,s4,c=1 family", flush=True)
    assert_x_ge_v_side()
    assert_v_ge_x_side()
    print("PASS y=1,u=1,s4,c=1 family is Bernstein-positive")


if __name__ == "__main__":
    main()