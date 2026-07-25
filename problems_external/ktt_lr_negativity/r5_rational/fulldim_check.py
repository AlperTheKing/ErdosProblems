#!/usr/bin/env python3
"""Is a maximal-denominator tight basis realizable at a vertex of a genuine
hive polytope?

K_S = { z in Z^14 : R z <= 0 }  (R = the non-trivial rows of
       A adj_S D_S - d D  and the partition-cone rows, in the coordinates
       p = G z of the lattice |lam|+|mu|=|nu|).

If K_S contains an integer point with R z < 0 STRICTLY, then K_S is
full-dimensional, so for every M large the open cone contains every integer
point of a box of side > d around M z.  Since d is prime and N = adj_S D_S G
has an entry not divisible by d, some z in that box has N z != 0 mod d, and the
corresponding hive polytope has a vertex of denominator exactly d.

A strict integer z is searched for with a float LP and then VERIFIED exactly.
"""

import itertools
import json
import sys
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

from realize_denom import build
from hiveR import fixed_A


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    An, Dn, Cs, adj, ds, denq, Pc, vv, G = build()
    idxs = np.nonzero(denq == target)[0]
    print("bases with denominator %d: %d" % (target, idxs.size), flush=True)
    hits = []
    for t in idxs:
        S = Cs[t]
        d = int(ds[t])
        Ccon = An @ adj[t] @ Dn[S] - d * Dn
        R = np.vstack([Ccon, Pc]) @ G                    # rows in z-coordinates
        R = R[np.any(R != 0, axis=1)]
        n = R.shape[0]
        # max s  s.t.  R z + s <= 0, s <= 1, |z| <= 1000
        Aub = np.hstack([R.astype(np.float64), np.ones((n, 1))])
        c = np.zeros(15)
        c[-1] = -1.0
        res = linprog(c, A_ub=Aub, b_ub=np.zeros(n),
                      bounds=[(-1000, 1000)] * 14 + [(0, 1)], method="highs")
        if not res.success or res.x[-1] < 1e-9:
            continue
        z = res.x[:14]
        got = None
        for sc in (1, 2, 4, 8, 16, 64, 256, 1024, 4096, 16384):
            zi = np.rint(z * sc).astype(np.int64)
            if np.all(R @ zi < 0):
                got = zi
                break
        if got is None:
            continue
        # explicit witness: scale up and hunt a residue with denominator d
        N = adj[t] @ Dn[S] @ G
        found = None
        rng = np.random.default_rng(9)
        for M in (1, 2, 4, 8, 16, 32, 64, 128):
            zz = got * M
            for _ in range(3000):
                w = rng.integers(-d, d + 1, size=14)
                cand = zz + w
                if not np.all(R @ cand <= 0):
                    continue
                num = N @ cand
                lq = 1
                for xx in num:
                    dd = Fraction(int(xx), d).denominator
                    lq = lq * dd // int(np.gcd(lq, dd))
                if lq == d:
                    p = G @ cand
                    found = {"lam": [int(x) for x in p[:5]],
                             "mu": [int(x) for x in p[5:10]],
                             "nu": [int(x) for x in p[10:]],
                             "vertex": [str(Fraction(int(x), d)) for x in num],
                             "det": d, "basis_rows": [int(x) for x in S]}
                    break
            if found:
                break
        hits.append({"basis": [int(x) for x in S], "det": d,
                     "full_dimensional_cone": True, "witness": found})
        print(json.dumps(hits[-1]), flush=True)
        if found:
            break
    res = {"target_denominator": target, "bases": int(idxs.size),
           "full_dim_bases_found": len(hits),
           "realized": any(h["witness"] for h in hits),
           "hits": hits[:3]}
    print(json.dumps(res, indent=1))
    with open("fulldim_%d.json" % target, "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
