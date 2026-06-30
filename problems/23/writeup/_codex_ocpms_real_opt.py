"""Floating real optimization smoke test for seven-cut PMS margin."""

import random

import numpy as np
from scipy.optimize import minimize

import _codex_ocpms_weight_formula as wf


def vals(x):
    w = np.asarray(x)
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    m = w1 * w9 + w2 * w7 + w7 * w9
    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    a27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    a19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z79 = w0 * w5 * w6 + w3 * w4 * w8 + w3 * w6 * w8 + w4 * w5 * w8 + w5 * w6 * w8
    a79 = (
        w0 * w5
        + w0 * w6
        + w3 * w4
        + w3 * w6
        + w3 * w8
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )
    I = w1 + w2 + w7 + w9 + w2 * w7 * a27 / z27 + w1 * w9 * a19 / z19 + w7 * w9 * a79 / z79
    N = float(np.sum(w))
    return 2 * (N * N - 25 * m) - 75 * (I - N)


def cons_fun(x):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = x
    m = w1 * w9 + w2 * w7 + w7 * w9
    return np.array(
        [
            w5 - w9,
            w6 - w7,
            w3 + w5 - w2 - w9,
            w4 + w6 - w1 - w7,
            w0 * w6 + w3 * w8 + w5 * w8 - m,
            w0 * w5 + w3 * w8 + w5 * w8 - m,
            w0 * w6 + w4 * w8 + w6 * w8 - m,
        ]
    )


def main():
    rng = random.Random(20260630)
    constraints = [{"type": "ineq", "fun": lambda x, i=i: cons_fun(x)[i]} for i in range(7)]
    bounds = [(1, 50)] * 10
    best = None
    for k in range(50):
        if k == 0:
            x0 = np.ones(10)
        else:
            # Generate feasible-ish points by rejection.
            x0 = None
            for _ in range(10000):
                cand = np.array([1 + 9 * rng.random() for _ in range(10)])
                if np.all(cons_fun(cand) >= -1e-9):
                    x0 = cand
                    break
            if x0 is None:
                x0 = np.ones(10)
        res = minimize(vals, x0, method="SLSQP", bounds=bounds, constraints=constraints, options={"maxiter": 1000, "ftol": 1e-10})
        item = (res.fun, res.success, res.x, cons_fun(res.x))
        if best is None or item[0] < best[0]:
            best = item
            print("best", k, "fun", item[0], "success", item[1], "x", item[2], "cons", item[3])


if __name__ == "__main__":
    main()
