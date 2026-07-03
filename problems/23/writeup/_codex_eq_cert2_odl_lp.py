#!/usr/bin/env python3
"""Search/check EQ CERT-2 ODL cone certificate.

Target from EQ_HEIGHT_LEMMA_GPTPRO.md ADDENDUM 2:

  P_EQ = D_EQ * (2*eta25 - 75*(I_EQ - N))

LP-1 asks for P_EQ = P0 + sum_j F_j * P_j with P0 and all P_j
shifted-coefficient nonnegative after w_i = 1+x_i.  scipy is only a
search oracle; rationalized candidates are accepted only after exact SymPy
coefficient positivity of P0.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

import sympy as sp
from scipy.optimize import linprog

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_weighted_quotient_gate import EQ, b_edges, edges_of, m_edges, shortest_paths

ACTIVE_ROW = (7, 5, 8, 6, 9)
SIDE = "0001111000"

xs = sp.symbols("x0:10", nonnegative=True)
ws = tuple(1 + x for x in xs)
w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = ws

m = w1 * w9 + w2 * w7 + w7 * w9
N = sum(ws)
eta25 = sp.expand(N * N - 25 * m)
F = [
    w5 - w9,
    w6 - w7,
    w3 + w5 - w2 - w9,
    w4 + w6 - w1 - w7,
    w0 * w6 + w3 * w8 + w5 * w8 - m,
    w0 * w5 + w3 * w8 + w5 * w8 - m,
    w0 * w6 + w4 * w8 + w6 * w8 - m,
]


def path_weight(path: tuple[int, ...], weights: tuple[sp.Expr, ...]) -> sp.Expr:
    out = sp.Integer(1)
    for v in path[1:-1]:
        out *= weights[v]
    return out


def row_overlap_expr(row: tuple[int, ...], weights: tuple[sp.Expr, ...], paths_by_bad) -> sp.Expr:
    row_set = set(row)
    total = sp.Integer(0)
    for a, b in sorted(paths_by_bad):
        paths = paths_by_bad[(a, b)]
        denom = sp.Integer(0)
        inner = sp.Integer(0)
        for path in paths:
            wp = path_weight(path, weights)
            denom += wp
            for v in path[1:-1]:
                if v in row_set:
                    inner += wp / weights[v]
        endpoint = sp.Integer(0)
        if a in row_set:
            endpoint += weights[b]
        if b in row_set:
            endpoint += weights[a]
        total += endpoint + weights[a] * weights[b] * inner / denom
    return sp.factor(total)


def eq_denominator(weights: tuple[sp.Expr, ...]) -> sp.Expr:
    w = weights
    A = w[0] * w[6] + w[4] * w[8] + w[6] * w[8]
    B = w[0] * w[5] + w[3] * w[8] + w[5] * w[8]
    C = (
        w[0] * w[5] * w[6]
        + w[3] * w[4] * w[8]
        + w[3] * w[6] * w[8]
        + w[4] * w[5] * w[8]
        + w[5] * w[6] * w[8]
    )
    return sp.factor(w[5] * w[6] * A * B * C)


def build_target() -> tuple[sp.Expr, dict[str, object]]:
    n, edges = edges_of(EQ)
    side = tuple(int(c) for c in SIDE)
    B = b_edges(edges, side)
    M = sorted(m_edges(edges, side))
    if n != 10 or M != [(1, 9), (2, 7), (7, 9)]:
        raise RuntimeError(f"unexpected EQ data: n={n} M={M}")
    paths_by_bad = {edge: shortest_paths(n, B, edge[0], edge[1]) for edge in M}
    I = row_overlap_expr(ACTIVE_ROW, ws, paths_by_bad)
    D = eq_denominator(ws)
    expr = sp.together(D * (2 * eta25 - 75 * (I - N)))
    num, den = expr.as_numer_denom()
    if sp.factor(den) != 1:
        raise RuntimeError(f"D_EQ did not clear denominator: {sp.factor(den)}")
    return sp.expand(num), {
        "graph": EQ,
        "side": SIDE,
        "active_row": list(ACTIVE_ROW),
        "bad_edges": [list(e) for e in M],
        "D_EQ": str(D),
        "I_EQ": str(I),
    }


def monomial_from_exp(exp: tuple[int, ...]) -> sp.Expr:
    mon = sp.Integer(1)
    for x, power in zip(xs, exp):
        if power:
            mon *= x ** power
    return mon


def monomials(max_degree: int) -> list[sp.Expr]:
    out = [sp.Integer(1)]
    for degree in range(1, max_degree + 1):
        for combo in combinations_with_replacement(range(len(xs)), degree):
            exp = [0] * len(xs)
            for i in combo:
                exp[i] += 1
            out.append(monomial_from_exp(tuple(exp)))
    return out


def coeff_map(expr: sp.Expr) -> dict[tuple[int, ...], Fraction]:
    poly = sp.Poly(sp.expand(expr), *xs)
    return {monom: Fraction(int(coeff.p), int(coeff.q)) for monom, coeff in poly.terms()}


def negative_repair_monomials(target: sp.Expr, max_degree: int) -> list[list[sp.Expr]]:
    base = coeff_map(target)
    negative_exps = [exp for exp, coeff in base.items() if coeff < 0]
    out: list[list[sp.Expr]] = []
    for f in F:
        fmap = coeff_map(f)
        candidates: set[tuple[int, ...]] = set()
        for beta in negative_exps:
            for alpha, coeff in fmap.items():
                if coeff >= 0:
                    continue
                gamma = tuple(b - a for b, a in zip(beta, alpha))
                if min(gamma) < 0:
                    continue
                if sum(gamma) <= max_degree:
                    candidates.add(gamma)
        out.append([monomial_from_exp(exp) for exp in sorted(candidates)])
    return out


def exact_check(coeffs: list[Fraction], multiplier_mons_by_f: list[list[sp.Expr]], target: sp.Expr) -> tuple[bool, dict[str, object]]:
    idx = 0
    expr = target
    nz_mult = []
    for j, (f, mons) in enumerate(zip(F, multiplier_mons_by_f), start=1):
        mult = sp.Integer(0)
        for mon in mons:
            c = coeffs[idx]
            if c:
                nz_mult.append({"F": j, "monomial": str(mon), "coeff": str(c)})
            idx += 1
            mult += sp.Rational(c.numerator, c.denominator) * mon
        expr -= f * mult
    poly = sp.Poly(sp.expand(expr), *xs, domain=sp.QQ)
    vals = [Fraction(int(c.p), int(c.q)) for c in poly.coeffs()]
    neg = []
    for monom, coeff in poly.terms():
        q = Fraction(int(coeff.p), int(coeff.q))
        if q < 0:
            neg.append({"monomial": monom, "coeff": str(q)})
            if len(neg) >= 10:
                break
    return not neg, {
        "residual_terms": len(vals),
        "residual_min_coeff": str(min(vals) if vals else Fraction(0)),
        "negative_terms": neg,
        "nonzero_multipliers": nz_mult,
    }


def solve_lp(target: sp.Expr, degrees: list[int], max_denominators: list[int], objective: str, support: str) -> dict[str, object]:
    if len(degrees) != 7:
        raise ValueError("need seven multiplier degree bounds")
    if support == "all":
        multiplier_mons_by_f = [monomials(d) for d in degrees]
    elif support == "negative":
        if len(set(degrees)) != 1:
            raise ValueError("negative support currently expects a uniform degree bound")
        multiplier_mons_by_f = negative_repair_monomials(target, degrees[0])
    else:
        raise ValueError(f"unknown support mode {support!r}")
    base = coeff_map(target)
    term_maps = []
    for f, mons in zip(F, multiplier_mons_by_f):
        for mon in mons:
            term_maps.append(coeff_map(f * mon))
    monom_set = sorted(set(base) | set().union(*(set(mp) for mp in term_maps)))
    print("degrees", degrees, "support", support, "vars", len(term_maps), "constraints", len(monom_set), flush=True)
    a_ub = []
    b_ub = []
    for monom in monom_set:
        a_ub.append([float(mp.get(monom, Fraction(0))) for mp in term_maps])
        b_ub.append(float(base.get(monom, Fraction(0))))
    c = [0.0 if objective == "zero" else 1.0] * len(term_maps)
    res = linprog(c=c, A_ub=a_ub, b_ub=b_ub, bounds=[(0, None)] * len(term_maps), method="highs")
    out = {
        "degrees": degrees,
        "support": support,
        "support_sizes": [len(mons) for mons in multiplier_mons_by_f],
        "variables": len(term_maps),
        "constraints": len(monom_set),
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
    }
    print("LP", res.status, res.message, flush=True)
    if not res.success:
        return out
    raw = res.x
    out["float_nonzero"] = int(sum(1 for x in raw if x > 1e-9))
    print("float_nonzero", out["float_nonzero"], flush=True)
    for max_den in max_denominators:
        coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in raw]
        ok, check = exact_check(coeffs, multiplier_mons_by_f, target)
        print("try", max_den, "ok", ok, "min", check["residual_min_coeff"], "neg", check["negative_terms"][:1], flush=True)
        if ok:
            out.update({
                "exact_ok": True,
                "max_denominator": max_den,
                "residual_terms": check["residual_terms"],
                "residual_min_coeff": check["residual_min_coeff"],
                "nonzero_multipliers": check["nonzero_multipliers"],
            })
            return out
    out["exact_ok"] = False
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--degrees", default="0,0,0,0,0,0,0")
    ap.add_argument("--max-den", default="10,25,50,100,250,1000,5000,20000")
    ap.add_argument("--objective", choices=["sum", "zero"], default="sum")
    ap.add_argument("--support", choices=["all", "negative"], default="all")
    ap.add_argument("--summary", default="tmp/eq_cert2_odl_lp_summary.json")
    ap.add_argument("--stats-only", action="store_true")
    args = ap.parse_args()
    target, meta = build_target()
    poly = sp.Poly(target, *xs, domain=sp.ZZ)
    coeffs = [int(c) for c in poly.coeffs()]
    summary = {
        "schema": "eq_cert2_odl_lp_v1",
        **meta,
        "target_terms": len(coeffs),
        "target_total_degree": poly.total_degree(),
        "target_min_coeff": min(coeffs),
        "target_negative_coeffs": sum(1 for c in coeffs if c < 0),
    }
    print("target terms", summary["target_terms"], "degree", summary["target_total_degree"], "min", summary["target_min_coeff"], "neg", summary["target_negative_coeffs"], flush=True)
    if not args.stats_only:
        degrees = [int(x) for x in args.degrees.split(",") if x.strip()]
        max_denominators = [int(x) for x in args.max_den.split(",") if x.strip()]
        summary["lp"] = solve_lp(target, degrees, max_denominators, args.objective, args.support)
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    if summary.get("lp", {}).get("exact_ok"):
        print("PASS EQ CERT-2 exact LP certificate", args.summary)
    elif args.stats_only:
        print("PASS EQ CERT-2 stats", args.summary)
    else:
        print("FAIL EQ CERT-2 exact LP certificate", args.summary)
        raise SystemExit(1)


if __name__ == "__main__":
    main()