"""Exact positivity for the s3-branch critical survivor family.

The y=1,s3=0 capacity-critical scan found only a high positive family on the
s5 branch with active constraints

    b=f=1, v=1, u=1.

On this branch x=b+c-1=c and q=u+v=2.  The s5 capacity equality gives ae=c.
Use the domain parameters

    e=1+E,   c=e+C,   d=C+1+D,   a=c/e,

so E,C,D>=0 and the remaining capacity slacks are nonnegative.  In these
coordinates the cleared Phi numerator has nonnegative coefficients.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def main() -> None:
    E, C, D = sp.symbols("E C D", nonnegative=True)
    e = 1 + E
    c = e + C
    d = C + 1 + D
    a = c / e
    b = f = y = u = v = sp.Integer(1)
    x = c
    q = sp.Integer(2)

    S = a + b + c + d + e + f
    N = S + x + y + q
    m = x * q + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    M = a * e + b * f + c * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + v * B / (e * Y) - S)

    assert sp.factor(m - M) == 0
    assert sp.factor(Y - M - C * (C + E + 1) / (E + 1)) == 0
    assert sp.factor((a * c + d * f + e * f - m) - (C ** 2 + C * E + C + D * E + D) / (E + 1)) == 0
    assert sp.factor(a * e + d * f + e * f - m - D) == 0

    P = sp.together(Phi).as_numer_denom()[0]
    assert coeffs_nonnegative(P, (E, C, D))

    print("PASS y=1,s3 survivor family on s5 is positive")


if __name__ == "__main__":
    main()
