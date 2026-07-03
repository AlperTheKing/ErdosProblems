#!/usr/bin/env python3
"""Audit the generated Branch-B Lean certificate-data artifact.

This is a lightweight reproducibility gate for the accepted Branch-B
certificate-to-Lean layer.  It does not re-run Lean; it checks that the
transpiler manifest, generated Lean files, and recorded module-build summary
are mutually consistent and free of forbidden proof shortcuts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FORBIDDEN = ("native_decide", "sorry", "admit", "axiom", "unsafe")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel_to_abs(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path


def scan_forbidden(paths: list[Path]) -> list[dict]:
    hits: list[dict] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for token in FORBIDDEN:
                if token in line:
                    hits.append({"file": str(path), "line": lineno, "token": token})
    return hits


def shard_record_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    return len(re.findall(r"\{\s*name\s*:=", text))


def parse_expected_lengths(index_text: str) -> list[int]:
    match = re.search(
        r"branchBShardLengths\s*=\s*\[(.*?)\]\s*:=\s*by\s*rfl",
        index_text,
        flags=re.S,
    )
    if not match:
        raise ValueError("could not find branchBShardLengths expected theorem")
    return [int(x) for x in re.findall(r"\d+", match.group(1))]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--manifest",
        default="tmp/branchb_lean_transpile_full_v6_manifest.json",
    )
    ap.add_argument(
        "--build-summary",
        default="tmp/branchb_lean_module_build_v6g_summary.json",
    )
    ap.add_argument(
        "--summary",
        default="tmp/branchb_lean_artifact_audit_v1.json",
    )
    args = ap.parse_args()

    root = Path.cwd()
    manifest_path = rel_to_abs(root, args.manifest)
    build_path = rel_to_abs(root, args.build_summary)
    manifest = read_json(manifest_path)
    build = read_json(build_path)

    emitted = [rel_to_abs(root, p) for p in manifest["emitted"]]
    for path in emitted:
        require(path.exists(), f"missing emitted Lean file: {path}")

    support = rel_to_abs(root, manifest["support_out"])
    index = rel_to_abs(root, manifest["index_out"])
    require(support.exists(), f"missing support file: {support}")
    require(index.exists(), f"missing aggregate index file: {index}")

    all_files = [support, *emitted]
    if index not in all_files:
        all_files.append(index)
    forbidden_hits = scan_forbidden(all_files)
    require(not forbidden_hits, f"forbidden Lean tokens found: {forbidden_hits[:3]}")

    shard_files = sorted(p for p in emitted if p.name.startswith("Shard") and p.suffix == ".lean")
    record_counts = [shard_record_count(p) for p in shard_files]
    index_text = index.read_text(encoding="utf-8")
    expected_lengths = parse_expected_lengths(index_text)
    require(record_counts == expected_lengths, "shard record counts do not match aggregate theorem")

    total_rows = sum(record_counts)
    require(total_rows == manifest["counts"]["rows"], "manifest row count mismatch")
    require(total_rows == 14247, "unexpected Branch-B row total")
    require(len(shard_files) == 29, "unexpected shard count")
    require("branchBTotalRows : natListSum branchBShardLengths = 14247" in index_text, "missing total-row theorem")
    require("branchBShardCount : branchBShardChecks.length = 29" in index_text, "missing shard-count theorem")

    require(build.get("failures") == [], "build summary contains failures")
    require(build.get("count") == 32, "unexpected build module count")
    require(build.get("shard_count") == 29, "unexpected build shard count")

    recovered = [r for r in build.get("results", []) if r.get("recovered_tmp")]
    out = {
        "schema": "branchb_lean_artifact_audit_v1",
        "manifest": str(manifest_path),
        "build_summary": str(build_path),
        "rows": total_rows,
        "shards": len(shard_files),
        "case_counts": manifest["counts"]["case_counts"],
        "gate_b_rows": manifest["counts"]["gate_b_rows"],
        "op_steps": manifest["counts"]["op_steps"],
        "forbidden_tokens": list(FORBIDDEN),
        "forbidden_hits": 0,
        "build_modules": build["count"],
        "build_failures": 0,
        "recovered_tmp_modules": len(recovered),
        "recovered_tmp_workaround": len(recovered) > 0,
        "status": "PASS",
    }
    summary = rel_to_abs(root, args.summary)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
