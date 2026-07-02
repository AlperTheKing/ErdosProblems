"""Deterministic falsifier stress for y=1,u=1 capacity critical leaves.

This is NOT a proof artifact.  It enforces the exact one-dimensional critical
equation from _codex_sib_s7_y1_u1_capacity_vfibers.py numerically:

    d Phi / dv = 0

on each capacity face s_j=0.  The goal is only to make the current observed
critical-leaf inventory reproducible while the exact FJ/Sturm coverage proof is
being developed.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")

KNOWN = {
    "s4": {
        ("b1", "d1", "f1", "s1", "s2", "s3", "s5", "s6", "s7"): "seven-tight critical",
        ("a1", "b1", "d1", "s1", "s2", "s5", "s6", "s7"): "high positive critical",
    },
    "s5": {
        ("b1", "d1", "f1", "s1", "s2", "s3", "s4", "s6", "s7"): "seven-tight critical",
    },
    "s6": {
        ("d1", "f1", "s1", "s2", "s3", "s7"): "u1 s6/s7 high critical",
    },
    "s7": {
        ("d1", "f1", "s1", "s2", "s3", "s6"): "u1 s6/s7 high critical",
        ("a1", "b1", "d1", "s1", "s2", "s4", "s5", "s6"): "high positive critical",
    },
}


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
        "s2": d + e - q,
        "s3": b + c - x - 1.0,
    }
    for name, expr in caps.items():
        if name != cap:
            sl[name] = expr - M
    return Phi, dPhi_v, sl, x


def starts_for(cap: str, n_random: int) -> list[np.ndarray]:
    rng = np.random.default_rng(abs(hash(("codex-u1-critical", cap))) % (2**32))
    starts: list[np.ndarray] = []
    for t in (1.0, 1.4, 1.9562952, 2.3345127, 2.4393767, 4.0, 8.0):
        starts.append(np.array([t + 1.0 - 1.0 / t, 1.0, t, 1.0, t, 1.0, t], dtype=float))
        starts.append(np.array([t + 0.7, 1.08, t, 1.0, t, 1.0, t], dtype=float))
    for _ in range(n_random):
        starts.append(1.0 + rng.random(7) * 10.0)
    return starts


def constraints(cap: str):
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
        *[c for c in CAPS if c != cap],
    ]
    cons = [{"type": "eq", "fun": lambda w: vals(w, cap)[1]}]
    cons.extend({"type": "ineq", "fun": lambda w, n=name: vals(w, cap)[2][n]} for name in names)
    return cons


def run_cap(cap: str, n_random: int = 240):
    clusters: dict[tuple[str, ...], list[tuple[float, np.ndarray, float]]] = defaultdict(list)
    cons = constraints(cap)
    for w0 in starts_for(cap, n_random):
        res = minimize(
            lambda w: vals(w, cap)[0],
            w0,
            method="SLSQP",
            bounds=[(1.0, 80.0)] * 7,
            constraints=cons,
            options={"maxiter": 2000, "ftol": 1e-12, "disp": False},
        )
        if not res.success:
            continue
        phi, dphi, sl, x = vals(res.x, cap)
        if abs(dphi) > 2e-6 or min(sl.values()) < -2e-6:
            continue
        active = tuple(sorted(k for k, vv in sl.items() if vv < 2e-5))
        clusters[active].append((float(phi), res.x, x))
    return clusters


def main() -> None:
    unknown = []
    for cap in CAPS:
        clusters = run_cap(cap)
        print("CAP", cap, "clusters", len(clusters))
        for active, pts in sorted(clusters.items(), key=lambda kv: min(p[0] for p in kv[1])):
            pts.sort(key=lambda p: p[0])
            label = KNOWN.get(cap, {}).get(active, "UNKNOWN")
            print(" ", label, "phi", round(pts[0][0], 10), "count", len(pts), "active", active)
            if label == "UNKNOWN":
                unknown.append((cap, active, pts[0][0], pts[0][1], pts[0][2]))
    if unknown:
        print("UNKNOWN CRITICAL SUPPORTS:")
        for cap, active, phi, w, x in unknown:
            print(" ", cap, round(phi, 12), active, "x", x, np.array2string(w, precision=12))
        raise SystemExit(1)
    print("PASS-STRESS y=1,u=1 critical leaves found only known support families")


if __name__ == "__main__":
    main()
