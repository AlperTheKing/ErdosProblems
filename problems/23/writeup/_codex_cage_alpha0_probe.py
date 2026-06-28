"""Probe whether the uniform CAGE routing alpha0 already suffices.

If alpha0 were universally feasible after optimizing only gate ratios, the
proof target would simplify substantially.  This script compares that
ratio-only certificate with the full adaptive-alpha CAGE solve.
"""

from __future__ import annotations

import argparse
import subprocess

from _codex_cage import GENG, blowup_edges, build_instance, solve_cage, solve_x
from _h import dec, loads


def run_case(label, info, rounds, restarts):
    inst = build_instance(info, label)
    if inst is None:
        return None
    ratio0, _x0, ok0, msg0 = solve_x(inst, inst.alpha0)
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    return {
        "label": label,
        "n": inst.n,
        "vars": len(inst.vars),
        "gates": len(inst.gates),
        "alpha0_ratio": ratio0,
        "alpha0_gap": ratio0 - 1.0,
        "alpha0_ok": ok0,
        "alpha0_msg": msg0,
        "full_ratio": row["ratio"],
        "full_gap": row["gap"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--named", action="store_true")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--nmin", type=int, default=8)
    ap.add_argument("--nmax", type=int, default=8)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--restarts", type=int, default=4)
    args = ap.parse_args()

    rows = []
    if args.named:
        for g6, blow in [
            ("I?BD@g]Qo", 1),
            ("I?ABCc]}?", 1),
            ("J???E?pNu\\?", 2),
            ("J?AEB?oE?W?", 2),
            ("H?bB@_W", 2),
            ("I?rFf_{N?", 2),
        ]:
            n, edges = dec(g6) if blow == 1 else blowup_edges(g6, blow)
            info = loads(n, edges)
            if info:
                rows.append(run_case(f"{g6}[{blow}]", info, args.rounds, args.restarts))

    if args.census:
        for n in range(args.nmin, args.nmax + 1):
            g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True, check=True).stdout.split()
            used = 0
            for g6 in g6s:
                info = loads(*dec(g6))
                if info is None:
                    continue
                used += 1
                if args.limit and used > args.limit:
                    break
                rows.append(run_case(f"{g6}[1]", info, args.rounds, args.restarts))

    bad0 = 0
    for row in rows:
        if not row:
            continue
        if row["alpha0_ratio"] > 1.000001:
            bad0 += 1
        print(
            f"{row['label']:18} N={row['n']:3d} gates={row['gates']:4d} vars={row['vars']:5d} "
            f"alpha0_ratio={row['alpha0_ratio']:.9f} alpha0_gap={row['alpha0_gap']:+.3e} "
            f"full_ratio={row['full_ratio']:.9f} full_gap={row['full_gap']:+.3e}",
            flush=True,
        )
    print(f"SUMMARY rows={len(rows)} alpha0_bad={bad0}", flush=True)


if __name__ == "__main__":
    main()
