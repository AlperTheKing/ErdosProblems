"""Exact positivity for the second broad y=1,u=1,s4,a=1 chamber.

Family:

    y=1, u=1, s4=0, a=1.

This file certifies the chamber

    V >= X,  q <= V <= t,

where

    x = 1+X,  v = 1+V,  V = X+H,
    q = c-1 = S V,                 0 <= S <= 1,
    t = b+c-2 = V + R*(M3-q-V),    0 <= R <= 1,
    M3 = x(1+v)+v-3.

Set W=t-V.  The feasible d/e region splits into:

1. Segment: e=1+V+U*W, d=1+W-U*W+G, 0<=U<=1, G>=0.
   Boundary G=0 is positive; dPhi/dG is positive.
2. Ray: e=1+t+E, d=1+D.  The hand-cleared numerator is positive.

The selected capacity equation s4=0 gives

    f = (x(1+v)+v-c)/(b+c).

All checks are exact: Bernstein in bounded variables and monomial in the
unbounded nonnegative variables.
"""

from __future__ import annotations

from math import comb

import sympy as sp


X, H, R, S, U, G, D, E = sp.symbols("X H R S U G D E", nonnegative=True)


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(poly, var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    return [
        sp.factor(sum(
            power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i))
            for i in range(k + 1)
        ))
        for k in range(degree + 1)
    ]


def common_quantities():
    V = X + H
    x = 1 + X
    v = 1 + V
    m = sp.expand(x * (1 + v) + v)
    M3 = sp.expand(m - 3)
    q = S * V
    width = sp.expand(M3 - q - V)
    t = V + R * width
    W = t - V
    h = 2 + t
    c = 1 + q
    C = m - c

    assert sp.factor(V - X - H) == 0
    assert sp.factor(M3 - 2 * V - X * (V + 2)) == 0
    assert sp.factor(width - (M3 - q - V)) == 0
    assert sp.factor(width.subs(S, 1) - (M3 - 2 * V)) == 0

    return V, x, v, m, q, t, W, h, c, C


def phi_from_de(d: sp.Expr, e: sp.Expr) -> sp.Expr:
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    f = C / h
    sum_core = 3 + t + d + e + f
    n = sum_core + x + 2 + v
    z = e * m + d * C
    a_term = m + e + (d + e) * (h + f)
    b_term = m + e * (1 + h + f)
    p_term = m - v
    return 2 * (n * n - 25 * m) - 75 * (
        p_term * a_term / z + v * b_term / (e * m) - sum_core
    )


def hand_cleared_numerator(d: sp.Expr, e: sp.Expr) -> sp.Expr:
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    f = C / h
    sum_core = 3 + t + d + e + f
    n = sum_core + x + 2 + v
    z = e * m + d * C
    a_term = m + e + (d + e) * (h + f)
    b_term = m + e * (1 + h + f)
    p_term = m - v
    base = 2 * (n * n - 25 * m) + 75 * sum_core
    return sp.together(base * z * e * m - 75 * p_term * a_term * e * m - 75 * v * b_term * z).as_numer_denom()[0]


def assert_bernstein_positive(
    name: str,
    expr: sp.Expr,
    bounded: tuple[sp.Symbol, ...],
    unbounded: tuple[sp.Symbol, ...],
    *,
    expected_coeffs: int,
    expected_terms: int,
    expected_min: sp.Expr,
) -> None:
    coeffs = [expr]
    for var in bounded:
        next_coeffs: list[sp.Expr] = []
        for coeff in coeffs:
            next_coeffs.extend(bernstein_coeffs(coeff, var))
        coeffs = next_coeffs

    total_terms = 0
    min_coeff = None
    for coeff in coeffs:
        poly = sp.Poly(sp.factor(coeff), *unbounded)
        raw_coeffs = [sp.Integer(c) if c.is_Integer else c for c in poly.coeffs()]
        assert all(c >= 0 for c in raw_coeffs), name
        total_terms += len(raw_coeffs)
        this_min = min(raw_coeffs)
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)

    assert len(coeffs) == expected_coeffs, (name, len(coeffs), expected_coeffs)
    assert total_terms == expected_terms, (name, total_terms, expected_terms)
    assert min_coeff == expected_min, (name, min_coeff, expected_min)


def main() -> None:
    V, x, v, m, q, t, W, h, c, C = common_quantities()

    # Segment boundary G=0: e=1+V+U*W, d=1+W-U*W.
    e_seg = 1 + V + U * W
    d_seg = 1 + W - U * W
    assert_bernstein_positive(
        "a_s4_mid_segment_boundary",
        hand_cleared_numerator(d_seg, e_seg),
        (R, S, U),
        (X, H),
        expected_coeffs=116,
        expected_terms=11128,
        expected_min=sp.Rational(4, 3),
    )

    # Segment monotonicity in the extra d-slack G.
    print("CHECK a_s4_mid_segment_dG", flush=True)
    phi_seg = phi_from_de(d_seg + G, e_seg)
    num_dg = sp.together(sp.diff(phi_seg, G)).as_numer_denom()[0]
    assert_bernstein_positive(
        "a_s4_mid_segment_dG",
        num_dg,
        (R, S, U),
        (X, H, G),
        expected_coeffs=71,
        expected_terms=11532,
        expected_min=sp.Integer(1),
    )

    # Ray: e=1+t+E, d=1+D.
    e_ray = 1 + t + E
    d_ray = 1 + D
    assert_bernstein_positive(
        "a_s4_mid_ray_full",
        hand_cleared_numerator(d_ray, e_ray),
        (R, S),
        (X, H, D, E),
        expected_coeffs=40,
        expected_terms=30178,
        expected_min=sp.Rational(1, 10),
    )

    print("PASS y=1,u=1,s4,a=1 V>=X,q<=V<=t chamber is Bernstein-positive")


if __name__ == "__main__":
    main()