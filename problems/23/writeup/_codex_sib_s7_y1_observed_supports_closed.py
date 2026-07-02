"""Compact exact closure gate for observed y=1 SIB-S7 support families.

This is not the missing coverage theorem.  It is a single reference artifact
for the families that the active-set scans and exact support reductions have
already isolated.  The remaining coverage task is to prove that no other FJ
support can occur.
"""

from __future__ import annotations

import sympy as sp


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    P = sp.Poly(sp.expand(poly), var)
    degree = P.degree()
    coeff = [P.coeff_monomial(var**i) for i in range(degree + 1)]
    return [
        sp.factor(sum(coeff[i] * sp.Rational(sp.binomial(k, i), sp.binomial(degree, i)) for i in range(k + 1)))
        for k in range(degree + 1)
    ]


def coeffs_positive(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef > 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v", positive=True)
y = sp.Integer(1)
m = x * u + x * v + v
N = a + b + c + d + e + f + x + y + u + v
Y = a * c + b * f + c * f
Z = e * Y + d * f * (b + c)
A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + v * B / (e * Y) - (a + b + c + d + e + f)))


def numerator_on(subs: dict[sp.Symbol, sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
    num, den = sp.together(Phi.subs(subs)).as_numer_denom()
    return sp.factor(num), sp.factor(den)


def check_central_all_tight() -> None:
    T = sp.symbols("T", nonnegative=True)
    t = 1 + T
    subs = {a: t + 1 - 1 / t, b: 1, c: t, d: 1, e: t, f: 1, x: t, u: 1, v: t}
    num, den = numerator_on(subs)
    assert den.subs(T, 0) > 0

    tt = sp.symbols("tt", positive=True)
    P0 = 20 * tt**7 - 18 * tt**6 - 166 * tt**5 + 76 * tt**4 + 459 * tt**3 + 117 * tt**2 - 117 * tt + 4
    shifted = sp.expand(P0.subs(tt, 1 + T))
    assert sp.factor(num - (T + 1) * shifted) == 0
    assert P0.subs(tt, 1) == 375
    assert sp.polys.polytools.count_roots(P0, 1, sp.oo) == 0


def check_high_a() -> None:
    T = sp.symbols("T", nonnegative=True)
    t = 1 + T
    num, den = numerator_on({a: 1, b: 1, c: t, d: 1, e: t, f: t, x: t, u: 1, v: t})
    assert den.subs(T, 0) > 0
    assert coeffs_positive(num, (T,))


def check_xq_a() -> None:
    X, r = sp.symbols("X r", nonnegative=True)
    xx = 2 + X
    cc = 1 + X + r
    subs = {
        x: xx,
        u: 1,
        v: 1 + X,
        f: 1,
        c: cc,
        e: cc,
        b: xx + 1 - cc,
        d: xx + 1 - cc,
        a: (xx * xx - 2) / cc,
    }
    num, den = numerator_on(subs)
    assert den.subs({X: 0, r: 0}) > 0
    for coeff in bernstein_coeffs(num, r):
        assert coeffs_nonnegative(coeff, (X,))
        assert coeff.subs(X, 0) > 0


def check_xq_b() -> None:
    X = sp.symbols("X", nonnegative=True)
    xx = 2 + X
    subs = {x: xx, u: 1, v: 1 + X, a: 3 + X, b: 2, c: 1 + X, d: 1, e: 1 + X, f: 1}
    num, den = numerator_on(subs)
    assert den.subs(X, 0) > 0
    assert coeffs_positive(num, (X,))


def check_u1_s7_high() -> None:
    B0 = sp.symbols("B0", nonnegative=True)
    subs = {a: 1, b: 1 + B0, c: 1, d: 1, e: 1, f: 1, x: 1, u: 1, v: 1}
    num, den = numerator_on(subs)
    assert den.subs(B0, 0) > 0
    assert coeffs_positive(num, (B0,))


def check_xq_s5_high() -> None:
    X = sp.symbols("X", nonnegative=True)
    xx = 2 + X
    subs = {
        x: xx,
        u: 1,
        v: 1 + X,
        a: 1,
        b: 2,
        c: 1 + X,
        d: 2,
        e: 1 + X,
        f: xx * xx / (xx + 1),
    }
    num, den = numerator_on(subs)
    assert den.subs(X, 0) > 0
    assert coeffs_positive(num, (X,))


def main() -> None:
    check_central_all_tight()
    check_high_a()
    check_xq_a()
    check_xq_b()
    check_u1_s7_high()
    check_xq_s5_high()
    print("PASS y=1 observed support families are exactly positive/closed")


if __name__ == "__main__":
    main()
