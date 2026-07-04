#!/usr/bin/env python3
"""Emit a reproducibility manifest for an exact repaired Rung-2 certificate.

This is a Lean-facing/audit-facing index artifact: it does not certify by itself,
but it pins the exact JSONL solution, exact checker summary, and one-row repair
metadata by SHA-256 and basic schema checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_REPAIR_SCHEMA = "eq_odl1_rung2_one_row_repair_v1"
REQUIRED_CHECK_SCHEMA = "eq_odl1_rung2_source_solution_check_v1"


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_jsonl(path: Path) -> int:
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                json.loads(line)
                n += 1
    return n


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def run(args):
    solution = args.solution
    repair = read_json(args.repair_summary)
    check = read_json(args.check_summary)

    require(repair.get("schema") == REQUIRED_REPAIR_SCHEMA, "unexpected repair schema")
    require(check.get("schema") == REQUIRED_CHECK_SCHEMA, "unexpected check schema")
    require(repair.get("first_hit_exact_ok") is True, "repair summary is not exact-ok")
    require(check.get("exact_ok") is True, "source solution check is not exact-ok")
    require(check.get("solution_negative_count") == 0, "negative solution coefficient in check")
    require(check.get("full_negative_residual_count") == 0, "negative residual in check")
    require(check.get("full_min_residual") == "0", "full minimum residual is not exactly zero")
    require(str(solution).replace("/", "\\") in str(repair.get("repaired_source_solution", "")).replace("/", "\\"), "repair summary does not point at solution")
    require(str(solution).replace("/", "\\") in str(check.get("solution", "")).replace("/", "\\"), "check summary does not point at solution")

    first_hit = repair.get("first_hit", {})
    manifest = {
        "schema": "eq_odl1_rung2_repaired_certificate_manifest_v1",
        "chart": check["chart"],
        "dominant": check["dominant"],
        "band": check["band"],
        "support": check["support"],
        "solution_jsonl": str(solution),
        "solution_jsonl_sha256": sha256_path(solution),
        "solution_jsonl_records": count_jsonl(solution),
        "repair_summary": str(args.repair_summary),
        "repair_summary_sha256": sha256_path(args.repair_summary),
        "check_summary": str(args.check_summary),
        "check_summary_sha256": sha256_path(args.check_summary),
        "exact_ok": True,
        "solution_negative_count": check["solution_negative_count"],
        "full_negative_residual_count": check["full_negative_residual_count"],
        "full_min_residual": check["full_min_residual"],
        "nonzero_source_columns": check["nonzero_source_columns"],
        "columns_checked": check["columns"],
        "bad_row_repaired": repair["bad_row"],
        "bad_beta": repair["bad_beta"],
        "repair_source_col": first_hit.get("source_col"),
        "repair_column_name": first_hit.get("name"),
        "repair_column_kind": first_hit.get("kind"),
        "repair_multiplier_exp": first_hit.get("multiplier_exp"),
        "repair_required": first_hit.get("required"),
        "repair_bad_coeff": first_hit.get("bad_coeff"),
        "verification_command": (
            "python -B problems/23/writeup/_codex_eq_odl1_rung2_source_solution_check.py "
            "--chart 0 --dominant 7 --band near_2s_minus_1 --support negative "
            f"--solution {solution} --summary {args.check_summary}"
        ),
    }
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--repair-summary", type=Path, required=True)
    ap.add_argument("--check-summary", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("tmp/eq_odl1_rung2_repaired_certificate_manifest_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": out["exact_ok"],
        "solution_jsonl_records": out["solution_jsonl_records"],
        "nonzero_source_columns": out["nonzero_source_columns"],
        "full_negative_residual_count": out["full_negative_residual_count"],
        "out": str(args.out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
