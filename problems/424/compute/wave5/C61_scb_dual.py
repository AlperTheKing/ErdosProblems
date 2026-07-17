#!/usr/bin/env python3
"""Discover sparse integer dual certificates for finite SCB instances.

Floating-point HiGHS output is used only to locate candidate integer
multipliers.  Acceptance is delegated to the independent integer-only script
C61_scb_verify.py.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from array import array
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pair_iter(limit: int):
    for a in range(2, math.isqrt(limit + 1) + 1):
        if not allowed(a):
            continue
        for b in range(a + 1, (limit + 1) // a + 1):
            if allowed(b):
                yield a * b - 1, a, b


def round_integer_vector(vector, tolerance: float, label: str):
    rounded = np.rint(np.asarray(vector, dtype=float)).astype(np.int64)
    error = float(np.max(np.abs(np.asarray(vector, dtype=float) - rounded))) if len(rounded) else 0.0
    if error > tolerance:
        raise RuntimeError(f"{label} dual is not integral: maximum error {error}")
    return rounded, error


def generate(limit: int, tolerance: float) -> dict:
    started = time.perf_counter()
    values = [n for n in range(2, limit + 1) if allowed(n)]
    col = array("i", [-1]) * (limit + 1)
    for j, n in enumerate(values):
        col[n] = j

    pair_count = array("I", [0]) * (limit + 1)
    total_pairs = 0
    for n, _, _ in pair_iter(limit):
        pair_count[n] += 1
        total_pairs += 1

    hard = []
    splitless = []
    for n in values:
        if n not in (2, 3) and pair_count[n] == 0:
            splitless.append(n)
        if n % 2 or pair_count[n] == 0:
            continue
        if (n + 1) % 3:
            hard.append(n)
        else:
            parent = (n + 1) // 3
            if not (allowed(parent) and parent != 3):
                hard.append(n)

    rows = np.repeat(np.arange(total_pairs, dtype=np.int32), 3)
    cols = np.empty(3 * total_pairs, dtype=np.int32)
    data = np.empty(3 * total_pairs, dtype=np.int8)
    row_n = np.empty(total_pairs, dtype=np.int32)
    row_a = np.empty(total_pairs, dtype=np.int32)
    row_b = np.empty(total_pairs, dtype=np.int32)
    for i, (n, a, b) in enumerate(pair_iter(limit)):
        base = 3 * i
        cols[base:base + 3] = (col[a], col[b], col[n])
        data[base:base + 3] = (1, 1, -1)
        row_n[i], row_a[i], row_b[i] = n, a, b
    matrix = coo_matrix(
        (data, (rows, cols)), shape=(total_pairs, len(values)), dtype=float
    ).tocsr()

    objective = np.zeros(len(values), dtype=float)
    for n in hard:
        objective[col[n]] += 1.0
    seed2_edges = 0
    for m in values:
        child = 2 * m - 1
        if child > limit:
            continue
        seed2_edges += 1
        objective[col[child]] += 1.0
        objective[col[m]] -= 1.0

    splitless_set = set(splitless)
    bounds = []
    for n in values:
        if n in (2, 3):
            bounds.append((1.0, 1.0))
        elif n in splitless_set:
            bounds.append((0.0, 0.0))
        else:
            bounds.append((0.0, 1.0))

    result = linprog(
        objective,
        A_ub=matrix,
        b_ub=np.ones(total_pairs, dtype=float),
        bounds=bounds,
        method="highs",
        options={"presolve": True},
    )
    if not result.success:
        raise RuntimeError(result.message)

    row_dual, row_error = round_integer_vector(result.ineqlin.marginals, tolerance, "row")
    lower_dual, lower_error = round_integer_vector(result.lower.marginals, tolerance, "lower")
    upper_dual, upper_error = round_integer_vector(result.upper.marginals, tolerance, "upper")

    nz_rows = np.flatnonzero(row_dual)
    nz_lower = np.flatnonzero(lower_dual)
    nz_upper = np.flatnonzero(upper_dual)
    cert = {
        "format": "C61_SCB_REDUCED_DUAL_V1",
        "limit": limit,
        "hard_count": len(hard),
        "splitless_count": len(splitless),
        "value_count": len(values),
        "pair_count": total_pairs,
        "seed2_edges": seed2_edges,
        "floating_objective": float(result.fun),
        "max_rounding_error": max(row_error, lower_error, upper_error),
        "wall_seconds": time.perf_counter() - started,
        "row": [
            [int(row_n[i]), int(row_a[i]), int(row_b[i]), int(row_dual[i])]
            for i in nz_rows
        ],
        "lower": [[int(values[i]), int(lower_dual[i])] for i in nz_lower],
        "upper": [[int(values[i]), int(upper_dual[i])] for i in nz_upper],
    }
    return cert


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=1e-7)
    args = parser.parse_args()
    certs = [generate(limit, args.tolerance) for limit in args.limits]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certs, separators=(",", ":")) + "\n", encoding="utf-8")

    verifier = Path(__file__).with_name("C61_scb_verify.py")
    command = [
        sys.executable, "-O", str(verifier), "--certificate", str(args.output),
        "--summary", str(args.summary),
    ]
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(
            f"independent verifier failed ({completed.returncode}):\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
    print(completed.stdout, end="")


if __name__ == "__main__":
    main()
