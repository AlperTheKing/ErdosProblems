"""Stronger lifted SDP for the psi ceiling: add the row-sum (moment) constraints.

The first attempt (claude_psi_sdp.py) used only Y >= 0, Y psd, sum(Y) = 1 and was far too weak --
0.0553 on C5, whose true value is exactly 1/25 = 0.04. That relaxation forgets that Y is supposed
to be x x^T for an x in the simplex. The standard lifted formulation keeps x explicitly:

        maximise  t
        s.t.      (1/2) <A_S, Y>  >=  t          for every cut S
                  [[1, x^T], [x, Y]]  psd         (equivalently Y - x x^T psd)
                  Y >= 0 entrywise,  x >= 0,  sum(x) = 1
                  sum_v Y[u,v] = x[u]  for every u        <-- the row-sum / moment constraints
                  Y[u,u] <= x[u]                          <-- since x_u^2 <= x_u on the simplex

Every x in the simplex gives a feasible point with Y = x x^T, so the optimum is still a valid UPPER
bound on max_x psi(H,x). The row-sum equalities are exactly what the first attempt was missing:
sum_v x_u x_v = x_u (sum x = 1).

Calibration: on C5 the truth is exactly 1/25. A value of 0.04 would mean this relaxation is tight on
the extremal object and the route is alive; anything above means it is not.
"""

import numpy as np
import cvxpy as cp


def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def circulant(n, conn):
    E = set()
    for v in range(n):
        for d in conn:
            w = (v + d) % n
            E.add((min(v, w), max(v, w)))
    return n, sorted(E)


def petersen():
    o = [(i, (i + 1) % 5) for i in range(5)]
    s = [(i, 5 + i) for i in range(5)]
    inn = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, sorted({(min(a, b), max(a, b)) for a, b in o + s + inn})


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((10, 5 + i))
    return 11, sorted({(min(a, b), max(a, b)) for a, b in E})


PATTERNS = [
    ("C5  (truth 1/25)", cycle(5)),
    ("C7  (truth 1/49)", cycle(7)),
    ("Wagner C8(1,4)", circulant(8, [1, 4])),
    ("Petersen", petersen()),
    ("Grotzsch", grotzsch()),
    ("C11(1,3)", circulant(11, [1, 3])),
    ("C13(1,5)", circulant(13, [1, 5])),
]

print("=" * 96)
print("lifted SDP with row-sum constraints: upper bound on max_x psi(H,x)   target 1/25 = 0.040000")
print("=" * 96)
print(f"{'pattern':20s} {'n':>3} {'cuts':>6} {'SDP upper bound':>17} {'ratio to 1/25':>14} {'verdict':>11}")
for name, (n, E) in PATTERNS:
    Y = cp.Variable((n, n), symmetric=True)
    x = cp.Variable(n)
    t = cp.Variable()
    M = cp.bmat([[cp.reshape(cp.Constant(1.0), (1, 1), order='C'), cp.reshape(x, (1, n), order='C')],
                 [cp.reshape(x, (n, 1), order='C'), Y]])
    cons = [M >> 0, Y >= 0, x >= 0, cp.sum(x) == 1,
            cp.sum(Y, axis=1) == x, cp.diag(Y) <= x]
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        A = np.zeros((n, n))
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                A[u, v] = A[v, u] = 1.0
        cons.append(0.5 * cp.sum(cp.multiply(A, Y)) >= t)
    prob = cp.Problem(cp.Maximize(t), cons)
    try:
        prob.solve(solver=cp.CLARABEL)
        val = float(t.value)
        st = prob.status
    except Exception as ex:
        val, st = float("nan"), "error"
    verdict = "CERTIFIES" if val <= 0.04 + 1e-7 else "too weak"
    print(f"{name:20s} {n:>3} {1 << (n-1):>6} {val:>17.6f} {val/0.04:>13.3f}x {verdict:>11}  [{st}]")

print()
print("""C5 is the calibration point: its true value is exactly 1/25, so the bound there measures how
much slack the relaxation has on the extremal object. If the bound on C5 exceeds 1/25, this level of
lifting cannot certify the ceiling anywhere, and the route needs a higher Lasserre level.""")
