#!/usr/bin/env python3
"""Run one full-source feasibility-basis exact row certificate pipeline.

Pipeline:
  1. export a full-source feasibility-basis square core;
  2. solve the core exactly with the parallel modular CRT solver;
  3. convert the core solution to source-column coefficients;
  4. run the exact full source-solution checker.

The floating Clarabel solve is only a support/row selector.  The final status is
accepted only when the exact source-solution checker reports exact_ok=true.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_step(name: str, cmd: list[str], *, cwd: Path) -> dict:
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)
    return {
        "name": name,
        "returncode": proc.returncode,
        "seconds": round(time.time() - t0, 3),
        "cmd": cmd,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--prime-count", type=int, default=384)
    ap.add_argument("--modular-backend", choices=["python", "cpp"], default="cpp")
    ap.add_argument("--native-exe", type=Path, default=Path("tmp/codex_mod_prime_solve.exe"))
    ap.add_argument("--selector", choices=["highs-basis", "clarabel-support"], default="highs-basis")
    ap.add_argument("--solver", choices=["simplex", "ipm", "choose"], default="ipm")
    ap.add_argument("--presolve", choices=["on", "off", "choose"], default="on")
    ap.add_argument("--run-crossover", choices=["on", "off", "choose"], default="on")
    ap.add_argument("--highs-objective", choices=["l1", "random", "perturbed-l1"], default="l1")
    ap.add_argument("--highs-objective-seed", type=int, default=1729)
    ap.add_argument("--basis-column-mode", choices=["all-basic", "positive-basic"], default="all-basic")
    ap.add_argument("--basis-positive-tol", type=float, default=1.0e-9)
    ap.add_argument("--support-threshold", type=float, default=1.0e-4)
    ap.add_argument("--tight-row-tol", type=float, default=1.0e-7)
    ap.add_argument("--qr-oversample", type=int, default=4)
    ap.add_argument("--time-limit", type=float, default=None)
    ap.add_argument("--clarabel-objective", choices=["l1", "zero"], default="l1")
    ap.add_argument("--stop-after-core", action="store_true")
    ap.add_argument("--summary", type=Path, default=None)
    args = ap.parse_args()

    tag = args.tag or f"k{args.chart}_d{args.dominant}_febc_codex"
    tmp = REPO / "tmp"
    core = tmp / f"eq_odl1_rung2_core_{tag}.jsonl"
    core_summary = tmp / f"eq_odl1_rung2_core_{tag}.summary.json"
    core_solution = tmp / f"eq_odl1_rung2_core_solution_{tag}.jsonl"
    modular_summary = tmp / f"eq_odl1_rung2_modular_{tag}.json"
    crt_state = tmp / f"eq_odl1_rung2_modular_{tag}.crtstate.json"
    source_solution = tmp / f"eq_odl1_rung2_source_solution_{tag}.jsonl"
    convert_summary = tmp / f"eq_odl1_rung2_convert_{tag}.json"
    check_summary = tmp / f"eq_odl1_rung2_check_{tag}.json"
    summary = args.summary or (tmp / f"eq_odl1_rung2_pipeline_{tag}.json")

    steps: list[dict] = []
    extract_cmd = [
        sys.executable,
        "problems/23/writeup/_codex_eq_odl1_rung2_feasibility_basis_core.py",
        "--chart", str(args.chart),
        "--dominant", str(args.dominant),
        "--band", args.band,
        "--support", args.support,
        "--selector", args.selector,
        "--solver", args.solver,
        "--presolve", args.presolve,
        "--run-crossover", args.run_crossover,
        "--highs-objective", args.highs_objective,
        "--highs-objective-seed", str(args.highs_objective_seed),
        "--basis-column-mode", args.basis_column_mode,
        "--basis-positive-tol", str(args.basis_positive_tol),
        "--threads", str(args.threads),
        "--support-threshold", str(args.support_threshold),
        "--tight-row-tol", str(args.tight_row_tol),
        "--qr-oversample", str(args.qr_oversample),
        "--clarabel-objective", args.clarabel_objective,
        "--out-core", str(core),
        "--summary", str(core_summary),
    ]
    if args.time_limit is not None:
        extract_cmd.extend(["--time-limit", str(args.time_limit)])
    steps.append(run_step("extract_core", extract_cmd, cwd=REPO))
    if steps[-1]["returncode"] != 0 or not core_summary.exists():
        final = {"exact_ok": False, "abort": "extract_core_failed", "steps": steps}
        summary.write_text(json.dumps(final, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"exact_ok": False, "abort": final["abort"], "summary": str(summary)}, sort_keys=True))
        sys.exit(1)
    if not core.exists():
        final = {
            "exact_ok": False,
            "abort": "extract_core_not_exported",
            "core_summary": read_json(core_summary),
            "steps": steps,
        }
        summary.write_text(json.dumps(final, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"exact_ok": False, "abort": final["abort"], "summary": str(summary)}, sort_keys=True))
        sys.exit(1)

    if args.stop_after_core:
        core_payload = read_json(core_summary)
        final = {
            "exact_ok": None,
            "stopped_after_core": True,
            "core_summary": core_payload,
            "artifacts": {"core": str(core), "core_sha256": sha256(core)},
            "steps": steps,
        }
        summary.write_text(json.dumps(final, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"exact_ok": None, "stopped_after_core": True, "summary": str(summary)}, sort_keys=True))
        return

    if args.modular_backend == "cpp":
        solve_cmd = [
            sys.executable,
            "tmp/codex_modular_solve_cpp_parallel.py",
            "--core", str(core),
            "--prime-count", str(args.prime_count),
            "--workers", str(args.workers),
            "--native-exe", str(args.native_exe),
            "--store-solution", str(core_solution),
            "--summary", str(modular_summary),
            "--store-crt", str(crt_state),
        ]
    else:
        solve_cmd = [
            sys.executable,
            "tmp/claude_modular_solve_parallel.py",
            "--core", str(core),
            "--prime-count", str(args.prime_count),
            "--workers", str(args.workers),
            "--store-solution", str(core_solution),
            "--summary", str(modular_summary),
            "--store-crt", str(crt_state),
        ]
    steps.append(run_step("modular_solve", solve_cmd, cwd=REPO))
    if steps[-1]["returncode"] != 0 or not core_solution.exists() or not modular_summary.exists():
        final = {"exact_ok": False, "abort": "modular_solve_failed", "steps": steps}
        summary.write_text(json.dumps(final, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"exact_ok": False, "abort": final["abort"], "summary": str(summary)}, sort_keys=True))
        sys.exit(1)

    convert_cmd = [
        sys.executable,
        "tmp/convert_core_solution_to_source_solution.py",
        "--core", str(core),
        "--solution", str(core_solution),
        "--out", str(source_solution),
        "--summary", str(convert_summary),
    ]
    steps.append(run_step("convert", convert_cmd, cwd=REPO))
    if steps[-1]["returncode"] != 0 or not source_solution.exists():
        final = {"exact_ok": False, "abort": "convert_failed", "steps": steps}
        summary.write_text(json.dumps(final, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"exact_ok": False, "abort": final["abort"], "summary": str(summary)}, sort_keys=True))
        sys.exit(1)

    check_cmd = [
        sys.executable,
        "problems/23/writeup/_codex_eq_odl1_rung2_source_solution_check.py",
        "--chart", str(args.chart),
        "--dominant", str(args.dominant),
        "--band", args.band,
        "--support", args.support,
        "--solution", str(source_solution),
        "--summary", str(check_summary),
    ]
    steps.append(run_step("source_check", check_cmd, cwd=REPO))
    check = read_json(check_summary) if check_summary.exists() else {}
    exact_ok = bool(check.get("exact_ok")) and steps[-1]["returncode"] == 0
    final = {
        "schema": "eq_odl1_rung2_febc_pipeline_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "tag": tag,
        "exact_ok": exact_ok,
        "core_summary": read_json(core_summary),
        "modular_summary": read_json(modular_summary) if modular_summary.exists() else None,
        "convert_summary": read_json(convert_summary) if convert_summary.exists() else None,
        "check_summary": check,
        "artifacts": {
            "core": str(core),
            "core_sha256": sha256(core),
            "core_solution": str(core_solution),
            "core_solution_sha256": sha256(core_solution),
            "source_solution": str(source_solution),
            "source_solution_sha256": sha256(source_solution),
            "check": str(check_summary),
            "check_sha256": sha256(check_summary),
        },
        "steps": steps,
    }
    summary.write_text(json.dumps(final, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": exact_ok,
        "summary": str(summary),
        "core_dim": final["core_summary"].get("export_core", {}).get("dimension"),
        "full_negative_residual_count": check.get("full_negative_residual_count"),
        "solution_negative_count": check.get("solution_negative_count"),
    }, sort_keys=True))
    if not exact_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
