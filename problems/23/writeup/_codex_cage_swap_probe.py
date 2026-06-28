"""2x2 swap probe for y-dependent CAGE routes.

For a fixed hard y, sample an extreme route for each bad edge, then test all
pair/gate 2x2 balance-preserving swaps:

    p->g, q->h  becomes  p->h, q->g.

If the sampled route is supposed to represent a Monge/no-crossing local
minimum, these swaps should not improve the y-dependent conic objective.
This is floating structure mining, not an exact checker.
"""

from __future__ import annotations

import argparse

import numpy as np

from _codex_cage import aggregate, blowup_edges, build_instance
from _codex_cage_extreme_sample import f_subproblem, pair_meta, sample_extremes
from _codex_cage_ydep import maximize_gap
from _h import dec, loads


def sub_phi(inst, idx, gates, x, y):
    A = {g: 0.0 for g in gates}
    B = {g: 0.0 for g in gates}
    for val, k in zip(x, idx):
        if val <= 1e-12:
            continue
        av = inst.vars[k]
        A[av.gate] += val * sum(pfv * y[v] for v, pfv in av.left)
        B[av.gate] += val * sum(pfv * y[v] for v, pfv in av.right)
    return sum(2.0 * np.sqrt(max(A[g], 0.0) * max(B[g], 0.0)) for g in gates)


def best_swaps(inst, idx, gates, x, y, tol=1e-10):
    pos = [a for a, val in enumerate(x) if val > tol]
    by_pg = {(inst.vars[k].pair, inst.vars[k].gate): a for a, k in enumerate(idx)}
    base = sub_phi(inst, idx, gates, x, y)
    best = []
    for a in pos:
        p = inst.vars[idx[a]].pair
        g = inst.vars[idx[a]].gate
        for b in pos:
            if b <= a:
                continue
            q = inst.vars[idx[b]].pair
            h = inst.vars[idx[b]].gate
            if p == q or g == h:
                continue
            ah = by_pg.get((p, h))
            bg = by_pg.get((q, g))
            if ah is None or bg is None:
                continue
            eps = min(x[a], x[b])
            if eps <= tol:
                continue
            yx = x.copy()
            yx[a] -= eps
            yx[b] -= eps
            yx[ah] += eps
            yx[bg] += eps
            val = sub_phi(inst, idx, gates, yx, y)
            gain = base - val
            if gain > 1e-9:
                best.append((gain, eps, a, b, ah, bg, val))
    best.sort(reverse=True)
    return base, best


def greedy_descent(inst, idx, gates, x, y, max_steps=200):
    x = x.copy()
    total_gain = 0.0
    for step in range(max_steps):
        base, swaps = best_swaps(inst, idx, gates, x, y)
        if not swaps:
            return x, base, total_gain, step
        gain, eps, a, b, ah, bg, _newval = swaps[0]
        x[a] -= eps
        x[b] -= eps
        x[ah] += eps
        x[bg] += eps
        total_gain += gain
    base, _swaps = best_swaps(inst, idx, gates, x, y)
    return x, base, total_gain, max_steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--samples", type=int, default=500)
    ap.add_argument("--y-restarts", type=int, default=64)
    ap.add_argument("--seed", type=int, default=20260628)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--descent", action="store_true")
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    inst = build_instance(info, f"{args.g6}[{args.blow}]")
    A0, B0 = aggregate(inst, inst.alpha0)
    gap, y, _ok, _msg = maximize_gap(A0, B0, inst.cap, restarts=args.y_restarts)
    rows, total, _alpha0, _fixed = sample_extremes(inst, info, y, args.samples, args.seed)
    meta = pair_meta(info)
    print(f"{inst.label}: alpha0_gap={gap:+.9f} sampled_total={total:.9f}")
    for row in rows:
        val, f_idx, f, src, _nnz, _nv, _npair, _ngate, idx, alpha_sub = row
        if alpha_sub is None:
            continue
        _idx2, _pairs, gates, _Aeq, _beq = f_subproblem(inst, f_idx)
        base, swaps = best_swaps(inst, idx, gates, np.array(alpha_sub, dtype=float), y)
        print(f"f#{f_idx}{f}: src={src} phi={base:.9f} improving_2x2={len(swaps)}")
        for gain, eps, a, b, ah, bg, newval in swaps[: args.top]:
            av = inst.vars[idx[a]]
            bv = inst.vars[idx[b]]
            ahv = inst.vars[idx[ah]]
            bgv = inst.vars[idx[bg]]
            _fa, ai, aj = meta[av.pair]
            _fb, bi, bj = meta[bv.pair]
            print(
                "  gain={:.9g} eps={:.6g} ({},{})@{} <-> ({},{})@{} "
                "via gates {} {}".format(
                    gain,
                    eps,
                    ai,
                    aj,
                    inst.gates[av.gate],
                    bi,
                    bj,
                    inst.gates[bv.gate],
                    inst.gates[ahv.gate],
                    inst.gates[bgv.gate],
                )
            )
        if args.descent:
            x2, val2, gain2, steps = greedy_descent(inst, idx, gates, np.array(alpha_sub, dtype=float), y)
            _base2, swaps2 = best_swaps(inst, idx, gates, x2, y)
            print(
                f"  descent steps={steps} total_gain={gain2:.9g} "
                f"phi2={val2:.9f} remaining_swaps={len(swaps2)}"
            )


if __name__ == "__main__":
    main()
