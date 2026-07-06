#!/usr/bin/env python3
"""Exact verifier for quotient face-split Tier-0 diagnostics.

The Tier-0 JSON is a coordination artifact: it records the monic divisor and
the exact rem(P), quo(P) supports/coefficients for a chart target.  This script
recomputes those objects from the chart definitions using Fraction arithmetic
and checks that the JSON payload is not merely self-consistent but also matches
the current source polynomials.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import _codex_eq_odl1_rung2_charts as charts
import _codex_eq_odl1_rung2_face_split_quotient_probe as probe


def parse_fraction(record: dict[str, int]) -> Fraction:
    return Fraction(int(record["num"]), int(record["den"]))


def parse_poly(records: list[dict[str, Any]]) -> probe.Poly:
    out: probe.Poly = {}
    for item in records:
        exp = tuple(int(x) for x in item["exp"])
        coeff = parse_fraction(item["coeff"])
        if coeff:
            out[exp] = coeff
    return probe.clean(out)


def mismatch_prefix(a: probe.Poly, b: probe.Poly, limit: int = 10) -> list[dict[str, Any]]:
    out = []
    for exp in sorted(set(a) | set(b), key=probe.grevlex_key, reverse=True):
        av = a.get(exp, Fraction(0))
        bv = b.get(exp, Fraction(0))
        if av != bv:
            out.append(
                {
                    "exp": list(exp),
                    "expected": probe.fmt_fraction(av),
                    "actual": probe.fmt_fraction(bv),
                }
            )
            if len(out) >= limit:
                break
    return out


def run(args: argparse.Namespace) -> dict[str, Any]:
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    chart_idx = int(artifact["chart"])
    dominant = int(artifact["dominant"])
    chart = charts.build_chart(chart_idx)

    target = probe.homogenize_poly(chart.target, chart.variables, probe.TARGET_DEGREE)
    gen_polys = [probe.homogenize_poly(expr, chart.variables, probe.GEN_DEGREE) for expr in chart.generators]
    divisor_raw = gen_polys[dominant]
    divisor, lead_exp, lead_coeff = probe.monic_normalize(divisor_raw)
    quo_p, rem_p = probe.divide_grevlex(target, divisor)
    recomposed = probe.add_poly(probe.mul_poly(quo_p, divisor), rem_p)

    payload_divisor = parse_poly(artifact["divisor_monic_terms"])
    payload_rem = parse_poly(artifact["remP_terms"])
    payload_quo = parse_poly(artifact["quoP_terms"])

    checks = {
        "schema_ok": artifact.get("schema") == "eq_odl1_rung2_face_split_quotient_tier0_v1",
        "dominant_name_ok": artifact.get("dominant_name") == chart.generator_names[dominant],
        "term_order_ok": artifact.get("term_order") == "graded_reverse_lex",
        "normalization_ok": artifact.get("divisor_normalization") == "leading_coeff_to_1",
        "raw_leading_exp_ok": artifact.get("divisor_raw_leading_exp") == list(lead_exp),
        "raw_leading_coeff_ok": parse_fraction(artifact["divisor_raw_leading_coeff"]) == lead_coeff,
        "divisor_terms_ok": payload_divisor == divisor,
        "rem_terms_ok": payload_rem == rem_p,
        "quo_terms_ok": payload_quo == quo_p,
        "recomposition_ok": recomposed == target,
    }

    exact_ok = all(checks.values())
    out: dict[str, Any] = {
        "schema": "eq_odl1_rung2_verify_quotient_tier0_v1",
        "artifact": str(args.artifact),
        "chart": chart_idx,
        "dominant": dominant,
        "dominant_name": chart.generator_names[dominant],
        "exact_ok": exact_ok,
        "checks": checks,
        "target_terms": len(target),
        "divisor_terms": len(divisor),
        "rem_terms": len(rem_p),
        "quo_terms": len(quo_p),
    }
    if not exact_ok:
        out["mismatches"] = {
            "divisor": mismatch_prefix(divisor, payload_divisor),
            "rem": mismatch_prefix(rem_p, payload_rem),
            "quo": mismatch_prefix(quo_p, payload_quo),
            "recomposition": mismatch_prefix(target, recomposed),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"exact_ok": out["exact_ok"], "summary": str(args.summary)}, sort_keys=True))
    if not out["exact_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
