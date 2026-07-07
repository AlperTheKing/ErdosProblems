#!/usr/bin/env python3
"""HiGHS basis extraction and exact-core probe for one Rung-2 support LP chart.

The support LP script can find floating feasible dominance certificates, but naive
coefficient rounding does not pass the exact residual gate.  This probe solves the
same LP through highspy, extracts the simplex basis, and identifies the active
row/basic-column subsystem that would have to be solved exactly.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import highspy
import numpy as np
import sympy as sp

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_support_lp as support


INF = 1.0e30

def stable_column_weight(col, mode: str) -> float:
    if mode == "sum":
        return 1.0
    h = 1469598103934665603
    for part in (col.kind, col.name, str(col.multiplier_exp)):
        for b in part.encode("utf-8"):
            h ^= b
            h = (h * 1099511628211) & ((1 << 64) - 1)
    frac = (h % 1000003) / 1000003.0
    if mode == "lex-small":
        return 1.0 + 1.0e-6 * frac
    if mode == "lex-large":
        return 1.0 + 1.0e-3 * frac
    if mode == "family":
        family = {"gen": 0.0, "delta": 0.37, "band": 0.73}.get(col.kind, 0.19)
        return 1.0 + 1.0e-4 * family + 1.0e-7 * frac
    raise ValueError(mode)


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 1024 and q.denominator.bit_length() < 1024:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def build_item(k: int, dominant: int, band: str, support_mode: str, objective: str):
    prepared = support.prepare_chart(k)
    chart = prepared.chart
    columns = support.selected_degree2_columns(
        prepared.p_beta,
        prepared.beta_index,
        prepared.gen_polys,
        chart.generator_names,
        dominant,
        support_mode,
        None,
    )
    columns.extend(support.selected_band_columns(prepared.p_beta, prepared.beta_index, band, support_mode, None))
    return prepared, columns


def build_highs(prepared: support.PreparedChart, columns: list[support.Column], time_limit: float, presolve: str, solver: str, threads: int, objective: str):
    num_rows = len(prepared.betas)
    num_cols = len(columns)
    starts = [0]
    indices: list[int] = []
    values: list[float] = []
    for col in columns:
        for i, coeff in col.terms:
            indices.append(i)
            values.append(float(coeff))
        starts.append(len(indices))

    lp = highspy.HighsLp()
    lp.num_col_ = num_cols
    lp.num_row_ = num_rows
    lp.col_cost_ = np.array([stable_column_weight(col, objective) for col in columns], dtype=np.float64)
    lp.col_lower_ = np.zeros(num_cols, dtype=np.float64)
    lp.col_upper_ = np.full(num_cols, INF, dtype=np.float64)
    lp.row_lower_ = np.full(num_rows, -INF, dtype=np.float64)
    lp.row_upper_ = np.array([float(v) for v in prepared.p_beta], dtype=np.float64)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.num_col_ = num_cols
    lp.a_matrix_.num_row_ = num_rows
    lp.a_matrix_.start_ = np.array(starts[:-1], dtype=np.int32)
    lp.a_matrix_.p_end_ = np.array(starts[1:], dtype=np.int32)
    lp.a_matrix_.index_ = np.array(indices, dtype=np.int32)
    lp.a_matrix_.value_ = np.array(values, dtype=np.float64)

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", float(time_limit))
    h.setOptionValue("solver", solver)
    h.setOptionValue("presolve", presolve)
    if threads > 0:
        h.setOptionValue("threads", int(threads))
    h.passModel(lp)
    return h


def exact_core_probe(
    prepared: support.PreparedChart,
    columns: list[support.Column],
    basis,
    max_exact_dim: int,
) -> dict[str, object]:
    basic = highspy.HighsBasisStatus.kBasic
    basic_cols = [j for j, st in enumerate(basis.col_status) if st == basic]
    active_rows = [i for i, st in enumerate(basis.row_status) if st != basic]
    out: dict[str, object] = {
        "basic_cols": len(basic_cols),
        "active_rows": len(active_rows),
        "square_core": len(basic_cols) == len(active_rows),
        "attempted_exact_solve": False,
    }
    if len(basic_cols) != len(active_rows):
        return out
    if len(basic_cols) > max_exact_dim:
        out["exact_solve_skipped_reason"] = f"core dimension {len(basic_cols)} exceeds max_exact_dim {max_exact_dim}"
        return out

    row_pos = {row: r for r, row in enumerate(active_rows)}
    mat = [[Fraction(0) for _ in basic_cols] for _ in active_rows]
    for cpos, col_index in enumerate(basic_cols):
        for row, coeff in columns[col_index].terms:
            rpos = row_pos.get(row)
            if rpos is not None:
                mat[rpos][cpos] = coeff
    rhs = [prepared.p_beta[row] for row in active_rows]
    out["attempted_exact_solve"] = True
    try:
        M = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in mat])
        b = sp.Matrix([sp.Rational(x.numerator, x.denominator) for x in rhs])
        sol = M.LUsolve(b)
    except Exception as exc:  # pragma: no cover - diagnostic path
        out["exact_solve_error"] = repr(exc)
        return out

    q = [Fraction(0) for _ in columns]
    min_basic = None
    neg_basic = 0
    for col_index, value in zip(basic_cols, sol):
        val = Fraction(int(value.p), int(value.q))
        q[col_index] = val
        min_basic = val if min_basic is None else min(min_basic, val)
        if val < 0:
            neg_basic += 1
    residual = prepared.p_beta[:]
    nonzero = 0
    for val, col in zip(q, columns):
        if not val:
            continue
        nonzero += 1
        for i, coeff in col.terms:
            residual[i] -= coeff * val
    out.update({
        "exact_nonzero": nonzero,
        "exact_min_basic": fmt_fraction(min_basic or Fraction(0)),
        "exact_negative_basic_count": neg_basic,
        "exact_min_residual": fmt_fraction(min(residual) if residual else Fraction(0)),
        "exact_negative_residual_count": sum(1 for r in residual if r < 0),
        "exact_ok": neg_basic == 0 and all(r >= 0 for r in residual),
    })
    return out


def export_basis_core(path: Path, prepared: support.PreparedChart, columns: list[support.Column], basis) -> dict[str, object]:
    basic = highspy.HighsBasisStatus.kBasic
    basic_cols = [j for j, st in enumerate(basis.col_status) if st == basic]
    active_rows = [i for i, st in enumerate(basis.row_status) if st != basic]
    if len(basic_cols) != len(active_rows):
        raise RuntimeError(f"basis not square: {len(basic_cols)} cols vs {len(active_rows)} rows")

    terms, rhs, nnz_by_col = replay.extract_core(prepared, columns, basic_cols, active_rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "dimension": len(basic_cols), "terms": len(terms)}) + "\n")
        for j, source_col in enumerate(basic_cols):
            f.write(json.dumps({"type": "col", "col": j, "source_col": int(source_col)}) + "\n")
        for i, row_index in enumerate(active_rows):
            f.write(json.dumps({"type": "selected_row", "row": i, "source_row": int(row_index)}) + "\n")
        for i, val in enumerate(rhs):
            f.write(json.dumps({"type": "rhs", "row": i, "value": fmt_fraction(val)}) + "\n")
        for i, j, coeff in terms:
            f.write(json.dumps({"type": "term", "row": i, "col": j, "value": fmt_fraction(coeff)}) + "\n")
    return {
        "dimension": len(basic_cols),
        "terms": len(terms),
        "rhs_nonzero": sum(1 for x in rhs if x),
        "nnz_by_col_min": min(nnz_by_col) if nnz_by_col else 0,
        "nnz_by_col_max": max(nnz_by_col) if nnz_by_col else 0,
        "export_core": str(path),
        "basic_cols_prefix": basic_cols[:20],
        "active_rows_prefix": active_rows[:20],
    }


def run(args) -> dict[str, object]:
    prepared, columns = build_item(args.chart, args.dominant, args.band, args.support, args.objective)
    h = build_highs(prepared, columns, args.time_limit, args.presolve, args.solver, args.threads, args.objective)
    status = h.run()
    model_status = h.getModelStatus()
    basis = h.getBasis()
    sol = h.getSolution()
    col_status_counts: dict[str, int] = {}
    row_status_counts: dict[str, int] = {}
    for st in basis.col_status:
        key = h.basisStatusToString(st)
        col_status_counts[key] = col_status_counts.get(key, 0) + 1
    for st in basis.row_status:
        key = h.basisStatusToString(st)
        row_status_counts[key] = row_status_counts.get(key, 0) + 1
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_basis_replay_probe_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "objective": args.objective,
        "presolve": args.presolve,
        "solver": args.solver,
        "threads": args.threads,
        "highs_run_status": str(status),
        "model_status": h.modelStatusToString(model_status),
        "variables": len(columns),
        "constraints": len(prepared.betas),
        "float_nonzero": sum(1 for x in sol.col_value if x > 1e-9),
        "col_status_counts": col_status_counts,
        "row_status_counts": row_status_counts,
    }
    if "Optimal" in out["model_status"]:
        out["exact_core_probe"] = exact_core_probe(prepared, columns, basis, args.max_exact_dim)
        if args.export_core:
            out["export_core"] = export_basis_core(args.export_core, prepared, columns, basis)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", choices=["negative", "all"], default="negative")
    ap.add_argument("--objective", choices=["sum", "lex-small", "lex-large", "family"], default="sum")
    ap.add_argument("--presolve", choices=["on", "off", "choose"], default="off")
    ap.add_argument("--solver", choices=["simplex", "ipm", "choose"], default="simplex")
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--max-exact-dim", type=int, default=700)
    ap.add_argument("--export-core", type=Path, default=None)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_basis_probe_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "model_status": out.get("model_status"),
        "variables": out.get("variables"),
        "float_nonzero": out.get("float_nonzero"),
        "exact_core_probe": out.get("exact_core_probe"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()





