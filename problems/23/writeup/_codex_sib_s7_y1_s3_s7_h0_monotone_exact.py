"""Exact monotonicity on the H=0 triple face.

This certificate proves that, on the shifted H=0 parametrization,
the cleared numerators of dPhi/dB and dPhi/dR have nonnegative coefficients.
Since the denominators are positive in the feasible domain, Phi is
nondecreasing in B=b-1 and R=c-e. Therefore the H=0 face descends to
the smaller boundary B=R=0.
"""

from __future__ import annotations

from collections import defaultdict

import sympy as sp

from _codex_sib_s7_y1_s3_s7_h0_cone_probe import VARS

PolyDict = dict[tuple[int, ...], int]


def poly_dict(expr: sp.Expr) -> PolyDict:
    return {mon: int(coef) for mon, coef in sp.Poly(sp.expand(expr), *VARS).terms()}


def poly_derivative(poly: PolyDict, idx: int) -> PolyDict:
    out: defaultdict[tuple[int, ...], int] = defaultdict(int)
    for mon, coef in poly.items():
        if mon[idx] == 0:
            continue
        nxt = list(mon)
        nxt[idx] -= 1
        out[tuple(nxt)] += coef * mon[idx]
    return dict(out)


def poly_mul(left: PolyDict, right: PolyDict) -> PolyDict:
    out: defaultdict[tuple[int, ...], int] = defaultdict(int)
    for mon_l, coef_l in left.items():
        for mon_r, coef_r in right.items():
            out[tuple(mon_l[i] + mon_r[i] for i in range(len(VARS)))] += coef_l * coef_r
    return dict(out)


def poly_sub(left: PolyDict, right: PolyDict) -> PolyDict:
    out: defaultdict[tuple[int, ...], int] = defaultdict(int)
    for mon, coef in left.items():
        out[mon] += coef
    for mon, coef in right.items():
        out[mon] -= coef
    return {mon: coef for mon, coef in out.items() if coef}


def coeffs_nonnegative(poly: PolyDict) -> bool:
    bad = [(mon, coef) for mon, coef in poly.items() if coef < 0]
    if bad:
        print(f"BAD first={bad[0]} bad_count={len(bad)} terms={len(poly)}")
        return False
    print(f"OK terms={len(poly)}")
    return True


def build_phi() -> sp.Expr:
    A, B, F, V, S, R = VARS
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
    return 2 * (n * n - 25 * m) - 75 * (x * (u + v) * aa / z + v * bb / (e * yy) - core)


def main() -> None:
    _A, B, _F, _V, _S, R = VARS
    phi = build_phi()
    num_expr, den_expr = sp.together(phi).as_numer_denom()
    num = poly_dict(num_expr)
    den = poly_dict(den_expr)
    assert coeffs_nonnegative(den)
    print(f"H0-MONO-EXACT phi_num_terms={len(num)} phi_den_terms={len(den)}")

    for name, var in (("B", B), ("R", R)):
        idx = VARS.index(var)
        der_num = poly_sub(poly_mul(poly_derivative(num, idx), den), poly_mul(num, poly_derivative(den, idx)))
        print(f"H0-MONO-EXACT d/d{name}")
        assert coeffs_nonnegative(der_num)
    print("PASS H0 exact monotonicity in B=b-1 and R=c-e")


if __name__ == "__main__":
    main()
