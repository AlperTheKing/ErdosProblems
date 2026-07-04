#!/usr/bin/env python3
"""Reproduce the Branch-B Lean certificate-data handoff end to end.

This is an orchestration wrapper around the existing checked steps:
  1. compact dictionary-signature Lean audit emission;
  2. full Branch-B RowPilot shard emission with aggregate dictionary import;
  3. Lean module build for support + dictionary + pilot + shards + aggregate;
  4. SHA-pinned artifact audit.

It intentionally delegates the mathematical checks to the focused emit/build/audit
scripts so there is one reproducible command without duplicating proof logic.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DICT_EMITTER = Path("problems/23/writeup/_codex_branchb_dictionary_audit_to_lean.py")
LEAN_EMITTER = Path("problems/23/writeup/_codex_branchb_jsonl_to_lean.py")
LEAN_BUILDER = Path("problems/23/writeup/_codex_branchb_lean_build.py")
ARTIFACT_AUDIT = Path("problems/23/writeup/_codex_branchb_lean_artifact_audit.py")
DICT_MODULE = "Erdos23Delta0.Cert.BranchBDictionaryAudit"


def rel(path: Path) -> str:
    return str(path).replace("/", "\\") if sys.platform.startswith("win") else str(path)


def run_step(name: str, cmd: list[str]) -> dict:
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    result = {
        "name": name,
        "cmd": cmd,
        "returncode": proc.returncode,
        "seconds": round(time.time() - t0, 3),
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }
    print(f"{name} rc={proc.returncode} sec={result['seconds']}", flush=True)
    if proc.stdout:
        print(proc.stdout[-1000:], flush=True)
    if proc.stderr:
        print(proc.stderr[-1000:], file=sys.stderr, flush=True)
    if proc.returncode != 0:
        raise RuntimeError(f"step failed: {name}")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="v9")
    ap.add_argument("--input", default="tmp/bankl_branchb_gateb_final_v1.jsonl")
    ap.add_argument("--signatures", default="tmp/bankl_completion_op_sequence_core_signatures_v1.json")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--summary", default=None)
    args = ap.parse_args()

    tag = args.tag
    dictionary_manifest = Path(f"tmp/branchb_dictionary_audit_lean_{tag}_manifest.json")
    transpile_manifest = Path(f"tmp/branchb_lean_transpile_full_{tag}_manifest.json")
    build_summary = Path(f"tmp/branchb_lean_module_build_{tag}_summary.json")
    build_root = Path(f"tmp/branchb_lean_o_{tag}")
    audit_summary = Path(f"tmp/branchb_lean_artifact_audit_{tag}.json")
    reproduce_summary = Path(args.summary) if args.summary else Path(f"tmp/branchb_lean_reproduce_{tag}_summary.json")

    steps: list[dict] = []
    try:
        steps.append(run_step(
            "dictionary_emit",
            [
                sys.executable,
                "-B",
                rel(DICT_EMITTER),
                "--input",
                args.input,
                "--lean-out",
                "problems/23/lean/Erdos23Delta0/Cert/BranchBDictionaryAudit.lean",
                "--manifest",
                rel(dictionary_manifest),
            ],
        ))
        steps.append(run_step(
            "full_lean_emit",
            [
                sys.executable,
                "-B",
                rel(LEAN_EMITTER),
                "--mode",
                "full",
                "--input",
                args.input,
                "--signatures",
                args.signatures,
                "--manifest",
                rel(transpile_manifest),
                "--extra-index-import",
                DICT_MODULE,
            ],
        ))
        steps.append(run_step(
            "lean_build",
            [
                sys.executable,
                "-B",
                rel(LEAN_BUILDER),
                "--build-root",
                rel(build_root),
                "--summary",
                rel(build_summary),
                "--workers",
                str(args.workers),
            ],
        ))
        steps.append(run_step(
            "artifact_audit",
            [
                sys.executable,
                "-B",
                rel(ARTIFACT_AUDIT),
                "--manifest",
                rel(transpile_manifest),
                "--build-summary",
                rel(build_summary),
                "--dictionary-manifest",
                rel(dictionary_manifest),
                "--summary",
                rel(audit_summary),
            ],
        ))
        audit = json.loads((ROOT / audit_summary).read_text(encoding="utf-8"))
        status = "PASS" if audit.get("status") == "PASS" else "FAIL"
    except Exception as exc:
        audit = None
        status = "FAIL"
        error = repr(exc)
    else:
        error = None

    summary = {
        "schema": "branchb_lean_reproduce_v1",
        "status": status,
        "tag": tag,
        "input": args.input,
        "signatures": args.signatures,
        "workers": args.workers,
        "artifacts": {
            "dictionary_manifest": str((ROOT / dictionary_manifest).resolve()),
            "transpile_manifest": str((ROOT / transpile_manifest).resolve()),
            "build_summary": str((ROOT / build_summary).resolve()),
            "audit_summary": str((ROOT / audit_summary).resolve()),
        },
        "audit_status": audit.get("status") if audit else None,
        "audit_rows": audit.get("rows") if audit else None,
        "audit_build_modules": audit.get("build_modules") if audit else None,
        "audit_forbidden_hits": audit.get("forbidden_hits") if audit else None,
        "steps": steps,
        "error": error,
    }
    out = ROOT / reproduce_summary
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["schema", "status", "tag", "audit_status", "audit_rows", "audit_build_modules", "audit_forbidden_hits"]}, indent=2), flush=True)
    print(f"summary={out}", flush=True)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()