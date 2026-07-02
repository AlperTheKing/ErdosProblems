from __future__ import annotations

import sympy as sp


def coeffs_nonneg(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]):
    P = sp.Poly(sp.expand(expr), *vars_)
    vals = [coef for _mon, coef in P.terms()]
    return all(coef >= 0 for coef in vals), len(vals), P.total_degree()


def main() -> None:
    b, c, d, e, f, v = sp.symbols("b c d e f v", positive=True)
    x = d + e
    S0 = b + c + d + e + f
    Y0 = b * f + c * f
    caps_a = {
        "s6": (x * x + v - d * f - e * f) / c,
        "s7": (x * x + v - d * f - e * f) / e,
    }
    B0, C0, D0, E0, F0, V0 = sp.symbols("B0 C0 D0 E0 F0 V0", nonnegative=True)
    shift = {b: 1 + B0, c: 1 + C0, d: 1 + D0, e: 1 + E0, f: 1 + F0, v: 1 + V0}
    vars_ = (B0, C0, D0, E0, F0, V0)
    for name, a in caps_a.items():
        S = a + S0
        Y = a * c + Y0
        Z = e * Y + d * f * (b + c)
        Aexpr = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
        Bexpr = a * c + a * e + b * f + b * e + c * f + c * e + e * f
        m = x * x + v
        N = S + 1 + 2 * x
        Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * x * Aexpr / Z + v * Bexpr / (e * Y) - S))
        for der in (1, 2):
            num, den = sp.together(sp.diff(Phi, v, der)).as_numer_denom()
            ok, terms, deg = coeffs_nonneg(num.subs(shift), vars_)
            okneg, _, _ = coeffs_nonneg((-num).subs(shift), vars_)
            print(name, "d", der, "terms", terms, "deg", deg, "pos", ok, "neg", okneg)
            print(" origin", num.subs({b: 1, c: 1, d: 1, e: 1, f: 1, v: 1}), den.subs({b: 1, c: 1, d: 1, e: 1, f: 1, v: 1}))


if __name__ == "__main__":
    main()
