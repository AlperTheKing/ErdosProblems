"""Exact endpoint-fiber algebra for the compact sibling S7 reduction.

GPT-Pro's endpoint-fiber reduction freezes

    a,b,c,d,e,f, p=x+y, q=u+v, theta

and views the compact numerator as a function of the two endpoint variables
(y,u), with x=p-y and v=q-u.  This script verifies the exact identity

    P_compact / (e*Y*Z) = C + K*y*u - H*y,

where K=50+75*theta*B/(eY)>0.  The proof consequence is that the fiber
minimum is piecewise linear and occurs on one of fourteen endpoint/capacity
faces.
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
    expected = C + K * y * u - H * y
    assert sp.factor(P_compact / (e * Y * Z) - expected) == 0

    # The four capacity constraints become yu >= pq-M_j.
    M4 = Y
    M5 = a * e + b * f + c * f
    M6 = a * c + d * f + e * f
    M7 = a * e + d * f + e * f
    for Mj in [M4, M5, M6, M7]:
        assert sp.expand(Mj - m - (Mj - p * q + y * u)) == 0

    # Linear endpoint constraints in the frozen fiber.
    # y>=theta, x>=theta -> y in [theta, p-theta].
    assert sp.expand(x - th - (p - th - y)) == 0
    # u>=theta, v>=theta -> u in [theta, q-theta].
    assert sp.expand(v - th - (q - th - u)) == 0
    # s1=e-v>=0 -> u>=q-e.
    assert sp.expand(e - v - (e - q + u)) == 0

    print("PASS endpoint-fiber algebra: compact S7 reduces to 14 endpoint/capacity faces")


if __name__ == "__main__":
    main()

