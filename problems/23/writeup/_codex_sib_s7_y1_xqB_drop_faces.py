"""Exact closure of several one-step drop faces from XQ_B.

XQ_B is the x=q, y=1, u=1 support

    d=f=1, s1=s2=s3=s6=s7=0,

which reduces to

    a=x+1, b=2, c=e=v=x-1, d=f=u=1, x>=2.

This verifier closes:

* drops d1, s1, s2, and u1: the remaining equations force the same XQ_B
  family in the positive domain;
* drop s3: the remaining equations force a=x+1, c=e=v=x-1, d=f=u=1,
  while b>=2 remains free.  The whole b-ray is coefficient-positive.
"""

from __future__ import annotations

import sympy as sp


def coeffs_positive(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], label: str) -> None:
    poly = sp.Poly(sp.expand(expr), *vars_)
    bad = [coef for _mon, coef in poly.terms() if coef <= 0]
    assert not bad, (label, bad[:3], sp.factor(expr))


def phi_expr(a, b, c, d, e, f, x, u, v):
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (N**2 - 25 * m) - 75 * (x * (u + v) * A / Z + v * B / (e * Y) - (a + b + c + d + e + f))


def main() -> None:
    a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v")
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    slacks = {
        "d1": d - 1,
        "f1": f - 1,
        "s1": e - v,
        "s2": d + e - u - v,
        "s3": b + c - x - y,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
        "u1": u - 1,
        "xq": x - u - v,
    }
    active = ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1", "xq")

    easy = ("d1", "s1", "s2", "u1")
    for missing in easy:
        eqs = [slacks[name] for name in active if name != missing]
        G = sp.groebner(eqs, a, b, c, d, e, f, u, v, x, order="lex")
        basis = {sp.factor(poly.as_expr()) for poly in G.polys}
        assert sp.factor(a * c - x**2 + 1) in basis, missing
        assert sp.factor(-(x - 1) * (-a + x + 1)) in basis, missing
        assert sp.factor(-(x - 1) * (x + 1) * (-c + x - 1)) in basis, missing
        assert sp.factor(b + c - x - 1) in basis, missing
        assert sp.factor(d - 1) in basis, missing
        assert sp.factor(e - x + 1) in basis, missing
        assert sp.factor(f - 1) in basis, missing
        assert sp.factor(u - 1) in basis, missing
        assert sp.factor(v - x + 1) in basis, missing

    # Drop s3 leaves the b-ray; prove it positive.
    eqs = [slacks[name] for name in active if name != "s3"]
    G = sp.groebner(eqs, a, b, c, d, e, f, u, v, x, order="lex")
    basis = {sp.factor(poly.as_expr()) for poly in G.polys}
    assert sp.factor(a * c - x**2 + 1) in basis
    assert sp.factor(-(x - 1) * (-a + x + 1)) in basis
    assert sp.factor(-(x - 1) * (x + 1) * (-c + x - 1)) in basis
    assert sp.factor(d - 1) in basis
    assert sp.factor(e - x + 1) in basis
    assert sp.factor(f - 1) in basis
    assert sp.factor(u - 1) in basis
    assert sp.factor(v - x + 1) in basis

    X, B0 = sp.symbols("X B0")
    xx = X + 2
    aa = xx + 1
    bb = 2 + B0
    cc = ee = vv = xx - 1
    dd = ff = uu = sp.Integer(1)
    Phi = sp.factor(phi_expr(aa, bb, cc, dd, ee, ff, xx, uu, vv))
    num, den = sp.together(Phi).as_numer_denom()
    coeffs_positive(num, (X, B0), "drop:s3 numerator")
    coeffs_positive(den, (X, B0), "drop:s3 denominator")

    print("PASS y=1 XQ_B easy drops and drop:s3 face are closed")


if __name__ == "__main__":
    main()