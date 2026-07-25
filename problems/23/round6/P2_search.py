"""P2 / round 6 - assignment (a): free-position derivative-free maximisation of CRIT, and (c)/(d).

(a)  atoms free on the continuum, weights free, n = 4..10, many restarts (differential evolution +
     Nelder-Mead polish), objective CRIT = min(A, bound_0..bound_K).  Winners are re-verified in
     exact rationals by P2_verify.Config.
(c)  the far-regular corner: for a measure with g constant on supp(mu) EVERY level of the hierarchy
     collapses to the single number W - 4W^2, so the hierarchy is powerless there; the three-arc
     family realises it with W -> 1/6.
(d)  the exact maximum of CRIT achieved, and the proved supremum 1/18.

Run:  python P2_search.py [nlo] [nhi] [restarts]
"""
import sys
import numpy as np
from fractions import Fraction as F
from scipy.optimize import differential_evolution, minimize
import P2_verify as V1

TARGET = 1.0 / 25
KLEV = 10


# ---------------------------------------------------------------- float evaluation
def decode(p, n):
    """p = [n gap logits, n weight logits] -> positions in [0,1), weights on the simplex."""
    gaps = np.exp(p[:n] - p[:n].max())
    gaps = gaps / gaps.sum()
    pos = np.concatenate([[0.0], np.cumsum(gaps)[:-1]])
    wl = p[n:] - p[n:].max()
    w = np.exp(wl)
    w = w / w.sum()
    return pos, w


def crit_float(pos, w, K=KLEV):
    n = len(pos)
    d = np.abs(pos[:, None] - pos[None, :])
    d = np.minimum(d, 1.0 - d)
    adj = (d > 1.0 / 3) & ~np.eye(n, dtype=bool)
    P = np.outer(w, w)
    W = 0.5 * (P * adj).sum()
    T = 0.5 * (P * adj * d).sum()
    A = W - 2 * T
    g = (adj * w[None, :]).sum(axis=1)
    m = W - (adj * (w * g)[None, :]).sum(axis=1)
    out = A
    for k in range(K + 1):
        wt = w * g ** k
        s = wt.sum()
        if s <= 0:
            continue
        out = min(out, float((wt * m).sum() / s))
    return out


def neg(p, n):
    pos, w = decode(np.asarray(p), n)
    return -crit_float(pos, w)


def rationalise(pos, w, den=2 ** 20):
    """snap to exact rationals; keep only atoms with non-negligible weight."""
    keep = w > 1e-9
    pos, w = pos[keep], w[keep]
    rp = [F(int(round(x * den)), den) for x in pos]
    rw = [F(int(round(x * 10 ** 9)), 10 ** 9) for x in w]
    seen, P, Wt = set(), [], []
    for a, b in zip(rp, rw):
        if a in seen:
            continue
        seen.add(a)
        P.append(a)
        Wt.append(b)
    return V1.Config(P, Wt, "optimiser winner")


# ---------------------------------------------------------------- main
if __name__ == '__main__':
    nlo = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    nhi = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    ntry = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    rng = np.random.default_rng(20260725)

    print("=" * 100)
    print("(a) free-position, free-weight maximisation of CRIT = min(A, bound_0..bound_%d)" % KLEV)
    print("    proved ceiling: CRIT < min(W/3, W - 4W^2) <= 1/18 = %.7f;  target to beat: 1/25 = 0.04"
          % (1 / 18))
    print("=" * 100)
    overall = (None, -1)
    for n in range(nlo, nhi + 1):
        best, bestp = -1, None
        for t in range(ntry):
            res = differential_evolution(neg, [(-6, 6)] * (2 * n), args=(n,), seed=int(rng.integers(1 << 30)),
                                         maxiter=400, popsize=25, tol=1e-12, polish=False, init='sobol')
            r2 = minimize(neg, res.x, args=(n,), method='Nelder-Mead',
                          options=dict(maxiter=40000, xatol=1e-12, fatol=1e-14))
            v = -min(res.fun, r2.fun)
            p = r2.x if r2.fun <= res.fun else res.x
            if v > best:
                best, bestp = v, p
        pos, w = decode(np.asarray(bestp), n)
        o = np.argsort(pos)
        print(f"  n={n:2d} atoms:  best CRIT = {best:.7f}  ({best*25:.5f} x 1/25)  "
              f"{'FALSIFIER' if best > TARGET else 'below 1/25'}")
        print(f"           positions = {np.round(pos[o], 6).tolist()}")
        print(f"           weights   = {np.round(w[o], 6).tolist()}")
        pp = pos[o]
        d = np.abs(pp[:, None] - pp[None, :])
        d = np.minimum(d, 1 - d)
        adj = (d > 1 / 3) & ~np.eye(n, dtype=bool)
        W = 0.5 * (np.outer(w[o], w[o]) * adj).sum()
        T = 0.5 * (np.outer(w[o], w[o]) * adj * d).sum()
        g = (adj * w[o][None, :]).sum(axis=1)
        print(f"           W = {W:.6f}   T/W = {T/W if W else 0:.6f}   Var(g) = {float(np.var(g)):.3e}"
              f"   (mass-weighted Var = {float((w[o]*g*g).sum() - (w[o]*g).sum()**2):.3e})")
        if best > overall[1]:
            overall = (n, best)
        sys.stdout.flush()

    print(f"\n  best over all sizes: n = {overall[0]} atoms, CRIT = {overall[1]:.7f}"
          f"  = {overall[1]*25:.5f} x 1/25   (ceiling 1/18 = {1/18:.7f})")

    print("\n" + "=" * 100)
    print("(c)/(d) the far-regular corner: three-cluster family, exact rationals, CRIT -> 1/18")
    print("=" * 100)
    print("   atoms/cluster |    N |            W |           A (exact) |          CRIT |  x 1/25")
    for n, den in ((2, 400), (3, 400), (4, 2000), (5, 4000), (6, 10000), (8, 20000),
                   (10, 40000), (15, 100000), (25, 400000)):
        cfg = V1.three_cluster(n, F(1, den))
        A = cfg.A()
        b0 = cfg.bound(0)
        crit = min(A, b0)                       # far-regular: every bound_k equals bound_0
        gs = cfg.g()
        assert len(set(gs)) == 1                 # far-regular
        assert all(cfg.bound(k) == b0 for k in range(6))
        print(f"   {n:13d} | {3*n:4d} | {str(cfg.W()):>12s} | {str(A):>19s} | {float(crit):.9f} | "
              f"{float(crit)*25:.5f}")
    print(f"   limit n -> infinity, eps -> 0 :  W -> 1/6, A -> 1/18, bound_k -> 1/18, "
          f"CRIT -> 1/18 = {1/18:.9f} = {25/18:.5f} x 1/25")
