#!/usr/bin/env python3
"""
q2_farkas.py -- EXACT decision: does a NONNEGATIVE edge-coefficient vector mu
reproduce a_1 on the sampled span?

Model: a_1(P) = <mu, Lambda(P)>  (Berline-Vergne local formula).  mu_true is a
solution of the sampled linear system.  Therefore:

  * if the system HAS a nonnegative solution, a_1 >= 0 for every lattice
    3-polytope whose Lambda lies in the sampled span  (=> no r=4 counterexample
    reachable there);
  * if it has NO nonnegative solution, then mu_true itself has a strictly
    negative coordinate: some edge type of the fixed r=4 rhombus normal set
    drives a_1 DOWN, and the Reeve mechanism is alive in the r=4 normal set.

Decided by an EXACT rational phase-1 simplex (Bland's rule, Fractions only).
"""
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def phase1(M, a):
    """Exact: is {x >= 0 : M x = a} nonempty?  Returns (feasible, x or None)."""
    m, n = len(M), len(M[0])
    T = [row[:] for row in M]
    rhs = a[:]
    for i in range(m):
        if rhs[i] < 0:
            T[i] = [-x for x in T[i]]
            rhs[i] = -rhs[i]
    # tableau with artificials
    for i in range(m):
        T[i] = T[i] + [Fraction(1) if j == i else Fraction(0) for j in range(m)]
    basis = [n + i for i in range(m)]
    cost = [Fraction(0)] * n + [Fraction(1)] * m
    # reduced costs z_j - c_j  with basis = artificials
    def price():
        y = [cost[basis[i]] for i in range(m)]
        red = []
        for j in range(n + m):
            s = sum(y[i] * T[i][j] for i in range(m))
            red.append(s - cost[j])
        obj = sum(y[i] * rhs[i] for i in range(m))
        return red, obj

    it = 0
    while True:
        it += 1
        red, obj = price()
        enter = next((j for j in range(n + m) if red[j] > 0), None)
        if enter is None:
            return (obj == 0), basis, T, rhs, n, m
        ratios = [(rhs[i] / T[i][enter], i) for i in range(m) if T[i][enter] > 0]
        if not ratios:
            return None, basis, T, rhs, n, m
        best = min(ratios, key=lambda t: (t[0], basis[t[1]]))
        leave = best[1]
        pv = T[leave][enter]
        T[leave] = [x / pv for x in T[leave]]
        rhs[leave] = rhs[leave] / pv
        for i in range(m):
            if i != leave and T[i][enter] != 0:
                f = T[i][enter]
                T[i] = [x - f * y for x, y in zip(T[i], T[leave])]
                rhs[i] = rhs[i] - f * rhs[leave]
        basis[leave] = enter
        if it > 20000:
            raise RuntimeError("simplex did not terminate")


def main(path=None):
    data = json.load(open(path or os.path.join(HERE, "q2_fitdata.json")))
    rowsM = [[Fraction(x) for x in r] for r in data["M"]]      # rank-many rows
    a = [Fraction(x) for x in data["a"]]
    print(f"exact LP: {len(rowsM)} equations, {len(rowsM[0])} nonneg unknowns")
    feas, basis, T, rhs, n, m = phase1(rowsM, a)
    print("nonnegative mu exists:", feas)
    x = [Fraction(0)] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = rhs[i]
    if feas:
        bad = 0
        for r, av in zip(rowsM, a):
            if sum(ri * xi for ri, xi in zip(r, x)) != av:
                bad += 1
        print("exact re-verification mismatches:", bad,
              " min entry:", min(x))
        json.dump({"feasible": True, "mu": [str(v) for v in x]},
                  open(os.path.join(HERE, "q2_farkas.json"), "w"), indent=1)
    else:
        json.dump({"feasible": False}, open(os.path.join(HERE, "q2_farkas.json"), "w"),
                  indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
