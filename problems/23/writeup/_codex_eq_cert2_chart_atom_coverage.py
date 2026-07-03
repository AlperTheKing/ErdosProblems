#!/usr/bin/env python3
"""Global 2x2 atom coverage report for CERT-2 ChartSOS rows.

This diagnoses the restricted SOC atom family used by the direct Clarabel smoke.
Search helper only; no certificate claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _codex_eq_cert2_chart_lp as lp
import _codex_eq_cert2_chart_sos as sos
import _codex_eq_cert2_chart_sos_2x2 as s2


def split_pairs_for_row(row: tuple[int, ...]):
    halves = [(x // 2, x - x // 2) for x in row]
    seen = set()
    for mask in range(1 << len(row)):
        a = tuple(halves[i][(mask >> i) & 1] for i in range(len(row)))
        b = tuple(row[i] - a[i] for i in range(len(row)))
        key = (a, b) if a <= b else (b, a)
        if key in seen:
            continue
        seen.add(key)
        yield key


def row_shape(row: tuple[int, ...]) -> str:
    first = sum(row[:5])
    last = sum(row[5:])
    odds = sum(x & 1 for x in row)
    zeros = sum(1 for x in row if x == 0)
    return f"first{first}_last{last}_odds{odds}_zeros{zeros}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_atom_coverage_v1.json")
    args = ap.parse_args()

    target11, _generators, meta = lp.build_chart(args.chart)
    target12 = sos.mul_linear(target11)
    selected = s2.selected_atoms(target12, 10**9, "all")
    selected_by_row: dict[tuple[int, ...], int] = defaultdict(int)
    for _a, _b, row in selected:
        selected_by_row[row] += 1

    split_hist = Counter()
    selected_hist = Counter()
    zero_selected_split_hist = Counter()
    shape_hist = Counter()
    zero_shape_hist = Counter()
    total_splits = 0
    neg_rows = []
    zero_examples = []
    for row, coeff in sorted(target12.items()):
        if coeff >= 0:
            continue
        splits = sum(1 for _ in split_pairs_for_row(row))
        sel = selected_by_row.get(row, 0)
        total_splits += splits
        split_hist[splits] += 1
        selected_hist[sel] += 1
        shape_hist[row_shape(row)] += 1
        if sel == 0:
            zero_selected_split_hist[splits] += 1
            zero_shape_hist[row_shape(row)] += 1
            if len(zero_examples) < 20:
                zero_examples.append({"row": list(row), "coeff": str(coeff), "split_pairs": splits})
        neg_rows.append((row, coeff, splits, sel))

    uncovered = [x for x in neg_rows if x[3] == 0]
    partial = [x for x in neg_rows if 0 < x[3] < x[2]]
    full = [x for x in neg_rows if x[3] == x[2]]
    out = {
        "schema": "eq_cert2_chart_atom_coverage_v1",
        "chart": args.chart,
        "negative_rows": len(neg_rows),
        "selected_atoms": len(selected),
        "all_split_atoms": total_splits,
        "missing_split_atoms": total_splits - len(selected),
        "rows_with_no_selected_atom": len(uncovered),
        "rows_partially_selected": len(partial),
        "rows_fully_selected": len(full),
        "split_hist": dict(sorted(split_hist.items())),
        "selected_per_row_hist": dict(sorted(selected_hist.items())),
        "zero_selected_split_hist": dict(sorted(zero_selected_split_hist.items())),
        "shape_hist_top20": shape_hist.most_common(20),
        "zero_selected_shape_hist_top20": zero_shape_hist.most_common(20),
        "zero_selected_examples": zero_examples,
        "meta": meta,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    printable = dict(out)
    printable.pop("meta", None)
    print(json.dumps(printable, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
