#!/usr/bin/env python3
"""
lattice_certificate.py -- BAND 10: exact certificate that EVERY vertex of EVERY
r=4 hive polytope is a LATTICE point, at every weight.

WHY IT IS NEEDED.  The band-10 bound "c = 4  =>  V = 1" (subset_atlas.py) uses
that Q is a LATTICE polytope: c = 4 lattice points in a 3-dim lattice polytope
forces an empty lattice simplex, whose volume is the (b-independent) vertex-cone
multiplicity.  If some Q had a non-integral vertex, that step would not apply.

THE CERTIFICATE.  Every vertex of Q = {h : A h <= b} solves M h = b_T for a
3-subset T of rows with det M != 0, so h = adj(M) b_T / det(M).  Hence h is
integral for EVERY integral b iff  adj(M) b_T = 0 (mod |det M|)  identically.
b is an INTEGER-LINEAR function of the 12 parts v = (lam,mu,nu) with no constant
term (b = L(v)), and the admissible v range inside the weight-zero lattice
    W = { v in Z^12 : |lam| + |mu| - |nu| = 0 },
so it suffices to verify  adj(M) L(w) = 0 (mod |det M|)  on an 11-element BASIS
of W: the map is a group homomorphism, so it then vanishes on all of W, hence on
every partition triple of any weight.

Everything below is exact integer arithmetic.
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from hive4 import build_hive4, _det3  # noqa: E402


def rows_and_b(v):
    """A (fixed) and b for the 12-vector v = (lam,mu,nu); no partition validation."""
    lam, mu, nu = v[0:4], v[4:8], v[8:12]
    B = {}
    acc = 0
    for y in range(5):
        B[(0, y)] = acc
        if y < 4:
            acc += lam[y]
    sl = sum(lam)
    acc = 0
    for x in range(5):
        B[(x, 4 - x)] = sl + acc
        if x < 4:
            acc += mu[x]
    acc = 0
    for x in range(5):
        B[(x, 0)] = acc
        if x < 4:
            acc += nu[x]
    B[(0, 0)] = 0
    INT = {(1, 1): 0, (1, 2): 1, (2, 1): 2}
    A, b = [], []

    def add(plus, minus):
        co = [0, 0, 0]
        const = 0
        for w in plus:
            if w in INT:
                co[INT[w]] -= 1
            else:
                const -= B[w]
        for w in minus:
            if w in INT:
                co[INT[w]] += 1
            else:
                const += B[w]
        if co == [0, 0, 0]:
            return
        A.append(co)
        b.append(-const)

    for x in range(5):
        for y in range(5):
            if x + y <= 2:
                add([(x + 1, y), (x, y + 1)], [(x, y), (x + 1, y + 1)])
            if y >= 1 and x + y <= 3:
                add([(x, y), (x + 1, y)], [(x, y + 1), (x + 1, y - 1)])
            if x >= 1 and x + y <= 3:
                add([(x, y), (x, y + 1)], [(x + 1, y), (x - 1, y + 1)])
    return A, b


def adjugate3(M):
    def minor(r, c):
        rs = [x for x in range(3) if x != r]
        cs = [x for x in range(3) if x != c]
        return M[rs[0]][cs[0]] * M[rs[1]][cs[1]] - M[rs[0]][cs[1]] * M[rs[1]][cs[0]]
    return [[(-1) ** (r + c) * minor(c, r) for c in range(3)] for r in range(3)]


def main():
    # fixed A, from any triple; check A really is v-independent
    A0, _ = rows_and_b([5, 3, 1, 0, 6, 4, 2, 0, 9, 6, 4, 2])
    A1, _ = rows_and_b([100, 7, 3, 1, 50, 9, 2, 0, 61, 33, 12, 5])
    assert A0 == A1, "A depends on v -- the whole moduli reduction is wrong"
    A = A0
    n = len(A)

    # basis of W = {v : sum(lam)+sum(mu)-sum(nu) = 0}, rank 11
    def e(i):
        z = [0] * 12
        z[i] = 1
        return z

    def add_v(a, bvec, s=1):
        return [a[i] + s * bvec[i] for i in range(12)]

    basis = []
    for i in [1, 2, 3]:
        basis.append(add_v(e(i), e(0), -1))          # lam_i - lam_1
    for i in [5, 6, 7]:
        basis.append(add_v(e(i), e(4), -1))          # mu_i - mu_1
    for i in [9, 10, 11]:
        basis.append(add_v(e(i), e(8), -1))          # nu_i - nu_1
    basis.append(add_v(e(0), e(8)))                  # lam_1 + nu_1
    basis.append(add_v(e(4), e(8)))                  # mu_1 + nu_1
    assert len(basis) == 11
    for w in basis:
        assert sum(w[0:4]) + sum(w[4:8]) - sum(w[8:12]) == 0

    bofw = [rows_and_b(w)[1] for w in basis]

    det_hist = {}
    bad = []
    ntrip = 0
    for T in itertools.combinations(range(n), 3):
        M = [A[T[0]], A[T[1]], A[T[2]]]
        D = _det3(M)
        if D == 0:
            continue
        ntrip += 1
        d = abs(D)
        det_hist[d] = det_hist.get(d, 0) + 1
        if d == 1:
            continue
        adj = adjugate3(M)
        for wi, bw in enumerate(bofw):
            bt = [bw[T[0]], bw[T[1]], bw[T[2]]]
            for r in range(3):
                s = sum(adj[r][k] * bt[k] for k in range(3))
                if s % d != 0:
                    bad.append({"triple": list(T), "det": D, "basis_index": wi,
                                "coord": r, "residue": s % d})
    out = {
        "n_rows": n,
        "n_nonsingular_row_triples": ntrip,
        "det_histogram": {str(k): v for k, v in sorted(det_hist.items())},
        "n_violations": len(bad),
        "violations": bad[:20],
        "CERTIFIED": len(bad) == 0,
        "VERDICT": (
            "For every 3-subset T of the 18 rhombus rows with det != 0 and every "
            "element w of a basis of the weight-zero lattice W, adj(M_T) b_T(w) = 0 "
            "mod |det M_T|.  By linearity this holds for every v in W, hence for "
            "EVERY partition triple (lam,mu,nu) of EVERY weight: every candidate "
            "vertex of every r=4 hive polytope has integral coordinates.  Q is "
            "always a LATTICE polytope."
            if len(bad) == 0 else
            "NOT certified: a non-integral vertex is possible; see violations."
        ),
    }
    print(json.dumps(out, indent=1))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
