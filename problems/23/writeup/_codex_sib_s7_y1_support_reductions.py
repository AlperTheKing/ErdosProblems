"""Exact algebraic reductions for observed y=1 SIB-S7 support clusters.

This is a bridge artifact, not a full y=1 proof.  The numerical basin
inventory in _tmp_y1_active_coverage.py classifies all observed low/high
clusters into a small set of supports.  This file records the exact algebraic
reason that those supports are precisely the already-checked parametric
families.

All identities are over the y=1 face.  The balanced x=q supports additionally
use u=1, v=x-1.
"""

from __future__ import annotations

import sympy as sp


def y1_slacks(a, b, c, d, e, f, x, u, v):
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    Y = a * c + b * f + c * f
    return {
        "s1": e - v,
        "s2": d + e - u - v,
        "s3": b + c - x - y,
        "s4": Y - m,
        "s5": a * e + b * f + c * f - m,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
    }


def assert_zero(expr: sp.Expr, label: str) -> None:
    assert sp.factor(expr) == 0, label


def check_all_tight_curve() -> None:
    """b=d=f=u=1 and all seven slacks force the seven-tight curve."""

    a, c, e, x, v = sp.symbols("a c e x v", positive=True)
    b = d = f = u = sp.Integer(1)
    sl = y1_slacks(a, b, c, d, e, f, x, u, v)

    # s1=s2=s3 give e=v and x=c.  With those substitutions the four capacity
    # slacks collapse to the same equation after e=c.
    subs13 = {e: v, x: c}
    assert_zero(sl["s6"].subs(subs13) - sl["s4"].subs(subs13) - (v - c), "all-tight s6-s4")
    assert_zero(sl["s7"].subs(subs13) - sl["s4"].subs(subs13) - (a + 1) * (v - c), "all-tight s7-s4")
    assert_zero(sl["s5"].subs(subs13) - sl["s4"].subs(subs13) - a * (v - c), "all-tight s5-s4")

    t = sp.symbols("t", positive=True)
    subs = {c: t, e: t, v: t, x: t, a: t + 1 - 1 / t}
    for name, expr in sl.items():
        assert_zero(expr.subs(subs), f"all-tight {name}")


def check_high_a_family() -> None:
    """a=b=d=u=1, s1..s5 active already force c=e=f=x=v."""

    c, f, t = sp.symbols("c f t", positive=True)
    a = b = d = u = sp.Integer(1)
    e, v, x = sp.symbols("e v x", positive=True)
    sl = y1_slacks(a, b, c, d, e, f, x, u, v)

    # s1,s2,s3 reduce to e=v and x=c; then s4=(1+c)(f-e) and
    # s5=e-c after s4=0.  Hence f=e=c, and s6/s7 are automatic.
    subs = {v: e, x: c}
    assert_zero(sl["s4"].subs(subs) - (1 + c) * (f - e), "high-A s4")
    assert_zero(sl["s5"].subs(subs).subs(f, e) - (e - c), "high-A s5")

    fam = {c: t, e: t, f: t, v: t, x: t}
    for name, expr in sl.items():
        assert_zero(expr.subs(fam), f"high-A {name}")


def check_xq_family_a() -> None:
    """x=q,u=1, f=1, s3 and s4..s7 force xq survivor family A."""

    a, b, c, d, e, x = sp.symbols("a b c d e x", positive=True)
    u = f = sp.Integer(1)
    v = x - 1
    sl = y1_slacks(a, b, c, d, e, f, x, u, v)

    # s3 gives b=x+1-c.  s4-s5 gives a(c-e), so e=c.  Then s4
    # gives a=(x^2-2)/c, and s6 gives d=x+1-c.
    subs_s3 = {b: x + 1 - c}
    assert_zero((sl["s4"] - sl["s5"]).subs(subs_s3) - a * (c - e), "xq-A s4-s5")
    subs = {b: x + 1 - c, e: c}
    assert_zero(sl["s4"].subs(subs) - (a * c - x**2 + 2), "xq-A s4")
    subs_a = {**subs, a: (x**2 - 2) / c}
    assert_zero(sl["s6"].subs(subs_a) - (d - (x + 1 - c)), "xq-A s6")
    subs_fam = {**subs_a, d: x + 1 - c}
    for name in ("s3", "s4", "s5", "s6", "s7"):
        assert_zero(sl[name].subs(subs_fam), f"xq-A {name}")


def check_xq_family_b() -> None:
    """x=q,u=1, d=f=1, s1,s2,s3,s6,s7 force family B."""

    a, b, c, e, x = sp.symbols("a b c e x", positive=True)
    u = d = f = sp.Integer(1)
    v = x - 1
    sl = y1_slacks(a, b, c, d, e, f, x, u, v)

    subs = {e: x - 1, b: x + 1 - c}
    assert_zero(sl["s7"].subs(subs) - (a * (x - 1) - (x**2 - 1)), "xq-B s7")
    subs_a = {**subs, a: x + 1}
    assert_zero(sl["s6"].subs(subs_a) - ((x + 1) * c - (x**2 - 1)), "xq-B s6")
    subs_fam = {**subs_a, c: x - 1, b: sp.Integer(2)}
    for name in ("s1", "s2", "s3", "s6", "s7"):
        assert_zero(sl[name].subs(subs_fam), f"xq-B {name}")


def check_u1_s7_high_family() -> None:
    """The u1/s7 high support is the b-ray with all other variables one."""

    b = sp.symbols("b", positive=True)
    a = c = d = e = f = x = u = v = sp.Integer(1)
    sl = y1_slacks(a, b, c, d, e, f, x, u, v)
    for name in ("s1", "s2", "s6", "s7"):
        assert_zero(sl[name], f"u1-s7-high {name}")


def check_xq_s5_high_family() -> None:
    """x=q,u=1, a=1, s1,s3 and s4..s7 force the high xq/s5 ray."""

    b, c, d, e, f, x = sp.symbols("b c d e f x", positive=True)
    a = u = sp.Integer(1)
    v = x - 1
    sl = y1_slacks(a, b, c, d, e, f, x, u, v)

    subs13 = {e: x - 1, b: x + 1 - c}
    assert_zero((sl["s4"] - sl["s5"]).subs(subs13) - (c - (x - 1)), "xq-s5 s4-s5")
    subs_c = {**subs13, c: x - 1, b: sp.Integer(2)}
    assert_zero(sl["s5"].subs(subs_c) - ((x + 1) * f - x**2), "xq-s5 s5")
    subs_f = {**subs_c, f: x**2 / (x + 1)}
    assert_zero(sp.factor((x + 1) * sl["s6"].subs(subs_f) - x**2 * (d - 2)), "xq-s5 s6")
    subs_fam = {**subs_f, d: sp.Integer(2)}
    for name in ("s1", "s3", "s4", "s5", "s6", "s7"):
        assert_zero(sl[name].subs(subs_fam), f"xq-s5 {name}")


def main() -> None:
    check_all_tight_curve()
    check_high_a_family()
    check_xq_family_a()
    check_xq_family_b()
    check_u1_s7_high_family()
    check_xq_s5_high_family()
    print("PASS y=1 observed support reductions match exact closed families")


if __name__ == "__main__":
    main()

