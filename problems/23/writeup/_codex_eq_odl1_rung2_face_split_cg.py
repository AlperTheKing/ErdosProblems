"""Column generation for quotient-coupled Rung-2 face splits.

This is a search driver.  It never emits an accepted proof by itself; any
candidate column set must still be replayed by the exact quotient/materializer
pipeline and then by the ordinary Fraction checker.
"""

from __future__ import annotations

import argparse
import heapq
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import coo_matrix, hstack

import _codex_eq_odl1_rung2_face_split_quotient_probe as qprobe

try:
    import highspy
except ImportError:  # pragma: no cover
    highspy = None


QColumn = qprobe.QColumn
Exp = qprobe.Exp
Poly = qprobe.Poly


def log(msg: str) -> None:
    print(f"[face-split-cg] {msg}", file=sys.stderr, flush=True)


def column_key(col: QColumn) -> tuple[str, str, str, tuple[int, ...]]:
    return (col.side, col.kind, col.name, tuple(col.multiplier_exp))


def qscore(col: QColumn, row_dual: np.ndarray, row_index: dict[tuple[str, Exp], int]) -> float:
    score = 0.0
    for exp, coeff in col.rem:
        idx = row_index.get(("rem", exp))
        if idx is not None:
            score += float(coeff) * float(row_dual[idx])
    for exp, coeff in col.quo:
        idx = row_index.get(("quo", exp))
        if idx is not None:
            score += float(coeff) * float(row_dual[idx])
    return score


def build_matrix_for_rows(columns: list[QColumn], row_index: dict[tuple[str, Exp], int]) -> coo_matrix:
    mat_rows: list[int] = []
    mat_cols: list[int] = []
    mat_vals: list[float] = []
    for j, col in enumerate(columns):
        for exp, coeff in col.rem:
            idx = row_index.get(("rem", exp))
            if idx is not None:
                mat_rows.append(idx)
                mat_cols.append(j)
                mat_vals.append(float(coeff))
        for exp, coeff in col.quo:
            idx = row_index.get(("quo", exp))
            if idx is not None:
                mat_rows.append(idx)
                mat_cols.append(j)
                mat_vals.append(float(coeff))
    return coo_matrix((mat_vals, (mat_rows, mat_cols)), shape=(len(row_index), len(columns)))


def solve_phase1_equalities(
    rows: list[tuple[str, Exp]],
    rhs: list[Fraction],
    columns: list[QColumn],
    *,
    threads: int,
    time_limit: float,
    solver: str,
    verbose: bool,
    x_tol: float,
) -> dict[str, Any]:
    if highspy is None:
        raise RuntimeError("highspy is not installed")
    row_index = {row: i for i, row in enumerate(rows)}
    mat = build_matrix_for_rows(columns, row_index).tocsc()
    row_count, real_cols = mat.shape
    art = coo_matrix(
        (
            [1.0] * row_count + [-1.0] * row_count,
            (
                list(range(row_count)) + list(range(row_count)),
                list(range(row_count)) + list(range(row_count, 2 * row_count)),
            ),
        ),
        shape=(row_count, 2 * row_count),
    ).tocsc()
    csc = hstack([mat, art], format="csc")
    inf = highspy.kHighsInf

    lp = highspy.HighsLp()
    lp.num_col_ = int(real_cols + 2 * row_count)
    lp.num_row_ = int(row_count)
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_cost_ = [0.0] * int(real_cols) + [1.0] * int(2 * row_count)
    lp.col_lower_ = [0.0] * int(real_cols + 2 * row_count)
    lp.col_upper_ = [inf] * int(real_cols + 2 * row_count)
    b = [float(x) for x in rhs]
    lp.row_lower_ = b
    lp.row_upper_ = b

    a = highspy.HighsSparseMatrix()
    a.format_ = highspy.MatrixFormat.kColwise
    a.num_col_ = int(real_cols + 2 * row_count)
    a.num_row_ = int(row_count)
    a.start_ = [int(x) for x in csc.indptr]
    a.index_ = [int(x) for x in csc.indices]
    a.value_ = [float(x) for x in csc.data]
    lp.a_matrix_ = a

    highs = highspy.Highs()
    highs.setOptionValue("output_flag", bool(verbose))
    if solver != "choose":
        highs.setOptionValue("solver", solver)
    if time_limit > 0:
        highs.setOptionValue("time_limit", float(time_limit))
    if threads > 0:
        highs.setOptionValue("threads", int(threads))
    status = highs.passModel(lp)
    if status != highspy.HighsStatus.kOk:
        return {"success": False, "message": f"passModel failed: {status}", "pass_status": int(status)}
    run_status = highs.run()
    model_status = highs.getModelStatus()
    info = highs.getInfo()
    sol = highs.getSolution()
    x = np.array(sol.col_value[:real_cols], dtype=float)
    up = np.array(sol.col_value[real_cols:real_cols + row_count], dtype=float)
    um = np.array(sol.col_value[real_cols + row_count:real_cols + 2 * row_count], dtype=float)
    residual = mat.tocsr().dot(x) + up - um - np.array(b, dtype=float)
    active_artificial = []
    for i, (vp, vm) in enumerate(zip(up, um)):
        val = max(float(vp), float(vm))
        if val > x_tol:
            active_artificial.append(
                {
                    "row": i,
                    "side": rows[i][0],
                    "exp": list(rows[i][1]),
                    "u_plus": float(vp),
                    "u_minus": float(vm),
                }
            )
    active_artificial.sort(key=lambda rec: max(rec["u_plus"], rec["u_minus"]), reverse=True)
    row_dual = np.array(sol.row_dual, dtype=float)
    objective = float(getattr(info, "objective_function_value", math.nan))
    return {
        "success": model_status == highspy.HighsModelStatus.kOptimal,
        "run_status": int(run_status),
        "model_status": int(model_status),
        "message": highs.modelStatusToString(model_status),
        "simplex_iteration_count": int(getattr(info, "simplex_iteration_count", -1)),
        "objective": objective,
        "artificial_sum": float(np.sum(up) + np.sum(um)),
        "artificial_nonzero": int(np.sum(up > x_tol) + np.sum(um > x_tol)),
        "artificial_max": float(max(np.max(up), np.max(um))) if row_count else 0.0,
        "active_artificial_rows": active_artificial[:100],
        "real_nonzero": int(np.sum(x > x_tol)),
        "max_abs_eq_residual": float(np.max(np.abs(residual))) if len(residual) else 0.0,
        "row_dual_min": float(row_dual.min()) if len(row_dual) else 0.0,
        "row_dual_max": float(row_dual.max()) if len(row_dual) else 0.0,
        "row_dual_nonzero": int(np.sum(np.abs(row_dual) > 1.0e-10)),
        "_row_dual": row_dual,
        "_x": x,
    }


def bounded_push(heap: list[tuple[float, int, QColumn]], item: tuple[float, int, QColumn], limit: int) -> None:
    if limit <= 0:
        return
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif item[0] > heap[0][0]:
        heapq.heapreplace(heap, item)


def candidate_exps_for_poly(
    poly: Poly,
    output_support: set[Exp],
    degree_cap: int,
    support_mode: str,
    max_scan: int,
    num_vars: int,
) -> list[Exp]:
    if support_mode == "derived":
        return qprobe.candidate_multiplier_exps(poly, output_support, degree_cap, None if max_scan == 0 else max_scan)
    return qprobe.charts.exps_upto(num_vars, degree_cap)


def price_face_pairs(
    *,
    chart: qprobe.charts.ChartData,
    dominant: int,
    divisor: Poly,
    rem_support: set[Exp],
    quo_support: set[Exp],
    face_product_support: set[Exp],
    row_dual: np.ndarray,
    row_index: dict[tuple[str, Exp], int],
    current_keys: set[tuple[str, str, str, tuple[int, ...]]],
    support_mode: str,
    degree_cap: int,
    add_per_family: int,
    price_tol: float,
    face_pair_family_filter: set[str] | None,
) -> tuple[list[tuple[float, QColumn]], list[dict[str, Any]]]:
    gen_polys = [qprobe.homogenize_poly(expr, chart.variables, qprobe.GEN_DEGREE) for expr in chart.generators]
    gen_names = chart.generator_names
    ga = gen_polys[dominant]
    dominant_lc = qprobe.leading_term(ga)[1]
    num_vars = len(chart.variables)
    out: list[tuple[float, QColumn]] = []
    family_summaries: list[dict[str, Any]] = []
    for i, gb in enumerate(gen_polys):
        if i == dominant:
            continue
        gen_name = gen_names[i]
        delta_name = f"{gen_names[dominant]}-{gen_name}"
        if face_pair_family_filter is not None and gen_name not in face_pair_family_filter and delta_name not in face_pair_family_filter:
            continue
        delta = qprobe.sub_poly(ga, gb)
        if support_mode == "derived":
            gen_candidates = qprobe.candidate_multiplier_exps(gb, face_product_support, degree_cap, None)
            delta_candidates = qprobe.candidate_multiplier_exps(delta, face_product_support, degree_cap, None)
            candidate_exps = sorted(set(gen_candidates) | set(delta_candidates), key=qprobe.grevlex_key, reverse=True)
        else:
            candidate_exps = qprobe.charts.exps_upto(num_vars, degree_cap)
        heap: list[tuple[float, int, QColumn]] = []
        checked = positive_pairs = skipped_existing = 0
        for checked, exp in enumerate(candidate_exps, start=1):
            mult = qprobe.bernstein_basis_poly(sum(exp), exp)
            gen_quo, gen_rem = qprobe.divide_grevlex(qprobe.mul_poly(gb, mult), divisor)
            gen_col = qprobe.qcolumn_from_parts(
                side="face",
                kind="face_gen",
                name=gen_name,
                multiplier_exp=exp,
                rem=gen_rem,
                quo=gen_quo,
            )
            delta_col = qprobe.qcolumn_from_parts(
                side="face",
                kind="face_delta",
                name=delta_name,
                multiplier_exp=exp,
                rem=qprobe.scale_poly(gen_rem, Fraction(-1)),
                quo=qprobe.sub_poly(qprobe.scale_poly(mult, dominant_lc), gen_quo),
            )
            if column_key(gen_col) in current_keys and column_key(delta_col) in current_keys:
                skipped_existing += 1
                continue
            s1 = qscore(gen_col, row_dual, row_index)
            s2 = qscore(delta_col, row_dual, row_index)
            pair_score = max(s1, s2)
            if pair_score <= price_tol:
                continue
            positive_pairs += 1
            if column_key(gen_col) not in current_keys:
                bounded_push(heap, (pair_score, checked * 2, gen_col), add_per_family * 2)
            if column_key(delta_col) not in current_keys:
                bounded_push(heap, (pair_score, checked * 2 + 1, delta_col), add_per_family * 2)
        chosen = sorted(heap, key=lambda item: item[0], reverse=True)
        out.extend((score, col) for score, _idx, col in chosen)
        family_summaries.append(
            {
                "kind": "face_pair",
                "name": gen_name,
                "delta_name": delta_name,
                "checked": checked,
                "positive_pairs": positive_pairs,
                "added_columns": len(chosen),
                "skipped_existing_pairs": skipped_existing,
                "best_score": float(chosen[0][0]) if chosen else 0.0,
            }
        )
    return out, family_summaries


def price_family_columns(
    *,
    label: str,
    candidates: list[tuple[str, str, str, Exp, Poly]],
    divisor: Poly,
    row_dual: np.ndarray,
    row_index: dict[tuple[str, Exp], int],
    current_keys: set[tuple[str, str, str, tuple[int, ...]]],
    add_per_family: int,
    price_tol: float,
) -> tuple[list[tuple[float, QColumn]], dict[str, Any]]:
    heap: list[tuple[float, int, QColumn]] = []
    checked = positive = skipped = 0
    for checked, (side, kind, name, exp, poly) in enumerate(candidates, start=1):
        col = qprobe.qcolumn(side=side, kind=kind, name=name, multiplier_exp=exp, poly=poly, divisor=divisor)
        if column_key(col) in current_keys:
            skipped += 1
            continue
        score = qscore(col, row_dual, row_index)
        if score > price_tol:
            positive += 1
            bounded_push(heap, (score, checked, col), add_per_family)
    chosen = sorted(heap, key=lambda item: item[0], reverse=True)
    return (
        [(score, col) for score, _idx, col in chosen],
        {
            "kind": label,
            "checked": checked,
            "positive": positive,
            "added_columns": len(chosen),
            "skipped_existing": skipped,
            "best_score": float(chosen[0][0]) if chosen else 0.0,
        },
    )


def price_columns_streaming(
    *,
    chart: qprobe.charts.ChartData,
    dominant: int,
    band: str,
    tier: str,
    support_mode: str,
    divisor: Poly,
    rem_p: Poly,
    quo_p: Poly,
    row_dual: np.ndarray,
    rows: list[tuple[str, Exp]],
    current_keys: set[tuple[str, str, str, tuple[int, ...]]],
    add_per_family: int,
    global_cap: int,
    price_tol: float,
    face_pair_family_filter: set[str] | None,
    include_base_band: bool,
) -> dict[str, Any]:
    row_index = {row: idx for idx, row in enumerate(rows)}
    num_vars = len(chart.variables)
    gen_polys = [qprobe.homogenize_poly(expr, chart.variables, qprobe.GEN_DEGREE) for expr in chart.generators]
    rem_support = set(rem_p)
    quo_support = set(quo_p)
    face_product_support = set(rem_p)
    for qe in quo_p:
        for de in divisor:
            face_product_support.add(qprobe.exp_add(qe, de))
    face_pair_cap, face_band_cap, lift_gen_cap, lift_band_cap = qprobe.tier_caps(tier)

    scored: list[tuple[float, QColumn]] = []
    families: list[dict[str, Any]] = []
    pair_scored, pair_families = price_face_pairs(
        chart=chart,
        dominant=dominant,
        divisor=divisor,
        rem_support=rem_support,
        quo_support=quo_support,
        face_product_support=face_product_support,
        row_dual=row_dual,
        row_index=row_index,
        current_keys=current_keys,
        support_mode=support_mode,
        degree_cap=face_pair_cap,
        add_per_family=add_per_family,
        price_tol=price_tol,
        face_pair_family_filter=face_pair_family_filter,
    )
    scored.extend(pair_scored)
    families.extend(pair_families)

    if include_base_band:
        face_base_candidates = [
            ("face", "face_base", f"B{qprobe.TARGET_DEGREE}", exp, qprobe.bernstein_basis_poly(qprobe.TARGET_DEGREE, exp))
            for exp in qprobe.base_candidate_exps(
                side="face",
                degree=qprobe.TARGET_DEGREE,
                divisor=divisor,
                rem_support=rem_support,
                quo_support=quo_support,
                support_mode=support_mode,
                num_vars=num_vars,
            )
        ]
        cols, summary = price_family_columns(
            label="face_base",
            candidates=face_base_candidates,
            divisor=divisor,
            row_dual=row_dual,
            row_index=row_index,
            current_keys=current_keys,
            add_per_family=add_per_family,
            price_tol=price_tol,
        )
        scored.extend(cols)
        families.append(summary)

        lift_base_candidates = [
            ("lift", "lift_base", "B9", exp, qprobe.bernstein_basis_poly(9, exp))
            for exp in qprobe.base_candidate_exps(
                side="lift",
                degree=9,
                divisor=divisor,
                rem_support=set(),
                quo_support=quo_support,
                support_mode=support_mode,
                num_vars=num_vars,
            )
        ]
        cols, summary = price_family_columns(
            label="lift_base",
            candidates=lift_base_candidates,
            divisor=divisor,
            row_dual=row_dual,
            row_index=row_index,
            current_keys=current_keys,
            add_per_family=add_per_family,
            price_tol=price_tol,
        )
        scored.extend(cols)
        families.append(summary)

        band_poly = qprobe.band_poly(num_vars, band)
        face_band_exps = candidate_exps_for_poly(band_poly, face_product_support, face_band_cap, support_mode, 0, num_vars)
        face_band_candidates = [
            ("face", "face_band", band, exp, qprobe.mul_poly(band_poly, qprobe.bernstein_basis_poly(sum(exp), exp)))
            for exp in face_band_exps
        ]
        cols, summary = price_family_columns(
            label="face_band",
            candidates=face_band_candidates,
            divisor=divisor,
            row_dual=row_dual,
            row_index=row_index,
            current_keys=current_keys,
            add_per_family=add_per_family,
            price_tol=price_tol,
        )
        scored.extend(cols)
        families.append(summary)

        lift_band_exps = candidate_exps_for_poly(band_poly, quo_support, lift_band_cap, support_mode, 0, num_vars)
        lift_band_candidates = [
            ("lift", "lift_band", band, exp, qprobe.mul_poly(band_poly, qprobe.bernstein_basis_poly(sum(exp), exp)))
            for exp in lift_band_exps
        ]
        cols, summary = price_family_columns(
            label="lift_band",
            candidates=lift_band_candidates,
            divisor=divisor,
            row_dual=row_dual,
            row_index=row_index,
            current_keys=current_keys,
            add_per_family=add_per_family,
            price_tol=price_tol,
        )
        scored.extend(cols)
        families.append(summary)

    lift_families: list[tuple[str, str, Poly]] = []
    ga = gen_polys[dominant]
    for i, poly in enumerate(gen_polys):
        lift_families.append(("lift_gen", chart.generator_names[i], poly))
    for i, poly in enumerate(gen_polys):
        if i != dominant:
            lift_families.append(("lift_delta", f"{chart.generator_names[dominant]}-{chart.generator_names[i]}", qprobe.sub_poly(ga, poly)))
    for kind, name, poly in lift_families:
        exps = candidate_exps_for_poly(poly, quo_support, lift_gen_cap, support_mode, 0, num_vars)
        candidates = []
        for exp in exps:
            if sum(exp) + qprobe.total_degree(poly) <= 9:
                candidates.append(("lift", kind, name, exp, qprobe.mul_poly(poly, qprobe.bernstein_basis_poly(sum(exp), exp))))
        cols, summary = price_family_columns(
            label=f"{kind}:{name}",
            candidates=candidates,
            divisor=divisor,
            row_dual=row_dual,
            row_index=row_index,
            current_keys=current_keys,
            add_per_family=add_per_family,
            price_tol=price_tol,
        )
        scored.extend(cols)
        families.append(summary)

    scored.sort(key=lambda item: item[0], reverse=True)
    if global_cap > 0:
        scored = scored[:global_cap]
    top = [
        {
            "score": float(score),
            "side": col.side,
            "kind": col.kind,
            "name": col.name,
            "multiplier_exp": list(col.multiplier_exp),
            "rem_terms": len(col.rem),
            "quo_terms": len(col.quo),
        }
        for score, col in scored[:50]
    ]
    return {
        "added": [col for _score, col in scored],
        "summary": {
            "positive_added_columns": len(scored),
            "best_score": float(scored[0][0]) if scored else 0.0,
            "top": top,
            "families": families,
        },
    }


def prepare_problem(args: argparse.Namespace):
    chart = qprobe.charts.build_chart(args.chart)
    gen_polys = [qprobe.homogenize_poly(expr, chart.variables, qprobe.GEN_DEGREE) for expr in chart.generators]
    divisor_raw = gen_polys[args.dominant]
    divisor, _lead_exp, _lead_coeff = qprobe.monic_normalize(divisor_raw)
    if args.target_beta_json:
        target_betas = qprobe.charts.all_exps(len(chart.variables), qprobe.TARGET_DEGREE)
        target_beta = qprobe.read_target_beta(args.target_beta_json, len(target_betas))
        target = qprobe.poly_from_bernstein_vector(target_betas, target_beta, qprobe.TARGET_DEGREE)
    else:
        target = qprobe.homogenize_poly(chart.target, chart.variables, qprobe.TARGET_DEGREE)
    quo_p, rem_p = qprobe.divide_grevlex(target, divisor)
    if qprobe.sub_poly(target, qprobe.add_poly(qprobe.mul_poly(quo_p, divisor), rem_p)):
        raise RuntimeError("target division identity failed")
    return chart, divisor, rem_p, quo_p


def load_qcolumns_json(path: Path, args: argparse.Namespace, divisor: Poly, rem_p: Poly, quo_p: Poly) -> list[QColumn]:
    payload, columns = qprobe.read_qcolumns_json(path, args=args, divisor=divisor, rem_p=rem_p, quo_p=quo_p)
    log(f"loaded seed qcolumns path={path} columns={len(columns)} schema={payload.get('schema')}")
    return columns


def run(args: argparse.Namespace) -> dict[str, Any]:
    t0 = time.monotonic()
    # Reuse the quotient probe's QColumn JSON writer, whose metadata field
    # names come from the one-shot probe CLI.
    args.max_base_columns = args.seed_max_base
    args.max_pairs_per_family = args.seed_max_pairs
    args.max_band_columns = args.seed_max_band
    args.tier0_json = None
    qprobe.DERIVED_SUPPORT_TERM_LIMIT = None if args.derived_support_limit == 0 else args.derived_support_limit
    chart, divisor, rem_p, quo_p = prepare_problem(args)
    if args.seed_columns_json:
        current_cols = load_qcolumns_json(args.seed_columns_json, args, divisor, rem_p, quo_p)
    else:
        current_cols = qprobe.build_columns(
            chart,
            args.dominant,
            args.band,
            args.tier,
            args.support,
            None if args.seed_max_base == 0 else args.seed_max_base,
            None if args.seed_max_pairs == 0 else args.seed_max_pairs,
            None if args.seed_max_band == 0 else args.seed_max_band,
            qprobe.parse_family_filter(args.face_pair_families),
            divisor,
            rem_p,
            quo_p,
            progress=args.verbose,
            progress_t0=t0,
        )
    current_keys = {column_key(col) for col in current_cols}
    iterations: list[dict[str, Any]] = []
    final_status = "iteration_limit"
    last_x: np.ndarray | None = None
    last_optimal_cols: list[QColumn] | None = None
    for it in range(args.iterations + 1):
        rows, rhs, _ = qprobe.build_equalities(rem_p, quo_p, current_cols)
        log(f"iteration={it} columns={len(current_cols)} rows={len(rows)}")
        phase1 = solve_phase1_equalities(
            rows,
            rhs,
            current_cols,
            threads=args.solver_threads,
            time_limit=args.time_limit,
            solver=args.highspy_solver,
            verbose=args.verbose,
            x_tol=args.x_tol,
        )
        row_dual = phase1.pop("_row_dual", None)
        last_x = phase1.pop("_x", None)
        rec: dict[str, Any] = {
            "iteration": it,
            "columns": len(current_cols),
            "rows": len(rows),
            "phase1": phase1,
        }
        artificial_sum = float(phase1.get("artificial_sum", math.inf))
        log(f"iteration={it} status={phase1.get('message')} artificial_sum={artificial_sum}")
        if phase1.get("success"):
            last_optimal_cols = list(current_cols)
        if phase1.get("success") and artificial_sum <= args.art_tol:
            final_status = "phase1_zero"
            iterations.append(rec)
            break
        if not phase1.get("success") and not args.price_from_nonoptimal:
            final_status = "phase1_not_optimal"
            iterations.append(rec)
            break
        if row_dual is None:
            final_status = "no_row_dual"
            iterations.append(rec)
            break
        pricing = price_columns_streaming(
            chart=chart,
            dominant=args.dominant,
            band=args.band,
            tier=args.tier,
            support_mode=args.support,
            divisor=divisor,
            rem_p=rem_p,
            quo_p=quo_p,
            row_dual=row_dual,
            rows=rows,
            current_keys=current_keys,
            add_per_family=args.add_per_family,
            global_cap=args.global_add_cap,
            price_tol=args.price_tol,
            face_pair_family_filter=qprobe.parse_family_filter(args.face_pair_families),
            include_base_band=args.price_base_band,
        )
        add_cols: list[QColumn] = pricing.pop("added")
        rec["pricing"] = pricing["summary"]
        iterations.append(rec)
        log(
            "iteration={} priced_add={} best={}".format(
                it,
                rec["pricing"].get("positive_added_columns"),
                rec["pricing"].get("best_score"),
            )
        )
        if not add_cols:
            final_status = "no_positive_priced_columns"
            break
        added = 0
        for col in add_cols:
            key = column_key(col)
            if key not in current_keys:
                current_cols.append(col)
                current_keys.add(key)
                added += 1
        rec["pricing"]["new_unique_columns"] = added
        if added == 0:
            final_status = "no_new_unique_priced_columns"
            break

    emitted_columns_json = None
    if args.emit_current_columns_json:
        qprobe.write_qcolumns_json(
            args.emit_current_columns_json,
            args=args,
            chart=chart,
            tier0_payload=None,
            target_beta_nonzero_count=None,
            target_summary=None,
            divisor=divisor,
            rem_p=rem_p,
            quo_p=quo_p,
            columns=current_cols,
            seconds=time.monotonic() - t0,
        )
        emitted_columns_json = str(args.emit_current_columns_json)

    emitted_last_optimal_columns_json = None
    if args.emit_last_optimal_columns_json and last_optimal_cols is not None:
        qprobe.write_qcolumns_json(
            args.emit_last_optimal_columns_json,
            args=args,
            chart=chart,
            tier0_payload=None,
            target_beta_nonzero_count=None,
            target_summary=None,
            divisor=divisor,
            rem_p=rem_p,
            quo_p=quo_p,
            columns=last_optimal_cols,
            seconds=time.monotonic() - t0,
        )
        emitted_last_optimal_columns_json = str(args.emit_last_optimal_columns_json)

    support_count = 0
    support_value_sum = 0.0
    emitted_support_columns_json = None
    if args.emit_support_columns_json and last_x is not None:
        support_indices = [idx for idx, val in enumerate(last_x) if float(val) > args.support_tol]
        support_cols = [current_cols[idx] for idx in support_indices]
        support_count = len(support_cols)
        support_value_sum = float(sum(float(last_x[idx]) for idx in support_indices))
        qprobe.write_qcolumns_json(
            args.emit_support_columns_json,
            args=args,
            chart=chart,
            tier0_payload=None,
            target_beta_nonzero_count=None,
            target_summary=None,
            divisor=divisor,
            rem_p=rem_p,
            quo_p=quo_p,
            columns=support_cols,
            seconds=time.monotonic() - t0,
        )
        emitted_support_columns_json = str(args.emit_support_columns_json)

    return {
        "schema": "eq_odl1_rung2_face_split_streaming_cg_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "iterations_requested": args.iterations,
        "final_status": final_status,
        "final_columns": len(current_cols),
        "iterations": iterations,
        "emitted_columns_json": emitted_columns_json,
        "emitted_last_optimal_columns_json": emitted_last_optimal_columns_json,
        "emitted_support_columns_json": emitted_support_columns_json,
        "support_count": support_count,
        "support_value_sum": support_value_sum,
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
    ap.add_argument("--seed-columns-json", type=Path, default=None)
    ap.add_argument("--seed-max-base", type=int, default=0)
    ap.add_argument("--seed-max-pairs", type=int, default=128)
    ap.add_argument("--seed-max-band", type=int, default=512)
    ap.add_argument("--face-pair-families", default="")
    ap.add_argument("--derived-support-limit", type=int, default=0)
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--add-per-family", type=int, default=256)
    ap.add_argument("--global-add-cap", type=int, default=4096)
    ap.add_argument("--price-tol", type=float, default=1.0e-9)
    ap.add_argument("--art-tol", type=float, default=1.0e-7)
    ap.add_argument("--price-base-band", action="store_true")
    ap.add_argument("--price-from-nonoptimal", action="store_true")
    ap.add_argument("--highspy-solver", choices=["choose", "simplex", "ipm"], default="simplex")
    ap.add_argument("--solver-threads", type=int, default=16)
    ap.add_argument("--time-limit", type=float, default=900.0)
    ap.add_argument("--x-tol", type=float, default=1.0e-9)
    ap.add_argument("--support-tol", type=float, default=1.0e-8)
    ap.add_argument("--emit-current-columns-json", type=Path, default=None)
    ap.add_argument("--emit-last-optimal-columns-json", type=Path, default=None)
    ap.add_argument("--emit-support-columns-json", type=Path, default=None)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    last = out["iterations"][-1] if out["iterations"] else {}
    print(
        json.dumps(
            {
                "chart": out["chart"],
                "dominant": out["dominant"],
                "dominant_name": out["dominant_name"],
                "final_status": out["final_status"],
                "iterations": len(out["iterations"]),
                "final_columns": out["final_columns"],
                "last_artificial_sum": last.get("phase1", {}).get("artificial_sum"),
                "last_positive_added": None if "pricing" not in last else last["pricing"].get("positive_added_columns"),
                "support_count": out.get("support_count"),
                "emitted_last_optimal_columns_json": out.get("emitted_last_optimal_columns_json"),
                "emitted_support_columns_json": out.get("emitted_support_columns_json"),
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
