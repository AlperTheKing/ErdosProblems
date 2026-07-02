from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")
BRANCHES = ("s2", "s3", "u1", "xq")


def eval_branch(w: np.ndarray, cap: str, branch: str):
    a, b, c, d, e, f, z = w
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
    if branch == "s2":
        x = z
        q = d + e
        v = M - x * q
        u = q - v
    elif branch == "s3":
        v = z
        x = b + c - 1.0
        q = (M - v) / x
        u = q - v
    elif branch == "u1":
        v = z
        u = 1.0
        q = 1.0 + v
        x = (M - v) / q
    elif branch == "xq":
        x = z
        q = x
        v = M - x * x
        u = q - v
    else:
        raise ValueError(branch)

    N = S + 1.0 + x + q
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
    for k, cm in caps.items():
        sl[k] = cm - M
    return Phi, sl, (x, q, u, v)


def objective(w, cap, branch):
    return eval_branch(w, cap, branch)[0]


def constraints(cap: str, branch: str):
    fixed = {cap}
    if branch == "s2":
        fixed.add("s2")
    elif branch == "s3":
        fixed.add("s3")
    elif branch == "u1":
        fixed.add("u1")
    elif branch == "xq":
        pass
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


def run_one(cap: str, branch: str, starts: int = 50):
    rng = np.random.default_rng(abs(hash((cap, branch))) % (2**32))
    clusters = defaultdict(list)
    cons = constraints(cap, branch)
    for i in range(starts):
        if i % 3 == 0:
            t = 2.439376 + rng.normal(0, 0.04)
            z = t
            if branch == "s2":
                z = t
            elif branch == "s3":
                z = t
            elif branch == "u1":
                z = t
            elif branch == "xq":
                z = t
            w0 = np.array([3.029436, 1.0, t, 1.0, t, 1.0, z])
            w0 += rng.normal(0, 0.025, 7)
            w0 = np.maximum(w0, 1.0)
        else:
            w0 = 1.0 + rng.random(7) * 5.0
        res = minimize(
            objective,
            w0,
            args=(cap, branch),
            method="SLSQP",
            bounds=[(1.0, 40.0)] * 7,
            constraints=cons,
            options={"maxiter": 1200, "ftol": 1e-11, "disp": False},
        )
        if not res.success:
            continue
        phi, sl, xquv = eval_branch(res.x, cap, branch)
        if min(sl.values()) < -1e-6:
            continue
        active = tuple(sorted(k for k, vv in sl.items() if vv < 1e-5))
        clusters[active].append((float(phi), res.x, xquv))
    ranked = []
    for active, pts in clusters.items():
        pts.sort(key=lambda t: t[0])
        ranked.append((pts[0][0], active, len(pts), pts[0][1], pts[0][2]))
    ranked.sort(key=lambda t: t[0])
    return ranked


if __name__ == "__main__":
    for branch in BRANCHES:
        print("BRANCH", branch)
        for cap in CAPS:
            ranked = run_one(cap, branch)
            print(" ", cap, "clusters", len(ranked))
            for phi, active, count, w, xquv in ranked[:8]:
                print("   phi", round(phi, 9), "count", count, "active", active)
                print("    w", np.array2string(w, precision=9), "xq uv", tuple(round(float(z), 9) for z in xquv))
