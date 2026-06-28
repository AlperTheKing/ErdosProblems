"""Sample extreme routings for the y-dependent CAGE objective.

For a chosen hard y (the alpha0 worst-y by default), each bad edge f has an
independent transportation polytope.  The y-dependent objective is concave on
that polytope, so a minimum is attained at an extreme point.  This diagnostic
samples vertices by optimizing random linear objectives and evaluates the
conic objective there.

This is floating structure mining, not an exact checker.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import linprog

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage
from _codex_cage_ydep import maximize_gap, ydep_gap
from _h import dec, loads


def pair_count(inst):
    return max(av.pair for av in inst.vars) + 1


def f_subproblem(inst, f_idx):
    pc = pair_count(inst)
    idx = [k for k, av in enumerate(inst.vars) if inst.gates[av.gate][0] == f_idx]
    pairs = sorted({inst.vars[k].pair for k in idx})
    gates = sorted({inst.vars[k].gate for k in idx})
    rows = []
    rhs = []
    for p in pairs:
        rows.append([1.0 if inst.vars[k].pair == p else 0.0 for k in idx])
        rhs.append(1.0)
    for g in gates:
        rows.append([1.0 if inst.vars[k].gate == g else 0.0 for k in idx])
        rhs.append(float(inst.beq[pc + g]))
    return idx, pairs, gates, np.array(rows), np.array(rhs)


def phi_for_subalpha(inst, idx, gates, alpha_sub, y):
    A = {g: 0.0 for g in gates}
    B = {g: 0.0 for g in gates}
    for val, k in zip(alpha_sub, idx):
        if val <= 1e-12:
            continue
        av = inst.vars[k]
        ly = sum(pfv * y[v] for v, pfv in av.left)
        ry = sum(pfv * y[v] for v, pfv in av.right)
        A[av.gate] += val * ly
        B[av.gate] += val * ry
    return sum(2.0 * np.sqrt(max(A[g], 0.0) * max(B[g], 0.0)) for g in gates)


def pair_meta(info):
    out = []
    for f_idx, f in enumerate(info["M"]):
        L = info["ell"][f]
        for i in range(L):
            for j in range(i + 1, L):
                out.append((f_idx, i, j))
    return out


def sample_extremes(inst, info, y, samples, seed):
    rng = np.random.default_rng(seed)
    rows = []
    total_best = 0.0
    total_alpha0 = 0.0
    total_fixed = 0.0
    fixed = solve_cage(inst, rounds=8, restarts=8)["alpha"]

    for f_idx, f in enumerate(info["M"]):
        idx, pairs, gates, Aeq, beq = f_subproblem(inst, f_idx)
        bounds = [(0.0, None)] * len(idx)

        def eval_global(alpha_global):
            return phi_for_subalpha(inst, idx, gates, [alpha_global[k] for k in idx], y)

        best = (eval_global(inst.alpha0), "alpha0", None)
        total_alpha0 += best[0]
        fixed_val = eval_global(fixed)
        total_fixed += fixed_val
        if fixed_val < best[0]:
            best = (fixed_val, "fixedCAGE", np.array([fixed[k] for k in idx], dtype=float))

        for s in range(samples):
            c = rng.normal(size=len(idx))
            res = linprog(c, A_eq=Aeq, b_eq=beq, bounds=bounds, method="highs")
            if not res.success:
                continue
            val = phi_for_subalpha(inst, idx, gates, res.x, y)
            if val < best[0] - 1e-10:
                best = (val, f"rand{s}", res.x)

        nnz = None if best[2] is None else int(np.sum(best[2] > 1e-9))
        rows.append((best[0], f_idx, f, best[1], nnz, len(idx), len(pairs), len(gates), idx, best[2]))
        total_best += best[0]

    return rows, total_best, total_alpha0, total_fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--samples", type=int, default=200)
    ap.add_argument("--y-restarts", type=int, default=64)
    ap.add_argument("--seed", type=int, default=20260628)
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--dump-top", type=int, default=20)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    label = f"{args.g6}[{args.blow}]"
    inst = build_instance(info, label)
    A0, B0 = aggregate(inst, inst.alpha0)
    gap0, y, _ok, _msg = maximize_gap(A0, B0, inst.cap, restarts=args.y_restarts)
    capy = float(inst.cap @ y)
    rows, best, alpha0, fixed = sample_extremes(inst, info, y, args.samples, args.seed)
    print(f"{label}: cap.y={capy:.9f} alpha0_worst_gap={gap0:+.9f}")
    print(f"  total alpha0={alpha0:.9f} gap={alpha0-capy:+.9f}")
    print(f"  total fixedCAGE={fixed:.9f} gap={fixed-capy:+.9f}")
    print(f"  total sampled_best={best:.9f} gap={best-capy:+.9f}")
    meta = pair_meta(info)
    for val, f_idx, f, src, nnz, nv, npair, ngate, idx, alpha_sub in rows:
        print(
            f"  f#{f_idx}{f}: best={val:.9f} src={src} nnz={nnz} "
            f"vars={nv} pairs={npair} gates={ngate}",
            flush=True,
        )
        if args.dump and alpha_sub is not None:
            support = []
            for val_sub, k in zip(alpha_sub, idx):
                if val_sub <= 1e-9:
                    continue
                av = inst.vars[k]
                _ff, i, j = meta[av.pair]
                gf, t, e = inst.gates[av.gate]
                support.append((float(val_sub), i, j, t, e))
            support.sort(reverse=True)
            for val_sub, i, j, t, e in support[: args.dump_top]:
                print(f"      a={val_sub:.6g} pair=({i},{j}) gap_t={t} gate={e}")


if __name__ == "__main__":
    main()
