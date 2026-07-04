#!/usr/bin/env python3
"""Audit generated Rung-2 Lean certificate-data artifacts."""

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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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
    return len(re.findall(r"\{\s*sourceCol\s*:=", text))


def parse_expected_lengths(index_text: str) -> list[int]:
    match = re.search(
        r"rung2CoeffShardLengths\s*=\s*\[(.*?)\]\s*:=\s*by\s*rfl",
        index_text,
        flags=re.S,
    )
    if not match:
        raise ValueError("could not find rung2CoeffShardLengths expected theorem")
    return [int(x) for x in re.findall(r"\d+", match.group(1))]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="tmp/eq_odl1_rung2_lean_transpile_v4_manifest.json")
    ap.add_argument("--build-summary", default="tmp/eq_odl1_rung2_lean_build_v4_summary.json")
    ap.add_argument("--certificate-manifest", default="tmp/eq_odl1_rung2_repaired_certificate_manifest_v1.json")
    ap.add_argument("--summary", default="tmp/eq_odl1_rung2_lean_artifact_audit_v1.json")
    args = ap.parse_args()

    root = Path.cwd()
    manifest_path = rel_to_abs(root, args.manifest)
    build_path = rel_to_abs(root, args.build_summary)
    cert_manifest_path = rel_to_abs(root, args.certificate_manifest)
    manifest = read_json(manifest_path)
    build = read_json(build_path)
    cert_manifest = read_json(cert_manifest_path)

    require(manifest.get("schema") == "eq_odl1_rung2_lean_transpile_v1", "unexpected transpile schema")
    require(cert_manifest.get("exact_ok") is True, "certificate manifest is not exact_ok")
    require(manifest.get("solution_sha256") == cert_manifest.get("solution_jsonl_sha256"), "solution hash mismatch")

    emitted = [rel_to_abs(root, p) for p in manifest["emitted"]]
    for path in emitted:
        require(path.exists(), f"missing emitted Lean file: {path}")

    support = rel_to_abs(root, manifest["support_out"])
    index = rel_to_abs(root, manifest["index_out"])
    require(support.exists(), f"missing support file: {support}")
    require(index.exists(), f"missing index file: {index}")

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
    require(sum(record_counts) == manifest["rows"], "manifest row count mismatch")
    require(sum(record_counts) == cert_manifest["solution_jsonl_records"], "certificate manifest record count mismatch")
    require(sum(record_counts) == 2687, "unexpected Rung-2 coefficient count")
    require(len(shard_files) == manifest["shards"], "manifest shard count mismatch")
    require("rung2RepairedMeta_check" in index_text, "missing metadata check theorem")
    require("rung2CoeffTotalRows_matches_meta" in index_text, "missing total-row metadata theorem")

    require(build.get("failures") == [], "build summary contains failures")
    require(build.get("count") == manifest["shards"] + 2, "unexpected build module count")
    require(build.get("shard_count") == manifest["shards"], "unexpected build shard count")

    recovered = [r for r in build.get("results", []) if r.get("recovered_tmp")]
    out = {
        "schema": "eq_odl1_rung2_lean_artifact_audit_v1",
        "manifest": str(manifest_path),
        "build_summary": str(build_path),
        "certificate_manifest": str(cert_manifest_path),
        "rows": sum(record_counts),
        "shards": len(shard_files),
        "forbidden_tokens": list(FORBIDDEN),
        "forbidden_hits": 0,
        "build_modules": build["count"],
        "build_failures": 0,
        "recovered_tmp_modules": len(recovered),
        "recovered_tmp_workaround": len(recovered) > 0,
        "solution_sha256": manifest["solution_sha256"],
        "status": "PASS",
    }
    summary = rel_to_abs(root, args.summary)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
