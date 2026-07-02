from __future__ import annotations

from itertools import combinations

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")


def vals(w: np.ndarray, cap: str):
    a, b, c, d, e, f, v = w
    S = a + b + c + d + e + f
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
    M = caps[cap]
    u = 1.0
    q = u + v
    x = (M - v) / q
    N = S + 1.0 + x + q
    Phi = 2.0 * (N * N - 25.0 * M) - 75.0 * (x * q * A / Z + v * B / (e * Y) - S)
    sl = {
        "a1": a - 1.0,
        "b1": b - 1.0,
        "c1": c - 1.0,
        "d1": d - 1.0,
        "e1": e - 1.0,
        "f1": f - 1.0,
        "v1": v - 1.0,
        "x1": x - 1.0,
        "s1": e - v,
        "s2": d + e - q,
        "s3": b + c - x - 1.0,
    }
    for k, cm in caps.items():
        if k != cap:
            sl[k] = cm - M
    return Phi, sl, x, q


def objective(w, cap):
    phi, _sl, _x, _q = vals(w, cap)
    return phi


def constraints(cap: str, active: tuple[str, ...]):
    names = [
        "a1",
        "b1",
        "c1",
        "d1",
        "e1",
        "f1",
        "v1",
        "x1",
        "s1",
        "s2",
        "s3",
        *[k for k in CAPS if k != cap],
    ]
    cons = []
    for name in names:
        if name in active:
            cons.append({"type": "eq", "fun": lambda w, n=name: vals(w, cap)[1][n]})
        else:
            cons.append({"type": "ineq", "fun": lambda w, n=name: vals(w, cap)[1][n]})
    return cons


def scan(cap: str, max_active: int = 4, starts: int = 12) -> None:
    rng = np.random.default_rng(2718)
    names = [
        "a1",
        "b1",
        "c1",
        "d1",
        "e1",
        "f1",
        "v1",
        "x1",
        "s1",
        "s2",
        "s3",
        *[k for k in CAPS if k != cap],
    ]
    best = []
    for r in range(max_active + 1):
        for active in combinations(names, r):
            local = None
            cons = constraints(cap, active)
            for _ in range(starts):
                w0 = 1.0 + rng.random(7) * 4.0
                # Seed near the known all-tight basin occasionally.
                if rng.random() < 0.4:
                    t = 2.43938 + rng.normal(0, 0.02)
                    w0 = np.array([3.02944, 1.0, t, 1.0, t, 1.0, t])
                    w0 += rng.normal(0, 0.015, 7)
                    w0 = np.maximum(w0, 1.0)
                res = minimize(
                    objective,
                    w0,
                    args=(cap,),
                    method="SLSQP",
                    bounds=[(1.0, 40.0)] * 7,
                    constraints=cons,
                    options={"maxiter": 1000, "ftol": 1e-11, "disp": False},
                )
                if not res.success:
                    continue
                phi, sl, x, q = vals(res.x, cap)
                eq_ok = all(abs(sl[n]) <= 1e-6 for n in active)
                ineq_ok = all(vv >= -1e-6 for vv in sl.values())
                if not (eq_ok and ineq_ok):
                    continue
                if local is None or phi < local[0]:
                    local = (phi, active, res.x, sl, x, q)
            if local is not None:
                best.append(local)
    best.sort(key=lambda z: z[0])
    print("CAP", cap, "survivors", len(best))
    for phi, active, w, sl, x, q in best[:20]:
        act = [k for k, vv in sl.items() if vv < 1e-5]
        print("phi", round(float(phi), 9), "forced", active, "active", act, "x", x, "q", q, "w", w)


if __name__ == "__main__":
    for cap in CAPS:
        scan(cap)
