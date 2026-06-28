"""Codex diagnostic: pairwise corridor price (PCP) feasibility.

GPT-Pro proposed a sufficient certificate for CORR/LPD:
for every bad edge f and layer pair i<j choose rho_{f,i,j}>0, and set

    b_{f,i} = 1 + sum_{j>i} rho_{f,i,j} + sum_{h<i} rho_{f,h,i}^{-1}.

The pairwise AM-GM inequality gives

    (sum_i sqrt(w_i))^2 <= sum_i b_{f,i} w_i

provided the harmonic condition sum_i 1/b_{f,i} <= 1 holds. The b above
should satisfy that condition; this script also prints the worst harmonic
sum as a sanity check.

If the vertex budgets

    sum_{f,i: v in I_i(f)} b_{f,i} p_f(v) <= N

hold, this is a layer-price certificate. This is a floating-point scout only;
any survivor must be rationalized and exact-checked before it counts.
"""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from _h import GENG, dec, loads
from _layerprice import layers_of


@dataclass(frozen=True)
class Instance:
    n: int
    base: np.ndarray
    pos: np.ndarray
    neg: np.ndarray
    edge_pair_slices: list[tuple[int, int, int]]
    label: str


def blowup_edges(g6: str, t: int):
    n, edges = dec(g6)
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return n * t, out


def build_instance(info, label: str) -> Instance | None:
    n = info["n"]
    base = np.zeros(n)
    pairs: list[tuple[dict[int, float], dict[int, float]]] = []
    edge_pair_slices: list[tuple[int, int, int]] = []

    for f in info["M"]:
        lay, pf, h = layers_of(info, f)
        # fixed base contribution is the "1" in every b_{f,i}, i.e. S(v).
        for i in range(h + 1):
            for v in lay[i]:
                base[v] += float(pf[v])

        start = len(pairs)
        for i in range(h + 1):
            for j in range(i + 1, h + 1):
                pos_layer = {v: float(pf[v]) for v in lay[i]}
                neg_layer = {v: float(pf[v]) for v in lay[j]}
                pairs.append((pos_layer, neg_layer))
        edge_pair_slices.append((start, len(pairs), h + 1))

    if not pairs:
        return None

    pos = np.zeros((len(pairs), n))
    neg = np.zeros((len(pairs), n))
    for k, (pl, nl) in enumerate(pairs):
        for v, val in pl.items():
            pos[k, v] = val
        for v, val in nl.items():
            neg[k, v] = val

    return Instance(n=n, base=base, pos=pos, neg=neg, edge_pair_slices=edge_pair_slices, label=label)


def budgets(inst: Instance, x: np.ndarray) -> np.ndarray:
    ep = np.exp(x)
    em = np.exp(-x)
    return inst.base + ep @ inst.pos + em @ inst.neg


def worst_harmonic(inst: Instance, x: np.ndarray) -> float:
    ep = np.exp(x)
    em = np.exp(-x)
    worst = 0.0
    for start, end, L in inst.edge_pair_slices:
        b = np.ones(L)
        idx = start
        for i in range(L):
            for j in range(i + 1, L):
                b[i] += ep[idx]
                b[j] += em[idx]
                idx += 1
        worst = max(worst, float(np.sum(1.0 / b)))
    return worst


def solve_pcp(inst: Instance, restarts: int = 4, bound: float = 18.0):
    m = inst.pos.shape[0]
    n = inst.n
    rng = np.random.default_rng(23)

    def obj(z):
        return float(z[-1])

    def jac_obj(z):
        g = np.zeros_like(z)
        g[-1] = 1.0
        return g

    def cons_fun(z):
        x = z[:-1]
        t = z[-1]
        return t - budgets(inst, x)

    def cons_jac(z):
        x = z[:-1]
        ep = np.exp(x)
        em = np.exp(-x)
        # rows are constraints indexed by vertex.
        J = np.zeros((n, m + 1))
        # d(t-budget_v)/dx_k = -pos[k,v] e^x_k + neg[k,v] e^-x_k
        J[:, :m] = (-(ep[:, None] * inst.pos) + (em[:, None] * inst.neg)).T
        J[:, m] = 1.0
        return J

    starts = [np.zeros(m)]
    for scale in [0.2, 0.7, 1.5]:
        for _ in range(max(1, restarts // 3)):
            starts.append(rng.normal(0.0, scale, size=m))

    best = None
    for x0 in starts:
        b0 = budgets(inst, x0)
        z0 = np.concatenate([x0, [max(float(np.max(b0)), float(n))]])
        res = minimize(
            obj,
            z0,
            jac=jac_obj,
            constraints=[{"type": "ineq", "fun": cons_fun, "jac": cons_jac}],
            bounds=[(-bound, bound)] * m + [(0.0, None)],
            method="SLSQP",
            options={"maxiter": 1000, "ftol": 1e-10, "disp": False},
        )
        x = res.x[:-1]
        t = float(np.max(budgets(inst, x)))
        if best is None or t < best[0]:
            best = (t, x, res.success, res.message)
    return best


def run_label(label: str, info, restarts: int):
    inst = build_instance(info, label)
    if inst is None:
        return None
    t, x, ok, msg = solve_pcp(inst, restarts=restarts)
    wh = worst_harmonic(inst, x)
    mxv = int(np.argmax(budgets(inst, x)))
    return {
        "label": label,
        "n": inst.n,
        "pairs": inst.pos.shape[0],
        "t": t,
        "ok": ok,
        "msg": str(msg),
        "worst_harm": wh,
        "max_vertex": mxv,
        "gap": t - inst.n,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=6)
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--nmin", type=int, default=8)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()

    tests = [
        ("FCp`_", 1),
        ("H?bB@_W", 1),
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?AEB?oE?W?", 1),
        ("J???E?pNu\\?", 2),
    ]
    print("=== pairwise corridor price scout ===")
    for g6, blow in tests:
        if blow == 1:
            n, edges = dec(g6)
        else:
            n, edges = blowup_edges(g6, blow)
        info = loads(n, edges)
        if info is None:
            continue
        row = run_label(f"{g6}[{blow}]", info, args.restarts)
        if row:
            print(
                f"{row['label']:17} N={row['n']:3d} pairs={row['pairs']:4d} "
                f"t={row['t']:.9f} gap={row['gap']:+.3e} "
                f"harm={row['worst_harm']:.9f} ok={row['ok']} maxv={row['max_vertex']}",
                flush=True,
            )

    if args.census:
        for nn in range(args.nmin, args.nmax + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout.split()
            worst = None
            count = 0
            bad = 0
            for g6 in out[:: args.stride]:
                info = loads(*dec(g6))
                if info is None:
                    continue
                row = run_label(g6, info, max(2, args.restarts // 2))
                if not row:
                    continue
                count += 1
                if row["gap"] > 1e-6:
                    bad += 1
                if worst is None or row["gap"] > worst["gap"]:
                    worst = row
            print(
                f"census N={nn}: count={count} bad={bad} "
                f"worst_gap={None if worst is None else worst['gap']:+.3e} "
                f"@{None if worst is None else worst['label']}",
                flush=True,
            )


if __name__ == "__main__":
    main()
