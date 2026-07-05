#!/usr/bin/env python3
"""Probe the EQ-ODL1 Rung-2 dominant-face split cone.

This is a diagnostic/emitter scaffold for the face-split shape requested in
F6_ACTIVE_FACE_REPAIR_GPTPRO.md:

    P = P_face + G_a * M,

where P_face has a ConeCert on the G_a=0 face using the ordinary source
dictionary with the dominant generator removed, and M has a ConeCert on the
full dominant chart.  The script builds the single combined linear cone

    P = base_face
        + face_source_columns
        + G_a * (base_M + M_source_columns)

in degree-11 Bernstein coordinates.  A feasible point is only a candidate until
an exact active core is replayed; this file deliberately reports LP structure
and float feasibility rather than declaring a proof.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_rung2_band_lp as band_lp
import _codex_eq_odl1_rung2_charts as charts
import _codex_eq_odl1_rung2_support_lp as support


TARGET_DEGREE = charts.TARGET_DEGREE
GEN_DEGREE = support.GEN_DEGREE


Exp = tuple[int, ...]
Poly = dict[Exp, Fraction]


@dataclass(frozen=True)
class SplitColumn:
    kind: str
    name: str
    multiplier_exp: Exp
    terms: tuple[tuple[int, Fraction], ...]


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 512 and q.denominator.bit_length() < 512:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def write_solution_jsonl(path: Path, values: list[Fraction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for source_col, val in enumerate(values):
            if val:
                f.write(json.dumps({"source_col": source_col, **fraction_record(val)}, sort_keys=True) + "\n")


def exp_add(a: Exp, b: Exp) -> Exp:
    return tuple(x + y for x, y in zip(a, b))


def exp_sub(a: Exp, b: Exp) -> Exp | None:
    out = tuple(x - y for x, y in zip(a, b))
    return None if min(out) < 0 else out


def clean(poly: Poly) -> Poly:
    return {exp: coeff for exp, coeff in poly.items() if coeff}


def bernstein_product(left_degree: int, left: Poly, right_degree: int, right: Poly) -> tuple[int, Poly]:
    out: Poly = {}
    for le, lc in left.items():
        if not lc:
            continue
        for re, rc in right.items():
            if not rc:
                continue
            exp = exp_add(le, re)
            coeff = lc * rc * support.bernstein_product_coeff(left_degree, le, right_degree, re)
            out[exp] = out.get(exp, Fraction(0)) + coeff
    return left_degree + right_degree, clean(out)


def basis_poly(exp: Exp) -> Poly:
    return {exp: Fraction(1)}


def band_poly(num_vars: int, band: str) -> Poly:
    out: Poly = {}
    for coord in range(num_vars):
        exp = tuple(1 if i == coord else 0 for i in range(num_vars))
        coeff = band_lp.band_coeff(tuple(0 for _ in range(num_vars)), coord, 0, band)
        out[exp] = coeff
    return out


def column_from_poly(
    kind: str,
    name: str,
    poly_degree: int,
    poly: Poly,
    multiplier_degree: int,
    multiplier_exp: Exp,
    beta_index: dict[Exp, int],
) -> SplitColumn:
    degree, product = bernstein_product(poly_degree, poly, multiplier_degree, basis_poly(multiplier_exp))
    if degree != TARGET_DEGREE:
        raise ValueError(f"column degree {degree} != {TARGET_DEGREE}")
    terms = tuple(
        sorted((beta_index[exp], coeff) for exp, coeff in product.items() if coeff)
    )
    return SplitColumn(kind=kind, name=name, multiplier_exp=multiplier_exp, terms=terms)


def negative_support_exps(
    p_beta: list[Fraction],
    beta_by_row: dict[int, Exp],
    poly_degree: int,
    poly: Poly,
    multiplier_degree: int,
) -> list[Exp]:
    neg_rows = [i for i, coeff in enumerate(p_beta) if coeff < 0]
    neg_poly_exps = [exp for exp, coeff in poly.items() if coeff < 0]
    seen: set[Exp] = set()
    for row in neg_rows:
        beta = beta_by_row[row]
        for poly_exp in neg_poly_exps:
            exp = exp_sub(beta, poly_exp)
            if exp is not None and sum(exp) == multiplier_degree:
                seen.add(exp)
    return sorted(seen)


def select_columns_from_poly(
    kind: str,
    name: str,
    poly_degree: int,
    poly: Poly,
    multiplier_degree: int,
    prepared: support.PreparedChart,
    support_mode: str,
    max_columns: int | None,
) -> list[SplitColumn]:
    num_vars = len(prepared.betas[0])
    beta_by_row = {row: beta for beta, row in prepared.beta_index.items()}
    if support_mode == "all":
        candidate_exps = charts.all_exps(num_vars, multiplier_degree)
    elif support_mode == "negative":
        candidate_exps = negative_support_exps(
            prepared.p_beta,
            beta_by_row,
            poly_degree,
            poly,
            multiplier_degree,
        )
    else:
        raise ValueError(support_mode)

    columns = [
        column_from_poly(kind, name, poly_degree, poly, multiplier_degree, exp, prepared.beta_index)
        for exp in candidate_exps
    ]
    if max_columns is not None and len(columns) > max_columns:
        neg_rows = {i for i, coeff in enumerate(prepared.p_beta) if coeff < 0}

        def score(col: SplitColumn) -> Fraction:
            return -sum(coeff for row, coeff in col.terms if row in neg_rows and coeff < 0)

        columns.sort(key=score, reverse=True)
        columns = columns[:max_columns]
    return columns


def make_face_columns(
    prepared: support.PreparedChart,
    dominant: int,
    band: str,
    support_mode: str,
    max_columns_per_family: int | None,
    max_band_columns: int | None,
) -> list[SplitColumn]:
    dominant_name = prepared.chart.generator_names[dominant]
    raw = support.selected_degree2_columns(
        prepared.p_beta,
        prepared.beta_index,
        prepared.gen_polys,
        prepared.chart.generator_names,
        dominant,
        support_mode,
        max_columns_per_family,
        include_deltas=True,
    )
    raw.extend(
        support.selected_band_columns(
            prepared.p_beta,
            prepared.beta_index,
            band,
            support_mode,
            max_band_columns,
        )
    )
    out = []
    for col in raw:
        if col.kind == "gen" and col.name == dominant_name:
            continue
        out.append(SplitColumn(f"face_{col.kind}", col.name, tuple(col.multiplier_exp), tuple(col.terms)))
    return out


def make_m_lift_columns(
    prepared: support.PreparedChart,
    dominant: int,
    band: str,
    support_mode: str,
    max_columns_per_family: int | None,
    max_band_columns: int | None,
    include_base: bool,
) -> list[SplitColumn]:
    num_vars = len(prepared.betas[0])
    gen_names = prepared.chart.generator_names
    ga = prepared.gen_polys[dominant]
    columns: list[SplitColumn] = []

    if include_base:
        columns.extend(
            select_columns_from_poly(
                "lift_base",
                f"{gen_names[dominant]}*baseM",
                GEN_DEGREE,
                ga,
                TARGET_DEGREE - GEN_DEGREE,
                prepared,
                support_mode,
                max_columns_per_family,
            )
        )

    families: list[tuple[str, Poly]] = []
    for name, poly in zip(gen_names, prepared.gen_polys):
        families.append((f"gen:{name}", poly))
    for i, poly in enumerate(prepared.gen_polys):
        if i == dominant:
            continue
        families.append((f"delta:{gen_names[dominant]}-{gen_names[i]}", support.poly_diff(ga, poly)))

    for name, poly in families:
        product_degree, product_poly = bernstein_product(GEN_DEGREE, ga, GEN_DEGREE, poly)
        columns.extend(
            select_columns_from_poly(
                "lift_" + name.split(":", 1)[0],
                f"{gen_names[dominant]}*{name}",
                product_degree,
                product_poly,
                TARGET_DEGREE - product_degree,
                prepared,
                support_mode,
                max_columns_per_family,
            )
        )

    bpoly = band_poly(num_vars, band)
    product_degree, product_poly = bernstein_product(GEN_DEGREE, ga, 1, bpoly)
    columns.extend(
        select_columns_from_poly(
            "lift_band",
            f"{gen_names[dominant]}*{band}",
            product_degree,
            product_poly,
            TARGET_DEGREE - product_degree,
            prepared,
            support_mode,
            max_band_columns,
        )
    )
    return columns


def exact_replay_candidate(
    prepared: support.PreparedChart,
    columns: list[SplitColumn],
    raw: np.ndarray,
    max_denominators: list[int],
    solution_jsonl: Path | None,
) -> dict[str, object]:
    attempts: list[dict[str, object]] = []
    best_q: list[Fraction] | None = None
    for max_den in max_denominators:
        q = [Fraction(str(max(0.0, float(x)))).limit_denominator(max_den) for x in raw]
        best_q = q
        residual = prepared.p_beta[:]
        nonzero = 0
        for val, col in zip(q, columns):
            if not val:
                continue
            nonzero += 1
            for row, coeff in col.terms:
                residual[row] -= coeff * val
        negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
        attempt = {
            "max_denominator": max_den,
            "nonzero_multiplier_count": nonzero,
            "residual_min_coeff": fmt_fraction(min(residual) if residual else Fraction(0)),
            "negative_residual_count": len(negative_rows),
            "negative_rows_prefix": [
                {"row": i, "residual": fmt_fraction(x)}
                for i, x in negative_rows[:10]
            ],
        }
        attempts.append(attempt)
        if not negative_rows:
            best_q = q
            if solution_jsonl is not None:
                write_solution_jsonl(solution_jsonl, q)
            return {
                "exact_ok": True,
                "solution_jsonl": str(solution_jsonl) if solution_jsonl is not None else None,
                "max_denominator": max_den,
                "nonzero_multiplier_count": nonzero,
                "attempts": attempts,
            }
    return {
        "exact_ok": False,
        "solution_jsonl": None,
        "attempts": attempts,
        "candidate_nonzero_prefix": [
            {"source_col": i, "value": fmt_fraction(v)}
            for i, v in enumerate(best_q or [])
            if v
        ][:20],
    }


def solve_float(prepared: support.PreparedChart, columns: list[SplitColumn], args: argparse.Namespace) -> dict[str, object]:
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for j, col in enumerate(columns):
        for row, coeff in col.terms:
            rows.append(row)
            cols.append(j)
            data.append(float(coeff))
    mat = coo_matrix((data, (rows, cols)), shape=(len(prepared.betas), len(columns))).tocsr()
    b_ub = np.array([float(x) for x in prepared.p_beta], dtype=float)
    if args.objective == "zero":
        c = np.zeros(len(columns), dtype=float)
    elif args.objective == "sum":
        c = np.ones(len(columns), dtype=float)
    else:
        raise ValueError(args.objective)
    options = {} if args.time_limit <= 0 else {"time_limit": args.time_limit}
    res = linprog(
        c=c,
        A_ub=mat,
        b_ub=b_ub,
        bounds=[(0, None)] * len(columns),
        method=args.method,
        options=options,
    )
    out: dict[str, object] = {
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
        "method": args.method,
        "objective": args.objective,
    }
    if res.success:
        residual = b_ub - mat.dot(res.x)
        out.update(
            {
                "float_objective": float(res.fun),
                "float_nonzero": int(sum(1 for x in res.x if x > args.x_tol)),
                "float_min_residual": float(residual.min()) if len(residual) else 0.0,
                "float_negative_residuals_tol": int(sum(1 for x in residual if x < -args.row_tol)),
                "x_tol": args.x_tol,
                "row_tol": args.row_tol,
            }
        )
        max_denominators = [int(x) for x in args.max_den.split(",") if x]
        if args.exact_replay_candidate:
            out["exact_replay_candidate"] = exact_replay_candidate(
                prepared,
                columns,
                res.x,
                max_denominators,
                args.candidate_solution_jsonl,
            )
    return out


def summarize_columns(columns: list[SplitColumn]) -> dict[str, object]:
    counts: dict[str, int] = {}
    for col in columns:
        key = f"{col.kind}:{col.name}"
        counts[key] = counts.get(key, 0) + 1
    return {
        "count": len(columns),
        "family_counts": dict(sorted(counts.items())),
        "terms": sum(len(col.terms) for col in columns),
    }


def write_columns_json(
    path: Path,
    *,
    prepared: support.PreparedChart,
    args: argparse.Namespace,
    column_set: str,
    columns: list[SplitColumn],
) -> None:
    payload = {
        "schema": "eq_odl1_rung2_face_split_columns_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "target_degree": TARGET_DEGREE,
        "row_count": len(prepared.betas),
        "column_set": column_set,
        "columns": [
            {
                "kind": col.kind,
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


def run(args: argparse.Namespace) -> dict[str, object]:
    t0 = time.monotonic()
    prepared = support.prepare_chart(args.chart)
    dominant_name = prepared.chart.generator_names[args.dominant]
    max_columns_per_family = None if args.max_columns_per_family == 0 else args.max_columns_per_family
    max_band_columns = None if args.max_band_columns == 0 else args.max_band_columns

    export_only = args.no_solve and args.emit_columns_json and args.emit_column_set != "combined"
    need_face = not (export_only and args.emit_column_set == "lift")
    need_lift = not (export_only and args.emit_column_set == "face")
    skipped_column_sets: list[str] = []
    if need_face:
        face_columns = make_face_columns(
            prepared,
            args.dominant,
            args.band,
            args.support,
            max_columns_per_family,
            max_band_columns,
        )
    else:
        face_columns = []
        skipped_column_sets.append("face")
    if need_lift:
        lift_columns = make_m_lift_columns(
            prepared,
            args.dominant,
            args.band,
            args.support,
            max_columns_per_family,
            max_band_columns,
            include_base=not args.no_lift_base,
        )
    else:
        lift_columns = []
        skipped_column_sets.append("lift")
    columns = face_columns + lift_columns
    emitted_columns_json = None
    if args.emit_columns_json:
        if args.emit_column_set == "face":
            emit_columns = face_columns
        elif args.emit_column_set == "lift":
            emit_columns = lift_columns
        elif args.emit_column_set == "combined":
            emit_columns = columns
        else:
            raise ValueError(args.emit_column_set)
        write_columns_json(
            args.emit_columns_json,
            prepared=prepared,
            args=args,
            column_set=args.emit_column_set,
            columns=emit_columns,
        )
        emitted_columns_json = str(args.emit_columns_json)
    solve = solve_float(prepared, columns, args) if not args.no_solve else {"skipped": True}
    return {
        "schema": "eq_odl1_rung2_face_split_probe_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": dominant_name,
        "band": args.band,
        "support": args.support,
        "target_degree": TARGET_DEGREE,
        "max_columns_per_family": max_columns_per_family,
        "max_band_columns": max_band_columns,
        "target_negative_coeffs": sum(1 for x in prepared.p_beta if x < 0),
        "constraints": len(prepared.betas),
        "face_columns": summarize_columns(face_columns),
        "lift_columns": summarize_columns(lift_columns),
        "combined_columns": summarize_columns(columns),
        "skipped_column_sets": skipped_column_sets,
        "emitted_columns_json": emitted_columns_json,
        "solve": solve,
        "seconds": time.monotonic() - t0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", choices=["negative", "all"], default="negative")
    ap.add_argument("--max-columns-per-family", type=int, default=64, help="0 means uncapped")
    ap.add_argument("--max-band-columns", type=int, default=64, help="0 means uncapped")
    ap.add_argument("--no-lift-base", action="store_true")
    ap.add_argument("--no-solve", action="store_true")
    ap.add_argument("--emit-columns-json", type=Path, default=None)
    ap.add_argument("--emit-column-set", choices=["face", "lift", "combined"], default="combined")
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")
    ap.add_argument("--objective", choices=["sum", "zero"], default="sum")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--x-tol", type=float, default=1e-9)
    ap.add_argument("--row-tol", type=float, default=1e-8)
    ap.add_argument("--exact-replay-candidate", action="store_true")
    ap.add_argument("--max-den", default="1000,10000,1000000")
    ap.add_argument("--candidate-solution-jsonl", type=Path, default=None)
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
                "face_columns": out["face_columns"]["count"],
                "lift_columns": out["lift_columns"]["count"],
                "combined_columns": out["combined_columns"]["count"],
                "constraints": out["constraints"],
                "solve": out["solve"],
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
