"""Exact v-fiber reductions for y=1,x=1 capacity subfaces.

After the y=1 capacity-fiber reduction, one endpoint class is x=1.  On any
capacity face s_j=0, j in {4,5,6,7}, write M_j for the capacity RHS.  With
y=x=1,

    m = u + 2v = M_j,      u = M_j - 2v,
    q = u+v = M_j - v.

For fixed core variables a,b,c,d,e,f, Phi is a convex quadratic in v.  Thus a
negative point on y=1,x=1,s_j=0 reduces to one of the feasible interval
endpoints

    v=1, u=1, s1=0, s2=0,

or to the interior critical equation dPhi/dv=0.

This is a reduction only; it leaves the endpoint/critical subfaces to close.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
    x = sp.Integer(1)
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
        u = Mj - 2 * v
        q = u + v
        m = x * u + x * v + y * v
        N = S + x + y + u + v
        Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S))

        assert sp.factor(m - Mj) == 0, name
        assert sp.factor(q - (Mj - v)) == 0, name
        assert sp.factor(N - (S + 2 + Mj - v)) == 0, name

        dPhi_dv = sp.factor(sp.diff(Phi, v))
        expected = -4 * N + 75 * (A / Z - B / (e * Y))
        assert sp.factor(dPhi_dv - expected) == 0, name
        assert sp.factor(sp.diff(Phi, v, 2) - 4) == 0, name

        # Feasible v-interval endpoints:
        s1 = e - v
        s2 = d + e - q
        assert sp.factor(u - 1 - (Mj - 2 * v - 1)) == 0, name
        assert sp.factor(s1 - (e - v)) == 0, name
        assert sp.factor(s2 - (d + e - Mj + v)) == 0, name

    print("PASS y=1,x=1 capacity v-fibers reduce to v=1,u=1,s1=0,s2=0,or dPhi/dv=0")


if __name__ == "__main__":
    main()
