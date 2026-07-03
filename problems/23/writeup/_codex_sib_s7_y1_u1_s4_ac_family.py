"""Exact positivity for the y=1,u=1,s4,a=c=1 family.

Set

    y=1, u=1, s4=0, a=c=1.

With

    m = x(1+v)+v,

the equation `s4=0` is

    1 + f(b+1) = m,

so it is convenient to write

    b = x+s,              f = (m-1)/(b+1).

The constraint `f>=1` gives

    0 <= s <= xv+v-2.

The remaining feasibility inequalities reduce to

    e >= v,       d+e >= b+1.

Write `x=1+X`, `v=1+V`.  Split by `X>=V` and `V>=X`.

If `X>=V`, then `b>=x>=v` throughout.  The minimum over the feasible
region is checked on:

    D = Q(b-v),        E = b-1-D,       0<=Q<=1,        (segment)
    D = b-v+G,         E = V,                           (ray)

where `d=1+D`, `e=1+E`.

If `V>=X`, write `V=X+H`.  The chamber `0<=s<=H` has `v>=b`, so the
minimum is on `E=V`.  The chamber `H<=s<=xv+v-2` has `b>=v`, and is
checked by the same segment/ray split.

Every bounded variable is certified in the Bernstein basis.  Denominators
are structurally positive because `b+1`, `e`, `Y`, and `Z` are positive on
the feasible region; the final Bernstein coefficients also have positive
denominators after collection.
"""

from __future__ import annotations

from math import comb

import sympy as sp


def phi_expr(b: sp.Expr, d: sp.Expr, e: sp.Expr, f: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    a = c = u = y = sp.Integer(1)
    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(poly, var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    out = []
    for k in range(degree + 1):
        coeff = 0
        for i in range(k + 1):
            coeff += power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i))
        out.append(sp.factor(coeff))
    return out


def coeff_stats(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> tuple[int, sp.Integer, int]:
    numerator, denominator = sp.together(expr).as_numer_denom()
    den_poly = sp.Poly(denominator, *variables)
    den_coeffs = [sp.Integer(c) for c in den_poly.coeffs()]
    assert den_coeffs
    assert all(c > 0 for c in den_coeffs)
    poly = sp.Poly(numerator, *variables)
    coeffs = [sp.Integer(c) for c in poly.coeffs()]
    neg = sum(1 for c in coeffs if c < 0)
    return len(coeffs), min(coeffs), neg


def assert_bernstein_positive(
    name: str,
    expr: sp.Expr,
    bounded: tuple[sp.Symbol, ...],
    unbounded: tuple[sp.Symbol, ...],
    *,
    expected_coeffs: int,
    expected_terms: int,
    expected_min: int,
) -> None:
    numerator, _ = sp.together(expr).as_numer_denom()
    coeffs = [numerator]
    for var in bounded:
        next_coeffs: list[sp.Expr] = []
        for coeff in coeffs:
            next_coeffs.extend(bernstein_coeffs(coeff, var))
        coeffs = next_coeffs

    total_terms = 0
    min_coeff = None
    for coeff in coeffs:
        terms, this_min, neg = coeff_stats(coeff, unbounded)
        assert neg == 0, (name, terms, this_min, neg)
        assert this_min >= 0, (name, terms, this_min)
        total_terms += terms
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)

    assert len(coeffs) == expected_coeffs, (name, len(coeffs), expected_coeffs)
    assert total_terms == expected_terms, (name, total_terms, expected_terms)
    assert min_coeff == expected_min, (name, min_coeff, expected_min)


def assert_x_ge_v_side() -> None:
    V, H, R, Q, G = sp.symbols("V H R Q G", nonnegative=True)
    X = V + H
    x = 1 + X
    v = 1 + V
    m = x * (1 + v) + v
    s_max = sp.factor(x * v + v - 2)
    assert s_max == V**2 + H * V + 3 * V + H

    s = R * s_max
    b = x + s
    f = sp.cancel((m - 1) / (b + 1))
    S = sp.factor(b - v)

    D_seg = Q * S
    E_seg = b - 1 - D_seg
    assert_bernstein_positive(
        "x_ge_v_segment",
        phi_expr(b, 1 + D_seg, 1 + E_seg, f, x, v),
        (R, Q),
        (V, H),
        expected_coeffs=27,
        expected_terms=3488,
        expected_min=8,
    )

    D_ray = S + G
    E_ray = V
    assert_bernstein_positive(
        "x_ge_v_ray",
        phi_expr(b, 1 + D_ray, 1 + E_ray, f, x, v),
        (R,),
        (V, H, G),
        expected_coeffs=8,
        expected_terms=2732,
        expected_min=2,
    )


def assert_v_ge_x_side() -> None:
    X, H, R, Q, G = sp.symbols("X H R Q G", nonnegative=True)
    V = X + H
    x = 1 + X
    v = 1 + V
    m = x * (1 + v) + v
    s_max = sp.factor(x * v + v - 2)
    assert s_max == H * X + 2 * H + X**2 + 3 * X

    # Low chamber: 0<=s<=H, so v>=b.  The lower boundary is E=V.
    s_low = R * H
    b_low = x + s_low
    f_low = sp.cancel((m - 1) / (b_low + 1))
    assert_bernstein_positive(
        "v_ge_x_low",
        phi_expr(b_low, 1 + G, 1 + V, f_low, x, v),
        (R,),
        (X, H, G),
        expected_coeffs=7,
        expected_terms=1457,
        expected_min=2,
    )

    # High chamber: H<=s<=s_max, so b>=v.
    high_width = sp.factor(s_max - H)
    assert high_width == H * X + H + X**2 + 3 * X
    s_high = H + R * high_width
    b_high = x + s_high
    f_high = sp.cancel((m - 1) / (b_high + 1))
    S = sp.factor(b_high - v)

    D_seg = Q * S
    E_seg = b_high - 1 - D_seg
    assert_bernstein_positive(
        "v_ge_x_high_segment",
        phi_expr(b_high, 1 + D_seg, 1 + E_seg, f_high, x, v),
        (R, Q),
        (X, H),
        expected_coeffs=24,
        expected_terms=3277,
        expected_min=8,
    )

    D_ray = S + G
    E_ray = V
    assert_bernstein_positive(
        "v_ge_x_high_ray",
        phi_expr(b_high, 1 + D_ray, 1 + E_ray, f_high, x, v),
        (R,),
        (X, H, G),
        expected_coeffs=8,
        expected_terms=2732,
        expected_min=2,
    )


def main() -> None:
    assert_x_ge_v_side()
    assert_v_ge_x_side()
    print("PASS y=1,u=1,s4,a=c=1 family is Bernstein-positive")


if __name__ == "__main__":
    main()
