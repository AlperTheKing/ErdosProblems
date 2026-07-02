"""Exact hard-case diagnostics for the seven-cut OC-PMS atom.

This script is exploratory only: it does not certify the theorem.  It scans
integer weights satisfying the seven quotient inequalities and reports the
cases where the shifted coefficient reservoirs barely cover the crude
coefficient-cap deficit.
"""

from __future__ import annotations

import argparse
import heapq
from fractions import Fraction as F
from itertools import product

import _codex_ocpms_sevencut_gate as gate


def coeff_parts(w: tuple[int, ...]):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w

    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    a27 = (
        w0 * w5
        + w0 * w6
        + w3 * w6
        + w3 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    a19 = (
        w0 * w5
        + w0 * w6
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )
    z79 = (
        w0 * w5 * w6
        + w3 * w4 * w8
        + w3 * w6 * w8
        + w4 * w5 * w8
        + w5 * w6 * w8
    )
    a79 = (
        w0 * w5
        + w0 * w6
        + w3 * w4
        + w3 * w6
        + w3 * w8
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )

    c27 = F(a27, z27)
    c19 = F(a19, z19)
    c79 = F(a79, z79)

    x, y, u, v = w1, w2, w7, w9
    core = w0 + w3 + w4 + w5 + w6 + w8
    s = x + y + u + v
    f0 = 2 * (core + s) ** 2 + 75 * core - 225 * x * v - 225 * y * u - 200 * u * v
    r19 = 75 * (F(7, 3) - c19) * x * v
    r27 = 75 * (F(7, 3) - c27) * y * u
    r79 = 75 * (F(2, 1) - c79) * u * v
    return {
        "f0": F(f0, 1),
        "r19": r19,
        "r27": r27,
        "r79": r79,
        "reservoir": r19 + r27 + r79,
        "margin": F(f0, 1) + r19 + r27 + r79,
        "c19": c19,
        "c27": c27,
        "c79": c79,
    }


def active_constraints(w: tuple[int, ...]) -> list[str]:
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    m = w1 * w9 + w2 * w7 + w7 * w9
    checks = [
        ("w5=w9", w5 == w9),
        ("w6=w7", w6 == w7),
        ("w3+w5=w2+w9", w3 + w5 == w2 + w9),
        ("w4+w6=w1+w7", w4 + w6 == w1 + w7),
        ("D27=m", w0 * w6 + w3 * w8 + w5 * w8 == m),
        ("D0=m", w0 * w5 + w3 * w8 + w5 * w8 == m),
        ("D19=m", w0 * w6 + w4 * w8 + w6 * w8 == m),
    ]
    return [name for name, ok in checks if ok]


def scan(max_weight: int, keep: int):
    selected = 0
    crude_neg = 0
    heap: list[tuple[F, int, tuple[int, ...], dict, list[str]]] = []
    for idx, w in enumerate(product(range(1, max_weight + 1), repeat=10)):
        if not gate.selected_ok(w):
            continue
        selected += 1
        parts = coeff_parts(w)
        if parts["f0"] >= 0:
            continue
        crude_neg += 1
        ratio = parts["reservoir"] / (-parts["f0"])
        item = (-ratio, idx, w, parts, active_constraints(w))
        if len(heap) < keep:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    rows = sorted([(-r, idx, w, p, a) for r, idx, w, p, a in heap])
    return selected, crude_neg, rows


def fmt(fr: F) -> str:
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-weight", type=int, default=5)
    parser.add_argument("--keep", type=int, default=20)
    args = parser.parse_args()

    selected, crude_neg, rows = scan(args.max_weight, args.keep)
    print("max_weight", args.max_weight, "selected", selected, "crude_neg", crude_neg)
    for rank, (ratio, _idx, w, parts, active) in enumerate(rows, 1):
        print("rank", rank)
        print("  w", w)
        print("  active", ",".join(active) if active else "-")
        print(
            "  ratio",
            fmt(ratio),
            "f0",
            fmt(parts["f0"]),
            "reservoir",
            fmt(parts["reservoir"]),
            "margin",
            fmt(parts["margin"]),
        )
        print(
            "  r19",
            fmt(parts["r19"]),
            "r27",
            fmt(parts["r27"]),
            "r79",
            fmt(parts["r79"]),
        )
        print("  coeffs", fmt(parts["c19"]), fmt(parts["c27"]), fmt(parts["c79"]))


if __name__ == "__main__":
    main()
