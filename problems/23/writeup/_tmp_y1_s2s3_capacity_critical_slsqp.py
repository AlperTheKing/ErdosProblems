from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")


def core(a, b, c, d, e, f):
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
    return S, Y, Z, A, B, caps


def vals(w: np.ndarray, branch: str, cap: str):
    a, b, c, d, e, f, v = w
    y = 1.0
    S, Y, Z, A, B, caps = core(a, b, c, d, e, f)
    M = caps[cap]
    if branch == "s2":
        q = d + e
        x = (M - v) / q
    elif branch == "s3":
        x = b + c - 1.0
        q = (M - v) / x
    else:
        raise ValueError(branch)
    u = q - v
    N = S + y + x + q
    Phi = 2.0 * (N * N - 25.0 * M) - 75.0 * ((M - v) * A / Z + v * B / (e * Y) - S)
    slope = -1.0 / (q if branch == "s2" else x)
    dPhi_v = 4.0 * N * slope - 75.0 * (-A / Z + B / (e * Y))
    sl = {
        "a1": a - 1.0,
        "b1": b - 1.0,
        "c1": c - 1.0,
        "d1": d - 1.0,
        "e1": e - 1.0,
        "f1": f - 1.0,
        "v1": v - 1.0,
        "x1": x - 1.0,
        "u1": u - 1.0,
        "s1": e - v,
    }
    if branch == "s2":
        sl["s3"] = b + c - 1.0 - x
    else:
        sl["s2"] = d + e - q
    for name, expr in caps.items():
        if name != cap:
            sl[name] = expr - M
    return Phi, dPhi_v, sl, x, u


def scan(branch: str, cap: str) -> None:
    rng = np.random.default_rng(20260702)
    names = ["a1", "b1", "c1", "d1", "e1", "f1", "v1", "x1", "u1", "s1", *("s3" if branch == "s2" else "s2",), *[c for c in CAPS if c != cap]]
    cons = [{"type": "ineq", "fun": lambda w, n=n: vals(w, branch, cap)[2][n]} for n in names]
    cons.append({"type": "eq", "fun": lambda w: vals(w, branch, cap)[1]})
    best = None
    seeds: list[np.ndarray] = []
    for t in (1.0, 1.4, 2.0, 2.4393767, 4.0):
        seeds.append(np.array([t + 1.0 - 1.0 / t, 1.0, t, 1.0, t, 1.0, t]))
    for _ in range(80):
        seeds.append(1.0 + rng.random(7) * 8.0)
    for w0 in seeds:
        res = minimize(lambda w: vals(w, branch, cap)[0], w0, method="SLSQP", bounds=[(1.0, 80.0)] * 7, constraints=cons, options={"maxiter": 2000, "ftol": 1e-12})
        if not res.success:
            continue
        Phi, dPhi, sl, x, u = vals(res.x, branch, cap)
        if abs(dPhi) <= 1e-6 and all(z >= -1e-7 for z in sl.values()):
            if best is None or Phi < best[0]:
                best = (Phi, res.x, sl, x, u, dPhi)
    print("BR", branch, "CAP", cap, "best", None if best is None else best[0])
    if best is not None:
        Phi, w, sl, x, u, dPhi = best
        print(" w", w, "x", x, "u", u, "dPhi", dPhi)
        print(" active", [k for k, z in sl.items() if z < 1e-5])


def main() -> None:
    for branch in ("s2", "s3"):
        for cap in CAPS:
            scan(branch, cap)


if __name__ == "__main__":
    main()
