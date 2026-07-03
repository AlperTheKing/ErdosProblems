"""Diagnostic re-emission for the V>=X,q<=V<=t y=1,u=1,s4,a=1 chamber.

This emits the first exact Bernstein coefficient of the segment-boundary
numerator to a sidecar text file, with flushed progress messages.
"""

from __future__ import annotations

from pathlib import Path

import sympy as sp


X, H, R, S, U = sp.symbols("X H R S U", nonnegative=True)


def common_quantities():
    V = X + H
    x = 1 + X
    v = 1 + V
    m = sp.expand(x * (1 + v) + v)
    M3 = sp.expand(m - 3)
    q = S * V
    width = sp.expand(M3 - q - V)
    t = V + R * width
    W = t - V
    h = 2 + t
    c = 1 + q
    C = m - c
    return V, x, v, m, q, t, W, h, c, C


def hand_cleared_numerator(d: sp.Expr, e: sp.Expr) -> sp.Expr:
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    f = C / h
    sum_core = 3 + t + d + e + f
    n = sum_core + x + 2 + v
    z = e * m + d * C
    a_term = m + e + (d + e) * (h + f)
    b_term = m + e * (1 + h + f)
    p_term = m - v
    base = 2 * (n * n - 25 * m) + 75 * sum_core
    return sp.together(base * z * e * m - 75 * p_term * a_term * e * m - 75 * v * b_term * z).as_numer_denom()[0]


def first_bernstein_coeff(poly: sp.Expr, bounded: tuple[sp.Symbol, ...]) -> sp.Expr:
    coeff = poly
    for var in bounded:
        coeff = sp.Poly(coeff, var).coeff_monomial(var**0)
    return sp.factor(coeff)


def main() -> None:
    print("DIAG mid chamber start", flush=True)
    print(f"DIAG sympy_version={sp.__version__}", flush=True)
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    e_seg = 1 + V + U * W
    d_seg = 1 + W - U * W
    print("DIAG segment expressions constructed", flush=True)
    numerator = hand_cleared_numerator(d_seg, e_seg)
    print("DIAG segment numerator_ready", flush=True)

    first = first_bernstein_coeff(numerator, (R, S, U))
    poly = sp.Poly(first, X, H)
    coeffs = poly.coeffs()
    min_coeff = min(coeffs)
    neg_count = sum(1 for c in coeffs if c < 0)

    out = Path("tmp") / "codex_mid_chamber_first_bernstein_coeff.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(sp.sstr(first), encoding="utf-8")

    print(f"DIAG first_coeff_terms={len(coeffs)}", flush=True)
    print(f"DIAG first_coeff_min={min_coeff}", flush=True)
    print(f"DIAG first_coeff_negative_count={neg_count}", flush=True)
    print(f"DIAG first_coeff_file={out}", flush=True)
    print("DIAG mid chamber done", flush=True)


if __name__ == "__main__":
    main()
