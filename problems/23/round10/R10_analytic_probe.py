"""Numerical microscope for the Gamma_11 arc frontier.

This is steering evidence only.  It maximises the epigraph variable t subject
to t <= q_{s,l}(x), x >= 0, sum x = 1, for selected cyclic window lengths.
Every q_{s,l} is rebuilt directly as the monochromatic edge weight of the
corresponding arc cut.
"""
from __future__ import annotations

import argparse
from collections import Counter

import numpy as np
from scipy.optimize import minimize


N = 11
EDGES = tuple(
    (u, v)
    for u in range(N)
    for v in range(u + 1, N)
    if min(v - u, N - (v - u)) in (4, 5)
)


def cut_matrix(start: int, length: int) -> np.ndarray:
    inside = {(start + j) % N for j in range(length)}
    matrix = np.zeros((N, N))
    for u, v in EDGES:
        if (u in inside) == (v in inside):
            matrix[u, v] = matrix[v, u] = 0.5
    return matrix


def matrices(lengths: tuple[int, ...]) -> tuple[np.ndarray, list[tuple[int, int]]]:
    labels = [(start, length) for length in lengths for start in range(N)]
    return np.stack([cut_matrix(*label) for label in labels]), labels


def values(x: np.ndarray, mats: np.ndarray) -> np.ndarray:
    return np.einsum("i,kij,j->k", x, mats, x)


def solve(lengths: tuple[int, ...], starts: int, seed: int) -> None:
    mats, labels = matrices(lengths)
    rng = np.random.default_rng(seed)
    records = []
    constraints = [
        {"type": "eq", "fun": lambda z: np.sum(z[:-1]) - 1.0},
        {
            "type": "ineq",
            "fun": lambda z, mats=mats: values(z[:-1], mats) - z[-1],
        },
    ]
    bounds = [(0.0, 1.0)] * N + [(0.0, 0.25)]
    seeds = [np.ones(N) / N]
    for step in range(N):
        x = np.zeros(N)
        x[[0, (4 * step) % N, (8 * step) % N, (1 * step) % N, (5 * step) % N]] = 0.2
        if abs(x.sum() - 1) < 1e-9:
            seeds.append(x)
    seeds += [rng.dirichlet(np.ones(N) * 0.4) for _ in range(starts)]
    for x0 in seeds:
        t0 = float(values(x0, mats).min())
        result = minimize(
            lambda z: -z[-1],
            np.r_[x0, t0],
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"ftol": 1e-13, "maxiter": 4000},
        )
        x = result.x[:-1]
        q = values(x, mats)
        active = tuple(labels[j] for j in np.flatnonzero(q <= q.min() + 2e-8))
        records.append((float(q.min()), result.success, x, active))
    records.sort(key=lambda item: item[0], reverse=True)
    print(f"lengths={lengths}; local optima={len(records)}")
    for value, success, x, active in records[:20]:
        support = tuple(i for i, a in enumerate(x) if a > 1e-7)
        rounded = tuple(round(float(a), 9) for a in x)
        print(
            f"value={value:.12f}; success={success}; support={support}; "
            f"active={active}; x={rounded}"
        )
    print("support histogram:", Counter(tuple(i for i, a in enumerate(r[2]) if a > 1e-7) for r in records))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lengths", default="3,4,5")
    parser.add_argument("--starts", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20260726)
    args = parser.parse_args()
    solve(tuple(int(item) for item in args.lengths.split(",")), args.starts, args.seed)
