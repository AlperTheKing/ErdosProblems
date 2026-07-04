#!/usr/bin/env python3
"""Floor-buffer exact certificate attempt for EQ-ODL1 Rung-2 charts.

The float LP only finds an interior nonnegative multiplier vector. Acceptance is
an exact Fraction check of residual base b = p - A lambda_Q >= 0 after flooring
all multipliers to a shared denominator Q.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_support_lp as support
import _codex_eq_odl1_rung2_modular_replay as replay


def fmt_fraction(q: Fraction) -> str:
    return replay.fmt_fraction(q)


def build_prepared_columns(k: int, dominant: int, band: str, support_mode: str):
    prepared = support.prepare_chart(k)
    gen_names = prepared.chart.generator_names
    columns = support.selected_degree2_columns(
        prepared.p_beta,
        prepared.beta_index,
        prepared.gen_polys,
        gen_names,
        dominant,
        support_mode,
        None,
    )
    columns.extend(support.selected_band_columns(prepared.p_beta, prepared.beta_index, band, support_mode, None))
    print(f"floor-buffer selected columns={len(columns)}", flush=True)
    return prepared, columns

def build_sparse_columns(columns, row_count: int):
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    nminus = [Fraction(0) for _ in range(row_count)]
    col_l1 = [Fraction(0) for _ in columns]
    for j, col in enumerate(columns):
        total = Fraction(0)
        for i, coeff in col.terms:
            rows.append(i)
            cols.append(j)
            data.append(float(coeff))
            total += abs(coeff)
            if coeff < 0:
                nminus[i] += -coeff
        col_l1[j] = total
    mat = coo_matrix((data, (rows, cols)), shape=(row_count, len(columns))).tocsr()
    return mat, nminus, col_l1


def solve_stage1(mat, p_beta: list[Fraction], nminus: list[Fraction], time_limit: float, method: str):
    row_count, col_count = mat.shape
    theta_rows = [i for i, x in enumerate(nminus) if x]
    theta_col = coo_matrix(
        ([float(nminus[i]) for i in theta_rows], (theta_rows, [0] * len(theta_rows))),
        shape=(row_count, 1),
    ).tocsr()
    from scipy.sparse import hstack

    a_ub = hstack([mat, theta_col], format="csr")
    b_ub = np.array([float(x) for x in p_beta], dtype=float)
    c = np.zeros(col_count + 1, dtype=float)
    c[-1] = -1.0
    res = linprog(
        c=c,
        A_ub=a_ub,
        b_ub=b_ub,
        bounds=[(0, None)] * (col_count + 1),
        method=method,
        options={"time_limit": time_limit},
    )
    return res


def solve_stage2(mat, p_beta: list[Fraction], nminus: list[Fraction], col_l1: list[Fraction], theta0: float, time_limit: float, method: str):
    b_ub = np.array([float(p) - theta0 * float(nm) for p, nm in zip(p_beta, nminus)], dtype=float)
    costs = np.array([1.0 + math.log1p(float(x)) for x in col_l1], dtype=float)
    res = linprog(
        c=costs,
        A_ub=mat,
        b_ub=b_ub,
        bounds=[(0, None)] * mat.shape[1],
        method=method,
        options={"time_limit": time_limit},
    )
    return res


def floor_solution(raw, qden: int, eps_sol: float) -> list[Fraction]:
    out: list[Fraction] = []
    for x in raw:
        val = max(0.0, float(x) - eps_sol)
        out.append(Fraction(math.floor(qden * val), qden))
    return out


def exact_residual(p_beta: list[Fraction], columns, lambdas: list[Fraction]):
    residual = p_beta[:]
    for val, col in zip(lambdas, columns):
        if not val:
            continue
        for i, coeff in col.terms:
            residual[i] -= coeff * val
    return residual


def write_certificate(path: Path, *, args, prepared, columns, lambdas: list[Fraction], residual: list[Fraction], q_power: int, theta_max: float, theta0: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        meta = {
            "type": "meta",
            "schema": "eq_odl1_rung2_floor_buffer_cert_v1",
            "chart": args.chart,
            "dominant": args.dominant,
            "dominant_name": prepared.chart.generator_names[args.dominant],
            "band": args.band,
            "support": args.support,
            "q_power": q_power,
            "q_denominator": 1 << q_power,
            "theta_max_float": theta_max,
            "theta0_float": theta0,
            "row_count": len(residual),
            "column_count": len(columns),
        }
        f.write(json.dumps(meta, sort_keys=True) + "\n")
        for j, (col, val) in enumerate(zip(columns, lambdas)):
            if not val:
                continue
            f.write(json.dumps({
                "type": "mult",
                "col": j,
                "kind": col.kind,
                "name": col.name,
                "multiplier_exp": list(col.multiplier_exp),
                "num": val.numerator,
                "den": val.denominator,
            }, sort_keys=True) + "\n")
        for i, val in enumerate(residual):
            if val:
                f.write(json.dumps({
                    "type": "base",
                    "row": i,
                    "beta": list(prepared.betas[i]),
                    "num": val.numerator,
                    "den": val.denominator,
                }, sort_keys=True) + "\n")


def run(args):
    prepared, columns = build_prepared_columns(args.chart, args.dominant, args.band, args.support)
    print("floor-buffer sparse build start", flush=True)
    sparse_t0 = time.time()
    mat, nminus, col_l1 = build_sparse_columns(columns, len(prepared.betas))
    print(
        f"floor-buffer sparse build done seconds={time.time() - sparse_t0:.3f} "
        f"shape={mat.shape} nnz={mat.nnz}",
        flush=True,
    )
    print("floor-buffer stage1 start", flush=True)
    stage1_t0 = time.time()
    stage1 = solve_stage1(mat, prepared.p_beta, nminus, args.time_limit_stage1, args.method)
    print(
        f"floor-buffer stage1 done seconds={time.time() - stage1_t0:.3f} "
        f"success={stage1.success} status={stage1.status}",
        flush=True,
    )
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_floor_buffer_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "method": args.method,
        "rows": mat.shape[0],
        "columns": mat.shape[1],
        "nnz": int(mat.nnz),
        "nminus_nonzero_rows": sum(1 for x in nminus if x),
        "stage1": {
            "success": bool(stage1.success),
            "status": int(stage1.status),
            "message": stage1.message,
        },
    }
    if not stage1.success:
        return out
    theta_max = max(0.0, float(stage1.x[-1]))
    theta0 = theta_max * args.theta_fraction
    out["stage1"].update({"theta_max": theta_max, "objective": float(stage1.fun)})
    if theta0 <= 0:
        out["abort"] = "nonpositive_theta0"
        return out

    print("floor-buffer stage2 start", flush=True)
    stage2_t0 = time.time()
    stage2 = solve_stage2(mat, prepared.p_beta, nminus, col_l1, theta0, args.time_limit_stage2, args.method)
    print(
        f"floor-buffer stage2 done seconds={time.time() - stage2_t0:.3f} "
        f"success={stage2.success} status={stage2.status}",
        flush=True,
    )
    out["stage2"] = {
        "success": bool(stage2.success),
        "status": int(stage2.status),
        "message": stage2.message,
    }
    if not stage2.success:
        return out
    out["stage2"].update({"objective": float(stage2.fun), "theta0": theta0})

    min_q_power = max(args.min_q_power, math.ceil(math.log2(4.0 / max(theta0, 1.0e-300))))
    attempts = []
    best_residual = None
    best_lambdas = None
    best_power = None
    for q_power in range(min_q_power, args.max_q_power + 1):
        qden = 1 << q_power
        lambdas = floor_solution(stage2.x, qden, args.eps_sol)
        residual = exact_residual(prepared.p_beta, columns, lambdas)
        neg = [(i, v) for i, v in enumerate(residual) if v < 0]
        nonzero_mults = sum(1 for v in lambdas if v)
        attempt = {
            "q_power": q_power,
            "q_denominator": qden,
            "nonzero_multipliers": nonzero_mults,
            "negative_residual_count": len(neg),
            "residual_min": fmt_fraction(min(residual) if residual else Fraction(0)),
            "residual_zero_count": sum(1 for v in residual if v == 0),
        }
        if neg:
            attempt["negative_rows_prefix"] = [
                {"row": int(i), "beta": list(prepared.betas[i]), "residual": fmt_fraction(v)}
                for i, v in neg[:10]
            ]
        attempts.append(attempt)
        if best_residual is None or len(neg) < best_residual[0]:
            best_residual = (len(neg), min(residual) if residual else Fraction(0))
            best_lambdas = lambdas
            best_power = q_power
        if not neg:
            out["exact_ok"] = True
            out["q_power"] = q_power
            out["q_denominator"] = qden
            out["nonzero_multipliers"] = nonzero_mults
            out["residual_min"] = fmt_fraction(min(residual) if residual else Fraction(0))
            out["residual_zero_count"] = attempt["residual_zero_count"]
            out["attempts"] = attempts
            if args.certificate:
                write_certificate(
                    args.certificate,
                    args=args,
                    prepared=prepared,
                    columns=columns,
                    lambdas=lambdas,
                    residual=residual,
                    q_power=q_power,
                    theta_max=theta_max,
                    theta0=theta0,
                )
                out["certificate"] = str(args.certificate)
            return out
    out["exact_ok"] = False
    out["attempts"] = attempts
    if best_lambdas is not None and args.certificate_on_fail:
        residual = exact_residual(prepared.p_beta, columns, best_lambdas)
        write_certificate(
            args.certificate_on_fail,
            args=args,
            prepared=prepared,
            columns=columns,
            lambdas=best_lambdas,
            residual=residual,
            q_power=int(best_power or min_q_power),
            theta_max=theta_max,
            theta0=theta0,
        )
        out["best_failed_certificate"] = str(args.certificate_on_fail)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--method", default="highs", choices=["highs", "highs-ds", "highs-ipm"])
    ap.add_argument("--time-limit-stage1", type=float, default=120.0)
    ap.add_argument("--time-limit-stage2", type=float, default=120.0)
    ap.add_argument("--theta-fraction", type=float, default=0.5)
    ap.add_argument("--eps-sol", type=float, default=1.0e-9)
    ap.add_argument("--min-q-power", type=int, default=14)
    ap.add_argument("--max-q-power", type=int, default=24)
    ap.add_argument("--certificate", type=Path)
    ap.add_argument("--certificate-on-fail", type=Path)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_floor_buffer_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": out.get("exact_ok"),
        "stage1": out.get("stage1"),
        "stage2": out.get("stage2"),
        "q_power": out.get("q_power"),
        "nonzero_multipliers": out.get("nonzero_multipliers"),
        "residual_min": out.get("residual_min"),
        "attempts_tail": out.get("attempts", [])[-3:],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

