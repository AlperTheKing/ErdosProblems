#!/usr/bin/env python3
"""Exact monomial quotient/remainder diagnostic for EQ-ODL1 face splits.

This is a scaffold for the approved face-split certificate shape.  It does not
claim nonnegativity of either part; it only computes an exact identity

    target = remainder + dominant_generator * quotient

in the ordinary monomial basis under lexicographic term order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "problems" / "23" / "writeup"))

import _codex_eq_odl1_rung2_charts as charts  # noqa: E402


Exp = tuple[int, ...]
PolyDict = dict[Exp, Fraction]


def frac_from_sympy(value: sp.Expr) -> Fraction:
    q = sp.Rational(value)
    return Fraction(int(q.p), int(q.q))


def fmt_frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def clean(poly: PolyDict) -> PolyDict:
    return {exp: coeff for exp, coeff in poly.items() if coeff}


def poly_obj(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> sp.Poly:
    return sp.Poly(sp.expand(expr), *vars_, domain=sp.QQ)


def poly_dict_from_poly(poly: sp.Poly) -> PolyDict:
    out: PolyDict = {}
    for exp_raw, coeff_raw in poly.terms():
        coeff = frac_from_sympy(coeff_raw)
        if coeff:
            out[tuple(int(x) for x in exp_raw)] = coeff
    return out


def poly_dict(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> PolyDict:
    return poly_dict_from_poly(poly_obj(expr, vars_))


def leading_term(poly: PolyDict) -> tuple[Exp, Fraction]:
    exp = max(poly)
    return exp, poly[exp]


def exp_sub(a: Exp, b: Exp) -> Exp:
    return tuple(x - y for x, y in zip(a, b))


def exp_add(a: Exp, b: Exp) -> Exp:
    return tuple(x + y for x, y in zip(a, b))


def divisible(a: Exp, b: Exp) -> bool:
    return all(x >= y for x, y in zip(a, b))


def subtract_shifted(poly: PolyDict, divisor: PolyDict, shift: Exp, scale: Fraction) -> None:
    for exp, coeff in divisor.items():
        out_exp = exp_add(exp, shift)
        new_coeff = poly.get(out_exp, Fraction(0)) - scale * coeff
        if new_coeff:
            poly[out_exp] = new_coeff
        elif out_exp in poly:
            del poly[out_exp]


def divide_one(target: PolyDict, divisor: PolyDict) -> tuple[PolyDict, PolyDict]:
    if not divisor:
        raise ValueError("empty divisor")
    lead_exp, lead_coeff = leading_term(divisor)
    work = dict(target)
    quotient: PolyDict = {}
    remainder: PolyDict = {}
    while work:
        exp, coeff = leading_term(work)
        del work[exp]
        if divisible(exp, lead_exp):
            shift = exp_sub(exp, lead_exp)
            scale = coeff / lead_coeff
            quotient[shift] = quotient.get(shift, Fraction(0)) + scale
            subtract_shifted(work, divisor, shift, scale)
        else:
            remainder[exp] = remainder.get(exp, Fraction(0)) + coeff
    return clean(quotient), clean(remainder)


def multiply(a: PolyDict, b: PolyDict) -> PolyDict:
    out: PolyDict = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            exp = exp_add(ea, eb)
            out[exp] = out.get(exp, Fraction(0)) + ca * cb
    return clean(out)


def add(a: PolyDict, b: PolyDict) -> PolyDict:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) + coeff
        if not out[exp]:
            del out[exp]
    return out


def subtract(a: PolyDict, b: PolyDict) -> PolyDict:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) - coeff
        if not out[exp]:
            del out[exp]
    return out


def sign_summary(poly: PolyDict) -> dict[str, object]:
    coeffs = list(poly.values())
    neg = [c for c in coeffs if c < 0]
    pos = [c for c in coeffs if c > 0]
    return {
        "terms": len(coeffs),
        "positive_terms": len(pos),
        "negative_terms": len(neg),
        "zero_terms": 0,
        "min_coeff": fmt_frac(min(coeffs)) if coeffs else "0",
        "max_coeff": fmt_frac(max(coeffs)) if coeffs else "0",
        "total_degree": max((sum(exp) for exp in poly), default=0),
    }


def encode_terms(poly: PolyDict, limit: int | None) -> list[dict[str, object]]:
    items = sorted(poly.items(), key=lambda item: item[0], reverse=True)
    if limit is not None:
        items = items[:limit]
    return [{"exp": list(exp), "coeff": fmt_frac(coeff)} for exp, coeff in items]


def sha256_jsonable(obj: object) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def run(args: argparse.Namespace) -> dict[str, object]:
    t0 = time.monotonic()
    if args.verbose:
        print("phase=build_chart start", flush=True)
    chart = charts.build_chart(args.chart)
    if args.verbose:
        print(f"phase=build_chart done seconds={time.monotonic() - t0:.3f}", flush=True)
        print("phase=poly target start", flush=True)
    target_poly = poly_obj(chart.target, chart.variables)
    target = poly_dict_from_poly(target_poly)
    if args.verbose:
        print(f"phase=poly target done terms={len(target)} seconds={time.monotonic() - t0:.3f}", flush=True)
        print("phase=poly divisor start", flush=True)
    divisor_poly = poly_obj(chart.generators[args.dominant], chart.variables)
    divisor = poly_dict_from_poly(divisor_poly)
    if args.verbose:
        print(f"phase=poly divisor done terms={len(divisor)} seconds={time.monotonic() - t0:.3f}", flush=True)
        print(f"phase=divide start method={args.method}", flush=True)
    if args.method == "sympy":
        quotient_poly, remainder_poly = sp.div(target_poly, divisor_poly)
        quotient = poly_dict_from_poly(quotient_poly)
        remainder = poly_dict_from_poly(remainder_poly)
    else:
        quotient, remainder = divide_one(target, divisor)
    if args.verbose:
        print(
            f"phase=divide done quotient={len(quotient)} remainder={len(remainder)} "
            f"seconds={time.monotonic() - t0:.3f}",
            flush=True,
        )
        print("phase=recompose start", flush=True)
    recomposed = add(multiply(quotient, divisor), remainder)
    diff = subtract(target, recomposed)
    if args.verbose:
        print(f"phase=recompose done diff={len(diff)} seconds={time.monotonic() - t0:.3f}", flush=True)
    lead_exp, lead_coeff = leading_term(divisor)

    full_terms = None if args.full_terms else args.preview_terms
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_face_split_polydiv_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "variables": [str(v) for v in chart.variables],
        "term_order": "lexicographic on variables as listed",
        "division_method": args.method,
        "leading_exp": list(lead_exp),
        "leading_coeff": fmt_frac(lead_coeff),
        "identity_ok": not diff,
        "diff_summary": sign_summary(diff),
        "target_summary": sign_summary(target),
        "divisor_summary": sign_summary(divisor),
        "quotient_summary": sign_summary(quotient),
        "remainder_summary": sign_summary(remainder),
        "target_terms": encode_terms(target, full_terms),
        "divisor_terms": encode_terms(divisor, full_terms),
        "quotient_terms": encode_terms(quotient, full_terms),
        "remainder_terms": encode_terms(remainder, full_terms),
    }
    out["content_sha256"] = sha256_jsonable({k: v for k, v in out.items() if k != "content_sha256"})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--preview-terms", type=int, default=40)
    ap.add_argument("--full-terms", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--method", choices=("sympy", "python"), default="sympy")
    args = ap.parse_args()
    out = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "chart": out["chart"],
        "dominant": out["dominant"],
        "dominant_name": out["dominant_name"],
        "identity_ok": out["identity_ok"],
        "leading_exp": out["leading_exp"],
        "leading_coeff": out["leading_coeff"],
        "quotient_terms": out["quotient_summary"]["terms"],
        "remainder_terms": out["remainder_summary"]["terms"],
        "out": str(args.out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
