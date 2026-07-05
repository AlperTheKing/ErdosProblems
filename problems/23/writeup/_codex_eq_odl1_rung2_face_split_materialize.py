#!/usr/bin/env python3
"""Materialize a combined face-split cone solution into two exact subcerts.

Input:
  * a combined sparse column dictionary from
    _codex_eq_odl1_rung2_face_split_probe.py --emit-column-set combined;
  * a solution JSONL over that combined dictionary;
  * the original target beta vector, either via --target-beta-json or by
    rebuilding the standard chart target.

Output:
  * face-only column dictionary and remapped solution;
  * lift-only column dictionary and remapped solution;
  * face target beta = original target - lift contribution;
  * lift target beta = lift contribution.

If the combined certificate is exact, both emitted subcerts replay exactly with
_codex_eq_odl1_rung2_custom_cone_check.py, and their targets sum back to the
original target coefficientwise.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import _codex_eq_odl1_rung2_custom_cone_check as custom_check
import _codex_eq_odl1_rung2_scipy_core_probe as standard_probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def sparse_target_payload(values: list[Fraction]) -> dict[str, Any]:
    rows = [
        {"row": i, **fraction_record(v)}
        for i, v in enumerate(values)
        if v
    ]
    if not rows:
        rows = [{"row": 0, "num": 0, "den": 1}]
    return {"target_beta_sparse": rows}


def write_target(path: Path, values: list[Fraction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sparse_target_payload(values), separators=(",", ":"), sort_keys=True), encoding="utf-8")


def write_solution(path: Path, vals: dict[int, Fraction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for source_col in sorted(vals):
            val = vals[source_col]
            if val:
                f.write(json.dumps({"source_col": source_col, **fraction_record(val)}, sort_keys=True) + "\n")


def write_columns(
    path: Path,
    *,
    source_meta: dict[str, Any],
    column_set: str,
    columns: list[custom_check.SparseColumn],
) -> None:
    payload = dict(source_meta)
    payload["schema"] = "eq_odl1_rung2_face_split_columns_v1"
    payload["column_set"] = column_set
    payload["columns"] = [
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
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True), encoding="utf-8")


def contribution(row_count: int, columns: list[custom_check.SparseColumn], vals: dict[int, Fraction]) -> list[Fraction]:
    out = [Fraction(0) for _ in range(row_count)]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            out[row] += coeff * val
    return out


def read_target(args: argparse.Namespace, row_count: int) -> tuple[list[Fraction], str]:
    if args.target_beta_json:
        return source_check.read_target_beta(args.target_beta_json, row_count), "custom"
    prepared, _columns, _mat, _b_ub = standard_probe.build_lp(args.chart, args.dominant, args.band, args.support)
    if len(prepared.p_beta) != row_count:
        raise ValueError(f"standard target row count {len(prepared.p_beta)} != columns row count {row_count}")
    return prepared.p_beta[:], "prepared_p_beta"


def split_columns(
    columns: list[custom_check.SparseColumn],
    vals: dict[int, Fraction],
) -> tuple[list[custom_check.SparseColumn], dict[int, Fraction], list[custom_check.SparseColumn], dict[int, Fraction]]:
    face_columns: list[custom_check.SparseColumn] = []
    lift_columns: list[custom_check.SparseColumn] = []
    face_vals: dict[int, Fraction] = {}
    lift_vals: dict[int, Fraction] = {}
    face_map: dict[int, int] = {}
    lift_map: dict[int, int] = {}

    for old_idx, col in enumerate(columns):
        if col.kind.startswith("face_"):
            face_map[old_idx] = len(face_columns)
            face_columns.append(col)
        elif col.kind.startswith("lift_"):
            lift_map[old_idx] = len(lift_columns)
            lift_columns.append(col)
        else:
            raise ValueError(f"combined column {old_idx} has non face/lift kind {col.kind!r}")

    for old_idx, val in vals.items():
        if old_idx in face_map:
            new_idx = face_map[old_idx]
            face_vals[new_idx] = face_vals.get(new_idx, Fraction(0)) + val
        elif old_idx in lift_map:
            new_idx = lift_map[old_idx]
            lift_vals[new_idx] = lift_vals.get(new_idx, Fraction(0)) + val
        else:
            raise ValueError(f"solution references unknown combined column {old_idx}")

    return face_columns, face_vals, lift_columns, lift_vals


def run(args: argparse.Namespace) -> dict[str, Any]:
    columns, row_count, source_meta = custom_check.read_columns_json(args.columns_json)
    if source_meta.get("column_set") != "combined":
        raise ValueError("materializer expects columns JSON with column_set=combined")
    target_beta, target_mode = read_target(args, row_count)
    vals = source_check.read_source_solution(args.solution)

    face_columns, face_vals, lift_columns, lift_vals = split_columns(columns, vals)
    lift_beta = contribution(row_count, lift_columns, lift_vals)
    face_beta = [t - l for t, l in zip(target_beta, lift_beta)]
    face_contrib = contribution(row_count, face_columns, face_vals)
    combined_residual = [f - c for f, c in zip(face_beta, face_contrib)]
    identity_ok = all((f + l) == t for f, l, t in zip(face_beta, lift_beta, target_beta))

    write_columns(args.face_columns_json, source_meta=source_meta, column_set="face", columns=face_columns)
    write_columns(args.lift_columns_json, source_meta=source_meta, column_set="lift", columns=lift_columns)
    write_solution(args.face_solution, face_vals)
    write_solution(args.lift_solution, lift_vals)
    write_target(args.face_target_beta_json, face_beta)
    write_target(args.lift_target_beta_json, lift_beta)

    negative_residuals = [(i, x) for i, x in enumerate(combined_residual) if x < 0]
    out: dict[str, Any] = {
        "schema": "eq_odl1_rung2_face_split_materialize_v1",
        "columns_json": str(args.columns_json),
        "solution": str(args.solution),
        "target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
        "target_beta_mode": target_mode,
        "row_count": row_count,
        "combined_columns": len(columns),
        "face_columns": len(face_columns),
        "lift_columns": len(lift_columns),
        "combined_solution_nonzero": sum(1 for v in vals.values() if v),
        "face_solution_nonzero": sum(1 for v in face_vals.values() if v),
        "lift_solution_nonzero": sum(1 for v in lift_vals.values() if v),
        "solution_negative_count": sum(1 for v in vals.values() if v < 0),
        "identity_ok": identity_ok,
        "combined_negative_residual_count": len(negative_residuals),
        "combined_min_residual": custom_check.replay.fmt_fraction(min(combined_residual) if combined_residual else Fraction(0)),
        "combined_negative_rows_prefix": [
            {"row": i, "residual": custom_check.replay.fmt_fraction(x)}
            for i, x in negative_residuals[:10]
        ],
        "outputs": {
            "face_columns_json": str(args.face_columns_json),
            "lift_columns_json": str(args.lift_columns_json),
            "face_solution": str(args.face_solution),
            "lift_solution": str(args.lift_solution),
            "face_target_beta_json": str(args.face_target_beta_json),
            "lift_target_beta_json": str(args.lift_target_beta_json),
        },
    }
    out["exact_ok"] = out["solution_negative_count"] == 0 and out["identity_ok"] and out["combined_negative_residual_count"] == 0
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--columns-json", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--target-beta-json", type=Path, default=None)
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--face-columns-json", type=Path, required=True)
    ap.add_argument("--lift-columns-json", type=Path, required=True)
    ap.add_argument("--face-solution", type=Path, required=True)
    ap.add_argument("--lift-solution", type=Path, required=True)
    ap.add_argument("--face-target-beta-json", type=Path, required=True)
    ap.add_argument("--lift-target-beta-json", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "exact_ok": out["exact_ok"],
                "identity_ok": out["identity_ok"],
                "combined_negative_residual_count": out["combined_negative_residual_count"],
                "face_columns": out["face_columns"],
                "lift_columns": out["lift_columns"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
