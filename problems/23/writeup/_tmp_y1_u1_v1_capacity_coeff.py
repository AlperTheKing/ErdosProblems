from __future__ import annotations

import sympy as sp


def stats(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> tuple[int, int, sp.Rational | None]:
    poly = sp.Poly(sp.expand(expr), *vars_)
    pos = neg = 0
    mn = None
    for _m, c in poly.terms():
        pos += 1 if c > 0 else 0
        neg += 1 if c < 0 else 0
        mn = c if mn is None or c < mn else mn
    return pos, neg, mn


def main() -> None:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    y = sp.Integer(1)
    u = sp.Integer(1)
    v = sp.Integer(1)
    q = 1 + v
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
    vars_ = (a, b, c, d, e, f)
    shift = {z: 1 + z for z in vars_}
    for name, M in caps.items():
        x = (M - v) / q
        m = x * q + v
        N = S + x + y + u + v
        Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)
        num, _den = sp.together(Phi).as_numer_denom()
        print(name, stats(num.subs(shift), vars_))


if __name__ == "__main__":
    main()
