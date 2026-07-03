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
    assert den_coeffs and all(c > 0 for c in den_coeffs), (min(den_coeffs), sum(1 for c in den_coeffs if c <= 0))
    poly = sp.Poly(numerator, *variables)
    coeffs = [sp.Integer(c) for c in poly.coeffs()]
    neg = sum(1 for c in coeffs if c < 0)
    return len(coeffs), min(coeffs), neg


def run_one(name: str, expr: sp.Expr, bounded: tuple[sp.Symbol, ...], unbounded: tuple[sp.Symbol, ...]) -> None:
    numerator, denominator = sp.together(expr).as_numer_denom()
    print(name, "den_terms", coeff_stats(denominator, (*bounded, *unbounded))[:2], flush=True)
    coeffs = [numerator]
    for var in bounded:
        next_coeffs = []
        for coeff in coeffs:
            next_coeffs.extend(bernstein_coeffs(coeff, var))
        coeffs = next_coeffs
        print(name, "after", var, len(coeffs), flush=True)

    total = 0
    min_coeff = None
    bad = []
    for idx, coeff in enumerate(coeffs):
        terms, this_min, neg = coeff_stats(coeff, unbounded)
        total += terms
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)
        if neg or this_min < 0:
            bad.append((idx, terms, this_min, neg))
    print(name, "coeffs", len(coeffs), "terms", total, "min", min_coeff, "bad", bad[:10], flush=True)
    assert not bad


def main() -> None:
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

    # Segment: D+E=b-1, with E from b-1 down to V.
    D_seg = Q * S
    E_seg = b - 1 - D_seg
    phi_seg = phi_expr(b, 1 + D_seg, 1 + E_seg, f, x, v)
    run_one("segment", phi_seg, (R, Q), (V, H))

    # Ray: E=V, D=b-v+G.
    D_ray = S + G
    E_ray = V
    phi_ray = phi_expr(b, 1 + D_ray, 1 + E_ray, f, x, v)
    run_one("ray", phi_ray, (R,), (V, H, G))


if __name__ == "__main__":
    main()
