#!/usr/bin/env python3
"""Slack-eliminated hybrid LP for EQ-ODL1 Rung-2 face splits.

This is the scalable search form accepted after the quotient Tier-2 gate:

    P - F_other - g*M has nonnegative degree-11 Bernstein coefficients.

It deliberately removes explicit face_base columns.  The remaining quotient
columns are converted back to the ordinary degree-11 Bernstein row space and
solved as the inequality system A x <= P_beta, x >= 0.  A nonnegative residual
is exactly the recovered face-base slack.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_rung2_charts as charts
import _codex_eq_odl1_rung2_custom_cone_check as custom_check
import _codex_eq_odl1_rung2_face_split_quotient_probe as quotient
import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_source_solution_check as source_check

try:
    import highspy
except ImportError:  # pragma: no cover - optional backend
    highspy = None


Exp = tuple[int, ...]
Poly = dict[Exp, Fraction]


@dataclass(frozen=True)
class HybridColumn:
    side: str
    kind: str
    name: str
    multiplier_exp: Exp
    terms: tuple[tuple[int, Fraction], ...]


def fmt_fraction(q: Fraction) -> str:
    return replay.fmt_fraction(q)


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def poly_from_qterms(terms: tuple[tuple[Exp, Fraction], ...]) -> Poly:
    return {exp: coeff for exp, coeff in terms if coeff}


def qcolumn_full_poly(col: quotient.QColumn, divisor: Poly) -> Poly:
    rem = poly_from_qterms(col.rem)
    quo = poly_from_qterms(col.quo)
    if col.side == "face":
        return quotient.add_poly(rem, quotient.mul_poly(divisor, quo))
    if col.side == "lift":
        return quotient.mul_poly(divisor, quo)
    raise ValueError(f"unknown side {col.side!r}")


def make_bernstein_converter(num_vars: int, degree: int, betas: list[Exp], beta_index: dict[Exp, int]):
    exps_by_degree = {r: charts.all_exps(num_vars, r) for r in range(degree + 1)}
    multinomial_degree = {
        r: {exp: charts.multinomial(r, exp) for exp in exps_by_degree[r]}
        for r in range(degree + 1)
    }
    denom = multinomial_degree[degree]

    def convert(poly: Poly) -> tuple[tuple[int, Fraction], ...]:
        out: dict[int, Fraction] = {}
        for alpha, coeff in poly.items():
            adeg = sum(alpha)
            if adeg > degree:
                raise ValueError(f"column monomial degree {adeg} exceeds Bernstein degree {degree}: {alpha}")
            rem = degree - adeg
            for gamma in exps_by_degree[rem]:
                beta = tuple(a + g for a, g in zip(alpha, gamma))
                row = beta_index[beta]
                val = coeff * Fraction(multinomial_degree[rem][gamma], denom[beta])
                if val:
                    out[row] = out.get(row, Fraction(0)) + val
                    if not out[row]:
                        del out[row]
        return tuple(sorted(out.items()))

    return convert


def read_target_beta(args: argparse.Namespace, chart: charts.ChartData, betas: list[Exp]) -> list[Fraction]:
    if args.target_beta_json:
        return quotient.read_target_beta(args.target_beta_json, len(betas))
    p_map = charts.bernstein_degree_coefficients(chart.target, chart.variables, quotient.TARGET_DEGREE)
    return [p_map[beta] for beta in betas]


def fast_candidate_multiplier_exps(
    poly: Poly,
    output_support: set[Exp],
    degree_cap: int,
    max_count: int | None,
) -> list[Exp]:
    """Fast set-equivalent derived candidate generator for hybrid builds.

    The quotient probe's default derived path scans every output-support term
    against every generator monomial.  Hybrid builds often have a very large
    output support and many families.  Here we enumerate the much smaller
    multiplier simplex and use O(1) support membership tests instead.  For
    uncapped runs this returns the same candidate set, sorted by the same
    grevlex order.  For capped diagnostic runs it takes the first sorted
    candidates rather than preserving the old support-scan discovery order.
    """

    if not output_support or not poly:
        return []
    num_vars = len(next(iter(output_support)))
    poly_exps = tuple(poly.keys())
    out: list[Exp] = []
    for mult in charts.exps_upto(num_vars, degree_cap):
        for pexp in poly_exps:
            if quotient.exp_add(pexp, mult) in output_support:
                out.append(mult)
                break
    out.sort(key=quotient.grevlex_key, reverse=True)
    if max_count is not None:
        out = out[:max_count]
    return out


def load_tier0_or_divide(
    args: argparse.Namespace,
    chart: charts.ChartData,
    divisor: Poly,
    target_beta: list[Fraction],
    betas: list[Exp],
) -> tuple[Poly, Poly, dict[str, Any]]:
    if args.tier0_json:
        if args.verbose:
            print(f"phase=tier0_reuse read_start path={args.tier0_json}", flush=True)
        payload = json.loads(args.tier0_json.read_text(encoding="utf-8"))
        if args.verbose:
            print("phase=tier0_reuse read_done", flush=True)
        if int(payload.get("chart")) != args.chart or int(payload.get("dominant")) != args.dominant:
            raise ValueError("--tier0-json chart/dominant mismatch")
        if not payload.get("target_division_identity_ok"):
            raise ValueError("--tier0-json target_division_identity_ok is not true")
        cached_divisor = quotient.poly_from_terms_record(payload["divisor_monic_terms"])  # type: ignore[index]
        if cached_divisor != divisor:
            raise ValueError("--tier0-json divisor does not match current divisor")
        if args.verbose:
            print("phase=tier0_reuse parse_terms_start", flush=True)
        rem_p = quotient.poly_from_terms_record(payload["remP_terms"])  # type: ignore[index]
        quo_p = quotient.poly_from_terms_record(payload["quoP_terms"])  # type: ignore[index]
        if args.verbose:
            print(f"phase=tier0_reuse parse_terms_done rem_terms={len(rem_p)} quo_terms={len(quo_p)}", flush=True)
        return (
            rem_p,
            quo_p,
            {"target_mode": payload.get("target_mode", "chart_target"), "tier0_json": str(args.tier0_json)},
        )

    if args.target_beta_json:
        target = quotient.poly_from_bernstein_vector(betas, target_beta, quotient.TARGET_DEGREE)
        target_mode = "custom_bernstein"
    else:
        target = quotient.homogenize_poly(chart.target, chart.variables, quotient.TARGET_DEGREE)
        target_mode = "chart_target"
    quo_p, rem_p = quotient.divide_grevlex(target, divisor)
    recomposed = quotient.add_poly(quotient.mul_poly(quo_p, divisor), rem_p)
    if quotient.sub_poly(target, recomposed):
        raise RuntimeError("target division identity failed")
    return rem_p, quo_p, {"target_mode": target_mode, "tier0_json": None}


def build_hybrid_columns(args: argparse.Namespace) -> tuple[charts.ChartData, list[Exp], list[Fraction], list[HybridColumn], dict[str, Any]]:
    t0 = time.monotonic()
    if args.verbose:
        print("phase=hybrid_build chart_start", flush=True)
    chart = charts.build_chart(args.chart)
    if args.verbose:
        print(f"phase=hybrid_build chart_done seconds={time.monotonic() - t0:.3f}", flush=True)
    betas = charts.all_exps(len(chart.variables), quotient.TARGET_DEGREE)
    beta_index = {beta: i for i, beta in enumerate(betas)}
    if args.verbose:
        print(f"phase=hybrid_build target_beta_start rows={len(betas)}", flush=True)
    target_beta = read_target_beta(args, chart, betas)
    if args.verbose:
        print(f"phase=hybrid_build target_beta_done seconds={time.monotonic() - t0:.3f}", flush=True)

    if args.verbose:
        print("phase=hybrid_build gen_hom_start", flush=True)
    gen_polys = [quotient.homogenize_poly(expr, chart.variables, quotient.GEN_DEGREE) for expr in chart.generators]
    divisor_raw = gen_polys[args.dominant]
    divisor, lead_exp, lead_coeff = quotient.monic_normalize(divisor_raw)
    if args.verbose:
        print(f"phase=hybrid_build gen_hom_done seconds={time.monotonic() - t0:.3f}", flush=True)
    rem_p, quo_p, target_meta = load_tier0_or_divide(args, chart, divisor, target_beta, betas)
    if args.verbose:
        print(f"phase=hybrid_build target_division_ready seconds={time.monotonic() - t0:.3f}", flush=True)

    rem_support = set(rem_p)
    quo_support = set(quo_p)
    face_product_support = set(rem_p)
    for qe in quo_p:
        for de in divisor:
            face_product_support.add(quotient.exp_add(qe, de))
    face_pair_cap, face_band_cap, lift_gen_cap, lift_band_cap = quotient.tier_caps(args.tier)
    num_vars = len(chart.variables)
    family_filter = quotient.parse_family_filter(args.face_pair_families)
    max_pairs = None if args.max_pairs_per_family == 0 else args.max_pairs_per_family
    max_band = None if args.max_band_columns == 0 else args.max_band_columns

    # The hybrid formulation eliminates face_base entirely; do not construct
    # those expensive divided Bernstein columns only to filter them away.
    kept_qcols: list[quotient.QColumn] = []
    old_candidate_fn = quotient.candidate_multiplier_exps
    if args.support == "derived":
        quotient.candidate_multiplier_exps = fast_candidate_multiplier_exps
    try:
        kept_qcols.extend(
            quotient.make_face_pair_columns(
                gen_polys=gen_polys,
                gen_names=chart.generator_names,
                dominant=args.dominant,
                degree_cap=face_pair_cap,
                divisor=divisor,
                rem_support=rem_support,
                quo_support=quo_support,
                support_mode=args.support,
                max_pairs_per_family=max_pairs,
                face_pair_family_filter=family_filter,
                num_vars=num_vars,
                face_product_support=face_product_support,
                progress=args.verbose,
                progress_t0=t0,
            )
        )
        kept_qcols.extend(
            quotient.make_band_columns(
                side="face",
                band=args.band,
                band_degree=face_band_cap,
                divisor=divisor,
                rem_support=rem_support,
                quo_support=quo_support,
                support_mode=args.support,
                max_columns=max_band,
                num_vars=num_vars,
                output_support=face_product_support,
                progress=args.verbose,
                progress_t0=t0,
            )
        )
        kept_qcols.extend(
            quotient.make_base_columns(
                side="lift",
                degree=9,
                divisor=divisor,
                rem_support=set(),
                quo_support=quo_support,
                support_mode=args.support,
                max_columns=None,
                num_vars=num_vars,
                progress=args.verbose,
                progress_t0=t0,
            )
        )
        kept_qcols.extend(
            quotient.make_lift_gen_columns(
                gen_polys=gen_polys,
                gen_names=chart.generator_names,
                dominant=args.dominant,
                degree_cap=lift_gen_cap,
                divisor=divisor,
                quo_support=quo_support,
                support_mode=args.support,
                max_columns_per_family=max_pairs,
                num_vars=num_vars,
                progress=args.verbose,
                progress_t0=t0,
            )
        )
        kept_qcols.extend(
            quotient.make_band_columns(
                side="lift",
                band=args.band,
                band_degree=lift_band_cap,
                divisor=divisor,
                rem_support=set(),
                quo_support=quo_support,
                support_mode=args.support,
                max_columns=max_band,
                num_vars=num_vars,
                output_support=quo_support,
                progress=args.verbose,
                progress_t0=t0,
            )
        )
    finally:
        quotient.candidate_multiplier_exps = old_candidate_fn
    skipped_face_base = len(charts.all_exps(num_vars, quotient.TARGET_DEGREE))
    if args.count_columns_only:
        meta = {
            **target_meta,
            "dominant_name": chart.generator_names[args.dominant],
            "divisor_raw_leading_exp": list(lead_exp),
            "divisor_raw_leading_coeff": fraction_record(lead_coeff),
            "remP_summary": quotient.poly_summary(rem_p),
            "quoP_summary": quotient.poly_summary(quo_p),
            "quotient_columns_before_filter": len(kept_qcols) + skipped_face_base,
            "skipped_face_base_columns": skipped_face_base,
            "hybrid_columns": len(kept_qcols),
            "converted_hybrid_columns": 0,
            "hybrid_column_terms": None,
            "conversion_skipped": True,
            "conversion_incomplete": True,
            "conversion_limit": None,
            "build_seconds": time.monotonic() - t0,
        }
        return chart, betas, target_beta, [], meta

    convert = make_bernstein_converter(len(chart.variables), quotient.TARGET_DEGREE, betas, beta_index)

    if args.verbose:
        print(f"phase=hybrid_convert start qcols={len(kept_qcols)} seconds={time.monotonic() - t0:.3f}", flush=True)
    columns: list[HybridColumn] = []
    term_count = 0
    conversion_limit = None if args.convert_limit == 0 else args.convert_limit
    for idx, col in enumerate(kept_qcols, start=1):
        if conversion_limit is not None and idx > conversion_limit:
            break
        poly = qcolumn_full_poly(col, divisor)
        terms = convert(poly)
        term_count += len(terms)
        columns.append(
            HybridColumn(
                side=col.side,
                kind=col.kind,
                name=col.name,
                multiplier_exp=col.multiplier_exp,
                terms=terms,
            )
        )
        if args.verbose and idx % 50000 == 0:
            print(f"phase=hybrid_convert progress checked={idx} term_count={term_count} seconds={time.monotonic() - t0:.3f}", flush=True)

    if args.verbose:
        print(f"phase=hybrid_convert done columns={len(columns)} terms={term_count} seconds={time.monotonic() - t0:.3f}", flush=True)

    meta = {
        **target_meta,
        "dominant_name": chart.generator_names[args.dominant],
        "divisor_raw_leading_exp": list(lead_exp),
        "divisor_raw_leading_coeff": fraction_record(lead_coeff),
        "remP_summary": quotient.poly_summary(rem_p),
        "quoP_summary": quotient.poly_summary(quo_p),
        "quotient_columns_before_filter": len(kept_qcols) + skipped_face_base,
        "skipped_face_base_columns": skipped_face_base,
        "hybrid_columns": len(kept_qcols),
        "converted_hybrid_columns": len(columns),
        "hybrid_column_terms": term_count,
        "conversion_skipped": False,
        "conversion_incomplete": conversion_limit is not None and len(columns) < len(kept_qcols),
        "conversion_limit": conversion_limit,
        "build_seconds": time.monotonic() - t0,
    }
    return chart, betas, target_beta, columns, meta


def build_matrix(columns: list[HybridColumn], row_count: int) -> coo_matrix:
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for j, col in enumerate(columns):
        for i, coeff in col.terms:
            rows.append(i)
            cols.append(j)
            data.append(float(coeff))
    return coo_matrix((data, (rows, cols)), shape=(row_count, len(columns)))


def stable_column_weight(col: HybridColumn, mode: str) -> float:
    if mode == "zero":
        return 0.0
    if mode == "sum":
        return 1.0
    h = 1469598103934665603
    for part in (col.side, col.kind, col.name, str(col.multiplier_exp)):
        for b in part.encode("utf-8"):
            h ^= b
            h = (h * 1099511628211) & ((1 << 64) - 1)
    return 1.0 + 1.0e-7 * ((h % 1000003) / 1000003.0)


def solve_scipy(mat: coo_matrix, target_beta: list[Fraction], columns: list[HybridColumn], args: argparse.Namespace) -> dict[str, Any]:
    c = np.array([stable_column_weight(col, args.objective) for col in columns], dtype=float)
    b_ub = np.array([float(x) for x in target_beta], dtype=float)
    res = linprog(
        c=c,
        A_ub=mat.tocsr(),
        b_ub=b_ub,
        bounds=[(0, None)] * len(columns),
        method=args.method,
        options={} if args.time_limit <= 0 else {"time_limit": args.time_limit},
    )
    out: dict[str, Any] = {
        "method": args.method,
        "objective": args.objective,
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
    }
    if res.success:
        residual = b_ub - mat.tocsr().dot(res.x)
        out.update(
            {
                "float_objective": float(res.fun),
                "float_nonzero": int(np.sum(res.x > args.x_tol)),
                "float_min_residual": float(residual.min()) if len(residual) else 0.0,
                "float_negative_residual_count": int(np.sum(residual < -args.row_tol)),
            }
        )
    return out


def solve_highspy(mat: coo_matrix, target_beta: list[Fraction], columns: list[HybridColumn], args: argparse.Namespace) -> dict[str, Any]:
    if highspy is None:
        return {"method": "highspy", "success": False, "lp_status": -2, "lp_message": "highspy is not installed"}
    csc = mat.tocsc()
    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_ = len(columns)
    lp.num_row_ = len(target_beta)
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_cost_ = [stable_column_weight(col, args.objective) for col in columns]
    lp.col_lower_ = [0.0] * len(columns)
    lp.col_upper_ = [inf] * len(columns)
    lp.row_lower_ = [-inf] * len(target_beta)
    lp.row_upper_ = [float(x) for x in target_beta]
    a = highspy.HighsSparseMatrix()
    a.format_ = highspy.MatrixFormat.kColwise
    a.num_col_ = len(columns)
    a.num_row_ = len(target_beta)
    a.start_ = [int(x) for x in csc.indptr]
    a.index_ = [int(x) for x in csc.indices]
    a.value_ = [float(x) for x in csc.data]
    lp.a_matrix_ = a

    highs = highspy.Highs()
    highs.setOptionValue("output_flag", bool(args.verbose))
    if args.highspy_solver != "choose":
        highs.setOptionValue("solver", args.highspy_solver)
    if args.time_limit > 0:
        highs.setOptionValue("time_limit", float(args.time_limit))
    if args.solver_threads > 0:
        highs.setOptionValue("threads", int(args.solver_threads))
    status = highs.passModel(lp)
    if status != highspy.HighsStatus.kOk:
        return {"method": "highspy", "success": False, "lp_status": int(status), "lp_message": f"passModel failed: {status}"}
    run_status = highs.run()
    model_status = highs.getModelStatus()
    success = model_status == highspy.HighsModelStatus.kOptimal
    out: dict[str, Any] = {
        "method": "highspy",
        "highspy_solver": args.highspy_solver,
        "solver_threads": args.solver_threads,
        "run_status": int(run_status),
        "lp_status": int(model_status),
        "lp_message": highs.modelStatusToString(model_status),
        "success": bool(success),
    }
    if success:
        sol = highs.getSolution()
        x = np.array(sol.col_value, dtype=float)
        residual = np.array(lp.row_upper_, dtype=float) - mat.tocsr().dot(x)
        out.update(
            {
                "float_objective": float(np.dot(np.array(lp.col_cost_, dtype=float), x)),
                "float_nonzero": int(np.sum(x > args.x_tol)),
                "float_min_residual": float(residual.min()) if len(residual) else 0.0,
                "float_negative_residual_count": int(np.sum(residual < -args.row_tol)),
            }
        )
    return out


def write_columns(path: Path, chart: charts.ChartData, args: argparse.Namespace, columns: list[HybridColumn], meta: dict[str, Any], row_count: int) -> None:
    payload = {
        "schema": "eq_odl1_rung2_hybrid_columns_v1",
        "column_set": "hybrid_combined",
        "row_count": row_count,
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "meta": meta,
        "columns": [
            {
                "kind": f"{col.side}_{col.kind}" if not col.kind.startswith(col.side) else col.kind,
                "name": col.name,
                "multiplier_exp": list(col.multiplier_exp),
                "terms": [
                    {"row": int(row), **fraction_record(coeff)}
                    for row, coeff in col.terms
                ],
            }
            for col in columns
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    t0 = time.monotonic()
    chart, betas, target_beta, columns, meta = build_hybrid_columns(args)
    if (meta.get("conversion_skipped") or meta.get("conversion_incomplete")) and not args.no_solve:
        raise ValueError("--count-columns-only/--convert-limit require --no-solve")
    if args.verbose:
        print(f"phase=matrix_build start columns={len(columns)}", flush=True)
    mat = build_matrix(columns, len(betas))
    if args.verbose:
        print(f"phase=matrix_build done rows={len(betas)} cols={len(columns)} nnz={mat.nnz}", flush=True)
    solve: dict[str, Any]
    if args.no_solve:
        solve = {"skipped": True}
    elif args.method == "highspy":
        solve = solve_highspy(mat, target_beta, columns, args)
    else:
        solve = solve_scipy(mat, target_beta, columns, args)
    if args.emit_columns_json:
        write_columns(args.emit_columns_json, chart, args, columns, meta, len(betas))
    out = {
        "schema": "eq_odl1_rung2_hybrid_lp_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
        "tier0_json": str(args.tier0_json) if args.tier0_json else None,
        "rows": len(betas),
        "columns": int(meta.get("hybrid_columns", len(columns))),
        "converted_columns": len(columns),
        "matrix_columns": len(columns),
        "nnz": int(mat.nnz),
        "target_beta_nonzero_count": sum(1 for x in target_beta if x),
        "meta": meta,
        "solve": solve,
        "seconds": time.monotonic() - t0,
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--tier", choices=["tier1", "tier2", "tier3"], default="tier2")
    ap.add_argument("--support", choices=["target", "derived", "all"], default="derived")
    ap.add_argument("--target-beta-json", type=Path, default=None)
    ap.add_argument("--tier0-json", type=Path, default=None)
    ap.add_argument("--max-pairs-per-family", type=int, default=0)
    ap.add_argument("--max-band-columns", type=int, default=0)
    ap.add_argument("--face-pair-families", default="")
    ap.add_argument("--method", choices=["highspy", "highs", "highs-ds", "highs-ipm"], default="highspy")
    ap.add_argument("--highspy-solver", choices=["choose", "simplex", "ipm"], default="simplex")
    ap.add_argument("--solver-threads", type=int, default=48)
    ap.add_argument("--objective", choices=["zero", "sum", "lex-small"], default="zero")
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--x-tol", type=float, default=1.0e-9)
    ap.add_argument("--row-tol", type=float, default=1.0e-8)
    ap.add_argument("--no-solve", action="store_true")
    ap.add_argument("--count-columns-only", action="store_true")
    ap.add_argument("--convert-limit", type=int, default=0)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--emit-columns-json", type=Path, default=None)
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
                "rows": out["rows"],
                "columns": out["columns"],
                "converted_columns": out["converted_columns"],
                "nnz": out["nnz"],
                "solve": out["solve"],
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
