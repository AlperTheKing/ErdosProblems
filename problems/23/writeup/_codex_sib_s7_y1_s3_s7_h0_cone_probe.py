"""LP cone probe for the H=0 triple face.

Tries to certify the cleared H=0 Phi numerator as

    nonnegative_poly + U1_num * nonnegative_poly + S2_num * nonnegative_poly,

where U1_num and S2_num are the remaining feasibility numerators on the
H=0 face.  This is a floating LP search only, intended to identify whether
the face has a simple slack-multiplier certificate.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import sympy as sp
from scipy.optimize import linprog


VARS = sp.symbols("A B F V S R", nonnegative=True)
A, B, F, V, S, R = VARS


def poly_terms(expr: sp.Expr) -> dict[tuple[int, ...], int]:
    return {mon: int(coef) for mon, coef in sp.Poly(sp.expand(expr), *VARS).terms()}


def add_terms(dst: dict[tuple[int, ...], int], src: dict[tuple[int, ...], int], shift: tuple[int, ...]) -> None:
    for mon, coef in src.items():
        key = tuple(mon[i] + shift[i] for i in range(len(VARS)))
        dst[key] = dst.get(key, 0) + coef


def monomials_upto(max_deg: int) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []

    def rec(pos: int, remaining: int, cur: list[int]) -> None:
        if pos == len(VARS):
            out.append(tuple(cur))
            return
        for k in range(remaining + 1):
            cur.append(k)
            rec(pos + 1, remaining - k, cur)
            cur.pop()

    rec(0, max_deg, [])
    return out


def build_face() -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    a = 1 + A
    b = 1 + B
    f = 1 + F
    v = 1 + V
    e = v + S
    c = e + R
    d = b + R
    x = b + c - 1
    u = (a * e + b * f + c * f - v * (b + c)) / (b + c - 1)

    core = a + b + c + d + e + f
    n = core + x + 1 + u + v
    m = x * u + x * v + v
    yy = a * c + b * f + c * f
    z = e * yy + d * f * (b + c)
    aa = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    bb = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    phi = 2 * (n * n - 25 * m) - 75 * (x * (u + v) * aa / z + v * bb / (e * yy) - core)

    num = sp.together(phi).as_numer_denom()[0]
    u1_num = sp.together(u - 1).as_numer_denom()[0]
    s2_num = sp.together(d + e - u - v).as_numer_denom()[0]
    return sp.expand(num), sp.expand(u1_num), sp.expand(s2_num)


def main() -> None:
    target_expr, u1_expr, s2_expr = build_face()
    target = poly_terms(target_expr)
    u1 = poly_terms(u1_expr)
    s2 = poly_terms(s2_expr)

    max_deg = max(sum(mon) for mon in target)
    u1_deg = max(sum(mon) for mon in u1)
    s2_deg = max(sum(mon) for mon in s2)
    print(f"H0-CONE target_terms={len(target)} max_deg={max_deg} u1_terms={len(u1)} u1_deg={u1_deg} s2_terms={len(s2)} s2_deg={s2_deg}")

    cols: list[dict[tuple[int, ...], int]] = []
    labels: list[tuple[str, tuple[int, ...]]] = []

    # Residual nonnegative coefficient columns.
    for mon in sorted(target):
        cols.append({mon: 1})
        labels.append(("res", mon))

    for name, slack, deg in (("u1", u1, u1_deg), ("s2", s2, s2_deg)):
        for shift in monomials_upto(max_deg - deg):
            col: dict[tuple[int, ...], int] = {}
            add_terms(col, slack, shift)
            cols.append(col)
            labels.append((name, shift))

    universe = sorted(set(target) | {mon for col in cols for mon in col})
    row_index = {mon: i for i, mon in enumerate(universe)}
    aeq = np.zeros((len(universe), len(cols)), dtype=float)
    for j, col in enumerate(cols):
        for mon, coef in col.items():
            aeq[row_index[mon], j] = coef
    beq = np.array([target.get(mon, 0) for mon in universe], dtype=float)

    print(f"H0-CONE rows={aeq.shape[0]} cols={aeq.shape[1]}")
    res = linprog(np.zeros(len(cols)), A_eq=aeq, b_eq=beq, bounds=(0, None), method="highs")
    if not res.success:
        print(f"FAIL H0-CONE LP {res.message}")
        return

    active = [(labels[i], res.x[i]) for i in range(len(cols)) if res.x[i] > 1e-8]
    print(f"PASS H0-CONE LP feasible active={len(active)}")
    print("H0-CONE first_active=" + repr(active[:20]))


if __name__ == "__main__":
    main()
