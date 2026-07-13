import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    vals: dict[int, Fraction] = {}
    for source_col, val in zip(source_cols, sol):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val

    args.out.parent.mkdir(parents=True, exist_ok=True)
    records = 0
    with args.out.open("w", encoding="utf-8") as f:
        for source_col in sorted(vals):
            val = vals[source_col]
            if not val:
                continue
            records += 1
            f.write(json.dumps({
                "source_col": source_col,
                "num": val.numerator,
                "den": val.denominator,
            }, sort_keys=True) + "\n")

    payload = {
        "schema": "eq_odl1_rung2_core_to_source_solution_v1",
        "core": str(args.core),
        "core_solution": str(args.solution),
        "source_solution": str(args.out),
        "dimension": dim,
        "source_records": records,
        "solution_negative_count": sum(1 for x in vals.values() if x < 0),
    }
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
