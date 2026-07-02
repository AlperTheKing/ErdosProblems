"""Exact y=1 six-face reduction for the sibling S7 atom.

This verifies GPT-Pro's proposed reduction of the old-variable endpoint face
`y=1` to six smaller faces:

    s4=0, s5=0, s6=0, s7=0,
    s1=s2=s3=0,
    u=1, s2=s3=0.

The script checks the exact algebraic identities used in the descent and the
elementary lower bounds proving that a negative feasible point cannot have
nonnegative x- or q-derivative.

This is a reduction only; it does not prove the six remaining faces empty.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def main() -> None:
    a, b, c, d, e, f, x, q, v = sp.symbols("a b c d e f x q v", positive=True)
    y = sp.Integer(1)
    u = q - v
    S = a + b + c + d + e + f
    T = a + b + c + f
    D = d + e
    m = x * q + v
    N = S + y + x + q

    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f

    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * q * A / Z + v * B / (e * Y) - S))
    Pi = sp.factor(e * Y * Z * Phi)

    # Basic row-form identity.
    CA = 50 + 75 * A / Z
    CB = 50 + 75 * B / (e * Y)
    assert sp.factor(Phi - (2 * N * N + 75 * S - CA * x * q - CB * v)) == 0

    # Cleared derivative identities.
    Rx = sp.factor(Z * sp.diff(Phi, x))
    Rq = sp.factor(Z * sp.diff(Phi, q))
    assert sp.factor(Rx - (4 * Z * N - q * (50 * Z + 75 * A))) == 0
    assert sp.factor(Rq - (4 * Z * N - x * (50 * Z + 75 * A))) == 0

    Lx = sp.factor(e * Y * (2 * N * (N - 2 * x) + 75 * S) - (50 * e * Y + 75 * B) * v)
    Lq = sp.factor(e * Y * (2 * N * (N - 2 * q) + 75 * S) - (50 * e * Y + 75 * B) * v)
    assert sp.factor(Pi - (e * Y * x * Rx + Z * Lx)) == 0
    assert sp.factor(Pi - (e * Y * q * Rq + Z * Lq)) == 0

    # B = Y + e*T, so CB*v = 50v + 75v/e + 75v*T/Y.
    assert sp.factor(B - (Y + e * T)) == 0

    # Verify the elementary positive lower bounds used for Lx and Lq.
    # Feasibility supplies:
    #   x <= b+c-1, q >= 2, q <= D, v <= e <= D, v <= Y.
    # The bracket Lx/(eY) is bounded below by
    #   2(T+D+q+2)(a+d+e+f+q+2)+25D-75 >= 135.
    lower_x = 2 * (T + D + q + 2) * (a + d + e + f + q + 2) + 25 * D - 75
    lower_x_min = lower_x.subs({a: 1, b: 1, c: 1, d: 1, e: 1, f: 1, q: 2})
    assert lower_x_min == 135
    A0, B0, C0, D0, E0, F0, Q0 = sp.symbols("A0 B0 C0 D0 E0 F0 Q0", nonnegative=True)
    shifted_x = lower_x.subs({
        a: 1 + A0,
        b: 1 + B0,
        c: 1 + C0,
        d: 1 + D0,
        e: 1 + E0,
        f: 1 + F0,
        q: 2 + Q0,
    }) - 135
    assert coeffs_nonnegative(shifted_x, (A0, B0, C0, D0, E0, F0, Q0))

    # The bracket Lq/(eY) is bounded below by
    #   2(T+D+q+2)(T+2)+25D-75 >= 95.
    lower_q = 2 * (T + D + q + 2) * (T + 2) + 25 * D - 75
    lower_q_min = lower_q.subs({a: 1, b: 1, c: 1, d: 1, e: 1, f: 1, q: 2})
    assert lower_q_min == 95
    shifted_q = lower_q.subs({
        a: 1 + A0,
        b: 1 + B0,
        c: 1 + C0,
        d: 1 + D0,
        e: 1 + E0,
        f: 1 + F0,
        q: 2 + Q0,
    }) - 95
    assert coeffs_nonnegative(shifted_q, (A0, B0, C0, D0, E0, F0, Q0))

    # Endpoint blockers in the descent:
    # Step A, increasing x at fixed q,v, only s3 or a capacity slack can tighten.
    s3 = b + c - x - 1
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m
    assert sp.diff(s3, x) == -1
    for sj in [s4, s5, s6, s7]:
        assert sp.diff(sj, x) == -q

    # Step B, increasing q at fixed x,v, only s2 or capacity slacks can tighten.
    s2 = D - q
    assert sp.diff(s2, q) == -1
    for sj in [s4, s5, s6, s7]:
        assert sp.diff(sj, q) == -x

    # Step C, increasing v at fixed q, only u=1, s1, or capacity slacks can tighten.
    s1 = e - v
    assert sp.factor(sp.diff(Phi, v) + CB) == 0
    assert sp.diff(u - 1, v) == -1
    assert sp.diff(s1, v) == -1
    assert sp.diff(s2, v) == 0
    assert sp.diff(s3, v) == 0
    for sj in [s4, s5, s6, s7]:
        assert sp.diff(sj, v) == -1

    print("PASS y=1 six-face reduction: derivative blockers and descent algebra verified")


if __name__ == "__main__":
    main()
