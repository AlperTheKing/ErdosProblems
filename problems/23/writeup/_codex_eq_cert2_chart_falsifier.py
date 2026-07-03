#!/usr/bin/env python3
"""Exact falsifier search for EQ CERT-2 ADDENDUM 3b charts.

This is deliberately a falsifier gate, not a certificate prover.  It searches
integer points in the ten min-coordinate charts

    w_k = 1,  w_i >= 1

equivalently x_k = 0, x_i >= 0 for w_i = 1 + x_i.  Any reported hit is
checked with exact integer polynomial arithmetic:

    F1..F7 >= 0, G1..G8 >= 0, and P_EQ < 0.

No floating point result is used as evidence.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path
from typing import Iterable

import sympy as sp

import _codex_eq_cert2_odl_lp as old_lp


xs = old_lp.xs
ws = old_lp.ws
w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = ws

m = old_lp.m
N = old_lp.N
eta25 = old_lp.eta25
F = old_lp.F

U = w0 + w8
V = w4 + w6
X = w1 + w7
Y = w2 + w9
Z = w3 + w5
T = m + 1
A = U + V + Z
B = X + Y

G = [
    U * V - T,
    U * Z - T,
    V * Z - T,
    X * Y - T,
    V * Z - X * Y,
    A * A - 9 * T,
    B * B - 4 * T,
    eta25 - 25,
]


def make_int_func(expr: sp.Expr):
    """Return a Python-int evaluator for an integer polynomial."""
    poly = sp.Poly(sp.expand(expr), *xs, domain=sp.ZZ)
    terms = [(tuple(mon), int(coeff)) for mon, coeff in poly.terms()]

    def eval_at(point: tuple[int, ...]) -> int:
        total = 0
        for mon, coeff in terms:
            val = coeff
            for idx, power in enumerate(mon):
                if power:
                    val *= point[idx] ** power
            total += val
        return total

    return eval_at


def chart_points(chart: int, bound: int) -> Iterable[tuple[int, ...]]:
    """Enumerate x-points with x_chart=0 and other x_i in [0,bound]."""
    others = [i for i in range(10) if i != chart]
    for vals in itertools.product(range(bound + 1), repeat=9):
        point = [0] * 10
        for i, value in zip(others, vals):
            point[i] = value
        yield tuple(point)


def random_chart_points(chart: int, bound: int, samples: int, seed: int) -> Iterable[tuple[int, ...]]:
    rng = random.Random(seed + 1009 * chart)
    others = [i for i in range(10) if i != chart]
    for _ in range(samples):
        point = [0] * 10
        for i in others:
            # Bias toward the seed faces while still touching the outer box.
            if rng.random() < 0.55:
                point[i] = rng.randrange(min(bound, 3) + 1)
            else:
                point[i] = rng.randrange(bound + 1)
        yield tuple(point)


def point_weights(point: tuple[int, ...]) -> list[int]:
    return [1 + x for x in point]


def search(points: Iterable[tuple[int, ...]], evals, best: dict[str, object] | None = None):
    p_eval, f_evals, g_evals = evals
    checked = 0
    feasible = 0
    best_val = None if best is None else int(best["P_EQ"])
    best_point = None if best is None else tuple(best["x"])
    hit = None

    for point in points:
        checked += 1
        f_vals = [fn(point) for fn in f_evals]
        if min(f_vals) < 0:
            continue
        g_vals = [fn(point) for fn in g_evals]
        if min(g_vals) < 0:
            continue
        feasible += 1
        p_val = p_eval(point)
        if best_val is None or p_val < best_val:
            best_val = p_val
            best_point = point
        if p_val < 0:
            hit = {
                "x": list(point),
                "w": point_weights(point),
                "P_EQ": str(p_val),
                "F": [str(v) for v in f_vals],
                "G": [str(v) for v in g_vals],
            }
            break

    return {
        "checked": checked,
        "feasible": feasible,
        "best": None
        if best_val is None
        else {
            "x": list(best_point),
            "w": point_weights(best_point),
            "P_EQ": str(best_val),
        },
        "hit": hit,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bound", type=int, default=3, help="exhaustive box bound for x variables")
    ap.add_argument("--random-bound", type=int, default=20, help="random box bound for x variables")
    ap.add_argument("--random-samples", type=int, default=0, help="random samples per chart")
    ap.add_argument("--seed", type=int, default=1729)
    ap.add_argument("--charts", default="0,1,2,3,4,5,6,7,8,9")
    ap.add_argument("--summary", default="tmp/eq_cert2_chart_falsifier_v1.json")
    args = ap.parse_args()

    target, meta = old_lp.build_target()
    evals = (
        make_int_func(target),
        [make_int_func(f) for f in F],
        [make_int_func(g) for g in G],
    )

    charts = [int(x) for x in args.charts.split(",") if x.strip()]
    out = {
        "schema": "eq_cert2_add3b_chart_falsifier_v1",
        "mode": "integer_points_exact",
        "bound": args.bound,
        "random_bound": args.random_bound,
        "random_samples_per_chart": args.random_samples,
        "seed": args.seed,
        "target_meta": meta,
        "generators": {
            "F": [str(f) for f in F],
            "G": [str(g) for g in G],
        },
        "charts": [],
        "hit": None,
    }

    for chart in charts:
        exhaustive = search(chart_points(chart, args.bound), evals)
        combined_best = exhaustive["best"]
        random_result = None
        if exhaustive["hit"] is None and args.random_samples > 0:
            random_result = search(
                random_chart_points(chart, args.random_bound, args.random_samples, args.seed),
                evals,
                combined_best,
            )
        hit = exhaustive["hit"] or (random_result or {}).get("hit")
        chart_out = {
            "chart": chart,
            "exhaustive": exhaustive,
            "random": random_result,
            "hit": hit,
        }
        out["charts"].append(chart_out)
        if hit is not None:
            out["hit"] = {"chart": chart, **hit}
            break

    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    if out["hit"] is not None:
        print("FAIL CERT-2 chart falsifier found", args.summary)
        raise SystemExit(1)
    print("PASS no integer chart falsifier found", args.summary)


if __name__ == "__main__":
    main()
