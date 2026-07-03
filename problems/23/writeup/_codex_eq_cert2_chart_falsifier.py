#!/usr/bin/env python3
"""Exact falsifier search for EQ CERT-2 ADDENDUM 3b charts.

This is deliberately a falsifier gate, not a certificate prover. It searches
integer points in the ten min-coordinate charts

    w_k = 1,  w_i >= 1

equivalently x_k = 0, x_i >= 0 for w_i = 1 + x_i. Any reported hit is
checked with exact integer/Fraction arithmetic:

    F1..F7 >= 0, G1..G8 >= 0, and P_EQ < 0.

No floating point result is used as evidence.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import random
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import _codex_eq_cert2_odl_lp as old_lp

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_weighted_quotient_gate import EQ, b_edges, edges_of, m_edges, shortest_paths


def chart_points(chart: int, bound: int) -> Iterable[tuple[int, ...]]:
    """Enumerate x-points with x_chart=0 and other x_i in [0,bound]."""
    others = [i for i in range(10) if i != chart]

    def rec(pos: int, point: list[int]):
        if pos == len(others):
            yield tuple(point)
            return
        i = others[pos]
        for value in range(bound + 1):
            point[i] = value
            yield from rec(pos + 1, point)
        point[i] = 0

    yield from rec(0, [0] * 10)


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


@lru_cache(maxsize=1)
def eq_paths_by_bad():
    n, edges = edges_of(EQ)
    side = tuple(int(c) for c in old_lp.SIDE)
    bset = b_edges(edges, side)
    bad = sorted(m_edges(edges, side))
    if n != 10 or bad != [(1, 9), (2, 7), (7, 9)]:
        raise RuntimeError(f"unexpected EQ data: n={n} bad={bad}")
    return {edge: shortest_paths(n, bset, edge[0], edge[1]) for edge in bad}


def numeric_d_eq(w: list[int]) -> int:
    a = w[0] * w[6] + w[4] * w[8] + w[6] * w[8]
    b = w[0] * w[5] + w[3] * w[8] + w[5] * w[8]
    c = (
        w[0] * w[5] * w[6]
        + w[3] * w[4] * w[8]
        + w[3] * w[6] * w[8]
        + w[4] * w[5] * w[8]
        + w[5] * w[6] * w[8]
    )
    return w[5] * w[6] * a * b * c


def numeric_row_overlap(w: list[int]) -> Fraction:
    row_set = set(old_lp.ACTIVE_ROW)
    total = Fraction(0)
    paths_by_bad = eq_paths_by_bad()
    for a, b in sorted(paths_by_bad):
        paths = paths_by_bad[(a, b)]
        denom = 0
        inner = Fraction(0)
        for path in paths:
            wp = 1
            for v in path[1:-1]:
                wp *= w[v]
            denom += wp
            for v in path[1:-1]:
                if v in row_set:
                    inner += Fraction(wp, w[v])
        endpoint = 0
        if a in row_set:
            endpoint += w[b]
        if b in row_set:
            endpoint += w[a]
        total += endpoint + Fraction(w[a] * w[b], denom) * inner
    return total


def p_eq_numeric(point: tuple[int, ...]) -> int:
    w = point_weights(point)
    n_val = sum(w)
    m_val = w[1] * w[9] + w[2] * w[7] + w[7] * w[9]
    eta25_val = n_val * n_val - 25 * m_val
    value = numeric_d_eq(w) * (2 * eta25_val - 75 * (numeric_row_overlap(w) - n_val))
    if value.denominator != 1:
        raise ArithmeticError(f"uncleared P_EQ denominator at {point}: {value}")
    return value.numerator


def fg_numeric(point: tuple[int, ...]) -> tuple[list[int], list[int]]:
    w = point_weights(point)
    m_val = w[1] * w[9] + w[2] * w[7] + w[7] * w[9]
    n_val = sum(w)
    eta25_val = n_val * n_val - 25 * m_val
    u_val = w[0] + w[8]
    v_val = w[4] + w[6]
    x_val = w[1] + w[7]
    y_val = w[2] + w[9]
    z_val = w[3] + w[5]
    t_val = m_val + 1
    a_val = u_val + v_val + z_val
    b_val = x_val + y_val
    f_vals = [
        w[5] - w[9],
        w[6] - w[7],
        w[3] + w[5] - w[2] - w[9],
        w[4] + w[6] - w[1] - w[7],
        w[0] * w[6] + w[3] * w[8] + w[5] * w[8] - m_val,
        w[0] * w[5] + w[3] * w[8] + w[5] * w[8] - m_val,
        w[0] * w[6] + w[4] * w[8] + w[6] * w[8] - m_val,
    ]
    g_vals = [
        u_val * v_val - t_val,
        u_val * z_val - t_val,
        v_val * z_val - t_val,
        x_val * y_val - t_val,
        v_val * z_val - x_val * y_val,
        a_val * a_val - 9 * t_val,
        b_val * b_val - 4 * t_val,
        eta25_val - 25,
    ]
    return f_vals, g_vals


def search(points: Iterable[tuple[int, ...]], best: dict[str, object] | None = None):
    checked = 0
    feasible = 0
    best_val = None if best is None else int(best["P_EQ"])
    best_point = None if best is None else tuple(best["x"])
    hit = None

    for point in points:
        checked += 1
        f_vals, g_vals = fg_numeric(point)
        if min(f_vals) < 0:
            continue
        if min(g_vals) < 0:
            continue
        feasible += 1
        p_val = p_eq_numeric(point)
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
    ap.add_argument("--summary", default="tmp/eq_cert2_chart_falsifier_v2.json")
    args = ap.parse_args()

    charts = [int(x) for x in args.charts.split(",") if x.strip()]
    out = {
        "schema": "eq_cert2_add3b_chart_falsifier_v2",
        "mode": "integer_points_exact_direct_row_overlap",
        "bound": args.bound,
        "random_bound": args.random_bound,
        "random_samples_per_chart": args.random_samples,
        "seed": args.seed,
        "target_meta": {
            "graph": EQ,
            "side": old_lp.SIDE,
            "active_row": list(old_lp.ACTIVE_ROW),
            "bad_edges": [list(e) for e in sorted(eq_paths_by_bad())],
            "eval": "direct exact Fraction row-overlap, cleared by D_EQ",
        },
        "generators": {
            "F": [str(f) for f in old_lp.F],
            "G_order": [
                "UV-T",
                "UZ-T",
                "VZ-T",
                "XY-T",
                "VZ-XY",
                "A^2-9T",
                "B^2-4T",
                "eta25-25",
            ],
        },
        "charts": [],
        "hit": None,
    }

    for chart in charts:
        exhaustive = search(chart_points(chart, args.bound))
        combined_best = exhaustive["best"]
        random_result = None
        if exhaustive["hit"] is None and args.random_samples > 0:
            random_result = search(
                random_chart_points(chart, args.random_bound, args.random_samples, args.seed),
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
        print(
            "chart",
            chart,
            "checked",
            exhaustive["checked"],
            "feasible",
            exhaustive["feasible"],
            "hit",
            bool(hit),
            flush=True,
        )
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
