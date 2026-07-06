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

DEFAULT_MANIFEST = "tmp/branchb_lean_transpile_full_codex20260705_counts_manifest.json"
DEFAULT_BUILD_SUMMARY = "tmp/branchb_lean_module_build_codex20260705_counts_summary.json"
DEFAULT_DICTIONARY_MANIFEST = "tmp/branchb_dictionary_audit_lean_codex20260705_live_manifest.json"
DEFAULT_V2_SMOKE_SUMMARY = "tmp/branchb_v2_candidate_smoke_live_summary.json"
DEFAULT_SUMMARY = "tmp/branchb_lean_artifact_audit_current.json"


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


def lean_files_under(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".lean" else []
    return sorted(p for p in path.rglob("*.lean") if p.is_file())


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
    if not path_arg:
        return None, None, root / "<skipped-dictionary-manifest>"
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


def load_v2_smoke(root: Path, path_arg: str | None) -> tuple[dict | None, Path | None]:
    if not path_arg:
        return None, None
    smoke_path = rel_to_abs(root, path_arg)
    require(smoke_path.exists(), f"missing candidate_v2 smoke summary: {smoke_path}")
    smoke = read_json(smoke_path)
    require(smoke.get("schema") == "branchb_v2_candidate_smoke_v1", "unexpected candidate_v2 smoke schema")
    require(smoke.get("status") == "PASS", "candidate_v2 smoke did not PASS")
    counts = smoke.get("counts", {})
    require(counts.get("gate_b_candidate_counts") == {"candidate_v2": 1}, "candidate_v2 smoke did not exercise candidate_v2 only")
    require(counts.get("gate_b_rows") == 1, "candidate_v2 smoke expected exactly one Gate-B row")
    require(counts.get("op_steps", 0) > 0, "candidate_v2 smoke has no op steps")
    emit = smoke.get("emit", {})
    require(emit.get("returncode") == 0, "candidate_v2 smoke emitter failed")
    lean_build = smoke.get("lean_build", {})
    require(lean_build.get("returncode") == 0, "candidate_v2 smoke Lean build failed")
    dict_emit = smoke.get("dictionary_emit", {})
    require(dict_emit.get("returncode") == 0, "candidate_v2 smoke dictionary emitter failed")
    dict_manifest = smoke.get("dictionary_manifest_data") or {}
    require(dict_manifest.get("schema") == "branchb_dictionary_audit_lean_v2", "candidate_v2 smoke dictionary schema mismatch")
    dict_checks = dict_manifest.get("checks", {})
    require(bool(dict_checks) and all(dict_checks.values()), "candidate_v2 smoke dictionary checks failed")
    require(dict_manifest.get("row_term_occurrences") == smoke.get("dictionary_expected_row_occurrences"), "candidate_v2 smoke row occurrence mismatch")
    require(dict_manifest.get("op_piece_occurrences") == smoke.get("dictionary_expected_op_occurrences"), "candidate_v2 smoke op occurrence mismatch")
    dict_support = smoke.get("dictionary_support_lean_build") or {}
    require(dict_support.get("returncode") == 0, "candidate_v2 smoke dictionary support build failed")
    dict_build = smoke.get("dictionary_lean_build") or {}
    require(dict_build.get("returncode") == 0, "candidate_v2 smoke dictionary Lean build failed")
    lean_path = rel_to_abs(root, smoke["lean"])
    require(lean_path.exists(), f"missing candidate_v2 smoke Lean file: {lean_path}")
    lean_text = lean_path.read_text(encoding="utf-8")
    require("gateBCandidate := GateBCandidate.candidateV2" in lean_text, "candidate_v2 smoke Lean row missing candidateV2 tag")
    require("gateBCandidate := GateBCandidate.candidateV1" not in lean_text, "candidate_v2 smoke Lean row contains candidateV1 tag")
    return smoke, smoke_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="Branch-B Lean transpiler manifest to audit.",
    )
    ap.add_argument(
        "--build-summary",
        default=DEFAULT_BUILD_SUMMARY,
        help="Branch-B Lean module build summary to audit.",
    )
    ap.add_argument(
        "--dictionary-manifest",
        default=DEFAULT_DICTIONARY_MANIFEST,
        help="Dictionary-audit manifest. Use an empty string to skip dictionary checks.",
    )
    ap.add_argument(
        "--v2-smoke-summary",
        default=DEFAULT_V2_SMOKE_SUMMARY,
        help="Candidate_v2 smoke summary. Use an empty string only for legacy audits without the v2+dictionary path.",
    )
    ap.add_argument(
        "--lean-scan-root",
        default=None,
        help="Optional Lean file or directory for an additional tree-wide forbidden-token scan.",
    )
    ap.add_argument(
        "--summary",
        default=DEFAULT_SUMMARY,
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
    bridge = root / "problems/23/lean/Erdos23Delta0/Cert/BranchBBridge.lean"
    require(support.exists(), f"missing support file: {support}")
    require(index.exists(), f"missing aggregate index file: {index}")
    require(bridge.exists(), f"missing BranchBBridge Lean file: {bridge}")
    support_text = support.read_text(encoding="utf-8")
    require("gateBDominance : ScaledGeCert" in support_text, "support missing Gate-B dominance certificate field")
    require("ScaledGeCert.check r.gateBDominance" in support_text, "support does not check Gate-B dominance")

    input_jsonl = rel_to_abs(root, manifest["input"])
    signatures = rel_to_abs(root, manifest["signatures"])
    require(input_jsonl.exists(), f"missing input JSONL: {input_jsonl}")
    require(signatures.exists(), f"missing signature artifact: {signatures}")

    dictionary_arg = args.dictionary_manifest or ""
    smoke_arg = args.v2_smoke_summary or ""
    dictionary_manifest, dictionary_lean, dictionary_manifest_path = load_dictionary_audit(root, dictionary_arg)
    v2_smoke, v2_smoke_path = load_v2_smoke(root, smoke_arg)

    smoke_lean_files: list[Path] = []
    if v2_smoke is not None:
        smoke_lean = rel_to_abs(root, v2_smoke["lean"])
        require(smoke_lean.exists(), f"missing candidate_v2 smoke Lean file: {smoke_lean}")
        smoke_lean_files.append(smoke_lean)
        smoke_dict_lean_value = (v2_smoke.get("dictionary_manifest_data") or {}).get("lean_out")
        require(bool(smoke_dict_lean_value), "candidate_v2 smoke is missing dictionary Lean path")
        smoke_dict_lean = rel_to_abs(root, smoke_dict_lean_value)
        require(smoke_dict_lean.exists(), f"missing candidate_v2 smoke dictionary Lean file: {smoke_dict_lean}")
        smoke_lean_files.append(smoke_dict_lean)

    all_files = [support, bridge, *emitted]
    if index not in all_files:
        all_files.append(index)
    if dictionary_lean is not None:
        all_files.append(dictionary_lean)
    all_files.extend(smoke_lean_files)
    forbidden_hits = scan_forbidden(all_files)
    require(not forbidden_hits, f"forbidden Lean tokens found: {forbidden_hits[:3]}")

    tree_scan_files: list[Path] = []
    if args.lean_scan_root:
        scan_root = rel_to_abs(root, args.lean_scan_root)
        require(scan_root.exists(), f"missing Lean scan root: {scan_root}")
        tree_scan_files = lean_files_under(scan_root)
        require(tree_scan_files, f"Lean scan root contained no .lean files: {scan_root}")
        tree_forbidden_hits = scan_forbidden(tree_scan_files)
        require(
            not tree_forbidden_hits,
            f"tree-wide forbidden Lean tokens found: {tree_forbidden_hits[:3]}",
        )
    else:
        tree_forbidden_hits = []

    shard_files = sorted(p for p in emitted if p.name.startswith("Shard") and p.suffix == ".lean")
    record_counts = [shard_record_count(p) for p in shard_files]
    index_text = index.read_text(encoding="utf-8")
    expected_lengths = parse_expected_lengths(index_text)
    require(record_counts == expected_lengths, "shard record counts do not match aggregate theorem")

    total_rows = sum(record_counts)
    require(total_rows == manifest["counts"]["rows"], "manifest row count mismatch")
    require(total_rows == 14247, "unexpected Branch-B row total")
    require(len(shard_files) == 29, "unexpected shard count")
    checks = manifest.get("checks", {})
    require(checks.get("all_pressure_eq_scaled") is True, "manifest pressure checks not all true")
    require(checks.get("all_finite_margins_scaled") is True, "manifest finite-margin checks not all true")
    require(checks.get("all_gate_b_dominance_scaled") is True, "manifest Gate-B dominance checks not all true")
    require(
        manifest["counts"].get("case_counts")
        == {
            "DETOUR_RESIDUAL": 136,
            "FREE_PACKET_EXCHANGE": 3688,
            "MU_NUK": 800,
            "MU_NUK_REPAIRED": 126,
            "SPARSE_M1_BANKL_BYPASS": 9463,
            "TIGHT_ZERO": 34,
        },
        "unexpected Branch-B case counts",
    )
    require(manifest["counts"].get("gate_b_candidate_counts") == {"candidate_v1": 926, "none": 13321}, "unexpected Gate-B candidate counts")
    require(manifest["counts"].get("gate_b_rows") == 926, "unexpected Gate-B row count")
    require(manifest["counts"].get("op_steps") == 1852, "unexpected Gate-B op-step count")
    require("branchBTotalRows : natListSum branchBShardLengths = 14247" in index_text, "missing total-row theorem")
    require("branchBShardCount : branchBShardChecks.length = 29" in index_text, "missing shard-count theorem")
    require("branchBShardCaseCountVectors_expected" in index_text, "missing shard case-count theorem")
    require("branchBShardCandidateCountVectors_expected" in index_text, "missing shard candidate-count theorem")
    require("branchBShardGateBRowCounts_expected" in index_text, "missing shard Gate-B row-count theorem")

    require(build.get("failures") == [], "build summary contains failures")
    build_modules = {r.get("module") for r in build.get("results", [])}
    require("Erdos23Delta0.CertGraph" in build_modules, "CertGraph missing from build summary")
    require("Erdos23Delta0.Cert.BranchBBridge" in build_modules, "BranchBBridge missing from build summary")
    expected_build_count = 35 if dictionary_manifest is not None else 34
    require(build.get("count") == expected_build_count, "unexpected build module count")
    require(build.get("shard_count") == 29, "unexpected build shard count")
    if dictionary_manifest is not None:
        require("Erdos23Delta0.Cert.BranchBDictionaryAudit" in manifest.get("extra_index_imports", []), "dictionary audit missing from transpile manifest imports")
        require("import Erdos23Delta0.Cert.BranchBDictionaryAudit" in index_text, "dictionary audit missing from aggregate import")
        require("Erdos23Delta0.Cert.BranchBDictionaryAudit" in build_modules, "dictionary audit missing from build summary")

    legacy_recovered = [r for r in build.get("results", []) if r.get("recovered_tmp")]
    require(not legacy_recovered, "build summary uses legacy recovered_tmp stale-olean path")

    recovered = [r for r in build.get("results", []) if r.get("recovery_olean")]
    allowed_recovery = {"fresh_rerun", "fresh_rerun_tmp_copy"}
    for r in recovered:
        method = r.get("recovery_method")
        stderr = r.get("stderr", "")
        require(method in allowed_recovery, f"unexpected recovery method for {r.get('module')}: {method}")
        require("WRITE_PERMISSION_RETRY_OLEAN=" in stderr, f"missing fresh retry marker for {r.get('module')}")
        if method == "fresh_rerun":
            require("RECOVERED_OLEAN_FROM_FRESH_RERUN=" in stderr, f"missing fresh-rerun marker for {r.get('module')}")
        if method == "fresh_rerun_tmp_copy":
            require("RECOVERED_OLEAN_FROM_FRESH_RERUN_TMP=" in stderr, f"missing fresh-rerun tmp marker for {r.get('module')}")
        require("RECOVERED_OLEAN_FROM=" not in stderr, f"legacy stale recovery marker in {r.get('module')}")

    sha256 = {
        "input_jsonl": sha256_file(input_jsonl),
        "signatures": sha256_file(signatures),
        "transpile_manifest": sha256_file(manifest_path),
        "build_summary": sha256_file(build_path),
        "support": sha256_file(support),
        "index": sha256_file(index),
        "branchb_bridge": sha256_file(bridge),
        "dictionary_manifest": sha256_file(dictionary_manifest_path) if dictionary_manifest is not None else None,
        "dictionary_lean": sha256_file(dictionary_lean) if dictionary_lean is not None else None,
        "candidate_v2_smoke_summary": sha256_file(v2_smoke_path) if v2_smoke_path is not None else None,
        "candidate_v2_smoke_lean_files": [
            {"file": str(p), "sha256": sha256_file(p)} for p in smoke_lean_files
        ],
        "shards": [{"file": str(p), "sha256": sha256_file(p)} for p in shard_files],
    }

    out = {
        "schema": "branchb_lean_artifact_audit_v3",
        "manifest": str(manifest_path),
        "build_summary": str(build_path),
        "rows": total_rows,
        "shards": len(shard_files),
        "case_counts": manifest["counts"]["case_counts"],
        "gate_b_rows": manifest["counts"]["gate_b_rows"],
        "op_steps": manifest["counts"]["op_steps"],
        "forbidden_tokens": list(FORBIDDEN),
        "forbidden_hits": 0,
        "lean_scan_root": str(rel_to_abs(root, args.lean_scan_root)) if args.lean_scan_root else None,
        "lean_scan_files": len(tree_scan_files),
        "lean_scan_forbidden_hits": len(tree_forbidden_hits),
        "build_modules": build["count"],
        "build_failures": 0,
        "legacy_recovered_tmp_modules": len(legacy_recovered),
        "recovery_olean_modules": len(recovered),
        "recovery_methods": sorted({r.get("recovery_method") for r in recovered}),
        "recovered_tmp_modules": 0,
        "recovered_tmp_workaround": False,
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
        "candidate_v2_smoke": {
            "present": v2_smoke is not None,
            "summary": str(v2_smoke_path) if v2_smoke_path is not None else None,
            "status": v2_smoke.get("status") if v2_smoke else None,
            "gate_b_candidate_counts": v2_smoke.get("counts", {}).get("gate_b_candidate_counts") if v2_smoke else None,
            "op_steps": v2_smoke.get("counts", {}).get("op_steps") if v2_smoke else None,
            "lean_files": [str(p) for p in smoke_lean_files],
        },
        "status": "PASS",
    }
    summary = rel_to_abs(root, args.summary)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
