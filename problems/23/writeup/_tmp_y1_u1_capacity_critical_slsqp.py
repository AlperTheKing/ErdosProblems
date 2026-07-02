from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")


def vals(w: np.ndarray, cap: str):
    a, b, c, d, e, f, v = w
    y = 1.0
    u = 1.0
    q = 1.0 + v
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
    Phi = 2.0 * (N * N - 25.0 * M) - 75.0 * (x * q * A / Z + v * B / (e * Y) - S)
    dPhi_v = 4.0 * N * (1.0 - (M + 1.0) / (q * q)) - 75.0 * (-A / Z + B / (e * Y))
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
        "s2": d + e - 1.0 - v,
        "s3": b + c - 1.0 - x,
    }
    for name, expr in caps.items():
        if name != cap:
            sl[name] = expr - M
    return Phi, dPhi_v, sl, x


def scan(cap: str) -> None:
    rng = np.random.default_rng(9237)
    ineq_names = ["a1", "b1", "c1", "d1", "e1", "f1", "v1", "x1", "s1", "s2", "s3", *[c for c in CAPS if c != cap]]
    cons = [{"type": "ineq", "fun": lambda w, n=n: vals(w, cap)[2][n]} for n in ineq_names]
    cons.append({"type": "eq", "fun": lambda w: vals(w, cap)[1]})
    best = None
    seeds: list[np.ndarray] = []
    for t in (1.0, 1.4, 2.0, 2.4393767, 4.0):
        seeds.append(np.array([t + 1.0 - 1.0 / t, 1.0, t, 1.0, t, 1.0, t]))
    for _ in range(80):
        seeds.append(1.0 + rng.random(7) * 8.0)
    for w0 in seeds:
        res = minimize(lambda w: vals(w, cap)[0], w0, method="SLSQP", bounds=[(1.0, 80.0)] * 7, constraints=cons, options={"maxiter": 2000, "ftol": 1e-12})
        if not res.success:
            continue
        Phi, dPhi, sl, x = vals(res.x, cap)
        if abs(dPhi) <= 1e-6 and all(z >= -1e-7 for z in sl.values()):
            if best is None or Phi < best[0]:
                best = (Phi, res.x, sl, x, dPhi)
    print("CAP", cap, "best", None if best is None else best[0])
    if best is not None:
        Phi, w, sl, x, dPhi = best
        print(" w", w, "x", x, "dPhi", dPhi)
        print(" active", [k for k, z in sl.items() if z < 1e-5])


def main() -> None:
    for cap in CAPS:
        scan(cap)


if __name__ == "__main__":
    main()
