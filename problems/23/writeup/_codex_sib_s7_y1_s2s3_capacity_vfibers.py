"""Exact v-fiber reductions for y=1 capacity faces with s2=0 or s3=0.

On a y=1 capacity face s_j=0, write M_j for the tight capacity expression:

    m = xq + v = M_j.

If s2=0 then q=d+e is fixed while x=(M_j-v)/q.  If s3=0 then
x=b+c-1 is fixed while q=(M_j-v)/x.  In both cases the non-quadratic part of
Phi is affine in v and the only curved term is 2N(v)^2, so Phi is convex on
the fiber:

    s2=0: Phi''(v)=4/q^2,
    s3=0: Phi''(v)=4/x^2.

Thus negative points on these subbranches reduce to v-endpoints or a single
critical leaf Phi'(v)=0.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
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
        # s2=0 branch: q=d+e is fixed.
        q = d + e
        x = (Mj - v) / q
        u = q - v
        m = x * q + v
        N = S + x + y + q
        Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)

        assert sp.factor(m - Mj) == 0, ("s2", name)
        assert sp.factor(sp.diff(Phi, v, 2) - 4 / q ** 2) == 0, ("s2", name)

        s1 = e - v
        u1 = u - 1
        x1 = x - 1
        s3 = b + c - y - x
        assert sp.diff(s1, v) == -1, ("s2", name)
        assert sp.diff(u1, v) == -1, ("s2", name)
        assert sp.factor(sp.diff(x1, v) + 1 / q) == 0, ("s2", name)
        assert sp.factor(sp.diff(s3, v) - 1 / q) == 0, ("s2", name)

        # s3=0 branch: x=b+c-1 is fixed.
        x = b + c - 1
        q = (Mj - v) / x
        u = q - v
        m = x * q + v
        N = S + x + y + q
        Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)

        assert sp.factor(m - Mj) == 0, ("s3", name)
        assert sp.factor(sp.diff(Phi, v, 2) - 4 / x ** 2) == 0, ("s3", name)

        s1 = e - v
        u1 = u - 1
        s2 = d + e - q
        assert sp.diff(s1, v) == -1, ("s3", name)
        assert sp.factor(sp.diff(u1, v) + (1 / x + 1)) == 0, ("s3", name)
        assert sp.factor(sp.diff(s2, v) - 1 / x) == 0, ("s3", name)

    print("PASS y=1 capacity s2/s3 v-fibers are convex; minima reduce to v endpoints or Phi'=0")


if __name__ == "__main__":
    main()
