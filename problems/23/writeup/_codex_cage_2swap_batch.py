"""Small-census falsifier for 2x2-closed y-dependent CAGE.

For each census graph with bad edges:
1. find the alpha0-hard y;
2. start from a floating fixed CAGE alpha;
3. apply greedy 2x2 closure;
4. report any positive y-dependent gap.

This is a floating stress screen, not an exact checker.
"""

from __future__ import annotations

import argparse
import subprocess
from multiprocessing import Pool

import numpy as np

from _codex_cage import aggregate, build_instance, solve_cage
from _codex_cage_2swap_closure import close_alpha
from _codex_cage_ydep import maximize_gap, ydep_gap
from _h import GENG, dec, loads


def one(args):
    g6, rounds, restarts, y_restarts = args
    try:
        n, edges = dec(g6)
        info = loads(n, edges)
        if info is None or not info["M"]:
            return None
        inst = build_instance(info, g6)
        fixed = solve_cage(inst, rounds=rounds, restarts=restarts)["alpha"]
        A0, B0 = aggregate(inst, inst.alpha0)
        gap0, y, _ok, _msg = maximize_gap(A0, B0, inst.cap, restarts=y_restarts)
        closed, gain, steps = close_alpha(inst, info, fixed, y)
        gap = ydep_gap(*aggregate(inst, closed), inst.cap, y)
        return (gap, g6, gap0, gain, steps, len(info["M"]))
    except Exception as exc:  # diagnostic script
        return ("ERR", g6, repr(exc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--restarts", type=int, default=4)
    ap.add_argument("--y-restarts", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    gs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit:
        gs = gs[: args.limit]
    jobs = [(g, args.rounds, args.restarts, args.y_restarts) for g in gs]
    worst = None
    errors = []
    count = 0
    positive = []
    with Pool(processes=args.workers) as pool:
        for row in pool.imap_unordered(one, jobs, chunksize=4):
            if row is None:
                continue
            if row[0] == "ERR":
                errors.append(row)
                continue
            gap, g6, gap0, gain, steps, m = row
            count += 1
            if worst is None or gap > worst[0]:
                worst = row
            if gap > 1e-7:
                positive.append(row)
    print(f"N={args.n} checked={count} errors={len(errors)} positives={len(positive)}")
    if worst:
        gap, g6, gap0, gain, steps, m = worst
        print(f"worst gap={gap:+.9f} g6={g6} alpha0_gap={gap0:+.9f} gain={gain:.9g} steps={steps} M={m}")
    for row in positive[:20]:
        gap, g6, gap0, gain, steps, m = row
        print(f"POS gap={gap:+.9f} g6={g6} alpha0_gap={gap0:+.9f} gain={gain:.9g} steps={steps} M={m}")
    for row in errors[:10]:
        print("ERR", row[1], row[2])


if __name__ == "__main__":
    main()
