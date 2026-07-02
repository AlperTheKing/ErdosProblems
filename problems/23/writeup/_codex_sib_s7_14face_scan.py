"""Exploratory SLSQP scan for the 14 endpoint-fiber S7 faces.

Not an acceptance gate.  It ranks the exact faces from the endpoint-fiber
reduction by numerical minimum of Phi under old variables >= 1.
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
    N = float(np.sum(z))
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    IminusN = x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)
    phi = 2 * (N * N - 25 * m) - 75 * IminusN
    slacks = np.array([
        e - v,
        d + e - u - v,
        b + c - x - y,
        Y - m,
        a * e + b * f + c * f - m,
        a * c + d * f + e * f - m,
        a * e + d * f + e * f - m,
    ])
    return float(phi), slacks


def objective(z: np.ndarray) -> float:
    return pieces(z)[0]


def base_constraints():
    return [{"type": "ineq", "fun": lambda z, i=i: pieces(z)[1][i]} for i in range(7)]


def face_constraints(face: tuple[str, ...]):
    cons = base_constraints()
    for item in face:
        if item in NAMES:
            idx = NAMES.index(item)
            cons.append({"type": "eq", "fun": lambda z, idx=idx: z[idx] - 1.0})
        elif item == "v=e":
            cons.append({"type": "eq", "fun": lambda z: z[9] - z[4]})
        elif item.startswith("s"):
            j = int(item[1:]) - 1
            cons.append({"type": "eq", "fun": lambda z, j=j: pieces(z)[1][j]})
        else:
            raise ValueError(item)
    return cons


@dataclass
class Hit:
    face: tuple[str, ...]
    value: float
    z: np.ndarray
    slacks: np.ndarray


def run_face(face: tuple[str, ...], rng: random.Random) -> Hit | None:
    bounds = [(1.0, 40.0)] * 10
    cons = face_constraints(face)
    seeds = [np.ones(10), np.array([3, 1, 2.4, 1, 2.4, 1, 2.4, 1, 1, 2.4], dtype=float)]
    for _ in range(80):
        seeds.append(np.array([math.exp(rng.uniform(0, math.log(12))) for _ in range(10)], dtype=float))
    best: Hit | None = None
    for z0 in seeds:
        # Make obvious lower-bound faces feasible-ish initially.
        for item in face:
            if item in NAMES:
                z0[NAMES.index(item)] = 1.0
            elif item == "v=e":
                z0[9] = z0[4]
        res = minimize(objective, z0, method="SLSQP", bounds=bounds, constraints=cons, options={"maxiter": 2500, "ftol": 1e-11, "disp": False})
        phi, sl = pieces(res.x)
        if np.min(sl) < -1e-5:
            continue
        eq_ok = True
        for item in face:
            if item in NAMES and abs(res.x[NAMES.index(item)] - 1.0) > 1e-5:
                eq_ok = False
            elif item == "v=e" and abs(res.x[9] - res.x[4]) > 1e-5:
                eq_ok = False
            elif item.startswith("s") and abs(sl[int(item[1:]) - 1]) > 1e-5:
                eq_ok = False
        if not eq_ok:
            continue
        hit = Hit(face, phi, res.x.copy(), sl.copy())
        if best is None or hit.value < best.value:
            best = hit
    return best


def main() -> None:
    faces: list[tuple[str, ...]] = [("y",), ("x",)]
    for s in ["s4", "s5", "s6", "s7"]:
        faces.extend([(s, "u"), (s, "v"), (s, "v=e")])
    rng = random.Random(20260702)
    hits = [run_face(face, rng) for face in faces]
    hits = [h for h in hits if h is not None]
    hits.sort(key=lambda h: h.value)
    for h in hits:
        ztxt = " ".join(f"{name}={val:.8g}" for name, val in zip(NAMES, h.z))
        active = tuple(i + 1 for i, s in enumerate(h.slacks) if abs(s) < 1e-5)
        print("face", h.face, "phi", f"{h.value:.12g}", "active", active)
        print(" ", ztxt)


if __name__ == "__main__":
    main()
