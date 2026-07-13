#!/usr/bin/env python3
"""Audit the zero-wrap tetrahedron Fourier kernel used in P27.

The proof is analytic.  This script checks its exact identities, signs, wrap
bookkeeping, confluent divided-difference formulas, and sample Wiener norms.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path

import numpy as np


def complete_homogeneous(nodes: list[complex], degree: int) -> complex:
    """Return h_degree(nodes) from prod_i (1-nodes[i] t)^(-1)."""
    coeff = np.zeros(degree + 1, dtype=np.complex128)
    coeff[0] = 1.0
    for node in nodes:
        for j in range(1, degree + 1):
            coeff[j] += node * coeff[j - 1]
    return complex(coeff[degree])


def tetrahedron(v: int, d: int) -> np.ndarray:
    axis = np.arange(v)
    return (
        axis[:, None, None] + axis[None, :, None] + axis[None, None, :] < d
    ).astype(np.float64)


def partition_norms(kernel: np.ndarray) -> dict[str, float]:
    v = kernel.shape[0]
    axis = np.arange(v)
    r = axis[:, None, None]
    s = axis[None, :, None]
    t = axis[None, None, :]

    rz = r == 0
    sz = s == 0
    tz = t == 0
    zero_count = rz.astype(np.int8) + sz.astype(np.int8) + tz.astype(np.int8)
    all_nonzero = (r != 0) & (s != 0) & (t != 0)
    rs = r == s
    rt = r == t
    st = s == t

    masks = {
        "4": rz & sz & tz,
        "3+1": (zero_count == 2) | (all_nonzero & rs & rt),
        "2+2": (zero_count == 1) & (rs | rt | st),
        "2+1+1": ((zero_count == 1) & ~(rs | rt | st))
        | (all_nonzero & ((rs & ~rt) | (rt & ~rs) | (st & ~rs))),
        "1+1+1+1": all_nonzero & ~rs & ~rt & ~st,
    }

    covered = np.zeros(kernel.shape, dtype=np.int8)
    for mask in masks.values():
        covered += mask.astype(np.int8)
    if not np.all(covered == 1):
        raise AssertionError("coincidence masks do not partition frequency space")

    scale = float(v**3)
    absolute = np.abs(kernel)
    return {name: float(absolute[mask].sum() / scale) for name, mask in masks.items()}


def distinct_formula(nodes: list[complex], exponent: int) -> complex:
    total = 0.0j
    for i, node in enumerate(nodes):
        denominator = 1.0 + 0.0j
        for j, other in enumerate(nodes):
            if i != j:
                denominator *= node - other
        total += node**exponent / denominator
    return total


def hermite_211(a: complex, b: complex, c: complex, n: int) -> complex:
    repeated = (
        n * a ** (n - 1) / ((a - b) * (a - c))
        - a**n / ((a - b) ** 2 * (a - c))
        - a**n / ((a - b) * (a - c) ** 2)
    )
    at_b = b**n / ((b - a) ** 2 * (b - c))
    at_c = c**n / ((c - a) ** 2 * (c - b))
    return repeated + at_b + at_c


def hermite_22(a: complex, b: complex, n: int) -> complex:
    at_a = n * a ** (n - 1) / (a - b) ** 2 - 2 * a**n / (a - b) ** 3
    at_b = n * b ** (n - 1) / (b - a) ** 2 - 2 * b**n / (b - a) ** 3
    return at_a + at_b


def hermite_31(a: complex, b: complex, n: int) -> complex:
    repeated = 0.5 * (
        n * (n - 1) * a ** (n - 2) / (a - b)
        - 2 * n * a ** (n - 1) / (a - b) ** 2
        + 2 * a**n / (a - b) ** 3
    )
    return repeated + b**n / (b - a) ** 3


def audit_wraps() -> dict[str, int]:
    tested = 0
    for v in (5, 7, 11):
        for d in range(1, v):
            for x in range(v):
                for y in range(v):
                    for z in range(v):
                        total = x + y + z
                        cyclic = int(total % v < d)
                        lanes = sum(
                            int(j * v <= total < j * v + d) for j in range(3)
                        )
                        if cyclic != lanes:
                            raise AssertionError((v, d, x, y, z, cyclic, lanes))
                        tested += 1
    return {"pointwise_cases": tested}


def audit_kernel_identities() -> dict[str, float | int]:
    max_fft_h = 0.0
    max_distinct = 0.0
    tested_fft_h = 0
    tested_distinct = 0
    for v in (7, 11):
        roots = np.exp(-2j * np.pi * np.arange(v) / v)
        for d in range(1, v):
            kernel = np.fft.fftn(tetrahedron(v, d))
            for r in range(v):
                for s in range(v):
                    for t in range(v):
                        nodes = [1.0 + 0.0j, roots[r], roots[s], roots[t]]
                        h_value = complete_homogeneous(nodes, d - 1)
                        max_fft_h = max(max_fft_h, abs(kernel[r, s, t] - h_value))
                        tested_fft_h += 1
                        if len({0, r, s, t}) == 4:
                            closed = distinct_formula(nodes, d + 2)
                            max_distinct = max(max_distinct, abs(h_value - closed))
                            tested_distinct += 1
    return {
        "fft_vs_complete_homogeneous_cases": tested_fft_h,
        "fft_vs_complete_homogeneous_max_abs_error": max_fft_h,
        "distinct_formula_cases": tested_distinct,
        "distinct_formula_max_abs_error": max_distinct,
    }


def audit_hermite_formulas() -> dict[str, float | int]:
    v = 17
    roots = np.exp(-2j * np.pi * np.arange(v) / v)
    maxima = {"2+1+1": 0.0, "2+2": 0.0, "3+1": 0.0}
    counts = {name: 0 for name in maxima}
    for d in range(1, v):
        n = d + 2
        degree = d - 1
        for a_idx in range(v):
            for b_idx in range(v):
                if b_idx == a_idx:
                    continue
                a, b = roots[a_idx], roots[b_idx]
                actual_22 = complete_homogeneous([a, a, b, b], degree)
                maxima["2+2"] = max(maxima["2+2"], abs(actual_22 - hermite_22(a, b, n)))
                counts["2+2"] += 1

                actual_31 = complete_homogeneous([a, a, a, b], degree)
                maxima["3+1"] = max(maxima["3+1"], abs(actual_31 - hermite_31(a, b, n)))
                counts["3+1"] += 1

                for c_idx in range(v):
                    if c_idx in (a_idx, b_idx):
                        continue
                    c = roots[c_idx]
                    actual_211 = complete_homogeneous([a, a, b, c], degree)
                    maxima["2+1+1"] = max(
                        maxima["2+1+1"],
                        abs(actual_211 - hermite_211(a, b, c, n)),
                    )
                    counts["2+1+1"] += 1
    return {
        name: {"cases": counts[name], "max_abs_error": maxima[name]}
        for name in maxima
    }


def norm_record(v: int, d: int) -> dict[str, object]:
    kernel = np.fft.fftn(tetrahedron(v, d))
    parts = partition_norms(kernel)
    total = float(np.abs(kernel).sum() / v**3)
    if abs(total - sum(parts.values())) > 2e-10 * max(1.0, total):
        raise AssertionError("partition norms do not sum to the Wiener norm")
    return {
        "v": v,
        "d": d,
        "d_over_v": d / v,
        "normalized_wiener_norm": total,
        "partition_contributions": parts,
        "norm_over_log_cubed_2v": total / math.log(2 * v) ** 3,
    }


def audit_norms() -> dict[str, object]:
    samples = [norm_record(v, 3 * v // 4) for v in (17, 31, 61, 101)]
    all_d_v17 = [norm_record(17, d) for d in range(1, 17)]
    maximum = max(all_d_v17, key=lambda record: record["normalized_wiener_norm"])
    return {
        "three_quarter_samples": samples,
        "all_d_v17_maximum": maximum,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("tetrahedron_wiener_audit.json"),
    )
    args = parser.parse_args()

    result = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "wrap_decomposition": audit_wraps(),
        "kernel_identities": audit_kernel_identities(),
        "hermite_formulas": audit_hermite_formulas(),
        "wiener_norms": audit_norms(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
