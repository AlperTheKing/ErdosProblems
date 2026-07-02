"""Parallel census runner for _codex_c5_masksize_split_gate.py."""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter
from fractions import Fraction

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5_masksize_split_gate import run_gmins, mask_s, fmt
    from _h import GENG, dec


def empty_acc(positive_eta: bool):
    return {
        "positive_eta": positive_eta,
        "cuts": 0,
        "rows": 0,
        "checks": 0,
        "fails": 0,
        "first_fail": None,
        "orbit_counts": Counter(),
        "min_by_orbit": {},
        "min_by_size": {},
    }


def worker(args):
    g6, max_cuts, positive_eta = args
    n, edges = dec(g6)
    acc = empty_acc(positive_eta)
    run_gmins(f"cen:{g6}", n, edges, max_cuts, acc)
    return acc


def better(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return b if b["margin"] < a["margin"] else a


def unwrap(slot):
    if slot is None:
        return None
    if isinstance(slot, list):
        return slot[0]
    return slot


def print_rec(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    for k in ("margin", "orbit_s", "mask_s", "size", "coeff", "name", "n", "m", "eta", "tau", "lhs", "budget", "active", "s", "f", "Q", "side"):
        print(f"  {k}: {fmt(rec[k])}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--positive-eta", action="store_true")
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    total = empty_acc(args.positive_eta)
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        tasks = ((g6, args.max_cuts, args.positive_eta) for g6 in graphs)
        for acc in pool.imap_unordered(worker, tasks, chunksize=args.chunksize):
            done += 1
            for k in ("cuts", "rows", "checks", "fails"):
                total[k] += acc[k]
            for orb, count in acc["orbit_counts"].items():
                total["orbit_counts"][orb] = total["orbit_counts"].get(orb, 0) + count
            for size, slot in acc["min_by_size"].items():
                rec = unwrap(slot)
                current = unwrap(total["min_by_size"].get(size))
                total["min_by_size"][size] = [better(current, rec)]
            for orb, slot in acc["min_by_orbit"].items():
                rec = unwrap(slot)
                current = unwrap(total["min_by_orbit"].get(orb))
                total["min_by_orbit"][orb] = [better(current, rec)]
            if total["first_fail"] is None and acc["first_fail"] is not None:
                total["first_fail"] = acc["first_fail"]
                if args.stop_first:
                    pool.terminate()
                    break
            if done % 500 == 0:
                print(f"progress graphs={done}/{len(graphs)} cuts={total['cuts']} checks={total['checks']}", flush=True)

    print("=== parallel C5 fixed-mask-size split gate ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("positive_eta:", args.positive_eta)
    for k in ("cuts", "rows", "checks", "fails"):
        print(f"{k}:", total[k])
    print("orbits:", {mask_s(k): v for k, v in sorted(total["orbit_counts"].items())})
    for size in sorted(total["min_by_size"]):
        print_rec(f"min_size_{size}", unwrap(total["min_by_size"][size]))
    for orb in sorted(total["min_by_orbit"]):
        print_rec(f"min_orbit_{mask_s(orb)}", unwrap(total["min_by_orbit"][orb]))
    print_rec("first_fail", total["first_fail"])
    print("VERDICT:", "PASS" if total["fails"] == 0 else "FAIL")
    return 0 if total["fails"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
