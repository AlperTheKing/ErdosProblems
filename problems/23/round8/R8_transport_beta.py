"""Exact quantitative failure constant for the multiplicative transport certificate.

Game: the *adversary* picks a distribution mu over the induced C5s of H;
the *certifier* picks a distribution lambda over cuts.  Payoff A[C][S] = 1 iff
k_S(C) >= 3 (i.e. cut S is NOT optimal on the 5-cycle C).  Put

    beta(H) = max_mu min_S  mu({C : k_S(C) >= 3})        (value of that 0/1 game).

Then for EVERY lambda,   max_x prod_S nu_S(x)^{lambda_S} >= (1/25) * 3^{beta(H)}.

  proof:  max_C (1/25) prod_S k_S(C)^{lambda_S}
       >= (1/25) exp( sum_C mu_C sum_S lambda_S log k_S(C) )        (max >= mean)
        = (1/25) exp( sum_S lambda_S  sum_C mu_C log k_S(C) )
       >= (1/25) exp( sum_S lambda_S * beta * log 3 )  =  (1/25) 3^beta .

mu is found with a float LP and then *verified exactly* over all cuts with Fractions,
so the reported beta is a rigorous lower bound on the true game value.
"""
import sys
from fractions import Fraction
from itertools import combinations
import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, ".")
from R8_transport_lib import *   # noqa


def induced_c5s(G):
    out = []
    for verts in combinations(range(G.n), 5):
        mask = 0
        for v in verts:
            mask |= 1 << v
        e = G.induced_edges(mask)
        if len(e) != 5:
            continue
        deg = {v: 0 for v in verts}
        for u, v in e:
            deg[u] += 1
            deg[v] += 1
        if all(d == 2 for d in deg.values()):
            out.append((verts, e))
    return out


def beta(G, denom=2520):
    cyc = induced_c5s(G)
    cuts = list(G.all_cuts())
    A = np.zeros((len(cyc), len(cuts)), dtype=np.int8)
    for j, (vs, es) in enumerate(cyc):
        for i, S in enumerate(cuts):
            k = sum(1 for u, v in es if ((S >> u) & 1) == ((S >> v) & 1))
            A[j, i] = 1 if k >= 3 else 0
    nc = len(cyc)
    # max t  s.t.  sum_j mu_j A[j,i] >= t for all i ; sum mu = 1 ; mu >= 0
    c = np.zeros(nc + 1)
    c[-1] = -1.0
    Aub = np.hstack([-A.T, np.ones((len(cuts), 1))])
    bub = np.zeros(len(cuts))
    Aeq = np.zeros((1, nc + 1))
    Aeq[0, :nc] = 1.0
    beq = [1.0]
    res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                  bounds=[(0, None)] * nc + [(None, None)], method="highs")
    mu = res.x[:nc]
    val = res.x[-1]
    # ---- exact rationalisation + verification ----
    num = [int(round(m * denom)) for m in mu]
    s = sum(num)
    if s == 0:
        return None
    muQ = [Fraction(t, s) for t in num]
    worst = None
    for i, S in enumerate(cuts):
        tot = Fraction(0)
        for j in range(nc):
            if A[j, i]:
                tot += muQ[j]
        if worst is None or tot < worst:
            worst = tot
    print("%-14s n=%2d  #indC5=%3d  LP beta=%.6f   exact verified beta >= %s = %.6f"
          % (G.name, G.n, nc, val, worst, float(worst)), flush=True)
    b = float(worst)
    print("      ==> for EVERY distribution lambda over cuts:  max_x prod nu_S^lambda "
          ">= 3^(%s)/25 = %.6f   (target 1/25 = 0.04, excess %.2f%%)"
          % (worst, 3 ** b / 25, 100 * (3 ** b / 25 / 0.04 - 1)), flush=True)
    return worst


if __name__ == "__main__":
    for G in [andrasfai(4), from_g6("M?AE@bH{AYN_LgBs?", "N14extremal"), andrasfai(5)]:
        beta(G)
