"""Continuous fixed-core endpoint optimization for the seven-cut PMS target."""

import random

import numpy as np
from scipy.optimize import minimize


def constants(core):
    w0, w3, w4, w5, w6, w8 = core
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
    K = sum(core)
    A = w0 * w6 + w3 * w8 + w5 * w8
    B = w0 * w5 + w3 * w8 + w5 * w8
    C = w0 * w6 + w4 * w8 + w6 * w8
    return K, a19 / z19, a27 / z27, a79 / z79, A, B, C


def margin(core, end):
    x, y, u, v = end  # w1,w2,w7,w9
    K, c19, c27, c79, _A, _B, _C = constants(core)
    s = x + y + u + v
    m = x * v + y * u + u * v
    weighted = c19 * x * v + c27 * y * u + c79 * u * v
    return 2 * ((K + s) ** 2 - 25 * m) - 75 * (weighted - K)


def cons(core):
    w0, w3, w4, w5, w6, w8 = core
    K, c19, c27, c79, A, B, C = constants(core)

    def vals(end):
        x, y, u, v = end
        m = x * v + y * u + u * v
        return np.array(
            [
                w5 - v,
                w6 - u,
                w3 + w5 - y - v,
                w4 + w6 - x - u,
                A - m,
                B - m,
                C - m,
            ]
        )

    return vals


def active(core, end, tol=1e-6):
    names = ["v<=w5", "u<=w6", "y+v", "x+u", "A", "B", "C"]
    vals = cons(core)(end)
    return tuple(name for name, val in zip(names, vals) if abs(val) <= tol)


def optimize_core(core, starts=20, seed=0):
    rng = random.Random(seed)
    con = cons(core)
    constraints = [{"type": "ineq", "fun": lambda z, i=i: con(z)[i]} for i in range(7)]
    w0, w3, w4, w5, w6, w8 = core
    bounds = [(1, w4 + w6 - 1), (1, w3 + w5 - 1), (1, w6), (1, w5)]
    best = None
    for k in range(starts):
        if k == 0:
            x0 = np.ones(4)
        else:
            x0 = None
            for _ in range(1000):
                cand = np.array([rng.uniform(lo, hi) for lo, hi in bounds])
                if np.all(con(cand) >= -1e-9):
                    x0 = cand
                    break
            if x0 is None:
                x0 = np.ones(4)
        res = minimize(lambda z: margin(core, z), x0, method="SLSQP", bounds=bounds, constraints=constraints, options={"ftol": 1e-11, "maxiter": 1000})
        item = (res.fun, res.success, res.x, con(res.x), active(core, res.x))
        if best is None or item[0] < best[0]:
            best = item
    return best


def main():
    rng = random.Random(20260630)
    worst = None
    hist = {}
    cores = [tuple([1.0] * 6)]
    for _ in range(100):
        cores.append(tuple(1 + 5 * rng.random() for _ in range(6)))
    for i, core in enumerate(cores):
        best = optimize_core(core, starts=30, seed=i)
        hist[best[4]] = hist.get(best[4], 0) + 1
        if worst is None or best[0] < worst[0][0]:
            worst = (best, core)
            print("worst", worst)
    print("hist")
    for k, v in sorted(hist.items(), key=lambda kv: (-kv[1], kv[0])):
        print(v, k)


if __name__ == "__main__":
    main()
