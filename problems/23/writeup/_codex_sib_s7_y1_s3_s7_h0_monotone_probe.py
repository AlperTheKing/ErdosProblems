"""Numerical derivative stress for H=0 triple face variables.

Uses the shifted parametrization from the H0 probes and checks partial
derivatives of Phi with respect to A,B,F,V,S,R on random feasible samples.
"""

from __future__ import annotations

import random

import sympy as sp

from _codex_sib_s7_y1_s3_s7_h0_cone_probe import VARS, build_face


def main() -> None:
    phi_num, _u1, _s2 = build_face()

    # Rebuild the rational Phi, not just its numerator.
    A, B, F, V, S, R = VARS
    a = 1 + A
    b = 1 + B
    f = 1 + F
    v = 1 + V
    e = v + S
    c = e + R
    d = b + R
    x = b + c - 1
    u = (a * e + b * f + c * f - v * (b + c)) / (b + c - 1)
    core = a + b + c + d + e + f
    n = core + x + 1 + u + v
    m = x * u + x * v + v
    yy = a * c + b * f + c * f
    z = e * yy + d * f * (b + c)
    aa = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    bb = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    phi = 2 * (n * n - 25 * m) - 75 * (x * (u + v) * aa / z + v * bb / (e * yy) - core)
    funcs = [sp.lambdify(VARS, sp.diff(phi, var), "math") for var in VARS]
    u1_func = sp.lambdify(VARS, u - 1, "math")
    s2_func = sp.lambdify(VARS, d + e - u - v, "math")

    rng = random.Random(881911)
    neg = [0 for _ in VARS]
    worst = [(0.0, None) for _ in VARS]
    feasible = 0
    for _ in range(50000):
        vals = tuple(5.0 * rng.random() for _ in VARS)
        if u1_func(*vals) < -1e-9 or s2_func(*vals) < -1e-9:
            continue
        feasible += 1
        for i, fn in enumerate(funcs):
            val = fn(*vals)
            if val < 0:
                neg[i] += 1
                if val < worst[i][0]:
                    worst[i] = (val, vals)
    print(f"H0-MONO feasible={feasible}")
    for var, nbad, item in zip(VARS, neg, worst):
        print(f"H0-MONO d/d{var}: negatives={nbad} worst={item[0]}")
        if item[1] is not None:
            print(f"H0-MONO d/d{var} witness={item[1]}")


if __name__ == "__main__":
    main()
