"""Sparse LP cone for constrained H0 derivative monotonicity.

For var in {B,R}, this tries to express the derivative numerator as

    nonnegative_poly + U1_num * nonnegative_poly + S2_num * nonnegative_poly.

The matrix is built sparse; this is a search gate, not yet an exact
rational certificate.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from _codex_sib_s7_y1_s3_s7_h0_cone_probe import VARS, build_face, monomials_upto, poly_terms
from _codex_sib_s7_y1_s3_s7_h0_monotone_exact import (
    poly_derivative,
    poly_dict,
    poly_mul,
    poly_sub,
)


def add_terms(dst: dict[tuple[int, ...], int], src: dict[tuple[int, ...], int], shift: tuple[int, ...]) -> None:
    for mon, coef in src.items():
        key = tuple(mon[i] + shift[i] for i in range(len(VARS)))
        dst[key] = dst.get(key, 0) + coef


def solve_for(var_name: str) -> None:
    target_expr, u1_expr, s2_expr = build_face()
    # Need the true rational numerator/denominator, not just Phi numerator from build_face.
    # Reuse monotone_exact's build_phi indirectly would duplicate work; target_expr is Phi numerator.
    # Importing build_phi here would create a circular import, so reconstruct via monotone_exact.
    from _codex_sib_s7_y1_s3_s7_h0_monotone_exact import build_phi

    phi = build_phi()
    num_expr, den_expr = __import__("sympy").together(phi).as_numer_denom()
    num = poly_dict(num_expr)
    den = poly_dict(den_expr)
    idx = [str(v) for v in VARS].index(var_name)
    target = poly_sub(poly_mul(poly_derivative(num, idx), den), poly_mul(num, poly_derivative(den, idx)))
    u1 = poly_terms(u1_expr)
    s2 = poly_terms(s2_expr)

    max_deg = max(sum(mon) for mon in target)
    print(f"H0-DER-CONE {var_name}: target_terms={len(target)} max_deg={max_deg}")

    cols: list[dict[tuple[int, ...], int]] = []
    labels: list[tuple[str, tuple[int, ...]]] = []
    for mon in sorted(target):
        cols.append({mon: 1})
        labels.append(("res", mon))
    for name, slack in (("u1", u1), ("s2", s2)):
        deg = max(sum(mon) for mon in slack)
        for shift in monomials_upto(max_deg - deg):
            col: dict[tuple[int, ...], int] = {}
            add_terms(col, slack, shift)
            cols.append(col)
            labels.append((name, shift))

    universe = sorted(set(target) | {mon for col in cols for mon in col})
    row_index = {mon: i for i, mon in enumerate(universe)}
    rows: list[int] = []
    col_ids: list[int] = []
    data: list[float] = []
    for j, col in enumerate(cols):
        for mon, coef in col.items():
            rows.append(row_index[mon])
            col_ids.append(j)
            data.append(float(coef))
    aeq = coo_matrix((data, (rows, col_ids)), shape=(len(universe), len(cols))).tocsr()
    beq = np.array([target.get(mon, 0) for mon in universe], dtype=float)
    print(f"H0-DER-CONE {var_name}: rows={aeq.shape[0]} cols={aeq.shape[1]} nnz={aeq.nnz}")
    res = linprog(np.zeros(len(cols)), A_eq=aeq, b_eq=beq, bounds=(0, None), method="highs")
    if not res.success:
        print(f"FAIL H0-DER-CONE {var_name}: {res.message}")
        return
    active = sum(1 for x in res.x if x > 1e-8)
    print(f"PASS H0-DER-CONE {var_name}: active={active}")


def main() -> None:
    solve_for("B")
    solve_for("R")


if __name__ == "__main__":
    main()
