"""Parallel graph-shard runner for _codex_c5_masksize_split_gate.py."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path


def frac(s):
    return Fraction(s) if s is not None else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=11)
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--shards", type=int, default=60)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--positive-eta", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    worker_script = here / "_codex_c5_masksize_split_gate.py"
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = here / "_tmp_masksize_parallel" / f"{run_id}_n{args.min_n}_{args.max_n}"
    out_dir.mkdir(parents=True, exist_ok=False)

    pending = list(range(args.shards))
    running = []
    completed = []

    def launch(shard: int) -> None:
        json_path = out_dir / f"shard_{shard:03d}.json"
        log_path = out_dir / f"shard_{shard:03d}.log"
        cmd = [
            sys.executable,
            str(worker_script),
            "--min-n",
            str(args.min_n),
            "--max-n",
            str(args.max_n),
            "--graph-shard-index",
            str(shard),
            "--graph-shard-count",
            str(args.shards),
            "--json-out",
            str(json_path),
        ]
        if args.positive_eta:
            cmd.append("--positive-eta")
        if args.skip_named:
            cmd.append("--skip-named")
        fh = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=here.parents[2], stdout=fh, stderr=subprocess.STDOUT, text=True)
        proc._codex_log_fh = fh  # type: ignore[attr-defined]
        running.append((shard, proc, json_path, log_path))

    while pending or running:
        while pending and len(running) < args.workers:
            launch(pending.pop(0))
        still = []
        for item in running:
            shard, proc, json_path, log_path = item
            rc = proc.poll()
            if rc is None:
                still.append(item)
                continue
            proc._codex_log_fh.close()  # type: ignore[attr-defined]
            if rc != 0:
                print(f"SHARD_FAIL shard={shard} rc={rc} log={log_path}")
                return rc
            completed.append((shard, json_path, log_path))
        running = still
        if running:
            time.sleep(0.2)

    total = {"cuts": 0, "rows": 0, "checks": 0, "fails": 0}
    orbit_counts = {}
    first_fail = None
    min_by_size = {}
    min_by_orbit = {}

    for shard, json_path, _log_path in sorted(completed):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        for key in total:
            total[key] += int(data[key])
        for key, value in data["orbit_counts"].items():
            orbit_counts[key] = orbit_counts.get(key, 0) + int(value)
        if first_fail is None and data["first_fail"] is not None:
            first_fail = data["first_fail"]
        for key, rec in data["min_by_size"].items():
            if rec is None:
                continue
            if key not in min_by_size or frac(rec["margin"]) < frac(min_by_size[key]["margin"]):
                min_by_size[key] = rec
        for key, rec in data["min_by_orbit"].items():
            if rec is None:
                continue
            if key not in min_by_orbit or frac(rec["margin"]) < frac(min_by_orbit[key]["margin"]):
                min_by_orbit[key] = rec

    print("=== parallel C5 fixed-mask-size split gate ===")
    print("n_range:", f"{args.min_n}..{args.max_n}")
    print("shards:", args.shards)
    print("workers:", args.workers)
    print("positive_eta:", args.positive_eta)
    print("skip_named:", args.skip_named)
    print("out_dir:", out_dir)
    for key, value in total.items():
        print(f"{key}:", value)
    print("orbit_counts:", dict(sorted(orbit_counts.items())))
    print("min_by_size:")
    for key in sorted(min_by_size, key=int):
        print(key, json.dumps(min_by_size[key], sort_keys=True))
    print("min_by_orbit:")
    for key in sorted(min_by_orbit):
        print(key, json.dumps(min_by_orbit[key], sort_keys=True))
    print("first_fail:", json.dumps(first_fail, sort_keys=True))
    print("VERDICT:", "PASS" if total["fails"] == 0 else "FAIL")
    return 0 if total["fails"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
