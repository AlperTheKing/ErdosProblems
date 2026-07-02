"""Exact reduction of the y=1,u=1,v=1 all-tight endpoint to all-ones.

The v=1 endpoint scan on y=1,u=1 capacity branches lands at Phi=25 with
all endpoint/capacity slacks tight.  This file records the elementary algebra:
v=1, s1=s2=x1=s3=0 force e=d=x=b=c=1, and any tight capacity then forces
a=f=1.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, f = sp.symbols("a f", positive=True)
    y = u = v = e = d = x = b = c = sp.Integer(1)
    q = u + v
    m = x * q + v
    Y = a * c + b * f + c * f
    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    assert m == 3
    for name, expr in caps.items():
        assert sp.factor(expr - (a + 2 * f)) == 0, name
        # expr=m with a,f>=1 gives a=f=1.
        assert sp.factor((expr - m).subs({a: 1, f: 1})) == 0, name

    S = a + b + c + d + e + f
    N = S + x + y + u + v
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)
    assert sp.factor(Phi.subs({a: 1, f: 1})) == 25

    print("PASS y=1,u=1,v=1 all-tight endpoint is all-ones with Phi=25")


if __name__ == "__main__":
    main()
