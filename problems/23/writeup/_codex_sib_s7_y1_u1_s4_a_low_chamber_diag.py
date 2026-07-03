"""Diagnostic re-emission for the low y=1,u=1,s4,a=1 chamber.

This file is intentionally separate from the certificate script.  It prints
before expensive SymPy work and emits the first exact Bernstein coefficient to
a sidecar text file for audit.
"""

from __future__ import annotations

from pathlib import Path

import sympy as sp


X, H, R, S, D, E = sp.symbols("X H R S D E", nonnegative=True)


def phi_expr() -> sp.Expr:
    V = X + H
    t = X + R * H
    q = S * t

    a = u = y = sp.Integer(1)
    x = 1 + X
    v = 1 + V
    b = 1 + t - q
    c = 1 + q
    d = 1 + D
    e = 1 + V + E
    f = sp.cancel((x * (1 + v) + v - c) / (b + c))

    m = x * (1 + v) + v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f

    return 2 * (n**2 - 25 * m) - 75 * (
        x * (u + v) * A / Z + y * v * B / (e * Y)
        - (a + b + c + d + e + f)
    )


def first_bernstein_coeff(poly: sp.Expr, bounded: tuple[sp.Symbol, ...]) -> sp.Expr:
    coeff = poly
    for var in bounded:
        coeff = sp.Poly(coeff, var).coeff_monomial(var**0)
    return sp.factor(coeff)


def main() -> None:
    print("DIAG low chamber start", flush=True)
    print(f"DIAG sympy_version={sp.__version__}", flush=True)
    phi = phi_expr()
    print("DIAG phi constructed", flush=True)
    numerator, denominator = sp.together(phi).as_numer_denom()
    print(f"DIAG numerator_ready denominator_zero={denominator == 0}", flush=True)

    first = first_bernstein_coeff(numerator, (R, S))
    poly = sp.Poly(first, X, H, D, E)
    coeffs = poly.coeffs()
    min_coeff = min(coeffs)
    neg_count = sum(1 for c in coeffs if c < 0)

    out = Path("tmp") / "codex_low_chamber_first_bernstein_coeff.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(sp.sstr(first), encoding="utf-8")

    print(f"DIAG first_coeff_terms={len(coeffs)}", flush=True)
    print(f"DIAG first_coeff_min={min_coeff}", flush=True)
    print(f"DIAG first_coeff_negative_count={neg_count}", flush=True)
    print(f"DIAG first_coeff_file={out}", flush=True)
    print("DIAG low chamber done", flush=True)


if __name__ == "__main__":
    main()
