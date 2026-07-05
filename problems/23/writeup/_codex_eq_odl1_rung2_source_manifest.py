#!/usr/bin/env python3
"""Emit a reproducibility manifest for an exact Rung-2 source-column certificate.

This is the no-repair/general counterpart of _codex_eq_odl1_rung2_repaired_manifest.py.
The exact Python/Fraction source-solution check remains the acceptance gate; this
helper pins the checked source JSONL and checker summary for later Lean/batch
packaging.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


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


def norm_path_text(path: Path | str) -> str:
    return str(path).replace("/", "\\")


def run(args: argparse.Namespace) -> dict[str, Any]:
    solution = args.solution
    check = read_json(args.check_summary)

    require(check.get("schema") == REQUIRED_CHECK_SCHEMA, "unexpected check schema")
    require(check.get("exact_ok") is True, "source solution check is not exact-ok")
    require(check.get("solution_negative_count") == 0, "negative solution coefficient in check")
    require(check.get("full_negative_residual_count") == 0, "negative residual in check")
    require(check.get("full_min_residual") == "0", "full minimum residual is not exactly zero")
    require(norm_path_text(solution) in norm_path_text(check.get("solution", "")), "check summary does not point at solution")
    target_beta_mode = check.get("target_beta_mode", "prepared_p_beta")
    target_beta_json = check.get("target_beta_json")
    target_beta_path = Path(target_beta_json) if target_beta_json else None
    if target_beta_mode == "custom":
        require(target_beta_path is not None, "custom target check missing target_beta_json")
        require(target_beta_path.exists(), f"custom target beta JSON missing: {target_beta_path}")
    else:
        require(target_beta_mode == "prepared_p_beta", f"unexpected target beta mode: {target_beta_mode}")

    records = count_jsonl(solution)
    require(records == int(check["nonzero_source_columns"]), "source solution record count mismatch")
    require(records > 0, "empty source solution")

    manifest: dict[str, Any] = {
        "schema": "eq_odl1_rung2_source_certificate_manifest_v1",
        "chart": int(check["chart"]),
        "dominant": int(check["dominant"]),
        "band": check["band"],
        "support": check["support"],
        "solution_jsonl": str(solution),
        "solution_jsonl_sha256": sha256_path(solution),
        "solution_jsonl_records": records,
        "check_summary": str(args.check_summary),
        "check_summary_sha256": sha256_path(args.check_summary),
        "exact_ok": True,
        "solution_negative_count": int(check["solution_negative_count"]),
        "full_negative_residual_count": int(check["full_negative_residual_count"]),
        "full_min_residual": check["full_min_residual"],
        "full_zero_residual_count": int(check["full_zero_residual_count"]),
        "nonzero_source_columns": int(check["nonzero_source_columns"]),
        "columns_checked": int(check["columns"]),
        "target_beta_mode": target_beta_mode,
        "target_beta_json": str(target_beta_path) if target_beta_path is not None else None,
        "target_beta_json_sha256": sha256_path(target_beta_path) if target_beta_path is not None else None,
        "target_beta_nonzero_count": check.get("target_beta_nonzero_count"),
        "certificate_kind": "source",
        "repair": None,
        "verification_command": " ".join(
            [
            "python -B problems/23/writeup/_codex_eq_odl1_rung2_source_solution_check.py "
            f"--chart {check['chart']}",
            f"--dominant {check['dominant']}",
            f"--band {check['band']}",
            f"--support {check['support']}",
            f"--solution {solution}",
            *( [f"--target-beta-json {target_beta_path}"] if target_beta_path is not None else [] ),
            f"--summary {args.check_summary}",
            ]
        ),
    }
    if args.core:
        manifest["core"] = str(args.core)
    if args.modular_summary:
        manifest["modular_summary"] = str(args.modular_summary)
        manifest["modular_summary_sha256"] = sha256_path(args.modular_summary)
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--check-summary", type=Path, required=True)
    ap.add_argument("--core", type=Path)
    ap.add_argument("--modular-summary", type=Path)
    ap.add_argument("--out", type=Path, default=Path("tmp/eq_odl1_rung2_source_certificate_manifest_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": out["exact_ok"],
        "chart": out["chart"],
        "dominant": out["dominant"],
        "solution_jsonl_records": out["solution_jsonl_records"],
        "nonzero_source_columns": out["nonzero_source_columns"],
        "out": str(args.out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
