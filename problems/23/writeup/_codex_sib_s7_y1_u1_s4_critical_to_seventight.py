"""Exact reduction of the y=1,u=1,s4 critical active set to seven-tight.

The u=1 capacity critical scan found an s4-branch survivor with active set

    b=d=f=1,  s1=s2=s3=s5=s6=s7=0.

These equations force

    c=e=v=x=t,       a=t+1-1/t,

which is the already closed all-seven-tight y=1 manifold handled by
_codex_sib_s7_seventight_y1.py.  This file records the algebraic reduction.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    t = sp.symbols("t", positive=True)
    y = u = b = d = f = sp.Integer(1)
    c = e = v = x = t
    q = u + v
    a = t + 1 - 1 / t

    S = a + b + c + d + e + f
    N = S + x + y + u + v
    m = x * q + v
    Y = a * c + b * f + c * f
    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    slacks = {
        "s1": e - v,
        "s2": d + e - u - v,
        "s3": b + c - x - y,
        **{name: expr - m for name, expr in caps.items()},
    }
    assert all(sp.factor(expr) == 0 for expr in slacks.values())
    assert sp.factor(m - (t ** 2 + 2 * t)) == 0
    assert sp.factor(N - (a + 4 * t + 5)) == 0
    assert sp.factor(a - (t + 1 - 1 / t)) == 0

    print("PASS y=1,u=1 s4 critical active set is the seven-tight manifold")


if __name__ == "__main__":
    main()
