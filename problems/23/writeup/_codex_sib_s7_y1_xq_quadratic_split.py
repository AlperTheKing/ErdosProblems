"""Exact quadratic split for the y=1, x=q branch.

On a y=1 capacity face s_j=0, let M_j be the tight capacity expression.
The balanced branch x=q has

    v = M_j - x^2,
    u = x - v = x + x^2 - M_j,
    N = S + 1 + 2x.

For fixed core variables a,b,c,d,e,f, Phi is a quadratic polynomial in x.
Moreover dPhi/dx=(C*x+D)/(e*Y*Z), where D is strictly positive on the positive domain.
If C>=0 then Phi is strictly increasing on x>0; if C<0 then Phi is concave and its only critical point is a maximum.
Therefore any negative minimum on a compact feasible x=q fiber occurs at a feasible endpoint.

The endpoint blockers are v=1, u=1, s1=0, s2=0, or s3=0.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x = sp.symbols("a b c d e f x", positive=True)
    y = sp.Integer(1)
    S = a + b + c + d + e + f
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = (
        b * d
        + c * d
        + d * f
        + a * c
        + a * e
        + b * f
        + b * e
        + c * f
        + c * e
        + e * f
    )
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }

    expected_d2_num = None
    for name, Mj in caps.items():
        q = x
        v = Mj - x**2
        u = q - v
        m = x * q + v
        N = S + y + x + q
        Phi = sp.factor(
            2 * (N**2 - 25 * m)
            - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)
        )

        assert sp.factor(m - Mj) == 0, name
        assert sp.Poly(sp.together(Phi).as_numer_denom()[0], x).degree() <= 2, name

        d1 = sp.factor(sp.diff(Phi, x))
        d2 = sp.factor(sp.diff(Phi, x, 2))
        d1_num, d1_den = sp.together(d1).as_numer_denom()
        d2_num, d2_den = sp.together(d2).as_numer_denom()
        assert sp.factor(d1_den - e * Y * Z) == 0, name
        assert sp.factor(d2_den - e * Y * Z) == 0, name
        assert sp.Poly(d1_num, x).degree() <= 1, name
        assert sp.Poly(d2_num, x).degree() == 0, name
        d1_poly = sp.Poly(d1_num, x)
        slope = d1_poly.coeff_monomial(x)
        intercept = d1_poly.coeff_monomial(1)
        positive_intercept = 8 * e * Y * (a * c * e + b * d * f + b * e * f + c * d * f + c * e * f) * (S + 1)
        assert sp.factor(intercept - positive_intercept) == 0, name
        assert sp.factor(slope - d2_num) == 0, name
        if expected_d2_num is None:
            expected_d2_num = sp.factor(d2_num)
        else:
            assert sp.factor(d2_num - expected_d2_num) == 0, name

        # Feasible endpoint blockers on the x=q fiber.
        s1 = e - v
        s2 = d + e - q
        s3 = b + c - y - x
        u1 = u - 1
        v1 = v - 1
        assert sp.factor(sp.diff(v1, x) + 2 * x) == 0, name
        assert sp.factor(sp.diff(u1, x) - (1 + 2 * x)) == 0, name
        assert sp.factor(sp.diff(s1, x) - 2 * x) == 0, name
        assert sp.diff(s2, x) == -1, name
        assert sp.diff(s3, x) == -1, name

    print("PASS y=1 x=q branch has no interior minimum; minima reduce to endpoints")


if __name__ == "__main__":
    main()
