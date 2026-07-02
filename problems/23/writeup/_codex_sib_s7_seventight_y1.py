"""Exact seven-tight y=1 manifold certificate for S7.

On the all-seven-tight S7 manifold with y=1, write

    d=b, e=c, u=b, v=c, x=b+c-1,
    a=((b+c)^2-b-f(b+c))/c,
    1 <= f <= b+c-1.

Step 1: parameterize f=1+r(b+c-2).  The numerator of dPhi/db has
nonnegative Bernstein coefficients in r after shifting b=1+B,c=1+C.
Hence Phi is increasing in b and the minimum occurs at b=1.

Step 2: with b=y=1, parameterize f=1+r(c-1).  The numerator of Phi has
Bernstein coefficients in r; coefficients 1..3 are shifted coefficient-positive
in C=c-1, and coefficient 0 is exactly the central f=1 curve, closed by Sturm.
"""

from __future__ import annotations

import sympy as sp


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    P = sp.Poly(sp.expand(poly), var)
    n = P.degree()
    coeff = [P.coeff_monomial(var**i) for i in range(n + 1)]
    out = []
    for k in range(n + 1):
        out.append(sum(coeff[i] * sp.Rational(sp.binomial(k, i), sp.binomial(n, i)) for i in range(k + 1)))
    return out


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], strict: bool = False) -> bool:
    coeffs = [coef for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms()]
    return all(coef > 0 for coef in coeffs) if strict else all(coef >= 0 for coef in coeffs)


def phi_on_seventight(b, c, f):
    y = sp.Integer(1)
    a = ((b + c) ** 2 - b * y - f * (b + c)) / c
    d = b
    e = c
    u = b
    v = c
    x = b + c - y
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    E = x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)
    return sp.factor(2 * (N * N - 25 * m) - 75 * E)


def main() -> None:
    # Step 1: dPhi/db >= 0 on y=1 seven-tight manifold.
    b0, c0, f0 = sp.symbols("b0 c0 f0", positive=True)
    Phi0 = phi_on_seventight(b0, c0, f0)
    dPhi_db = sp.diff(Phi0, b0)
    Bv, Cv, r = sp.symbols("B C r", nonnegative=True)
    b = 1 + Bv
    c = 1 + Cv
    f = 1 + r * (b + c - 2)
    num_db, den_db = sp.fraction(sp.factor(dPhi_db.subs({b0: b, c0: c, f0: f})))
    assert den_db.subs({Bv: 0, Cv: 0, r: 0}) > 0
    for coeff in bernstein_coeffs(num_db, r):
        assert coeffs_nonnegative(coeff, (Bv, Cv), strict=True)

    # Step 2: Phi >= 0 on b=y=1 seven-tight manifold.
    C, rr = sp.symbols("C rr", nonnegative=True)
    cc = 1 + C
    ff = 1 + rr * C
    Phi = phi_on_seventight(sp.Integer(1), cc, ff)
    num, den = sp.fraction(Phi)
    assert den.subs({C: 1, rr: sp.Rational(1, 2)}) > 0
    bcoeffs = bernstein_coeffs(num, rr)

    # Coefficient 0 is the central curve numerator after f=1, b=1.
    t = sp.symbols("t", positive=True)
    central = sp.factor(Phi.subs({rr: 0, C: t - 1}))
    P0 = 20 * t**7 - 18 * t**6 - 166 * t**5 + 76 * t**4 + 459 * t**3 + 117 * t**2 - 117 * t + 4
    expected = P0 / (t**2 * (t + 2) * (t**3 + 2 * t**2 + t + 1))
    assert sp.factor(central - expected) == 0
    assert P0.subs(t, 1) == 375
    assert sp.polys.polytools.count_roots(P0, 1, sp.oo) == 0

    # Higher Bernstein coefficients are coefficient-positive in C.
    for coeff in bcoeffs[1:]:
        assert coeffs_nonnegative(coeff, (C,), strict=True)

    print("PASS seven-tight y=1 manifold: b-monotone, then Bernstein/Sturm positive")


if __name__ == "__main__":
    main()
