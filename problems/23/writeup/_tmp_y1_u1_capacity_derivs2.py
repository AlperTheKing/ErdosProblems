from __future__ import annotations

import sympy as sp


def coeff_sign(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> tuple[int, int, sp.Rational | None]:
    poly = sp.Poly(sp.expand(expr), *vars_)
    neg = 0
    pos = 0
    mn = None
    for _mon, coef in poly.terms():
        if coef < 0:
            neg += 1
        if coef > 0:
            pos += 1
        mn = coef if mn is None or coef < mn else mn
    return pos, neg, mn


def main() -> None:
    a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
    y = sp.Integer(1)
    u = sp.Integer(1)
    q = u + v
    S = a + b + c + d + e + f

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
    vars_ = (a, b, c, d, e, f, v)
    shifts = {z: 1 + z for z in vars_}

    for cap, M in caps.items():
        x = (M - v) / q
        m = x * q + v
        N = S + x + y + q
        Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)
        print("CAP", cap)
        pnum, _ = sp.together(Phi).as_numer_denom()
        print(" Phi shifted", coeff_sign(pnum.subs(shifts), vars_))
        for var in vars_:
            num, _den = sp.together(sp.diff(Phi, var)).as_numer_denom()
            pos, neg, mn = coeff_sign(num.subs(shifts), vars_)
            print(" d", var, "pos", pos, "neg", neg, "min", mn)
        print()


if __name__ == "__main__":
    main()
