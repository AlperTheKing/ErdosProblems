#!/usr/bin/env python3
"""Exact source-coefficient sanitizer for Rung-2 source solutions.

For dominant generator G_a and any other generator G_b, the source dictionary
contains the exact identity

    m*G_b + m*(G_a - G_b) - m*G_a = 0.

This script changes only the source representation, block by block in the
multiplier monomial m.  It never changes the residual polynomial checked by
_codex_eq_odl1_rung2_source_solution_check.py.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

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


def write_source_solution(path: Path, vals: dict[int, Fraction]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for source_col in sorted(vals):
            val = vals[source_col]
            if not val:
                continue
            f.write(json.dumps({
                "source_col": int(source_col),
                "num": int(val.numerator),
                "den": int(val.denominator),
            }, sort_keys=True) + "\n")
            count += 1
    return count


def fmt(q: Fraction) -> str:
    return replay.fmt_fraction(q)


def run(args: argparse.Namespace) -> dict[str, object]:
    vals = read_source_solution(args.solution)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    gen_names = tuple(prepared.chart.generator_names)
    dominant_name = gen_names[args.dominant]

    by_key: dict[tuple[str, str, tuple[int, ...]], int] = {}
    by_mult: dict[tuple[int, ...], list[int]] = {}
    for i, col in enumerate(columns):
        by_key[(col.kind, col.name, tuple(col.multiplier_exp))] = i
        by_mult.setdefault(tuple(col.multiplier_exp), []).append(i)

    initial_negative = [(i, vals.get(i, Fraction(0))) for i in range(len(columns)) if vals.get(i, Fraction(0)) < 0]
    target_mults = {
        tuple(columns[i].multiplier_exp)
        for i, val in initial_negative
        if columns[i].kind in {"gen", "delta"}
    }

    out_vals = dict(vals)
    moves: list[dict[str, object]] = []
    skipped_blocks: list[dict[str, object]] = []

    for mult in sorted(target_mults):
        dom_col = by_key.get(("gen", dominant_name, mult))
        if dom_col is None:
            skipped_blocks.append({
                "multiplier_exp": list(mult),
                "reason": "dominant column absent from selected source dictionary",
            })
            continue

        relations = []
        lower_sum = Fraction(0)
        for b_name in gen_names:
            if b_name == dominant_name:
                continue
            gen_col = by_key.get(("gen", b_name, mult))
            delta_col = by_key.get(("delta", f"{dominant_name}-{b_name}", mult))
            if gen_col is None or delta_col is None:
                continue
            lam_b = out_vals.get(gen_col, Fraction(0))
            lam_delta = out_vals.get(delta_col, Fraction(0))
            lower = max(-lam_b, -lam_delta)
            lower_sum += lower
            relations.append((b_name, gen_col, delta_col, lower, lam_b, lam_delta))

        if not relations:
            skipped_blocks.append({
                "multiplier_exp": list(mult),
                "reason": "no usable same-monomial gen/delta relations",
            })
            continue

        lam_dom = out_vals.get(dom_col, Fraction(0))
        if lower_sum > lam_dom:
            skipped_blocks.append({
                "multiplier_exp": list(mult),
                "reason": "block infeasible under selected source dictionary",
                "dominant_col": dom_col,
                "dominant_value": fmt(lam_dom),
                "lower_sum": fmt(lower_sum),
                "deficit": fmt(lower_sum - lam_dom),
            })
            continue

        # Choose the lexicographically smallest feasible point: all t_b at their
        # lower bounds.  This makes every touched non-dominant gen/delta pair
        # nonnegative and leaves the unused slack on the dominant generator.
        out_vals[dom_col] = lam_dom - lower_sum
        touched = []
        for b_name, gen_col, delta_col, t, lam_b, lam_delta in relations:
            if t:
                out_vals[gen_col] = lam_b + t
                out_vals[delta_col] = lam_delta + t
                touched.append({
                    "name": b_name,
                    "gen_col": gen_col,
                    "delta_col": delta_col,
                    "t": fmt(t),
                    "new_gen": fmt(out_vals[gen_col]),
                    "new_delta": fmt(out_vals[delta_col]),
                })
        moves.append({
            "multiplier_exp": list(mult),
            "dominant_col": dom_col,
            "dominant_before": fmt(lam_dom),
            "dominant_after": fmt(out_vals[dom_col]),
            "lower_sum": fmt(lower_sum),
            "relations": len(relations),
            "touched": touched,
        })

    final_negative = [(i, out_vals.get(i, Fraction(0))) for i in range(len(columns)) if out_vals.get(i, Fraction(0)) < 0]
    final_negative_detail = [
        {
            "source_col": i,
            "kind": columns[i].kind,
            "name": columns[i].name,
            "multiplier_exp": list(columns[i].multiplier_exp),
            "value": fmt(v),
        }
        for i, v in final_negative
    ]

    records = write_source_solution(args.out_solution, out_vals)
    summary = {
        "schema": "eq_odl1_rung2_source_nullspace_sanitizer_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": dominant_name,
        "band": args.band,
        "support": args.support,
        "input_solution": str(args.solution),
        "output_solution": str(args.out_solution),
        "columns": len(columns),
        "input_nonzero": sum(1 for v in vals.values() if v),
        "output_nonzero": records,
        "initial_negative_count": len(initial_negative),
        "final_negative_count": len(final_negative),
        "moves": moves,
        "skipped_blocks": skipped_blocks,
        "final_negative_detail": final_negative_detail,
        "representation_changed": vals != out_vals,
        "exact_source_nonnegative": len(final_negative) == 0,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--out-solution", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    print(json.dumps({
        "initial_negative_count": out["initial_negative_count"],
        "final_negative_count": out["final_negative_count"],
        "moves": len(out["moves"]),
        "skipped_blocks": len(out["skipped_blocks"]),
        "output_solution": out["output_solution"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
