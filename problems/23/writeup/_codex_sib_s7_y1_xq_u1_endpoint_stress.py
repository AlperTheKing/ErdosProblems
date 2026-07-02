"""Deterministic falsifier stress for the y=1, x=q, u=1 endpoint.

This is NOT a proof artifact.  It is a reproducible numerical guardrail for
the first endpoint-coverage theorem we still need to prove exactly.  The exact
positive families are checked elsewhere:

  * _codex_sib_s7_y1_xq_survivors.py
  * _codex_sib_s7_y1_xqA_drop_*.py
  * _codex_sib_s7_y1_xqB_drop_faces.py

Here we only ask whether a larger deterministic SLSQP battery finds an active
support outside the known x=q,u=1 endpoint families.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import minimize


CAPS = ("s4", "s5", "s6", "s7")

KNOWN = {
    ("f1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_A",
    ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1"): "XQ_B",
}


def eval_cap(w: np.ndarray, cap: str):
    a, b, c, d, e, f, x = w
    y = 1.0
    u = 1.0
    q = x
    v = x - 1.0
    m = x * q + v
    S = a + b + c + d + e + f
    N = S + y + x + q
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
    Phi = 2.0 * (N * N - 25.0 * m) - 75.0 * (x * q * A / Z + v * B / (e * Y) - S)
    sl = {
        "a1": a - 1.0,
        "b1": b - 1.0,
        "c1": c - 1.0,
        "d1": d - 1.0,
        "e1": e - 1.0,
        "f1": f - 1.0,
        "x1": x - 1.0,
        "v1": v - 1.0,
        "u1": 0.0,
        "s1": e - v,
        "s2": d + e - q,
        "s3": b + c - x - y,
    }
    for name, cm in caps.items():
        sl[name] = cm - m
    return Phi, sl


def starts_for(cap: str, n_random: int) -> list[np.ndarray]:
    rng = np.random.default_rng(abs(hash(("codex-xq-u1-stress", cap))) % (2**32))
    out: list[np.ndarray] = []

    # Known-family neighborhoods.
    for t in (1.0, 1.25, 1.75, 2.5, 4.0, 8.0, 16.0):
        x = t + 1.0
        out.append(np.array([t + 2.0 - 1.0 / t, 2.0, t, 2.0, t, 1.0, x], dtype=float))
        out.append(np.array([t + 2.0, 2.0, t, 1.0, t, 1.0, x], dtype=float))

    for _ in range(n_random):
        out.append(np.r_[1.0 + rng.random(6) * 12.0, 2.0 + rng.random() * 12.0])
    return out


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
        "s1",
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


def run_cap(cap: str, n_random: int = 300):
    clusters: dict[tuple[str, ...], list[tuple[float, np.ndarray]]] = defaultdict(list)
    cons = constraints(cap)
    for w0 in starts_for(cap, n_random):
        res = minimize(
            lambda w: eval_cap(w, cap)[0],
            w0,
            method="SLSQP",
            bounds=[(1.0, 80.0)] * 6 + [(2.0, 80.0)],
            constraints=cons,
            options={"maxiter": 2000, "ftol": 1e-12, "disp": False},
        )
        if not res.success:
            continue
        phi, sl = eval_cap(res.x, cap)
        if min(sl.values()) < -2e-6:
            continue
        active = tuple(sorted(k for k, vv in sl.items() if vv < 2e-5))
        clusters[active].append((float(phi), res.x))
    return clusters


def main() -> None:
    unknown: list[tuple[str, tuple[str, ...], float, np.ndarray]] = []
    for cap in CAPS:
        clusters = run_cap(cap)
        print("CAP", cap, "clusters", len(clusters))
        for active, pts in sorted(clusters.items(), key=lambda kv: min(p[0] for p in kv[1])):
            pts.sort(key=lambda p: p[0])
            label = KNOWN.get(active, "UNKNOWN")
            print(" ", label, "phi", round(pts[0][0], 10), "count", len(pts), "active", active)
            if label == "UNKNOWN":
                unknown.append((cap, active, pts[0][0], pts[0][1]))
    if unknown:
        print("UNKNOWN SUPPORTS:")
        for cap, active, phi, w in unknown:
            print(" ", cap, round(phi, 12), active, np.array2string(w, precision=12))
        raise SystemExit(1)
    print("PASS-STRESS y=1 x=q,u=1 endpoint found only known support families")


if __name__ == "__main__":
    main()
