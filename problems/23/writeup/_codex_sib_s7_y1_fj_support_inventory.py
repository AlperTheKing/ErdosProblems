"""Exact rank inventory for observed y=1 SIB-S7 support systems.

This is not a closure certificate.  It converts the observed active-support
families into explicit algebraic systems on the y=1 variables and checks the
Jacobian rank at rational generic points on the corresponding exact family.
The output is meant to guide the next FJ/Sturm coverage certificate.
"""

from __future__ import annotations

import sympy as sp


a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v", positive=True)
VARS = (a, b, c, d, e, f, x, u, v)

m = x * u + x * v + v
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
    "s3": b + c - x - 1,
    "s4": Y - m,
    "s5": a * e + b * f + c * f - m,
    "s6": a * c + d * f + e * f - m,
    "s7": a * e + d * f + e * f - m,
}

BRANCH_EQ = {
    "s2": SLACKS["s2"],
    "s3": SLACKS["s3"],
    "u1": SLACKS["u1"],
    "xq": x - u - v,
}

SUPPORTS = [
    {
        "name": "ALL_TIGHT",
        "branch": "u1",
        "cap": "s4",
        "active": ("b1", "d1", "f1", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "u1"),
        "sample": {a: sp.Rational(5, 2), b: 1, c: 2, d: 1, e: 2, f: 1, x: 2, u: 1, v: 2},
        "rank": 8,
    },
    {
        "name": "HIGH_A",
        "branch": "u1",
        "cap": "s4",
        "active": ("a1", "b1", "d1", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "u1"),
        "sample": {a: 1, b: 1, c: 2, d: 1, e: 2, f: 2, x: 2, u: 1, v: 2},
        "rank": 8,
    },
    {
        "name": "XQ_A",
        "branch": "xq",
        "cap": "s4",
        "active": ("f1", "s3", "s4", "s5", "s6", "s7", "u1"),
        "sample": {a: sp.Rational(7, 2), b: 2, c: 2, d: 2, e: 2, f: 1, x: 3, u: 1, v: 2},
        "rank": 7,
    },
    {
        "name": "XQ_B",
        "branch": "xq",
        "cap": "s6",
        "active": ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1"),
        "sample": {a: 4, b: 2, c: 2, d: 1, e: 2, f: 1, x: 3, u: 1, v: 2},
        "rank": 8,
    },
    {
        "name": "U1_S7_HIGH",
        "branch": "u1",
        "cap": "s7",
        "active": ("a1", "c1", "d1", "e1", "f1", "s1", "s2", "s6", "s7", "u1", "v1", "x1"),
        "sample": {a: 1, b: 3, c: 1, d: 1, e: 1, f: 1, x: 1, u: 1, v: 1},
        "rank": 8,
    },
    {
        "name": "XQ_S5_HIGH",
        "branch": "xq",
        "cap": "s5",
        "active": ("a1", "s1", "s3", "s4", "s5", "s6", "s7", "u1"),
        "sample": {a: 1, b: 2, c: 2, d: 2, e: 2, f: sp.Rational(9, 4), x: 3, u: 1, v: 2},
        "rank": 8,
    },
    {
        "name": "ALL_ONES",
        "branch": "u1",
        "cap": "s4",
        "active": ("a1", "b1", "c1", "d1", "e1", "f1", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "u1", "v1", "x1"),
        "sample": {a: 1, b: 1, c: 1, d: 1, e: 1, f: 1, x: 1, u: 1, v: 1},
        "rank": 9,
    },
]


def unique_equations(row: dict) -> list[sp.Expr]:
    exprs = [BRANCH_EQ[row["branch"]], SLACKS[row["cap"]]]
    exprs.extend(SLACKS[name] for name in row["active"])
    out: list[sp.Expr] = []
    seen: set[str] = set()
    for expr in exprs:
        key = sp.srepr(sp.factor(expr))
        if key not in seen:
            out.append(sp.factor(expr))
            seen.add(key)
    return out


def main() -> None:
    for row in SUPPORTS:
        eqs = unique_equations(row)
        sample = row["sample"]
        for expr in eqs:
            assert sp.factor(expr.subs(sample)) == 0, (row["name"], expr)
        J = sp.Matrix([[sp.diff(expr, var) for var in VARS] for expr in eqs])
        rank = J.subs(sample).rank()
        dim = len(VARS) - rank
        assert rank == row["rank"], (row["name"], rank, row["rank"])
        print(f"SUPPORT {row['name']}: equations={len(eqs)} rank={rank} local_dim={dim}")
    print("PASS y=1 observed FJ support inventory ranks are exact at rational family points")


if __name__ == "__main__":
    main()
