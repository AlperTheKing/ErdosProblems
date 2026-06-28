"""KKT diagnostic for the floating CAGE certificate.

This is not an exact checker.  It inspects the LP dual for the adaptive
routing step at the optimized gate-ratio vector.  The goal is to identify
the small KKT cores that a proof of universal CAGE feasibility must exclude.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import linprog

from _codex_cage import aggregate, blowup_edges, build_instance, solve_cage, solve_x
from _h import dec, loads


def alpha_lp_with_dual(inst, x):
    m = len(inst.vars)
    n = inst.n
    costs = np.zeros((n, m))
    ep = np.exp(x)
    em = np.exp(-x)
    for k, av in enumerate(inst.vars):
        for v, pfv in av.left:
            costs[v, k] += ep[av.gate] * pfv
        for v, pfv in av.right:
            costs[v, k] += em[av.gate] * pfv

    aub = np.zeros((n, m + 1))
    aub[:, :m] = costs
    aub[:, m] = -inst.cap
    aeq = np.zeros((inst.Aeq.shape[0], m + 1))
    aeq[:, :m] = inst.Aeq
    c = np.zeros(m + 1)
    c[m] = 1.0
    res = linprog(
        c,
        A_ub=aub,
        b_ub=np.zeros(n),
        A_eq=aeq,
        b_eq=inst.beq,
        bounds=[(0.0, None)] * (m + 1),
        method="highs",
    )
    if not res.success:
        raise RuntimeError(res.message)
    return res, costs


def summarize(label, info, rounds, restarts, top, polish):
    inst = build_instance(info, label)
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    x = row["x"]
    for _ in range(polish):
        res0, _costs0 = alpha_lp_with_dual(inst, x)
        _ratio, x, _ok, _msg = solve_x(inst, res0.x[: len(inst.vars)], x0=x)
    res, costs = alpha_lp_with_dual(inst, x)
    alpha = res.x[: len(inst.vars)]
    eta = float(res.x[-1])
    A_gate, B_gate = aggregate(inst, alpha)

    lambda_v = -np.asarray(res.ineqlin.marginals, dtype=float)
    eq_dual = np.asarray(res.eqlin.marginals, dtype=float)
    lower = np.asarray(res.lower.marginals, dtype=float)
    reduced = np.zeros(len(inst.vars))
    # HiGHS reports marginals for the <= constraints directly.  At optimum,
    # c + A_ub^T marg + A_eq^T y + lower_marg = 0.
    reduced[:] = costs.T @ res.ineqlin.marginals
    reduced += inst.Aeq.T @ eq_dual

    print(
        f"{label}: n={inst.n} vars={len(inst.vars)} gates={len(inst.gates)} "
        f"gap={row['gap']:+.6g} ratio={row['ratio']:.9f} eta_lp={eta:.9f}",
        flush=True,
    )
    print(
        f"dual: lambda_nnz={int(np.sum(lambda_v>1e-9))}/{inst.n} "
        f"sum_lambda_cap={float(lambda_v @ inst.cap):.9f} "
        f"sum_lambda={float(np.sum(lambda_v)):.9f}",
        flush=True,
    )

    raw = costs @ alpha
    slack = eta * inst.cap - raw
    print("active vertex duals:")
    order = sorted(range(inst.n), key=lambda v: (-lambda_v[v], slack[v]))
    for v in order[: min(top, inst.n)]:
        print(
            f"  v={v} lambda={lambda_v[v]:.9g} cap={inst.cap[v]:.6g} "
            f"used={raw[v]:.6g} slack={slack[v]:+.3g}",
            flush=True,
        )

    pos = np.where(alpha > 1e-9)[0]
    low = np.where(alpha <= 1e-9)[0]
    print(
        f"kkt residuals: pos max|red|={float(np.max(np.abs(reduced[pos])) if len(pos) else 0):.3g} "
        f"zero min red={float(np.min(reduced[low]) if len(low) else 0):.3g} "
        f"lower max={float(np.max(np.abs(lower[:len(inst.vars)] + reduced))):.3g}",
        flush=True,
    )

    contrib = lambda_v[:, None] * costs
    var_price = np.sum(contrib, axis=0)
    print("top positive-alpha variables by dual price:")
    for k in sorted(pos, key=lambda kk: var_price[kk], reverse=True)[:top]:
        av = inst.vars[k]
        gate = inst.gates[av.gate]
        print(
            f"  a={alpha[k]:.6g} price={var_price[k]:.6g} red={reduced[k]:+.3g} "
            f"pair={av.pair} gate={gate}",
            flush=True,
        )

    print("gate balance residuals under dual lambda:")
    gate_rows = []
    for g, gate in enumerate(inst.gates):
        left = float(lambda_v @ A_gate[g])
        right = float(lambda_v @ B_gate[g])
        r = float(np.exp(x[g]))
        resid = r * left - right / r
        scale = abs(r * left) + abs(right / r) + 1e-15
        mass = float(np.sum(A_gate[g]) + np.sum(B_gate[g]))
        gate_rows.append((abs(resid) / scale, resid, left, right, r, mass, gate))
    for rel, resid, left, right, r, mass, gate in sorted(gate_rows, reverse=True)[:top]:
        print(
            f"  rel={rel:.3g} resid={resid:+.6g} left={left:.6g} right={right:.6g} "
            f"r={r:.6g} mass={mass:.6g} gate={gate}",
            flush=True,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--top", type=int, default=16)
    ap.add_argument("--polish", type=int, default=3)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    summarize(f"{args.g6}[{args.blow}]", info, args.rounds, args.restarts, args.top, args.polish)


if __name__ == "__main__":
    main()
