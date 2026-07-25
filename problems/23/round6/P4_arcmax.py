"""Route-viability probe for item (c): how large can ARCBOUND get?

An upper bound on ARCBOUND can only prove the conjecture if sup_mu ARCBOUND(mu) <= 1/25.
ARCBOUND >= psi always, so this is a strictly stronger statement than Erdos 23 restricted to
circle graphs, and it is NOT implied by it.  Here it is attacked with structured seeds
(C5 blow-ups, uniform, the recorded witnesses, W8) plus hill climbing, and with an exhaustive
sweep over all 5- and 6-atom integer configurations on Z_M for small M and q.

Also probes  J4 = min( min over HALF-arcs , min over THIRD-arcs ) : if that can exceed 1/25 then
the two extreme arc lengths do not suffice and genuinely intermediate arcs are needed.
"""
import itertools
import numpy as np
from fractions import Fraction as F
from P4_search import circle_matrices, arcbound_float
from P4_core import from_gamma, sort_cyclic, adjacency, arcbound, mono, TARGET

rng = np.random.default_rng(77)


def third_and_half(x, M):
    """min over all arcs of length exactly 1/3, and exactly 1/2, on the grid Z_M"""
    pos = np.arange(M) / M
    B = None
    i = np.arange(M)
    dif = np.abs(i[:, None] - i[None, :])
    dif = np.minimum(dif, M - dif) / M
    adj = (dif > 1.0 / 3 + 1e-12).astype(float)
    B = adj * np.outer(x, x)
    Wtot = 0.5 * B.sum()
    best3 = np.inf
    best2 = np.inf
    for t in (0.0, 1.0 / 3, 0.5, 2.0 / 3):
        for i0 in range(M):
            b = (i0 + t) / M
            d = np.abs(pos - b)
            d = np.minimum(d, 1 - d)
            u3 = (d > 1.0 / 3 + 1e-12).astype(float)
            u2 = (((pos - b) % 1.0) < 0.5).astype(float)
            for u, ref in ((u3, 3), (u2, 2)):
                cross = float(u @ (B @ (1 - u)))
                v = Wtot - cross
                if ref == 3:
                    best3 = min(best3, v)
                else:
                    best2 = min(best2, v)
    return best3, best2


def seeds(M, q):
    out = []
    # uniform
    w = np.full(M, q // M + 1.0)
    out.append(w)
    # C5 blow-up when 5 | M
    if M % 5 == 0:
        w = np.zeros(M)
        w[::M // 5] = q // 5 if q % 5 == 0 else 1
        out.append(w.copy())
        # unbalanced C5
        w2 = w.copy()
        w2[0] += 1
        out.append(w2)
    # C7-like
    if M % 7 == 0:
        w = np.zeros(M)
        w[::M // 7] = 1
        out.append(w)
    # random supports
    for _ in range(30):
        k = int(rng.integers(4, min(11, M) + 1))
        w = np.zeros(M)
        idx = rng.choice(M, size=k, replace=False)
        for i in idx:
            w[i] = rng.integers(1, 5)
        out.append(w)
    return out


def climb(w, M, obj, iters=60):
    cur = obj(w)
    for _ in range(iters):
        improved = False
        for i in rng.permutation(M):
            for j in rng.permutation(M):
                if i == j or w[i] <= 0:
                    continue
                w[i] -= 1
                w[j] += 1
                v = obj(w)
                if v > cur + 1e-14:
                    cur, improved = v, True
                else:
                    w[i] += 1
                    w[j] -= 1
        if not improved:
            break
    return w, cur


def main():
    print("=" * 90)
    print("(c) route viability: sup ARCBOUND  and  sup min(half-arc, third-arc)")
    print("=" * 90)
    for M in (10, 15, 20, 25, 30, 35, 40, 45, 60):
        adj, D, Q = circle_matrices(M)

        def f_arc(w):
            x = w / w.sum()
            return arcbound_float(x, adj)

        def f_j4(w):
            x = w / w.sum()
            a, b = third_and_half(x, M)
            return min(a, b)

        bestA = (-1, None)
        bestJ = (-1, None)
        for q in (10, 15, 20, 30):
            for s in seeds(M, q):
                s = s.copy()
                if s.sum() == 0:
                    continue
                w, v = climb(s.copy(), M, f_arc)
                if v > bestA[0]:
                    bestA = (v, w.astype(int).tolist())
                w, v = climb(s.copy(), M, f_j4)
                if v > bestJ[0]:
                    bestJ = (v, w.astype(int).tolist())
        print(f"  M={M:3d}  max ARCBOUND = {bestA[0]:.8f} ({bestA[0]*25:.5f}/25) at {bestA[1]}")
        print(f"        max min(half,third) = {bestJ[0]:.8f} ({bestJ[0]*25:.5f}/25) at {bestJ[1]}",
              flush=True)

    # exhaustive: all 5-atom and 6-atom integer configurations on Z_M, q <= qmax  (exact)
    print("\n  exhaustive exact sweep (5- and 6-atom supports):")
    for M, natoms, qmax in ((10, 5, 12), (12, 5, 12), (15, 5, 12), (20, 5, 10), (12, 6, 12), (15, 6, 10)):
        worst = (F(0), None)
        cnt = 0
        for supp in itertools.combinations(range(M), natoms):
            if supp[0] != 0:
                continue                      # rotation symmetry
            for comp in itertools.product(range(1, qmax + 1), repeat=natoms):
                if sum(comp) > qmax:
                    continue
                w = [0] * M
                for i, c in zip(supp, comp):
                    w[i] = c
                pos, wt = sort_cyclic(*from_gamma(M, w))
                ab = arcbound(pos, wt, adjacency(pos))
                cnt += 1
                if ab > worst[0]:
                    worst = (ab, (M, tuple(w)))
        print(f"    M={M:3d} atoms={natoms} q<={qmax:3d}: {cnt:8d} configs, max ARCBOUND = "
              f"{worst[0]} = {float(worst[0]):.8f}  {'<= 1/25 OK' if worst[0] <= TARGET else '*** > 1/25 ***'}"
              f"  at {worst[1][1] if worst[1] else None}", flush=True)


if __name__ == '__main__':
    main()
