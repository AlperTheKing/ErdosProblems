"""Finite audit for the P35 simplex Fourier-algebra decomposition."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def harmonic(n: int) -> float:
    return sum(1.0 / k for k in range(1, n + 1))


def algebra_norm(values: np.ndarray) -> float:
    return float(np.sum(np.abs(np.fft.fftn(values))) / values.size)


def ordered_piece(a: int, b: int, c: int, d: int, v: int) -> int:
    """Evaluate the exact four-piece decomposition of 0 <= a <= b <= c < d."""
    if not (0 <= a < d and 0 <= b < d and 0 <= c < d):
        return 0

    split = (d + 1) // 2
    blocks = (int(a >= split), int(b >= split), int(c >= split))
    if blocks not in ((0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1)):
        return 0

    lengths = (split, d - split)
    if blocks[0] == blocks[1] and (b - a) % v >= lengths[blocks[0]]:
        return 0
    if blocks[1] == blocks[2] and (c - b) % v >= lengths[blocks[1]]:
        return 0
    return 1


def audit_modulus(v: int) -> dict[str, object]:
    if v < 3 or v % 2 == 0:
        raise ValueError("v must be odd and at least 3")

    grid = np.arange(v)
    x = grid[:, None, None]
    y = grid[None, :, None]
    z = grid[None, None, :]
    diagonal = (x == y).astype(np.float64) + np.zeros((1, 1, v))
    delta_norm = algebra_norm(diagonal)

    h_n = harmonic((v - 1) // 2)
    interval_bound = 1.0 + h_n
    max_interval_norm = 0.0
    max_tetrahedron_ratio = 0.0
    max_diagonal_ratio = 0.0
    max_diagonal_over_tetrahedron = 0.0
    witnesses: dict[str, object] = {}

    for length in range(v + 1):
        interval = np.zeros(v, dtype=np.float64)
        interval[:length] = 1.0
        norm = algebra_norm(interval)
        max_interval_norm = max(max_interval_norm, norm)
        if norm > interval_bound + 1e-10:
            raise AssertionError(("interval norm", v, length, norm, interval_bound))

    for d in range(v):
        tetrahedron = (x + y + z < d).astype(np.float64)
        decomposed = np.zeros((v, v, v), dtype=np.float64)
        for xi in range(v):
            for yi in range(v):
                for zi in range(v):
                    a = xi
                    b = (xi + yi) % v
                    c = (xi + yi + zi) % v
                    decomposed[xi, yi, zi] = ordered_piece(a, b, c, d, v)

        if not np.array_equal(tetrahedron, decomposed):
            mismatch = np.argwhere(tetrahedron != decomposed)[0].tolist()
            raise AssertionError(("four-piece identity", v, d, mismatch))

        tetrahedron_count = int(np.sum(tetrahedron))
        expected_tetrahedron = math.comb(d + 2, 3)
        if tetrahedron_count != expected_tetrahedron:
            raise AssertionError(
                ("tetrahedron cardinality", v, d, tetrahedron_count, expected_tetrahedron)
            )

        diagonal_slice = tetrahedron * diagonal
        diagonal_count = int(np.sum(diagonal_slice))
        expected_diagonal = ((d + 1) ** 2) // 4
        if diagonal_count != expected_diagonal:
            raise AssertionError(
                ("diagonal cardinality", v, d, diagonal_count, expected_diagonal)
            )

        tetrahedron_norm = algebra_norm(tetrahedron)
        diagonal_norm = algebra_norm(diagonal_slice)
        bound = 4.0 * interval_bound**5
        tetrahedron_ratio = tetrahedron_norm / bound
        diagonal_ratio = diagonal_norm / bound
        if tetrahedron_ratio > max_tetrahedron_ratio:
            max_tetrahedron_ratio = tetrahedron_ratio
            witnesses["tetrahedron"] = {"d": d, "norm": tetrahedron_norm}
        if diagonal_ratio > max_diagonal_ratio:
            max_diagonal_ratio = diagonal_ratio
            witnesses["diagonal"] = {"d": d, "norm": diagonal_norm}
        if tetrahedron_norm > 0:
            ratio = diagonal_norm / tetrahedron_norm
            if ratio > max_diagonal_over_tetrahedron:
                max_diagonal_over_tetrahedron = ratio
                witnesses["diagonal_over_tetrahedron"] = {"d": d, "ratio": ratio}

        if tetrahedron_norm > bound + 1e-9:
            raise AssertionError(("tetrahedron norm", v, d, tetrahedron_norm, bound))
        if diagonal_norm > tetrahedron_norm + 1e-9:
            raise AssertionError(
                ("diagonal submultiplicativity", v, d, diagonal_norm, tetrahedron_norm)
            )

    if abs(delta_norm - 1.0) > 1e-10:
        raise AssertionError(("diagonal hyperplane norm", v, delta_norm))

    return {
        "v": v,
        "checked_d": v,
        "interval_bound": interval_bound,
        "max_interval_norm": max_interval_norm,
        "diagonal_hyperplane_norm": delta_norm,
        "max_tetrahedron_bound_ratio": max_tetrahedron_ratio,
        "max_diagonal_bound_ratio": max_diagonal_ratio,
        "max_diagonal_over_tetrahedron": max_diagonal_over_tetrahedron,
        "witnesses": witnesses,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-v", type=int, default=15)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("audit_results.json"),
    )
    args = parser.parse_args()
    moduli = list(range(3, args.max_v + 1, 2))
    result = {
        "scope": "exact decomposition and numerical Fourier-algebra audit",
        "moduli": [audit_modulus(v) for v in moduli],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
