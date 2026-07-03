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
    p = sp.Poly(sp.expand(poly), var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    out = []
    for k in range(degree + 1):
        coeff = 0
        for i in range(k + 1):
            coeff += power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i))
        out.append(sp.cancel(coeff))
    return out


def coeff_stats(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> tuple[int, sp.Integer, int]:
    poly = sp.Poly(sp.expand(expr), *variables)
    coeffs = [sp.Integer(c) for c in poly.coeffs()]
    if not coeffs:
        return (0, sp.Integer(0), 0)
    neg = sum(1 for c in coeffs if c < 0)
    return len(coeffs), min(coeffs), neg


def assert_positive_coeffs(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> tuple[int, sp.Integer]:
    terms, min_coeff, neg = coeff_stats(expr, variables)
    assert neg == 0, (terms, min_coeff, neg)
    assert min_coeff >= 0, (terms, min_coeff)
    return terms, min_coeff


def main() -> None:
    V, H, R, G, Q = sp.symbols("V H R G Q", nonnegative=True)
    X = V + H
    x = 1 + X
    v = 1 + V
    U = V + X / (X + 2)
    F = R * U
    f = 1 + F
    b = sp.cancel((x * (1 + v) + v - 1 - f) / f)
    S = sp.cancel(b - 1 - V)

    print("ray")
    phi_ray = phi_expr(b, 1 + S + G, 1 + V, f, x, v)
    num_ray, den_ray = sp.together(phi_ray).as_numer_denom()
    den_ray_stats = assert_positive_coeffs(den_ray, (R, V, H, G))
    ray_total = 0
    ray_min = None
    ray_bad = []
    for idx, coeff in enumerate(bernstein_coeffs(num_ray, R)):
        terms, min_coeff, neg = coeff_stats(coeff, (V, H, G))
        ray_total += terms
        ray_min = min_coeff if ray_min is None else min(ray_min, min_coeff)
        if neg or min_coeff < 0:
            ray_bad.append((idx, terms, min_coeff, neg))
    print("ray_den", den_ray_stats)
    print("ray_coeffs", len(bernstein_coeffs(num_ray, R)), ray_total, ray_min, ray_bad[:5])

    print("segment")
    D = Q * S
    E = b - 1 - D
    phi_seg = phi_expr(b, 1 + D, 1 + E, f, x, v)
    num_seg, den_seg = sp.together(phi_seg).as_numer_denom()
    seg_total = 0
    seg_min = None
    seg_bad = []
    r_coeffs = bernstein_coeffs(num_seg, R)
    print("segment_R_count", len(r_coeffs))
    for ridx, r_coeff in enumerate(r_coeffs):
        q_coeffs = bernstein_coeffs(r_coeff, Q)
        print("segment_Q_count", ridx, len(q_coeffs), flush=True)
        for qidx, q_coeff in enumerate(q_coeffs):
            terms, min_coeff, neg = coeff_stats(q_coeff, (V, H))
            seg_total += terms
            seg_min = min_coeff if seg_min is None else min(seg_min, min_coeff)
            if neg or min_coeff < 0:
                seg_bad.append((ridx, qidx, terms, min_coeff, neg))
    print("segment_coeffs", "final", "see_Q_counts", seg_total, seg_min, seg_bad[:10])


if __name__ == "__main__":
    main()

