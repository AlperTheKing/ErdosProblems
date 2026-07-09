#!/usr/bin/env python3
"""Batch-run O14 chunked-cone exports from the accepted v108 inventory."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXPORTER = ROOT / "problems/23/writeup/_codex_o14_chunked_cone_export.py"


def run_slot(slot: int, chunk_size: int, out_dir: Path) -> dict:
    out = out_dir / f"codex_o14_chart{slot:03d}_chunked_cone_export.json"
    cmd = [
        sys.executable,
        str(EXPORTER),
        "--slot",
        str(slot),
        "--chunk-size",
        str(chunk_size),
        "--out",
        str(out),
    ]
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return {
        "slot": slot,
        "ok": proc.returncode == 0,
        "rc": proc.returncode,
        "sec": round(time.time() - t0, 3),
        "out": str(out),
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", default="1-107")
    ap.add_argument("--chunk-size", type=int, default=64)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--out-dir", type=Path, default=Path("tmp/o14_exports_v108"))
    ap.add_argument("--summary", type=Path, default=Path("tmp/codex_o14_batch_export_summary.jsonl"))
    args = ap.parse_args()

    slots = parse_slots(args.slots)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    started = {
        "event": "started",
        "slots": slots,
        "workers": args.workers,
        "chunk_size": args.chunk_size,
        "out_dir": str(args.out_dir),
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with args.summary.open("a", encoding="utf-8") as f:
        f.write(json.dumps(started, sort_keys=True) + "\n")

    ok = 0
    fail = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(run_slot, slot, args.chunk_size, args.out_dir): slot
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
                    f"[{status}] slot={rec['slot']:03d} rc={rec['rc']} "
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
