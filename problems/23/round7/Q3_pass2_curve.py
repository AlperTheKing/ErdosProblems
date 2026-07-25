"""Q3 PASS 2 -- exact one-parameter trade-off curves through the extremal point.

For a triangle-free H and a weighting x(t) that starts (t=0) at a balanced C5
concentration, compute EXACTLY (Fractions)

    psi(t)   = min over all cuts of the monochromatic mass,
    d(t)     = min over phi : V -> Z5 of the weighted edit distance to B_phi,
    deficit  = 1/25 - psi(t),          R = d(t) / deficit(t).

The point of the exercise: base fact (7) says every induced-C5 concentration is
a FIRST-ORDER local maximum of psi.  If the deficit is Theta(t) the trade-off is
linear and perfect stability survives along that direction; if the deficit is
Theta(t^2) while d = Theta(t), then R ~ 1/t -> infinity and perfect stability is
FALSE with an exact witness.
"""
from fractions import Fraction as F
from itertools import product
import sys
from Q3_pass2_core import prism, petersen, circle_graph, c5_blowup, blowup_edge


def psi_exact(n, edges, w):
    """exact min over all 2^(n-1) cuts of the monochromatic mass; returns (val, cut)."""
    best, bestS = None, None
    for s in range(1 << (n - 1)):
        tot = 0
        for u, v in edges:
            if ((s >> u) & 1) == ((s >> v) & 1):
                tot += w[u] * w[v]
        if best is None or tot < best:
            best, bestS = tot, s
    return best, bestS


def dist_exact_w(n, edges, w):
    """exact min over phi:V->Z5 of the weighted edit distance (branch and bound)."""
    E = set((min(u, v), max(u, v)) for u, v in edges)
    same = [[1 if blowup_edge(a, b) else 0 for b in range(5)] for a in range(5)]
    order = sorted(range(n), key=lambda v: -w[v])          # heavy vertices first
    phi = [-1] * n
    best = [None, None]

    def pcost(u, v, a, b):
        e = 1 if (min(u, v), max(u, v)) in E else 0
        return w[u] * w[v] if e != same[a][b] else 0

    def rec(k, cur):
        if best[0] is not None and cur >= best[0]:
            return
        if k == n:
            best[0] = cur
            best[1] = list(phi)
            return
        # admissible bound: each unplaced vertex against the placed ones
        lb = cur
        for idx in range(k, n):
            v = order[idx]
            mv = None
            for a in range(5):
                c = 0
                for j in range(k):
                    u = order[j]
                    c += pcost(u, v, phi[u], a)
                if mv is None or c < mv:
                    mv = c
            lb += mv
            if best[0] is not None and lb >= best[0]:
                return
        v = order[k]
        rng = [0] if k == 0 else range(5)
        cand = []
        for a in rng:
            c = 0
            for j in range(k):
                u = order[j]
                c += pcost(u, v, phi[u], a)
            cand.append((c, a))
        cand.sort(key=lambda z: z[0])
        for c, a in cand:
            phi[v] = a
            rec(k + 1, cur + c)
            phi[v] = -1

    rec(0, 0)
    return best[0], best[1]


def curve(name, n, edges, wfun, ts):
    print(f"### {name}   (n={n}, |E|={len(edges)})")
    print(f"{'t':>12} {'psi':>18} {'1/25-psi':>18} {'d':>18} {'R=d/deficit':>14}")
    rows = []
    for t in ts:
        w = wfun(t)
        assert sum(w) == 1, (name, t, sum(w))
        p, S = psi_exact(n, edges, w)
        d, phi = dist_exact_w(n, edges, w)
        defc = F(1, 25) - p
        R = (d / defc) if defc != 0 else None
        rows.append((t, p, defc, d, R))
        print(f"{str(t):>12} {str(p):>18} {str(defc):>18} {str(d):>18} "
              f"{(str(R) + ' = ' + str(round(float(R), 4))) if R is not None else '-':>14}")
    return rows


# ---------------------------------------------------------------- families

def prism_w(t):
    """outer C5 weight 1/5 - t, inner C5 weight t   (t=0 -> C5 uniform)."""
    return [F(1, 5) - t] * 5 + [t] * 5


def petersen_w(t):
    return [F(1, 5) - t] * 5 + [t] * 5


def c5_pendant():
    """C5 on 0..4 plus a pendant vertex 5 attached to 0."""
    n, e = c5_blowup([1] * 5)
    return 6, e + [(0, 5)]


def c5_pendant_w(t):
    return [F(1, 5) - F(t, 5)] * 5 + [t]


def wagner_w(t):
    """Gamma_8 = Wagner.  Support {0,1,2,5,6,7} ... use the C5 that sits inside."""
    return None


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "prism"
    ts = [F(0), F(1, 100), F(1, 50), F(1, 20), F(1, 15), F(1, 12), F(1, 10)]
    if which == "prism":
        n, e = prism()
        curve("pentagonal prism C5[]K2, inner weight t", n, e, prism_w, ts)
    elif which == "petersen":
        n, e = petersen()
        curve("Petersen, inner (pentagram) weight t", n, e, petersen_w, ts)
    elif which == "pendant":
        n, e = c5_pendant()
        curve("C5 + pendant, pendant weight t", n, e, c5_pendant_w,
              [F(0), F(1, 100), F(1, 50), F(1, 20), F(1, 10), F(1, 6)])
    elif which == "all":
        for w in ("prism", "petersen", "pendant"):
            sys.argv = [sys.argv[0], w]
            main()
            print()


if __name__ == "__main__":
    main()
