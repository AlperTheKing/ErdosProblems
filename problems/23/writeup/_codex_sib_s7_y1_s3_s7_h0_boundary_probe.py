"""Diagnostic gate for the y=1, s3=s7=0, H=0 boundary.

On the hard s3/s7 face, put H=b+c-d-e.  The H=0 boundary is the
triple face s3=s5=s7=0, with s4=s6=a(c-e).  This script records the
exact reduction and runs a bounded numerical stress probe to identify
which lower faces the remaining minimum appears to use.

This is not a positivity certificate; it is a routing diagnostic for the
next exact subface proof.
"""

from __future__ import annotations

import math
import random

import sympy as sp

import _codex_sib_s7_y1_fj_support_inventory as inv


def phi_value(a: float, b: float, c: float, d: float, e: float, f: float, x: float, u: float, v: float) -> float:
    s = a + b + c + d + e + f
    n = s + x + 1.0 + u + v
    m = x * u + x * v + v
    y = a * c + b * f + c * f
    z = e * y + d * f * (b + c)
    aa = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    bb = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2.0 * (n * n - 25.0 * m) - 75.0 * (x * (u + v) * aa / z + v * bb / (e * y) - s)


def symbolic_reduction() -> None:
    a, b, c, d, e, f, x, u, v = inv.VARS
    subs = {
        x: b + c - 1,
        d: b + c - e,
        u: (a * e + b * f + c * f - v * (b + c)) / (b + c - 1),
    }

    s = {name: sp.factor(expr.subs(subs)) for name, expr in inv.SLACKS.items()}
    assert sp.factor(s["s3"]) == 0
    assert sp.factor(s["s5"]) == 0
    assert sp.factor(s["s7"]) == 0
    assert sp.factor(s["s4"] - a * (c - e)) == 0
    assert sp.factor(s["s6"] - a * (c - e)) == 0

    # The remaining feasibility gates are s1, u1, and s2.
    denom = b + c - 1
    assert sp.factor(sp.denom(s["u1"]) - denom) == 0
    assert sp.factor(sp.denom(s["s2"]) - denom) == 0
    print("H0-BOUNDARY identities: s3=s5=s7=0 and s4=s6=a(c-e)")
    print(f"H0-BOUNDARY u1 numerator: {sp.factor(sp.together(s['u1']).as_numer_denom()[0])}")
    print(f"H0-BOUNDARY s2 numerator: {sp.factor(sp.together(s['s2']).as_numer_denom()[0])}")


def random_probe(samples: int = 20000, seed: int = 92317) -> None:
    rng = random.Random(seed)
    best = (math.inf, None)
    active_counts: dict[tuple[str, ...], int] = {}

    for _ in range(samples):
        # H=0 parametrization: e=v+S, c=e+C, d=b+C, x=b+c-1.
        a = 1.0 + 5.0 * rng.random()
        b = 1.0 + 5.0 * rng.random()
        f = 1.0 + 5.0 * rng.random()
        v = 1.0 + 5.0 * rng.random()
        s1 = 5.0 * rng.random()
        gap = 5.0 * rng.random()
        e = v + s1
        c = e + gap
        d = b + gap
        x = b + c - 1.0
        u = (a * e + b * f + c * f - v * (b + c)) / (b + c - 1.0)
        if u < 1.0:
            continue
        s2 = d + e - u - v
        if s2 < -1e-9:
            continue
        val = phi_value(a, b, c, d, e, f, x, u, v)
        slacks = {
            "a1": a - 1.0,
            "b1": b - 1.0,
            "f1": f - 1.0,
            "s1": s1,
            "R": gap,
            "u1": u - 1.0,
            "s2": s2,
        }
        near = tuple(sorted(k for k, z in slacks.items() if z < 1e-5))
        active_counts[near] = active_counts.get(near, 0) + 1
        if val < best[0]:
            best = (val, (a, b, c, d, e, f, x, u, v, s2, s1, gap, near))

    assert best[1] is not None
    print(f"H0-BOUNDARY random feasible samples={sum(active_counts.values())}/{samples}")
    print(f"H0-BOUNDARY best_phi={best[0]:.12g}")
    labels = ("a", "b", "c", "d", "e", "f", "x", "u", "v", "s2", "s1", "R", "near")
    print("H0-BOUNDARY best_point=" + ", ".join(f"{k}={val}" for k, val in zip(labels, best[1])))
    print("PASS H0 boundary diagnostic completed")


def main() -> None:
    symbolic_reduction()
    random_probe()


if __name__ == "__main__":
    main()
