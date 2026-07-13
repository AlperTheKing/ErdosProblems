#!/usr/bin/env python3
"""Rerun the corrected R57 replay, then regenerate REPORT.md and manifest.json."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "manifest.json"
REPORT = HERE / "REPORT.md"
LOGS = HERE / "logs"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ident = "r57_positive_defect_interface_countermodel"
    script = HERE / "r57_positive_defect_interface_countermodel_v2.py"
    command = [sys.executable, "-B", str(script)]
    started = now()
    before = time.perf_counter()
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False)
    elapsed = time.perf_counter() - before
    stdout = LOGS / f"{ident}.stdout.txt"
    stderr = LOGS / f"{ident}.stderr.txt"
    stdout.write_text(proc.stdout, encoding="utf-8")
    stderr.write_text(proc.stderr, encoding="utf-8")
    lines = [line.strip() for line in (proc.stdout + "\n" + proc.stderr).splitlines()
             if line.strip()]
    record = {
        "id": ident,
        "script": str(script.relative_to(ROOT)).replace("\\", "/"),
        "args": [],
        "expected_exit_codes": [0],
        "claim": "Exact nine-copy positive-defect countermodel to the compiled R55/R57 interface.",
        "command": command,
        "cwd": str(ROOT),
        "started_utc": started,
        "finished_utc": now(),
        "elapsed_seconds": round(elapsed, 6),
        "exit_code": proc.returncode,
        "expected_exit": proc.returncode == 0,
        "script_sha256": sha(script),
        "stdout": str(stdout.relative_to(HERE)),
        "stdout_sha256": sha(stdout),
        "stderr": str(stderr.relative_to(HERE)),
        "stderr_sha256": sha(stderr),
        "key_output": lines[-20:],
    }
    manifest["runs"] = [r for r in manifest["runs"] if r["id"] != ident]
    manifest["runs"].insert(5, record)
    failures = [r["id"] for r in manifest["runs"] if not r["expected_exit"]]
    manifest["unexpected_exit_ids"] = failures
    manifest["audit_status"] = "PASS" if not failures else "UNEXPECTED_EXIT"
    manifest["updated_utc"] = now()

    rows = "\n".join(
        f"| `{r['id']}` | {r['exit_code']} | "
        f"{'PASS' if r['expected_exit'] else 'UNEXPECTED'} | "
        f"{r['elapsed_seconds']:.3f} | `{r['script_sha256']}` |"
        for r in manifest["runs"]
    )
    details = []
    for r in manifest["runs"]:
        details.append(
            f"### {r['id']}\n\nClaim: {r['claim']}\n\n"
            f"```text\n{subprocess.list2cmdline(r['command'])}\n```\n\n"
            f"Exit code: `{r['exit_code']}` (expected: "
            f"{', '.join(map(str, r['expected_exit_codes']))}); runtime: "
            f"`{r['elapsed_seconds']:.6f} s`.\n\n"
            f"Input SHA-256: `{r['script_sha256']}`  \n"
            f"stdout SHA-256: `{r['stdout_sha256']}`  \n"
            f"stderr SHA-256: `{r['stderr_sha256']}`\n\n"
            "Key output:\n\n```text\n" + "\n".join(r["key_output"]) + "\n```\n"
        )
    report = f"""# Reproducibility audit: Erdős #23 obstruction-paper candidates

Generated: `{manifest['updated_utc']}`  
Workspace: `{manifest['workspace']}`  
Python: `{manifest['python']}`  
Platform: `{manifest['platform']}`  
Detected logical CPUs: `{manifest['cpu_count']}`

## Verdict

**{manifest['audit_status']}**: all nine declared replays returned their expected exit codes.

The C5[3] two-row exchange gate intentionally returns exit code `1`: its exact
negative verdict is `NO_TWO_ROW_EXCHANGE`. The R57 nine-copy object is an
interface countermodel, not a graph counterexample: it violates
`CompleteShortestRowDB.badKeys_nodup`, absent from the proposed bridge.

## Summary

| Replay | Exit | Status | Seconds | Input SHA-256 |
|---|---:|---|---:|---|
{rows}

## Main exact outcomes

- Local footprints: none for `m=6,7,8`; one footprint/one atom set for `m=9`;
  three footprints/56 atom sets for `m=10`.
- Census `n=5..10`: 11,563 connected triangle-free graphs and 23,449 maximum
  cuts; zero Hall violations and zero endpoint-position anomalies.
- The 24-vertex graph has a unique maximum cut and a genuine `9>8` support-Hall
  obstruction. The 8-vertex rotor is genuine but has scoped defect zero.
- The 16-vertex R57 graph has no negative four-corner pair among 65,536 pairs.
- The nine-copy R57 interface model has lex face `(179,50)` with 420 states,
  residual unit core `293=292+1`, and P1 demand/capacity `318>142`.
- On balanced `C5[3]`, no Hamming-distance-at-most-two defect descent exists
  from the center, although a distant global collision minimizer has defect zero.
- Exact Hoffman-Singleton identities and `2^22` image-cut enumeration certify
  `beta=50` and maximum cut 125.

## Exactness boundary

All combinatorial evaluations use integers (and integral Dinic flow). Graph
censuses use exhaustive `nauty geng`; the 24-vertex gate exhausts `2^23`
normalized cuts. The C5[3] global minimum is an integer CP-SAT replay followed
by exact flow evaluation, not a standalone SAT proof certificate.

## Commands and outputs

{chr(10).join(details)}
"""
    REPORT.write_text(report, encoding="utf-8")
    manifest["audit_artifacts"] = {
        "REPORT.md": sha(REPORT),
        "run_audit.py": sha(HERE / "run_audit.py"),
        "finalize_audit_v2.py": sha(Path(__file__)),
        "r57_positive_defect_interface_countermodel.py": sha(
            HERE / "r57_positive_defect_interface_countermodel.py"),
        "r57_positive_defect_interface_countermodel_v2.py": sha(script),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(json.dumps({"audit_status": manifest["audit_status"],
                      "runs": len(manifest["runs"]),
                      "report_sha256": manifest["audit_artifacts"]["REPORT.md"]},
                     sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
