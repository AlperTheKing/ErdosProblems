"""Resumable per-n driver for the exact active-component Hall falsifier.

Each graph record is independent. Completed records are appended as JSONL, so
an interrupted run resumes without repeating finished graphs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _codex_internal_offsupport_gate as gate


def graph_records(n: int, m: int) -> list[str]:
    edge_count = m - 1
    if edge_count > (n * n) // 4:
        return []
    run = subprocess.run(
        [gate.GENG, "-q", "-c", "-b", str(n), f"{edge_count}:{edge_count}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in run.stdout.splitlines() if line.strip()]


def load_done(path: Path) -> set[str]:
    done: set[str] = set()
    if not path.exists():
        return done
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") in {"ok", "witness", "node_cap"}:
            done.add(row["g6"])
    return done


def run_one(task):
    g6, mode, max_length = task
    try:
        witness = gate.find_atoms_with_chord((g6, mode, max_length))
        return {
            "g6": g6,
            "status": "witness" if witness is not None else "ok",
            "witness": witness,
        }
    except RuntimeError as exc:
        return {"g6": g6, "status": "node_cap", "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, default=15)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--workers", type=int, default=40)
    parser.add_argument("--mode", default="flowdichotomy")
    parser.add_argument("--component-max-length", type=int, default=14)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=100)
    args = parser.parse_args()

    records = graph_records(args.n, args.m)
    done = load_done(args.out)
    pending = [g6 for g6 in records if g6 not in done]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    start = time.time()
    counts = {"ok": 0, "witness": 0, "node_cap": 0}

    with args.out.open("a", encoding="utf-8", buffering=1) as stream:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(
                    run_one,
                    (g6, args.mode, args.component_max_length),
                ): g6
                for g6 in pending
            }
            for index, future in enumerate(as_completed(futures), 1):
                row = future.result()
                counts[row["status"]] += 1
                stream.write(json.dumps(row, separators=(",", ":")) + "\n")
                if index % args.progress_every == 0 or row["status"] != "ok":
                    elapsed = time.time() - start
                    print(json.dumps({
                        "m": args.m,
                        "n": args.n,
                        "done_now": index,
                        "pending_start": len(pending),
                        "total": len(records),
                        "elapsed_sec": round(elapsed, 1),
                        "counts": counts,
                    }, separators=(",", ":")), flush=True)

    summary = {
        "m": args.m,
        "n": args.n,
        "records": len(records),
        "already_done": len(done),
        "processed_now": len(pending),
        "counts": counts,
        "elapsed_sec": round(time.time() - start, 1),
    }
    print("RESUMABLE_ACTIVE_HALL_GATE", json.dumps(summary, separators=(",", ":")))
    return 1 if counts["witness"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
