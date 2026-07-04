#!/usr/bin/env python3
"""Emit a SHA-pinned ledger for exact EQ-ODL1 Rung-2 chart certificates.

The ledger is intentionally light: it does not reprove any row certificate.
Instead it validates the row manifests that already passed the exact Fraction
source-solution checker, pins every referenced artifact by SHA-256, and records
the global numeric-map order so the chart batch can be audited incrementally.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SOURCE_SCHEMA = "eq_odl1_rung2_source_certificate_manifest_v1"
REPAIRED_SCHEMA = "eq_odl1_rung2_repaired_certificate_manifest_v1"


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def resolve(root: Path, text: str | None) -> Path | None:
    if not text:
        return None
    p = Path(text)
    return p if p.is_absolute() else root / p


def validate_hash(root: Path, manifest: dict[str, Any], path_key: str, hash_key: str) -> dict[str, str] | None:
    text = manifest.get(path_key)
    if not text:
        return None
    path = resolve(root, str(text))
    require(path is not None and path.exists(), f"missing {path_key}: {text}")
    actual = sha256_path(path).lower()
    expected = str(manifest.get(hash_key, "")).lower()
    require(expected == actual, f"sha mismatch for {path_key}: expected {expected}, got {actual}")
    return {"path": str(text), "sha256": actual}


def flatten_numeric_map(path: Path) -> tuple[list[dict[str, Any]], dict[tuple[int, int, str], dict[str, Any]]]:
    data = read_json(path)
    rows: list[dict[str, Any]] = []
    for chart in data.get("chart_results", []):
        for item in chart.get("items", []):
            if item.get("band") != "near_2s_minus_1":
                continue
            if item.get("lp_status") != 0:
                continue
            row = {
                "chart": int(item["k"]),
                "dominant": int(item["dominant_index"]),
                "dominant_name": item.get("dominant_name"),
                "band": item.get("band"),
                "variables": int(item.get("variables", 10**18)),
                "float_nonzero": int(item.get("float_nonzero", 10**18)),
                "objective": item.get("objective"),
            }
            rows.append(row)
    rows.sort(key=lambda r: (r["float_nonzero"], r["variables"], r["chart"], r["dominant"]))
    by_key = {(r["chart"], r["dominant"], r["band"]): r | {"numeric_order": i} for i, r in enumerate(rows)}
    return rows, by_key


def normalize_manifest(root: Path, path: Path, numeric_by_key: dict[tuple[int, int, str], dict[str, Any]]) -> dict[str, Any]:
    manifest = read_json(path)
    schema = manifest.get("schema")
    require(schema in {SOURCE_SCHEMA, REPAIRED_SCHEMA}, f"unsupported manifest schema {schema!r}")
    require(manifest.get("exact_ok") is True, f"manifest is not exact_ok: {path}")
    require(int(manifest.get("solution_negative_count", -1)) == 0, f"negative solution in {path}")
    require(int(manifest.get("full_negative_residual_count", -1)) == 0, f"negative residual in {path}")
    require(str(manifest.get("full_min_residual")) == "0", f"nonzero min residual in {path}")

    chart = int(manifest["chart"])
    dominant = int(manifest["dominant"])
    band = str(manifest["band"])
    key = (chart, dominant, band)
    numeric = numeric_by_key.get(key)
    require(numeric is not None, f"manifest row not present in numeric map: {key}")

    solution = validate_hash(root, manifest, "solution_jsonl", "solution_jsonl_sha256")
    check = validate_hash(root, manifest, "check_summary", "check_summary_sha256")
    repair = validate_hash(root, manifest, "repair_summary", "repair_summary_sha256")
    modular = validate_hash(root, manifest, "modular_summary", "modular_summary_sha256")
    core_path = manifest.get("core")
    if core_path:
        core_resolved = resolve(root, str(core_path))
        require(core_resolved is not None and core_resolved.exists(), f"missing core: {core_path}")

    return {
        "numeric_order": numeric["numeric_order"],
        "chart": chart,
        "dominant": dominant,
        "dominant_name": numeric.get("dominant_name"),
        "band": band,
        "support": manifest.get("support"),
        "certificate_kind": "source" if schema == SOURCE_SCHEMA else "repaired",
        "manifest": str(path),
        "manifest_sha256": sha256_path(path).lower(),
        "solution": solution,
        "check_summary": check,
        "repair_summary": repair,
        "core": str(core_path) if core_path else None,
        "modular_summary": modular,
        "solution_jsonl_records": int(manifest.get("solution_jsonl_records", 0)),
        "nonzero_source_columns": int(manifest.get("nonzero_source_columns", 0)),
        "columns_checked": int(manifest.get("columns_checked", 0)),
        "full_min_residual": manifest.get("full_min_residual"),
        "full_negative_residual_count": int(manifest.get("full_negative_residual_count", 0)),
        "solution_negative_count": int(manifest.get("solution_negative_count", 0)),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = Path.cwd()
    rows, numeric_by_key = flatten_numeric_map(args.numeric_map)
    certified = [normalize_manifest(root, p, numeric_by_key) for p in args.manifest]
    seen: set[tuple[int, int, str]] = set()
    for item in certified:
        key = (item["chart"], item["dominant"], item["band"])
        require(key not in seen, f"duplicate certified row {key}")
        seen.add(key)
    certified.sort(key=lambda r: r["numeric_order"])

    pending = [r for r in rows if (r["chart"], r["dominant"], r["band"]) not in seen]
    return {
        "schema": "eq_odl1_rung2_chart_batch_ledger_v1",
        "numeric_map": str(args.numeric_map),
        "numeric_map_sha256": sha256_path(args.numeric_map).lower(),
        "band": "near_2s_minus_1",
        "support": "negative",
        "variable_convention": {
            "Var 0": "N",
            "Var 1+i": "w_i",
            "Var >= 1000": "auxiliary certificate variables",
            "Var 200": "s/sigma or sub-band sigma",
            "Var 201+r": "active z/u coordinate r in increasing original index order skipping chart k",
        },
        "feasible_near_row_count": len(rows),
        "certified_count": len(certified),
        "certified_rows": certified,
        "pending_count": len(pending),
        "pending_rows_prefix": pending[: args.pending_prefix],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--numeric-map", type=Path, default=Path("tmp/eq_odl1_rung2_support_numeric_map_full_sum_t60_w16_v1.json"))
    ap.add_argument("--manifest", type=Path, action="append", required=True)
    ap.add_argument("--pending-prefix", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path("tmp/eq_odl1_rung2_chart_batch_ledger_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    first_pending = out["pending_rows_prefix"][0] if out["pending_rows_prefix"] else None
    print(json.dumps({
        "schema": out["schema"],
        "certified_count": out["certified_count"],
        "feasible_near_row_count": out["feasible_near_row_count"],
        "pending_count": out["pending_count"],
        "first_pending": first_pending,
        "out": str(args.out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
