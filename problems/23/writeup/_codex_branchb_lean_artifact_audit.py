#!/usr/bin/env python3
"""Audit generated Branch-B Lean certificate-data artifacts.

This reproducibility gate checks that the accepted Branch-B transpiler manifest,
generated Lean files, optional compact dictionary audit, and recorded module-build
summary are mutually consistent and free of forbidden proof shortcuts.
"""

from __future__ import annotations

import argparse
import hashlib
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

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def load_dictionary_audit(root: Path, path_arg: str) -> tuple[dict | None, Path | None, Path]:
    manifest_path = rel_to_abs(root, path_arg)
    if not manifest_path.exists():
        return None, None, manifest_path
    manifest = read_json(manifest_path)
    schema = manifest.get("schema")
    require(schema in {"branchb_dictionary_audit_lean_v1", "branchb_dictionary_audit_lean_v2"}, "unexpected dictionary audit schema")
    require(manifest.get("row_signature_count") == 38, "unexpected row dictionary signature count")
    require(manifest.get("op_signature_count") == 10, "unexpected op dictionary signature count")
    require(manifest.get("row_term_occurrences") == 19988, "unexpected row dictionary occurrence total")
    require(manifest.get("op_piece_occurrences") == 713, "unexpected op dictionary occurrence total")
    checks = manifest.get("checks", {})
    require(bool(checks), "missing dictionary audit checks")
    require(all(checks.values()), "dictionary audit manifest contains false checks")
    if schema == "branchb_dictionary_audit_lean_v2":
        require(checks.get("lean_denominator_guard_emitted") is True, "missing dictionary denominator-guard check")
    lean_out = rel_to_abs(root, manifest["lean_out"])
    require(lean_out.exists(), f"missing dictionary audit Lean file: {lean_out}")
    text = lean_out.read_text(encoding="utf-8")
    require("def RatLit.valid" in text, "missing RatLit denominator-valid checker")
    require("RatLit.valid a && RatLit.valid b && RatLit.valid c" in text, "RatLit.mulEq does not guard denominators")
    require("branchBRowDictSignatures_check" in text, "missing row dictionary check theorem")
    require("branchBOpDictSignatures_check" in text, "missing op dictionary check theorem")
    require("branchBRowDictOccurrenceTotal" in text, "missing row occurrence theorem")
    require("branchBOpDictOccurrenceTotal" in text, "missing op occurrence theorem")
    return manifest, lean_out, manifest_path


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
        "--dictionary-manifest",
        default="tmp/branchb_dictionary_audit_lean_v1_manifest.json",
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

    input_jsonl = rel_to_abs(root, manifest["input"])
    signatures = rel_to_abs(root, manifest["signatures"])
    require(input_jsonl.exists(), f"missing input JSONL: {input_jsonl}")
    require(signatures.exists(), f"missing signature artifact: {signatures}")

    dictionary_manifest, dictionary_lean, dictionary_manifest_path = load_dictionary_audit(root, args.dictionary_manifest)

    all_files = [support, *emitted]
    if index not in all_files:
        all_files.append(index)
    if dictionary_lean is not None:
        all_files.append(dictionary_lean)
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
    build_modules = {r.get("module") for r in build.get("results", [])}
    expected_build_count = 33 if dictionary_manifest is not None else 32
    require(build.get("count") == expected_build_count, "unexpected build module count")
    require(build.get("shard_count") == 29, "unexpected build shard count")
    if dictionary_manifest is not None:
        require("Erdos23Delta0.Cert.BranchBDictionaryAudit" in manifest.get("extra_index_imports", []), "dictionary audit missing from transpile manifest imports")
        require("import Erdos23Delta0.Cert.BranchBDictionaryAudit" in index_text, "dictionary audit missing from aggregate import")
        require("Erdos23Delta0.Cert.BranchBDictionaryAudit" in build_modules, "dictionary audit missing from build summary")

    recovered = [r for r in build.get("results", []) if r.get("recovered_tmp")]
    sha256 = {
        "input_jsonl": sha256_file(input_jsonl),
        "signatures": sha256_file(signatures),
        "transpile_manifest": sha256_file(manifest_path),
        "build_summary": sha256_file(build_path),
        "support": sha256_file(support),
        "index": sha256_file(index),
        "dictionary_manifest": sha256_file(dictionary_manifest_path) if dictionary_manifest is not None else None,
        "dictionary_lean": sha256_file(dictionary_lean) if dictionary_lean is not None else None,
        "shards": [{"file": str(p), "sha256": sha256_file(p)} for p in shard_files],
    }

    out = {
        "schema": "branchb_lean_artifact_audit_v2",
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
        "sha256": sha256,
        "dictionary_audit": {
            "present": dictionary_manifest is not None,
            "manifest": str(dictionary_manifest_path) if dictionary_manifest is not None else None,
            "lean_out": str(dictionary_lean) if dictionary_lean is not None else None,
            "row_signature_count": dictionary_manifest.get("row_signature_count") if dictionary_manifest else None,
            "row_term_occurrences": dictionary_manifest.get("row_term_occurrences") if dictionary_manifest else None,
            "op_signature_count": dictionary_manifest.get("op_signature_count") if dictionary_manifest else None,
            "op_piece_occurrences": dictionary_manifest.get("op_piece_occurrences") if dictionary_manifest else None,
        },
        "status": "PASS",
    }
    summary = rel_to_abs(root, args.summary)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
