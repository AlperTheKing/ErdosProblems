"""Exact rational stress for the s3 hard-chart ridge directions.

This is explicitly not a proof certificate.  It records which ridge direction is
worth certifying after `_codex_sib_s7_y1_s3_pair_structure.py`:

* on s3=0,s7=0, increasing R=c-e had positive dPhi/dR on the deterministic
  feasible rational sample set below;
* on s3=0,s6=0, increasing R=e-c has an exact feasible rational sample with
  negative dPhi/dR, so direct ridge descent is false there.
"""

from __future__ import annotations

from fractions import Fraction

import sympy as sp


R = sp.symbols("R")


def phi(a, b, c, d, e, f, x, u, v):
    y = sp.Integer(1)
    m = x * u + x * v + v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    S = a + b + c + d + e + f
    return 2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + v * B / (e * Y) - S)


def slacks(a, b, c, d, e, f, x, u, v):
    m = x * u + x * v + v
    Y = a * c + b * f + c * f
    return {
        "s1": e - v,
        "s2": d + e - u - v,
        "s3": b + c - x - 1,
        "s4": Y - m,
        "s5": a * e + b * f + c * f - m,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
    }


def dphi_s7(a, b, e, d, f, v, r):
    c = e + R
    x = b + c - 1
    m = a * e + d * f + e * f
    u = (m - v * (x + 1)) / x
    expr = phi(a, b, c, d, e, f, x, u, v)
    val = sp.factor(sp.diff(expr, R).subs(R, r))
    ss = slacks(a, b, e + r, d, e, f, b + e + r - 1, u.subs(R, r), v)
    return val, ss


def dphi_s6(a, b, c, d, f, v, r):
    e = c + R
    x = b + c - 1
    m = a * c + d * f + e * f
    u = (m - v * (x + 1)) / x
    expr = phi(a, b, c, d, e, f, x, u, v)
    val = sp.factor(sp.diff(expr, R).subs(R, r))
    ss = slacks(a, b, c, d, c + r, f, x, u.subs(R, r), v)
    return val, ss


def assert_feasible(ss: dict[str, sp.Expr], active: str) -> None:
    assert ss["s3"] == 0
    assert ss[active] == 0
    for name, value in ss.items():
        assert value >= 0, (name, value)


def main() -> None:
    # Deterministic feasible s7 samples.  All use small exact rationals and
    # have dPhi/dR > 0, supporting descent to the c=e ridge.
    s7_samples = [
        (sp.Rational(3), sp.Rational(2), sp.Rational(2), sp.Rational(2), sp.Rational(2), sp.Rational(1), sp.Rational(1, 2)),
        (sp.Rational(5, 2), sp.Rational(3), sp.Rational(2), sp.Rational(3, 2), sp.Rational(2), sp.Rational(1), sp.Rational(1)),
        (sp.Rational(4), sp.Rational(2), sp.Rational(3), sp.Rational(2), sp.Rational(3), sp.Rational(1), sp.Rational(2)),
        (sp.Rational(7, 3), sp.Rational(5, 2), sp.Rational(2), sp.Rational(5, 3), sp.Rational(2), sp.Rational(1), sp.Rational(3, 2)),
    ]
    for sample in s7_samples:
        val, ss = dphi_s7(*sample)
        assert_feasible(ss, "s7")
        assert val > 0, (sample, val)

    # A direct ridge-descent obstruction on s6.  This exact rational point was
    # rounded from a random feasible witness and then rechecked exactly.
    s6_bad = (
        sp.Rational(2223155, 1000000),
        sp.Rational(3744102, 1000000),
        sp.Rational(3095854, 1000000),
        sp.Rational(1356826, 1000000),
        sp.Rational(4456669, 1000000),
        sp.Rational(2088402, 1000000),
        sp.Rational(481580, 1000000),
    )
    val, ss = dphi_s6(*s6_bad)
    assert_feasible(ss, "s6")
    assert val < 0, val

    print("PASS y=1 s3 ridge stress: s7 direct ridge derivative positive on samples, s6 direct ridge derivative has exact negative witness")


if __name__ == "__main__":
    main()
