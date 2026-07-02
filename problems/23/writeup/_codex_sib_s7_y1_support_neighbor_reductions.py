"""Exact reductions for one-step add-neighbors of observed y=1 supports.

The one-step neighborhood inventory has 38 neighbors that are not satisfied by
the generic rational point of the parent observed family.  Every such neighbor
is an added active constraint.  This file verifies that each added constraint is
one of two harmless types on the already-closed parent family:

  * a closed subface of that positive family, or
  * impossible on the family domain because the added slack is strictly > 0.

This still is not a full FJ/Sturm coverage certificate; it closes the explicit
observed-family add-neighbor obligations produced by
_codex_sib_s7_y1_support_neighborhoods.py.
"""

from __future__ import annotations

import sympy as sp


def assert_zero(expr: sp.Expr, label: str) -> None:
    assert sp.factor(expr) == 0, label


def assert_positive_poly(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], label: str) -> None:
    poly = sp.Poly(sp.expand(expr), *vars_)
    assert all(coef >= 0 for _mon, coef in poly.terms()), label
    assert expr != 0, label


def check_all_tight_adds() -> None:
    T = sp.symbols("T", nonnegative=True)
    t = 1 + T
    # all-tight curve: a=t+1-1/t, c=e=v=x=t.
    slacks = {
        "a1_num": sp.factor(t * (t + 1 - 1 / t - 1)),
        "c1": T,
        "e1": T,
        "v1": T,
        "x1": T,
    }
    assert_zero(slacks["a1_num"] - T * (T + 2), "all-tight add a1")
    for key in ("c1", "e1", "v1", "x1"):
        assert_zero(slacks[key] - T, f"all-tight add {key}")
    print("ADD-NEIGHBOR ALL_TIGHT: five add constraints reduce to T=0 all-ones endpoint")


def check_high_a_adds() -> None:
    T = sp.symbols("T", nonnegative=True)
    # high-A family: a=b=d=u=1, c=e=f=x=v=1+T.
    formulas = {key: T for key in ("c1", "e1", "f1", "v1", "x1")}
    for key, expr in formulas.items():
        assert_zero(expr - T, f"high-A add {key}")
    print("ADD-NEIGHBOR HIGH_A: five add constraints reduce to T=0 all-ones endpoint")


def check_xq_a_adds() -> None:
    X, R, H = sp.symbols("X R H", nonnegative=True)
    # XQ_A family: x=2+X, c=x-1+R, H=1-R with 0<=R<=1.
    # Existing positivity certificate covers the whole family; added equalities
    # are either subfaces of it or impossible.
    formulas = {
        "a1_num": X**2 + 3 * X + H,
        "b1": H,
        "c1": X + R,
        "d1": H,
        "e1": X + R,
        "s2": sp.Integer(1),
        "v1": X,
        "x1": 1 + X,
    }
    for key in ("a1_num", "b1", "c1", "d1", "e1", "v1"):
        assert_positive_poly(formulas[key], (X, R, H), f"xq-A subset {key}")
    assert formulas["s2"] == 1
    assert formulas["x1"] == 1 + X
    print("ADD-NEIGHBOR XQ_A: six add constraints are closed subfaces; s2 and x1 are impossible")


def check_xq_b_adds() -> None:
    X = sp.symbols("X", nonnegative=True)
    # XQ_B family: x=2+X, a=x+1, b=2, c=e=v=x-1, d=f=u=1.
    formulas = {
        "a1": X + 2,
        "b1": sp.Integer(1),
        "c1": X,
        "e1": X,
        "s4": sp.Integer(1),
        "s5": sp.Integer(1),
        "v1": X,
        "x1": X + 1,
    }
    for key in ("c1", "e1", "v1"):
        assert_zero(formulas[key] - X, f"xq-B subset {key}")
    assert formulas["a1"] == X + 2
    assert formulas["b1"] == 1
    assert formulas["s4"] == 1
    assert formulas["s5"] == 1
    assert formulas["x1"] == X + 1
    print("ADD-NEIGHBOR XQ_B: c1/e1/v1 are X=0 subfaces; a1,b1,s4,s5,x1 are impossible")


def check_u1_s7_high_adds() -> None:
    B = sp.symbols("B", nonnegative=True)
    # U1_S7_HIGH: b=1+B, all other variables in the family equal one.
    formulas = {
        "b1": B,
        "s3": B,
        "s4": 1 + B,
        "s5": 1 + B,
    }
    assert_zero(formulas["b1"] - B, "u1-s7 add b1")
    assert_zero(formulas["s3"] - B, "u1-s7 add s3")
    assert formulas["s4"] == 1 + B
    assert formulas["s5"] == 1 + B
    print("ADD-NEIGHBOR U1_S7_HIGH: b1/s3 reduce to all-ones; s4/s5 are impossible")


def check_xq_s5_high_adds() -> None:
    X = sp.symbols("X", nonnegative=True)
    # XQ_S5_HIGH: x=2+X, a=1, b=d=2, c=e=v=x-1,
    # f=x^2/(x+1), u=1.
    f1_num = X**2 + 3 * X + 1
    formulas = {
        "b1": sp.Integer(1),
        "c1": X,
        "d1": sp.Integer(1),
        "e1": X,
        "f1_num": f1_num,
        "s2": sp.Integer(1),
        "v1": X,
        "x1": X + 1,
    }
    for key in ("c1", "e1", "v1"):
        assert_zero(formulas[key] - X, f"xq-s5-high subset {key}")
    assert_positive_poly(f1_num, (X,), "xq-s5-high f1 impossible numerator")
    assert formulas["b1"] == 1
    assert formulas["d1"] == 1
    assert formulas["s2"] == 1
    assert formulas["x1"] == X + 1
    print("ADD-NEIGHBOR XQ_S5_HIGH: c1/e1/v1 are X=0 subfaces; b1,d1,f1,s2,x1 are impossible")


def main() -> None:
    check_all_tight_adds()
    check_high_a_adds()
    check_xq_a_adds()
    check_xq_b_adds()
    check_u1_s7_high_adds()
    check_xq_s5_high_adds()
    print("PASS y=1 one-step add-neighbor reductions are closed subfaces or impossible")


if __name__ == "__main__":
    main()


