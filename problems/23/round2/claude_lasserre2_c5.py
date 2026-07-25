"""THE DECIDING CALIBRATION: does Lasserre level 2 see max_x psi(C5,x) = 1/25 ?

R2-C1 established that the level-1 lift returns (5 - sqrt 5)/50 = 0.0553 on C5, whose true value is
exactly 1/25 = 0.04 -- a 38% gap on the extremal object, so level 1 can certify nothing. The record
there states the decision rule: go to Lasserre level 2 and CALIBRATE ON C5 FIRST; if level 2 does
not return (essentially) 1/25 on C5, the whole SDP-certificate route is dead and no further pattern
needs to be tried.

Problem in polynomial-optimisation form:

        maximise t
        s.t.     q_S(x) - t >= 0   for every cut S of C5,
                 x_i >= 0,  sum_i x_i = 1,

with q_S(x) = sum over monochromatic uv under S of x_u x_v. The optimum is max_x psi(C5,x) = 1/25.

Level-2 moment relaxation:
  * moment vector y indexed by multi-indices alpha with |alpha| <= 4, y_0 = 1;
  * moment matrix M_2(y), rows/cols indexed by |beta| <= 2, entry y_{beta+beta'};   M_2 psd
  * localizing matrices for the degree-1 constraints x_i:  M_1(x_i y) psd,
    rows/cols |beta| <= 1, entry y_{beta+beta'+e_i};
  * localizing matrices for the degree-2 constraints q_S - t:
    M_1((q_S - t) y) = M_1(q_S y) - t M_1(y)  psd;
  * the equality sum x = 1 imposed on every moment: sum_i y_{alpha+e_i} = y_alpha for |alpha| <= 3.

The value is an upper bound on the true optimum. Everything is small for n = 5:
M_2 is 21x21, each localizing matrix is 6x6, and there are 16 cuts.
"""

import numpy as np
import cvxpy as cp
from itertools import combinations_with_replacement

n = 5
EDGES = [(i, (i + 1) % n) for i in range(n)]


def monomials(deg):
    """all multi-indices in N^n with |alpha| <= deg, as tuples"""
    out = []
    def rec(pos, rem, cur):
        if pos == n:
            out.append(tuple(cur))
            return
        for k in range(rem + 1):
            rec(pos + 1, rem - k, cur + [k])
    rec(0, deg, [])
    return sorted(set(out), key=lambda a: (sum(a), a))


ALL4 = monomials(4)
IDX = {a: i for i, a in enumerate(ALL4)}
B2 = [a for a in monomials(2)]          # |beta| <= 2, 21 of them
B1 = [a for a in monomials(1)]          # |beta| <= 1, 6 of them


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


CUTS = []
for mask in range(1 << (n - 1)):
    S = (mask << 1) | 1
    CUTS.append([(u, v) for (u, v) in EDGES if ((S >> u) & 1) == ((S >> v) & 1)])

print(f"C5: {len(CUTS)} cuts, moment vector length {len(ALL4)}, M_2 is {len(B2)}x{len(B2)}, "
      f"localizing {len(B1)}x{len(B1)}")


def feasible(tval):
    """t enters bilinearly, so bisect: for a FIXED numeric t every constraint is linear in y."""
    y = cp.Variable(len(ALL4))
    cons = [y[IDX[tuple([0] * n)]] == 1, y >= 0]  # x >= 0 => every moment is nonnegative
    cons.append(cp.bmat([[y[IDX[add(b, c)]] for c in B2] for b in B2]) >> 0)
    for i in range(n):
        e = tuple(1 if k == i else 0 for k in range(n))
        cons.append(cp.bmat([[y[IDX[add(add(b, c), e)]] for c in B1] for b in B1]) >> 0)
    for a in monomials(3):
        cons.append(cp.sum(cp.hstack(
            [y[IDX[add(a, tuple(1 if k == i else 0 for k in range(n)))]] for i in range(n)]
        )) == y[IDX[a]])
    M1y = cp.bmat([[y[IDX[add(b, c)]] for c in B1] for b in B1])
    for mono in CUTS:
        rows = []
        for b in B1:
            row = []
            for c in B1:
                expr = 0
                for (u, v) in mono:
                    g = tuple((1 if k == u else 0) + (1 if k == v else 0) for k in range(n))
                    expr = expr + y[IDX[add(add(b, c), g)]]
                row.append(expr)
            rows.append(row)
        cons.append(cp.bmat(rows) - tval * M1y >> 0)
    prob = cp.Problem(cp.Minimize(0), cons)
    try:
        prob.solve(solver=cp.SCS, eps=1e-8, max_iters=100000, verbose=False)
    except Exception:
        return False
    return prob.status in ("optimal", "optimal_inaccurate")


lo, hi = 0.0, 0.12
if not feasible(lo):
    print("   WARNING: infeasible even at t = 0; formulation problem")
for _ in range(24):
    mid = (lo + hi) / 2
    if feasible(mid):
        lo = mid
    else:
        hi = mid
v = lo
print(f"   status                : bisection on t, 24 steps, bracket [{lo:.8f}, {hi:.8f}]")
print(f"   Lasserre level-2 bound: {v:.8f}")
print(f"   true max_x psi(C5,x)  : {1/25:.8f}")
print(f"   level-1 bound (R2-C1) : {(5 - 5 ** 0.5) / 50:.8f}")
print(f"   ratio to 1/25         : {v / 0.04:.4f}x")
print()
if v <= 0.04 + 1e-4:
    print("   VERDICT: level 2 SEES the truth on C5 -- the SDP-certificate route is ALIVE and the")
    print("            next step is to run it on Wagner (n=8) and rationalise the dual.")
else:
    print("   VERDICT: level 2 does NOT see the truth on C5 -- by the decision rule recorded in")
    print("            R2C1_SDP_LEVEL1_BLOCKED.md the SDP-certificate route is DEAD, and no other")
    print("            pattern needs to be tried.")

