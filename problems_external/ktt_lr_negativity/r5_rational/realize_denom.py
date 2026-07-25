#!/usr/bin/env python3
"""Which tight-basis denominators can actually occur at a vertex of a genuine
r=5 hive polytope?

For a nonsingular 6-subset S of rows, x(p) = A_S^{-1} D_S p is linear and
homogeneous in the partition data p = (lam,mu,nu) in Z^15.  x(p) is a vertex of
Q(p) iff  A x(p) <= D p , which is the homogeneous system (A adj_S D_S - d D)p <= 0.
Together with the partition cone (weakly decreasing, nonnegative, |lam|+|mu|=|nu|)
this is a rational polyhedral cone K_S.  A float LP searches for a point of K_S
with sum(nu)=1; every verdict is then re-verified EXACTLY over the integers.

Stage 1 : is K_S nonempty (i.e. can S be a tight vertex basis at all)?
Stage 2 : among realizable S, scan integer p in K_S for the target denominator.
"""

import itertools
import json
import sys
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

from hiveR import fixed_A


def build():
    A, Dm, tags = fixed_A(5)
    m, D, k = len(A), 6, 15
    An = np.array(A, dtype=np.int64)
    Dn = np.array(Dm, dtype=np.int64)
    combos = np.array(list(itertools.combinations(range(m), D)), dtype=np.int32)
    M = An[combos]
    det = np.rint(np.linalg.det(M.astype(np.float64))).astype(np.int64)
    ns = det != 0
    Ms, ds, Cs = M[ns], det[ns], combos[ns]
    adj = np.rint(np.linalg.inv(Ms.astype(np.float64)) * ds[:, None, None]).astype(np.int64)
    assert np.all(np.matmul(Ms, adj) == np.eye(D, dtype=np.int64)[None] * ds[:, None, None])
    neg = ds < 0
    adj[neg] = -adj[neg]
    ds = np.abs(ds)
    G = np.zeros((k, k - 1), dtype=np.int64)
    vv = np.array([1] * 5 + [1] * 5 + [-1] * 5, dtype=np.int64)
    for i in range(k - 1):
        G[i, i] = 1
        G[k - 1, i] = vv[i]
    NN = np.matmul(adj, np.matmul(Dn[Cs], G))
    g = np.gcd.reduce(np.abs(NN).reshape(NN.shape[0], -1), axis=1)
    denq = ds // np.gcd(g, ds)
    Pc = []
    for off in (0, 5, 10):
        for i in range(4):
            r = [0] * k
            r[off + i] = -1
            r[off + i + 1] = 1
            Pc.append(r)
        r = [0] * k
        r[off + 4] = -1
        Pc.append(r)
    return An, Dn, Cs, adj, ds, denq, np.array(Pc, dtype=np.int64), vv, G


def cone_point(Ccon, Pc, vv):
    """float LP: find p with Ccon p <= 0, Pc p <= 0, vv.p = 0, sum(nu) = 1."""
    k = 15
    Aub = np.vstack([Ccon, Pc]).astype(np.float64)
    Aeq = np.vstack([vv.astype(np.float64), np.array([[0.0] * 10 + [1.0] * 5])])
    res = linprog(np.zeros(k), A_ub=Aub, b_ub=np.zeros(Aub.shape[0]),
                  A_eq=Aeq, b_eq=[0.0, 1.0], bounds=[(None, None)] * k,
                  method="highs")
    return res.x if res.success else None


def main():
    targets = [int(t) for t in (sys.argv[1].split(",") if len(sys.argv) > 1
                                else ["7", "6", "5", "4", "3", "2"])]
    An, Dn, Cs, adj, ds, denq, Pc, vv, G = build()
    out = {}
    for q in targets:
        idxs = np.nonzero(denq == q)[0]
        rec = {"bases_with_denominator": int(idxs.size),
               "bases_tested": 0, "bases_cone_nonempty": 0,
               "denominator_realized": False}
        witness = None
        for t in idxs[:1500]:
            rec["bases_tested"] += 1
            S = Cs[t]
            d = int(ds[t])
            Ccon = An @ adj[t] @ Dn[S] - d * Dn
            x = cone_point(Ccon, Pc, vv)
            if x is None:
                continue
            # rationalise
            base = None
            for sc in (1, 2, 3, 4, 6, 12, 24, 30, 60, 120, 210, 420, 840, 2520):
                cand = np.rint(x * sc).astype(np.int64)
                if np.any(cand != 0) and np.all(Ccon @ cand <= 0) and \
                   np.all(Pc @ cand <= 0) and int(vv @ cand) == 0:
                    base = cand
                    break
            if base is None:
                continue
            rec["bases_cone_nonempty"] += 1
            rng = np.random.default_rng(1234 + int(t))
            for trial in range(3000):
                mult = 1 + trial % 30
                if trial == 0:
                    cand = base.copy()
                else:
                    w = rng.integers(-3, 4, size=14)
                    cand = base * mult + G @ w
                if not (np.all(Ccon @ cand <= 0) and np.all(Pc @ cand <= 0)
                        and int(vv @ cand) == 0 and np.any(cand != 0)):
                    continue
                num = adj[t] @ (Dn[S] @ cand)
                lq = 1
                for xx in num:
                    dd = Fraction(int(xx), d).denominator
                    lq = lq * dd // np.gcd(lq, dd)
                if lq == q:
                    witness = {"lam": [int(z) for z in cand[:5]],
                               "mu": [int(z) for z in cand[5:10]],
                               "nu": [int(z) for z in cand[10:]],
                               "vertex": [str(Fraction(int(z), d)) for z in num],
                               "basis_rows": [int(z) for z in S], "det": d}
                    break
            if witness:
                rec["denominator_realized"] = True
                rec["witness"] = witness
                break
        out[str(q)] = rec
        print(q, json.dumps(rec), flush=True)
    with open("realize_denom.json", "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
