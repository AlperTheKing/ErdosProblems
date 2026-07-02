"""Exact checks for GPT-Pro's sibling S7 atom.

This verifies two narrow facts for the representative sibling row

    graph=sib, side=0001111000, Q=(1,6,8,4,9).

1. The proposed S7 formula for I(Q)-N matches exact path enumeration.
2. The proposed central seven-tight KKT face has positive margin by Sturm.

This does not prove the full S7 lemma.
"""

from __future__ import annotations

import contextlib
import io

import sympy as sp

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_active5_symbolic_margin import symbolic_margin
    from _codex_c5lift_weighted_quotient_gate import SIB


def main() -> None:
    side = "0001111000"
    row = (1, 6, 8, 4, 9)
    w, _n, _M, _terms, I, _m, _margin, _numer, _denom, _poly = symbolic_margin(SIB, side, row)

    a, b, c, d, e, f, x, y, u, v = sp.symbols("a b c d e f x y u v", positive=True)
    relabel = {
        w[0]: a,
        w[3]: b,
        w[4]: c,
        w[5]: d,
        w[6]: e,
        w[8]: f,
        w[1]: x,
        w[2]: y,
        w[7]: u,
        w[9]: v,
    }

    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    IminusN_s7 = x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)

    assert sp.factor((I - sum(w)).subs(relabel) - IminusN_s7) == 0

    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * IminusN_s7)

    t = sp.symbols("t", positive=True)
    central = {
        b: 1,
        d: 1,
        f: 1,
        u: 1,
        y: 1,
        c: t,
        e: t,
        x: t,
        v: t,
        a: t + 1 - 1 / t,
    }
    Phi_central = sp.factor(Phi.subs(central))
    P0 = 20 * t**7 - 18 * t**6 - 166 * t**5 + 76 * t**4 + 459 * t**3 + 117 * t**2 - 117 * t + 4
    expected = P0 / (t**2 * (t + 2) * (t**3 + 2 * t**2 + t + 1))
    assert sp.factor(Phi_central - expected) == 0
    assert P0.subs(t, 1) == 375
    assert sp.polys.polytools.count_roots(P0, 1, sp.oo) == 0

    print("PASS S7 identity and central KKT face")


if __name__ == "__main__":
    main()
