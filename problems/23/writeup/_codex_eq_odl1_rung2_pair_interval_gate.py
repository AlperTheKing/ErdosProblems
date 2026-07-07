#!/usr/bin/env python3
"""Exact pair-interval identity gate for Rung-2 face splits.

This checks the algebraic identity behind the pair-interval dual master:

    D(G_b*m) + D((G_a-G_b)*m) = D(G_a*m)

where D(F) = (rem_Ga(F), quo_Ga(F)) and the divisor is the monic
normalization of the dominant generator G_a.  The existing column generator
uses the optimized form for the second pair member.  This gate independently
divides both sides and confirms the normalization before the dual interval
master is trusted.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path
from typing import Any

import _codex_eq_odl1_rung2_face_split_quotient_probe as qprobe


Exp = qprobe.Exp
Poly = qprobe.Poly


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def parse_fraction(value: object) -> Fraction:
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, list) and len(value) == 2:
        return Fraction(int(value[0]), int(value[1]))
    if isinstance(value, dict):
        if "num" in value and "den" in value:
            return Fraction(int(value["num"]), int(value["den"]))
        if "value" in value:
            return parse_fraction(value["value"])
    raise ValueError(f"cannot parse Fraction from {value!r}")


def read_target_beta(path: Path, row_count: int) -> list[Fraction]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict) and "target_beta_sparse" in data:
        raw = data["target_beta_sparse"]
    elif isinstance(data, dict) and "target_beta" in data:
        raw = data["target_beta"]
    else:
        raise ValueError("target beta JSON must be a list or contain target_beta/target_beta_sparse")

    if isinstance(raw, list) and raw and all(isinstance(x, dict) and "row" in x for x in raw):
        out = [Fraction(0) for _ in range(row_count)]
        for rec in raw:
            row = int(rec["row"])
            if row < 0 or row >= row_count:
                raise ValueError(f"target beta row out of range: {row}")
            out[row] += parse_fraction(rec)
        return out

    if not isinstance(raw, list):
        raise ValueError("target beta payload must be a list")
    if len(raw) != row_count:
        raise ValueError(f"dense target beta length {len(raw)} != row count {row_count}")
    return [parse_fraction(x) for x in raw]


def target_division(args: argparse.Namespace, chart: qprobe.charts.ChartData, divisor: Poly) -> tuple[Poly, Poly, dict[str, object]]:
    if args.tier0_json:
        if args.target_beta_json:
            raise ValueError("--target-beta-json cannot be combined with --tier0-json")
        payload = json.loads(args.tier0_json.read_text(encoding="utf-8"))
        if int(payload.get("chart")) != args.chart or int(payload.get("dominant")) != args.dominant:
            raise ValueError("--tier0-json chart/dominant does not match requested chart/dominant")
        cached_divisor = qprobe.poly_from_terms_record(payload["divisor_monic_terms"])  # type: ignore[index]
        if cached_divisor != divisor:
            raise ValueError("--tier0-json divisor_monic_terms do not match current divisor")
        rem_p = qprobe.poly_from_terms_record(payload["remP_terms"])  # type: ignore[index]
        quo_p = qprobe.poly_from_terms_record(payload["quoP_terms"])  # type: ignore[index]
        return rem_p, quo_p, {
            "target_mode": payload.get("target_mode", "chart_target"),
            "target_beta_json": payload.get("target_beta_json"),
            "tier0_json": str(args.tier0_json),
            "target_summary": payload.get("target_summary"),
        }

    if args.target_beta_json:
        target_betas = qprobe.charts.all_exps(len(chart.variables), qprobe.TARGET_DEGREE)
        target_beta = read_target_beta(args.target_beta_json, len(target_betas))
        target = qprobe.poly_from_bernstein_vector(target_betas, target_beta, qprobe.TARGET_DEGREE)
        mode = "custom_bernstein"
    else:
        target = qprobe.homogenize_poly(chart.target, chart.variables, qprobe.TARGET_DEGREE)
        mode = "chart_target"
    quo_p, rem_p = qprobe.divide_grevlex(target, divisor)
    recomposed = qprobe.add_poly(qprobe.mul_poly(quo_p, divisor), rem_p)
    if qprobe.sub_poly(target, recomposed):
        raise RuntimeError("target division identity failed")
    return rem_p, quo_p, {
        "target_mode": mode,
        "target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
        "tier0_json": None,
        "target_summary": qprobe.poly_summary(target),
    }


def face_product_support(rem_p: Poly, quo_p: Poly, divisor: Poly) -> set[Exp]:
    out = set(rem_p)
    for qe in quo_p:
        for de in divisor:
            out.add(qprobe.exp_add(qe, de))
    return out


def family_multiplier_exps(
    *,
    ga: Poly,
    gb: Poly,
    face_support: set[Exp],
    degree_cap: int,
    support_mode: str,
    max_pairs_per_family: int | None,
    num_vars: int,
) -> list[Exp]:
    if support_mode == "derived":
        delta = qprobe.sub_poly(ga, gb)
        gen_candidates = qprobe.candidate_multiplier_exps(gb, face_support, degree_cap, max_pairs_per_family)
        delta_candidates = qprobe.candidate_multiplier_exps(delta, face_support, degree_cap, max_pairs_per_family)
        candidates = sorted(set(gen_candidates) | set(delta_candidates), key=qprobe.grevlex_key, reverse=True)
    else:
        candidates = qprobe.charts.exps_upto(num_vars, degree_cap)
    if max_pairs_per_family is not None:
        candidates = candidates[:max_pairs_per_family]
    return candidates


def first_diff(a: Poly, b: Poly) -> dict[str, object] | None:
    diff = qprobe.sub_poly(a, b)
    if not diff:
        return None
    exp, coeff = max(diff.items(), key=lambda item: qprobe.grevlex_key(item[0]))
    return {"exp": list(exp), "coeff": fraction_record(coeff), "diff_terms": len(diff)}


def check_family(payload: dict[str, Any]) -> dict[str, object]:
    ga: Poly = payload["ga"]
    gb: Poly = payload["gb"]
    divisor: Poly = payload["divisor"]
    dominant_lc: Fraction = payload["dominant_lc"]
    exps: list[Exp] = payload["exps"]
    family_name: str = payload["family_name"]
    dominant_name: str = payload["dominant_name"]

    delta = qprobe.sub_poly(ga, gb)
    checked = 0
    failures: list[dict[str, object]] = []
    max_rem_terms = 0
    max_quo_terms = 0
    t0 = time.monotonic()
    for exp in exps:
        checked += 1
        mult = qprobe.bernstein_basis_poly(sum(exp), exp)
        gen_quo, gen_rem = qprobe.divide_grevlex(qprobe.mul_poly(gb, mult), divisor)
        delta_quo, delta_rem = qprobe.divide_grevlex(qprobe.mul_poly(delta, mult), divisor)
        ell_quo, ell_rem = qprobe.divide_grevlex(qprobe.mul_poly(ga, mult), divisor)

        expected_ell_quo = qprobe.scale_poly(mult, dominant_lc)
        expected_delta_rem = qprobe.scale_poly(gen_rem, Fraction(-1))
        expected_delta_quo = qprobe.sub_poly(expected_ell_quo, gen_quo)

        rem_sum = qprobe.add_poly(gen_rem, delta_rem)
        quo_sum = qprobe.add_poly(gen_quo, delta_quo)

        max_rem_terms = max(max_rem_terms, len(gen_rem), len(delta_rem), len(ell_rem))
        max_quo_terms = max(max_quo_terms, len(gen_quo), len(delta_quo), len(ell_quo))

        reasons: list[dict[str, object]] = []
        if ell_rem:
            reasons.append({"check": "ell_rem_zero", "diff": qprobe.poly_terms_record(ell_rem)[:5]})
        diff = first_diff(ell_quo, expected_ell_quo)
        if diff is not None:
            reasons.append({"check": "ell_quo_lc_mult", "diff": diff})
        diff = first_diff(rem_sum, ell_rem)
        if diff is not None:
            reasons.append({"check": "gen_plus_delta_rem_eq_ell_rem", "diff": diff})
        diff = first_diff(quo_sum, ell_quo)
        if diff is not None:
            reasons.append({"check": "gen_plus_delta_quo_eq_ell_quo", "diff": diff})
        diff = first_diff(delta_rem, expected_delta_rem)
        if diff is not None:
            reasons.append({"check": "optimized_delta_rem", "diff": diff})
        diff = first_diff(delta_quo, expected_delta_quo)
        if diff is not None:
            reasons.append({"check": "optimized_delta_quo", "diff": diff})
        if reasons:
            failures.append({"multiplier_exp": list(exp), "reasons": reasons[:10]})
            if len(failures) >= int(payload["max_failures"]):
                break

    return {
        "family": family_name,
        "delta_family": f"{dominant_name}-{family_name}",
        "candidate_count": len(exps),
        "checked": checked,
        "ok": not failures and checked == len(exps),
        "failure_count": len(failures),
        "failure_examples": failures,
        "max_rem_terms_seen": max_rem_terms,
        "max_quo_terms_seen": max_quo_terms,
        "seconds": time.monotonic() - t0,
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    qprobe.DERIVED_SUPPORT_TERM_LIMIT = None if args.derived_support_limit == 0 else args.derived_support_limit
    t0 = time.monotonic()
    chart = qprobe.charts.build_chart(args.chart)
    gen_polys = [qprobe.homogenize_poly(expr, chart.variables, qprobe.GEN_DEGREE) for expr in chart.generators]
    ga = gen_polys[args.dominant]
    divisor, lead_exp, lead_coeff = qprobe.monic_normalize(ga)
    rem_p, quo_p, target_meta = target_division(args, chart, divisor)
    support = face_product_support(rem_p, quo_p, divisor)
    face_pair_cap, _face_band_cap, _lift_gen_cap, _lift_band_cap = qprobe.tier_caps(args.tier)
    family_filter = qprobe.parse_family_filter(args.face_pair_families)
    max_pairs = None if args.max_pairs_per_family == 0 else args.max_pairs_per_family
    num_vars = len(chart.variables)

    payloads: list[dict[str, Any]] = []
    family_plans: list[dict[str, object]] = []
    for i, gb in enumerate(gen_polys):
        if i == args.dominant:
            continue
        family_name = chart.generator_names[i]
        delta_name = f"{chart.generator_names[args.dominant]}-{family_name}"
        if family_filter is not None and family_name not in family_filter and delta_name not in family_filter:
            continue
        exps = family_multiplier_exps(
            ga=ga,
            gb=gb,
            face_support=support,
            degree_cap=face_pair_cap,
            support_mode=args.support,
            max_pairs_per_family=max_pairs,
            num_vars=num_vars,
        )
        family_plans.append({"family": family_name, "delta_family": delta_name, "candidate_count": len(exps)})
        payloads.append(
            {
                "ga": ga,
                "gb": gb,
                "divisor": divisor,
                "dominant_lc": lead_coeff,
                "exps": exps,
                "family_name": family_name,
                "dominant_name": chart.generator_names[args.dominant],
                "max_failures": args.max_failures,
            }
        )

    family_results: list[dict[str, object]] = []
    if args.workers > 1 and len(payloads) > 1:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(payloads))) as pool:
            futures = [pool.submit(check_family, payload) for payload in payloads]
            for fut in as_completed(futures):
                family_results.append(fut.result())
    else:
        for payload in payloads:
            family_results.append(check_family(payload))
    family_results.sort(key=lambda rec: str(rec["family"]))

    checked = sum(int(rec["checked"]) for rec in family_results)
    failure_count = sum(int(rec["failure_count"]) for rec in family_results)
    ok = failure_count == 0 and all(bool(rec["ok"]) for rec in family_results)
    return {
        "schema": "eq_odl1_rung2_pair_interval_identity_gate_v1",
        **target_meta,
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "derived_support_limit": qprobe.DERIVED_SUPPORT_TERM_LIMIT,
        "face_pair_families": sorted(family_filter) if family_filter is not None else None,
        "max_pairs_per_family": args.max_pairs_per_family,
        "term_order": "graded_reverse_lex",
        "divisor_normalization": "leading_coeff_to_1",
        "divisor_raw_leading_exp": list(lead_exp),
        "divisor_raw_leading_coeff": fraction_record(lead_coeff),
        "remP_summary": qprobe.poly_summary(rem_p),
        "quoP_summary": qprobe.poly_summary(quo_p),
        "face_product_support_terms": len(support),
        "family_plan": family_plans,
        "family_results": family_results,
        "checked_pairs": checked,
        "failure_count": failure_count,
        "identity_ok": ok,
        "seconds": time.monotonic() - t0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--tier", choices=["tier1", "tier2", "tier3"], default="tier3")
    ap.add_argument("--support", choices=["target", "derived", "all"], default="derived")
    ap.add_argument("--target-beta-json", type=Path, default=None)
    ap.add_argument("--tier0-json", type=Path, default=None)
    ap.add_argument("--max-pairs-per-family", type=int, default=0, help="0 means uncapped after support filter")
    ap.add_argument("--face-pair-families", default="", help="comma-separated non-dominant generator names/delta names")
    ap.add_argument("--derived-support-limit", type=int, default=0, help="0 scans all target support terms")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--max-failures", type=int, default=5)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "chart": out["chart"],
                "dominant": out["dominant"],
                "dominant_name": out["dominant_name"],
                "tier": out["tier"],
                "support": out["support"],
                "checked_pairs": out["checked_pairs"],
                "identity_ok": out["identity_ok"],
                "failure_count": out["failure_count"],
                "seconds": out["seconds"],
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )
    if not out["identity_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
