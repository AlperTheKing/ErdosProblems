"""Compact Fritz-John gate scaffold for the sibling S7 atom.

This builds the normalized compact S7 polynomials described in
`C5_HOM_SHARP_BRANCH_REDUCTION_CODEX.md`.  It does not yet solve the real
feasibility systems.  It is a reproducible exact scaffold for the next gate:
enumerating active sets, stationarity equations, and algebraic degrees.
"""

from __future__ import annotations

from itertools import combinations
from math import comb

import sympy as sp


def build() -> tuple[list[sp.Symbol], sp.Symbol, sp.Expr, list[tuple[str, sp.Expr]]]:
    a, b, c, d, e, f, x, y, u, v, th = sp.symbols("a b c d e f x y u v theta")
    vars = [a, b, c, d, e, f, x, y, u, v, th]
    m = x * u + x * v + y * v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    P = sp.expand(2 * e * Y * Z * (1 - 25 * m) - 75 * th * (e * Y * x * (u + v) * A + Z * y * v * B - e * Y * Z * (a + b + c + d + e + f)))
    H = a + b + c + d + e + f + x + y + u + v - 1
    ineqs: list[tuple[str, sp.Expr]] = [
        ("theta", th),
        ("a_lb", a - th),
        ("b_lb", b - th),
        ("c_lb", c - th),
        ("d_lb", d - th),
        ("e_lb", e - th),
        ("f_lb", f - th),
        ("x_lb", x - th),
        ("y_lb", y - th),
        ("u_lb", u - th),
        ("v_lb", v - th),
        ("s1", e - v),
        ("s2", d + e - u - v),
        ("s3", b + c - x - y),
        ("s4", Y - m),
        ("s5", a * e + b * f + c * f - m),
        ("s6", a * c + d * f + e * f - m),
        ("s7", a * e + d * f + e * f - m),
    ]
    return vars, H, P, ineqs


def active_set_count(n: int = 18, max_size: int = 11) -> int:
    return sum(comb(n, k) for k in range(max_size + 1))


def central_active_names() -> set[str]:
    # Old central curve: b=d=f=u=y=theta, c=e=x=v, and all seven S7 slacks tight.
    return {"b_lb", "d_lb", "f_lb", "u_lb", "y_lb", "s1", "s2", "s3", "s4", "s5", "s6", "s7"}


def main() -> None:
    vars, H, P, ineqs = build()
    print("variables", [str(v) for v in vars])
    print("H_degree", sp.Poly(H, *vars).total_degree())
    print("P_degree", sp.Poly(P, *vars).total_degree(), "P_terms", len(sp.Poly(P, *vars).terms()))
    print("ineq_count", len(ineqs))
    for name, g in ineqs:
        poly = sp.Poly(g, *vars)
        print(name, "degree", poly.total_degree(), "terms", len(poly.terms()))
    print("active_sets_le_11", active_set_count())
    print("central_active_size", len(central_active_names()))
    print("central_active_names", sorted(central_active_names()))

    # Show the number of stationarity equations and multiplier variables for
    # representative active set sizes.
    for k in [0, 1, 5, 10, 11]:
        print("FJ_size", k, "equations", len(vars) + 3 + k, "multipliers", k + 2)

    # One lightweight construction check: build stationarity for the central
    # active set and report degrees.
    active = [item for item in ineqs if item[0] in central_active_names()]
    lam0 = sp.symbols("lambda0")
    mu = sp.symbols("mu")
    lams = sp.symbols(" ".join(f"lam_{name}" for name, _ in active))
    stat = []
    for z in vars:
        expr = lam0 * sp.diff(P, z) + mu * sp.diff(H, z)
        for lam, (_name, g) in zip(lams, active):
            expr -= lam * sp.diff(g, z)
        stat.append(sp.expand(expr))
    all_vars = vars + [lam0, mu] + list(lams)
    degs = [sp.Poly(eq, *all_vars).total_degree() for eq in stat]
    print("central_FJ_stationarity_degrees", degs)


if __name__ == "__main__":
    main()
