#!/usr/bin/env python3
"""Build generated O14 sharded chart payload Lean files.

The accepted Chart000 gate builds directly into tmp/claude_lean_o_base_v1 with
LEAN_PATH pointing at that cache.  Lean on this tree does not reliably fall
through from a separate first output root, so this companion keeps the same
single-cache layout and uses phase-level parallelism:

  support -> base -> MS/Pairs shards -> aggregators -> optional registry

No proof content is generated here; this is only an honest Lean build driver.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
FORMAL = ROOT / "formal-conjectures"
SRC = ROOT / "problems/23/lean"
PAYLOAD_DIR = SRC / "Erdos23Delta0/O14/Generated/ChartPayloads"
DEFAULT_CACHE = ROOT / "tmp/claude_lean_o_base_v1"
TOOLCHAIN = "leanprover/lean4:v4.27.0"


def chart_prefix(slot: int) -> str:
    return f"Chart{slot:03d}Cone"


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(SRC).with_suffix("").parts)


def olean_path(cache: Path, path: Path) -> Path:
    return cache / (module_name(path).replace(".", "/") + ".olean")


def source_kind(path: Path) -> str:
    name = path.name
    if name.endswith("Support.lean"):
        return "support"
    if name.endswith("Base.lean"):
        return "base"
    if "MS" in name or "Pairs" in name:
        return "shard"
    if name == "PayloadRegistry.lean":
        return "registry"
    return "aggregator"


def needs_build(cache: Path, path: Path, force: bool) -> bool:
    if force:
        return True
    out = olean_path(cache, path)
    if not out.exists():
        return True
    return out.stat().st_mtime < path.stat().st_mtime


def run_lean(cache: Path, path: Path, timeout: int | None = None) -> dict:
    mod = module_name(path)
    out = olean_path(cache, path)
    out.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(cache) + os.pathsep + env.get("LEAN_PATH", "")
    cmd = [
        "elan",
        "run",
        TOOLCHAIN,
        "lake",
        "env",
        "lean",
        f"--root={SRC}",
        f"--o={out}",
        str(path),
    ]
    t0 = time.time()
    try:
        r = subprocess.run(
            cmd,
            cwd=FORMAL,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        rc = r.returncode
        stdout = r.stdout
        stderr = r.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        rc = -999
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        timed_out = True
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", "replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", "replace")
    ok = (rc == 0) and ("error:" not in stderr.lower()) and not timed_out
    return {
        "module": mod,
        "path": str(path.relative_to(ROOT)),
        "olean": str(out.relative_to(ROOT)),
        "kind": source_kind(path),
        "rc": rc,
        "ok": ok,
        "timed_out": timed_out,
        "sec": round(time.time() - t0, 3),
        "err": "" if ok else (stdout[-800:] + stderr[-2400:]),
    }


def parse_slots(raw: str) -> list[int]:
    out: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return sorted(out)


def collect_phase(slots: Iterable[int], phase: str, include_registry: bool) -> list[Path]:
    files: list[Path] = []
    for slot in slots:
        prefix = chart_prefix(slot)
        if phase == "support":
            files.append(PAYLOAD_DIR / f"{prefix}Support.lean")
        elif phase == "base":
            files.append(PAYLOAD_DIR / f"{prefix}Base.lean")
        elif phase == "shard":
            files.extend(sorted(PAYLOAD_DIR.glob(f"{prefix}MS*.lean")))
            files.extend(sorted(PAYLOAD_DIR.glob(f"{prefix}Pairs*.lean")))
        elif phase == "aggregator":
            files.append(PAYLOAD_DIR / f"{prefix}.lean")
        else:
            raise ValueError(f"unknown phase {phase}")
    if phase == "aggregator" and include_registry:
        files.append(SRC / "Erdos23Delta0/O14/Generated/PayloadRegistry.lean")
    missing = [str(f.relative_to(ROOT)) for f in files if not f.exists()]
    if missing:
        raise FileNotFoundError("missing generated Lean files: " + ", ".join(missing[:20]))
    return files


def scan_forbidden(files: Iterable[Path]) -> list[dict]:
    pat = re.compile(rb"sorry|admit|native_decide|sorryAx")
    hits: list[dict] = []
    for path in files:
        data = path.read_bytes()
        for m in pat.finditer(data):
            line_no = data.count(b"\n", 0, m.start()) + 1
            line_start = data.rfind(b"\n", 0, m.start()) + 1
            line_end = data.find(b"\n", m.start())
            if line_end < 0:
                line_end = len(data)
            line = data[line_start:line_end][:180].decode("utf-8", "replace")
            hits.append({"file": str(path.relative_to(ROOT)), "line": line_no, "text": line})
    return hits


def run_phase(
    cache: Path,
    phase: str,
    files: list[Path],
    workers: int,
    force: bool,
    timeout: int | None,
    summary_jsonl: Path,
) -> dict:
    todo = [p for p in files if needs_build(cache, p, force)]
    skipped = len(files) - len(todo)
    phase_summary = {
        "phase": phase,
        "total": len(files),
        "todo": len(todo),
        "skipped": skipped,
        "ok": 0,
        "fail": 0,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": workers,
        "failures": [],
    }
    print(
        f"[{phase}] total={len(files)} todo={len(todo)} skipped={skipped} workers={workers}",
        flush=True,
    )
    if not todo:
        phase_summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return phase_summary
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = {ex.submit(run_lean, cache, path, timeout): path for path in todo}
        for fut in as_completed(futs):
            res = fut.result()
            done += 1
            if res["ok"]:
                phase_summary["ok"] += 1
            else:
                phase_summary["fail"] += 1
                phase_summary["failures"].append(res)
            with summary_jsonl.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"event": "module", **res}, sort_keys=True) + "\n")
            if done % 50 == 0 or not res["ok"] or done == len(todo):
                print(
                    f"[{phase}] done={done}/{len(todo)} ok={phase_summary['ok']} "
                    f"fail={phase_summary['fail']} elapsed={round(time.time() - t0, 1)}s",
                    flush=True,
                )
            if not res["ok"] and phase in {"support", "base", "aggregator", "registry"}:
                # Dependency phases should stop quickly; shard phase can collect failures.
                pass
    phase_summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    phase_summary["seconds"] = round(time.time() - t0, 3)
    with summary_jsonl.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "phase", **phase_summary}, sort_keys=True) + "\n")
    return phase_summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", default="1-107")
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    ap.add_argument("--summary-json", type=Path, default=ROOT / "tmp/codex_o14_payload_build_summary.json")
    ap.add_argument("--summary-jsonl", type=Path, default=ROOT / "tmp/codex_o14_payload_build_events.jsonl")
    ap.add_argument("--support-workers", type=int, default=16)
    ap.add_argument("--base-workers", type=int, default=8)
    ap.add_argument("--shard-workers", type=int, default=48)
    ap.add_argument("--aggregator-workers", type=int, default=16)
    ap.add_argument("--timeout", type=int, default=0, help="per-file timeout seconds; 0 disables")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--skip-token-scan", action="store_true")
    ap.add_argument("--include-registry", action="store_true")
    args = ap.parse_args()

    worker_max = max(args.support_workers, args.base_workers, args.shard_workers, args.aggregator_workers)
    if worker_max > 64:
        raise SystemExit(f"worker cap exceeded: {worker_max} > 64")

    slots = parse_slots(args.slots)
    timeout = args.timeout or None
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_jsonl.parent.mkdir(parents=True, exist_ok=True)
    if args.force and args.summary_jsonl.exists():
        args.summary_jsonl.unlink()

    phases = {
        "support": collect_phase(slots, "support", False),
        "base": collect_phase(slots, "base", False),
        "shard": collect_phase(slots, "shard", False),
        "aggregator": collect_phase(slots, "aggregator", args.include_registry),
    }
    all_files = [p for xs in phases.values() for p in xs]
    summary = {
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "slots": slots,
        "cache": str(args.cache.relative_to(ROOT) if args.cache.is_relative_to(ROOT) else args.cache),
        "worker_caps": {
            "support": args.support_workers,
            "base": args.base_workers,
            "shard": args.shard_workers,
            "aggregator": args.aggregator_workers,
        },
        "source_counts": {k: len(v) for k, v in phases.items()},
        "token_scan": None,
        "phases": [],
    }

    if not args.skip_token_scan:
        hits = scan_forbidden(all_files)
        summary["token_scan"] = {"files": len(all_files), "hits": hits}
        print(f"[scan] files={len(all_files)} hits={len(hits)}", flush=True)
        if hits:
            args.summary_json.write_text(json.dumps(summary, indent=1), encoding="utf-8")
            return 2

    for phase, workers in [
        ("support", args.support_workers),
        ("base", args.base_workers),
        ("shard", args.shard_workers),
        ("aggregator", args.aggregator_workers),
    ]:
        ps = run_phase(
            args.cache,
            phase,
            phases[phase],
            workers,
            args.force,
            timeout,
            args.summary_jsonl,
        )
        summary["phases"].append(ps)
        args.summary_json.write_text(json.dumps(summary, indent=1), encoding="utf-8")
        if ps["fail"]:
            print(f"[stop] phase {phase} failed; see {args.summary_json}", flush=True)
            summary["all_ok"] = False
            summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            args.summary_json.write_text(json.dumps(summary, indent=1), encoding="utf-8")
            return 1

    summary["all_ok"] = True
    summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    args.summary_json.write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"[done] all_ok=true summary={args.summary_json}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
