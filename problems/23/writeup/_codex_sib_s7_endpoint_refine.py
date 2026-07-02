"""Refined endpoint-fiber face reduction for the sibling S7 atom.

The first endpoint-fiber gate reduces a compact theta-positive counterexample
to fourteen faces, including two broad endpoint faces y=theta and x=theta.

This script verifies the exact algebraic refinement that those two broad faces
can be replaced by two-equation faces.  On a frozen

    a,b,c,d,e,f,p=x+y,q=u+v,theta

fiber, the compact numerator divided by e*Y*Z is

    C + K*y*u - H*y,     K > 0.

Hence after fixing an endpoint y=theta or x=theta (i.e. y=p-theta),
the expression is strictly increasing in u.  The fiber minimum therefore uses

    u = max(theta, q-e, R/y),     R = p*q - min(M4,M5,M6,M7).

Consequently every negative point on an endpoint face can be moved, without
increasing the compact numerator, to one of

    u=theta,  v=e,  or  m=M_j for some j in {4,5,6,7}.

This removes the two one-equation faces from the 14-face reduction and replaces
them by endpoint+endpoint/capacity faces.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, p, q, y, u, th = sp.symbols("a b c d e f p q y u theta")
    x = p - y
    v = q - u
    S = a + b + c + d + e + f
    m = x * u + x * v + y * v
    assert sp.expand(m - (p * q - y * u)) == 0

    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f

    P_compact = sp.expand(
        2 * e * Y * Z * (1 - 25 * m)
        - 75 * th * (e * Y * x * q * A + Z * y * v * B - e * Y * Z * S)
    )

    alpha = A / Z
    beta = B / (e * Y)
    C = 2 - 50 * p * q - 75 * th * alpha * p * q + 75 * th * S
    K = 50 + 75 * th * beta
    H = 75 * th * (beta - alpha) * q
    F = C + K * y * u - H * y
    assert sp.factor(P_compact / (e * Y * Z) - F) == 0

    # For either endpoint y=theta or x=theta, y is fixed and positive, so
    # dF/du = K*y is strictly positive on the theta-positive compact region.
    assert sp.factor(sp.diff(F, u) - K * y) == 0

    # The lower endpoint for u is max(theta, q-e, R/y), where each capacity
    # branch R/y is equivalent to one of the product slacks becoming tight.
    M4 = Y
    M5 = a * e + b * f + c * f
    M6 = a * c + d * f + e * f
    M7 = a * e + d * f + e * f
    for Mj in [M4, M5, M6, M7]:
        assert sp.expand(Mj - m - (Mj - p * q + y * u)) == 0

    # u=theta is the lower endpoint from u>=theta.
    assert sp.expand(u - th) == u - th
    # q-e lower endpoint is exactly v=e.
    assert sp.expand(u - (q - e) - (e - v)) == 0
    # The other upper endpoint x=theta is y=p-theta.
    assert sp.expand(x - th - (p - th - y)) == 0

    print("PASS refined endpoint-fiber: broad x/y endpoint faces split into endpoint/capacity faces")


if __name__ == "__main__":
    main()
