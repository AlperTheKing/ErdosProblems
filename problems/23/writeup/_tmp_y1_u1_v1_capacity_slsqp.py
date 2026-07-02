from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")


def vals(w: np.ndarray, cap: str):
    a, b, c, d, e, f = w
    y = 1.0
    u = 1.0
    v = 1.0
    q = 2.0
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
    x = (M - v) / q
    N = S + x + y + u + v
    Phi = 2 * (N * N - 25 * M) - 75 * (x * q * A / Z + v * B / (e * Y) - S)
    sl = {
        "x1": x - 1,
        "s1": e - 1,
        "s2": d + e - 2,
        "s3": b + c - 1 - x,
    }
    for name, expr in caps.items():
        if name != cap:
            sl[name] = expr - M
    return Phi, sl, x


def scan(cap: str) -> None:
    rng = np.random.default_rng(1729)
    cons = [{"type": "ineq", "fun": lambda w, n=n: vals(w, cap)[1][n]} for n in ["x1", "s1", "s2", "s3", *[c for c in CAPS if c != cap]]]
    best = None
    seeds = [np.ones(6), np.array([3.03, 1, 2.44, 1, 2.44, 1])]
    for _ in range(40):
        seeds.append(1 + rng.random(6) * 6)
    for w0 in seeds:
        res = minimize(lambda w: vals(w, cap)[0], w0, method="SLSQP", bounds=[(1, 60)] * 6, constraints=cons, options={"maxiter": 1000, "ftol": 1e-12})
        if not res.success:
            continue
        Phi, sl, x = vals(res.x, cap)
        if all(z >= -1e-7 for z in sl.values()):
            if best is None or Phi < best[0]:
                best = (Phi, res.x, sl, x)
    print("CAP", cap, "best", None if best is None else best[0])
    if best is not None:
        Phi, w, sl, x = best
        print(" w", w, "x", x, "active", [k for k, z in sl.items() if z < 1e-6], "sl", sl)


def main() -> None:
    for cap in CAPS:
        scan(cap)


if __name__ == "__main__":
    main()
