"""Explore active endpoint KKT signatures for the sibling S7 fixed-core form.

This is a discovery tool only.  It samples feasible cores, minimizes the
four endpoint variables, and records active endpoint/cap signatures.
"""

from __future__ import annotations

import math
import random
from collections import Counter

import numpy as np
from scipy.optimize import minimize


def core_caps(core: np.ndarray) -> tuple[float, float, float, float, float, float, float, float]:
    a, b, c, d, e, f = core
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    caps = (
        Y,
        a * e + b * f + c * f,
        a * c + d * f + e * f,
        a * e + d * f + e * f,
    )
    return Y, Z, A, B, min(caps), caps[0], caps[1], caps[2]  # last cap omitted from display


def endpoint_phi(core: np.ndarray, z: np.ndarray) -> float:
    a, b, c, d, e, f = core
    x, y, u, v = z
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    C0 = a + b + c + d + e + f
    p = A / Z
    q = B / (e * Y)
    m = x * u + x * v + y * v
    N = C0 + x + y + u + v
    return 2 * (N * N - 25 * m) + 75 * C0 - 75 * (p * x * (u + v) + q * y * v)


def feasible_endpoint_start(core: np.ndarray) -> np.ndarray | None:
    a, b, c, d, e, f = core
    x = 1.0
    y = 1.0
    v = 1.0
    u = 1.0
    if v > e + 1e-9 or u + v > d + e + 1e-9 or x + y > b + c + 1e-9:
        return None
    caps = core_caps(core)
    m = x * u + x * v + y * v
    if m > caps[4] + 1e-9:
        return None
    return np.array([x, y, u, v], dtype=float)


def optimize_core(core: np.ndarray) -> tuple[float, np.ndarray, tuple[str, ...]] | None:
    a, b, c, d, e, f = core
    start = feasible_endpoint_start(core)
    if start is None:
        return None
    mcap = core_caps(core)[4]
    bounds = [(1.0, b + c - 1.0), (1.0, b + c - 1.0), (1.0, d + e - 1.0), (1.0, e)]
    cons = [
        {"type": "ineq", "fun": lambda z: b + c - z[0] - z[1]},
        {"type": "ineq", "fun": lambda z: d + e - z[2] - z[3]},
        {"type": "ineq", "fun": lambda z: mcap - (z[0] * z[2] + z[0] * z[3] + z[1] * z[3])},
    ]
    seeds = [
        start,
        np.array([max(1, b + c - 1), 1, 1, min(e, max(1, d + e - 1))], dtype=float),
    ]
    best = None
    for z0 in seeds:
        z0 = np.minimum(np.maximum(z0, [lo for lo, _ in bounds]), [hi for _, hi in bounds])
        if cons[0]["fun"](z0) < -1e-8 or cons[1]["fun"](z0) < -1e-8 or cons[2]["fun"](z0) < -1e-8:
            continue
        res = minimize(lambda z: endpoint_phi(core, z), z0, method="SLSQP", bounds=bounds, constraints=cons, options={"ftol": 1e-11, "maxiter": 1000})
        if not res.success and res.fun > 0:
            pass
        z = res.x
        if min(cons[i]["fun"](z) for i in range(3)) < -1e-6:
            continue
        val = endpoint_phi(core, z)
        if best is None or val < best[0]:
            best = (val, z)
    if best is None:
        return None
    val, z = best
    active = []
    labels = ["x1", "y1", "u1", "v1", "vE", "xyBC", "uvDE", "mcap"]
    vals = [
        z[0] - 1,
        z[1] - 1,
        z[2] - 1,
        z[3] - 1,
        e - z[3],
        b + c - z[0] - z[1],
        d + e - z[2] - z[3],
        mcap - (z[0] * z[2] + z[0] * z[3] + z[1] * z[3]),
    ]
    for lab, vv in zip(labels, vals):
        if abs(vv) < 1e-5:
            active.append(lab)
    return val, z, tuple(active)


def main() -> None:
    rng = random.Random(23)
    sigs = Counter()
    best = (float("inf"), None, None, None)
    checked = feasible = 0
    for _ in range(2000):
        core = np.array([math.exp(rng.uniform(0, math.log(6))) for _ in range(6)], dtype=float)
        checked += 1
        ans = optimize_core(core)
        if ans is None:
            continue
        feasible += 1
        val, z, sig = ans
        sigs[sig] += 1
        if val < best[0]:
            best = (val, core.copy(), z.copy(), sig)
    print("checked", checked, "feasible", feasible)
    print("best", best[0], "core", best[1], "endpoint", best[2], "sig", best[3])
    for sig, n in sigs.most_common(30):
        print(n, sig)


if __name__ == "__main__":
    main()
