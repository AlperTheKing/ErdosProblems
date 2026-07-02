"""Exact scaling reduction for the sibling S7 atom.

This records the homogeneity fact behind the theta-positive reduction:
if S7 has a negative counterexample, then it has one on a lower-bound face
`a=1` or ... or `v=1`.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x, y, u, v, lam = sp.symbols("a b c d e f x y u v lam")
    vals = [a, b, c, d, e, f, x, y, u, v]
    m = x * u + x * v + y * v
    N = sum(vals)
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    E = x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)
    D = N * N - 25 * m
    Phi = 2 * D - 75 * E

    sub = {z: lam * z for z in vals}
    assert sp.factor(D.subs(sub) - lam**2 * D) == 0
    assert sp.factor(E.subs(sub) - lam * E) == 0
    assert sp.factor(Phi.subs(sub) - lam * (2 * lam * D - 75 * E)) == 0

    slacks = [
        e - v,
        d + e - u - v,
        b + c - x - y,
        Y - m,
        a * e + b * f + c * f - m,
        a * c + d * f + e * f - m,
        a * e + d * f + e * f - m,
    ]
    for s in slacks[:3]:
        assert sp.factor(s.subs(sub) - lam * s) == 0
    for s in slacks[3:]:
        assert sp.factor(s.subs(sub) - lam**2 * s) == 0

    print("PASS S7 scaling reduction: negative counterexample scales to a lower-bound face")


if __name__ == "__main__":
    main()
