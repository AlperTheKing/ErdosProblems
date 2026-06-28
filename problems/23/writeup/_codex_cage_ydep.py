"""Probe y-dependent CAGE variants.

For a fixed alpha satisfying the CAGE R1/R2 marginals, the best gate ratio
for a single nonnegative vertex weight y is

    r_g = sqrt((B_g.y)/(A_g.y)).

Thus the y-dependent AM-GM cost is

    sum_g 2 sqrt((A_g.y)(B_g.y)).

This script maximizes that cost minus cap.y over y>=0, cap.y=1.  It is a
floating diagnostic, not an exact checker.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import minimize

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage
from _h import dec, loads


def ydep_gap(A, B, cap, y):
    ay = A @ y
    by = B @ y
    return float(np.sum(2.0 * np.sqrt(np.maximum(ay, 0.0) * np.maximum(by, 0.0))) - cap @ y)


def maximize_gap(A, B, cap, restarts=64, seed=2307):
    n = len(cap)
    rng = np.random.default_rng(seed)

    def normalize(z):
        y = np.maximum(z, 0.0)
        den = float(cap @ y)
        if den <= 0:
            return np.ones(n) / float(np.sum(cap))
        return y / den

    def objective(z):
        return -ydep_gap(A, B, cap, normalize(z))

    starts = [np.ones(n)]
    starts += [np.eye(n)[v] / cap[v] for v in range(n)]
    starts += [rng.random(n) for _ in range(restarts)]
    best = None
    for z0 in starts:
        res = minimize(
            objective,
            z0,
            method="Nelder-Mead",
            options={"maxiter": 8000, "xatol": 1e-9, "fatol": 1e-12},
        )
        y = normalize(res.x)
        gap = ydep_gap(A, B, cap, y)
        if best is None or gap > best[0]:
            best = (gap, y, bool(res.success), str(res.message))
    return best


def inspect(label, info, rounds, restarts, y_restarts):
    inst = build_instance(info, label)
    cases = [("alpha0", inst.alpha0)]
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    cases.append(("adaptive", row["alpha"]))

    print(f"{label}: n={inst.n} M={len(info['M'])} fixedCAGE_gap={row['gap']:+.6g}")
    for name, alpha in cases:
        A, B = aggregate(inst, alpha)
        gap, y, ok, msg = maximize_gap(A, B, inst.cap, restarts=y_restarts)
        nnz = int(np.sum(y > 1e-7))
        print(
            f"  {name}: max_ydep_gap={gap:+.9f} y_nnz={nnz} "
            f"solver_ok={ok}",
            flush=True,
        )
        top = sorted(range(inst.n), key=lambda v: -y[v])[:8]
        print("    y_top=" + " ".join(f"{v}:{y[v]:.4g}" for v in top if y[v] > 1e-8), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--y-restarts", type=int, default=32)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    inspect(f"{args.g6}[{args.blow}]", info, args.rounds, args.restarts, args.y_restarts)


if __name__ == "__main__":
    main()
