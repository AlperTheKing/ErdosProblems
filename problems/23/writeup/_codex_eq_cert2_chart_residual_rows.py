#!/usr/bin/env python3
"""Classify top residual rows from direct Clarabel ChartSOS probes."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_sos as sos
import _codex_eq_cert2_chart_sos_2x2 as s2


def splits_for_row(row: tuple[int, ...]) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    out = []
    halves = []
    for x in row:
        halves.append((x // 2, x - x // 2))
    seen = set()
    for mask in range(1 << len(row)):
        a = tuple(halves[i][(mask >> i) & 1] for i in range(len(row)))
        b = tuple(row[i] - a[i] for i in range(len(row)))
        key = (a, b) if a <= b else (b, a)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--residual", required=True)
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_residual_row_classify_v1.json")
    args = ap.parse_args()

    target11, generators, meta = lp.build_chart(args.chart)
    target12 = sos.mul_linear(target11)
    residual = json.loads(Path(args.residual).read_text(encoding="utf-8"))
    rows = residual.get("top_negative_coeff_rows", [])
    all_atoms = s2.selected_atoms(target12, 10**9, "all")
    atom_cross_counts = {}
    for _a, _b, cross in all_atoms:
        atom_cross_counts[cross] = atom_cross_counts.get(cross, 0) + 1
    out_rows = []
    for item in rows:
        row = tuple(int(x) for x in item["row"])
        coeff = target12.get(row, Fraction(0))
        splits = splits_for_row(row)
        diag_splits = sum(1 for a, b in splits if a == b)
        out_rows.append({
            "row": list(row),
            "residual_slack": item["slack"],
            "in_target12": row in target12,
            "target12_coeff": str(coeff),
            "target12_sign": "neg" if coeff < 0 else "pos" if coeff > 0 else "zero",
            "split_pairs": len(splits),
            "diag_splits": diag_splits,
            "selected_2x2_atoms": atom_cross_counts.get(row, 0),
            "sample_splits": [[list(a), list(b)] for a, b in splits[:5]],
        })
    out = {
        "schema": "eq_cert2_chart_residual_row_classify_v1",
        "chart": args.chart,
        "residual": args.residual,
        "rows": out_rows,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

