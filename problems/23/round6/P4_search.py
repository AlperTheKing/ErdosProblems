"""P4 adversarial search over measures on the circle.

Three targets, all of them attacks on the CAMPAIGN (not on Erdos 23):

  J1 = min( A , min_{b in supp} m(b) )      > 1/25  ==>  item 7's OPEN step is FALSE,
                                                        because bound_k >= min_b m(b) for EVERY k.
  J2 = ARCBOUND                             > 1/25  ==>  items 3-7 are all dead (the arc-cut
                                                        ceiling would exceed the target).
  J3 = min( A , min_b m(b) , bound_0 )      - the two-term form of R5-K18.

Search = exact integer-weight hill climbing on the grid Z_M (positions i/M), evaluated in float
for speed and re-verified in exact rationals for every reported record.
"""
import sys
import numpy as np
from fractions import Fraction as F

np.seterr(all='raise')


def circle_matrices(M):
    i = np.arange(M)
    dif = np.abs(i[:, None] - i[None, :])
    dif = np.minimum(dif, M - dif)          # integer circular distance
    adj = (3 * dif > M).astype(float)
    np.fill_diagonal(adj, 0.0)
    D = dif / M
    Q = adj * (1.0 - 2.0 * D)               # A = 1/2 x^T Q x
    return adj, D, Q


def evaluate(x, adj, Q, tol=0.0):
    gv = adj @ x
    W = 0.5 * float(x @ gv)
    A = 0.5 * float(x @ (Q @ x))
    mvec = W - adj @ (x * gv)
    supp = x > tol
    minm = float(mvec[supp].min()) if supp.any() else 0.0
    return W, A, minm, mvec, gv


def arcbound_float(x, adj):
    """min over all cyclic intervals of the grid (equivalently of the support)"""
    M = len(x)
    B = adj * np.outer(x, x)
    rowsum = B.sum(1)
    best = np.inf
    Wtot = 0.5 * B.sum()
    # arcs [i, i+L)
    for i in range(M):
        u = np.zeros(M)
        acc_r = 0.0
        for L in range(1, M + 1):
            j = (i + L - 1) % M
            acc_r += rowsum[j]
            u[j] = 1.0
            quad = float(u @ (B @ u))
            # acc_r = sum_{j in S} x_j g_j = 2*in(S) + cross(S);  quad = 2*in(S)
            cross = acc_r - quad                       # unordered crossing mass
            mono = Wtot - cross
            if mono < best:
                best = mono
    return min(best, Wtot)


def objective(w, adj, Q, which):
    q = w.sum()
    x = w / q
    W, A, minm, mvec, gv = evaluate(x, adj, Q, tol=0.0)
    supp = w > 0
    minm = float(mvec[supp].min())
    if which == 'J1':
        return min(A, minm)
    if which == 'J2':
        return arcbound_float(x, adj)
    if which == 'J3':
        b0 = W - float(x @ (gv * gv))
        return min(A, minm, b0)
    if which == 'minm':
        return minm
    if which == 'A':
        return A
    raise ValueError(which)


def hill_climb(M, q, which, rng, iters=400, start=None):
    adj, D, Q = circle_matrices(M)
    if start is None:
        w = np.zeros(M)
        k = rng.integers(3, min(12, M) + 1)
        idx = rng.choice(M, size=int(k), replace=False)
        rem = q
        for t, i in enumerate(idx):
            take = 1 if t < len(idx) - 1 else rem
            w[i] = take
            rem -= take
        # distribute the rest randomly
        for _ in range(int(rem)):
            w[idx[rng.integers(0, len(idx))]] += 1
    else:
        w = start.copy()
    cur = objective(w, adj, Q, which)
    for _ in range(iters):
        improved = False
        order_i = rng.permutation(M)
        for i in order_i:
            if w[i] <= 0:
                continue
            for j in rng.permutation(M):
                if j == i or w[i] <= 0:
                    continue
                w[i] -= 1
                w[j] += 1
                val = objective(w, adj, Q, which)
                if val > cur + 1e-15:
                    cur = val
                    improved = True
                else:
                    w[i] += 1
                    w[j] -= 1
        if not improved:
            break
    return w, cur


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'J1'
    Ms = [int(t) for t in (sys.argv[2].split(',') if len(sys.argv) > 2 else
                           ['10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60'])]
    qs = [int(t) for t in (sys.argv[3].split(',') if len(sys.argv) > 3 else ['12', '20', '30', '45'])]
    restarts = int(sys.argv[4]) if len(sys.argv) > 4 else 25
    rng = np.random.default_rng(20260725)
    target = 1.0 / 25
    best = (-1, None, None, None)
    for M in Ms:
        for q in qs:
            for r in range(restarts):
                w, val = hill_climb(M, q, which, rng)
                if val > best[0]:
                    best = (val, M, q, w.copy())
                    print(f"  new record {which}={val:.8f}  (M={M}, q={q})  w={w.astype(int).tolist()}",
                          flush=True)
                    if val > target + 1e-12:
                        print("  *** EXCEEDS 1/25 ***", flush=True)
        print(f"  ...M={M} done, best so far {best[0]:.8f} = {best[0]*25:.6f}/25", flush=True)
    val, M, q, w = best
    print(f"\nBEST {which} = {val:.10f}   ({val*25:.8f} x 1/25)   M={M} q={q}")
    print(f"weights = {w.astype(int).tolist()}")
    return best


if __name__ == '__main__':
    main()
