from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")


def eval_cap(w: np.ndarray, cap: str):
    a, b, c, d, e, f, x = w
    y = 1.0
    v = e
    u = x - v
    m = x * x + v
    S = a + b + c + d + e + f
    N = S + y + x + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    Phi = 2.0 * (N * N - 25.0 * m) - 75.0 * (x * x * A / Z + v * B / (e * Y) - S)
    sl = {
        "a1": a - 1.0,
        "b1": b - 1.0,
        "c1": c - 1.0,
        "d1": d - 1.0,
        "e1": e - 1.0,
        "f1": f - 1.0,
        "x1": x - 1.0,
        "v1": v - 1.0,
        "u1": u - 1.0,
        "s1": e - v,
        "s2": d + e - x,
        "s3": b + c - x - 1.0,
    }
    for name, cm in caps.items():
        sl[name] = cm - m
    return Phi, sl


def constraints(cap: str):
    names = [
        "a1",
        "b1",
        "c1",
        "d1",
        "e1",
        "f1",
        "x1",
        "v1",
        "u1",
        "s2",
        "s3",
        *CAPS,
    ]
    out = [{"type": "eq", "fun": lambda w, n=cap: eval_cap(w, cap)[1][n]}]
    for name in names:
        if name == cap:
            continue
        out.append({"type": "ineq", "fun": lambda w, n=name: eval_cap(w, cap)[1][n]})
    return out


def run_one(cap: str, starts: int = 80):
    rng = np.random.default_rng(abs(hash(("xq-s1", cap))) % (2**32))
    clusters = defaultdict(list)
    cons = constraints(cap)
    for i in range(starts):
        if i % 4 == 0:
            t = 2.2 + rng.normal(0, 0.08)
            w0 = np.array([t + 1.0 - 1.0 / t, 1.0, t, 1.0, t, 1.0, t])
            w0 += rng.normal(0, 0.04, 7)
            w0 = np.maximum(w0, 1.0)
        else:
            w0 = 1.0 + rng.random(7) * 6.0
        res = minimize(
            lambda w: eval_cap(w, cap)[0],
            w0,
            method="SLSQP",
            bounds=[(1.0, 60.0)] * 7,
            constraints=cons,
            options={"maxiter": 1600, "ftol": 1e-11, "disp": False},
        )
        if not res.success:
            continue
        phi, sl = eval_cap(res.x, cap)
        if min(sl.values()) < -1e-6:
            continue
        active = tuple(sorted(k for k, vv in sl.items() if vv < 1e-5))
        clusters[active].append((float(phi), res.x))
    ranked = []
    for active, pts in clusters.items():
        pts.sort(key=lambda t: t[0])
        ranked.append((pts[0][0], active, len(pts), pts[0][1]))
    ranked.sort(key=lambda t: t[0])
    return ranked


def main() -> None:
    for cap in CAPS:
        ranked = run_one(cap)
        print("CAP", cap, "clusters", len(ranked))
        for phi, active, count, w in ranked[:12]:
            print(" ", round(phi, 10), count, active, np.array2string(w, precision=9))


if __name__ == "__main__":
    main()
