#!/usr/bin/env python3
"""EQ CERT-2 LP-2 fallback with quadratic-module F_i F_j generators."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from scipy.optimize import linprog

import _codex_eq_cert2_odl_lp as lp1

xs = lp1.xs
F = lp1.F


def build_generators(target: sp.Expr, f_degree: int, product_degree: int):
    gens = []
    for j, f in enumerate(F, start=1):
        for mon in lp1.monomials(f_degree):
            gens.append({"kind": "F", "i": j, "j": 0, "mon": mon, "poly": sp.expand(f * mon)})
    if product_degree >= 0:
        mons = lp1.monomials(product_degree)
        for i, fi in enumerate(F, start=1):
            for j, fj in enumerate(F[i - 1 :], start=i):
                for mon in mons:
                    gens.append({"kind": "FF", "i": i, "j": j, "mon": mon, "poly": sp.expand(fi * fj * mon)})
    return gens


def exact_check(target: sp.Expr, gens, coeffs: list[Fraction]):
    expr = target
    nz = []
    for g, c in zip(gens, coeffs):
        if c:
            nz.append({"kind": g["kind"], "i": g["i"], "j": g["j"], "monomial": str(g["mon"]), "coeff": str(c)})
        expr -= sp.Rational(c.numerator, c.denominator) * g["poly"]
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
        "nonzero_generators": nz,
    }


def solve(target: sp.Expr, f_degree: int, product_degree: int, max_denominators: list[int], objective: str):
    gens = build_generators(target, f_degree, product_degree)
    base = lp1.coeff_map(target)
    term_maps = [lp1.coeff_map(g["poly"]) for g in gens]
    monom_set = sorted(set(base) | set().union(*(set(mp) for mp in term_maps)))
    print("f_degree", f_degree, "product_degree", product_degree, "vars", len(gens), "constraints", len(monom_set), flush=True)
    a_ub = []
    b_ub = []
    for monom in monom_set:
        a_ub.append([float(mp.get(monom, Fraction(0))) for mp in term_maps])
        b_ub.append(float(base.get(monom, Fraction(0))))
    c = [0.0 if objective == "zero" else 1.0] * len(gens)
    res = linprog(c=c, A_ub=a_ub, b_ub=b_ub, bounds=[(0, None)] * len(gens), method="highs")
    out = {
        "f_degree": f_degree,
        "product_degree": product_degree,
        "variables": len(gens),
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
        ok, check = exact_check(target, gens, coeffs)
        print("try", max_den, "ok", ok, "min", check["residual_min_coeff"], "neg", check["negative_terms"][:1], flush=True)
        if ok:
            out.update({
                "exact_ok": True,
                "max_denominator": max_den,
                "residual_terms": check["residual_terms"],
                "residual_min_coeff": check["residual_min_coeff"],
                "nonzero_generators": check["nonzero_generators"],
            })
            return out
    out["exact_ok"] = False
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f-degree", type=int, default=4)
    ap.add_argument("--product-degree", type=int, default=0)
    ap.add_argument("--max-den", default="10,25,50,100,250,1000,5000,20000")
    ap.add_argument("--objective", choices=["sum", "zero"], default="sum")
    ap.add_argument("--summary", default="tmp/eq_cert2_odl_lp2_summary.json")
    args = ap.parse_args()
    target, meta = lp1.build_target()
    max_denominators = [int(x) for x in args.max_den.split(",") if x.strip()]
    result = solve(target, args.f_degree, args.product_degree, max_denominators, args.objective)
    summary = {"schema": "eq_cert2_odl_lp2_v1", **meta, "lp2": result}
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    if result.get("exact_ok"):
        print("PASS EQ CERT-2 LP-2 exact certificate", args.summary)
    else:
        print("FAIL EQ CERT-2 LP-2 exact certificate", args.summary)
        raise SystemExit(1)


if __name__ == "__main__":
    main()