"""How small can a falsifier of item 7 be?  Greedy support reduction of W9 (and W8):
for every subset of the support, re-optimise the integer weights and test
    min( A , min_b m(b) ) > 1/25 .
Reports the smallest support that still defeats both certificates, exactly verified.
"""
import itertools
import numpy as np
from fractions import Fraction as F
from P4_search import circle_matrices
from P4_core import from_gamma, sort_cyclic, adjacency, A_of, m_values, arcbound, psi, g_of, TARGET

rng = np.random.default_rng(99)
M = 20
W9 = [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]
W8 = [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]


def j1_float(w, adj, Q):
    if w.sum() <= 0:
        return -1
    x = w / w.sum()
    gv = adj @ x
    Wv = 0.5 * float(x @ gv)
    A = 0.5 * float(x @ (Q @ x))
    mvec = Wv - adj @ (x * gv)
    supp = w > 0
    return min(A, float(mvec[supp].min()))


def climb_on_support(supp, q, adj, Q, tries=6):
    best = (-1, None)
    k = len(supp)
    for _ in range(tries):
        w = np.zeros(M)
        cut = sorted(rng.choice(range(1, q), size=k - 1, replace=False)) if k > 1 else []
        parts = np.diff([0] + list(cut) + [q])
        for i, p in zip(supp, parts):
            w[i] = float(p)
        if (w[list(supp)] <= 0).any():
            continue
        cur = j1_float(w, adj, Q)
        improved = True
        while improved:
            improved = False
            for i in supp:
                for j in supp:
                    if i == j or w[i] <= 1:
                        continue
                    w[i] -= 1
                    w[j] += 1
                    v = j1_float(w, adj, Q)
                    if v > cur + 1e-14:
                        cur, improved = v, True
                    else:
                        w[i] += 1
                        w[j] -= 1
        if cur > best[0]:
            best = (cur, w.copy())
    return best


def exact_check(w):
    pos, wt = sort_cyclic(*from_gamma(M, [int(t) for t in w]))
    adj = adjacency(pos)
    A = A_of(pos, wt, adj)
    mm = min(m_values(pos, wt, adj))
    return A, mm, min(A, mm), arcbound(pos, wt, adj), min(g_of(pos, wt, adj)), psi(pos, wt, adj)


if __name__ == '__main__':
    adj, D, Q = circle_matrices(M)
    for name, base in (("W9", W9), ("W8", W8)):
        full = [i for i in range(M) if base[i] > 0]
        print(f"\n{name}: support {full} ({len(full)} atoms)")
        for size in range(4, len(full) + 1):
            hits = []
            for supp in itertools.combinations(full, size):
                for q in (20, 40, 60):
                    v, w = climb_on_support(list(supp), q, adj, Q)
                    if v > 1.0 / 25 + 1e-12:
                        A, mm, j1, ab, ming, ps = exact_check(w)
                        if j1 > TARGET:
                            hits.append((j1, tuple(int(t) for t in w), A, mm, ab, ming, ps))
                        break
            if hits:
                hits.sort(reverse=True)
                j1, w, A, mm, ab, ming, ps = hits[0]
                print(f"  size {size}: {len(hits)} supports work.  best  weights {list(w)}")
                print(f"           A={A}={float(A):.6f}  min m={mm}={float(mm):.6f}  "
                      f"min g={ming}={float(ming):.4f}{' (>1/3)' if ming > F(1,3) else ''}  "
                      f"ARCBOUND={ab}={float(ab):.6f}  psi={ps}")
                break
            else:
                print(f"  size {size}: none")
