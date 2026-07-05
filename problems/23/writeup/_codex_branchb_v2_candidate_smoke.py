#!/usr/bin/env python3
"""Synthetic candidate_v2 smoke gate for the Branch-B Lean emitter.

The current accepted Branch-B JSONL carries only ``candidate_v1`` rows.  This
gate proves the v2 path is not merely dead code: it clones one valid v1 row,
places the same op-sequence under ``candidate_v2``, blanks candidate_v1, runs
the real Lean emitter, and compiles the resulting self-contained Lean file.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_v1_row(rows: list[dict]) -> tuple[int, dict]:
    for idx, row in enumerate(rows):
        gate_b = row.get("gate_b_dictionary") or {}
        seq = (gate_b.get("candidate_v1") or {}).get("op_sequence")
        if seq:
            return idx, row
    raise RuntimeError("no candidate_v1 op-sequence row found")


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> dict:
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "seconds": round(time.time() - t0, 3),
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("tmp/bankl_branchb_gateb_final_v1.jsonl"))
    ap.add_argument("--emitter", type=Path, default=Path("problems/23/writeup/_codex_branchb_jsonl_to_lean.py"))
    ap.add_argument("--dictionary-emitter", type=Path, default=Path("problems/23/writeup/_codex_branchb_dictionary_audit_to_lean.py"))
    ap.add_argument("--out-jsonl", type=Path, default=Path("tmp/branchb_v2_candidate_smoke_input.jsonl"))
    ap.add_argument("--out-dir", type=Path, default=Path("tmp/branchb_v2_candidate_smoke_lean"))
    ap.add_argument("--manifest", type=Path, default=Path("tmp/branchb_v2_candidate_smoke_manifest.json"))
    ap.add_argument("--olean", type=Path, default=Path("tmp/branchb_v2_candidate_smoke.olean"))
    ap.add_argument(
        "--dict-lean-out",
        type=Path,
        default=Path("problems/23/lean/Erdos23Delta0/Cert/BranchBDictionaryAuditV2Smoke.lean"),
    )
    ap.add_argument("--dict-manifest", type=Path, default=Path("tmp/branchb_v2_candidate_dictionary_smoke_manifest.json"))
    ap.add_argument("--dict-olean", type=Path, default=Path("tmp/branchb_v2_candidate_dictionary_smoke.olean"))
    ap.add_argument(
        "--dict-build-root",
        type=Path,
        default=Path("tmp/branchb_v2_candidate_dictionary_smoke_o"),
        help="Temporary Lean olean root for dictionary smoke support imports.",
    )
    ap.add_argument("--summary", type=Path, default=Path("tmp/branchb_v2_candidate_smoke_summary.json"))
    args = ap.parse_args()

    input_path = ROOT / args.input
    rows = read_jsonl(input_path)
    source_idx, source_row = find_v1_row(rows)
    smoke_row = copy.deepcopy(source_row)
    gate_b = smoke_row.setdefault("gate_b_dictionary", {})
    candidate_v1 = copy.deepcopy(gate_b["candidate_v1"])
    gate_b["candidate_v2"] = candidate_v1
    gate_b["candidate_v1"] = {}
    gate_b["candidate_complete"] = True
    gate_b["complete"] = True

    out_jsonl = ROOT / args.out_jsonl
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl.write_text(json.dumps(smoke_row, sort_keys=True) + "\n", encoding="utf-8")

    out_dir = ROOT / args.out_dir
    manifest = ROOT / args.manifest
    emitter_cmd = [
        sys.executable,
        "-B",
        str(ROOT / args.emitter),
        "--input",
        str(out_jsonl),
        "--mode",
        "full",
        "--self-contained",
        "--out-dir",
        str(out_dir),
        "--manifest",
        str(manifest),
        "--shard-size",
        "1",
    ]
    emit_result = run(emitter_cmd, cwd=ROOT)
    if emit_result["returncode"] != 0:
        raise SystemExit(json.dumps({"status": "FAIL_EMIT", "emit": emit_result}, indent=2))

    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    counts = manifest_data.get("counts") or {}
    candidate_counts = counts.get("gate_b_candidate_counts") or {}
    emitted = manifest_data.get("emitted") or []
    if candidate_counts != {"candidate_v2": 1}:
        raise SystemExit(
            json.dumps(
                {
                    "status": "FAIL_CANDIDATE_COUNTS",
                    "candidate_counts": candidate_counts,
                    "manifest": str(manifest),
                },
                indent=2,
            )
        )
    if counts.get("gate_b_rows") != 1 or counts.get("op_steps", 0) <= 0:
        raise SystemExit(json.dumps({"status": "FAIL_OP_COUNTS", "counts": counts}, indent=2))
    if len(emitted) != 1:
        raise SystemExit(json.dumps({"status": "FAIL_EMITTED_COUNT", "emitted": emitted}, indent=2))

    lean_path = ROOT / emitted[0]
    lean_text = lean_path.read_text(encoding="utf-8")
    if "gateBCandidate := GateBCandidate.candidateV2" not in lean_text:
        raise SystemExit(json.dumps({"status": "FAIL_NO_CANDIDATEV2_TAG", "lean": str(lean_path)}, indent=2))
    if "gateBCandidate := GateBCandidate.candidateV1" in lean_text:
        raise SystemExit(json.dumps({"status": "FAIL_CANDIDATEV1_TAG_PRESENT", "lean": str(lean_path)}, indent=2))

    formal_root = ROOT / "formal-conjectures"
    src_root = ROOT
    olean = ROOT / args.olean
    olean.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    build_cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={olean}", str(lean_path)]
    build_result = run(build_cmd, cwd=formal_root, env=env)

    sys.path.insert(0, str(ROOT / "problems/23/writeup"))
    import _codex_branchb_dictionary_audit_to_lean as dict_audit  # type: ignore

    row_sigs, op_sigs, *_ = dict_audit.collect(out_jsonl)
    expected_row_occurrences = sum(row_sigs.values())
    expected_op_occurrences = sum(op_sigs.values())
    dict_lean = ROOT / args.dict_lean_out
    dict_manifest = ROOT / args.dict_manifest
    dict_cmd = [
        sys.executable,
        "-B",
        str(ROOT / args.dictionary_emitter),
        "--input",
        str(out_jsonl),
        "--lean-out",
        str(dict_lean),
        "--manifest",
        str(dict_manifest),
        "--expected-row-occurrences",
        str(expected_row_occurrences),
        "--expected-op-occurrences",
        str(expected_op_occurrences),
    ]
    dict_emit_result = run(dict_cmd, cwd=ROOT)
    dict_manifest_data = None
    dict_support_build_result = None
    dict_build_result = None
    if dict_emit_result["returncode"] == 0:
        dict_manifest_data = json.loads(dict_manifest.read_text(encoding="utf-8"))
        dict_src_root = ROOT / "problems/23/lean"
        dict_build_root = ROOT / args.dict_build_root
        support_lean = dict_src_root / "Erdos23Delta0/Cert/BranchBSupport.lean"
        support_olean = dict_build_root / "Erdos23Delta0/Cert/BranchBSupport.olean"
        support_olean.parent.mkdir(parents=True, exist_ok=True)
        support_cmd = [
            "lake",
            "env",
            "lean",
            f"--root={dict_src_root}",
            f"--o={support_olean}",
            str(support_lean),
        ]
        dict_support_build_result = run(support_cmd, cwd=formal_root, env=env)
        dict_olean = ROOT / args.dict_olean
        dict_olean.parent.mkdir(parents=True, exist_ok=True)
        dict_env = os.environ.copy()
        dict_env["LEAN_PATH"] = str(dict_build_root) + os.pathsep + dict_env.get("LEAN_PATH", "")
        dict_build_cmd = [
            "lake",
            "env",
            "lean",
            f"--root={dict_src_root}",
            f"--o={dict_olean}",
            str(dict_lean),
        ]
        if dict_support_build_result["returncode"] == 0:
            dict_build_result = run(dict_build_cmd, cwd=formal_root, env=dict_env)

    status = "PASS"
    if build_result["returncode"] != 0:
        status = "FAIL_LEAN"
    elif dict_emit_result["returncode"] != 0:
        status = "FAIL_DICT_EMIT"
    elif not dict_manifest_data or not all(dict_manifest_data.get("checks", {}).values()):
        status = "FAIL_DICT_MANIFEST_CHECKS"
    elif not dict_support_build_result or dict_support_build_result["returncode"] != 0:
        status = "FAIL_DICT_SUPPORT_LEAN"
    elif not dict_build_result or dict_build_result["returncode"] != 0:
        status = "FAIL_DICT_LEAN"

    summary = {
        "schema": "branchb_v2_candidate_smoke_v1",
        "status": status,
        "source_index": source_idx,
        "source_input": str(input_path),
        "synthetic_input": str(out_jsonl),
        "lean": str(lean_path),
        "manifest": str(manifest),
        "counts": counts,
        "dictionary_expected_row_occurrences": expected_row_occurrences,
        "dictionary_expected_op_occurrences": expected_op_occurrences,
        "dictionary_manifest": str(dict_manifest),
        "emit": emit_result,
        "lean_build": build_result,
        "dictionary_emit": dict_emit_result,
        "dictionary_manifest_data": dict_manifest_data,
        "dictionary_support_lean_build": dict_support_build_result,
        "dictionary_lean_build": dict_build_result,
    }
    (ROOT / args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"{status} branchb candidate_v2 smoke "
        f"source_index={source_idx} op_steps={counts.get('op_steps')} lean={lean_path}"
    )
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
