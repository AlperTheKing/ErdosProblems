#!/usr/bin/env python3
"""Compare known k6/F6 source support with emitted hybrid column keys."""

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
HYBRID_COLS = Path("tmp/eq_odl1_rung2_hybrid_k6_F6_known22_pool_cols_v1.json")
OUT = Path("tmp/eq_odl1_rung2_k6_F6_known_source_vs_known22_hybrid_keys_v1.json")


def source_family(col) -> str:
    return f"{col.kind}:{col.name}"


def source_to_hybrid_key(col) -> tuple[str, str, tuple[int, ...]]:
    if col.kind == "gen":
        return ("face_gen", col.name, tuple(col.multiplier_exp))
    if col.kind == "delta":
        return ("face_delta", col.name, tuple(col.multiplier_exp))
    if col.kind == "band":
        # Source band columns are face-side nonnegative band columns.
        return ("face_band", col.name, tuple(col.multiplier_exp))
    return (f"source_{col.kind}", col.name, tuple(col.multiplier_exp))


def main() -> None:
    prepared, source_cols, _mat, _b = probe.build_lp(CHART, DOMINANT, BAND, SUPPORT)
    vals = source_check.read_source_solution(SOLUTION)
    used = {idx: val for idx, val in vals.items() if val}

    payload = json.loads(HYBRID_COLS.read_text(encoding="utf-8"))
    hybrid_keys = {
        (rec["kind"], rec["name"], tuple(int(x) for x in rec["multiplier_exp"]))
        for rec in payload["columns"]
    }

    missing: list[dict[str, object]] = []
    present = 0
    missing_by_family: Counter[str] = Counter()
    present_by_family: Counter[str] = Counter()
    missing_abs_by_family: defaultdict[str, Fraction] = defaultdict(Fraction)
    present_abs_by_family: defaultdict[str, Fraction] = defaultdict(Fraction)

    for source_col, val in sorted(used.items()):
        col = source_cols[source_col]
        family = source_family(col)
        hkey = source_to_hybrid_key(col)
        if hkey in hybrid_keys:
            present += 1
            present_by_family[family] += 1
            present_abs_by_family[family] += abs(val)
        else:
            missing_by_family[family] += 1
            missing_abs_by_family[family] += abs(val)
            if len(missing) < 100:
                missing.append(
                    {
                        "source_col": int(source_col),
                        "family": family,
                        "hybrid_kind": hkey[0],
                        "name": hkey[1],
                        "multiplier_exp": list(hkey[2]),
                        "value_num": val.numerator,
                        "value_den": val.denominator,
                    }
                )

    out = {
        "schema": "eq_odl1_rung2_known_source_vs_hybrid_keys_v1",
        "hybrid_columns": len(hybrid_keys),
        "source_nonzero_columns": len(used),
        "present_source_columns": present,
        "missing_source_columns": len(used) - present,
        "missing_by_family": dict(sorted(missing_by_family.items())),
        "present_by_family": dict(sorted(present_by_family.items())),
        "missing_abs_by_family": {
            k: str(v) for k, v in sorted(missing_abs_by_family.items())
        },
        "present_abs_by_family": {
            k: str(v) for k, v in sorted(present_abs_by_family.items())
        },
        "missing_prefix": missing,
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "source_nonzero_columns": len(used),
                "present_source_columns": present,
                "missing_source_columns": len(used) - present,
                "out": str(OUT),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
