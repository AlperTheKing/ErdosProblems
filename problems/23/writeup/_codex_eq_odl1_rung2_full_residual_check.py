#!/usr/bin/env python3
"""Exact full-residual checker for an exported Rung-2 core solution."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_modular_replay as replay


def parse_fraction(text: str) -> Fraction:
    if text == "0":
        return Fraction(0)
    if text.startswith("num_bits=") or text.startswith("-num_bits="):
        raise ValueError(f"nonliteral fraction in solution: {text}")
    if "/" in text:
        a, b = text.split("/", 1)
        return Fraction(int(a), int(b))
    return Fraction(int(text), 1)


def read_core_maps(path: Path):
    cols: dict[int, int] = {}
    rows: dict[int, int] = {}
    dim = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            typ = rec.get("type")
            if typ == "meta":
                dim = int(rec["dimension"])
            elif typ == "col":
                cols[int(rec["col"])] = int(rec["source_col"])
            elif typ == "selected_row":
                rows[int(rec["row"])] = int(rec["source_row"])
    if dim is None:
        raise ValueError("missing core meta")
    if len(cols) != dim:
        raise ValueError(f"core column map incomplete: {len(cols)} != {dim}")
    return dim, [cols[i] for i in range(dim)], [rows[i] for i in range(len(rows))]


def read_solution(path: Path, dim: int):
    vals: dict[int, Fraction] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            vals[int(rec["col"])] = Fraction(int(rec["num"]), int(rec["den"])) if "num" in rec else parse_fraction(rec["value"])
    if len(vals) != dim:
        raise ValueError(f"solution dimension mismatch: {len(vals)} != {dim}")
    return [vals[i] for i in range(dim)]


def run(args):
    dim, source_cols, selected_rows = read_core_maps(args.core)
    sol = read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = prepared.p_beta[:]
    for val, source_col in zip(sol, source_cols):
        if not val:
            continue
        col = columns[source_col]
        for row, coeff in col.terms:
            residual[row] -= coeff * val
    core_residual = [residual[row] for row in selected_rows]
    negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    out = {
        "schema": "eq_odl1_rung2_full_residual_check_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "solution": str(args.solution),
        "dimension": dim,
        "source_columns": len(source_cols),
        "selected_rows": len(selected_rows),
        "solution_negative_count": sum(1 for x in sol if x < 0),
        "solution_min": replay.fmt_fraction(min(sol) if sol else Fraction(0)),
        "solution_max": replay.fmt_fraction(max(sol) if sol else Fraction(0)),
        "core_nonzero_residuals": sum(1 for x in core_residual if x),
        "core_min_residual": replay.fmt_fraction(min(core_residual) if core_residual else Fraction(0)),
        "full_negative_residual_count": sum(1 for x in residual if x < 0),
        "negative_rows_prefix": [
            {
                "row": int(i),
                "beta": list(prepared.betas[i]),
                "residual": replay.fmt_fraction(x),
            }
            for i, x in negative_rows[:10]
        ],
        "full_zero_residual_count": sum(1 for x in residual if x == 0),
        "full_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "full_max_residual": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
    }
    out["exact_ok"] = (
        out["solution_negative_count"] == 0
        and out["core_nonzero_residuals"] == 0
        and out["full_negative_residual_count"] == 0
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_full_residual_check_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ["exact_ok", "solution_negative_count", "core_nonzero_residuals", "full_negative_residual_count", "full_min_residual"]}, sort_keys=True))


if __name__ == "__main__":
    main()



