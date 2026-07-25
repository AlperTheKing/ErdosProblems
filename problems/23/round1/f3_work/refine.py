"""Continuous local refinement of  max_x min_S Q_S(x)  by constraint generation + SLSQP.

Epigraph form:   max t  s.t.  Q_S(x) >= t for S in working set,  sum x = 1,  x >= 0.
The working set starts from the currently active cuts and grows with the most violated cut.
Output is then rounded to a rational point and re-verified with EXACT integer arithmetic,
so nothing on the acceptance path depends on floating point.
"""
import numpy as np
from scipy.optimize import minimize


def refine(t, x0, rounds=12):
    n = t.n
    x = np.maximum(np.asarray(x0, float), 0)
    x = x / x.sum()
    work = set()
    best = (None, None)
    for _ in range(rounds):
        p = x[t.eu] * x[t.ev]
        vals = t.M @ p
        order = np.argsort(vals)[:3]
        before = len(work)
        work.update(int(i) for i in order)
        rows = np.array(sorted(work))
        Mw = t.M[rows]                      # (k, m)

        def negt(z):
            return -z[-1]

        def cons_f(z):
            xx = z[:-1]
            pp = xx[t.eu] * xx[t.ev]
            return Mw @ pp - z[-1]

        z0 = np.concatenate([x, [float((Mw @ p).min())]])
        cons = [{"type": "ineq", "fun": cons_f},
                {"type": "eq", "fun": lambda z: z[:-1].sum() - 1.0}]
        bnds = [(0, 1)] * n + [(None, None)]
        r = minimize(negt, z0, method="SLSQP", bounds=bnds, constraints=cons,
                     options={"maxiter": 300, "ftol": 1e-14})
        xn = np.maximum(r.x[:-1], 0)
        if xn.sum() <= 0:
            break
        xn /= xn.sum()
        pn = xn[t.eu] * xn[t.ev]
        vn = float((t.M @ pn).min())
        vo = float((t.M @ (x[t.eu] * x[t.ev])).min())
        if vn > vo + 1e-15:
            x = xn
        if len(work) == before and vn <= vo + 1e-15:
            break
    p = x[t.eu] * x[t.ev]
    return x, float((t.M @ p).min())


def exact_check(t, x, denoms=(25, 50, 100, 200, 400, 1000, 2500)):
    """round x to integer weights with several denominators; return best EXACT (ratio,D,w,bip)"""
    best = (0.0, None, None, None)
    for D in denoms:
        w = np.floor(np.asarray(x) * D)
        rem = int(D - w.sum())
        frac = np.asarray(x) * D - w
        for i in np.argsort(-frac)[:rem]:
            w[i] += 1
        if w.sum() != D or w.min() < 0:
            continue
        b, _ = t.bip(w)
        r = 25.0 * b / D ** 2
        if r > best[0]:
            best = (r, D, [int(v) for v in w], b)
    return best
