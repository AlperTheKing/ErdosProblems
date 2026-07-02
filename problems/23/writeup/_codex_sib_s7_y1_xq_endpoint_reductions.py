"""Exact reductions for observed y=1, x=q endpoint active systems.

`_codex_sib_s7_y1_xq_endpoint_inventory.py` records the observed endpoint
inventory.  This file makes the algebra behind that map explicit: each
observed active system reduces, over the positive domain, to one of the exact
families already certified positive or infeasible in the x=q endpoint files.

This is still not a full endpoint coverage theorem.  It closes the observed
endpoint map by Groebner reduction.
"""

from __future__ import annotations

import sympy as sp


a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v", positive=True)
y = sp.Integer(1)
q = u + v
m = x * q + v
Y = a * c + b * f + c * f

SLACKS = {
    "a1": a - 1,
    "b1": b - 1,
    "c1": c - 1,
    "d1": d - 1,
    "e1": e - 1,
    "f1": f - 1,
    "x1": x - 1,
    "u1": u - 1,
    "v1": v - 1,
    "s1": e - v,
    "s2": d + e - u - v,
    "s3": b + c - x - y,
    "s4": Y - m,
    "s5": a * e + b * f + c * f - m,
    "s6": a * c + d * f + e * f - m,
    "s7": a * e + d * f + e * f - m,
    "xq": x - u - v,
}

VARS = (a, b, c, d, e, f, u, v, x)


def groebner_basis(labels: tuple[str, ...]) -> set[sp.Expr]:
    eqs = [SLACKS["xq"]]
    eqs.extend(SLACKS[label] for label in labels)
    G = sp.groebner(eqs, *VARS, order="lex")
    return {sp.factor(poly.as_expr()) for poly in G.polys}


def assert_contains(basis: set[sp.Expr], required: set[sp.Expr], label: str) -> None:
    missing = {expr for expr in required if not any(sp.factor(poly - expr) == 0 for poly in basis)}
    assert not missing, (label, missing, basis)


def check_xq_a() -> None:
    """XQ_A endpoint systems reduce to f=u=1, c=e, a=(x^2-2)/c."""

    cases = {
        "u1": ("f1", "s3", "s4", "s5", "s6", "s7", "u1"),
        "s3": ("f1", "s3", "s4", "s5", "s6", "s7", "u1"),
    }
    required = {
        a * c - x**2 + 2,
        a * e - x**2 + 2,
        b + c - x - 1,
        (c - e) * (x**2 - 2),
        d + e - x - 1,
        f - 1,
        u - 1,
        v - x + 1,
    }
    for name, labels in cases.items():
        assert_contains(groebner_basis(labels), required, f"XQ_A {name}")
    # Since v=x-1>=1 on this endpoint, x>=2 and x^2-2>0, so c=e.

    # v=1 and s1 endpoint subfaces of XQ_A have smaller bases.
    assert_contains(
        groebner_basis(("f1", "s3", "s4", "s5", "s6", "s7", "u1", "v1")),
        {a * e - 2, b + e - 3, c - e, d + e - 3, f - 1, u - 1, v - 1, x - 2},
        "XQ_A v1",
    )
    assert_contains(
        groebner_basis(("f1", "s1", "s3", "s4", "s5", "s6", "s7", "u1")),
        {
            a * c - x**2 + 2,
            a * x - a - x**2 + 2,
            b + c - x - 1,
            -(x**2 - 2) * (-c + x - 1),
            d - 2,
            e - x + 1,
            f - 1,
            u - 1,
            v - x + 1,
        },
        "XQ_A s1",
    )
    print("XQ-ENDPOINT XQ_A observed systems reduce to the certified XQ_A family/subfaces")


def check_xq_b() -> None:
    """XQ_B endpoint systems reduce to a=x+1,b=2,c=e=v=x-1,d=f=u=1."""

    labels = ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1")
    required = {
        a * c - x**2 + 1,
        -(x - 1) * (-a + x + 1),
        b + c - x - 1,
        -(x - 1) * (x + 1) * (-c + x - 1),
        d - 1,
        e - x + 1,
        f - 1,
        u - 1,
        v - x + 1,
    }
    # This same observed support appears as u1, s1, s2, and s3 endpoint blocker.
    for name in ("u1", "s1", "s2", "s3"):
        assert_contains(groebner_basis(labels), required, f"XQ_B {name}")
    # Positive domain has x>=2, so x-1>0 and x+1>0, forcing a=x+1,c=x-1,b=2.
    print("XQ-ENDPOINT XQ_B observed systems reduce to the certified XQ_B family")


def check_v1_family() -> None:
    """The v=1 endpoint family reduces to c=e=x-1,b=2,d=f=1."""

    assert_contains(
        groebner_basis(("d1", "f1", "s2", "s3", "s6", "s7", "v1")),
        {
            a * c - x**2 + x - 1,
            a * x - a - x**2 + x - 1,
            b + c - x - 1,
            -(-c + x - 1) * (x**2 - x + 1),
            d - 1,
            e - x + 1,
            f - 1,
            u - x + 1,
            v - 1,
        },
        "v1 family",
    )
    # x>=2 and x^2-x+1>0 force c=x-1.
    print("XQ-ENDPOINT v=1 observed system reduces to the certified v=1 family")


def check_uv1_curve() -> None:
    """The u=v=1 endpoint curve reduces to x=2,c=e=t,b=3-t,a=4/t-1."""

    basis = groebner_basis(("d1", "f1", "s3", "s6", "s7", "u1", "v1"))
    assert_contains(
        basis,
        {
            a * c + e - 4,
            a * e + e - 4,
            b + c - 3,
            (c - e) * (e - 4),
            d - 1,
            f - 1,
            u - 1,
            v - 1,
            x - 2,
        },
        "u=v=1 curve",
    )
    # The alternative e=4 branch forces a=0 from a*e+e-4=0, outside the
    # positive domain, so c=e.
    print("XQ-ENDPOINT u=v=1 observed system reduces to the certified endpoint curve")


def check_xq_s5_high() -> None:
    """XQ_S5_HIGH endpoint systems reduce to a=1,b=d=2,c=e=v=x-1."""

    labels = ("a1", "s1", "s3", "s4", "s5", "s6", "s7", "u1")
    required = {
        a - 1,
        b - 2,
        c - x + 1,
        f * (d - 2),
        x**2 * (d - 2),
        e - x + 1,
        f * x + f - x**2,
        u - 1,
        v - x + 1,
    }
    for name in ("s1", "s3"):
        assert_contains(groebner_basis(labels), required, f"XQ_S5_HIGH {name}")
    # Positive domain has f>0 and x>0, hence d=2, and f=x^2/(x+1).

    assert_contains(
        groebner_basis(("a1", "c1", "e1", "s1", "s3", "s4", "s5", "s6", "s7", "u1", "v1")),
        {a - 1, b - 2, c - 1, d - 2, e - 1, 3 * f - 4, u - 1, v - 1, x - 2},
        "XQ_S5_HIGH v1",
    )
    print("XQ-ENDPOINT XQ_S5_HIGH observed systems reduce to the certified high family/subfaces")


def main() -> None:
    check_xq_a()
    check_xq_b()
    check_v1_family()
    check_uv1_curve()
    check_xq_s5_high()
    print("PASS y=1 x=q observed endpoint active systems reduce to exact closed families")


if __name__ == "__main__":
    main()
