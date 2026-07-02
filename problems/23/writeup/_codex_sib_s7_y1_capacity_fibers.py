"""Exact fiber reductions for all four y=1 SIB S7 capacity faces.

For j in {4,5,6,7}, let M_j be the right-hand side of capacity slack s_j.
On the face y=1,s_j=0:

    m = x*q + v = M_j,      q = (M_j-v)/x.

For fixed core variables a,b,c,d,e,f and fixed v, the non-quadratic terms in
Phi are constant along the fiber.  The only x-dependence is through

    N = S + 1 + x + (M_j-v)/x.

Thus a negative point on any y=1 capacity face reduces to one of:

    x=1, s2=0, s3=0, u=1, or the interior balanced fiber x=q.

This script checks the exact identities for all four capacity faces.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x, v = sp.symbols("a b c d e f x v", positive=True)
    y = sp.Integer(1)
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

    for name, Mj in caps.items():
        R = Mj - v
        q = R / x
        u = q - v
        m = x * q + v
        N = S + y + x + q
        Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S))

        assert sp.factor(m - Mj) == 0, name
        assert sp.factor(x * q - R) == 0, name

        dPhi_dx = sp.factor(sp.diff(Phi, x))
        assert sp.factor(dPhi_dx - 4 * N * (1 - R / (x * x))) == 0, name

        num, den = sp.together(dPhi_dx).as_numer_denom()
        assert sp.factor(num - 4 * ((S + 1 + x) * x + R) * (x * x - R)) == 0, name
        assert den == x ** 3, name

        s2 = d + e - q
        s3 = b + c - 1 - x
        assert sp.factor(q - (d + e) + s2) == 0, name
        assert sp.factor(s3 - (b + c - 1 - x)) == 0, name
        assert sp.factor(u - 1 - (q - v - 1)) == 0, name
        assert sp.factor(x * x - R - x * (x - q)) == 0, name

    print("PASS y=1 capacity fibers s4..s7 reduce to x=1, s2=0, s3=0, u=1, or x=q")


if __name__ == "__main__":
    main()
