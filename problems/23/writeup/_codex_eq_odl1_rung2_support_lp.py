#!/usr/bin/env python3
"""Reduced-support full dominance LP diagnostic for EQ-ODL1 Rung-2.

This is not a final proof emitter.  It probes one or more dominance-band charts
using only Bernstein columns that can directly repair a negative Bernstein
coefficient of the chart target.

Rung-2 chart identity:

    P_k = P0 + sum_i G_i^hom Q_i
              + sum_{b != a} (G_a^hom - G_b^hom) R_b
              + Band_beta H

where all multipliers have nonnegative Bernstein coefficients, G_i and deltas
are degree 2 on the compactified simplex, Q_i/R_b have degree 9, the band
multiplier has degree 10, and P0 is degree 11 Bernstein-nonnegative.
"""

from __future__ import annotations

import argparse
import json
import time
from functools import lru_cache
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, hstack

import _codex_eq_odl1_rung2_band_lp as band_lp
import _codex_eq_odl1_rung2_charts as charts


TARGET_DEGREE = charts.TARGET_DEGREE
GEN_DEGREE = 2
GEN_MULT_DEGREE = 9
BAND_MULT_DEGREE = 10
BANDS = band_lp.BANDS


@dataclass(frozen=True)
class Column:
    kind: str
    name: str
    multiplier_exp: tuple[int, ...]
    terms: tuple[tuple[int, Fraction], ...]


@dataclass(frozen=True)
class PreparedChart:
    k: int
    chart: charts.ChartData
    gen_polys: list[dict[tuple[int, ...], Fraction]]
    betas: list[tuple[int, ...]]
    beta_index: dict[tuple[int, ...], int]
    p_beta: list[Fraction]


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 1024 and q.denominator.bit_length() < 1024:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def multinomial(total: int, exp: tuple[int, ...]) -> int:
    return charts.multinomial(total, exp)


@lru_cache(maxsize=None)
def bernstein_product_coeff(
    left_degree: int,
    left_exp: tuple[int, ...],
    right_degree: int,
    right_exp: tuple[int, ...],
) -> Fraction:
    """Coefficient of B_{left+right}^{d+e} in B_left^d * B_right^e."""
    out_exp = tuple(a + b for a, b in zip(left_exp, right_exp))
    return Fraction(
        multinomial(left_degree, left_exp) * multinomial(right_degree, right_exp),
        multinomial(left_degree + right_degree, out_exp),
    )


def add_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def sub_exp(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...] | None:
    out = tuple(x - y for x, y in zip(a, b))
    return None if min(out) < 0 else out


def build_chart_hom2_generators(k: int) -> tuple[charts.ChartData, list[dict[tuple[int, ...], Fraction]]]:
    """Build chart and return all generators in Bernstein degree 2.

    charts.build_chart already performs the correct chart substitution and
    homogenizes each raw generator to its natural degree.  The Rung-2 dominance
    split compares all generators in degree 2, so linear generators are simply
    degree-elevated to Bernstein degree 2 here.
    """
    chart = charts.build_chart(k)
    out = []
    for expr in chart.generators:
        out.append(charts.bernstein_degree_coefficients(expr, chart.variables, GEN_DEGREE))
    return chart, out


def poly_diff(
    a: dict[tuple[int, ...], Fraction],
    b: dict[tuple[int, ...], Fraction],
) -> dict[tuple[int, ...], Fraction]:
    keys = set(a) | set(b)
    return {k: a.get(k, Fraction(0)) - b.get(k, Fraction(0)) for k in keys}


def column_from_degree2_poly(
    kind: str,
    name: str,
    poly_b2: dict[tuple[int, ...], Fraction],
    multiplier_exp: tuple[int, ...],
    beta_index: dict[tuple[int, ...], int],
) -> Column:
    terms: list[tuple[int, Fraction]] = []
    for gen_exp, gen_coeff in poly_b2.items():
        if not gen_coeff:
            continue
        out_exp = add_exp(gen_exp, multiplier_exp)
        coeff = gen_coeff * bernstein_product_coeff(GEN_DEGREE, gen_exp, GEN_MULT_DEGREE, multiplier_exp)
        if coeff:
            terms.append((beta_index[out_exp], coeff))
    return Column(kind=kind, name=name, multiplier_exp=multiplier_exp, terms=tuple(terms))


def selected_degree2_columns(
    p_beta: list[Fraction],
    beta_index: dict[tuple[int, ...], int],
    gen_polys: list[dict[tuple[int, ...], Fraction]],
    gen_names: tuple[str, ...],
    dominant: int,
    support: str,
    max_columns_per_family: int | None,
    include_deltas: bool = True,
    leading_s0_only: bool = False,
) -> list[Column]:
    neg_rows = {i for i, val in enumerate(p_beta) if val < 0}
    beta_by_row = {row: beta for beta, row in beta_index.items()}
    neg_betas = [beta_by_row[i] for i in neg_rows]
    num_vars = len(next(iter(beta_index)))
    columns: list[Column] = []

    def maybe_leading(poly: dict[tuple[int, ...], Fraction]) -> dict[tuple[int, ...], Fraction]:
        if not leading_s0_only:
            return poly
        return {exp: coeff for exp, coeff in poly.items() if exp[0] == 0}

    families: list[tuple[str, str, dict[tuple[int, ...], Fraction]]] = []
    for i, poly in enumerate(gen_polys):
        families.append(("gen", gen_names[i], maybe_leading(poly)))
    if include_deltas:
        for i, poly in enumerate(gen_polys):
            if i == dominant:
                continue
            families.append(("delta", f"{gen_names[dominant]}-{gen_names[i]}", maybe_leading(poly_diff(gen_polys[dominant], poly))))

    all_mult_exps = None
    for kind, name, poly in families:
        family_cols: list[Column] = []
        if support == "all":
            if all_mult_exps is None:
                all_mult_exps = charts.all_exps(num_vars, GEN_MULT_DEGREE)
            candidate_exps = all_mult_exps
        elif support == "negative":
            neg_gen_exps = [exp for exp, coeff in poly.items() if coeff < 0]
            seen: set[tuple[int, ...]] = set()
            for beta in neg_betas:
                for gen_exp in neg_gen_exps:
                    exp = sub_exp(beta, gen_exp)
                    if exp is not None and sum(exp) == GEN_MULT_DEGREE:
                        seen.add(exp)
            candidate_exps = list(seen)
        else:
            raise ValueError(support)
        for exp in candidate_exps:
            col = column_from_degree2_poly(kind, name, poly, exp, beta_index)
            family_cols.append(col)
        if max_columns_per_family is not None and len(family_cols) > max_columns_per_family:
            # Keep columns with the largest direct negative repair mass first.
            def score(col: Column) -> Fraction:
                return -sum(coeff for i, coeff in col.terms if i in neg_rows and coeff < 0)

            family_cols.sort(key=score, reverse=True)
            family_cols = family_cols[:max_columns_per_family]
        columns.extend(family_cols)
        print(
            f"support LP family {kind}:{name} candidate_exps={len(candidate_exps)} "
            f"kept_columns={len(family_cols)} total_columns={len(columns)}",
            flush=True,
        )
    return columns


def selected_band_columns(
    p_beta: list[Fraction],
    beta_index: dict[tuple[int, ...], int],
    band: str,
    support: str,
    max_columns: int | None,
) -> list[Column]:
    neg_rows = {i for i, val in enumerate(p_beta) if val < 0}
    beta_by_row = {row: beta for beta, row in beta_index.items()}
    num_vars = len(next(iter(beta_index)))
    if support == "all":
        candidate_exps = charts.all_exps(num_vars, BAND_MULT_DEGREE)
    elif support == "negative":
        seen: set[tuple[int, ...]] = set()
        for row in neg_rows:
            beta = beta_by_row[row]
            for coord in range(num_vars):
                alpha = list(beta)
                alpha[coord] -= 1
                if alpha[coord] < 0:
                    continue
                alpha_t = tuple(alpha)
                if sum(alpha_t) != BAND_MULT_DEGREE:
                    continue
                coeff = band_lp.band_coeff(alpha_t, coord, BAND_MULT_DEGREE, band)
                if coeff < 0:
                    seen.add(alpha_t)
        candidate_exps = list(seen)
    else:
        raise ValueError(support)

    columns = []
    for alpha in candidate_exps:
        terms = []
        for coord in range(num_vars):
            beta = list(alpha)
            beta[coord] += 1
            beta_t = tuple(beta)
            coeff = band_lp.band_coeff(alpha, coord, BAND_MULT_DEGREE, band)
            terms.append((beta_index[beta_t], coeff))
        columns.append(Column(kind="band", name=band, multiplier_exp=alpha, terms=tuple(terms)))
    if max_columns is not None and len(columns) > max_columns:
        def score(col: Column) -> Fraction:
            return -sum(coeff for i, coeff in col.terms if i in neg_rows and coeff < 0)

        columns.sort(key=score, reverse=True)
        columns = columns[:max_columns]
    print(
        f"support LP band {band} candidate_exps={len(candidate_exps)} "
        f"kept_columns={len(columns)}",
        flush=True,
    )
    return columns


def prepare_chart(k: int) -> PreparedChart:
    t0 = time.time()
    print(f"support LP stage build_chart k={k}", flush=True)
    chart, gen_polys = build_chart_hom2_generators(k)
    print(f"support LP stage build_chart done seconds={time.time() - t0:.3f}", flush=True)
    betas = charts.all_exps(len(chart.variables), TARGET_DEGREE)
    beta_index = {beta: i for i, beta in enumerate(betas)}
    print("support LP stage target bernstein", flush=True)
    t1 = time.time()
    p_map = charts.bernstein_degree_coefficients(chart.target, chart.variables, TARGET_DEGREE)
    p_beta = [p_map[beta] for beta in betas]
    print(f"support LP stage target bernstein done seconds={time.time() - t1:.3f}", flush=True)
    return PreparedChart(k=k, chart=chart, gen_polys=gen_polys, betas=betas, beta_index=beta_index, p_beta=p_beta)

def exact_replay(
    p_beta: list[Fraction],
    columns: list[Column],
    raw,
    max_denominators: list[int],
    store_certificate: bool,
    include_deltas: bool = True,
    leading_s0_only: bool = False,
) -> tuple[bool, dict[str, object]]:
    attempts = []
    for max_den in max_denominators:
        q = [Fraction(str(max(0.0, float(x)))).limit_denominator(max_den) for x in raw]
        residual = p_beta[:]
        nonzero = 0
        for val, col in zip(q, columns):
            if not val:
                continue
            nonzero += 1
            for i, coeff in col.terms:
                residual[i] -= coeff * val
        min_res = min(residual) if residual else Fraction(0)
        neg_count = sum(1 for r in residual if r < 0)
        attempt = {
            "max_denominator": max_den,
            "nonzero_multiplier_count": nonzero,
            "residual_min_coeff": fmt_fraction(min_res),
            "negative_residual_count": neg_count,
        }
        attempts.append(attempt)
        if neg_count == 0:
            out = {
                "max_denominator": max_den,
                "nonzero_multiplier_count": nonzero,
                "residual_min_coeff": fmt_fraction(min_res),
                "attempts": attempts,
            }
            if store_certificate:
                out["certificate_q"] = [fmt_fraction(v) for v in q]
                out["columns"] = [
                    {"kind": c.kind, "name": c.name, "multiplier_exp": list(c.multiplier_exp)}
                    for c in columns
                ]
            return True, out
    return False, {"attempts": attempts}


def solve_one(
    k: int,
    dominant: int,
    band: str,
    support: str,
    max_columns_per_family: int | None,
    max_band_columns: int | None,
    time_limit: float,
    objective: str,
    method: str,
    max_denominators: list[int],
    store_certificate: bool,
    include_deltas: bool = True,
    leading_s0_only: bool = False,
    prepared: PreparedChart | None = None,
) -> dict[str, object]:
    if prepared is None:
        prepared = prepare_chart(k)
    chart = prepared.chart
    gen_polys = prepared.gen_polys
    betas = prepared.betas
    beta_index = prepared.beta_index
    p_beta = prepared.p_beta
    gen_names = chart.generator_names

    print("support LP stage select columns", flush=True)
    t2 = time.time()
    columns = selected_degree2_columns(
        p_beta,
        beta_index,
        gen_polys,
        gen_names,
        dominant,
        support,
        max_columns_per_family,
        include_deltas=include_deltas,
        leading_s0_only=leading_s0_only,
    )
    columns.extend(selected_band_columns(p_beta, beta_index, band, support, max_band_columns))
    print(f"support LP stage select columns done seconds={time.time() - t2:.3f} columns={len(columns)}", flush=True)

    rows = []
    cols = []
    data = []
    for j, col in enumerate(columns):
        for i, coeff in col.terms:
            rows.append(i)
            cols.append(j)
            data.append(float(coeff))
    print(f"support LP stage sparse matrix nnz={len(data)}", flush=True)
    mat = coo_matrix((data, (rows, cols)), shape=(len(betas), len(columns))).tocsr()
    b_ub = np.array([float(v) for v in p_beta], dtype=float)
    if objective == "sum":
        c = np.ones(len(columns), dtype=float)
        solve_mat = mat
        bounds = [(0, None)] * len(columns)
    elif objective == "zero":
        c = np.zeros(len(columns), dtype=float)
        solve_mat = mat
        bounds = [(0, None)] * len(columns)
    elif objective == "margin":
        # A*x + tau <= p, tau >= 0.  Minimize -tau.
        solve_mat = hstack([mat, np.ones((len(betas), 1), dtype=float)]).tocsr()
        c = np.zeros(len(columns) + 1, dtype=float)
        c[-1] = -1.0
        bounds = [(0, None)] * len(columns) + [(0, None)]
    else:
        raise ValueError(objective)
    options = {} if time_limit <= 0 else {"time_limit": float(time_limit)}
    print(
        f"rung2 support LP k={k} dom={gen_names[dominant]} band={band} "
        f"support={support} vars={len(columns)} constraints={len(betas)}",
        flush=True,
    )
    res = linprog(c=c, A_ub=solve_mat, b_ub=b_ub, bounds=bounds, method=method, options=options)
    family_counts: dict[str, int] = {}
    for col in columns:
        key = f"{col.kind}:{col.name}"
        family_counts[key] = family_counts.get(key, 0) + 1
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_support_lp_item_v1",
        "k": k,
        "dominant_index": dominant,
        "dominant_name": gen_names[dominant],
        "band": band,
        "support": support,
        "include_deltas": include_deltas,
        "leading_s0_only": leading_s0_only,
        "method": method,
        "variables": len(columns),
        "constraints": len(betas),
        "target_negative_coeffs": sum(1 for v in p_beta if v < 0),
        "family_counts": family_counts,
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
        "exact_ok": None,
    }
    if not res.success:
        return out
    raw_x = res.x[:-1] if objective == "margin" else res.x
    if objective == "margin":
        out["float_margin_tau"] = float(res.x[-1])
    out["float_nonzero"] = int(sum(1 for x in raw_x if x > 1e-9))
    ok, check = exact_replay(p_beta, columns, raw_x, max_denominators, store_certificate)
    out["exact_ok"] = ok
    out["exact_check"] = check
    return out


def parse_ints(text: str, upper: int) -> list[int]:
    if text == "all":
        return list(range(upper))
    return [int(x) for x in text.split(",") if x]


def summarize(items: list[dict[str, object]], complete: bool) -> dict[str, object]:
    return {
        "schema": "eq_odl1_rung2_support_lp_v1",
        "complete": complete,
        "items": items,
        "rows": len(items),
        "success": sum(1 for r in items if r.get("success")),
        "exact_ok": sum(1 for r in items if r.get("exact_ok") is True),
        "timeouts": sum(1 for r in items if r.get("lp_status") == 1),
        "infeasible_or_failed": sum(1 for r in items if not r.get("success")),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--charts", default="0")
    ap.add_argument("--dominants", default="14", help="0-based dominant generator indices or all")
    ap.add_argument("--bands", default="near_2s_minus_1")
    ap.add_argument("--support", choices=["negative", "all"], default="negative")
    ap.add_argument("--no-deltas", action="store_true")
    ap.add_argument("--leading-s0-only", action="store_true")
    ap.add_argument("--max-columns-per-family", type=int, default=0, help="0 means no cap")
    ap.add_argument("--max-band-columns", type=int, default=0, help="0 means no cap")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--objective", choices=["sum", "zero", "margin"], default="sum")
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")
    ap.add_argument("--max-den", default="1000,10000,1000000")
    ap.add_argument("--store-certificate", action="store_true")
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_support_lp_v1.json"))
    args = ap.parse_args()
    ks = parse_ints(args.charts, 10)
    doms = parse_ints(args.dominants, 15)
    bands = list(BANDS) if args.bands == "all" else [x for x in args.bands.split(",") if x]
    max_denominators = [int(x) for x in args.max_den.split(",") if x]
    max_columns_per_family = None if args.max_columns_per_family == 0 else args.max_columns_per_family
    max_band_columns = None if args.max_band_columns == 0 else args.max_band_columns
    rows = []
    prepared_cache: dict[int, PreparedChart] = {}
    for k in ks:
        if k not in prepared_cache:
            prepared_cache[k] = prepare_chart(k)
        for dominant in doms:
            for band in bands:
                rows.append(
                    solve_one(
                        k,
                        dominant,
                        band,
                        args.support,
                        max_columns_per_family,
                        max_band_columns,
                        args.time_limit,
                        args.objective,
                        args.method,
                        max_denominators,
                        args.store_certificate,
                        include_deltas=not args.no_deltas,
                        leading_s0_only=args.leading_s0_only,
                        prepared=prepared_cache[k],
                    )
                )
                args.summary.parent.mkdir(parents=True, exist_ok=True)
                args.summary.write_text(json.dumps(summarize(rows, complete=False), indent=2, sort_keys=True), encoding="utf-8")
    out = summarize(rows, complete=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ["rows", "success", "exact_ok", "timeouts", "infeasible_or_failed"]}, sort_keys=True))


if __name__ == "__main__":
    main()












