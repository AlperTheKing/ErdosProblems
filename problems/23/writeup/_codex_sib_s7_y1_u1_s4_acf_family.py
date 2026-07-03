"""Exact positivity for the y=1,u=1,s4,a=c=f=1 family.

Set

    y=1, u=1, s4=0, a=c=f=1.

Then `s4=0` gives

    b = x(1+v)+v-2.

With `x=1+X`, `v=1+V`, this gives

    b = 1 + VX + 2V + 2X,

so `b>=x` and `b>=v`.  Write `d=1+D`, `e=1+E`.  The remaining
feasibility constraints reduce to

    E >= V,
    D + E >= B0 := b-1 = VX + 2V + 2X.

The cleared numerator of Phi is coefficientwise increasing in both `D`
and `E`.  Hence the minimum occurs on the segment

    E = V + R*(B0-V),  D = B0-E,  0<=R<=1.

On this segment the numerator is nonnegative in the Bernstein basis in R.
"""

from __future__ import annotations

import sympy as sp


def phi_expr(d: sp.Expr, e: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    a = c = f = u = y = sp.Integer(1)
    b = sp.factor(x * (1 + v) + v - 2)
    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))


def assert_coeff_positive(expr: sp.Expr, variables: tuple[sp.Symbol, ...], *, expected_terms: int, min_coeff: int) -> None:
    numerator, denominator = sp.together(expr).as_numer_denom()
    den_poly = sp.Poly(sp.expand(denominator), *variables)
    assert all(sp.Integer(coeff) > 0 for coeff in den_poly.coeffs())
    poly = sp.Poly(sp.expand(numerator), *variables)
    coeffs = [sp.Integer(coeff) for coeff in poly.coeffs()]
    assert len(coeffs) == expected_terms
    assert min(coeffs) == min_coeff
    assert all(coeff > 0 for coeff in coeffs)


def power_to_bernstein(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(sp.expand(poly), var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    out = []
    for k in range(degree + 1):
        coeff = 0
        for i in range(k + 1):
            coeff += power_coeffs[i] * sp.binomial(k, i) / sp.binomial(degree, i)
        out.append(sp.factor(coeff))
    return out


def main() -> None:
    X, V, D, E = sp.symbols("X V D E", nonnegative=True)
    x = 1 + X
    v = 1 + V
    b = sp.factor(x * (1 + v) + v - 2)
    assert b == V * X + 2 * V + 2 * X + 1
    assert sp.factor(b - x) == V * X + 2 * V + X
    assert sp.factor(b - v) == V * X + V + 2 * X

    # Monotonicity in the free feasibility variables d=1+D and e=1+E.
    phi = phi_expr(1 + D, 1 + E, x, v)
    assert_coeff_positive(sp.diff(phi, D), (X, V, D, E), expected_terms=132, min_coeff=4)
    assert_coeff_positive(sp.diff(phi, E), (X, V, D, E), expected_terms=396, min_coeff=4)

    # Boundary segment D+E=B0, E ranges from V to B0.
    R = sp.symbols("R", nonnegative=True)
    B0 = sp.factor(b - 1)
    E0 = V + R * (B0 - V)
    D0 = B0 - E0
    assert sp.factor(B0 - V) == V * X + V + 2 * X
    boundary_phi = phi_expr(1 + D0, 1 + E0, x, v)
    numerator, denominator = sp.together(boundary_phi).as_numer_denom()

    den_poly = sp.Poly(sp.expand(denominator), R, X, V)
    den_coeffs = [sp.Integer(coeff) for coeff in den_poly.coeffs()]
    assert len(den_coeffs) == 57
    assert min(den_coeffs) == 1
    assert all(coeff > 0 for coeff in den_coeffs)

    bcoeffs = power_to_bernstein(numerator, R)
    assert len(bcoeffs) == 3
    total_terms = 0
    mins = []
    for coeff in bcoeffs:
        poly = sp.Poly(sp.expand(coeff), X, V)
        coeffs = [sp.Integer(c) for c in poly.coeffs()]
        total_terms += len(coeffs)
        mins.append(min(coeffs))
        assert all(c > 0 for c in coeffs)
    assert total_terms == 140
    assert min(mins) == 4

    print("PASS y=1,u=1,s4,a=c=f=1 family is Bernstein-positive on the monotone boundary")


if __name__ == "__main__":
    main()
