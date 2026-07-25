"""
f8_srg_verify.py -- EXACT determination of bip for the triangle-free strongly
regular graphs, by matching an eigenvalue lower bound with an explicit cut.

Lower bound.  For a d-regular graph, maxcut = (1/4) max_{x in {+-1}^n} x^T(dI-A)x
              <= (1/4) n (d - lambda_min),  hence  bip = m - maxcut >= n(d+lambda_min)/4.
              lambda_min is obtained EXACTLY from the strongly-regular identity
              A^2 + (mu-lambda) A - (d-mu) I = mu J, verified here with exact
              integer matrix arithmetic; the two non-principal eigenvalues are the
              roots of  t^2 + (mu-lambda) t - (d-mu) = 0.

Upper bound.  An explicit bipartition, its monochromatic edge count computed with
              exact integer arithmetic.

When the two coincide, bip is determined exactly.
"""
import numpy as np
from fractions import Fraction
from f8_core import edges_of, is_triangle_free
from f8_families import hoffman_singleton, higman_sims, clebsch, kneser


def adjmat(n, adj):
    A = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            if (adj[i] >> j) & 1:
                A[i, j] = 1
    return A


def check_srg(A, d, lam, mu):
    n = A.shape[0]
    I = np.eye(n, dtype=np.int64)
    J = np.ones((n, n), dtype=np.int64)
    ok_reg = bool(np.all(A.sum(1) == d))
    ok_srg = bool(np.array_equal(A.dot(A) + (mu - lam) * A - (d - mu) * I, mu * J))
    return ok_reg, ok_srg


def lambda_min_from_srg(d, lam, mu):
    """roots of t^2 + (mu-lam) t - (d-mu) = 0 ; returns the smaller (exact if disc is a square)"""
    b = mu - lam
    disc = b * b + 4 * (d - mu)
    r = int(round(disc ** 0.5))
    assert r * r == disc, ("discriminant not a perfect square", disc)
    return (-b - r) // 2, (-b + r) // 2


def local_search_cut(n, adj, rounds=4000, seed=1):
    rng = np.random.default_rng(seed)
    nb = [[j for j in range(n) if (adj[i] >> j) & 1] for i in range(n)]
    deg = np.array([len(x) for x in nb])
    m = int(deg.sum()) // 2
    best, bestside = m, None
    for _ in range(rounds):
        side = rng.integers(0, 2, size=n)
        improved = True
        while improved:
            improved = False
            for i in range(n):
                same = sum(1 for j in nb[i] if side[j] == side[i])
                if 2 * same - deg[i] > 0:
                    side[i] ^= 1
                    improved = True
        mono = sum(1 for i in range(n) for j in nb[i] if j > i and side[i] == side[j])
        if mono < best:
            best, bestside = mono, side.copy()
    return best, bestside, m


def exact_mono(n, adj, side):
    """exact integer count of monochromatic edges"""
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1 and side[i] == side[j]:
                c += 1
    return c


def induced(n, adj, keep):
    keep = sorted(keep)
    idx = {v: i for i, v in enumerate(keep)}
    a2 = [0] * len(keep)
    for v in keep:
        for w in keep:
            if v != w and (adj[v] >> w) & 1:
                a2[idx[v]] |= 1 << idx[w]
    return len(keep), a2


_hsn, _hsa = higman_sims()
_M22 = induced(_hsn, _hsa, [w for w in range(_hsn) if w != 0 and not (_hsa[0] >> w) & 1])
_u = 0
_v = next(w for w in range(_hsn) if (_hsa[0] >> w) & 1)
_GEW = induced(_hsn, _hsa, [w for w in range(_hsn)
                            if w not in (_u, _v) and not (_hsa[_u] >> w) & 1
                            and not (_hsa[_v] >> w) & 1])

CASES = [("Clebsch",           clebsch(),            5,  0, 2),
         ("Gewirtz",           _GEW,                10,  0, 2),
         ("M22graph",          _M22,                16,  0, 4),
         ("Petersen",          kneser(5, 2),         3,  0, 1),
         ("HoffmanSingleton",  hoffman_singleton(),  7,  0, 1),
         ("HigmanSims",        higman_sims(),       22,  0, 6)]

print(f"{'graph':20s} {'n':>4} {'m':>5} {'d':>3} {'lmin':>5} {'LB=n(d+lmin)/4':>15} "
      f"{'cut UB':>7} {'bip':>7}  {'bip/N^2':>12}")
for name, (n, adj), d, lam, mu in CASES:
    assert is_triangle_free(n, adj)
    A = adjmat(n, adj)
    ok_reg, ok_srg = check_srg(A, d, lam, mu)
    s, r = lambda_min_from_srg(d, lam, mu)
    m = len(edges_of(n, adj))
    lb = Fraction(n * (d + s), 4)
    ub, side, m2 = local_search_cut(n, adj, rounds=(2000 if n < 60 else 400), seed=7)
    assert m2 == m
    assert exact_mono(n, adj, side) == ub
    exact = "EXACT" if Fraction(ub) == lb or (lb <= ub and ub < lb + 1) else "gap"
    print(f"{name:20s} {n:>4} {m:>5} {d:>3} {s:>5} {str(lb):>15} {ub:>7} "
          f"{ub if exact=='EXACT' else '?':>7}  {str(Fraction(ub,n*n)):>12}   "
          f"reg={ok_reg} srg-identity={ok_srg}  [{exact}]")
    np.save(f"f8_cut_{name}.npy", side)
