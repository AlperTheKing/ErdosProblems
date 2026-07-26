"""Recover the apparent four-dimensional rank-22 slice of the exact pencil.

The stable numerical kernel of the exported block-0 dual leaves four tiny
singular directions in coefficient space, separated from the remaining six
by a large gap.  This script puts that four-space in graph form over four
well-conditioned pivot coefficients and prints rational reconstructions.

No solver is called.  Rational candidates are checked by fresh-prime exact
modular ranks of the corresponding integer pencil combinations.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy.linalg as la


HERE = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def primitive(values: list[int]) -> list[int]:
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(int(value)))
    if divisor:
        values = [int(value) // divisor for value in values]
    first = next((value for value in values if value), 0)
    if first < 0:
        values = [-value for value in values]
    return values


def rational_columns(
    graph: np.ndarray, pivots: list[int], denominator_bound: int
) -> tuple[list[list[int]], float]:
    rational = [
        [
            Fraction(float(graph[row, column])).limit_denominator(
                denominator_bound
            )
            for column in range(graph.shape[1])
        ]
        for row in range(graph.shape[0])
    ]
    maximum_error = max(
        abs(float(rational[row][column]) - graph[row, column])
        for row in range(graph.shape[0])
        for column in range(graph.shape[1])
    )
    columns = []
    for column in range(graph.shape[1]):
        denominator = math.lcm(
            *[
                rational[row][column].denominator
                for row in range(graph.shape[0])
            ]
        )
        vector = [
            int(rational[row][column] * denominator)
            for row in range(graph.shape[0])
        ]
        columns.append(primitive(vector))
    for column, pivot in enumerate(pivots):
        if columns[column][pivot] == 0:
            raise AssertionError("rational pivot vanished")
    return columns, maximum_error


def main() -> None:
    unique = load_module(
        "codex_r10_slice_unique",
        "CODEX_R10_SECOND_FACE_BLOCK0_UNIQUE_RAY_PROBE.py",
    )
    rank_helper = load_module(
        "codex_r10_slice_rank",
        "CODEX_R10_ZERO_NU_BLOCK0_PSD_EXPOSURE.py",
    )
    pencil_integer, steering = unique.exact_pencil()
    pencil = pencil_integer.astype(np.float64)
    raw = unique.raw_block0()
    _eigenvalues, eigenvectors = np.linalg.eigh((raw + raw.T) / 2)
    kernel = eigenvectors[:, :132]
    annihilation = np.column_stack(
        [(matrix @ kernel).reshape(-1) for matrix in pencil]
    )
    norms = np.linalg.norm(annihilation, axis=0)
    normalized = annihilation / norms
    _u, singular, vt = np.linalg.svd(normalized, full_matrices=False)
    coefficient_space = vt[-4:].T / norms[:, None]
    coefficient_space = la.orth(coefficient_space)
    _q, _r, permutation = la.qr(
        coefficient_space.T, mode="economic", pivoting=True
    )
    pivots = list(map(int, permutation[:4]))
    graph = coefficient_space @ np.linalg.inv(
        coefficient_space[pivots, :]
    )
    projector = coefficient_space @ coefficient_space.T
    steering_residual = np.linalg.norm(
        steering - projector @ steering
    ) / np.linalg.norm(steering)
    print(
        "slice"
        f" pivots={pivots}"
        f" singular_gap={singular[-5] / singular[-4]:.12e}"
        f" tiny={','.join(f'{value:.12e}' for value in singular[-4:])}"
        f" steering_relative_residual={steering_residual:.12e}"
    )
    for row in range(10):
        print(
            f"GRAPH row={row} values="
            + ",".join(f"{value:.15g}" for value in graph[row])
        )

    primes = (1_000_037, 1_000_039)
    for bound in (10, 100, 1_000, 10_000, 100_000, 1_000_000):
        columns, error = rational_columns(graph, pivots, bound)
        combinations = []
        for coefficients in columns:
            matrix = np.zeros((154, 154), dtype=np.int64)
            for coefficient, generator in zip(
                coefficients, pencil_integer
            ):
                matrix += int(coefficient) * generator
            combinations.append(matrix)
        stacked = np.vstack(combinations)
        ranks = [
            len(rank_helper.select_rows_mod_prime(stacked, prime)[0])
            for prime in primes
        ]
        print(
            f"RATIONAL bound={bound} error={error:.12e}"
            f" ranks={ranks} columns={columns}"
        )


if __name__ == "__main__":
    main()
