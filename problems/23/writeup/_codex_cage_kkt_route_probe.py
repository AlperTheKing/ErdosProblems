"""KKT probe for y-dependent CAGE route minimizers.

For fixed y and a route alpha, the y-dependent gate cost satisfies

    2 sqrt((A_g.y)(B_g.y)) = min_{r_g>0} r_g (A_g.y) + r_g^{-1} (B_g.y).

At a smooth local minimum, with r_g=sqrt((B_g.y)/(A_g.y)), alpha should solve
the linear interval-transport problem with costs

    c_{(i,j),g} = r_g w_i + r_g^{-1} w_j.

This diagnostic starts from fixed CAGE alpha, applies greedy 2x2 closure, then
checks the linear OT optimality gap for the induced ratios.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import linprog

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage
from _codex_cage_extreme_sample import f_subproblem, pair_meta
from _codex_cage_swap_probe import greedy_descent
from _codex_cage_ydep import maximize_gap
from _h import dec, loads


def gate_xy(inst, idx, gates, x, y):
    X = {g: 0.0 for g in gates}
    Y = {g: 0.0 for g in gates}
    for val, k in zip(x, idx):
        if val <= 1e-12:
            continue
        av = inst.vars[k]
        X[av.gate] += val * sum(pfv * y[v] for v, pfv in av.left)
        Y[av.gate] += val * sum(pfv * y[v] for v, pfv in av.right)
    return X, Y


def linear_costs(inst, idx, gates, x, y):
    X, Y = gate_xy(inst, idx, gates, x, y)
    r = {}
    for g in gates:
        if X[g] <= 1e-14 and Y[g] <= 1e-14:
            r[g] = 1.0
        elif X[g] <= 1e-14:
            r[g] = 1e9
        elif Y[g] <= 1e-14:
            r[g] = 1e-9
        else:
            r[g] = float(np.sqrt(Y[g] / X[g]))
    c = []
    for k in idx:
        av = inst.vars[k]
        wi = sum(pfv * y[v] for v, pfv in av.left)
        wj = sum(pfv * y[v] for v, pfv in av.right)
        rg = r[av.gate]
        c.append(rg * wi + wj / rg)
    return np.array(c), r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
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
    meta = pair_meta(info)

    print(f"{inst.label}: alpha0_hard_gap={gap0:+.9f}")
    total_gap = 0.0
    for f_idx, f in enumerate(info["M"]):
        idx, _pairs, gates, Aeq, beq = f_subproblem(inst, f_idx)
        x0 = fixed[idx]
        x, _val, gain, steps = greedy_descent(inst, idx, gates, x0, y)
        c, _r = linear_costs(inst, idx, gates, x, y)
        res = linprog(c, A_eq=Aeq, b_eq=beq, bounds=[(0.0, None)] * len(idx), method="highs")
        if not res.success:
            print(f"f#{f_idx}{f}: linprog failed {res.message}")
            continue
        current = float(c @ x)
        opt = float(res.fun)
        gap = current - opt
        total_gap += gap
        print(
            f"f#{f_idx}{f}: steps={steps} swap_gain={gain:.9g} "
            f"linear_gap={gap:.9g} current={current:.9f} opt={opt:.9f}"
        )
        if gap > 1e-8:
            diff = x - res.x
            support = sorted(
                [(abs(d), d, k) for d, k in zip(diff, idx) if abs(d) > 1e-7],
                reverse=True,
            )[:6]
            for _absd, d, k in support:
                av = inst.vars[k]
                _ff, i, j = meta[av.pair]
                print(f"  diff={d:+.6g} pair=({i},{j}) gate={inst.gates[av.gate]}")
    print(f"total_linear_gap={total_gap:.9g}")


if __name__ == "__main__":
    main()
