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
        out.append(sp.cancel(coeff))
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


def main() -> None:
    V, H, R, Q = sp.symbols("V H R Q", nonnegative=True)
    X = V + H
    x = 1 + X
    v = 1 + V
    U = V + X / (X + 2)
    F = R * U
    f = 1 + F
    b = sp.cancel((x * (1 + v) + v - 1 - f) / f)
    S = sp.cancel(b - 1 - V)
    D = Q * S
    E = b - 1 - D

    phi_seg = phi_expr(b, 1 + D, 1 + E, f, x, v)
    num_seg, _ = sp.together(phi_seg).as_numer_denom()
    r_coeffs = bernstein_coeffs(num_seg, R)
    print("R_count", len(r_coeffs), flush=True)

    total_terms = 0
    final_count = 0
    min_coeff = None
    bad = []
    for ridx, r_coeff in enumerate(r_coeffs):
        q_coeffs = bernstein_coeffs(r_coeff, Q)
        print("Q_count", ridx, len(q_coeffs), flush=True)
        final_count += len(q_coeffs)
        for qidx, q_coeff in enumerate(q_coeffs):
            terms, this_min, neg = coeff_stats(q_coeff, (V, H))
            total_terms += terms
            min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)
            if neg or this_min < 0:
                bad.append((ridx, qidx, terms, this_min, neg))
                print("BAD", bad[-1], flush=True)
                raise SystemExit(1)

    print("PASS", final_count, total_terms, min_coeff, bad)


if __name__ == "__main__":
    main()
