#!/usr/bin/env python3
"""Repackage the known k6/F6 source certificate support as generic columns.

This diagnostic checks whether the already verified source certificate can be
viewed as a direct column set for the generic/custom cone tooling.  It does not
try to quotient by the F6 divisor; it isolates whether the blocker is in the
hybrid quotient generator rather than the certificate data itself.
"""

from __future__ import annotations

import json
import sys
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
OUT_COLUMNS = Path("tmp/eq_odl1_rung2_k6_F6_known_source_import_cols_v1.json")
OUT_SOLUTION = Path("tmp/eq_odl1_rung2_k6_F6_known_source_import_solution_v1.jsonl")
OUT_TARGET = Path("tmp/eq_odl1_rung2_k6_F6_known_source_import_target_beta_v1.json")
OUT_REPLAY = Path("tmp/eq_odl1_rung2_k6_F6_known_source_import_replay_v1.json")


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def main() -> None:
    prepared, columns, _mat, _b = probe.build_lp(CHART, DOMINANT, BAND, SUPPORT)
    vals = source_check.read_source_solution(SOLUTION)
    used = {idx: val for idx, val in vals.items() if val}

    imported = []
    old_to_new = {}
    for new_idx, source_col in enumerate(sorted(used)):
        col = columns[source_col]
        old_to_new[source_col] = new_idx
        imported.append(
            {
                "kind": f"source_{col.kind}",
                "name": col.name,
                "source_col": source_col,
                "multiplier_exp": list(col.multiplier_exp),
                "terms": [
                    {"row": int(row), **fraction_record(coeff)}
                    for row, coeff in col.terms
                    if coeff
                ],
            }
        )

    residual = prepared.p_beta[:]
    for source_col, val in used.items():
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    negative = [(i, x) for i, x in enumerate(residual) if x < 0]

    OUT_COLUMNS.write_text(
        json.dumps(
            {
                "schema": "eq_odl1_rung2_source_import_columns_v1",
                "chart": CHART,
                "dominant": DOMINANT,
                "dominant_name": prepared.chart.generator_names[DOMINANT],
                "band": BAND,
                "support": SUPPORT,
                "row_count": len(prepared.betas),
                "columns": imported,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    with OUT_SOLUTION.open("w", encoding="utf-8") as f:
        for source_col in sorted(used):
            val = used[source_col]
            f.write(
                json.dumps(
                    {
                        "source_col": old_to_new[source_col],
                        **fraction_record(val),
                        "original_source_col": source_col,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    OUT_TARGET.write_text(
        json.dumps(
            {
                "schema": "eq_odl1_rung2_dense_target_beta_v1",
                "chart": CHART,
                "dominant": DOMINANT,
                "band": BAND,
                "support": SUPPORT,
                "target_beta": [fraction_record(q) for q in prepared.p_beta],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    OUT_REPLAY.write_text(
        json.dumps(
            {
                "schema": "eq_odl1_rung2_source_import_replay_v1",
                "source_solution": str(SOLUTION),
                "import_solution": str(OUT_SOLUTION),
                "target_beta": str(OUT_TARGET),
                "imported_columns": len(imported),
                "source_nonzero_columns": len(used),
                "solution_negative_count": sum(1 for v in used.values() if v < 0),
                "full_negative_residual_count": len(negative),
                "full_min_residual": str(min(residual) if residual else Fraction(0)),
                "full_zero_residual_count": sum(1 for x in residual if x == 0),
                "exact_ok": len(negative) == 0 and all(v >= 0 for v in used.values()),
                "old_to_new_prefix": [
                    {"source_col": int(old), "import_col": int(new)}
                    for old, new in list(sorted(old_to_new.items()))[:20]
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "exact_ok": len(negative) == 0 and all(v >= 0 for v in used.values()),
                "imported_columns": len(imported),
                "negative_residual_count": len(negative),
                "columns": str(OUT_COLUMNS),
                "solution": str(OUT_SOLUTION),
                "target_beta": str(OUT_TARGET),
                "replay": str(OUT_REPLAY),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()