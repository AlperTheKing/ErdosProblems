#!/usr/bin/env python3
"""Exact full LP checker for a source-column solution JSONL."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as probe


def read_source_solution(path: Path) -> dict[int, Fraction]:
    vals: dict[int, Fraction] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            source_col = int(rec["source_col"])
            val = Fraction(int(rec["num"]), int(rec["den"]))
            vals[source_col] = vals.get(source_col, Fraction(0)) + val
    return vals


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, list) and len(value) == 2:
        return Fraction(int(value[0]), int(value[1]))
    if isinstance(value, dict):
        if "num" in value and "den" in value:
            return Fraction(int(value["num"]), int(value["den"]))
        if "value" in value:
            return parse_fraction(value["value"])
    raise ValueError(f"cannot parse Fraction from {value!r}")


def read_target_beta(path: Path, row_count: int) -> list[Fraction]:
    """Read an exact target beta vector for custom face-split targets.

    Accepted JSON forms:
      * dense list: ["1/2", [3, 4], {"num": 5, "den": 6}, ...]
      * {"target_beta": dense-list}
      * {"target_beta": [{"row": i, "num": n, "den": d}, ...]} sparse rows
      * {"target_beta_sparse": [{"row": i, "value": "n/d"}, ...]}

    Sparse forms default unspecified rows to zero.  Dense forms must have the
    same length as the prepared Bernstein row count.
    """

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict) and "target_beta_sparse" in data:
        raw = data["target_beta_sparse"]
    elif isinstance(data, dict) and "target_beta" in data:
        raw = data["target_beta"]
    else:
        raise ValueError("target beta JSON must be a list or contain target_beta/target_beta_sparse")

    if isinstance(raw, list) and raw and all(isinstance(x, dict) and "row" in x for x in raw):
        out = [Fraction(0) for _ in range(row_count)]
        for rec in raw:
            row = int(rec["row"])
            if row < 0 or row >= row_count:
                raise ValueError(f"target beta row out of range: {row}")
            out[row] += parse_fraction(rec)
        return out

    if not isinstance(raw, list):
        raise ValueError("target beta payload must be a list")
    if len(raw) != row_count:
        raise ValueError(f"dense target beta length {len(raw)} != row count {row_count}")
    return [parse_fraction(x) for x in raw]


def check_values_against_target(
    vals: dict[int, Fraction],
    prepared: support.PreparedChart,  # type: ignore[name-defined]
    columns,
    target_beta: list[Fraction],
    *,
    args,
) -> dict:
    residual = target_beta[:]
    invalid_cols = [c for c in vals if c < 0 or c >= len(columns)]
    if invalid_cols:
        raise ValueError(f"invalid source columns: {invalid_cols[:10]}")
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    out = {
        "schema": "eq_odl1_rung2_source_solution_check_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "solution": str(args.solution),
        "target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
        "target_beta_mode": "custom" if args.target_beta_json else "prepared_p_beta",
        "target_beta_nonzero_count": sum(1 for x in target_beta if x),
        "columns": len(columns),
        "nonzero_source_columns": sum(1 for x in vals.values() if x),
        "solution_negative_count": sum(1 for x in vals.values() if x < 0),
        "solution_min": replay.fmt_fraction(min(vals.values()) if vals else Fraction(0)),
        "solution_max": replay.fmt_fraction(max(vals.values()) if vals else Fraction(0)),
        "full_negative_residual_count": len(negative_rows),
        "full_zero_residual_count": sum(1 for x in residual if x == 0),
        "full_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "full_max_residual": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
        "negative_rows_prefix": [
            {"row": int(i), "beta": list(prepared.betas[i]), "residual": replay.fmt_fraction(x)}
            for i, x in negative_rows[:10]
        ],
    }
    out["exact_ok"] = out["solution_negative_count"] == 0 and out["full_negative_residual_count"] == 0
    return out


def run(args):
    vals = read_source_solution(args.solution)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    if args.target_beta_json:
        target_beta = read_target_beta(args.target_beta_json, len(prepared.p_beta))
    else:
        target_beta = prepared.p_beta
    return check_values_against_target(vals, prepared, columns, target_beta, args=args)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument(
        "--target-beta-json",
        type=Path,
        default=None,
        help="Optional exact custom target beta vector for face-split/quotient checks.",
    )
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_source_solution_check_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": out["exact_ok"],
        "solution_negative_count": out["solution_negative_count"],
        "full_negative_residual_count": out["full_negative_residual_count"],
        "full_min_residual": out["full_min_residual"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
