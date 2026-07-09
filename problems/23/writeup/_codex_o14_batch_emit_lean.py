#!/usr/bin/env python3
"""Batch-emit sharded Lean payload modules for O14 chunked-cone exports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EMITTER = ROOT / "problems/23/writeup/_codex_o14_chunked_cone_to_lean_sharded.py"


def parse_slots(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(dict.fromkeys(out))


def run_slot(
    slot: int,
    export_dir: Path,
    out_dir: Path,
    base_term_chunk: int,
    source_chunk: int,
    pair_chunk: int,
) -> dict:
    export = export_dir / f"codex_o14_chart{slot:03d}_chunked_cone_export.json"
    cmd = [
        sys.executable,
        str(EMITTER),
        "--export",
        str(export),
        "--out-dir",
        str(out_dir),
        "--base-term-chunk",
        str(base_term_chunk),
        "--source-chunk",
        str(source_chunk),
        "--pair-chunk",
        str(pair_chunk),
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    payload = None
    if proc.returncode == 0:
        try:
            payload = json.loads(proc.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            payload = {"parse_error": proc.stdout[-1000:]}
    return {
        "slot": slot,
        "ok": proc.returncode == 0,
        "rc": proc.returncode,
        "sec": round(time.time() - t0, 3),
        "export": str(export),
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "payload": payload,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", default="1-107")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--export-dir", type=Path, default=Path("tmp/o14_exports_v108"))
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("problems/23/lean/Erdos23Delta0/O14/Generated/ChartPayloads"),
    )
    ap.add_argument("--summary", type=Path, default=Path("tmp/codex_o14_batch_emit_summary.jsonl"))
    ap.add_argument("--base-term-chunk", type=int, default=64)
    ap.add_argument("--source-chunk", type=int, default=32)
    # Keep pair shards small by default; heavy charts have very large
    # `checkEq` goals and benefit more from finer Lean files than from fewer
    # generated modules.
    ap.add_argument("--pair-chunk", type=int, default=4)
    args = ap.parse_args()
    if args.workers > 64:
        raise SystemExit(f"worker cap exceeded: {args.workers} > 64")

    slots = parse_slots(args.slots)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    started = {
        "event": "started",
        "slots": slots,
        "workers": args.workers,
        "export_dir": str(args.export_dir),
        "out_dir": str(args.out_dir),
        "base_term_chunk": args.base_term_chunk,
        "source_chunk": args.source_chunk,
        "pair_chunk": args.pair_chunk,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with args.summary.open("a", encoding="utf-8") as f:
        f.write(json.dumps(started, sort_keys=True) + "\n")

    ok = 0
    fail = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(
                run_slot,
                slot,
                args.export_dir,
                args.out_dir,
                args.base_term_chunk,
                args.source_chunk,
                args.pair_chunk,
            ): slot
            for slot in slots
        }
        with args.summary.open("a", encoding="utf-8") as f:
            for fut in as_completed(futs):
                rec = fut.result()
                if rec["ok"]:
                    ok += 1
                else:
                    fail += 1
                rec["event"] = "slot"
                rec["ok_total"] = ok
                rec["fail_total"] = fail
                f.write(json.dumps(rec, sort_keys=True) + "\n")
                f.flush()
                status = "OK" if rec["ok"] else "FAIL"
                print(
                    f"[{status}] emit slot={rec['slot']:03d} rc={rec['rc']} "
                    f"{rec['sec']}s ok={ok} fail={fail}",
                    flush=True,
                )

    finished = {
        "event": "finished",
        "ok": ok,
        "fail": fail,
        "total": len(slots),
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with args.summary.open("a", encoding="utf-8") as f:
        f.write(json.dumps(finished, sort_keys=True) + "\n")
    print(json.dumps(finished, sort_keys=True))


if __name__ == "__main__":
    main()
