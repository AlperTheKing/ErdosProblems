"""Exact coefficient certificates for S7 s1=0 floor polynomials.

This verifier covers the GPT-Pro REPLY 6/7 floor forms used in the
Branch-A S7 y=1 endpoint work.

Certified exactly, without floats:
  * F4A: C=e, e<=R-1, split by P<=e+1 / P>=e+1.
  * F4B: C=R-1, e>=R-1.
  * F5: same floor target and box as F4A, with M=eP+ux.
  * F6: j=6 gap floor using L6=R-D and T>=R+1+(M-c)/D.
  * F7: j=7 gap floor using L7=(c-e)+(R-D) and T>=R+1+(M-e)/D.

The F6/F7 certificates use a two-stage Bernstein proof over the simplex
    x=1+X, y=1+W-X, 0<=X<=W<=R-2,
with all remaining domain constraints encoded by nonnegative shifts.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import sympy as sp


def poly_stats(poly: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> dict:
    P = sp.Poly(sp.expand(poly), *vars_)
    coeffs = P.coeffs()
    neg = [(mon, coeff) for mon, coeff in zip(P.monoms(), coeffs) if coeff < 0]
    return {
        "terms": len(coeffs),
        "degree": P.total_degree(),
        "min_coeff": str(min(coeffs) if coeffs else 0),
        "negative_coeffs": len(neg),
        "first_negative": [([int(a) for a in mon], str(coeff)) for mon, coeff in neg[:10]],
    }


def aggregate_stats(stats: list[dict]) -> dict:
    bad = [s for s in stats if s["negative_coeffs"]]
    return {
        "controls": len(stats),
        "max_terms": max((s["terms"] for s in stats), default=0),
        "max_degree": max((s["degree"] for s in stats), default=0),
        "min_coeff": str(min((sp.Rational(s["min_coeff"]) for s in stats), default=sp.Integer(0))),
        "negative_controls": len(bad),
        "first_bad_control": bad[0] if bad else None,
    }


def bernstein_controls(poly: sp.Expr, var: sp.Symbol, upper: sp.Expr) -> list[sp.Expr]:
    P = sp.Poly(sp.expand(poly), var)
    n = P.degree()
    coeff = {i: P.nth(i) for i in range(n + 1)}
    out = []
    for k in range(n + 1):
        s = 0
        for i in range(k + 1):
            if coeff[i] != 0:
                s += coeff[i] * sp.Rational(math.comb(k, i), math.comb(n, i)) * upper**i
        out.append(sp.expand(s))
    return out


def build_f4_targets():
    e, u, x, y, R, D = sp.symbols("e u x y R D")
    P = x + y
    q = u + e
    M = e * P + u * x

    def FN(N):
        return 2 * N**2 + 4 * u * N * x / e - 50 * M - 75 * M / e + 75 * D

    def target(C):
        N0 = D + P + q + R + 1 + (M - C) / R
        return sp.expand(e * R**2 * (FN(N0) - 15))

    return target(e), target(R - 1), (e, u, x, y, R, D)


def verify_f4_f5() -> dict:
    F4A, F4B, (e, u, x, y, R, D) = build_f4_targets()
    U, E, X, Y0, p, r, d, s = sp.symbols("U E X Y0 p r d s")

    # F4B full domain: C=R-1, e>=R-1.
    R_B = (1 + X) + (1 + Y0) + r
    subs_B = {
        x: 1 + X,
        y: 1 + Y0,
        R: R_B,
        e: R_B - 1 + s,
        u: 1 + U,
        D: (R_B - 1 + s) + (1 + U) + d,
    }
    stats_B = poly_stats(F4B.subs(subs_B), (U, X, Y0, r, d, s))

    # F4A low subcase: P<=e+1, so e+1=P+p and R=e+1+r.
    e_A_low = (1 + X) + (1 + Y0) - 1 + p
    subs_A_low = {
        x: 1 + X,
        y: 1 + Y0,
        e: e_A_low,
        R: e_A_low + 1 + r,
        u: 1 + U,
        D: e_A_low + (1 + U) + d,
    }
    stats_A_low = poly_stats(F4A.subs(subs_A_low), (U, X, Y0, p, r, d))

    # F4A high subcase: P>=e+1.  It is quadratic in U=u-1 on
    # 0<=U<=X+Y0+r+d induced by q<=D, after D=R+d.
    R_A_high = (1 + E) + 1 + X + Y0 + r
    subs_A_high = {
        e: 1 + E,
        x: 1 + X,
        y: 1 + E + Y0,
        R: R_A_high,
        u: 1 + U,
        D: R_A_high + d,
    }
    Q = sp.Poly(sp.expand(F4A.subs(subs_A_high)), U)
    c0, c1, c2 = list(reversed(Q.all_coeffs()))
    M_bound = X + Y0 + r + d
    B0 = c0
    two_B1 = sp.expand(2 * c0 + c1 * M_bound)
    B2 = sp.expand(c0 + c1 * M_bound + c2 * M_bound * M_bound)
    stats_A_high = {
        "B0": poly_stats(B0, (E, X, Y0, r, d)),
        "two_B1": poly_stats(two_B1, (E, X, Y0, r, d)),
        "B2": poly_stats(B2, (E, X, Y0, r, d)),
    }

    pieces = [stats_B, stats_A_low, *stats_A_high.values()]
    return {
        "F4B_full": stats_B,
        "F4A_full_and_F5_same_floor": True,
        "F4A_low_P_le_e_plus_1": stats_A_low,
        "F4A_high_P_ge_e_plus_1_Bernstein_U": stats_A_high,
        "verdict": "PASS" if all(s["negative_coeffs"] == 0 for s in pieces) else "FAIL",
    }


def f6_target():
    C, E, U, d, L, W, X = sp.symbols("C E U d L W X")
    c = 1 + C
    e = c + E
    u = 1 + U
    x = 1 + X
    y = 1 + W - X
    P = x + y
    q = u + e
    M = e * P + u * x
    D = q + d
    R = D + L
    T = R + 1 + (M - c) / D
    N = T + D + P + q
    Phi = (
        2 * N**2
        + 4 * u * N * x / e
        - 50 * M
        - 75 * M / e
        + 75 * D
        + 75 * T * L / (M + L)
        - 15
    )
    target = sp.together(e * D**2 * (M + L) * Phi).as_numer_denom()[0]
    return target, (C, E, U, d, L), W, X, C + E + U + d + L


def f7_target():
    E, C, U, d, L, W, X = sp.symbols("E C U d L W X")
    e = 1 + E
    c = e + C
    u = 1 + U
    x = 1 + X
    y = 1 + W - X
    P = x + y
    q = u + e
    M = e * P + u * x
    D = q + d
    R = D + L
    gap = C + L
    T = R + 1 + (M - e) / D
    N = T + D + P + q
    Phi = (
        2 * N**2
        + 4 * u * N * x / e
        - 50 * M
        - 75 * M / e
        + 75 * D
        + 75 * T * gap / (M + gap)
        - 15
    )
    target = sp.together(e * D**2 * (M + gap) * Phi).as_numer_denom()[0]
    return target, (E, C, U, d, L), W, X, E + U + d + L


def verify_simplex_gap(builder) -> dict:
    target, base_vars, W, X, W_bound = builder()
    x_controls = bernstein_controls(target, X, W)
    stats = []
    for ctrl in x_controls:
        for w_ctrl in bernstein_controls(ctrl, W, W_bound):
            stats.append(poly_stats(w_ctrl, base_vars))
    agg = aggregate_stats(stats)
    agg["x_degree_controls"] = len(x_controls)
    agg["w_bound"] = str(W_bound)
    agg["verdict"] = "PASS" if agg["negative_controls"] == 0 else "FAIL"
    return agg


def verify() -> dict:
    out = verify_f4_f5()
    out["F6_gap_simplex_Bernstein"] = verify_simplex_gap(f6_target)
    out["F7_gap_simplex_Bernstein"] = verify_simplex_gap(f7_target)
    all_verdicts = [out["verdict"], out["F6_gap_simplex_Bernstein"]["verdict"], out["F7_gap_simplex_Bernstein"]["verdict"]]
    out["verdict"] = "PASS" if all(v == "PASS" for v in all_verdicts) else "FAIL"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", default="")
    args = ap.parse_args()
    out = verify()
    print("VERDICT", out["verdict"])
    for key in ("F4B_full", "F4A_low_P_le_e_plus_1"):
        s = out[key]
        print(key, "terms", s["terms"], "degree", s["degree"], "negative_coeffs", s["negative_coeffs"], "min_coeff", s["min_coeff"])
    for key, s in out["F4A_high_P_ge_e_plus_1_Bernstein_U"].items():
        print("F4A_high", key, "terms", s["terms"], "degree", s["degree"], "negative_coeffs", s["negative_coeffs"], "min_coeff", s["min_coeff"])
    for key in ("F6_gap_simplex_Bernstein", "F7_gap_simplex_Bernstein"):
        s = out[key]
        print(key, "controls", s["controls"], "negative_controls", s["negative_controls"], "max_terms", s["max_terms"], "max_degree", s["max_degree"], "min_coeff", s["min_coeff"])
    if args.summary:
        Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
