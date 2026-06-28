"""Floating diagnostic for the fixed-ratio CAGE Farkas/Hall form.

This script is not an exact checker.  It extracts the alpha-LP dual
`lambda` at optimized CAGE ratios and reports the lambda-weighted transport
cost decomposition

    eta(r) = max_lambda sum_f OT_f(lambda,r),  lambda.cap = 1.

The theorem behind this diagnostic is recorded in CAGE_farkas_hall.md.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import numpy as np

from _codex_cage import blowup_edges, build_instance, solve_cage, solve_x
from _codex_cage_kkt import alpha_lp_with_dual
from _h import dec, loads


def inspect(label, info, rounds, restarts, polish, top):
    inst = build_instance(info, label)
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    x = row["x"]

    # Polish the alternating solution against the exact fixed-r LP a few times.
    for _ in range(polish):
        res0, _costs0 = alpha_lp_with_dual(inst, x)
        _ratio, x, _ok, _msg = solve_x(inst, res0.x[: len(inst.vars)], x0=x)

    res, costs = alpha_lp_with_dual(inst, x)
    alpha = res.x[: len(inst.vars)]
    eta = float(res.x[-1])
    lam = -np.asarray(res.ineqlin.marginals, dtype=float)
    lam_cap = float(lam @ inst.cap)
    weighted_costs = lam @ costs

    by_f = defaultdict(float)
    mass_by_f = defaultdict(float)
    support_by_f = defaultdict(int)
    for k, av in enumerate(inst.vars):
        f_idx = inst.gates[av.gate][0]
        by_f[f_idx] += float(alpha[k] * weighted_costs[k])
        mass_by_f[f_idx] += float(alpha[k])
        if alpha[k] > 1e-9:
            support_by_f[f_idx] += 1

    total_ot = sum(by_f.values())
    print(
        f"{label}: n={inst.n} M={len(info['M'])} vars={len(inst.vars)} gates={len(inst.gates)} "
        f"gap={row['gap']:+.6g} eta={eta:.9f} lambda.cap={lam_cap:.9f} "
        f"sumOT={total_ot:.9f}",
        flush=True,
    )

    print("lambda support:")
    for v in sorted(range(inst.n), key=lambda vv: -lam[vv])[:top]:
        if lam[v] <= 1e-10:
            continue
        print(
            f"  v={v} lambda={lam[v]:.9g} cap={inst.cap[v]:.6g} "
            f"T={float(info['T'][v]):.6g}",
            flush=True,
        )

    print("per-bad-edge OT contribution:")
    rows = []
    for f_idx, f in enumerate(info["M"]):
        ell = info["ell"][f]
        rows.append((by_f[f_idx], f_idx, f, ell, support_by_f[f_idx], mass_by_f[f_idx]))
    for val, f_idx, f, ell, supp, mass in sorted(rows, reverse=True)[:top]:
        print(
            f"  f#{f_idx}{f} ell={ell} OT={val:.9f} alpha_mass={mass:.6g} "
            f"support={supp}",
            flush=True,
        )

    # Reduced-cost check in the Farkas transport language.
    eq_dual = np.asarray(res.eqlin.marginals, dtype=float)
    red = costs.T @ res.ineqlin.marginals + inst.Aeq.T @ eq_dual
    pos = np.where(alpha > 1e-9)[0]
    zero = np.where(alpha <= 1e-9)[0]
    # HiGHS sign convention for lower-bound marginals gives red<=0 on
    # inactive variables and red=0 on positive variables.
    print(
        f"reduced-cost check: pos max|red|={float(np.max(np.abs(red[pos])) if len(pos) else 0):.3g} "
        f"inactive max red={float(np.max(red[zero]) if len(zero) else 0):+.3g}",
        flush=True,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--polish", type=int, default=3)
    ap.add_argument("--top", type=int, default=16)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    inspect(f"{args.g6}[{args.blow}]", info, args.rounds, args.restarts, args.polish, args.top)


if __name__ == "__main__":
    main()
