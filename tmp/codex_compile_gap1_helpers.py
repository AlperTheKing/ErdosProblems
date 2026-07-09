import json
import os
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = (ROOT / "tmp" / "claude_lean_o_base_v1").resolve()
LEAN_ROOT = ROOT / "problems" / "23" / "lean"
MODULE_DIR = LEAN_ROOT / "Erdos23Delta0"
SUMMARY = ROOT / "tmp" / "codex_gap1_helper_compile_summary.json"

MODULES = [
    "BankedCutDominationExtras",
    "Ell5DistancePrune",
    "Ell5GapLemmas",
    "Ell5UnionCount",
    "Ell5GeodesicUnion",
]


def main() -> int:
    env = os.environ.copy()
    env["LEAN_PATH"] = str(BASE) + os.pathsep + env.get("LEAN_PATH", "")
    results = []
    for module in MODULES:
        file_path = MODULE_DIR / f"{module}.lean"
        cmd = [
            "lake",
            "env",
            "lean",
            f"--root={LEAN_ROOT}",
            str(file_path),
        ]
        proc = subprocess.run(
            cmd,
            cwd=ROOT / "formal-conjectures",
            env=env,
            text=True,
            capture_output=True,
            timeout=240,
        )
        print(f"MODULE {module} RC {proc.returncode}")
        if proc.stdout:
            print(proc.stdout[-2000:])
        if proc.stderr:
            print(proc.stderr[-2000:])
        results.append(
            {
                "module": module,
                "rc": proc.returncode,
                "stdout_tail": proc.stdout[-4000:],
                "stderr_tail": proc.stderr[-4000:],
            }
        )
    SUMMARY.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0 if all(item["rc"] == 0 for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
