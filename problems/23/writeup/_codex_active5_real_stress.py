"""Numerical real-weight stress for a fixed active-5 quotient row.

This is only a falsifier radar.  It uses floating point optimization to look
for real weights w_i >= 1 satisfying the selected quotient cut maximality
constraints and making

    row_sum(Q) - N > coeff * eta.

Exact Fraction gates remain the acceptance standard.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import math
import random

import numpy as np
from scipy.optimize import differential_evolution, minimize

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_active_size_quotient_fast import EQ, SIB, side_data
    from _codex_c5lift_weighted_quotient_gate import edges_of


def path_weight_float(path, w):
    out = 1.0
    for v in path[1:-1]:
        out *= w[v]
    return out


def loads_for_float(n, M, paths, w):
    loads = np.zeros(n, dtype=float)
    for a, b in M:
        ps = paths[(a, b)]
        z = sum(path_weight_float(p, w) for p in ps)
        edge_mult = w[a] * w[b]
        loads[a] += w[b]
        loads[b] += w[a]
        for p in ps:
            wp = path_weight_float(p, w)
            for v in p[1:-1]:
                loads[v] += edge_mult * wp / (z * w[v])
    return loads


def qcut_slacks(g6, side, w):
    n, E = edges_of(g6)
    side_bits = tuple(int(c) for c in side)
    selected = sum(w[a] * w[b] for a, b in E if side_bits[a] != side_bits[b])
    slacks = []
    for mask in range(1, (1 << n) - 1):
        # quotient by complement
        if not (mask & 1):
            continue
        val = 0.0
        for a, b in E:
            if ((mask >> a) & 1) ^ ((mask >> b) & 1):
                val += w[a] * w[b]
        slacks.append(selected - val)
    return slacks


def objective_factory(g6, side, row, coeff, penalty):
    n, _E, M, paths, _rows = side_data(g6, side)
    row = tuple(row)

    def eval_x(x):
        w = np.exp(np.asarray(x, dtype=float)) + 1.0
        N = float(np.sum(w))
        m = sum(w[a] * w[b] for a, b in M)
        eta = N * N / 25.0 - m
        loads = loads_for_float(n, M, paths, w)
        row_sum = float(sum(loads[v] for v in row))
        debt = row_sum - N
        margin = coeff * eta - debt
        slacks = qcut_slacks(g6, side, w)
        qviol = sum(max(0.0, -s) ** 2 for s in slacks)
        etaviol = max(0.0, 1e-8 - eta) ** 2
        active_viol = 0.0
        tau = 5.0 * m / N
        for v in row:
            active_viol += max(0.0, tau - loads[v]) ** 2
        score = margin + penalty * (qviol + etaviol + active_viol)
        return score, {
            "w": w,
            "N": N,
            "m": m,
            "eta": eta,
            "tau": tau,
            "loads": loads,
            "row_sum": row_sum,
            "debt": debt,
            "ratio": debt / eta if eta > 0 else math.inf,
            "margin": margin,
            "min_qslack": min(slacks),
            "qviol": qviol,
            "active_viol": active_viol,
        }

    def obj(x):
        return eval_x(x)[0]

    return obj, eval_x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], required=True)
    ap.add_argument("--side", required=True)
    ap.add_argument("--row", required=True)
    ap.add_argument("--coeff", default="2/3")
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--seed", type=int, default=230704)
    ap.add_argument("--upper", type=float, default=8.0)
    ap.add_argument("--penalty", type=float, default=1e5)
    ap.add_argument("--mode", choices=["de", "random"], default="de")
    ap.add_argument("--samples", type=int, default=200000)
    args = ap.parse_args()

    graph = EQ if args.graph == "eq" else SIB
    row = tuple(int(x) for x in args.row.replace(",", " ").split())
    num, den = args.coeff.split("/") if "/" in args.coeff else (args.coeff, "1")
    coeff = float(num) / float(den)
    rng = random.Random(args.seed)

    obj, eval_x = objective_factory(graph, args.side, row, coeff, args.penalty)
    bounds = [(0.0, math.log(args.upper - 1.0))] * 10

    if args.mode == "random":
        best = None
        feasible = 0
        for i in range(args.samples):
            # Bias toward the hard lower boundary w_i=1 while still sampling
            # the interior.  Uniform x means w=1+exp(x).
            x = np.array([rng.random() * bounds[j][1] for j in range(10)])
            _score, rec = eval_x(x)
            if rec["min_qslack"] < -1e-8 or rec["eta"] <= 1e-8:
                continue
            if min(rec["loads"][v] - rec["tau"] for v in row) < -1e-8:
                continue
            feasible += 1
            key = rec["ratio"]
            if best is None or key > best[0]:
                best = (key, rec)
        print("mode random")
        print("samples", args.samples)
        print("feasible", feasible)
        if best is None:
            print("best none")
            return
        _key, rec = best
        for k in ("N", "m", "eta", "tau", "row_sum", "debt", "ratio", "margin", "min_qslack", "qviol", "active_viol"):
            print(k, rec[k])
        print("weights", [float(x) for x in rec["w"]])
        print("row_loads", [float(rec["loads"][v]) for v in row])
        return

    best = None
    for t in range(args.trials):
        seed = rng.randrange(1 << 30)
        res = differential_evolution(
            obj,
            bounds,
            seed=seed,
            polish=False,
            maxiter=500,
            popsize=12,
            tol=1e-9,
            workers=1,
            updating="immediate",
        )
        loc = minimize(obj, res.x, method="Nelder-Mead", options={"maxiter": 2000})
        cand = loc if loc.fun <= res.fun else res
        score, rec = eval_x(cand.x)
        if best is None or score < best[0]:
            best = (score, rec, seed)
            print("trial", t, "score", score, "ratio", rec["ratio"], "margin", rec["margin"], "min_qslack", rec["min_qslack"])

    assert best is not None
    score, rec, seed = best
    print("BEST seed", seed)
    print("score", score)
    for k in ("N", "m", "eta", "tau", "row_sum", "debt", "ratio", "margin", "min_qslack", "qviol", "active_viol"):
        print(k, rec[k])
    print("weights", [float(x) for x in rec["w"]])
    print("row_loads", [float(rec["loads"][v]) for v in row])


if __name__ == "__main__":
    main()
