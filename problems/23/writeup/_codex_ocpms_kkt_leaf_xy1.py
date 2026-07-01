"""Floating diagnostic for the first OC-PMS KKT leaf.

Leaf:

    x = y = 1,
    m = u + v + u v = Dj,  j in {D0,D27,D19},

with the cap-tangent stationarity equation

    (H-rho-tau*v)(1+u) = (H-sigma-tau*u)(1+v),
    H = 4(C + 2 + u + v).

This is not a proof script.  It searches integer/random cores a,b,c,p,q,r>=1
for floating counterexamples to the proposed first KKT leaf before investing
in exact denominator-cleared certificates.
"""

import argparse
import itertools
import random

from scipy.optimize import brentq


def constants(core):
    a, b, c, p, q, r = core
    C = a + b + c + p + q + r
    D27 = a * p + b * r + p * r
    D19 = a * q + c * r + q * r
    D0 = a * q + b * r + p * r
    D79 = a * p * q + b * c * r + b * q * r + c * p * r + p * q * r
    A27 = a * p + a * q + b * q + b * r + p * q + p * r + q * r
    A19 = a * p + a * q + c * p + c * r + p * q + p * r + q * r
    A79 = (
        a * p
        + a * q
        + b * c
        + b * q
        + b * r
        + c * p
        + c * r
        + p * q
        + p * r
        + q * r
    )
    alpha = A27 / (q * D27)
    beta = A19 / (p * D19)
    gamma = A79 / D79
    return dict(C=C, D0=D0, D27=D27, D19=D19, rho=50 + 75 * alpha, sigma=50 + 75 * beta, tau=50 + 75 * gamma)


def feasible_uv(core, u, v, cap_value):
    a, b, c, p, q, r = core
    cs = constants(core)
    if u < 1 - 1e-9 or v < 1 - 1e-9:
        return False
    if u > q + 1e-9 or v > p + 1e-9:
        return False
    if 1 + u > c + q + 1e-9:
        return False
    if 1 + v > b + p + 1e-9:
        return False
    m = u + v + u * v
    if abs(m - cap_value) > 1e-6 * max(1.0, cap_value):
        return False
    return m <= cs["D0"] + 1e-9 and m <= cs["D27"] + 1e-9 and m <= cs["D19"] + 1e-9


def F_value(core, u, v):
    cs = constants(core)
    C = cs["C"]
    Hs = C + 2 + u + v
    return 2 * Hs * Hs + 75 * C - cs["rho"] * u - cs["sigma"] * v - cs["tau"] * u * v


def tangent(core, cap_value, u):
    cs = constants(core)
    v = (cap_value - u) / (u + 1)
    H = 4 * (cs["C"] + 2 + u + v)
    return (H - cs["rho"] - cs["tau"] * v) * (1 + u) - (H - cs["sigma"] - cs["tau"] * u) * (1 + v)


def feasible_interval(core, cap_value):
    a, b, c, p, q, r = core
    lo = 1.0
    hi = min(float(q), float(c + q - 1))
    # v=(D-u)/(u+1), so v>=1 gives u <= (D-1)/2.
    hi = min(hi, (cap_value - 1) / 2)
    # v<=p and v<=b+p-1 give lower bounds on u.
    v_hi = min(float(p), float(b + p - 1))
    lo = max(lo, (cap_value - v_hi) / (v_hi + 1))
    if lo > hi + 1e-9:
        return None
    return lo, hi


def roots_for_cap(core, cap_name):
    cap_value = constants(core)[cap_name]
    if cap_value > min(constants(core)[k] for k in ("D0", "D27", "D19")):
        return []
    iv = feasible_interval(core, cap_value)
    if iv is None:
        return []
    lo, hi = iv
    pts = [lo + (hi - lo) * i / 200 for i in range(201)]
    vals = [tangent(core, cap_value, x) for x in pts]
    roots = []
    for x0, x1, y0, y1 in zip(pts, pts[1:], vals, vals[1:]):
        if abs(y0) < 1e-8:
            roots.append(x0)
        if y0 == 0 or y0 * y1 > 0:
            continue
        try:
            roots.append(brentq(lambda z: tangent(core, cap_value, z), x0, x1, maxiter=100))
        except ValueError:
            pass
    if abs(vals[-1]) < 1e-8:
        roots.append(hi)

    out = []
    seen = set()
    for u in roots:
        key = round(u, 10)
        if key in seen:
            continue
        seen.add(key)
        v = (cap_value - u) / (u + 1)
        if feasible_uv(core, u, v, cap_value):
            out.append((u, v, F_value(core, u, v)))
    return out


def scan_core(core):
    out = []
    for cap in ("D0", "D27", "D19"):
        for u, v, val in roots_for_cap(core, cap):
            out.append((val, cap, u, v))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--box", type=int, default=4)
    ap.add_argument("--random", type=int, default=1000)
    ap.add_argument("--max-core", type=float, default=20.0)
    ap.add_argument("--seed", type=int, default=300630)
    args = ap.parse_args()

    worst = None
    roots = 0
    for core in itertools.product(range(1, args.box + 1), repeat=6):
        got = scan_core(tuple(float(x) for x in core))
        roots += len(got)
        if got and (worst is None or got[0][0] < worst[0]):
            worst = (got[0][0], core, got[0])
            print("box worst", worst, flush=True)

    rng = random.Random(args.seed)
    for i in range(args.random):
        core = tuple(1.0 + (args.max_core - 1.0) * rng.random() for _ in range(6))
        got = scan_core(core)
        roots += len(got)
        if got and (worst is None or got[0][0] < worst[0]):
            worst = (got[0][0], core, got[0])
            print("random worst", worst, flush=True)

    print("=" * 60)
    print("roots:", roots)
    print("worst:", worst)
    print("VERDICT:", "NO FLOAT NEGATIVE ROOT" if worst is None or worst[0] >= -1e-7 else "FLOAT NEGATIVE ROOT")


if __name__ == "__main__":
    main()
