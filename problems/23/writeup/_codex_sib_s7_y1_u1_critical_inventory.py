"""Exact inventory for observed y=1,u=1 capacity-critical leaves.

This replaces the stress-only labels in
`_codex_sib_s7_y1_u1_critical_stress.py` by algebraic reductions.  It is still
not a full critical-leaf coverage theorem: it proves that every observed
critical support reduces to an already closed exact family.

The branch is y=1,u=1.  On a capacity face s_j=0, write M_j for the selected
capacity expression and use

    x = (M_j - v)/(1+v).

The observed critical supports reduce to one of:

* seven-tight curve;
* the d=f=1, s1=s2=s3=s6=s7 high survivor;
* the high strip a=b=d=1, c=e=v, x=f, 1<=f<=e.
"""

from __future__ import annotations

import sympy as sp


a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
y = u = sp.Integer(1)
q = 1 + v
Y = a * c + b * f + c * f
CAPS = {
    "s4": Y,
    "s5": a * e + b * f + c * f,
    "s6": a * c + d * f + e * f,
    "s7": a * e + d * f + e * f,
}
VARS = (a, b, c, d, e, f, v)


def slacks(cap: str) -> dict[str, sp.Expr]:
    M = CAPS[cap]
    x = (M - v) / q
    out = {
        "a1": a - 1,
        "b1": b - 1,
        "c1": c - 1,
        "d1": d - 1,
        "e1": e - 1,
        "f1": f - 1,
        "v1": v - 1,
        "x1": x - 1,
        "s1": e - v,
        "s2": d + e - q,
        "s3": b + c - x - 1,
    }
    for name, expr in CAPS.items():
        if name != cap:
            out[name] = expr - M
    return out


def groebner_basis(cap: str, labels: tuple[str, ...]) -> set[sp.Expr]:
    sl = slacks(cap)
    eqs = [sp.together(sl[label]).as_numer_denom()[0] for label in labels]
    G = sp.groebner(eqs, *VARS, order="lex")
    return {sp.factor(poly.as_expr()) for poly in G.polys}


def assert_contains(basis: set[sp.Expr], required: set[sp.Expr], label: str) -> None:
    missing = required - basis
    assert not missing, (label, missing, basis)


def check_seven_tight_observed() -> None:
    """Observed s4/s5 critical supports force the seven-tight curve."""

    cases = {
        "s4": ("b1", "d1", "f1", "s1", "s2", "s3", "s5", "s6", "s7"),
        "s5": ("b1", "d1", "f1", "s1", "s2", "s3", "s4", "s6", "s7"),
    }
    for cap, labels in cases.items():
        basis = groebner_basis(cap, labels)
        assert_contains(
            basis,
            {
                b - 1,
                c - v,
                d - 1,
                e - v,
                f - 1,
                a * v - v**2 - v + 1,
            },
            f"seven-tight {cap}",
        )
    print("CRIT-INV seven-tight observed supports reduce to a=v+1-1/v, b=d=f=1, c=e=x=v")


def check_s6s7_high_observed() -> None:
    """Observed s6/s7 critical supports force the known high survivor family."""

    cases = {
        "s6": ("d1", "f1", "s1", "s2", "s3", "s7"),
        "s7": ("d1", "f1", "s1", "s2", "s3", "s6"),
    }
    for cap, labels in cases.items():
        basis = groebner_basis(cap, labels)
        assert_contains(
            basis,
            {
                d - 1,
                e - v,
                f - 1,
            },
            f"s6/s7 high {cap}",
        )
        # The remaining basis has the two equations used in
        # _codex_sib_s7_y1_u1_s6s7_survivor.py:
        #   a*c = b*v+b+c*v+c-v-2 and a*v = b*v+b+c*v+c-v-2.
        assert any(sp.factor(poly - (a * c - b * v - b - c * v - c + v + 2)) == 0 for poly in basis)
        assert any(sp.factor(poly - (a * v - b * v - b - c * v - c + v + 2)) == 0 for poly in basis)
        assert any(sp.factor(poly - (c - v) * (b * v + b + c * v + c - v - 2)) == 0 for poly in basis)
    print("CRIT-INV s6/s7 observed supports reduce to the d=f=1 high survivor family")


def check_high_strip_observed() -> None:
    """Observed high-positive critical supports force the certified high strip."""

    cases = {
        "s4": ("a1", "b1", "d1", "s1", "s2", "s5", "s6", "s7"),
        "s7": ("a1", "b1", "d1", "s1", "s2", "s4", "s5", "s6"),
    }
    for cap, labels in cases.items():
        basis = groebner_basis(cap, labels)
        assert_contains(
            basis,
            {
                a - 1,
                b - 1,
                c - v,
                d - 1,
                e - v,
            },
            f"high strip {cap}",
        )
        # On either selected capacity face, these equations give
        # x=(M-v)/(1+v)=f, so this is the full certified high strip.
        M = CAPS[cap]
        x = sp.factor((M - v) / q)
        assert sp.factor(x.subs({a: 1, b: 1, c: v, d: 1, e: v}) - f) == 0
    print("CRIT-INV high-positive observed supports reduce to a=b=d=1, c=e=v, x=f")


def main() -> None:
    check_seven_tight_observed()
    check_s6s7_high_observed()
    check_high_strip_observed()
    print("PASS y=1,u=1 observed capacity-critical inventory reduces to exact closed families")


if __name__ == "__main__":
    main()
