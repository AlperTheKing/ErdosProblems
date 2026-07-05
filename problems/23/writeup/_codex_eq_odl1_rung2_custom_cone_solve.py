#!/usr/bin/env python3
"""Float probe for arbitrary sparse EQ-ODL1 Rung-2 cone dictionaries.

This is the solver companion to _codex_eq_odl1_rung2_custom_cone_check.py.
It reads a column JSON file plus a target beta JSON file, solves the cone
membership LP

    A x <= target,  x >= 0,

and optionally writes a rationalized candidate solution.  Any candidate is only
advisory until replayed by the exact checker.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_rung2_custom_cone_check as custom_check
import _codex_eq_odl1_rung2_source_solution_check as source_check


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 1024 and q.denominator.bit_length() < 1024:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def stable_column_weight(col: custom_check.SparseColumn, mode: str) -> float:
    if mode == "zero":
        return 0.0
    if mode == "sum":
        return 1.0
    h = 1469598103934665603
    for part in (col.kind, col.name, str(col.multiplier_exp)):
        for b in part.encode("utf-8"):
            h ^= b
            h = (h * 1099511628211) & ((1 << 64) - 1)
    frac = (h % 1000003) / 1000003.0
    if mode == "family":
        family = 0.0
        if col.kind.startswith("face_"):
            family = 0.17
        elif col.kind.startswith("lift_"):
            family = 0.43
        elif col.kind.startswith("band"):
            family = 0.73
        return 1.0 + 1.0e-4 * family + 1.0e-7 * frac
    if mode == "lex-small":
        return 1.0 + 1.0e-6 * frac
    raise ValueError(f"unknown objective mode {mode!r}")


def build_matrix(columns: list[custom_check.SparseColumn], row_count: int):
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for j, col in enumerate(columns):
        for i, coeff in col.terms:
            rows.append(i)
            cols.append(j)
            data.append(float(coeff))
    return coo_matrix((data, (rows, cols)), shape=(row_count, len(columns))).tocsr()


def write_solution(path: Path, values: list[Fraction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for source_col, val in enumerate(values):
            if val:
                f.write(json.dumps({"source_col": source_col, **fraction_record(val)}, sort_keys=True) + "\n")


def exact_replay(
    columns: list[custom_check.SparseColumn],
    row_count: int,
    target_beta: list[Fraction],
    raw_x: np.ndarray,
    *,
    max_den: int,
    solution_jsonl: Path | None,
) -> dict[str, object]:
    vals = [Fraction(float(x)).limit_denominator(max_den) if x > 0 else Fraction(0) for x in raw_x]
    if solution_jsonl is not None:
        write_solution(solution_jsonl, vals)
    val_map = {i: v for i, v in enumerate(vals) if v}
    ns = argparse.Namespace(solution=solution_jsonl or Path("<memory>"), columns_json=None, target_beta_json=None)
    out = custom_check.check_cone(
        val_map,
        columns,
        row_count,
        target_beta,
        args=ns,
        column_meta={"mode": "custom_cone_solve_replay"},
    )
    out["max_den"] = max_den
    out["solution_jsonl"] = str(solution_jsonl) if solution_jsonl is not None else None
    return out


def run(args: argparse.Namespace) -> dict[str, object]:
    columns, row_count, meta = custom_check.read_columns_json(args.columns_json)
    target_beta = source_check.read_target_beta(args.target_beta_json, row_count)
    mat = build_matrix(columns, row_count)
    b_ub = np.array([float(x) for x in target_beta], dtype=float)
    c = np.array([stable_column_weight(col, args.objective) for col in columns], dtype=float)
    res = linprog(
        c=c,
        A_ub=mat,
        b_ub=b_ub,
        bounds=[(0, None)] * len(columns),
        method=args.method,
        options={"time_limit": args.time_limit},
    )
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_custom_cone_solve_v1",
        "columns_json": str(args.columns_json),
        "target_beta_json": str(args.target_beta_json),
        "column_set": meta.get("column_set"),
        "chart": meta.get("chart"),
        "dominant": meta.get("dominant"),
        "dominant_name": meta.get("dominant_name"),
        "band": meta.get("band"),
        "method": args.method,
        "objective_mode": args.objective,
        "columns": len(columns),
        "row_count": row_count,
        "column_term_count": sum(len(c.terms) for c in columns),
        "target_beta_nonzero_count": sum(1 for x in target_beta if x),
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
    }
    if not res.success:
        return out
    residual = b_ub - mat.dot(res.x)
    out.update(
        {
            "objective": float(res.fun),
            "float_nonzero": int(np.sum(res.x > args.x_tol)),
            "float_min_x": float(res.x.min()) if len(res.x) else 0.0,
            "float_max_x": float(res.x.max()) if len(res.x) else 0.0,
            "float_min_residual": float(residual.min()) if len(residual) else 0.0,
            "float_max_residual": float(residual.max()) if len(residual) else 0.0,
            "float_negative_residual_count": int(np.sum(residual < -args.row_tol)),
            "x_tol": args.x_tol,
            "row_tol": args.row_tol,
        }
    )
    if args.exact_replay_candidate:
        out["exact_replay_candidate"] = exact_replay(
            columns,
            row_count,
            target_beta,
            res.x,
            max_den=args.max_den,
            solution_jsonl=args.candidate_solution_jsonl,
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--columns-json", type=Path, required=True)
    ap.add_argument("--target-beta-json", type=Path, required=True)
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")
    ap.add_argument("--objective", choices=["zero", "sum", "family", "lex-small"], default="sum")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--x-tol", type=float, default=1.0e-9)
    ap.add_argument("--row-tol", type=float, default=1.0e-9)
    ap.add_argument("--exact-replay-candidate", action="store_true")
    ap.add_argument("--max-den", type=int, default=10**12)
    ap.add_argument("--candidate-solution-jsonl", type=Path, default=None)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "success": out.get("success"),
                "lp_status": out.get("lp_status"),
                "float_nonzero": out.get("float_nonzero"),
                "float_negative_residual_count": out.get("float_negative_residual_count"),
                "exact_ok": (out.get("exact_replay_candidate") or {}).get("exact_ok")
                if isinstance(out.get("exact_replay_candidate"), dict)
                else None,
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
