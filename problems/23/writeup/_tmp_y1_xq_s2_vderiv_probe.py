from __future__ import annotations

import sympy as sp


def coeffs_nonneg(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]):
    P = sp.Poly(sp.expand(expr), *vars_)
    vals = [coef for _mon, coef in P.terms()]
    return all(coef >= 0 for coef in vals), len(vals), P.total_degree()


def main() -> None:
    A, C, D, H, F, R = sp.symbols("A C D H F R", nonnegative=True)
    a = 1 + A
    c = 1 + C
    d = 1 + D
    e = c + H
    f = 1 + F
    # s2=0: q=d+e.  Feasible s3 is b+c-q-1=R.
    q = d + e
    b = q + 1 - c + R
    S = a + b + c + d + e + f
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    Aexpr = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Bexpr = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    caps = {
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    for name, M in caps.items():
        v = sp.symbols("v", positive=True)
        x = (M - v) / q
        N = S + 1 + x + q
        Phi = sp.factor(2 * (N * N - 25 * M) - 75 * (x * q * Aexpr / Z + v * Bexpr / (e * Y) - S))
        dPhi = sp.diff(Phi, v)
        v_xq = M - q * q
        num, den = sp.together(dPhi.subs(v, v_xq)).as_numer_denom()
        ok, terms, deg = coeffs_nonneg(num, (A, C, D, H, F, R))
        okneg, _terms2, _deg2 = coeffs_nonneg(-num, (A, C, D, H, F, R))
        print(name, "v-deriv-at-xq terms", terms, "deg", deg, "pos", ok, "neg", okneg)
        print("value_at_origin", num.subs({A: 0, C: 0, D: 0, H: 0, F: 0, R: 0}))
        print("den_at_origin", den.subs({A: 0, C: 0, D: 0, H: 0, F: 0, R: 0}))


if __name__ == "__main__":
    main()
