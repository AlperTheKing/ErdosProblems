"""Phase-I / pricing diagnostics for Rung-2 hybrid face-split LPs.

This is search machinery only.  A successful run here is not an accepted
certificate; accepted rows still have to be expanded and checked by the exact
Fraction verifier.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import coo_matrix, hstack

import _codex_eq_odl1_rung2_hybrid_lp as hybrid

try:
    import highspy
except ImportError:  # pragma: no cover
    highspy = None


def column_key(col: hybrid.HybridColumn) -> tuple[str, str, str, tuple[int, ...]]:
    return (col.side, col.kind, col.name, col.multiplier_exp)


def log(msg: str) -> None:
    print(f"[phase1-cg] {msg}", file=sys.stderr, flush=True)


def make_hybrid_args(args: argparse.Namespace, *, max_pairs: int, max_band: int) -> argparse.Namespace:
    return argparse.Namespace(
        chart=args.chart,
        dominant=args.dominant,
        band=args.band,
        tier=args.tier,
        support=args.support,
        target_beta_json=args.target_beta_json,
        tier0_json=args.tier0_json,
        max_pairs_per_family=max_pairs,
        max_band_columns=max_band,
        face_pair_families=args.face_pair_families,
        method="highspy",
        highspy_solver=args.highspy_solver,
        objective="zero",
        time_limit=args.time_limit,
        solver_threads=args.solver_threads,
        x_tol=args.x_tol,
        row_tol=args.row_tol,
        no_solve=True,
        count_columns_only=False,
        convert_limit=0,
        emit_columns_json=None,
        summary=Path("unused.json"),
        verbose=args.verbose,
    )


def build_columns(args: argparse.Namespace, *, max_pairs: int, max_band: int):
    hargs = make_hybrid_args(args, max_pairs=max_pairs, max_band=max_band)
    return hybrid.build_hybrid_columns(hargs)


def build_matrix(columns: list[hybrid.HybridColumn], row_count: int) -> coo_matrix:
    return hybrid.build_matrix(columns, row_count)


def parse_column_json_kind(kind: str) -> tuple[str, str]:
    for side in ("face", "lift"):
        prefix = f"{side}_"
        if kind.startswith(prefix):
            return side, kind[len(prefix):]
    return "custom", kind


def read_seed_columns_json(path: Path, expected_row_count: int) -> tuple[list[hybrid.HybridColumn], dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    row_count = int(data.get("row_count", -1))
    if row_count != expected_row_count:
        raise ValueError(f"seed row_count {row_count} != expected {expected_row_count}")
    columns: list[hybrid.HybridColumn] = []
    for cidx, rec in enumerate(data.get("columns", [])):
        side, kind = parse_column_json_kind(str(rec.get("kind", "")))
        terms = []
        for term in rec.get("terms", []):
            row = int(term["row"])
            if row < 0 or row >= expected_row_count:
                raise ValueError(f"seed column {cidx} has row out of range: {row}")
            terms.append((row, Fraction(int(term["num"]), int(term["den"]))))
        columns.append(
            hybrid.HybridColumn(
                side=side,
                kind=kind,
                name=str(rec.get("name", "")),
                multiplier_exp=tuple(int(x) for x in rec.get("multiplier_exp", [])),
                terms=tuple(sorted(terms)),
            )
        )
    return columns, data


def solve_phase1(
    mat: coo_matrix,
    target_beta: list,
    *,
    threads: int,
    time_limit: float,
    verbose: bool,
    x_tol: float,
    solver: str,
    artificial_row_mode: str,
) -> dict[str, Any]:
    if highspy is None:
        raise RuntimeError("highspy is not installed")

    row_count, real_cols = mat.shape
    target_float = np.array([float(x) for x in target_beta], dtype=float)
    if artificial_row_mode == "all":
        artificial_rows = np.arange(row_count, dtype=int)
    elif artificial_row_mode == "negative":
        artificial_rows = np.flatnonzero(target_float < -1.0e-15)
    else:
        raise ValueError(f"unknown artificial_row_mode: {artificial_row_mode}")
    art_count = int(len(artificial_rows))
    art = coo_matrix(
        (-np.ones(art_count, dtype=float), (artificial_rows, np.arange(art_count))),
        shape=(row_count, art_count),
    ).tocsc()
    csc = hstack([mat.tocsc(), art], format="csc")
    inf = highspy.kHighsInf

    lp = highspy.HighsLp()
    lp.num_col_ = int(real_cols + art_count)
    lp.num_row_ = int(row_count)
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_cost_ = [0.0] * int(real_cols) + [1.0] * int(art_count)
    lp.col_lower_ = [0.0] * int(real_cols + art_count)
    lp.col_upper_ = [inf] * int(real_cols + art_count)
    lp.row_lower_ = [-inf] * int(row_count)
    lp.row_upper_ = [float(x) for x in target_beta]

    a = highspy.HighsSparseMatrix()
    a.format_ = highspy.MatrixFormat.kColwise
    a.num_col_ = int(real_cols + art_count)
    a.num_row_ = int(row_count)
    a.start_ = [int(x) for x in csc.indptr]
    a.index_ = [int(x) for x in csc.indices]
    a.value_ = [float(x) for x in csc.data]
    lp.a_matrix_ = a

    highs = highspy.Highs()
    highs.setOptionValue("output_flag", bool(verbose))
    highs.setOptionValue("solver", solver)
    if time_limit > 0:
        highs.setOptionValue("time_limit", float(time_limit))
    if threads > 0:
        highs.setOptionValue("threads", int(threads))

    status = highs.passModel(lp)
    if status != highspy.HighsStatus.kOk:
        return {"success": False, "pass_status": int(status), "message": f"passModel failed: {status}"}

    run_status = highs.run()
    model_status = highs.getModelStatus()
    info = highs.getInfo()
    sol = highs.getSolution()

    x = np.array(sol.col_value[:real_cols], dtype=float)
    z = np.array(sol.col_value[real_cols:real_cols + art_count], dtype=float)
    active_artificial = [
        {"row": int(artificial_rows[i]), "value": float(val)}
        for i, val in enumerate(z)
        if float(val) > x_tol
    ]
    active_artificial.sort(key=lambda rec: rec["value"], reverse=True)
    original_activity = mat.tocsr().dot(x)
    original_violation = original_activity - target_float
    row_dual = np.array(sol.row_dual, dtype=float)
    col_dual = np.array(sol.col_dual[:real_cols], dtype=float)

    # HiGHS reduced costs for upper-bound rows empirically satisfy
    # rc = cost - A^T row_dual.  Check this on the active restricted matrix.
    dot = mat.tocsc().T.dot(row_dual)
    rc_formula = -dot
    if len(col_dual):
        rc_err = np.abs(col_dual - rc_formula)
        max_rc_formula_error = float(rc_err.max())
        p95_rc_formula_error = float(np.quantile(rc_err, 0.95))
    else:
        max_rc_formula_error = 0.0
        p95_rc_formula_error = 0.0

    return {
        "success": model_status == highspy.HighsModelStatus.kOptimal,
        "run_status": int(run_status),
        "model_status": int(model_status),
        "message": highs.modelStatusToString(model_status),
        "simplex_iteration_count": int(getattr(info, "simplex_iteration_count", -1)),
        "objective": float(getattr(info, "objective_function_value", math.nan)),
        "real_nonzero": int(np.sum(x > x_tol)),
        "artificial_rows": art_count,
        "artificial_row_mode": artificial_row_mode,
        "artificial_initial_sum": float(np.maximum(0.0, -target_float[artificial_rows]).sum()) if art_count else 0.0,
        "artificial_nonzero": int(np.sum(z > x_tol)),
        "active_artificial_rows": active_artificial[:100],
        "active_artificial_value_sum": float(sum(rec["value"] for rec in active_artificial)),
        "artificial_max": float(z.max()) if len(z) else 0.0,
        "artificial_sum": float(z.sum()) if len(z) else 0.0,
        "original_max_upper_violation": float(original_violation.max()) if len(original_violation) else 0.0,
        "original_positive_violation_count": int(np.sum(original_violation > 1.0e-7)),
        "original_p95_upper_violation": float(np.percentile(original_violation, 95)) if len(original_violation) else 0.0,
        "row_dual_min": float(row_dual.min()) if len(row_dual) else 0.0,
        "row_dual_max": float(row_dual.max()) if len(row_dual) else 0.0,
        "row_dual_nonzero": int(np.sum(np.abs(row_dual) > 1.0e-10)),
        "col_dual_min": float(col_dual.min()) if len(col_dual) else 0.0,
        "col_dual_max": float(col_dual.max()) if len(col_dual) else 0.0,
        "max_rc_formula_error": max_rc_formula_error,
        "p95_rc_formula_error": p95_rc_formula_error,
        "_row_dual": row_dual,
        "_x": x,
    }


def fraction_record(q):
    return {"num": q.numerator, "den": q.denominator}


def write_target_beta(path: Path, target_beta: list) -> None:
    rows = []
    for row, val in enumerate(target_beta):
        if val:
            rows.append({"row": int(row), **fraction_record(val)})
    payload = {"schema": "eq_odl1_rung2_custom_target_beta_v1", "row_count": len(target_beta), "target_beta_sparse": rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True), encoding="utf-8")


def score_column(col: hybrid.HybridColumn, row_dual: np.ndarray) -> float:
    score = 0.0
    for row, coeff in col.terms:
        score += float(coeff) * float(row_dual[row])
    return score


def score_column_active_rows(col: hybrid.HybridColumn, active_rows: dict[int, float]) -> float:
    # The accepted cone uses A x <= target.  Positive artificial rows are
    # upper-bound violations, so columns with negative coefficients on those
    # rows are useful.  Weight by current artificial magnitude.
    score = 0.0
    for row, coeff in col.terms:
        weight = active_rows.get(int(row))
        if weight is not None:
            score += -float(coeff) * float(weight)
    return score


def price_columns(
    columns: list[hybrid.HybridColumn],
    row_dual: np.ndarray,
    *,
    skip: set,
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[hybrid.HybridColumn]]:
    candidates: list[tuple[float, int, hybrid.HybridColumn]] = []
    best: tuple[float, int, hybrid.HybridColumn] | None = None
    active_rows = getattr(args, "_active_artificial_row_weights", None)
    for idx, col in enumerate(columns):
        if column_key(col) in skip:
            continue
        if active_rows:
            score = score_column_active_rows(col, active_rows)
        else:
            score = score_column(col, row_dual)
        if best is None or score > best[0]:
            best = (score, idx, col)
        if score > args.price_tol:
            candidates.append((score, idx, col))
    candidates.sort(key=lambda item: item[0], reverse=True)
    top = []
    for score, idx, col in candidates[: args.top]:
        top.append(
            {
                "score": float(score),
                "pool_index": int(idx),
                "side": col.side,
                "kind": col.kind,
                "name": col.name,
                "multiplier_exp": list(col.multiplier_exp),
                "terms": len(col.terms),
            }
        )
    add_cols = [col for _score, _idx, col in candidates[: args.add_top]]
    return (
        {
            "priced_columns": len(columns),
            "skipped_columns": len(skip),
            "positive_score_count": len(candidates),
            "best_score": float(best[0]) if best else 0.0,
            "added_columns": len(add_cols),
            "targeted_active_rows": sorted(int(r) for r in getattr(args, "_active_artificial_row_weights", {}) or {}),
            "top": top,
        },
        add_cols,
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    t0 = time.monotonic()
    log(f"building seed columns max_pairs={args.seed_max_pairs} max_band={args.seed_max_band}")
    chart, betas, target_beta, current_cols, seed_meta = build_columns(
        args,
        max_pairs=args.seed_max_pairs,
        max_band=args.seed_max_band,
    )
    if args.seed_columns_json:
        current_cols, seed_payload = read_seed_columns_json(args.seed_columns_json, len(betas))
        seed_meta = dict(seed_payload.get("meta", {}))
        seed_meta["seed_columns_json"] = str(args.seed_columns_json)
        log(f"loaded seed columns from {args.seed_columns_json} count={len(current_cols)}")
    log(f"seed columns={len(current_cols)} rows={len(betas)}")
    price_cols: list[hybrid.HybridColumn] | None = None
    price_meta = None
    if args.price_max_pairs > 0:
        log(f"building price pool max_pairs={args.price_max_pairs} max_band={args.price_max_band}")
        _chart2, _betas2, _target2, price_cols, price_meta = build_columns(
            args,
            max_pairs=args.price_max_pairs,
            max_band=args.price_max_band,
        )
        log(f"price pool columns={len(price_cols)}")

    current_keys = {column_key(col) for col in current_cols}
    last_support_indices: list[int] = []
    last_support_values: list[float] = []
    iterations = []
    final_status = "iteration_limit"
    for it in range(args.iterations + 1):
        log(f"iteration={it} building matrix columns={len(current_cols)}")
        mat = build_matrix(current_cols, len(betas))
        log(f"iteration={it} solving Phase-I nnz={mat.nnz}")
        phase1 = solve_phase1(
            mat,
            target_beta,
            threads=args.solver_threads,
            time_limit=args.time_limit,
            verbose=args.verbose,
            x_tol=args.x_tol,
            solver=args.highspy_solver,
            artificial_row_mode=args.phase1_artificial_rows,
        )
        row_dual = phase1.pop("_row_dual", None)
        x_vec = phase1.pop("_x", None)
        if x_vec is not None:
            support_pairs = [(idx, float(val)) for idx, val in enumerate(x_vec) if float(val) > args.support_tol]
            last_support_indices = [idx for idx, _val in support_pairs]
            last_support_values = [val for _idx, val in support_pairs]
            phase1["support_count"] = len(last_support_indices)
            phase1["support_value_sum"] = float(sum(last_support_values))
        rec: dict[str, Any] = {
            "iteration": it,
            "columns": len(current_cols),
            "nnz": int(mat.nnz),
            "phase1": phase1,
        }
        artificial_sum = float(phase1.get("artificial_sum", math.inf))
        log(
            "iteration={} phase1 status={} objective={} artificial_sum={}".format(
                it,
                phase1.get("message"),
                phase1.get("objective"),
                artificial_sum,
            )
        )
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
        if price_cols is None:
            final_status = "no_price_pool"
            iterations.append(rec)
            break
        if args.target_active_artificials:
            active_weights = {
                int(rec["row"]): float(rec["value"])
                for rec in phase1.get("active_artificial_rows", [])
            }
            args._active_artificial_row_weights = active_weights
            log(f"iteration={it} targeted active artificial rows={sorted(active_weights)}")
        else:
            args._active_artificial_row_weights = {}
        log(f"iteration={it} pricing columns")
        pricing, add_cols = price_columns(price_cols, row_dual, skip=current_keys, args=args)
        rec["pricing"] = pricing
        iterations.append(rec)
        log(
            "iteration={} positives={} add={} best={}".format(
                it,
                pricing.get("positive_score_count"),
                pricing.get("added_columns"),
                pricing.get("best_score"),
            )
        )
        if not add_cols:
            final_status = "no_positive_priced_columns"
            break
        for col in add_cols:
            key = column_key(col)
            if key not in current_keys:
                current_cols.append(col)
                current_keys.add(key)

    emitted_support_columns_json = None
    emitted_support_target_beta_json = None
    if args.emit_support_columns_json and (last_support_indices or args.emit_all_current_columns):
        if args.emit_all_current_columns:
            support_cols = list(current_cols)
        else:
            support_cols = [current_cols[i] for i in last_support_indices]
        support_meta = dict(seed_meta)
        support_meta["mode"] = "phase1_extracted_support"
        support_meta["support_source_columns"] = len(current_cols)
        support_meta["support_count"] = len(support_cols)
        hybrid.write_columns(args.emit_support_columns_json, chart, args, support_cols, support_meta, len(betas))
        emitted_support_columns_json = str(args.emit_support_columns_json)
    if args.emit_support_target_beta_json:
        write_target_beta(args.emit_support_target_beta_json, target_beta)
        emitted_support_target_beta_json = str(args.emit_support_target_beta_json)

    return {
        "schema": "eq_odl1_rung2_hybrid_phase1_pricing_loop_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "face_pair_families": args.face_pair_families,
        "seed_max_pairs": args.seed_max_pairs,
        "seed_max_band": args.seed_max_band,
        "price_max_pairs": args.price_max_pairs,
        "price_max_band": args.price_max_band,
        "add_top": args.add_top,
        "iterations_requested": args.iterations,
        "final_status": final_status,
        "rows": len(betas),
        "target_beta_nonzero_count": sum(1 for x in target_beta if x),
        "seed_meta": seed_meta,
        "price_meta": price_meta,
        "iterations": iterations,
        "last_support_count": len(last_support_indices),
        "last_support_value_sum": float(sum(last_support_values)),
        "emitted_support_columns_json": emitted_support_columns_json,
        "emitted_support_target_beta_json": emitted_support_target_beta_json,
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
    ap.add_argument("--face-pair-families", default="")
    ap.add_argument("--seed-max-pairs", type=int, default=1024)
    ap.add_argument("--seed-max-band", type=int, default=4096)
    ap.add_argument("--seed-columns-json", type=Path, default=None)
    ap.add_argument("--price-max-pairs", type=int, default=0)
    ap.add_argument("--price-max-band", type=int, default=0)
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--add-top", type=int, default=1000)
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--highspy-solver", choices=["simplex", "ipm"], default="simplex")
    ap.add_argument("--phase1-artificial-rows", choices=["all", "negative"], default="all")
    ap.add_argument("--solver-threads", type=int, default=16)
    ap.add_argument("--time-limit", type=float, default=900.0)
    ap.add_argument("--price-tol", type=float, default=1.0e-8)
    ap.add_argument("--art-tol", type=float, default=1.0e-7)
    ap.add_argument("--price-from-nonoptimal", action="store_true")
    ap.add_argument("--target-active-artificials", action="store_true")
    ap.add_argument("--x-tol", type=float, default=1.0e-9)
    ap.add_argument("--support-tol", type=float, default=1.0e-8)
    ap.add_argument("--emit-support-columns-json", type=Path, default=None)
    ap.add_argument("--emit-support-target-beta-json", type=Path, default=None)
    ap.add_argument("--emit-all-current-columns", action="store_true")
    ap.add_argument("--row-tol", type=float, default=1.0e-8)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    last = out["iterations"][-1] if out["iterations"] else {}
    print(json.dumps({
        "chart": out["chart"],
        "dominant": out["dominant"],
        "final_status": out["final_status"],
        "iterations": len(out["iterations"]),
        "last_columns": last.get("columns"),
        "last_message": last.get("phase1", {}).get("message"),
        "last_artificial_sum": last.get("phase1", {}).get("artificial_sum"),
        "last_positive": None if "pricing" not in last else last["pricing"].get("positive_score_count"),
        "last_support_count": out.get("last_support_count"),
        "emitted_support_columns_json": out.get("emitted_support_columns_json"),
        "summary": str(args.summary),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

