"""Exact seven-tight slice certificate for S7.

On the all-seven-tight manifold, impose f=1 and y=1.  The remaining
parameters are b,c with b,c>=1 after the monotone push in b, and the script
verifies that dPhi/db has a shifted coefficient-positive numerator.  Thus the
slice minimum occurs at b=1, reducing to the already-checked central Sturm
curve.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    b, c = sp.symbols("b c", positive=True)
    f = sp.Integer(1)
    y = sp.Integer(1)
    a = ((b + c) ** 2 - b * y - f * (b + c)) / c
    d = b
    e = c
    u = b
    v = c
    x = b + c - y
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    E = x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)
    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * E)

    deriv = sp.factor(sp.diff(Phi, b))
    num, den = sp.fraction(deriv)
    Bv, Cv = sp.symbols("B C", nonnegative=True)
    shifted = sp.Poly(sp.expand(num.subs({b: 1 + Bv, c: 1 + Cv})), Bv, Cv)
    coeffs = [coef for _mon, coef in shifted.terms()]
    assert min(coeffs) > 0
    assert sp.factor(den).subs({b: 1, c: 1}) > 0

    # The b=1 central curve is the same one checked in _codex_sib_s7_gate.py.
    t = sp.symbols("t", positive=True)
    central = sp.factor(Phi.subs({b: 1, c: t}))
    P0 = 20 * t**7 - 18 * t**6 - 166 * t**5 + 76 * t**4 + 459 * t**3 + 117 * t**2 - 117 * t + 4
    expected = P0 / (t**2 * (t + 2) * (t**3 + 2 * t**2 + t + 1))
    assert sp.factor(central - expected) == 0
    assert P0.subs(t, 1) == 375
    assert sp.polys.polytools.count_roots(P0, 1, sp.oo) == 0
    print("PASS seven-tight f=y=1 slice: dPhi/db shifted-positive and central Sturm-positive")


if __name__ == "__main__":
    main()
