"""Codex KKT-support probe for the LPD/CORR optimizer.

This is a numerical structure/falsification tool, not a certificate.

For a connected-B triangle-free max-cut configuration, maximize

    L(y) = sum_f (sum_i sqrt(w_{f,i}))^2,  sum_v y_v = 1, y >= 0,

where w_{f,i}=sum_{v in I_i(f)} y_v p_f(v).  The script compares the
global optimum against optima restricted to supports of one or two bad-edge
geodesic intervals, and checks whether overloaded vertices T(v)>N occur in
the optimizer support.

The motivation is KKT-core exclusion: if two bad-edge intervals always carry
an optimum, the remaining proof target becomes much smaller than arbitrary
mixed y.
"""

from __future__ import annotations

import argparse
import itertools
import math
import subprocess
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from _h import GENG, dec, loads
from _layerprice import layers_of


@dataclass
class EdgeTerm:
    edge: tuple[int, int]
    layers: list[list[tuple[int, float]]]
    support: frozenset[int]


def build_terms(info) -> list[EdgeTerm]:
    out: list[EdgeTerm] = []
    for f in info["M"]:
        lay, pf, h = layers_of(info, f)
        layers = [[(v, float(pf[v])) for v in lay[i]] for i in range(h + 1)]
        out.append(EdgeTerm(f, layers, frozenset(pf)))
    return out


def value_grad(y: np.ndarray, terms: list[EdgeTerm], n: int) -> tuple[float, np.ndarray]:
    val = 0.0
    grad = np.zeros(n)
    for term in terms:
        w = np.array([sum(y[v] * p for v, p in layer) for layer in term.layers])
        sq_true = np.sqrt(np.maximum(w, 0.0))
        sq = np.sqrt(np.maximum(w, 1e-13))
        a_true = float(np.sum(sq_true))
        a = float(np.sum(sq))
        val += a_true * a_true
        for wi, layer in zip(w, term.layers):
            coeff = a / math.sqrt(max(float(wi), 1e-13))
            for v, p in layer:
                grad[v] += coeff * p
    return val, grad


def optimize_on_support(info, terms: list[EdgeTerm], support: set[int] | frozenset[int] | None):
    n = info["n"]
    allowed = list(range(n)) if support is None else sorted(support)
    m = len(allowed)
    if m == 0:
        return -math.inf, np.zeros(n), np.zeros(n)

    allowed_arr = np.array(allowed, dtype=int)

    def expand(z: np.ndarray) -> np.ndarray:
        y = np.zeros(n)
        y[allowed_arr] = z
        return y

    def obj(z: np.ndarray) -> float:
        return -value_grad(expand(z), terms, n)[0]

    def jac(z: np.ndarray) -> np.ndarray:
        return -value_grad(expand(z), terms, n)[1][allowed_arr]

    constraints = {"type": "eq", "fun": lambda z: float(np.sum(z) - 1.0), "jac": lambda z: np.ones(m)}
    bounds = [(0.0, 1.0)] * m

    starts: list[np.ndarray] = [np.full(m, 1.0 / m)]
    for k in range(m):
        z = np.zeros(m)
        z[k] = 1.0
        starts.append(z)
    for v, tv in enumerate(info["T"]):
        if float(tv) > n and v in allowed:
            z = np.zeros(m)
            z[allowed.index(v)] = 1.0
            starts.append(z)

    best = (-math.inf, np.zeros(n), np.zeros(n))
    for x0 in starts:
        res = minimize(
            obj,
            x0,
            jac=jac,
            constraints=constraints,
            bounds=bounds,
            method="SLSQP",
            options={"maxiter": 500, "ftol": 1e-11, "disp": False},
        )
        if (not res.success) or abs(float(np.sum(res.x)) - 1.0) > 1e-7:
            continue
        if np.min(res.x) < -1e-7 or np.max(res.x) > 1.0 + 1e-7:
            continue
        z = np.clip(res.x, 0.0, 1.0)
        z_sum = float(np.sum(z))
        if z_sum <= 0:
            continue
        z = z / z_sum
        y = expand(z)
        val, grad = value_grad(y, terms, n)
        if val > best[0]:
            best = (val, y, grad)
    return best


def analyze_graph(g6: str, two_interval_limit: int):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return None
    terms = build_terms(info)
    if not terms:
        return None

    global_val, y, grad = optimize_on_support(info, terms, None)

    best1 = -math.inf
    best1_edge = None
    for term in terms:
        val, _, _ = optimize_on_support(info, terms, term.support)
        if val > best1:
            best1 = val
            best1_edge = term.edge

    best2 = best1
    best2_pair = (best1_edge, best1_edge)
    if len(terms) >= 2 and len(terms) <= two_interval_limit:
        for a, b in itertools.combinations(range(len(terms)), 2):
            supp = terms[a].support | terms[b].support
            val, _, _ = optimize_on_support(info, terms, supp)
            if val > best2:
                best2 = val
                best2_pair = (terms[a].edge, terms[b].edge)

    overloaded = [v for v, tv in enumerate(info["T"]) if float(tv) > n + 1e-9]
    overload_missing = [v for v in overloaded if y[v] < 1e-7]
    support = [v for v, yy in enumerate(y) if yy > 1e-7]

    return {
        "g6": g6,
        "n": n,
        "bad_edges": len(terms),
        "gamma": info["G"],
        "global": global_val,
        "best1": best1,
        "gap1": global_val - best1,
        "best1_edge": best1_edge,
        "best2": best2,
        "gap2": global_val - best2,
        "best2_pair": best2_pair,
        "overloaded": overloaded,
        "overload_missing": overload_missing,
        "support": support,
        "lambda_support_min": min((grad[v] for v in support), default=float("nan")),
        "lambda_support_max": max((grad[v] for v in support), default=float("nan")),
    }


def geng_graphs(n: int) -> list[str]:
    out = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True, check=True).stdout.split()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0, help="per-n graph limit; 0 means all")
    ap.add_argument("--two-interval-limit", type=int, default=10, help="skip pair search if #bad edges exceeds this")
    args = ap.parse_args()

    for n in range(args.nmin, args.nmax + 1):
        graphs = geng_graphs(n)
        if args.limit:
            graphs = graphs[: args.limit]
        jobs = [(g, args.two_interval_limit) for g in graphs]
        if args.workers > 1:
            with Pool(processes=args.workers) as pool:
                rows = list(pool.starmap(analyze_graph, jobs))
        else:
            rows = [analyze_graph(*job) for job in jobs]
        rows = [r for r in rows if r is not None]

        one_fail = [r for r in rows if r["gap1"] > 1e-6]
        two_fail = [r for r in rows if r["gap2"] > 1e-6]
        over_fail = [r for r in rows if r["overload_missing"]]
        worst1 = max(rows, key=lambda r: r["gap1"], default=None)
        worst2 = max(rows, key=lambda r: r["gap2"], default=None)
        print(
            f"N={n}: cfg={len(rows)} | one-interval fails={len(one_fail)} "
            f"| two-interval fails={len(two_fail)} | overload-support fails={len(over_fail)}",
            flush=True,
        )
        if worst1:
            print(
                f"  worst1 gap={worst1['gap1']:.9g} @{worst1['g6']} "
                f"global={worst1['global']:.9g} best1={worst1['best1']:.9g} edge={worst1['best1_edge']}",
                flush=True,
            )
        if worst2:
            print(
                f"  worst2 gap={worst2['gap2']:.9g} @{worst2['g6']} "
                f"global={worst2['global']:.9g} best2={worst2['best2']:.9g} pair={worst2['best2_pair']}",
                flush=True,
            )
        if over_fail[:1]:
            print(f"  overload-support witness={over_fail[0]}", flush=True)


if __name__ == "__main__":
    main()
