from __future__ import annotations

import sympy as sp


def coeffs_nonneg(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]):
    P = sp.Poly(sp.expand(expr), *vars_)
    vals = [coef for _mon, coef in P.terms()]
    return all(coef >= 0 for coef in vals), len(vals), P.total_degree()


def main() -> None:
    A, C, D, H, F = sp.symbols("A C D H F", nonnegative=True)
    a = 1 + A
    c = 1 + C
    d = 1 + D
    h = H
    e = c + h
    f = 1 + F
    x = d + e
    b = d + h + 1
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
        v = M - x * x
        N = S + 1 + 2 * x
        Phi = sp.factor(2 * (N * N - 25 * M) - 75 * (x * x * Aexpr / Z + v * Bexpr / (e * Y) - S))
        num, den = sp.together(Phi).as_numer_denom()
        ok, terms, deg = coeffs_nonneg(num, (A, C, D, H, F))
        print(name, "Phi num terms", terms, "deg", deg, "coeff_nonneg", ok)
        print("num_at_origin", num.subs({A: 0, C: 0, D: 0, H: 0, F: 0}))
        print("den_at_origin", den.subs({A: 0, C: 0, D: 0, H: 0, F: 0}))


if __name__ == "__main__":
    main()
