"""TASK 2 (step 2) -- how large can eta be before the REFINED bound stops giving 1/25?

Maximise  min_i F_i  over the relaxation
    z_m >= tau_m >= 0,  r_j >= 0, r0 >= 0,
    sum z + sum r + r0 = 1,     eta = sum tau + sum r + r0 <= c
and find the critical c where the max first exceeds 1/25.

F_i = z_i z_{i+1}
    + r_i tau_{i+2} + r_{i+1} tau_{i+4} + r_{i+2} tau_i + r_{i+4} tau_{i+1}
    + r_i r_{i+1} + r_i r_{i+3} + r_{i+1} r_{i+3} + r_{i+2} r_{i+4}
    + (1/2) r0 eta
(the relaxation IGNORES realisability by a graph, so the resulting threshold is
 valid for the theorem: it is a lower bound on the truth.)
"""
import numpy as np
from scipy.optimize import minimize, linprog
from fractions import Fraction as Fr

M5 = lambda k: k % 5


def unpack(v):
    return v[0:5], v[5:10], v[10:15], v[15]


def Fvec(v):
    z, tau, r, r0 = unpack(v)
    eta = tau.sum() + r.sum() + r0
    out = np.empty(5)
    for i in range(5):
        out[i] = (z[i] * z[M5(i + 1)]
                  + r[i] * tau[M5(i + 2)] + r[M5(i + 1)] * tau[M5(i + 4)]
                  + r[M5(i + 2)] * tau[i] + r[M5(i + 4)] * tau[M5(i + 1)]
                  + r[i] * r[M5(i + 1)] + r[i] * r[M5(i + 3)]
                  + r[M5(i + 1)] * r[M5(i + 3)] + r[M5(i + 2)] * r[M5(i + 4)]
                  + 0.5 * r0 * eta)
    return out


def maxmin(c, ntry=400, seed=0, no_r0=False):
    rng = np.random.default_rng(seed)
    best, bestv = -1, None
    for t in range(ntry):
        # start: random
        z = rng.random(5); z /= z.sum()
        rho = rng.random() * min(c, 0.5)
        tau = rng.random(5); tau *= max(c - rho, 0) / max(tau.sum(), 1e-9)
        r = rng.random(5); r *= rho / max(r.sum(), 1e-9)
        r0 = 0.0
        if not no_r0 and t % 3 == 0:
            r0, r = rho, np.zeros(5)
        z = z * (1 - rho)
        z = np.maximum(z, tau)
        v0 = np.concatenate([z, tau, r, [r0]])
        v0[0:5] *= (1 - v0[10:15].sum() - v0[15]) / max(v0[0:5].sum(), 1e-12)
        x0 = np.concatenate([v0, [Fvec(v0).min()]])

        cons = [
            {'type': 'eq', 'fun': lambda x: x[0:5].sum() + x[10:15].sum() + x[15] - 1},
            {'type': 'ineq', 'fun': lambda x: c - (x[5:10].sum() + x[10:15].sum() + x[15])},
            {'type': 'ineq', 'fun': lambda x: x[0:5] - x[5:10]},
            {'type': 'ineq', 'fun': lambda x: Fvec(x[:16]) - x[16]},
        ]
        if no_r0:
            cons.append({'type': 'eq', 'fun': lambda x: x[15]})
        bnds = [(0, 1)] * 16 + [(None, None)]
        try:
            res = minimize(lambda x: -x[16], x0, constraints=cons, bounds=bnds,
                           method='SLSQP', options={'maxiter': 300, 'ftol': 1e-12})
        except Exception:
            continue
        if not res.success:
            continue
        x = res.x
        if (x[0:5].sum() + x[10:15].sum() + x[15] > 1 + 1e-7
                or x[5:10].sum() + x[10:15].sum() + x[15] > c + 1e-7
                or (x[0:5] - x[5:10]).min() < -1e-7 or x[:16].min() < -1e-7):
            continue
        val = Fvec(x[:16]).min()
        if val > best:
            best, bestv = val, x[:16].copy()
    return best, bestv


if __name__ == '__main__':
    print("critical-c scan for the REFINED bound   (target: max min_i F_i <= 1/25 = %.6f)" % (1 / 25))
    print("%8s %12s %12s   %s" % ("c", "maxminF", "-1/25", "argmax (z|tau|r|r0)"))
    for c in [0.0769, 0.10, 0.14, 0.16, 0.18, 0.20, 0.2222, 0.24, 0.2666, 0.28, 0.30, 0.35]:
        b, v = maxmin(c, ntry=300, seed=1)
        print("%8.4f %12.8f %12.2e   %s" % (c, b, b - 1 / 25,
              np.round(v, 4) if v is not None else None))
    print()
    print("same scan with r0 = 0 (no R-vertices without a C-neighbour):")
    for c in [0.20, 0.2666, 0.30, 0.3333, 0.36, 0.40]:
        b, v = maxmin(c, ntry=300, seed=2, no_r0=True)
        print("%8.4f %12.8f %12.2e   %s" % (c, b, b - 1 / 25,
              np.round(v, 4) if v is not None else None))
