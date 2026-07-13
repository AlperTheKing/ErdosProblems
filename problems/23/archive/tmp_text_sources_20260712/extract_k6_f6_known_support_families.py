#!/usr/bin/env python3
"""Group the known k6/F6 exact support by source-column family.

Diagnostic only.  It does not certify a chart; it cross-references the
already-certified source solution against the canonical source LP columns.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


CHART = 6
DOMINANT = 5
BAND = "near_2s_minus_1"
SUPPORT = "negative"
SOLUTION = Path(
    "tmp/eq_odl1_rung2_source_solution_k6_F6_near_exact_active_face_split_patch3_rowgen2_hardspill_v1.jsonl"
)
OUT = Path("tmp/eq_odl1_rung2_k6_F6_known_support_family_groups_v1.json")


def fmt(q: Fraction) -> str:
    if q == 0:
        return "0"
    if q.denominator == 1:
        return str(q.numerator)
    if abs(q.numerator).bit_length() > 256 or q.denominator.bit_length() > 256:
        sign = "-" if q < 0 else ""
        return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"
    return f"{q.numerator}/{q.denominator}"


def family_key(col) -> str:
    return f"{col.kind}:{col.name}"


def main() -> None:
    prepared, columns, _mat, _b_ub = probe.build_lp(CHART, DOMINANT, BAND, SUPPORT)
    vals = source_check.read_source_solution(SOLUTION)
    used = {int(c): v for c, v in vals.items() if v}
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    family_l1: defaultdict[str, Fraction] = defaultdict(Fraction)
    family_signed: defaultdict[str, Fraction] = defaultdict(Fraction)

    for source_col in sorted(used):
        col = columns[source_col]
        val = used[source_col]
        key = family_key(col)
        groups[key].append(
            {
                "source_col": source_col,
                "sign": -1 if val < 0 else 1,
                "value": fmt(val),
            }
        )
        family_l1[key] += abs(val)
        family_signed[key] += val

    payload = {
        "schema": "eq_odl1_rung2_known_support_family_groups_v1",
        "chart": CHART,
        "dominant": DOMINANT,
        "dominant_name": prepared.chart.generator_names[DOMINANT],
        "band": BAND,
        "support": SUPPORT,
        "solution": str(SOLUTION),
        "solution_nonzero_columns": len(used),
        "family_counts": {k: len(v) for k, v in sorted(groups.items())},
        "family_l1": {k: fmt(v) for k, v in sorted(family_l1.items())},
        "family_signed": {k: fmt(v) for k, v in sorted(family_signed.items())},
        "source_cols_by_family": {k: v for k, v in sorted(groups.items())},
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(OUT),
                "families": len(groups),
                "solution_nonzero_columns": len(used),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
