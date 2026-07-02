"""Exact closure of one-step drop faces from the all-tight y=1 support.

The lowest support-face probe found that dropping any single active equation
from the all-tight y=1,u=1,s4 support flows back to the all-tight curve.  This
file records the exact algebra.

For drops of b1,d1,f1, all seven capacity/row slacks remain tight, hence the
face is contained in the already closed seven-tight y=1 manifold.  For drops of
s1,s2,s5,s6,s7, the remaining equations force the central f=b=d=1 curve.  The
only genuine broader face is drop:s3:

    b=d=f=u=y=1, c=e=v=t, 1 <= x <= t,
    a = (x(t+1)-1)/t.

We prove Phi >= 0 on this face by x=1+r(t-1), Bernstein in r.  The final
Bernstein coefficient is exactly the central Sturm polynomial from the
seven-tight certificate.
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


def check_forced_central_drops() -> None:
    a, c, e, x, v = sp.symbols("a c e x v")
    b = d = f = u = sp.Integer(1)
    m = x * u + x * v + v
    Y = a * c + b * f + c * f
    sl = {
        "s1": e - v,
        "s2": d + e - u - v,
        "s3": b + c - x - 1,
        "s4": Y - m,
        "s5": a * e + b * f + c * f - m,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
    }
    central_generators = {"c - v", "e - v", "-v + x"}
    for missing in ("s1", "s2", "s5", "s6", "s7"):
        eqs = [sl[name] for name in sl if name != missing]
        G = sp.groebner(eqs, a, c, e, x, v, order="lex")
        basis = {str(poly.as_expr()) for poly in G.polys}
        assert central_generators <= basis, (missing, basis)
    print("DROP all-tight s1/s2/s5/s6/s7: remaining equations force central curve")


def check_drop_s3_positivity() -> None:
    T, r = sp.symbols("T r", nonnegative=True)
    t = 1 + T
    x = 1 + r * T
    a = (x * (t + 1) - 1) / t
    b = d = f = u = sp.Integer(1)
    c = e = v = t
    Phi = phi_expr(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs({T: 1, r: sp.Rational(1, 2)}) > 0

    bcoeffs = bernstein_coeffs(num, r)
    # All but the endpoint coefficient are coefficient-positive in T.
    for coeff in bcoeffs[:-1]:
        assert coeffs_nonnegative(coeff, (T,), strict=True)

    # Endpoint r=1 is the central seven-tight f=1 polynomial in t=T+1.
    endpoint = sp.factor(bcoeffs[-1] / (T + 1))
    assert sp.factor(endpoint - (20*T**7 + 122*T**6 + 146*T**5 - 324*T**4 - 557*T**3 + 440*T**2 + 1000*T + 375)) == 0
    assert endpoint.subs(T, 0) == 375
    assert sp.polys.polytools.count_roots(endpoint, 0, sp.oo) == 0
    print("DROP all-tight s3: Bernstein in x plus central Sturm endpoint proves Phi>=0")


def main() -> None:
    check_forced_central_drops()
    check_drop_s3_positivity()
    print("PASS y=1 all-tight one-step drop faces are closed")


if __name__ == "__main__":
    main()

