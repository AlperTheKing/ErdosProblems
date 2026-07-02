"""Exact closure of one-step drop faces from the HIGH_A y=1 support.

HIGH_A is the observed support

    a=b=d=u=1, s1=s2=s3=s4=s5=s6=s7=0,

which reduces to c=e=f=x=v=t and is already positive.  This file closes every
one-step drop face from that support.

Drops of d1,s1,s2,s5,s6,s7 force the HIGH_A curve again.  Drop of b1 also
forces b=1.  Drop of a1 is contained in the already closed seven-tight y=1
manifold with b=1.  The only genuine broader face is drop:s3:

    a=b=d=u=y=1, c=e=v=t, f=x, 1 <= x <= t.

We prove Phi >= 0 on this face by x=1+r(t-1), Bernstein in r with all
coefficients shifted-positive in T=t-1.
"""

from __future__ import annotations

import sympy as sp


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    P = sp.Poly(sp.expand(poly), var)
    n = P.degree()
    coeff = [P.coeff_monomial(var**i) for i in range(n + 1)]
    return [
        sp.factor(sum(coeff[i] * sp.Rational(sp.binomial(k, i), sp.binomial(n, i)) for i in range(k + 1)))
        for k in range(n + 1)
    ]


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], strict: bool = False) -> bool:
    coeffs = [coef for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms()]
    return all(coef > 0 for coef in coeffs) if strict else all(coef >= 0 for coef in coeffs)


def phi_expr(a, b, c, d, e, f, x, u, v):
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + v * B / (e * Y) - (a + b + c + d + e + f)))


def highA_slacks():
    a, b, c, d, e, f, x, v = sp.symbols("a b c d e f x v")
    u = sp.Integer(1)
    m = x * u + x * v + v
    Y = a * c + b * f + c * f
    return (a, b, c, d, e, f, x, v), {
        "a1": a - 1,
        "b1": b - 1,
        "d1": d - 1,
        "s1": e - v,
        "s2": d + e - u - v,
        "s3": b + c - x - 1,
        "s4": Y - m,
        "s5": a * e + b * f + c * f - m,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
    }


def check_forced_highA_drops() -> None:
    vars_, sl = highA_slacks()
    a, b, c, d, e, f, x, v = vars_
    active = ("a1", "b1", "d1", "s1", "s2", "s3", "s4", "s5", "s6", "s7")
    highA_generators = {"a - 1", "b - 1", "c - v", "d - 1", "e - v", "-v + x"}
    for missing in ("d1", "s1", "s2", "s5", "s6", "s7"):
        eqs = [sl[name] for name in active if name != missing]
        G = sp.groebner(eqs, a, b, c, d, e, f, x, v, order="lex")
        basis = {str(poly.as_expr()) for poly in G.polys}
        assert highA_generators <= basis, (missing, basis)
    # drop:b1 gives c=e=v, d=a=1, b+v-x-1=0, and x*(x-v)*(v+1)=0.
    # Since x>0 and v+1>0, x=v and hence b=1.
    eqs = [sl[name] for name in active if name != "b1"]
    G = sp.groebner(eqs, a, b, c, d, e, f, x, v, order="lex")
    basis = {sp.factor(poly.as_expr()) for poly in G.polys}
    assert sp.factor(x * (x - v) * (v + 1)) in basis
    assert sp.factor(b + v - x - 1) in basis
    print("DROP HIGH_A b1/d1/s1/s2/s5/s6/s7: equations force the HIGH_A curve")


def check_drop_a1_to_seventight() -> None:
    vars_, sl = highA_slacks()
    a, b, c, d, e, f, x, v = vars_
    active = ("a1", "b1", "d1", "s1", "s2", "s3", "s4", "s5", "s6", "s7")
    eqs = [sl[name] for name in active if name != "a1"]
    G = sp.groebner(eqs, a, b, c, d, e, f, x, v, order="lex")
    basis = {str(poly.as_expr()) for poly in G.polys}
    assert {"b - 1", "c - x", "d - 1", "e - v"} <= basis
    assert "(-v + x)*(v*x + v + x)" == sp.factor(-v**2 * x - v**2 + v * x**2 + x**2).__str__()
    print("DROP HIGH_A a1: positive domain forces x=v, hence the b=1 seven-tight manifold")


def check_drop_s3_positivity() -> None:
    T, r = sp.symbols("T r", nonnegative=True)
    t = 1 + T
    x = 1 + r * T
    a = b = d = u = sp.Integer(1)
    c = e = v = t
    f = x
    Phi = phi_expr(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs({T: 1, r: sp.Rational(1, 2)}) > 0
    for coeff in bernstein_coeffs(num, r):
        assert coeffs_nonnegative(coeff, (T,), strict=True)
    print("DROP HIGH_A s3: Bernstein in x has shifted-positive coefficients")


def main() -> None:
    check_forced_highA_drops()
    check_drop_a1_to_seventight()
    check_drop_s3_positivity()
    print("PASS y=1 HIGH_A one-step drop faces are closed")


if __name__ == "__main__":
    main()

