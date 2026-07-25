"""Q4: the DEGREE-INDEPENDENT first-order test at a maximiser.

Let nu_S be ANY family of functions that are nonnegative on the orthant, differentiable, with
    sum_S nu_S = c L^{2d}   and   T := L^{2d+2} - sum_S nu_S q_S >= 0 on the orthant   (c = 25).
Let x in Z be a maximiser: L(x) = 1, psi(x) = 1/25.  Then (proof in Q4.md):
  * q_S(x) >= 1/25 for every S and T(x) <= 0, so T(x) = 0 and nu_S(x) = 0 for every non-tight S;
  * nu_S >= 0 on the orthant, vanishing at x, forces d_j nu_S(x) = 0 for j in supp(x)
    (interior direction of the face) and d_j nu_S(x) >= 0 for j outside supp(x);
  * differentiating T at x and using sum_S d_j nu_S(x) = 25*2d*L^{2d-1} = 50d gives, with
    mu_S := nu_S(x)/25 (a probability distribution supported on the TIGHT cuts),

        sum_S mu_S d_j q_S(x)  =  2/25   for j in supp(x),
        sum_S mu_S d_j q_S(x) <=  2/25   for j outside supp(x).

    The multiplier degree 2d has CANCELLED.  So this LP is a necessary condition for a certificate
    of ANY degree (and for any orthant-nonnegative, not necessarily polynomial, multipliers).
"""
import sys
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
from Q4_graphs import graph_by_key as gamma_graph, all_cuts, nondominated_cuts
from Q4_zeroset import zero_points, psi_exact


def sides(mask, n):
    return [0 if v == 0 else (mask >> (v - 1)) & 1 for v in range(n)]


def firstorder_lp(n, E, cuts, x, verbose=False):
    """Returns (feasible, info).  Exact data, LP solved in floating point then re-checked."""
    L = sum(x)
    tgt = L * L / 25
    tight = []
    for S, (mask, mono) in enumerate(cuts):
        if sum(x[E[k][0]] * x[E[k][1]] for k in mono) == tgt:
            tight.append(S)
    supp = [j for j in range(n) if x[j] != 0]
    # d_j q_S(x) = sum over neighbours u of j on the same side as j (monochromatic edge ju) of x_u
    rows = []
    for j in range(n):
        row = []
        for S in tight:
            mask, mono = cuts[S]
            s = F(0)
            for k in mono:
                u, v = E[k]
                if u == j:
                    s += x[v]
                elif v == j:
                    s += x[u]
            row.append(s)
        rows.append(row)
    nt = len(tight)
    A_eq = [[1.0] * nt] + [[float(v) for v in rows[j]] for j in supp]
    b_eq = [1.0] + [float(F(2, 25) * L)] * len(supp)
    A_ub = [[float(v) for v in rows[j]] for j in range(n) if x[j] == 0]
    b_ub = [float(F(2, 25) * L)] * len(A_ub)
    res = linprog(c=[0.0] * nt, A_eq=A_eq, b_eq=b_eq,
                  A_ub=A_ub or None, b_ub=b_ub or None, bounds=[(0, None)] * nt,
                  method='highs')
    return res.success, dict(tight=tight, rows=rows, supp=supp, res=res, x=x)


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else 8
    n, E = gamma_graph(m)
    cuts = nondominated_cuts(all_cuts(n, E))
    Z = zero_points(n, E, cuts)
    print(f"Gamma_{m}: |Z sample| = {len(Z)}")
    bad = []
    for x in Z:
        ok, info = firstorder_lp(n, E, cuts, x)
        if not ok:
            bad.append((x, info))
    print(f"first-order LP INFEASIBLE at {len(bad)} of {len(Z)} maximisers")
    for x, info in bad[:6]:
        print(f"   x = {[str(v) for v in x]}  supp={info['supp']}  #tight cuts={len(info['tight'])}")
    if not bad:
        print("   (all maximisers pass the first-order test -- no degree-independent obstruction here)")
