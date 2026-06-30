"""LP search for a coefficientwise certificate of the seven-cut PMS lemma.

We shift w_i = 1+x_i.  The target numerator P(x) should be nonnegative on
x>=0 and seven shifted flip constraints g_j(x)>=0.  This script searches for

    P = R + sum_j h_j g_j

where R and the multiplier polynomials h_j have nonnegative coefficients.
"""

from collections import defaultdict
from math import comb

import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def poly_dict(expr, vars_):
    poly = sp.Poly(sp.expand(expr), *vars_)
    return {tuple(m): int(c) for m, c in poly.terms()}


def add_monom(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub_monom(a, b):
    return tuple(x - y for x, y in zip(a, b))


def divides(a, b):
    return all(x <= y for x, y in zip(a, b))


def total_deg(m):
    return sum(m)


def build_target_and_constraints():
    w = sp.symbols("w0:10")
    x = sp.symbols("x0:10")
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w

    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    i27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    i19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z79 = (
        w0 * w5 * w6
        + w3 * w4 * w8
        + w3 * w6 * w8
        + w4 * w5 * w8
        + w5 * w6 * w8
    )
    i79 = (
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
    n = sum(w)
    m = w1 * w9 + w2 * w7 + w7 * w9
    endpoint = w1 + w2 + w7 + w9
    den = z27 * z19 * z79
    numer = (2 * (n * n - 25 * m) - 75 * (endpoint - n)) * den
    numer -= 75 * w2 * w7 * i27 * z19 * z79
    numer -= 75 * w1 * w9 * i19 * z27 * z79
    numer -= 75 * w7 * w9 * i79 * z27 * z19
    shift = {w[i]: x[i] + 1 for i in range(10)}

    g = [
        w5 - w9,
        w6 - w7,
        w3 + w5 - w2 - w9,
        w4 + w6 - w1 - w7,
        w0 * w6 + w3 * w8 + w5 * w8 - m,
        w0 * w5 + w3 * w8 + w5 * w8 - m,
        w0 * w6 + w4 * w8 + w6 * w8 - m,
    ]
    return poly_dict(numer.subs(shift), x), [poly_dict(expr.subs(shift), x) for expr in g]


def main():
    p, gs = build_target_and_constraints()
    neg_p = [m for m, c in p.items() if c < 0]
    print("target terms", len(p), "negative", len(neg_p), "degree", max(map(total_deg, p)))

    # Candidate multipliers: any quotient of a negative target monomial by a
    # negative monomial of a constraint.  This is the smallest natural support.
    candidates = []
    seen = set()
    for gi, gd in enumerate(gs):
        neg_g = [m for m, c in gd.items() if c < 0]
        for pm in neg_p:
            for gm in neg_g:
                if divides(gm, pm):
                    q = sub_monom(pm, gm)
                    key = (gi, q)
                    if key not in seen:
                        seen.add(key)
                        candidates.append(key)
    print("candidates", len(candidates))

    # All monomials touched by the target or candidates.
    monoms = set(p)
    for gi, q in candidates:
        for gm in gs[gi]:
            monoms.add(add_monom(q, gm))
    monoms = sorted(monoms)
    mid = {m: i for i, m in enumerate(monoms)}

    # Feasibility P - A*lambda >= 0, lambda >= 0.
    # linprog uses A_ub x <= b_ub, so A*lambda <= P.
    rows = []
    cols = []
    data = []
    for j, (gi, q) in enumerate(candidates):
        for gm, coeff in gs[gi].items():
            rows.append(mid[add_monom(q, gm)])
            cols.append(j)
            data.append(coeff)
    A = coo_matrix((data, (rows, cols)), shape=(len(monoms), len(candidates))).tocsr()
    b = np.array([p.get(m, 0) for m in monoms], dtype=float)

    res = linprog(
        c=np.zeros(len(candidates)),
        A_ub=A,
        b_ub=b,
        bounds=(0, None),
        method="highs",
        options={"presolve": True},
    )
    print("status", res.status, res.message)
    if res.success:
        nz = [(candidates[i], res.x[i]) for i in range(len(candidates)) if res.x[i] > 1e-8]
        print("nonzero", len(nz))
        for item in nz[:80]:
            print(item)


if __name__ == "__main__":
    main()
