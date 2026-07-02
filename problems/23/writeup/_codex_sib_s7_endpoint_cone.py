"""Coefficient-cone probes for fixed S7 endpoint leaves.

Given a leaf, try to certify numerator >= 0 as

    numerator = nonnegative polynomial
              + sum_j nonnegative polynomial_j * slack_j

after shifting core variables by 1.  Float LP is only a discovery tool; any
positive result must be rationalized before use.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import sympy as sp
from scipy.optimize import linprog


def monomials(n: int, deg: int) -> list[tuple[int, ...]]:
    out = []
    for exps in product(range(deg + 1), repeat=n):
        if sum(exps) <= deg:
            out.append(exps)
    return out


def poly_coeff(poly: sp.Expr, vars: tuple[sp.Symbol, ...]) -> dict[tuple[int, ...], int]:
    P = sp.Poly(sp.expand(poly), *vars)
    return {mon: int(coef) for mon, coef in P.terms()}


def build_leaf() -> tuple[dict[tuple[int, ...], int], list[dict[tuple[int, ...], int]], tuple[sp.Symbol, ...]]:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    x = b + c - 1
    y = sp.Integer(1)
    u = d
    v = e
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    C0 = a + b + c + d + e + f
    num = sp.expand((2 * (N * N - 25 * m) + 75 * C0) * e * Y * Z - 75 * (x * (u + v) * A * e * Y + y * v * B * Z))
    slacks = [
        Y - m,
        a * e + b * f + c * f - m,
        a * c + d * f + e * f - m,
        a * e + d * f + e * f - m,
    ]
    shifted = sp.symbols("A B C D E F", nonnegative=True)
    subs = {a: 1 + shifted[0], b: 1 + shifted[1], c: 1 + shifted[2], d: 1 + shifted[3], e: 1 + shifted[4], f: 1 + shifted[5]}
    return poly_coeff(num.subs(subs), shifted), [poly_coeff(s.subs(subs), shifted) for s in slacks], shifted


def add_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def try_degree(deg: int) -> None:
    target, slacks, vars = build_leaf()
    n = len(vars)
    mult_mons = monomials(n, deg)
    all_mons = set(target)
    columns: list[dict[tuple[int, ...], int]] = []
    names: list[str] = []

    # Slack multiplier columns.
    for j, slack in enumerate(slacks):
        for mm in mult_mons:
            col = {add_exp(mm, mon): coef for mon, coef in slack.items()}
            columns.append(col)
            names.append(f"s{j+4}*{mm}")
            all_mons.update(col)

    # Remainder coefficient columns.
    for mon in sorted(all_mons):
        columns.append({mon: 1})
        names.append(f"rem{mon}")

    mons = sorted(all_mons)
    row_index = {m: i for i, m in enumerate(mons)}
    Aeq = np.zeros((len(mons), len(columns)))
    beq = np.zeros(len(mons))
    for mon, coef in target.items():
        beq[row_index[mon]] = coef
    for j, col in enumerate(columns):
        for mon, coef in col.items():
            Aeq[row_index[mon], j] = coef
    res = linprog(np.zeros(len(columns)), A_eq=Aeq, b_eq=beq, bounds=(0, None), method="highs")
    print("deg", deg, "vars", len(columns), "rows", len(mons), "success", res.success, "status", res.message)
    if res.success:
        nz = [(names[i], res.x[i]) for i in range(len(columns)) if res.x[i] > 1e-8 and not names[i].startswith("rem")]
        print("nonzero slack multipliers", len(nz))
        for name, val in nz[:40]:
            print(name, val)


def main() -> None:
    for deg in range(0, 4):
        try_degree(deg)


if __name__ == "__main__":
    main()
