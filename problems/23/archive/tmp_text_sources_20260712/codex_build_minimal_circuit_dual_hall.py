import json
import os
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "formal-conjectures"
LEAN_ROOT = ROOT / "problems" / "23" / "lean"
SOURCE = LEAN_ROOT / "Erdos23Delta0" / "Ell5MinimalCircuitDualHall.lean"
BASE = ROOT / "tmp" / "claude_lean_o_base_v1"
OUT_ROOT = ROOT / "tmp" / "codex_lean_o_minimal_circuit_dual_hall"
OUT = OUT_ROOT / "Erdos23Delta0" / "Ell5MinimalCircuitDualHall.olean"
LOG = ROOT / "tmp" / "codex_minimal_circuit_dual_hall_build.txt"
SUMMARY = ROOT / "tmp" / "codex_minimal_circuit_dual_hall_build.json"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    # Lean resolves imports from the first package root only; the target olean
    # may still be written to the isolated output path via `--o`.
    env["LEAN_PATH"] = str(BASE)
    command = [
        "lake", "env", "lean", f"--root={LEAN_ROOT}",
        f"--o={OUT}", str(SOURCE),
    ]
    start = time.time()
    proc = subprocess.run(
        command, cwd=FORMAL, env=env, capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    elapsed = round(time.time() - start, 3)
    output = (proc.stdout or "") + (proc.stderr or "")
    LOG.write_text(output, encoding="utf-8")
    result = {
        "rc": proc.returncode,
        "seconds": elapsed,
        "error": "error:" in output.lower(),
        "olean": str(OUT),
    }
    SUMMARY.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True))
    if output:
        print(output[-6000:].encode("ascii", "backslashreplace").decode("ascii"))
    return 0 if proc.returncode == 0 and not result["error"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
