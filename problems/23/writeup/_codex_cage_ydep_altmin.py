"""Alternating ratio / linear-OT descent for y-dependent CAGE.

For fixed y and route alpha:

    Phi(alpha,y) = sum_g 2 sqrt((A_g.y)(B_g.y))
                 = min_{r_g>0} sum_g r_g (A_g.y) + r_g^{-1} (B_g.y).

Given alpha, set r_g=sqrt((B_g.y)/(A_g.y)).  With r fixed, minimizing over
alpha is a linear interval-transport problem for each bad edge.  This
majorization step cannot increase Phi.

This diagnostic tests whether the simple alternating descent gives stronger
y-dependent certificates on hard directions.  It is floating structure mining,
not an exact checker.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import linprog

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage
from _codex_cage_extreme_sample import f_subproblem
from _codex_cage_kkt_route_probe import linear_costs
from _codex_cage_ydep import maximize_gap, ydep_gap
from _h import dec, loads


def phi(inst, alpha, y):
    A, B = aggregate(inst, alpha)
    return ydep_gap(A, B, np.zeros_like(inst.cap), y)


def linear_ot_step(inst, info, alpha, y):
    out = np.array(alpha, dtype=float)
    total_lin_gap = 0.0
    for f_idx, _f in enumerate(info["M"]):
        idx, _pairs, _gates, Aeq, beq = f_subproblem(inst, f_idx)
        c, _r = linear_costs(inst, idx, _gates, out[idx], y)
        res = linprog(c, A_eq=Aeq, b_eq=beq, bounds=[(0.0, None)] * len(idx), method="highs")
        if not res.success:
            raise RuntimeError(res.message)
        total_lin_gap += float(c @ out[idx] - res.fun)
        out[idx] = res.x
    return out, total_lin_gap


def run_alt(inst, info, alpha, y, iters):
    cur = np.array(alpha, dtype=float)
    rows = []
    for it in range(iters + 1):
        val = phi(inst, cur, y)
        gap = val - float(inst.cap @ y)
        if it == iters:
            rows.append((it, gap, val, 0.0))
            break
        nxt, lin_gap = linear_ot_step(inst, info, cur, y)
        rows.append((it, gap, val, lin_gap))
        cur = nxt
    return cur, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--y-restarts", type=int, default=64)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    inst = build_instance(info, f"{args.g6}[{args.blow}]")
    fixed = solve_cage(inst, rounds=args.rounds, restarts=args.restarts)["alpha"]
    A0, B0 = aggregate(inst, inst.alpha0)
    gap0, y, _ok, _msg = maximize_gap(A0, B0, inst.cap, restarts=args.y_restarts)

    print(f"{inst.label}: alpha0_hard_gap={gap0:+.9f} cap.y={float(inst.cap @ y):.9f}")
    _final, rows = run_alt(inst, info, fixed, y, args.iters)
    for it, gap, val, lin_gap in rows:
        print(f"  it={it:02d} phi={val:.9f} gap={gap:+.9f} linear_gap={lin_gap:.9g}")


if __name__ == "__main__":
    main()
