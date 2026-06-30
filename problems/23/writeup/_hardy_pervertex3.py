"""PINPOINT the single N=23 failure of the load-weighted row-sum certificate H g >= 0, g = T.

g = T_v passed 0-fail on the ENTIRE census N<=9 (2300+ cuts), all chains, C5 blowups, Grotzsch N=11,
60 random N=11/12; it FAILED at exactly ONE vertex (v=2) of the N=23 Myc(Grotzsch) maxcut.

Two hypotheses for the single failure:
  (i)  the certified RATIONAL beta' < beta_L weakens Lstar (less positive mass) -> spurious failure; with TRUE
       beta_L (float) the row-sum (H_true g)_2 might be >= 0.
  (ii) g = T is genuinely not a valid Z-matrix certificate; a slightly different g (e.g. T_v + c) fixes it.

We compute, for the EXACT N=23 cut:
  - exact (H_rat g)_v for every v with g=T, identify all negative rows;
  - float (H_true g)_v with the true irrational beta_L for those rows;
  - search a 1-parameter family g_v = T_v + t (t>=0) and report the smallest t making H_rat g >= 0 (rational),
    and whether g = T_v works with TRUE beta (float).
This isolates whether the load vector is the right certificate modulo rational rounding.
"""
import math
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski
from _hardy_gate import BETA, build_H, cycle_laplacian_add
import random


def build_H_true_float(n, M, ell, T, cyc):
    """H with TRUE beta_L (float)."""
    H = [[0.0] * n for _ in range(n)]
    for v in range(n):
        H[v][v] = float(n) - float(T[v])
    for f in M:
        Qs = cyc[f]; L = ell[f]
        beta = L / (2 + 2 * math.cos(math.pi / L))
        w = beta / len(Qs)
        for Q in Qs:
            Ql = list(Q)
            for i in range(len(Ql)):
                a = Ql[i]; b = Ql[(i + 1) % len(Ql)]
                H[a][a] += w; H[b][b] += w
                H[a][b] -= w; H[b][a] -= w
    return H


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    assert Bconn(m2N, adj, side)
    st = struct_for_side(m2N, adj, side)
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    n = m2N
    N = F(n)

    H = build_H(n, M, ell, T, cyc, BETA)      # rational, beta' < beta
    Hf = build_H_true_float(n, M, ell, T, cyc)  # float, true beta

    g = [T[v] for v in range(n)]
    # exact row-sums with g=T (rational beta')
    r_rat = [sum(H[v][w] * g[w] for w in range(n)) for v in range(n)]
    neg_rat = [v for v in range(n) if r_rat[v] < 0]
    print("N=23 cut: vertices with T_v>N (overloaded):", [v for v in range(n) if T[v] > N])
    print("RATIONAL beta' : negative rows of (H g)_v, g=T :", neg_rat)
    for v in neg_rat:
        print("   v=%d  T_v=%s  (H_rat T)_v = %.6e" % (v, str(T[v]), float(r_rat[v])))

    # float true-beta row-sums with g=T
    gf = [float(T[v]) for v in range(n)]
    r_true = [sum(Hf[v][w] * gf[w] for w in range(n)) for v in range(n)]
    neg_true = [v for v in range(n) if r_true[v] < -1e-9]
    print("TRUE  beta (float): negative rows of (H g)_v, g=T (tol -1e-9):", neg_true)
    for v in (neg_rat + neg_true):
        print("   v=%d  (H_true T)_v = %.6e" % (v, r_true[v]))

    # smallest constant shift t in g = T + t making H_rat g >= 0 (rational).  Since H 1 = N - T,
    # (H (T + t1))_v = (H T)_v + t (N - T_v).  Solve per row r_rat[v] + t (N - T_v) >= 0.
    # For overloaded v (N - T_v < 0) larger t HURTS; for v with N-T_v>0 larger t helps. So a single t may not work;
    # report feasibility interval.
    lo = None; hi = None; feasible = True
    for v in range(n):
        a = r_rat[v]; b = (N - T[v])   # need a + t b >= 0
        if b > 0:
            bound = -a / b  # t >= bound
            if lo is None or bound > lo:
                lo = bound
        elif b < 0:
            bound = -a / b  # t <= bound  (dividing flips)
            # a + t b >=0 -> t <= -a/b since b<0
            if hi is None or bound < hi:
                hi = bound
        else:
            if a < 0:
                feasible = False
    print("constant-shift g = T + t feasibility: t in [%s, %s]  feasible=%s"
          % (None if lo is None else float(lo), None if hi is None else float(hi),
             feasible and (lo is None or hi is None or lo <= hi)))

    # Also: does g = T + 1 fix it? (we know it failed at v=2 in rational). Float?
    g2f = [float(T[v]) + 1.0 for v in range(n)]
    r2 = [sum(Hf[v][w] * g2f[w] for w in range(n)) for v in range(n)]
    print("TRUE beta, g=T+1: min row =", min(r2), "negs:", [v for v in range(n) if r2[v] < -1e-9])

    # The honest test of (H) itself at this cut: numpy min eigenvalue with true beta
    try:
        import numpy as np
        A = np.array([[float(Hf[i][j]) for j in range(n)] for i in range(n)])
        ev = np.linalg.eigvalsh(A)
        print("TRUE-beta H min eigenvalue (numpy):", float(ev[0]), " -> (H) PSD holds:", float(ev[0]) > -1e-9)
    except Exception as e:
        print("numpy unavailable:", e)


if __name__ == "__main__":
    main()
