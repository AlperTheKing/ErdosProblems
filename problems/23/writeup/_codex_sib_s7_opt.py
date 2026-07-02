"""Exploratory continuous optimization for the sibling S7 atom.

This is not an acceptance gate.  It is only used to discover which S7 faces
look active before exact KKT/Bernstein work.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize


NAMES = ("a", "b", "c", "d", "e", "f", "x", "y", "u", "v")


def pieces(z: np.ndarray) -> tuple[float, np.ndarray]:
    a, b, c, d, e, f, x, y, u, v = z
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    IminusN = x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)
    phi = 2 * (N * N - 25 * m) - 75 * IminusN
    slacks = np.array(
        [
            e - v,
            d + e - u - v,
            b + c - x - y,
            Y - m,
            a * e + b * f + c * f - m,
            a * c + d * f + e * f - m,
            a * e + d * f + e * f - m,
        ],
        dtype=float,
    )
    return float(phi), slacks


def objective(z: np.ndarray) -> float:
    phi, _ = pieces(z)
    return phi


def constraints() -> list[dict]:
    cons = []
    for i in range(7):
        cons.append({"type": "ineq", "fun": lambda z, i=i: pieces(z)[1][i]})
    return cons


@dataclass
class Hit:
    value: float
    z: np.ndarray
    slacks: np.ndarray
    active: tuple[int, ...]


def start_point(rng: random.Random, bound: float) -> np.ndarray:
    # Log-uniform starts are more useful than uniform starts on this cone.
    vals = [math.exp(rng.uniform(0.0, math.log(bound))) for _ in range(10)]
    return np.array(vals, dtype=float)


def run(face_name: str, fixed: dict[int, float]) -> list[Hit]:
    rng = random.Random(20260702)
    bounds = []
    for i in range(10):
        if i in fixed:
            bounds.append((fixed[i], fixed[i]))
        else:
            bounds.append((1.0, 40.0))
    cons = constraints()
    hits: list[Hit] = []

    seeds = [
        np.ones(10),
        np.array([2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 1.0, 2.0]),
        np.array([3.0, 1.0, 3.0, 1.0, 3.0, 1.0, 3.0, 1.0, 1.0, 3.0]),
    ]
    seeds.extend(start_point(rng, 20.0) for _ in range(250))

    for z0 in seeds:
        z0 = z0.copy()
        for i, val in fixed.items():
            z0[i] = val
        res = minimize(
            objective,
            z0,
            method="SLSQP",
            bounds=bounds,
            constraints=cons,
            options={"maxiter": 3000, "ftol": 1e-11, "disp": False},
        )
        if not res.success and res.fun > 0:
            # Still useful if it found a feasible point.
            pass
        phi, sl = pieces(res.x)
        if np.min(sl) < -1e-6:
            continue
        active = tuple(i + 1 for i, s in enumerate(sl) if abs(s) < 1e-5)
        hits.append(Hit(phi, res.x.copy(), sl, active))

    hits.sort(key=lambda h: h.value)
    print("FACE", face_name, "hits", len(hits))
    for h in hits[:5]:
        print("phi", f"{h.value:.12g}", "active", h.active)
        print("z", " ".join(f"{name}={val:.9g}" for name, val in zip(NAMES, h.z)))
        print("slacks", " ".join(f"s{i+1}={val:.3e}" for i, val in enumerate(h.slacks)))
    return hits


def main() -> None:
    run("free", {})
    for i, name in enumerate(NAMES):
        run(f"{name}=1", {i: 1.0})


if __name__ == "__main__":
    main()
