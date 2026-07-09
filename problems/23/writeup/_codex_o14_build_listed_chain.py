#!/usr/bin/env python3
"""Build the source-only listed O14 dispatcher chain in a private olean root.

Lean's import lookup in this project expects dependencies in the first
`LEAN_PATH` root.  To avoid mutating Claude's accepted base cache and avoid
copying ~156 GB, this harness creates a hardlink mirror of the base cache,
unlinks only the target outputs, and writes rebuilt oleans into the private
root.

Default target chain:
  ListedClassifier -> ListedConcreteCover -> ListedLeafCover
  -> ListedChartCoverToODLFull

The harness is intentionally single-process.  It is safe to run while other
agents are using CPU, but it should still be scheduled with the shared
64-thread cap in mind.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path


DEFAULT_MODULES = [
    "Erdos23Delta0/O14/Generated/ListedClassifier.lean",
    "Erdos23Delta0/O14/Generated/ListedConcreteCover.lean",
    "Erdos23Delta0/O14/Generated/ListedLeafCover.lean",
    "Erdos23Delta0/O14/ListedChartCoverToODLFull.lean",
]

FORBIDDEN_PROBE_RE = re.compile(r"^\s*#print\s+axioms\b")


def generated_probe_hits(src_root: Path) -> list[dict[str, object]]:
    """Return generated Lean files that still contain local axiom probes."""
    generated = src_root / "Erdos23Delta0/O14/Generated"
    try:
        proc = subprocess.run(
            ["rg", "-n", r"^\s*#print\s+axioms\b", str(generated), "-g", "*.lean"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        proc = None
    if proc is not None:
        if proc.returncode == 1:
            return []
        if proc.returncode == 0:
            by_file: dict[str, list[int]] = {}
            for line in proc.stdout.splitlines():
                parts = line.rsplit(":", 2)
                if len(parts) < 2:
                    continue
                path_text, line_text = parts[0], parts[1]
                try:
                    line_no = int(line_text)
                except ValueError:
                    continue
                rel = str(Path(path_text).resolve().relative_to(src_root))
                by_file.setdefault(rel, []).append(line_no)
            return [
                {"file": file, "lines": lines}
                for file, lines in sorted(by_file.items())
            ]

    hits: list[dict[str, object]] = []
    for path in sorted(generated.rglob("*.lean")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        hit_lines = [
            idx for idx, line in enumerate(lines, start=1)
            if FORBIDDEN_PROBE_RE.match(line)
        ]
        if hit_lines:
            hits.append({
                "file": str(path.relative_to(src_root)),
                "lines": hit_lines,
            })
    return hits


def hardlink_mirror(src: Path, dst: Path) -> dict[str, int]:
    """Mirror files from `src` into `dst` using hardlinks where possible."""
    linked = 0
    existing = 0
    copied = 0
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        out = dst / rel
        if path.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            existing += 1
            continue
        try:
            os.link(path, out)
            linked += 1
        except OSError:
            shutil.copy2(path, out)
            copied += 1
    return {"linked": linked, "existing": existing, "copied": copied}


def active_base_cache_processes(base_cache: Path) -> list[str]:
    """Return active Lean/Lake processes whose command line mentions base_cache.

    The private cache is a hardlink mirror of the base cache.  Mirroring while
    another worker is actively writing that base cache is unsafe: the private
    run can inherit a moving dependency root.  On non-Windows platforms this
    guard is skipped because the current project runner is Windows-based.
    """
    if os.name != "nt":
        return []
    env = os.environ.copy()
    env["CODEX_BASE_CACHE_NEEDLE"] = str(base_cache)
    script = r"""
$needle = $env:CODEX_BASE_CACHE_NEEDLE
Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -and
    $_.CommandLine.Contains($needle) -and
    ($_.Name -eq 'lean.exe' -or $_.Name -eq 'lake.exe')
  } |
  ForEach-Object { "$($_.ProcessId):$($_.Name)" }
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def module_to_output(cache: Path, rel: str) -> Path:
    return cache / rel.replace(".lean", ".olean")


def run_lean(formal_root: Path, src_root: Path, cache: Path, rel: str) -> dict:
    src = src_root / rel
    out = module_to_output(cache, rel)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    env = os.environ.copy()
    env["LEAN_PATH"] = str(cache) + os.pathsep + env.get("LEAN_PATH", "")
    cmd = ["lake", "env", "lean", f"--root={src_root}", f"--o={out}", str(src)]
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=formal_root,
        env=env,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    lower = output.lower()
    ok = (
        proc.returncode == 0
        and "error:" not in lower
        and "sorryAx" not in output
        and "ofReduceBool" not in output
        and "Lean.trustCompiler" not in output
    )
    return {
        "module": rel,
        "rc": proc.returncode,
        "seconds": round(time.time() - started, 2),
        "ok": ok,
        "output": str(out),
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-4000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base-cache", type=Path, default=Path("tmp/claude_lean_o_base_v1"))
    parser.add_argument(
        "--private-cache",
        type=Path,
        default=Path("tmp/codex_lean_o_o14_listed_chain_v1"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("tmp/codex_o14_listed_chain_build_summary.json"),
    )
    parser.add_argument(
        "--allow-active-base-cache",
        action="store_true",
        help="Run even if Lean/Lake processes are currently writing the base cache.",
    )
    parser.add_argument(
        "--allow-generated-probes",
        action="store_true",
        help="Run even if generated Lean still contains local '#print axioms' probes.",
    )
    parser.add_argument("--module", action="append", dest="modules")
    args = parser.parse_args()

    root = args.root.resolve()
    formal_root = root / "formal-conjectures"
    src_root = root / "problems/23/lean"
    base_cache = (root / args.base_cache).resolve()
    private_cache = (root / args.private_cache).resolve()
    summary_path = (root / args.summary).resolve()
    modules = args.modules or DEFAULT_MODULES

    probe_hits = generated_probe_hits(src_root)
    if probe_hits and not args.allow_generated_probes:
        results = {
            "base_cache": str(base_cache),
            "private_cache": str(private_cache),
            "generated_probe_hits": probe_hits,
            "refused": True,
            "reason": "generated Lean still contains local '#print axioms' probes; strip them before final build",
            "modules": modules,
        }
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(json.dumps({"refused": True, "generated_probe_hit_files": len(probe_hits)}), flush=True)
        return 2

    active = active_base_cache_processes(base_cache)
    if active and not args.allow_active_base_cache:
        results = {
            "base_cache": str(base_cache),
            "private_cache": str(private_cache),
            "generated_probe_hits": probe_hits,
            "active_base_cache_processes": active,
            "refused": True,
            "reason": "base cache is actively used by Lean/Lake; rerun after wave drains or pass --allow-active-base-cache",
            "modules": modules,
        }
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(json.dumps({"refused": True, "active_base_cache_processes": active}), flush=True)
        return 2

    mirror = hardlink_mirror(base_cache, private_cache)
    results = {
        "base_cache": str(base_cache),
        "private_cache": str(private_cache),
        "active_base_cache_processes": active,
        "generated_probe_hits": probe_hits,
        "mirror": mirror,
        "modules": [],
    }

    all_ok = True
    for rel in modules:
        item = run_lean(formal_root, src_root, private_cache, rel)
        results["modules"].append(item)
        print(json.dumps({k: item[k] for k in ("module", "rc", "seconds", "ok")}), flush=True)
        all_ok = all_ok and item["ok"]
        if not item["ok"]:
            break

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
