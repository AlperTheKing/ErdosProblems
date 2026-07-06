#!/usr/bin/env python3
"""Audit tau_0 MCERT exact and Lean-facing artifacts.

This is a conservative reproducibility gate: it does not prove new
mathematics, but it verifies that the accepted exact coefficient artifact and
the generated Lean RawPoly shards agree on row counts, term counts, degree
metadata, and forbidden-token policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN = ("native_decide", "sorry", "admit", "axiom", "unsafe")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def scan_forbidden(path: Path) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        for token in FORBIDDEN:
            if token in line:
                hits.append({"file": str(path), "line": lineno, "token": token})
    return hits


def parse_lean_row(path: Path, index: int) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    count_match = re.search(rf"def tau0Row{index:02d}TermCount\s*:\s*Nat\s*:=\s*(\d+)", text)
    degree_match = re.search(rf"def tau0Row{index:02d}TotalDegree\s*:\s*Nat\s*:=\s*(\d+)", text)
    row_match = re.search(rf"def tau0Row{index:02d}Vertices\s*:\s*List Nat\s*:=\s*\[(.*?)\]", text, re.S)
    require(count_match is not None, f"missing term count in {path}")
    require(degree_match is not None, f"missing total degree in {path}")
    require(row_match is not None, f"missing vertices in {path}")
    row = [int(x) for x in re.findall(r"\d+", row_match.group(1))]
    literal_terms = len(re.findall(r"\{\s*coeff\s*:=", text))
    return {
        "row": row,
        "term_count_decl": int(count_match.group(1)),
        "term_literal_count": literal_terms,
        "total_degree": int(degree_match.group(1)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exact-summary", default="tmp/mcert_tau0_v1_summary.json")
    ap.add_argument("--shard-manifest", default="tmp/tau0_rawpoly_shards_lean_emit_v2_manifest.json")
    ap.add_argument("--summary", default="tmp/tau0_artifact_audit_v1.json")
    args = ap.parse_args()

    exact_path = Path(args.exact_summary)
    manifest_path = Path(args.shard_manifest)
    exact = read_json(exact_path)
    manifest = read_json(manifest_path)

    require(exact.get("verdict") == "PASS", "tau0 exact verifier did not PASS")
    require(exact.get("all_denominators_cleared") is True, "tau0 denominators are not all cleared")
    require(exact.get("all_coefficients_nonnegative") is True, "tau0 coefficients are not all nonnegative")
    require(manifest.get("schema") == "tau0_rawpoly_shards_lean_emit_v1", "unexpected tau0 shard manifest schema")

    exact_rows = exact.get("rows") or []
    manifest_rows = manifest.get("rows") or []
    require(len(exact_rows) == 11, "unexpected tau0 exact row count")
    require(len(manifest_rows) == 11, "unexpected tau0 manifest row count")
    require(manifest.get("row_count") == 11, "manifest row_count mismatch")
    require(exact.get("row_count") == 11, "exact row_count mismatch")

    index_path = Path(manifest["index_output"])
    require(index_path.exists(), f"missing tau0 index Lean file: {index_path}")
    files = [index_path]
    row_audits: list[dict[str, Any]] = []
    for exact_row, manifest_row in zip(exact_rows, manifest_rows, strict=True):
        idx = int(manifest_row["index"])
        require(idx == int(exact_row["index"]), f"row index mismatch at {idx}")
        require(manifest_row["row"] == exact_row["row"], f"row vertices mismatch at {idx}")
        require(int(manifest_row["terms"]) == int(exact_row["terms"]), f"term count mismatch at {idx}")
        require(int(manifest_row["total_degree"]) == int(exact_row["total_degree"]), f"degree mismatch at {idx}")
        require(exact_row.get("denominator_cleared") is True, f"denominator not cleared at row {idx}")
        require(int(exact_row.get("negative_coeffs", -1)) == 0, f"negative coefficients at row {idx}")
        row_path = Path(manifest_row["output"])
        require(row_path.exists(), f"missing tau0 row Lean file: {row_path}")
        files.append(row_path)
        lean_row = parse_lean_row(row_path, idx)
        require(lean_row["row"] == manifest_row["row"], f"Lean row vertices mismatch at {idx}")
        require(lean_row["term_count_decl"] == int(manifest_row["terms"]), f"Lean term count declaration mismatch at {idx}")
        require(lean_row["term_literal_count"] == int(manifest_row["terms"]), f"Lean literal term count mismatch at {idx}")
        require(lean_row["total_degree"] == int(manifest_row["total_degree"]), f"Lean degree mismatch at {idx}")
        row_audits.append(
            {
                "index": idx,
                "row": manifest_row["row"],
                "terms": int(manifest_row["terms"]),
                "total_degree": int(manifest_row["total_degree"]),
                "lean": str(row_path),
                "sha256": sha256_file(row_path),
            }
        )

    total_terms = sum(r["terms"] for r in row_audits)
    require(total_terms == int(manifest["total_terms"]), "manifest total_terms mismatch")
    require(total_terms == sum(int(r["terms"]) for r in exact_rows), "exact total terms mismatch")
    require(max(r["total_degree"] for r in row_audits) == int(manifest["max_total_degree"]), "max degree mismatch")

    forbidden_hits: list[dict[str, Any]] = []
    for path in files:
        forbidden_hits.extend(scan_forbidden(path))
    require(not forbidden_hits, f"forbidden tokens found: {forbidden_hits[:3]}")

    out = {
        "schema": "tau0_artifact_audit_v1",
        "status": "PASS",
        "exact_summary": str(exact_path),
        "shard_manifest": str(manifest_path),
        "row_count": len(row_audits),
        "total_terms": total_terms,
        "max_total_degree": max(r["total_degree"] for r in row_audits),
        "denominators_cleared": True,
        "coefficients_nonnegative": True,
        "forbidden_tokens": list(FORBIDDEN),
        "forbidden_hits": 0,
        "sha256": {
            "exact_summary": sha256_file(exact_path),
            "shard_manifest": sha256_file(manifest_path),
            "index": sha256_file(index_path),
        },
        "rows": row_audits,
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
