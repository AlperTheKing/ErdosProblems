"""Exact positivity for the y=1,u=1,s4,a=1 chamber V>=X,q>=V.

Family:

    y=1, u=1, s4=0, a=1.

This certifies the remaining chamber

    V >= X,  V <= q <= t,

where

    x = 1+X,  v = 1+V,  V = X+H,
    J = M3-2V = X(V+2),
    q = c-1 = V + S*J/2,          0 <= S <= 1,
    t = b+c-2 = q + R*(1-S)*J,    0 <= R <= 1.

The proof keeps J symbolic through Bernstein conversion and then substitutes
J=X(X+H+2) coefficientwise.  With W=t-q, the feasible d/e region is:

1. Segment: e=1+q+U*W, d=1+W-U*W+G, 0<=U<=1, G>=0.
   The boundary G=0 is positive.  The d-slack derivative is certified by
   the four coefficients of its cubic in G.
2. Ray: e=1+t+E, d=1+D.
"""

from __future__ import annotations

from math import comb

import sympy as sp


X, H, J, R, S, U, G, D, E = sp.symbols("X H J R S U G D E", nonnegative=True)
J_TRUE = X * (X + H + 2)


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(poly, var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    return [
        sum(
            power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i))
            for i in range(k + 1)
        )
        for k in range(degree + 1)
    ]


def common_quantities():
    V = X + H
    x = 1 + X
    v = 1 + V
    m = 3 + 2 * V + J
    q = V + S * J / 2
    t_width = (1 - S) * J
    t = q + R * t_width
    W = t - q
    h = 2 + t
    c = 1 + q
    C = m - c

    assert sp.factor(V - X - H) == 0
    assert sp.factor(t - q - R * (1 - S) * J) == 0
    assert sp.factor(t + q - (3 + 2 * V + J - 3) - (R - 1) * t_width) == 0

    return V, x, v, m, q, t, W, h, c, C


def hand_cleared_numerator(d: sp.Expr, e: sp.Expr) -> sp.Expr:
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    z = e * m + d * C
    p_term = m - v

    sc_num = h * (3 + t + d + e) + C
    n_num = sc_num + h * (x + 2 + v)
    a_num = h * (m + e) + (d + e) * (h * h + C)
    b_num = h * m + e * (h * (1 + h) + C)
    base_num = 2 * n_num * n_num - 50 * m * h * h + 75 * sc_num * h
    return sp.expand(
        base_num * z * e * m
        - 75 * p_term * a_num * h * e * m
        - 75 * v * b_num * h * z
    )


def derivative_coeffs_in_d(e: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    em = e * m
    p_term = m - v

    sc0 = h * (3 + t + e) + C
    n0 = sc0 + h * (x + 2 + v)
    base2 = 2 * h * h
    base1 = 4 * h * n0 + 75 * h * h
    base0 = 2 * n0 * n0 - 50 * m * h * h + 75 * h * sc0

    anum1 = h * h + C
    anum0 = h * (m + e) + e * (h * h + C)
    b_num = h * m + e * (h * (1 + h) + C)

    # N(d) = a3*d^3 + a2*d^2 + a1*d + a0 is the cleared numerator.
    a3 = base2 * C * em
    a2 = (base2 * em + base1 * C) * em
    a1 = (base1 * em + base0 * C) * em - 75 * p_term * anum1 * h * em - 75 * v * b_num * h * C
    a0 = base0 * em * em - 75 * p_term * anum0 * h * em - 75 * v * b_num * h * em

    # For Phi=N/z, z=em+C*d, the d-derivative numerator is N'(d)*z - N(d)*C.
    m0 = em * a1 - C * a0
    m1 = 2 * em * a2
    m2 = 3 * em * a3 + C * a2
    m3 = 2 * C * a3
    return m0, m1, m2, m3


def derivative_coeffs_in_g(d0: sp.Expr, e: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    m0, m1, m2, m3 = derivative_coeffs_in_d(e)
    g0 = m0 + m1 * d0 + m2 * d0 * d0 + m3 * d0 * d0 * d0
    g1 = m1 + 2 * m2 * d0 + 3 * m3 * d0 * d0
    g2 = m2 + 3 * m3 * d0
    g3 = m3
    return g0, g1, g2, g3


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
        true_coeff = coeff.subs(J, J_TRUE)
        poly = sp.Poly(true_coeff, *unbounded)
        raw_coeffs = [sp.Integer(c) if c.is_Integer else c for c in poly.coeffs()]
        negatives = [raw for raw in raw_coeffs if raw < 0]
        assert not negatives, (name, negatives[:5])
        total_terms += len(raw_coeffs)
        this_min = min(raw_coeffs)
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)

    assert len(coeffs) == expected_coeffs, (name, len(coeffs), expected_coeffs)
    assert total_terms == expected_terms, (name, total_terms, expected_terms)
    assert min_coeff == expected_min, (name, min_coeff, expected_min)
    print(f"{name}: coeffs={len(coeffs)} terms={total_terms} min={min_coeff}", flush=True)


def main() -> None:
    print("START y=1,u=1,s4,a=1 V>=X,q>=V chamber", flush=True)
    V, x, v, m, q, t, W, h, c, C = common_quantities()

    e_seg = 1 + q + U * W
    d_seg_boundary = 1 + W - U * W
    assert_bernstein_positive(
        "a_s4_vge_x_qge_v_segment_boundary",
        hand_cleared_numerator(d_seg_boundary, e_seg),
        (R, S, U),
        (X, H),
        expected_coeffs=127,
        expected_terms=13849,
        expected_min=sp.Rational(1, 105),
    )

    e_ray = 1 + t + E
    d_ray = 1 + D
    assert_bernstein_positive(
        "a_s4_vge_x_qge_v_ray_full",
        hand_cleared_numerator(d_ray, e_ray),
        (R, S),
        (X, H, D, E),
        expected_coeffs=49,
        expected_terms=40089,
        expected_min=sp.Rational(1, 80),
    )

    d0 = 1 + W - U * W
    dg_coeffs = derivative_coeffs_in_g(d0, e_seg)
    for name, coeff, expected_coeffs, expected_terms, expected_min in [
        ("a_s4_vge_x_qge_v_segment_dG_G0", dg_coeffs[0], 166, 22850, sp.Rational(1, 210)),
        ("a_s4_vge_x_qge_v_segment_dG_G1", dg_coeffs[1], 121, 13527, sp.Rational(1, 35)),
        ("a_s4_vge_x_qge_v_segment_dG_G2", dg_coeffs[2], 74, 6528, sp.Rational(1, 15)),
        ("a_s4_vge_x_qge_v_segment_dG_G3", dg_coeffs[3], 39, 2625, sp.Rational(1, 20)),
    ]:
        assert_bernstein_positive(
            name,
            coeff,
            (R, S, U),
            (X, H),
            expected_coeffs=expected_coeffs,
            expected_terms=expected_terms,
            expected_min=expected_min,
        )

    print("PASS y=1,u=1,s4,a=1 V>=X,q>=V chamber is Bernstein-positive")


if __name__ == "__main__":
    main()