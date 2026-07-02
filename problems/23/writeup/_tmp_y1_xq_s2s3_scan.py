from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")
BRANCHES = ("s2", "s3")


def eval_branch(w: np.ndarray, cap: str, branch: str):
    a, b, c, d, e, f = w
    y = 1.0
    if branch == "s2":
        x = d + e
    elif branch == "s3":
        x = b + c - 1.0
    else:
        raise ValueError(branch)
    q = x
    caps = {
        "s4": a * c + b * f + c * f,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    M = caps[cap]
    v = M - x * x
    u = x - v
    S = a + b + c + d + e + f
    N = S + y + x + q
    Y = caps["s4"]
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2.0 * (N * N - 25.0 * M) - 75.0 * (x * q * A / Z + v * B / (e * Y) - S)
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
        "s2": d + e - q,
        "s3": b + c - x - 1.0,
    }
    for name, cm in caps.items():
        sl[name] = cm - M
    return Phi, sl, (x, u, v)


def constraints(cap: str, branch: str):
    fixed = {cap, branch}
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
        "s1",
        "s2",
        "s3",
        *CAPS,
    ]
    out = []
    for name in names:
        if name in fixed:
            continue
        out.append({"type": "ineq", "fun": lambda w, n=name: eval_branch(w, cap, branch)[1][n]})
    return out


def run_one(cap: str, branch: str, starts: int = 100):
    rng = np.random.default_rng(abs(hash(("xq", branch, cap))) % (2**32))
    clusters = defaultdict(list)
    cons = constraints(cap, branch)
    for i in range(starts):
        if i % 4 == 0:
            t = 2.2 + rng.normal(0, 0.08)
            w0 = np.array([t + 1.0 - 1.0 / t, 1.0, t, 1.0, t, 1.0])
            w0 += rng.normal(0, 0.04, 6)
            w0 = np.maximum(w0, 1.0)
        else:
            w0 = 1.0 + rng.random(6) * 6.0
        res = minimize(
            lambda w: eval_branch(w, cap, branch)[0],
            w0,
            method="SLSQP",
            bounds=[(1.0, 60.0)] * 6,
            constraints=cons,
            options={"maxiter": 1600, "ftol": 1e-11, "disp": False},
        )
        if not res.success:
            continue
        phi, sl, xuv = eval_branch(res.x, cap, branch)
        if min(sl.values()) < -1e-6:
            continue
        active = tuple(sorted(k for k, vv in sl.items() if vv < 1e-5))
        clusters[active].append((float(phi), res.x, xuv))
    ranked = []
    for active, pts in clusters.items():
        pts.sort(key=lambda t: t[0])
        ranked.append((pts[0][0], active, len(pts), pts[0][1], pts[0][2]))
    ranked.sort(key=lambda t: t[0])
    return ranked


def main() -> None:
    for branch in BRANCHES:
        print("BRANCH", branch)
        for cap in CAPS:
            ranked = run_one(cap, branch)
            print(" CAP", cap, "clusters", len(ranked))
            for phi, active, count, w, xuv in ranked[:12]:
                print(
                    " ",
                    round(phi, 10),
                    count,
                    active,
                    np.array2string(w, precision=9),
                    tuple(round(float(z), 9) for z in xuv),
                )


if __name__ == "__main__":
    main()
