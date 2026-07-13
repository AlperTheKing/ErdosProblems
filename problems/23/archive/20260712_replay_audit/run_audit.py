#!/usr/bin/env python3
"""Re-run the exact obstruction-paper candidate checks with an audit trail.

Each command runs sequentially so the declared 64-worker ceiling is respected.
The manifest is checkpointed after every command.  A nonzero process exit is
recorded, not hidden: the C5[3] two-row gate intentionally exits 1 when it
confirms that no local exchange exists.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOGS = HERE / "logs"
MANIFEST = HERE / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


SPECS = [
    {
        "id": "localobs_m6_m10",
        "script": "problems/23/writeup/_claude_v3_localobs_recheck.py",
        "args": ["10"],
        "expected_exit_codes": [0],
        "claim": "Independent exact footprint enumeration for m=6,...,10.",
    },
    {
        "id": "census_n5_n10",
        "script": "problems/23/writeup/_claude_v3_census_recheck.py",
        "args": ["5", "10"],
        "expected_exit_codes": [0],
        "claim": "Independent exact census of connected triangle-free graphs and maximum cuts for n=5,...,10.",
    },
    {
        "id": "counterexample_24vtx",
        "script": "problems/23/writeup/_claude_verify_24vtx_ce.py",
        "args": [],
        "expected_exit_codes": [0],
        "claim": "Exact 24-vertex counterexample to bare shortest-support expansion.",
    },
    {
        "id": "rotor_8vtx",
        "script": "problems/23/writeup/_claude_r39_8vtx_rotor_gate.py",
        "args": [],
        "expected_exit_codes": [0],
        "claim": "Exact 8-vertex neutral rotor verification.",
    },
    {
        "id": "r57_interface_counterexample_16vtx",
        "script": "problems/23/archive/20260712_replay_audit/inputs/r57_current_interface_counterexample/verify.py",
        "args": [],
        "expected_exit_codes": [0],
        "claim": "Exact 16-vertex R57 current-interface counterexample.",
    },
    {
        "id": "c5_3_two_row_exchange",
        "script": "problems/23/archive/20260712_replay_audit/inputs/cdc_wave1_exchange/c5_3_exchange_gate.py",
        "args": ["--workers", "61"],
        "expected_exit_codes": [1],
        "claim": "Exhaustive Hamming-distance-at-most-two exchange obstruction on balanced C5[3].",
    },
    {
        "id": "c5_3_global_collision_minimum",
        "script": "problems/23/archive/20260712_replay_audit/inputs/cdc_wave1_exchange/c5_3_global_min_gate.py",
        "args": ["--workers", "64"],
        "expected_exit_codes": [0],
        "claim": "Exact global collision-face optimization on balanced C5[3].",
    },
    {
        "id": "hoffman_singleton_exact",
        "script": "problems/23/archive/20260712_replay_audit/inputs/agent_reform_audit_1/b_hosi.py",
        "args": [],
        "expected_exit_codes": [0],
        "claim": "Exact Hoffman-Singleton construction, spectral lower bound, and matching explicit cut.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {
        "schema": "ERDOS23_OBSTRUCTION_PAPER_REPLAY_AUDIT_V1",
        "created_utc": utc_now(),
        "workspace": str(ROOT),
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "runs": [],
    }


def checkpoint(manifest: dict) -> None:
    manifest["updated_utc"] = utc_now()
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def summarize(text: str) -> list[str]:
    needles = (
        "PASS",
        "FAIL",
        "VERDICT",
        "SUMMARY",
        "graphs:",
        "maxcuts:",
        "hall violations:",
        "position anomalies:",
        "m=",
        '"verdict"',
        '"selectorVerdict"',
    )
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    selected = [line for line in lines if any(key in line for key in needles)]
    if not selected:
        selected = lines[-12:]
    return selected[-40:]


def run_one(spec: dict, manifest: dict) -> None:
    script = ROOT / spec["script"]
    command = [sys.executable, "-B", str(script), *spec["args"]]
    started = utc_now()
    start = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    elapsed = time.perf_counter() - start

    LOGS.mkdir(parents=True, exist_ok=True)
    stdout_path = LOGS / f"{spec['id']}.stdout.txt"
    stderr_path = LOGS / f"{spec['id']}.stderr.txt"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")

    record = {
        **spec,
        "command": command,
        "cwd": str(ROOT),
        "started_utc": started,
        "finished_utc": utc_now(),
        "elapsed_seconds": round(elapsed, 6),
        "exit_code": proc.returncode,
        "expected_exit": proc.returncode in spec["expected_exit_codes"],
        "script_sha256": sha256(script),
        "stdout": str(stdout_path.relative_to(HERE)),
        "stdout_sha256": sha256(stdout_path),
        "stderr": str(stderr_path.relative_to(HERE)),
        "stderr_sha256": sha256(stderr_path),
        "key_output": summarize(proc.stdout + "\n" + proc.stderr),
    }
    manifest["runs"] = [r for r in manifest["runs"] if r["id"] != spec["id"]]
    manifest["runs"].append(record)
    checkpoint(manifest)
    print(
        f"{spec['id']}: exit={proc.returncode} expected={record['expected_exit']} "
        f"elapsed={elapsed:.3f}s",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--skip-completed", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest()
    completed = {r["id"] for r in manifest["runs"] if r.get("expected_exit")}
    selected = [s for s in SPECS if not args.only or s["id"] in args.only]
    unknown = set(args.only) - {s["id"] for s in SPECS}
    if unknown:
        parser.error(f"unknown ids: {sorted(unknown)}")

    for spec in selected:
        if args.skip_completed and spec["id"] in completed:
            print(f"{spec['id']}: SKIP_COMPLETED", flush=True)
            continue
        run_one(spec, manifest)

    failures = [r["id"] for r in manifest["runs"] if not r["expected_exit"]]
    manifest["audit_status"] = "PASS" if not failures else "UNEXPECTED_EXIT"
    manifest["unexpected_exit_ids"] = failures
    checkpoint(manifest)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
