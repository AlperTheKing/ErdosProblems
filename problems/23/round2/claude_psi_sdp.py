"""Does an SDP relaxation certify the 1/25 ceiling for max_x psi(H,x)?

Recorded bottleneck (round1/CLAUDE_GATE_RESULTS.md sections 3g, 3h): the conjecture is equivalent to
max_x psi(H,x) <= 1/25 for every triangle-free H, where
psi(H,x) = min over cuts S of sum_{uv monochromatic} x_u x_v on the simplex; hill-climbing gives only
lower bounds; the two natural FIXED-multiplier certificates were proved too weak (1/8 and 1/20, the
latter failing on C5 itself); and exact interval branch-and-bound does not scale (stalls on Wagner at
n=8 and Petersen at n=10). The recorded conclusion was that a valid certificate needs an
x-DEPENDENT multiplier, i.e. an SDP dual. This script tests exactly that.

Relaxation. Write q_S(x) = sum_{uv mono under S} x_u x_v = (1/2) <A_S, x x^T> with A_S the symmetric
0/1 adjacency matrix of the monochromatic edges under S. Lift Y = x x^T and relax:

        maximise  t
        s.t.      (1/2) <A_S, Y>  >=  t     for every cut S,
                  Y >= 0 entrywise,  Y positive semidefinite,  sum(Y) = 1.

Any x in the simplex gives a feasible Y = x x^T with the same objective, so the optimum is an UPPER
bound on max_x psi(H,x). This is the doubly-nonnegative relaxation; it is strictly stronger than any
fixed averaging weight because the multiplier on each cut is chosen after seeing Y.

If the value comes out at or below 1/25 for a pattern, the ceiling is certified for it (modulo
rationalising the dual, which is the follow-up step); if it comes out above, the relaxation is too
weak and that is itself the answer.
"""

import numpy as np
import cvxpy as cp
from itertools import combinations


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
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, 5 + i) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, [(min(a, b), max(a, b)) for a, b in outer + spokes + inner]


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((10, 5 + i))
    return 11, sorted({(min(a, b), max(a, b)) for a, b in E})


def complete_bipartite(a, b):
    return a + b, [(i, a + j) for i in range(a) for j in range(b)]


PATTERNS = [
    ("C5", cycle(5)),
    ("C7", cycle(7)),
    ("K_{3,3}", complete_bipartite(3, 3)),
    ("Wagner C8(1,4)", circulant(8, [1, 4])),
    ("Petersen", petersen()),
    ("Grotzsch", grotzsch()),
    ("C11(1,3)", circulant(11, [1, 3])),
    ("C13(1,5)", circulant(13, [1, 5])),
]

print("=" * 92)
print("doubly-nonnegative SDP upper bound on max_x psi(H,x)      target 1/25 = 0.040000")
print("=" * 92)
print(f"{'pattern':22s} {'n':>3} {'cuts':>6} {'SDP upper bound':>17} {'vs 1/25':>10} {'status':>12}")
for name, (n, E) in PATTERNS:
    cuts = []
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        A = np.zeros((n, n))
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                A[u, v] = 1.0
                A[v, u] = 1.0
        cuts.append(A)

    Y = cp.Variable((n, n), symmetric=True)
    t = cp.Variable()
    cons = [Y >> 0, Y >= 0, cp.sum(Y) == 1]
    for A in cuts:
        cons.append(0.5 * cp.sum(cp.multiply(A, Y)) >= t)
    prob = cp.Problem(cp.Maximize(t), cons)
    try:
        prob.solve(solver=cp.CLARABEL)
        val = float(t.value)
        stat = prob.status
    except Exception as e:
        val, stat = float("nan"), f"error"
    rel = "CERTIFIES" if val <= 0.04 + 1e-7 else "too weak"
    print(f"{name:22s} {n:>3} {len(cuts):>6} {val:>17.6f} {val/0.04:>9.3f}x {rel:>12}  [{stat}]")

print()
print("""Reading. The bound is valid for every pattern (Y = x x^T is feasible), so a value at or below
1/25 certifies the ceiling for that pattern, and a value above it means the doubly-nonnegative
relaxation is not tight enough there. C5 is the calibration point: its true value is exactly 1/25,
so any bound below 0.04 would indicate a bug, and a bound of exactly 0.04 would mean the relaxation
is tight on the extremal object.""")
