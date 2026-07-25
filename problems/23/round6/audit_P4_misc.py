"""audit_P4_misc — the remaining P4 claims:
  (f)  A = W - 2T is EXACTLY the average of mono([a, a+1/2)) over a uniform on the circle
  (d)  the 'pairing hazard' example on Gamma_11
  (b)  delta(Gamma_m) > m/3 iff m = 2 (mod 3)
  (e)  3-fold measures have g(x) = 1/3 - mu({x})  (so 'no adjacent pairs' is false)
  P4 recommendation 1: 'any future certificate must use arcs of length strictly between 1/3 and 1/2'
"""
from fractions import Fraction as F
from itertools import combinations
from audit_P4_core import (adj_matrix, normalise, W_of, T_of, A_of, g_of, m_of, mono,
                           arcbound, circ_dist_steps)

ONE25 = F(1, 25)


def halfarc_average(M, x):
    """exact E_a[ mono([a, a+1/2)) ], a uniform on R/Z.
    The window is constant on each cell of the partition of [0,1) by the points k/(2M);
    take the midpoint of each cell and average with weight 1/(2M)."""
    adj = adj_matrix(M)
    tot = F(0)
    cells = 2 * M
    for j in range(cells):
        a = F(2 * j + 1, 2 * cells)          # midpoint of cell j, in units of the circle
        inA = [False] * M
        for u in range(M):
            # is u/M in [a, a+1/2) mod 1 ?
            t = (F(u, M) - a) % 1
            if t < F(1, 2):
                inA[u] = True
        tot += mono(x, adj, inA)
    return tot / cells


def thirdarc_average(M, x):
    adj = adj_matrix(M)
    tot = F(0)
    cells = 6 * M
    for j in range(cells):
        a = F(2 * j + 1, 2 * cells)
        inA = [False] * M
        for u in range(M):
            t = (F(u, M) - a) % 1
            if t < F(1, 3):
                inA[u] = True
        tot += mono(x, adj, inA)
    return tot / cells


CASES = [
    ("C5 uniform", 5, [1] * 5),
    ("Gamma_7 uniform", 7, [1] * 7),
    ("Gamma_8 uniform", 8, [1] * 8),
    ("W1", 8, [0, 1, 0, 1, 2, 0, 2, 1]),
    ("Gamma_18 uniform", 18, [1] * 18),
    ("Gamma_20 uniform", 20, [1] * 20),
    ("W8", 20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
    ("W9", 20, [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]),
    ("W10", 20, [0, 5, 5, 0, 0, 0, 0, 6, 4, 5, 0, 0, 0, 0, 5, 4, 6, 0, 0, 0]),
    ("random Gamma_13", 13, [0, 2, 5, 1, 0, 3, 0, 4, 1, 2, 0, 6, 1]),
]

if __name__ == "__main__":
    print("(f) A == exact half-arc average?   and how the 1/3-arc average compares to int m dmu")
    for name, M, w in CASES:
        x = normalise(w)
        adj = adj_matrix(M)
        A = A_of(x, adj, M)
        H = halfarc_average(M, x)
        T3 = thirdarc_average(M, x)
        b0 = W_of(x, adj) - sum(x[b] * g_of(x, adj)[b] ** 2 for b in range(M))
        print(f"  {name:18s} A={str(A):>10s}  half-arc avg={str(H):>10s}  equal={A == H}"
              f"   1/3-arc avg={str(T3):>10s}  bound_0={str(b0):>10s}")

    print("\n(d) pairing hazard: index-arc vs N(b) on Gamma_11, support {0,2,4,7,9}, w=(1,2,3,2,1)/9")
    M = 11
    w = [0] * 11
    for i, v in zip([0, 2, 4, 7, 9], [1, 2, 3, 2, 1]):
        w[i] = v
    x = normalise(w)
    adj = adj_matrix(M)
    supp = [i for i in range(M) if w[i]]
    for bi, b in enumerate(supp):
        mb = m_of(b, x, adj, M)
        inA = [False] * M              # 'the arc that starts at the b-th atom', 1/3 of the circle
        for t in range(M // 3 + 1):
            inA[(b + t) % M] = True
        print(f"    b={b}: m(b)={str(mb):>8s}   index-arc value={str(mono(x,adj,inA)):>8s}"
              f"   differ={mb != mono(x,adj,inA)}")

    print("\n(b) delta(Gamma_m) > m/3 ?")
    for M in range(5, 27):
        dmin = M // 3 + 1
        deg = M - 2 * dmin + 1
        print(f"    Gamma_{M:2d}: degree {deg:2d}, m/3 = {M/3:6.3f}, delta>m/3 = "
              f"{str(deg > F(M,3)):>5s}, m mod 3 = {M % 3}")

    print("\n(e) 3-fold measures:  g(x) = 1/3 - mu({x}) ?")
    for M, base in [(9, [1, 0, 0] * 3), (12, [1, 1, 0, 0] * 3), (18, [1] * 18), (15, [2, 1, 0, 3, 4] * 3)]:
        x = normalise(base)
        adj = adj_matrix(M)
        g = g_of(x, adj)
        ok = all(g[u] == F(1, 3) - x[u] for u in range(M) if x[u] or True)
        print(f"    M={M:3d} w={base}  3-fold={base[:M//3]*3 == base}  "
              f"g == 1/3 - mu({{x}}) for all x: {ok}   W={W_of(x,adj)}")

    print("\nP4 recommendation 1 ('certificates must use arcs strictly between 1/3 and 1/2'):")
    for name, M, w in [("W8", 20, CASES[6][2]), ("W9", 20, CASES[7][2]), ("W10", 20, CASES[8][2])]:
        x = normalise(w)
        adj = adj_matrix(M)
        h = min(mono(x, adj, [(( (i - s) % M) < M // 2) for i in range(M)]) for s in range(M))
        print(f"    {name}: min over arcs of length EXACTLY 1/2 = {h} = {float(h):.6f} "
              f"<= 1/25 ? {h <= ONE25}  -> the exact-1/2 family already closes it")
