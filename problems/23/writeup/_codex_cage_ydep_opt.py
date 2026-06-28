"""Optimize alpha for one y-dependent CAGE objective.

This is a floating structure-mining diagnostic.  For a chosen graph, first
find a y that maximizes the alpha0 y-dependent gap, then minimize

    sum_g 2 sqrt((A_g.y)(B_g.y)) - cap.y

over alpha subject to the CAGE R1/R2 marginals.  The problem is nonconvex
(concave minimization), so this is not a certificate.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import minimize

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage
from _codex_cage_ydep import maximize_gap, ydep_gap
from _h import dec, loads


def ydep_value_and_grad(inst, y):
    m = len(inst.vars)
    gnum = len(inst.gates)
    left = np.zeros((gnum, m))
    right = np.zeros((gnum, m))
    for k, av in enumerate(inst.vars):
        ly = sum(pfv * y[v] for v, pfv in av.left)
        ry = sum(pfv * y[v] for v, pfv in av.right)
        left[av.gate, k] = ly
        right[av.gate, k] = ry

    def fun(alpha):
        A = left @ alpha
        B = right @ alpha
        return float(np.sum(2.0 * np.sqrt(np.maximum(A, 0.0) * np.maximum(B, 0.0))))

    def jac(alpha):
        A = left @ alpha
        B = right @ alpha
        grad = np.zeros(m)
        eps = 1e-14
        for g in range(gnum):
            if A[g] <= eps and B[g] <= eps:
                continue
            if A[g] <= eps:
                coeff_a = 0.0
                coeff_b = 0.0
            elif B[g] <= eps:
                coeff_a = 0.0
                coeff_b = 0.0
            else:
                coeff_a = np.sqrt(B[g] / A[g])
                coeff_b = np.sqrt(A[g] / B[g])
            grad += coeff_a * left[g] + coeff_b * right[g]
        return grad

    return fun, jac


def optimize_alpha(inst, y, starts, maxiter):
    fun, jac = ydep_value_and_grad(inst, y)
    cons = [{"type": "eq", "fun": lambda a: inst.Aeq @ a - inst.beq, "jac": lambda a: inst.Aeq}]
    bounds = [(0.0, None)] * len(inst.vars)
    best = None
    for name, a0 in starts:
        initial = (fun(a0), f"{name}:initial", None)
        if best is None or initial[0] < best[0]:
            best = initial
        res = minimize(
            fun,
            a0,
            jac=jac,
            constraints=cons,
            bounds=bounds,
            method="SLSQP",
            options={"maxiter": maxiter, "ftol": 1e-12, "disp": False},
        )
        val = fun(res.x)
        if best is None or val < best[0]:
            best = (val, name, res)
    return best


def inspect(label, info, rounds, restarts, y_restarts, maxiter):
    inst = build_instance(info, label)
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    A0, B0 = aggregate(inst, inst.alpha0)
    gap0, y, _ok, _msg = maximize_gap(A0, B0, inst.cap, restarts=y_restarts)
    capy = float(inst.cap @ y)
    starts = [("alpha0", inst.alpha0), ("fixedCAGE", row["alpha"])]
    best_val, name, res = optimize_alpha(inst, y, starts, maxiter)
    fixed_val = ydep_gap(*aggregate(inst, row["alpha"]), inst.cap, y) + capy
    print(f"{label}: n={inst.n} vars={len(inst.vars)} gates={len(inst.gates)}")
    print(f"  alpha0 worst gap={gap0:+.9f} cap.y={capy:.9f}")
    print(f"  fixedCAGE value={fixed_val:.9f} gap={fixed_val-capy:+.9f}")
    if res is None:
        print(
            f"  best alpha candidate={name} value={best_val:.9f} "
            f"gap={best_val-capy:+.9f} (initial point retained)",
            flush=True,
        )
    else:
        print(
            f"  optimized alpha start={name} value={best_val:.9f} "
            f"gap={best_val-capy:+.9f} success={res.success} nit={res.nit}",
            flush=True,
        )
        alpha = res.x
        print(
            f"  alpha nnz={int(np.sum(alpha>1e-9))}/{len(alpha)} "
            f"eq_err={float(np.max(np.abs(inst.Aeq@alpha-inst.beq))):.3g}",
            flush=True,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--y-restarts", type=int, default=32)
    ap.add_argument("--maxiter", type=int, default=2000)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    inspect(f"{args.g6}[{args.blow}]", info, args.rounds, args.restarts, args.y_restarts, args.maxiter)


if __name__ == "__main__":
    main()
