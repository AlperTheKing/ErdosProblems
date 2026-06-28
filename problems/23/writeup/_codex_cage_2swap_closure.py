"""Random stress for greedy 2x2-closed y-dependent CAGE routes.

For each sampled y, start from a fixed adaptive CAGE alpha, greedily apply
balance-preserving 2x2 swaps independently for each bad edge, and evaluate the
y-dependent conic gap.

This tests whether "2x2 local closure" is a plausible certificate class.  It is
floating structure mining, not an exact checker.
"""

from __future__ import annotations

import argparse

import numpy as np

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage
from _codex_cage_extreme_sample import f_subproblem
from _codex_cage_swap_probe import greedy_descent
from _codex_cage_ydep import maximize_gap, ydep_gap
from _h import dec, loads


def close_alpha(inst, info, alpha, y):
    out = np.array(alpha, dtype=float)
    total_gain = 0.0
    total_steps = 0
    for f_idx, _f in enumerate(info["M"]):
        idx, _pairs, gates, _Aeq, _beq = f_subproblem(inst, f_idx)
        x0 = out[idx]
        x1, _val, gain, steps = greedy_descent(inst, idx, gates, x0, y)
        out[idx] = x1
        total_gain += gain
        total_steps += steps
    return out, total_gain, total_steps


def normalize(cap, z):
    y = np.maximum(z, 0.0)
    den = float(cap @ y)
    if den <= 0:
        return np.ones_like(cap) / float(np.sum(cap))
    return y / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--samples", type=int, default=200)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--y-restarts", type=int, default=64)
    ap.add_argument("--seed", type=int, default=20260628)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    inst = build_instance(info, f"{args.g6}[{args.blow}]")
    fixed = solve_cage(inst, rounds=args.rounds, restarts=args.restarts)["alpha"]
    A0, B0 = aggregate(inst, inst.alpha0)
    gap0, hard_y, _ok, _msg = maximize_gap(A0, B0, inst.cap, restarts=args.y_restarts)

    rng = np.random.default_rng(args.seed)
    starts = [hard_y]
    starts += [np.eye(inst.n)[v] / inst.cap[v] for v in range(inst.n)]
    starts += [normalize(inst.cap, rng.exponential(size=inst.n)) for _ in range(args.samples)]

    best = None
    for y in starts:
        closed, gain, steps = close_alpha(inst, info, fixed, y)
        A, B = aggregate(inst, closed)
        gap = ydep_gap(A, B, inst.cap, y)
        if best is None or gap > best[0]:
            best = (gap, gain, steps, y)

    fixed_A, fixed_B = aggregate(inst, fixed)
    fixed_hard_gap = ydep_gap(fixed_A, fixed_B, inst.cap, hard_y)
    closed_hard, hard_gain, hard_steps = close_alpha(inst, info, fixed, hard_y)
    hard_gap = ydep_gap(*aggregate(inst, closed_hard), inst.cap, hard_y)

    print(f"{inst.label}: alpha0_hard_gap={gap0:+.9f}")
    print(f"  fixed_at_alpha0_hard_y={fixed_hard_gap:+.9f}")
    print(f"  closed_at_alpha0_hard_y={hard_gap:+.9f} gain={hard_gain:.9g} steps={hard_steps}")
    gap, gain, steps, y = best
    nnz = int(np.sum(y > 1e-8))
    print(f"  random_worst_closed_gap={gap:+.9f} gain={gain:.9g} steps={steps} y_nnz={nnz}")
    top = sorted(range(inst.n), key=lambda v: -y[v])[:10]
    print("  y_top=" + " ".join(f"{v}:{y[v]:.4g}" for v in top if y[v] > 1e-8))


if __name__ == "__main__":
    main()
