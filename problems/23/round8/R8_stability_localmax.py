"""R8: CONTINUOUS local-maximum test for psi, with exact certificates.

At a point x, psi = min over cuts of q_S(x); by Danskin the directional derivative in
direction d is  min over ACTIVE cuts of <grad q_S(x), d>.  So x is a first-order local
maximum iff the LP

     max t   s.t.   <grad q_S(x), d> >= t  for every active S,
                    sum d = 0,   d_v >= 0 whenever x_v = 0,   -1 <= d <= 1

has optimum t* <= 0.  If t* > 0 we EXHIBIT d and verify exactly (Fractions) that
psi(x + eps d) > psi(x) for an explicit rational eps -- a rigorous refutation.

Run: python R8_stability_localmax.py
"""
import sys, os
from fractions import Fraction as F
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import (Graph, C, blowup_C5, petersen, wagner, grotzsch, circle_graph,
                               psi_exact, cut_mono_masks)
from R8_stability_secondorder import build_twin_graph


def active(g, x, cuts):
    val, _ = psi_exact(g, x, cuts)
    E = g.edges
    out = []
    for (Sm, mono) in cuts:
        s = F(0)
        for k in mono:
            u, v = E[k]
            s += x[u] * x[v]
        if s == val:
            out.append(mono)
    return val, out


def ascent_direction(g, x, cuts):
    """Returns (t*, d) from the LP; d as floats."""
    from scipy.optimize import linprog
    val, act = active(g, x, cuts)
    E, n = g.edges, g.n
    G = np.zeros((len(act), n))
    xf = np.array([float(z) for z in x])
    for r, mono in enumerate(act):
        for k in mono:
            u, v = E[k]
            G[r, u] += xf[v]
            G[r, v] += xf[u]
    A_ub = np.hstack([-G, np.ones((len(act), 1))])
    b_ub = np.zeros(len(act))
    A_eq = np.zeros((1, n + 1)); A_eq[0, :n] = 1.0
    bounds = [((0.0 if x[i] == 0 else -1.0), 1.0) for i in range(n)] + [(None, 1.0)]
    r = linprog(c=np.concatenate([np.zeros(n), [-1.0]]), A_ub=A_ub, b_ub=b_ub,
                A_eq=A_eq, b_eq=[0.0], bounds=bounds, method="highs")
    if not r.success:
        return None, None, val, len(act)
    return r.x[-1], r.x[:n], val, len(act)


def certify(g, x, tag):
    cuts = cut_mono_masks(g)
    t, d, val, nact = ascent_direction(g, x, cuts)
    if t is None:
        print(f"  {tag}: LP failed"); return
    if t <= 1e-9:
        print(f"  {tag}: psi = {val} = {float(val):.6f}, |active| = {nact}, "
              f"LP t* = {t:.2e}  ->  FIRST-ORDER LOCAL MAX")
        return True
    # rationalise d and verify exactly
    for den in (60, 120, 300, 600, 1200, 6000):
        dr = [F(int(round(z * den)), den) for z in d]
        s = sum(dr)
        dr = [dr[i] - (s / g.n if x[i] > 0 else 0) for i in range(g.n)]
        s = sum(dr)
        if s != 0:
            k = max(range(g.n), key=lambda i: (x[i] > 0, abs(dr[i])))
            dr[k] -= s
        if any(dr[i] < 0 and x[i] == 0 for i in range(g.n)):
            continue
        for eps in (F(1, 50), F(1, 200), F(1, 1000), F(1, 5000), F(1, 20000)):
            y = [x[i] + eps * dr[i] for i in range(g.n)]
            if any(z < 0 for z in y) or sum(y) != 1:
                continue
            v2, _ = psi_exact(g, y, cuts)
            if v2 > val:
                print(f"  {tag}: psi = {val} = {float(val):.6f}, |active| = {nact}, LP t* = {t:.4f}"
                      f"  ->  NOT a local max; exact witness psi(x+{eps}d) = {v2} > {val}")
                return False
    print(f"  {tag}: psi = {val}, LP t* = {t:.4f} > 0 -> not a local max (no rational witness found)")
    return False


if __name__ == "__main__":
    print("=== C5: the grid-local maxima found at q = 25 ===")
    g = C(5)
    for a in [(5,5,5,5,5), (4,5,4,5,7), (4,5,4,6,6), (3,6,3,6,7), (4,4,4,4,9), (2,5,2,5,6)]:
        if sum(a) not in (25, 20):
            continue
        q = sum(a)
        certify(g, [F(t, q) for t in a], f"C5  a={a}/{q}")

    print("\n=== Wagner Gamma_8: grid-local maxima at q = 25 ===")
    g = wagner()
    for a in [(0,5,0,5,5,0,5,5), (1,4,4,1,4,5,1,5), (0,4,0,4,5,0,5,7), (1,3,1,3,6,1,6,4)]:
        certify(g, [F(t, 25) for t in a], f"Wagner a={a}/25")

    print("\n=== Petersen: a C5-concentration and a perturbation ===")
    g = petersen()
    for a in [(0,0,0,0,0,4,4,4,4,4), (1,0,0,0,0,3,4,4,4,4)]:
        certify(g, [F(t, 20) for t in a], f"Petersen a={a}/20")

    print("\n=== C5[2] plateau points ===")
    g = blowup_C5([2, 2, 2, 2, 2])
    for a in [(4,0,4,0,4,0,4,0,4,0), (2,2,1,3,4,0,3,1,0,4)]:
        certify(g, [F(t, 20) for t in a], f"C5[2] a={a}/20")

    print("\n=== incomplete twin graph (C5[2,2,1,1,1] minus one twin-twin edge) ===")
    g = build_twin_graph({(5, 6)})
    for a in [(4,4,4,4,4,0,0), (4,0,4,4,4,0,4), (3,3,4,4,4,1,1)]:
        certify(g, [F(t, 20) for t in a], f"H7- a={a}/20")
