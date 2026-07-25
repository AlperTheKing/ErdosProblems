#!/usr/bin/env python3
"""Exact vertex enumeration for r=5 hive polytopes, plus a realized-denominator
scan and the dilation check  a_k(Q) = a_k(qQ)/q^k .

Every vertex is A_S^{-1} b_S for a nonsingular 6-subset S of the 30 rhombus
rows; all such subsets are enumerated, so the vertex list is complete.
Candidate solutions are kept as (numerator, det) integer pairs and feasibility
is decided by the integer test  A.num <= b*det  (det > 0 by construction),
so no float ever decides anything.  int64 overflow is guarded by an explicit
magnitude assertion.
"""

import itertools
import json
import random
import sys
from fractions import Fraction

import numpy as np

from hiveR import fixed_A, build_hive, interior, det_int
from count5 import lr_count

_TAB = {}


def table(r=5):
    if r in _TAB:
        return _TAB[r]
    A, Dm, tags = fixed_A(r)
    D = len(A[0])
    An = np.array(A, dtype=np.int64)
    combos = np.array(list(itertools.combinations(range(len(A)), D)), dtype=np.int32)
    M = An[combos]
    det = np.rint(np.linalg.det(M.astype(np.float64))).astype(np.int64)
    ns = det != 0
    Ms, ds, Cs = M[ns], det[ns], combos[ns]
    adj = np.rint(np.linalg.inv(Ms.astype(np.float64)) * ds[:, None, None]).astype(np.int64)
    eye = np.eye(D, dtype=np.int64)[None, :, :] * ds[:, None, None]
    assert np.all(np.matmul(Ms, adj) == eye), "adjugate verification failed"
    neg = ds < 0
    adj[neg] = -adj[neg]
    ds = np.abs(ds)
    _TAB[r] = (An, adj, ds, Cs, D)
    return _TAB[r]


def vertices(b, r=5):
    """Exact vertex list (tuples of Fraction) of {A x <= b}."""
    An, adj, ds, Cs, D = table(r)
    bn = np.array(b, dtype=np.int64)
    bS = bn[Cs]                                     # (nb, 6)
    num = np.einsum("nij,nj->ni", adj, bS)          # (nb, 6) integer numerators
    assert np.abs(num).max() < 2 ** 40, "int64 magnitude guard"
    lhs = num @ An.T                                # (nb, m)
    rhs = ds[:, None] * bn[None, :]
    assert np.abs(lhs).max() < 2 ** 60 and np.abs(rhs).max() < 2 ** 60
    ok = np.all(lhs <= rhs, axis=1)
    out = set()
    for n_, d_ in zip(num[ok], ds[ok]):
        out.add(tuple(Fraction(int(x), int(d_)) for x in n_))
    return sorted(out)


def affine_dim(V):
    if not V:
        return -1
    P = np.array([[float(c) for c in v] for v in V])
    return int(np.linalg.matrix_rank(P[1:] - P[0])) if len(V) > 1 else 0


def analyze(lam, mu, nu, r=5, nmax=9):
    H = build_hive(lam, mu, nu, r)
    if not H["ok"]:
        return None
    V = vertices(H["b"], r)
    if not V:
        return None
    dens = sorted({c.denominator for v in V for c in v})
    q = 1
    for d in dens:
        q = q * d // np.gcd(q, d)
    return {"lam": lam, "mu": mu, "nu": nu, "n_vertices": len(V),
            "denoms": dens, "q": int(q), "dim": affine_dim(V), "V": V}


def scan(n=400, seed=7, maxpart=9):
    from validate5 import make_triples
    trips = make_triples(n, seed=seed)
    best = {}
    worst = 1
    rec = None
    for i, (lam, mu, nu) in enumerate(trips):
        a = analyze(lam, mu, nu)
        if a is None:
            continue
        for d in a["denoms"]:
            best[d] = best.get(d, 0) + 1
        if a["q"] > worst:
            worst = a["q"]
            rec = {k: a[k] for k in ("lam", "mu", "nu", "denoms", "q", "dim", "n_vertices")}
        if (i + 1) % 50 == 0:
            print("  scanned %d  max_q=%d" % (i + 1, worst), flush=True)
    return {"scanned": len(trips), "denominator_counts": best,
            "max_lcm_denominator_realized": worst, "witness": rec}


def dilation_check(lam, mu, nu, r=5, nmax=10):
    """P_Q(n) = L(nQ); check L_{qQ}(n) = P_Q(qn) and a_k(qQ) = q^k a_k(Q)."""
    a = analyze(lam, mu, nu, r)
    q = a["q"]
    d = a["dim"]
    LQ = [lr_count(lam, mu, nu, r, n) for n in range(d + 1)]
    P = interp(LQ)
    for n in range(d + 1, min(nmax, d + 4)):
        assert polyval(P, n) == lr_count(lam, mu, nu, r, n), "P not a polynomial"
    # qQ = {x : A x <= q b}; its Ehrhart values are L(n q Q) = P(q n)
    LqQ = [lr_count(lam, mu, nu, r, q * n) for n in range(d + 1)]
    Pq = interp(LqQ)
    ok = all(Pq[k] == P[k] * Fraction(q) ** k for k in range(len(P)))
    return {"q": q, "dim": d,
            "P_Q": [str(x) for x in P], "P_qQ": [str(x) for x in Pq],
            "a_k(qQ) == q^k a_k(Q)": bool(ok),
            "min_coeff_Q": str(min(P)), "min_coeff_qQ": str(min(Pq))}


def interp(vals):
    k = len(vals)
    co = [Fraction(0)] * k
    for i in range(k):
        num = [Fraction(1)]
        den = Fraction(1)
        for j in range(k):
            if j == i:
                continue
            num = polymul(num, [Fraction(-j), Fraction(1)])
            den *= Fraction(i - j)
        f = Fraction(vals[i]) / den
        for t, c in enumerate(num):
            co[t] += f * c
    return co


def polymul(p, q):
    o = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, c in enumerate(q):
            o[i + j] += a * c
    return o


def polyval(P, t):
    s = Fraction(0)
    for c in reversed(P):
        s = s * t + c
    return s


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ce"
    if mode == "ce":
        a = analyze([2, 2, 1], [4, 3, 2, 1], [5, 4, 3, 2, 1])
        print(json.dumps({k: (v if k != "V" else [[str(c) for c in x] for x in v])
                          for k, v in a.items()}, indent=1))
        print(json.dumps(dilation_check([2, 2, 1], [4, 3, 2, 1], [5, 4, 3, 2, 1]), indent=1))
    elif mode == "scan":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 400
        sd = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        res = scan(n, sd)
        print(json.dumps(res, indent=1, default=str))
        with open("scan_denoms_%d.json" % sd, "w") as f:
            json.dump(res, f, indent=1, default=str)
