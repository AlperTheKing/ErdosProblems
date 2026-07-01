"""Monge/single-crossing diagnostic for y-dependent CAGE routes.

This is a floating structural probe, not an acceptance checker.  For a fixed
adversarial y, it builds a CAGE route, applies greedy 2x2 closure, and checks
the exact first-variation sign predicted by the 2x2 derivative:

    dPhi/deps
      = (w_k-w_i)(r_g-r_h) + (w_l-w_j)(1/r_g-1/r_h).

For every feasible 2x2 swap whose two source variables are positive, a
2x2-closed local minimum should have dPhi/deps >= 0.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import numpy as np

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage
from _codex_cage_2swap_closure import close_alpha
from _codex_cage_extreme_sample import f_subproblem, pair_meta
from _codex_cage_ydep import maximize_gap, ydep_gap
from _h import dec, loads


def c5_blowup(sizes_text):
    sizes = [int(x) for x in sizes_text.split(",") if x.strip()]
    if len(sizes) != 5 or any(x <= 0 for x in sizes):
        raise ValueError("--c5-sizes must have five positive comma-separated integers")
    offsets = [0]
    for s in sizes[:-1]:
        offsets.append(offsets[-1] + s)
    parts = [list(range(offsets[i], offsets[i] + sizes[i])) for i in range(5)]
    edges = []
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i + 1) % 5]:
                edges.append((a, b))
    return sum(sizes), edges, "C5[" + ",".join(str(x) for x in sizes) + "]"


def sub_gate_sides(inst, idx, x, y):
    A = defaultdict(float)
    B = defaultdict(float)
    for val, k in zip(x, idx):
        if val <= 1e-12:
            continue
        av = inst.vars[k]
        A[av.gate] += val * sum(pfv * y[v] for v, pfv in av.left)
        B[av.gate] += val * sum(pfv * y[v] for v, pfv in av.right)
    return A, B


def monge_report(inst, info, alpha, y, tol):
    meta = pair_meta(info)
    rows = []
    total_sources = 0
    total_viol = 0
    global_min_deriv = 0.0
    worst = None

    for f_idx, f in enumerate(info["M"]):
        idx, _pairs, gates, _Aeq, _beq = f_subproblem(inst, f_idx)
        x = np.array([alpha[k] for k in idx], dtype=float)
        A, B = sub_gate_sides(inst, idx, x, y)
        ratio = {}
        for g in gates:
            if A[g] > tol and B[g] > tol:
                ratio[g] = float(np.sqrt(B[g] / A[g]))

        by_pg = {(inst.vars[k].pair, inst.vars[k].gate): a for a, k in enumerate(idx)}
        pos = [a for a, val in enumerate(x) if val > tol]
        viol = 0
        checked = 0
        min_deriv = 0.0
        f_worst = None

        for aa, a in enumerate(pos):
            av = inst.vars[idx[a]]
            p = av.pair
            g = av.gate
            if g not in ratio:
                continue
            wi = sum(pfv * y[v] for v, pfv in av.left)
            wj = sum(pfv * y[v] for v, pfv in av.right)
            for b in pos[aa + 1 :]:
                bv = inst.vars[idx[b]]
                q = bv.pair
                h = bv.gate
                if p == q or g == h or h not in ratio:
                    continue
                ah = by_pg.get((p, h))
                bg = by_pg.get((q, g))
                if ah is None or bg is None:
                    continue
                wk = sum(pfv * y[v] for v, pfv in bv.left)
                wl = sum(pfv * y[v] for v, pfv in bv.right)
                rg = ratio[g]
                rh = ratio[h]
                deriv = (wk - wi) * (rg - rh) + (wl - wj) * (1.0 / rg - 1.0 / rh)
                checked += 1
                if deriv < min_deriv:
                    min_deriv = deriv
                    f_worst = (a, b, ah, bg, deriv, rg, rh)
                if deriv < -tol:
                    viol += 1

        total_sources += checked
        total_viol += viol
        if min_deriv < global_min_deriv:
            global_min_deriv = min_deriv
            worst = (f_idx, f, f_worst, idx)
        rows.append((f_idx, f, len(pos), len(gates), checked, viol, min_deriv))

    return rows, total_sources, total_viol, global_min_deriv, worst, meta


def print_worst(inst, meta, worst):
    if worst is None or worst[2] is None:
        return
    f_idx, f, item, idx = worst
    a, b, ah, bg, deriv, rg, rh = item
    for label, loc in [("source1", a), ("source2", b), ("cross1", ah), ("cross2", bg)]:
        av = inst.vars[idx[loc]]
        _ff, i, j = meta[av.pair]
        print(
            f"    {label}: pair=({i},{j}) gate={inst.gates[av.gate]} "
            f"alpha={loc}",
            flush=True,
        )
    print(f"    worst f#{f_idx}{f} deriv={deriv:+.12g} r=({rg:.8g},{rh:.8g})", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--c5-sizes", default="")
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--restarts", type=int, default=6)
    ap.add_argument("--y-restarts", type=int, default=24)
    ap.add_argument("--start", choices=["fixed", "alpha0"], default="fixed")
    ap.add_argument("--tol", type=float, default=1e-8)
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()

    if args.c5_sizes:
        n, edges, label = c5_blowup(args.c5_sizes)
    else:
        n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
        label = f"{args.g6}[{args.blow}]"
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")

    inst = build_instance(info, label)
    A0, B0 = aggregate(inst, inst.alpha0)
    gap0, y, _ok, _msg = maximize_gap(A0, B0, inst.cap, restarts=args.y_restarts)
    if args.start == "alpha0":
        alpha_start = inst.alpha0
    else:
        alpha_start = solve_cage(inst, rounds=args.rounds, restarts=args.restarts)["alpha"]
    closed, gain, steps = close_alpha(inst, info, alpha_start, y)
    closed_gap = ydep_gap(*aggregate(inst, closed), inst.cap, y)
    capy = float(inst.cap @ y)

    rows, checked, viol, min_deriv, worst, meta = monge_report(inst, info, closed, y, args.tol)
    print(
        f"{label}: n={inst.n} M={len(info['M'])} cap.y={capy:.9f} "
        f"alpha0_gap={gap0:+.9f} start={args.start}",
        flush=True,
    )
    print(
        f"  closed_gap={closed_gap:+.9f} 2swap_gain={gain:.9g} "
        f"steps={steps} derivative_checks={checked} violations={viol} "
        f"min_deriv={min_deriv:+.12g}",
        flush=True,
    )
    for row in sorted(rows, key=lambda r: (r[5], -r[6]), reverse=True)[: args.top]:
        f_idx, f, pos, gates, chk, bad, md = row
        print(
            f"  f#{f_idx}{f}: pos={pos} gates={gates} checks={chk} "
            f"viol={bad} min_deriv={md:+.12g}",
            flush=True,
        )
    print_worst(inst, meta, worst)


if __name__ == "__main__":
    main()
