"""Farkas-ray column generation for hybrid Rung-2 face-split LPs.

Search-only helper.  It solves restricted feasibility LPs A x <= P_beta,
x >= 0.  If a restricted LP is infeasible, HiGHS returns a dual Farkas
ray.  Omitted columns with positive ray-dot-column score can invalidate that
ray, so the loop adds the best such columns from a bounded pool.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

import _codex_eq_odl1_rung2_hybrid_lp as hybrid

try:
    import highspy
except ImportError:  # pragma: no cover
    highspy = None


def column_key(col: hybrid.HybridColumn) -> tuple[str, str, str, tuple[int, ...]]:
    return (col.side, col.kind, col.name, col.multiplier_exp)


def log(msg: str) -> None:
    print(f"[farkas-cg] {msg}", file=sys.stderr, flush=True)


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
        highspy_solver="simplex",
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


def solve_feasibility(mat, target_beta: list, args: argparse.Namespace) -> dict[str, Any]:
    if highspy is None:
        raise RuntimeError("highspy is not installed")
    csc = mat.tocsc()
    row_count, col_count = mat.shape
    inf = highspy.kHighsInf

    lp = highspy.HighsLp()
    lp.num_col_ = int(col_count)
    lp.num_row_ = int(row_count)
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_cost_ = [0.0] * int(col_count)
    lp.col_lower_ = [0.0] * int(col_count)
    lp.col_upper_ = [inf] * int(col_count)
    lp.row_lower_ = [-inf] * int(row_count)
    lp.row_upper_ = [float(x) for x in target_beta]

    a = highspy.HighsSparseMatrix()
    a.format_ = highspy.MatrixFormat.kColwise
    a.num_col_ = int(col_count)
    a.num_row_ = int(row_count)
    a.start_ = [int(x) for x in csc.indptr]
    a.index_ = [int(x) for x in csc.indices]
    a.value_ = [float(x) for x in csc.data]
    lp.a_matrix_ = a

    highs = highspy.Highs()
    highs.setOptionValue("output_flag", bool(args.verbose))
    highs.setOptionValue("solver", "simplex")
    if args.time_limit > 0:
        highs.setOptionValue("time_limit", float(args.time_limit))
    if args.solver_threads > 0:
        highs.setOptionValue("threads", int(args.solver_threads))
    if getattr(args, "presolve_off", False):
        highs.setOptionValue("presolve", "off")

    status = highs.passModel(lp)
    if status != highspy.HighsStatus.kOk:
        return {"success": False, "pass_status": int(status), "message": f"passModel failed: {status}"}
    run_status = highs.run()
    model_status = highs.getModelStatus()
    info = highs.getInfo()
    out: dict[str, Any] = {
        "run_status": int(run_status),
        "model_status": int(model_status),
        "message": highs.modelStatusToString(model_status),
        "success": model_status == highspy.HighsModelStatus.kOptimal,
        "simplex_iteration_count": int(getattr(info, "simplex_iteration_count", -1)),
    }
    if out["success"]:
        sol = highs.getSolution()
        x = np.array(sol.col_value, dtype=float)
        out.update({"real_nonzero": int(np.sum(x > args.x_tol))})
    if model_status == highspy.HighsModelStatus.kInfeasible:
        ray_status, ray_exists, ray = highs.getDualRay()
        out.update({"dual_ray_status": int(ray_status), "dual_ray_exists": bool(ray_exists)})
        if ray_exists:
            ray_arr = np.array(ray, dtype=float)
            scores = mat.tocsc().T.dot(ray_arr)
            out.update(
                {
                    "ray_min": float(ray_arr.min()) if len(ray_arr) else 0.0,
                    "ray_max": float(ray_arr.max()) if len(ray_arr) else 0.0,
                    "ray_nonzero": int(np.sum(np.abs(ray_arr) > args.ray_tol)),
                    "ray_dot_rhs": float(np.dot(ray_arr, np.array([float(x) for x in target_beta], dtype=float))),
                    "seed_score_min": float(scores.min()) if len(scores) else 0.0,
                    "seed_score_max": float(scores.max()) if len(scores) else 0.0,
                    "seed_positive_score_count": int(np.sum(scores > args.price_tol)),
                    "_ray": ray_arr,
                }
            )
    return out


def score_column(col: hybrid.HybridColumn, ray: np.ndarray) -> float:
    score = 0.0
    for row, coeff in col.terms:
        score += float(coeff) * float(ray[row])
    return score


def price_columns(
    columns: list[hybrid.HybridColumn],
    ray: np.ndarray,
    *,
    skip: set,
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[hybrid.HybridColumn]]:
    candidates: list[tuple[float, int, hybrid.HybridColumn]] = []
    best: tuple[float, int, hybrid.HybridColumn] | None = None
    for idx, col in enumerate(columns):
        if column_key(col) in skip:
            continue
        score = score_column(col, ray)
        if best is None or score > best[0]:
            best = (score, idx, col)
        if score > args.price_tol:
            candidates.append((score, idx, col))
    candidates.sort(key=lambda item: item[0], reverse=True)
    report_top = []
    for score, idx, col in candidates[: args.top]:
        report_top.append(
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
            "top": report_top,
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
    iterations = []
    final_status = "iteration_limit"
    for it in range(args.iterations + 1):
        log(f"iteration={it} building matrix columns={len(current_cols)}")
        mat = hybrid.build_matrix(current_cols, len(betas))
        log(f"iteration={it} solving feasibility nnz={mat.nnz}")
        feas = solve_feasibility(mat, target_beta, args)
        ray = feas.pop("_ray", None)
        if (
            args.retry_no_ray_presolve_off
            and feas.get("message") == "Infeasible"
            and not feas.get("dual_ray_exists", False)
        ):
            log(f"iteration={it} retrying no-ray infeasibility with presolve off")
            old_presolve_off = getattr(args, "presolve_off", False)
            args.presolve_off = True
            retry = solve_feasibility(mat, target_beta, args)
            retry_ray = retry.pop("_ray", None)
            retry["retry_presolve_off"] = True
            retry["initial_no_ray_feasibility"] = feas
            args.presolve_off = old_presolve_off
            feas = retry
            ray = retry_ray
        rec: dict[str, Any] = {
            "iteration": it,
            "columns": len(current_cols),
            "nnz": int(mat.nnz),
            "feasibility": feas,
        }
        if feas.get("success"):
            final_status = "feasible"
            iterations.append(rec)
            break
        if ray is None:
            final_status = "no_ray"
            iterations.append(rec)
            break
        if price_cols is None:
            final_status = "no_price_pool"
            iterations.append(rec)
            break
        log(f"iteration={it} pricing columns")
        pricing, add_cols = price_columns(price_cols, ray, skip=current_keys, args=args)
        rec["pricing"] = pricing
        iterations.append(rec)
        log("iteration={} status={} positives={} add={}".format(it, feas.get("message"), pricing.get("positive_score_count"), pricing.get("added_columns")))
        if not add_cols:
            final_status = "no_positive_priced_columns"
            break
        for col in add_cols:
            key = column_key(col)
            if key not in current_keys:
                current_cols.append(col)
                current_keys.add(key)

    return {
        "schema": "eq_odl1_rung2_hybrid_farkas_cg_loop_v1",
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
        "seed_meta": seed_meta,
        "price_meta": price_meta,
        "iterations": iterations,
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
    ap.add_argument("--face-pair-families", default=None)
    ap.add_argument("--seed-max-pairs", type=int, default=1024)
    ap.add_argument("--seed-max-band", type=int, default=4096)
    ap.add_argument("--price-max-pairs", type=int, default=0)
    ap.add_argument("--price-max-band", type=int, default=0)
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--add-top", type=int, default=1000)
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--solver-threads", type=int, default=16)
    ap.add_argument("--time-limit", type=float, default=900.0)
    ap.add_argument("--price-tol", type=float, default=1.0e-8)
    ap.add_argument("--presolve-off", action="store_true")
    ap.add_argument("--retry-no-ray-presolve-off", action="store_true")
    ap.add_argument("--ray-tol", type=float, default=1.0e-10)
    ap.add_argument("--row-tol", type=float, default=1.0e-8)
    ap.add_argument("--x-tol", type=float, default=1.0e-9)
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
        "last_message": last.get("feasibility", {}).get("message"),
        "last_positive": None if "pricing" not in last else last["pricing"].get("positive_score_count"),
        "summary": str(args.summary),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
