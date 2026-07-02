from __future__ import annotations

import sympy as sp


def coeffs_nonneg(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]):
    try:
        P = sp.Poly(sp.expand(expr), *vars_)
    except Exception as exc:  # pragma: no cover
        return False, str(exc)
    vals = [coef for _mon, coef in P.terms()]
    return all(coef >= 0 for coef in vals), (len(vals), P.total_degree())


def main() -> None:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    S = a + b + c + d + e + f
    x = b + c - 1
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    A0, B0, C0, D0, E0, F0 = sp.symbols("A0 B0 C0 D0 E0 F0")
    shift = {a: 1 + A0, b: 1 + B0, c: 1 + C0, d: 1 + D0, e: 1 + E0, f: 1 + F0}
    vars_ = (A0, B0, C0, D0, E0, F0)

    for cap, M in caps.items():
        v = M - x * x
        N = S + 1 + 2 * x
        Phi = sp.factor(2 * (N * N - 25 * M) - 75 * (x * x * A / Z + v * B / (e * Y) - S))
        for var in (a, d, f):
            num, _den = sp.together(sp.diff(Phi, var)).as_numer_denom()
            ok, info = coeffs_nonneg(num.subs(shift), vars_)
            okneg, _ = coeffs_nonneg((-num).subs(shift), vars_)
            print(cap, "d", var, "info", info, "pos", ok, "neg", okneg)


if __name__ == "__main__":
    main()
