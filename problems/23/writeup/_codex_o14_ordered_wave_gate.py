#!/usr/bin/env python3
"""Dependency-ordered O14 sharded Lean gate.

This is a Codex-namespaced companion for the O14 generated payload gate.  It is
safe by default: without ``--execute`` it only classifies files and reports the
ordered phases.  The key difference from the failed wave is that chart bridges
are not treated as ordinary shards:

  Support -> Base/MS/Pairs shards -> ChartNNNCone aggregators
  -> ChartNNNBridge wrappers -> registries

That order matches the generated imports.  In particular, every
``ChartNNNBridge.lean`` imports ``ChartNNNCone.lean``, so bridge modules must be
built only after the corresponding cone aggregator olean exists.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path("E:/Projects/ErdosProblems")
FORMAL = ROOT / "formal-conjectures"
SRC = ROOT / "problems/23/lean"
BASE = ROOT / "tmp/claude_lean_o_base_v1"
CP = SRC / "Erdos23Delta0/O14/Generated/ChartPayloads"
DEFAULT_SUMMARY = ROOT / "tmp/codex_o14_ordered_wave_gate_summary.json"

TOKEN_RE = re.compile(rb"sorry|admit|native_decide|sorryAx")
CHART_RE = re.compile(r"^Chart(\d{3})(.*)\.lean$")


def mod_name(path: Path) -> str:
    return ".".join(path.relative_to(SRC).with_suffix("").parts)


def olean_of(path: Path, base: Path) -> Path:
    return base / path.relative_to(SRC).with_suffix(".olean")


def fresh(path: Path, base: Path) -> bool:
    out = olean_of(path, base)
    return out.exists() and out.stat().st_mtime > path.stat().st_mtime


def chart_suffix(path: Path) -> tuple[int, str] | None:
    m = CHART_RE.match(path.name)
    if not m:
        return None
    return int(m.group(1)), m.group(2)


def classify(chart000: bool = False) -> dict[str, list[Path]]:
    all_files = sorted(CP.glob("Chart*.lean"))
    if not chart000:
        all_files = [p for p in all_files if not p.name.startswith("Chart000")]

    phases: dict[str, list[Path]] = {
        "supports": [],
        "base": [],
        "ms": [],
        "pairs": [],
        "aggregators": [],
        "bridges": [],
        "other": [],
    }
    for path in all_files:
        parsed = chart_suffix(path)
        if parsed is None:
            phases["other"].append(path)
            continue
        _, suffix = parsed
        if suffix == "ConeSupport":
            phases["supports"].append(path)
        elif suffix == "ConeBase":
            phases["base"].append(path)
        elif re.fullmatch(r"ConeMS\d+", suffix):
            phases["ms"].append(path)
        elif re.fullmatch(r"ConePairs\d+", suffix):
            phases["pairs"].append(path)
        elif suffix == "Cone":
            phases["aggregators"].append(path)
        elif suffix == "Bridge":
            phases["bridges"].append(path)
        else:
            phases["other"].append(path)
    return phases


def token_scan(files: list[Path]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in files:
        data = path.read_bytes()
        for m in TOKEN_RE.finditer(data):
            hits.append({"file": str(path.relative_to(ROOT)), "offset": m.start()})
            if len(hits) >= 50:
                return hits
    return hits


def active_wave_pids() -> list[int]:
    try:
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-CimInstance Win32_Process | "
                    "Where-Object { $_.Name -eq 'python.exe' } | "
                    "ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }"
                ),
            ],
            text=True,
            capture_output=True,
            timeout=60,
        )
    except Exception:
        return [-1]
    pids: list[int] = []
    for line in proc.stdout.splitlines():
        if "\t" not in line:
            continue
        pid_s, cmd = line.split("\t", 1)
        if "claude_o14_wave_regate.py" in cmd:
            try:
                pids.append(int(pid_s.strip()))
            except ValueError:
                pass
    return pids


def run_lean(path: Path, base: Path) -> dict[str, object]:
    out = olean_of(path, base)
    out.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(base) + os.pathsep + env.get("LEAN_PATH", "")
    t0 = time.time()
    proc = subprocess.run(
        ["lake", "env", "lean", f"--root={SRC}", f"--o={out}", str(path)],
        cwd=FORMAL,
        env=env,
        text=True,
        capture_output=True,
    )
    tail = (proc.stdout[-800:] + proc.stderr[-1600:]).strip()
    ok = proc.returncode == 0 and "error:" not in proc.stderr.lower()
    return {
        "module": mod_name(path),
        "ok": ok,
        "rc": proc.returncode,
        "sec": round(time.time() - t0, 1),
        "err": "" if ok else tail,
    }


def run_phase(
    name: str,
    files: list[Path],
    workers: int,
    base: Path,
    execute: bool,
    check_fresh: bool,
) -> dict[str, object]:
    fresh_count = sum(1 for p in files if fresh(p, base)) if check_fresh else None
    result: dict[str, object] = {
        "files": len(files),
        "fresh": fresh_count,
        "ok": 0,
        "skip": 0,
        "fail": [],
    }
    todo = [p for p in files if (not check_fresh or not fresh(p, base))]
    result["skip"] = len(files) - len(todo) if check_fresh else 0
    if not execute:
        result["todo"] = len(todo)
        return result

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_lean, p, base): p for p in todo}
        for fut in as_completed(futures):
            row = fut.result()
            if row["ok"]:
                result["ok"] = int(result["ok"]) + 1
            else:
                result["fail"].append(row)  # type: ignore[union-attr]
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="actually run Lean")
    ap.add_argument("--include-chart000", action="store_true")
    ap.add_argument("--base", type=Path, default=BASE)
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    ap.add_argument("--workers-shards", type=int, default=48)
    ap.add_argument("--workers-light", type=int, default=16)
    ap.add_argument("--no-fresh-check", action="store_true",
                    help="skip olean freshness checks; useful for instant dry-run classification")
    ap.add_argument("--allow-concurrent-wave", action="store_true",
                    help="allow --execute even if claude_o14_wave_regate.py is active")
    args = ap.parse_args()

    if args.workers_shards > 64 or args.workers_light > 64:
        raise SystemExit("worker counts must stay <= 64")
    active_waves = active_wave_pids()
    if args.execute and active_waves and not args.allow_concurrent_wave:
        raise SystemExit(
            "refusing --execute while claude_o14_wave_regate.py is active; "
            f"pids={active_waves}"
        )

    phases = classify(chart000=args.include_chart000)
    ordered = [
        ("supports", phases["supports"], args.workers_light),
        ("base", phases["base"], args.workers_light),
        ("ms", phases["ms"], args.workers_shards),
        ("pairs", phases["pairs"], args.workers_shards),
        ("aggregators", phases["aggregators"], args.workers_light),
        ("bridges", phases["bridges"], args.workers_light),
    ]
    all_phase_files = [p for _, files, _ in ordered for p in files] + phases["other"]
    token_hits = token_scan(all_phase_files) if args.execute else []

    summary: dict[str, object] = {
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "execute": args.execute,
        "base": str(args.base),
        "active_claude_wave_pids": active_waves,
        "token_scan": "enabled" if args.execute else "skipped-dry-run",
        "token_hits": token_hits,
        "other": [str(p.relative_to(ROOT)) for p in phases["other"]],
        "phases": {},
    }
    if token_hits:
        args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return 1

    for name, files, workers in ordered:
        phase = run_phase(name, files, workers, args.base, args.execute,
                          not args.no_fresh_check)
        summary["phases"][name] = phase  # type: ignore[index]
        args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        if phase["fail"]:  # type: ignore[index]
            summary["all_ok"] = False
            summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            print(json.dumps(summary, indent=2))
            return 1

    registries = [
        SRC / "Erdos23Delta0/O14/Generated/PayloadRegistry.lean",
        SRC / "Erdos23Delta0/O14/Generated/BridgeRegistry.lean",
        SRC / "Erdos23Delta0/O14/Generated/ListedConcreteCover.lean",
    ]
    summary["phases"]["registries"] = run_phase(
        "registries", registries, args.workers_light, args.base, args.execute,
        not args.no_fresh_check
    )  # type: ignore[index]
    reg_fail = summary["phases"]["registries"]["fail"]  # type: ignore[index]
    summary["all_ok"] = (not bool(reg_fail)) if args.execute else None
    summary["dry_run_ok"] = (not args.execute) and not bool(reg_fail)
    summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not args.execute:
        return 0 if summary["dry_run_ok"] else 1
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
