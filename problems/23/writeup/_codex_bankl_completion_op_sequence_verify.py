#!/usr/bin/env python3
"""Verify the two-phase Gate-B op sequence trace artifact exactly."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from typing import Any


def parse_int(x: Any) -> int:
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        return int(F(x))
    raise TypeError(f"not int-like: {x!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_completion_op_sequence_trace_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_completion_op_sequence_trace_v1_verify_summary.json")
    ap.add_argument("--max-errors", type=int, default=20)
    args = ap.parse_args()

    counts: Counter[str] = Counter()
    errors: list[dict[str, Any]] = []
    by_class: Counter[str] = Counter()
    by_rho: Counter[str] = Counter()

    with Path(args.input).open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            counts["rows"] += 1
            row_errors: list[str] = []
            raw_drop = int(rec["raw_sigma"]) - int(rec["final_sigma"])
            if raw_drop != int(rec["raw_sigma_drop"]):
                row_errors.append("raw_sigma_drop_mismatch")
            q_sum = 0
            rho_sum = 0
            for step in rec.get("op_steps", []):
                counts["steps"] += 1
                by_class[step["op_class"]] += 1
                q = int(step["exchange_q"])
                q_formula = int(step["eB_XS"]) - int(step["eM_XS"]) - int(step["eB_XO"]) + int(step["eM_XO"])
                sigma_drop = int(step["sigma_before"]) - int(step["sigma_after"])
                rho = parse_int(step["rho_a"])
                by_rho[step["rho_a"]] += 1
                if q != q_formula:
                    row_errors.append(f"step_{step['step_index']}_quad_formula_mismatch")
                if q != sigma_drop:
                    row_errors.append(f"step_{step['step_index']}_sigma_drop_mismatch")
                if rho != 25 * max(0, q):
                    row_errors.append(f"step_{step['step_index']}_rho_formula_mismatch")
                decomp_sum = F(0)
                for dno, decomp in enumerate(step.get("dictionary_decomposition", [])):
                    value = F(decomp["value"])
                    coeff = F(decomp["coeff"])
                    contribution = F(decomp["contribution"])
                    if value * coeff != contribution:
                        row_errors.append(f"step_{step['step_index']}_decomp_{dno}_product_mismatch")
                    if value < 0 or coeff < 0 or contribution < 0:
                        row_errors.append(f"step_{step['step_index']}_decomp_{dno}_negative")
                    decomp_sum += contribution
                if decomp_sum != rho:
                    row_errors.append(f"step_{step['step_index']}_decomp_sum_mismatch")
                q_sum += q
                rho_sum += rho
            if q_sum != raw_drop:
                row_errors.append("op_sequence_q_sum_mismatch")
            if q_sum != int(rec["op_sequence_q_sum"]):
                row_errors.append("stored_q_sum_mismatch")
            if rho_sum != parse_int(rec["op_sequence_rho_sum"]):
                row_errors.append("stored_rho_sum_mismatch")
            if rho_sum < parse_int(rec.get("raw_to_final_rho_a") or 0):
                row_errors.append("rho_does_not_dominate_raw_rho")
            if row_errors:
                counts["bad_rows"] += 1
                if len(errors) < args.max_errors:
                    errors.append({"line_no": line_no, "row_ref": rec.get("row_ref"), "errors": row_errors})

    summary = {
        "schema": "bankl_completion_op_sequence_trace_v1_verify_summary",
        "input": args.input,
        "counts": dict(sorted(counts.items())),
        "by_class": dict(sorted(by_class.items())),
        "by_rho": dict(sorted(by_rho.items(), key=lambda kv: (F(kv[0]), kv[0]))),
        "bad_count": counts["bad_rows"],
        "errors": errors,
    }
    Path(args.summary_output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS op sequence verify "
        f"rows={counts['rows']} steps={counts['steps']} bad={counts['bad_rows']}"
    )
    return 0 if counts["bad_rows"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
