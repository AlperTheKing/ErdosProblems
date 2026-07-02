"""Exact one-dimensional fiber reduction for the SIB S7 face y=1,s4=0.

On y=1 put q=u+v.  On the capacity face s4=0 we have

    m = x*q + v = Y,      q = (Y-v)/x.

For fixed core variables a,b,c,d,e,f and fixed v, all non-quadratic terms in
Phi are constant along this fiber.  The only x-dependence is through

    N = S + 1 + x + (Y-v)/x.

Consequently Phi is minimized by moving x toward sqrt(Y-v), unless a fiber
endpoint is hit.  Therefore a negative point on y=1,s4=0 reduces to one of

    x = 1,      s2 = 0,      s3 = 0,      u = 1,      or x = q.

This is a reduction only; it leaves the listed subfaces to be closed.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x, v = sp.symbols("a b c d e f x v", positive=True)
    y = sp.Integer(1)
    S = a + b + c + d + e + f

    Y = a * c + b * f + c * f
    R = Y - v
    q = R / x
    u = q - v
    m = x * q + v
    N = S + y + x + q

    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S))

    # s4=0 is built in.
    assert sp.factor(m - Y) == 0
    assert sp.factor(x * q - R) == 0

    # The exact fiber derivative and its sign-changing factor.
    dPhi_dx = sp.factor(sp.diff(Phi, x))
    assert sp.factor(dPhi_dx - 4 * N * (1 - R / (x * x))) == 0

    # Equivalently, since N>0 and x>0, the sign is that of x^2-R.
    num, den = sp.together(dPhi_dx).as_numer_denom()
    assert sp.factor(num - 4 * ((S + 1 + x) * x + R) * (x * x - R)) == 0
    assert den == x ** 3

    # Feasible fiber interval endpoints:
    #   x >= 1,
    #   q <= d+e            <=> s2=0 at lower endpoint,
    #   x <= b+c-1          <=> s3=0 at upper endpoint,
    #   u=q-v >= 1          <=> u=1 at upper endpoint.
    s2 = d + e - q
    s3 = b + c - 1 - x
    assert sp.factor(q - (d + e)) == -sp.factor(s2)
    assert sp.factor(s3 - (b + c - 1 - x)) == 0
    assert sp.factor(u - 1 - (q - v - 1)) == 0

    # At an interior fiber minimizer, x^2=R, equivalently x=q because x*q=R.
    assert sp.factor(x * x - R - x * (x - q)) == 0

    print("PASS y=1,s4=0 fiber reduces to x=1, s2=0, s3=0, u=1, or x=q")


if __name__ == "__main__":
    main()
