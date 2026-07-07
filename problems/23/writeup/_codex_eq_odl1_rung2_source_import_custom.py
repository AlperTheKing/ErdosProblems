#!/usr/bin/env python3
"""Import a checked source-column solution as a custom sparse cone dictionary.

The source checker rebuilds the full standard chart dictionary and validates a
solution indexed by those source columns.  The custom cone/Lean path consumes a
compact explicit sparse dictionary instead.  This helper preserves the exact
source columns that have nonzero coefficients, remaps them to a dense custom
column index, and emits:

* sparse column JSON,
* remapped solution JSONL,
* dense target beta JSON,
* a replay summary with exact residual statistics.

It is a format bridge only.  The acceptance gate remains
_codex_eq_odl1_rung2_custom_cone_check.py on the emitted files.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def write_json(path: Path, data: object, *, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent, sort_keys=True), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, object]:
    prepared, columns, _mat, _b_ub = probe.build_lp(
        args.chart,
        args.dominant,
        args.band,
        args.support,
    )
    vals = source_check.read_source_solution(args.solution)
    used = {idx: val for idx, val in vals.items() if val}
    invalid_cols = [idx for idx in used if idx < 0 or idx >= len(columns)]
    if invalid_cols:
        raise ValueError(f"invalid source columns: {invalid_cols[:10]}")

    if args.target_beta_json:
        target_beta = source_check.read_target_beta(args.target_beta_json, len(prepared.p_beta))
        target_mode = "custom"
    else:
        target_beta = prepared.p_beta[:]
        target_mode = "prepared_p_beta"

    imported: list[dict[str, object]] = []
    old_to_new: dict[int, int] = {}
    for new_idx, source_col in enumerate(sorted(used)):
        col = columns[source_col]
        old_to_new[source_col] = new_idx
        imported.append(
            {
                "kind": f"source_{col.kind}",
                "name": col.name,
                "source_col": source_col,
                "multiplier_exp": [int(x) for x in col.multiplier_exp],
                "terms": [
                    {"row": int(row), **fraction_record(coeff)}
                    for row, coeff in col.terms
                    if coeff
                ],
            }
        )

    residual = target_beta[:]
    for source_col, val in used.items():
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val

    negative = [(i, x) for i, x in enumerate(residual) if x < 0]
    solution_negative_count = sum(1 for v in used.values() if v < 0)
    exact_ok = len(negative) == 0 and solution_negative_count == 0

    write_json(
        args.columns_out,
        {
            "schema": "eq_odl1_rung2_source_import_columns_v1",
            "chart": args.chart,
            "dominant": args.dominant,
            "dominant_name": prepared.chart.generator_names[args.dominant],
            "band": args.band,
            "support": args.support,
            "row_count": len(prepared.betas),
            "target_beta_mode": target_mode,
            "source_solution": str(args.solution),
            "columns": imported,
        },
    )

    args.solution_out.parent.mkdir(parents=True, exist_ok=True)
    with args.solution_out.open("w", encoding="utf-8") as f:
        for source_col in sorted(used):
            val = used[source_col]
            f.write(
                json.dumps(
                    {
                        "source_col": old_to_new[source_col],
                        "original_source_col": source_col,
                        **fraction_record(val),
                    },
                    sort_keys=True,
                )
                + "\n"
            )

    write_json(
        args.target_out,
        {
            "schema": "eq_odl1_rung2_dense_target_beta_v1",
            "chart": args.chart,
            "dominant": args.dominant,
            "band": args.band,
            "support": args.support,
            "target_beta_mode": target_mode,
            "source_target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
            "target_beta": [fraction_record(q) for q in target_beta],
        },
    )

    replay_summary: dict[str, object] = {
        "schema": "eq_odl1_rung2_source_import_replay_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "source_solution": str(args.solution),
        "imported_columns_json": str(args.columns_out),
        "import_solution_jsonl": str(args.solution_out),
        "target_beta_json": str(args.target_out),
        "source_nonzero_columns": len(used),
        "imported_columns": len(imported),
        "solution_negative_count": solution_negative_count,
        "full_negative_residual_count": len(negative),
        "full_zero_residual_count": sum(1 for x in residual if x == 0),
        "full_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "full_max_residual": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
        "target_beta_nonzero_count": sum(1 for x in target_beta if x),
        "negative_rows_prefix": [
            {"row": int(i), "residual": replay.fmt_fraction(x)}
            for i, x in negative[:10]
        ],
        "exact_ok": exact_ok,
        "old_to_new_prefix": [
            {"source_col": int(old), "import_col": int(new)}
            for old, new in list(sorted(old_to_new.items()))[:20]
        ],
    }
    write_json(args.replay_out, replay_summary, indent=2)
    return replay_summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--target-beta-json", type=Path, default=None)
    ap.add_argument("--columns-out", type=Path, required=True)
    ap.add_argument("--solution-out", type=Path, required=True)
    ap.add_argument("--target-out", type=Path, required=True)
    ap.add_argument("--replay-out", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    print(
        json.dumps(
            {
                "exact_ok": out["exact_ok"],
                "imported_columns": out["imported_columns"],
                "solution_negative_count": out["solution_negative_count"],
                "full_negative_residual_count": out["full_negative_residual_count"],
                "columns": out["imported_columns_json"],
                "solution": out["import_solution_jsonl"],
                "target_beta": out["target_beta_json"],
                "replay": str(args.replay_out),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
