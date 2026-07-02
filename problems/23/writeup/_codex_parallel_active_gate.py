"""Parallel shard runner for _codex_c5lift_active_size_quotient_fast.py."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path


def parse_fraction(s: str | None) -> Fraction | None:
    if s is None:
        return None
    return Fraction(s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], required=True)
    ap.add_argument("--max-weight", type=int, default=3)
    ap.add_argument("--coeff", required=True)
    ap.add_argument("--active-min", type=int, default=0)
    ap.add_argument("--active-max", type=int, required=True)
    ap.add_argument("--shards", type=int, default=64)
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--weight-orbits", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    worker_script = here / "_codex_c5lift_active_size_quotient_fast.py"
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = here / "_tmp_parallel" / f"{run_id}_{args.graph}_a{args.active_min}_{args.active_max}_c{args.coeff.replace('/', '-')}"
    out_dir.mkdir(parents=True, exist_ok=False)

    pending = list(range(args.shards))
    running: list[tuple[int, subprocess.Popen[str], Path, Path]] = []
    completed = []

    def launch(shard: int) -> None:
        json_path = out_dir / f"shard_{shard:03d}.json"
        log_path = out_dir / f"shard_{shard:03d}.log"
        cmd = [
            sys.executable,
            str(worker_script),
            "--graph",
            args.graph,
            "--max-weight",
            str(args.max_weight),
            "--coeff",
            args.coeff,
            "--active-min",
            str(args.active_min),
            "--active-max",
            str(args.active_max),
            "--shard-index",
            str(shard),
            "--shard-count",
            str(args.shards),
            "--json-out",
            str(json_path),
        ]
        if args.weight_orbits:
            cmd.append("--weight-orbits")
        fh = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=here.parents[2], stdout=fh, stderr=subprocess.STDOUT, text=True)
        proc._codex_log_fh = fh  # type: ignore[attr-defined]
        running.append((shard, proc, json_path, log_path))

    while pending or running:
        while pending and len(running) < args.workers:
            launch(pending.pop(0))
        still_running = []
        for item in running:
            shard, proc, json_path, log_path = item
            rc = proc.poll()
            if rc is None:
                still_running.append(item)
                continue
            proc._codex_log_fh.close()  # type: ignore[attr-defined]
            if rc != 0:
                print(f"SHARD_FAIL shard={shard} rc={rc} log={log_path}")
                return rc
            completed.append((shard, json_path, log_path))
        running = still_running
        if running:
            time.sleep(0.2)

    total = {
        "weights": 0,
        "orbit_skips": 0,
        "qmax_cuts": 0,
        "rows_checked": 0,
        "fails": 0,
    }
    active_counts: dict[str, int] = {}
    active_mask_counts: dict[str, int] = {}
    worst_by_active_mask = {}
    max_ratio_by_active_mask = {}
    worst = None
    first_fail = None

    for shard, json_path, _log_path in sorted(completed):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        for key in total:
            total[key] += int(data[key])
        for key, value in data["active_counts"].items():
            active_counts[key] = active_counts.get(key, 0) + int(value)
        for key, value in data.get("active_mask_counts", {}).items():
            active_mask_counts[key] = active_mask_counts.get(key, 0) + int(value)
        for key, rec in data.get("worst_by_active_mask", {}).items():
            margin = parse_fraction(rec["margin"])
            if key not in worst_by_active_mask or margin < parse_fraction(worst_by_active_mask[key]["margin"]):
                worst_by_active_mask[key] = rec
        for key, rec in data.get("max_ratio_by_active_mask", {}).items():
            ratio = parse_fraction(rec["debt_over_eta"])
            if key not in max_ratio_by_active_mask or ratio > parse_fraction(max_ratio_by_active_mask[key]["debt_over_eta"]):
                max_ratio_by_active_mask[key] = rec
        rec = data["worst"]
        if rec is not None:
            margin = parse_fraction(rec["margin"])
            if worst is None or margin < parse_fraction(worst["margin"]):
                worst = rec
        if first_fail is None and data["first_fail"] is not None:
            first_fail = data["first_fail"]

    print("=== parallel active-size gate ===")
    print("graph:", args.graph)
    print("coeff:", args.coeff)
    print("active_min:", args.active_min)
    print("active_max:", args.active_max)
    print("max_weight:", args.max_weight)
    print("shards:", args.shards)
    print("workers:", args.workers)
    print("weight_orbits:", args.weight_orbits)
    print("out_dir:", out_dir)
    for key, value in total.items():
        print(f"{key}:", value)
    print("active_counts:", dict(sorted(active_counts.items(), key=lambda kv: int(kv[0]))))
    print("active_mask_counts:", dict(sorted(active_mask_counts.items())))
    print("worst_margin:", None if worst is None else worst["margin"])
    print("worst:", json.dumps(worst, sort_keys=True))
    print("worst_by_active_mask:")
    for key in sorted(worst_by_active_mask):
        print(key, json.dumps(worst_by_active_mask[key], sort_keys=True))
    print("max_ratio_by_active_mask:")
    for key in sorted(max_ratio_by_active_mask):
        print(key, json.dumps(max_ratio_by_active_mask[key], sort_keys=True))
    print("first_fail:", json.dumps(first_fail, sort_keys=True))
    print("VERDICT:", "PASS" if total["fails"] == 0 else "FAIL")
    return 0 if total["fails"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
