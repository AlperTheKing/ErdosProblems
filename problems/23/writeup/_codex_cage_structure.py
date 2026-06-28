"""Inspect the adaptive CAGE routing pattern.

This diagnostic reconstructs the (f,i,j,t,e) metadata for alpha variables
and reports how far the optimized routing is from the uniform alpha0.
It is not an exact checker.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import numpy as np

from _codex_cage import aggregate, blowup_edges, budget, build_instance, canon_edge, solve_cage
from _h import dec, loads


def variable_details(info):
    pair_details = []
    gate_details = []
    pair_index = {}
    gate_index = {}
    vars_ = []
    for f_idx, f in enumerate(info["M"]):
        paths = info["cyc"][f]
        L = info["ell"][f]
        pi = [dict() for _ in range(L - 1)]
        for P in paths:
            for t in range(L - 1):
                e = canon_edge(P[t], P[t + 1])
                pi[t][e] = pi[t].get(e, 0) + 1
        for i in range(L):
            for j in range(i + 1, L):
                pair_index[(f_idx, i, j)] = len(pair_details)
                pair_details.append((f_idx, f, i, j, j - i))
        for t in range(L - 1):
            for e in pi[t]:
                gate_index[(f_idx, t, e)] = len(gate_details)
                gate_details.append((f_idx, f, t, e))
        for i in range(L):
            for j in range(i + 1, L):
                pidx = pair_index[(f_idx, i, j)]
                for t in range(i, j):
                    for e in pi[t]:
                        g = gate_index[(f_idx, t, e)]
                        vars_.append((pidx, g, f_idx, f, i, j, t, e))
    return pair_details, gate_details, vars_


def summarize(label, info, rounds, restarts, top):
    inst = build_instance(info, label)
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    pair_details, gate_details, vars_meta = variable_details(info)
    alpha = row["alpha"]
    alpha0 = inst.alpha0
    x = row["x"]
    diff = alpha - alpha0
    print(
        f"{label}: n={inst.n} M={len(info['M'])} vars={len(alpha)} gates={len(inst.gates)} "
        f"gap={row['gap']:+.6g} ratio={row['ratio']:.9f} eta={row['eta']:.9f}",
        flush=True,
    )
    print(
        f"alpha stats: nnz={int(np.sum(alpha>1e-10))}/{len(alpha)} "
        f"changed={int(np.sum(np.abs(diff)>1e-8))} "
        f"L1diff={float(np.sum(np.abs(diff))):.6g} Linf={float(np.max(np.abs(diff))):.6g}",
        flush=True,
    )

    A, B = aggregate(inst, alpha)
    raw = budget(A, B, x)
    slack = inst.cap - raw
    print("tightest vertex budgets:")
    for v in np.argsort(slack)[: min(top, inst.n)]:
        print(
            f"  v={int(v)} cap={inst.cap[v]:.6g} used={raw[v]:.6g} "
            f"slack={slack[v]:+.6g} ratio={raw[v]/inst.cap[v]:.9f}",
            flush=True,
        )

    by_pair = defaultdict(list)
    by_gate = defaultdict(float)
    for k, val in enumerate(alpha):
        pidx, g, *_rest = vars_meta[k]
        by_pair[pidx].append((k, val))
        by_gate[g] += float(val)

    print("largest gate masses:")
    gate_masses = [(mass, g) for g, mass in by_gate.items() if mass > 1e-10]
    for mass, g in sorted(gate_masses, reverse=True)[:top]:
        f_idx, f, t, e = gate_details[g]
        print(
            f"  mass={mass:.6g} r={float(np.exp(x[g])):.6g} log_r={float(x[g]):+.6g} "
            f"f#{f_idx}{f} t={t} e={e}",
            flush=True,
        )

    support_hist = defaultdict(int)
    max_pair = []
    for pidx, items in by_pair.items():
        nz = [(k, v) for k, v in items if v > 1e-10]
        support_hist[len(nz)] += 1
        vals = sorted((float(v), k) for k, v in nz)
        if vals:
            max_pair.append((len(nz), vals[-1][0], pidx))
    print("pair support histogram:", dict(sorted(support_hist.items())), flush=True)

    print("top changed alpha variables:")
    order = sorted(range(len(alpha)), key=lambda k: abs(diff[k]), reverse=True)[:top]
    for k in order:
        pidx, g, f_idx, f, i, j, t, e = vars_meta[k]
        print(
            f"  d={diff[k]:+.6g} a={alpha[k]:.6g} a0={alpha0[k]:.6g} "
            f"f#{f_idx}{f} pair=({i},{j}) gap={j-i} t={t} e={e}",
            flush=True,
        )

    print("largest pair supports:")
    for nz, mx, pidx in sorted(max_pair, reverse=True)[:top]:
        f_idx, f, i, j, gap = pair_details[pidx]
        vals = sorted(
            [
                (float(v), float(np.exp(x[vars_meta[k][1]])), vars_meta[k][6], vars_meta[k][7])
                for k, v in by_pair[pidx]
                if v > 1e-10
            ],
            reverse=True,
        )
        print(f"  f#{f_idx}{f} pair=({i},{j}) gap={gap} nz={nz} max={mx:.6g} vals={vals[:8]}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    summarize(f"{args.g6}[{args.blow}]", info, args.rounds, args.restarts, args.top)


if __name__ == "__main__":
    main()
