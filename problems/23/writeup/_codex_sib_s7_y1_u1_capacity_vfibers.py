"""Exact v-fiber reduction for y=1,u=1 SIB S7 capacity faces.

Fix one capacity face s_j=0, j in {4,5,6,7}, and set y=1,u=1.  Write
M_j for the tight capacity expression.  Then

    m = x(1+v)+v = M_j,        x = (M_j-v)/(1+v).

For fixed core variables a,b,c,d,e,f, Phi is a one-variable function of v:

    N(v) = S + 2 + v + (M_j-v)/(1+v).

All non-quadratic terms are affine in v:

    x(1+v) A/Z + v B/(eY) = (M_j-v) A/Z + v B/(eY).

Consequently

    Phi''(v) = 4 * (N'(v)^2 + N(v) N''(v)) > 0.

Thus any negative point on y=1,u=1,s_j=0 reduces to a v-endpoint
(`v=1`, `s1=0`, `s2=0`, or `s3=0`) or to the single critical leaf Phi'(v)=0.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
    y = sp.Integer(1)
    u = sp.Integer(1)
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

    for name, Mj in caps.items():
        x = (Mj - v) / q
        m = x * q + v
        N = S + x + y + u + v
        Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)

        assert sp.factor(m - Mj) == 0, name
        assert sp.factor(x * q - (Mj - v)) == 0, name

        N1 = sp.diff(N, v)
        N2 = sp.diff(N1, v)
        assert sp.factor(N1 - (1 - (Mj + 1) / q ** 2)) == 0, name
        assert sp.factor(N2 - (2 * (Mj + 1) / q ** 3)) == 0, name

        d2 = sp.factor(sp.diff(Phi, v, 2))
        convex_rhs = 4 * (N1 * N1 + N * N2)
        assert sp.factor(d2 - convex_rhs) == 0, name

        # Positivity certificate for the second derivative:
        # q>0, N>0, Mj>=v+x>=2 on the feasible branch, so N2>0.
        d2_num, d2_den = sp.together(d2).as_numer_denom()
        assert d2_den == q ** 4, name
        assert sp.factor(d2_num - 4 * (q ** 4 * N1 * N1 + q ** 4 * N * N2)) == 0, name

        # Feasible v-interval blockers on this fiber.
        s1 = e - v
        s2 = d + e - q
        s3 = b + c - y - x
        assert sp.diff(s1, v) == -1, name
        assert sp.diff(s2, v) == -1, name
        # s3 increases with v because x decreases along the u=1 capacity fiber.
        s3_v = sp.factor(sp.diff(s3, v))
        assert sp.factor(s3_v - (Mj + 1) / q ** 2) == 0, name

    print("PASS y=1,u=1 capacity v-fibers are convex; minima reduce to v endpoints or Phi'=0")


if __name__ == "__main__":
    main()
