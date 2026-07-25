"""Is the W8 refutation still valid inside the class the Brandt-Thomasse reduction actually
delivers, i.e. weighted graphs with MINIMUM WEIGHTED DEGREE > 1/3?

W8 has one atom with g(b) = 1/3 exactly, so a defender of item 7 could claim it is out of scope.
Here the same objective is maximised under the hard constraint  min_{b in supp} g(b) > 1/3,
which is exactly delta(G,omega) > 1/3 in Brandt-Thomasse's weighted language.
"""
import sys
import numpy as np
from P4_search import circle_matrices

rng = np.random.default_rng(1234)
THIRD = 1.0 / 3


def obj_factory(adj, Q, mode):
    def f(w):
        if w.sum() <= 0:
            return -9.0
        x = w / w.sum()
        gv = adj @ x
        W = 0.5 * float(x @ gv)
        A = 0.5 * float(x @ (Q @ x))
        mvec = W - adj @ (x * gv)
        supp = w > 0
        ming = float(gv[supp].min())
        minm = float(mvec[supp].min())
        base = min(A, minm) if mode == 'J1' else minm
        pen = 0.0
        if ming <= THIRD + 1e-12:
            pen = 10.0 * (THIRD + 1e-12 - ming) + 1.0
        return base - pen
    return f


def climb(w, M, f, iters=80):
    cur = f(w)
    for _ in range(iters):
        improved = False
        for i in rng.permutation(M):
            for j in rng.permutation(M):
                if i == j or w[i] <= 0:
                    continue
                w[i] -= 1
                w[j] += 1
                v = f(w)
                if v > cur + 1e-14:
                    cur, improved = v, True
                else:
                    w[i] += 1
                    w[j] -= 1
        if not improved:
            break
    return w, cur


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'J1'
    print(f"constrained search, objective {mode}, hard constraint min_supp g(b) > 1/3")
    best = (-9, None, None)
    for M in (11, 14, 17, 20, 23, 26, 29, 32, 35, 41, 44, 50):
        adj, D, Q = circle_matrices(M)
        f = obj_factory(adj, Q, mode)
        bm = (-9, None)
        for q in (M, 2 * M, 3 * M, 30, 45, 60):
            starts = [np.full(M, float(max(1, q // M)))]
            for _ in range(12):
                s = np.full(M, float(max(1, q // M)))
                for _ in range(int(q // 3)):
                    i = rng.integers(0, M)
                    j = rng.integers(0, M)
                    if s[i] > 0:
                        s[i] -= 1
                        s[j] += 1
                starts.append(s)
            for s in starts:
                w, v = climb(s.copy(), M, f)
                if v > bm[0]:
                    bm = (v, w.astype(int).tolist())
                if v > best[0]:
                    best = (v, M, w.astype(int).tolist())
        print(f"  M={M:3d}  best {mode} under delta>1/3 = {bm[0]:.8f} "
              f"({bm[0]*25:.5f}/25)   w={bm[1]}", flush=True)
    print(f"\nBEST {best[0]:.8f} = {best[0]*25:.6f}/25   on Gamma_{best[1]}   w={best[2]}")


if __name__ == '__main__':
    main()
