#!/usr/bin/env python3
"""EQ-ODL1 Rung-2 band-only Bernstein LP pass.

For each height chart k and band B in {2s-1, 1-2s}, solve
    P_k = P0 + B * Q
with P0 and Q Bernstein-coefficient nonnegative on the simplex.
Q has degree <= 10, represented in the degree-10 Bernstein basis.  The residual
P0 is checked in the degree-11 Bernstein basis.  This is the second Rung-2
triviality stage before full dominance LPs.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_rung2_charts as charts


BANDS = ("near_2s_minus_1", "inf_1_minus_2s")


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 1024 and q.denominator.bit_length() < 1024:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def band_coeff(alpha: tuple[int, ...], coord: int, degree_q: int, band: str) -> Fraction:
    base = Fraction(alpha[coord] + 1, degree_q + 1)
    if band == "near_2s_minus_1":
        return base if coord == 0 else -base
    if band == "inf_1_minus_2s":
        return -base if coord == 0 else base
    raise ValueError(band)


def build_band_matrix(num_vars: int, degree_q: int, band: str):
    alphas = charts.all_exps(num_vars, degree_q)
    betas = charts.all_exps(num_vars, degree_q + 1)
    beta_index = {beta: i for i, beta in enumerate(betas)}
    rows = []
    cols = []
    data = []
    exact_cols: list[list[tuple[int, Fraction]]] = []
    for j, alpha in enumerate(alphas):
        col_terms = []
        for coord in range(num_vars):
            beta = list(alpha)
            beta[coord] += 1
            beta_t = tuple(beta)
            coeff = band_coeff(alpha, coord, degree_q, band)
            i = beta_index[beta_t]
            rows.append(i)
            cols.append(j)
            data.append(float(coeff))
            col_terms.append((i, coeff))
        exact_cols.append(col_terms)
    mat = coo_matrix((data, (rows, cols)), shape=(len(betas), len(alphas))).tocsr()
    return alphas, betas, mat, exact_cols


def exact_replay(p_beta: list[Fraction], exact_cols: list[list[tuple[int, Fraction]]], raw, max_denominators: list[int]):
    attempts = []
    for max_den in max_denominators:
        q = [Fraction(str(max(0.0, float(x)))).limit_denominator(max_den) for x in raw]
        residual = p_beta[:]
        nonzero = 0
        for val, col_terms in zip(q, exact_cols):
            if not val:
                continue
            nonzero += 1
            for i, coeff in col_terms:
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
            cert = [fmt_fraction(v) for v in q]
            return True, {
                "max_denominator": max_den,
                "nonzero_multiplier_count": nonzero,
                "residual_min_coeff": fmt_fraction(min_res),
                "certificate_q": cert,
                "attempts": attempts,
            }
    return False, {"attempts": attempts}


def solve_one(k: int, band: str, time_limit: float, objective: str, max_denominators: list[int], store_certificate: bool) -> dict[str, object]:
    chart = charts.build_chart(k)
    p_map = charts.bernstein_degree_coefficients(chart.target, chart.variables, charts.TARGET_DEGREE)
    betas11 = charts.all_exps(len(chart.variables), charts.TARGET_DEGREE)
    p_beta = [p_map[beta] for beta in betas11]
    alphas, betas, mat, exact_cols = build_band_matrix(len(chart.variables), charts.TARGET_DEGREE - 1, band)
    if betas != betas11:
        raise RuntimeError("beta order mismatch")
    c = np.ones(len(alphas), dtype=float) if objective == "sum" else np.zeros(len(alphas), dtype=float)
    b_ub = np.array([float(v) for v in p_beta], dtype=float)
    print(f"band LP k={k} band={band} vars={len(alphas)} constraints={len(betas)}", flush=True)
    options = {} if time_limit <= 0 else {"time_limit": float(time_limit)}
    res = linprog(c=c, A_ub=mat, b_ub=b_ub, bounds=[(0, None)] * len(alphas), method="highs", options=options)
    out = {
        "k": k,
        "band": band,
        "variables": len(alphas),
        "constraints": len(betas),
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
        "exact_ok": None,
    }
    if not res.success:
        return out
    out["float_nonzero"] = int(sum(1 for x in res.x if x > 1e-9))
    ok, check = exact_replay(p_beta, exact_cols, res.x, max_denominators)
    out["exact_ok"] = ok
    if ok and not store_certificate:
        check.pop("certificate_q", None)
    out["exact_check"] = check
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--charts", default="all", help="comma list of height chart indices or all")
    ap.add_argument("--bands", default="all", help="comma list from near_2s_minus_1,inf_1_minus_2s or all")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--objective", choices=["sum", "zero"], default="sum")
    ap.add_argument("--max-den", default="1000,10000,1000000")
    ap.add_argument("--store-certificate", action="store_true")
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_band_lp_v1.json"))
    args = ap.parse_args()
    ks = list(range(10)) if args.charts == "all" else [int(x) for x in args.charts.split(",") if x]
    bands = list(BANDS) if args.bands == "all" else [x for x in args.bands.split(",") if x]
    max_denominators = [int(x) for x in args.max_den.split(",") if x]
    rows = []
    for k in ks:
        for band in bands:
            rows.append(solve_one(k, band, args.time_limit, args.objective, max_denominators, args.store_certificate))
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            partial = summarize(rows, complete=False)
            args.summary.write_text(json.dumps(partial, indent=2, sort_keys=True), encoding="utf-8")
    out = summarize(rows, complete=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ["rows", "success", "exact_ok", "timeouts", "infeasible_or_failed"]}, sort_keys=True))


def summarize(rows: list[dict[str, object]], complete: bool) -> dict[str, object]:
    return {
        "schema": "eq_odl1_rung2_band_lp_v1",
        "complete": complete,
        "rows": len(rows),
        "success": sum(1 for r in rows if r.get("success")),
        "exact_ok": sum(1 for r in rows if r.get("exact_ok") is True),
        "timeouts": sum(1 for r in rows if r.get("lp_status") == 1),
        "infeasible_or_failed": sum(1 for r in rows if not r.get("success")),
        "items": rows,
    }


if __name__ == "__main__":
    main()
