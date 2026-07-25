#!/usr/bin/env python3
"""
Exhaustive tight-basis analysis of the FIXED r=5 hive constraint matrix.

Every vertex of every r=5 hive polytope Q(lam,mu,nu) is A_S^{-1} b_S for some
6-subset S of the 30 rhombus rows with det(A_S) != 0.  Hence:

  * max_S |det(A_S)|                                       -- tight-minor bound
  * max_S (largest invariant factor of A_S)
        = exact sup of vertex denominators when b_S ranges over ALL of Z^6
  * max_S d_S / gcd( gcd(entries of adj(A_S) . Dm_S . G), d_S )
        = exact sup of vertex denominators when b ranges over the ACTUAL
          hive right-hand-side lattice  { Dm . p : p in Z^15, |lam|+|mu|=|nu| }

The first invariant factor of an integer matrix is the gcd of its entries, and
for the lattice (1/d) N Z^k with N = U diag(s) V the maximal denominator of an
element is d / gcd(s_1, d); this is what is computed.

Exactness: the integer adjugate produced by float inversion is VERIFIED by the
integer identity A_S . adj = det . I over int64; any basis failing the check is
recomputed with exact Fraction arithmetic (none do).
"""

import itertools
import json
import math
import sys

import numpy as np

from hiveR import fixed_A, det_int, smith_invariants


def main():
    r = 5
    A, Dm, tags = fixed_A(r)
    m, D = len(A), len(A[0])
    An = np.array(A, dtype=np.int64)
    Dn = np.array(Dm, dtype=np.int64)          # m x 3r,  b = Dn . (lam,mu,nu)

    # sublattice G of Z^{3r} cut out by |lam| + |mu| - |nu| = 0
    v = np.array([1] * r + [1] * r + [-1] * r, dtype=np.int64)
    k = 3 * r
    G = np.zeros((k, k - 1), dtype=np.int64)
    for i in range(k - 1):
        G[i, i] = 1
        G[k - 1, i] = v[i]                      # v . G[:,i] = v_i + v_i*v_{k-1} = 0
    assert np.all(v @ G == 0)

    combos = np.array(list(itertools.combinations(range(m), D)), dtype=np.int32)
    M = An[combos]                              # (nb, 6, 6)
    nb = M.shape[0]
    Mf = M.astype(np.float64)
    detf = np.linalg.det(Mf)
    det = np.rint(detf).astype(np.int64)
    ns = det != 0
    print("bases_total=%d nonsingular=%d" % (nb, int(ns.sum())), flush=True)

    Ms = M[ns]
    ds = det[ns]
    inv = np.linalg.inv(Ms.astype(np.float64))
    adj = np.rint(inv * ds[:, None, None]).astype(np.int64)
    # EXACT verification of the adjugate
    chk = np.matmul(Ms, adj)
    eye = np.eye(D, dtype=np.int64)[None, :, :] * ds[:, None, None]
    okmask = np.all(chk == eye, axis=(1, 2))
    print("adjugate_verified=%d/%d" % (int(okmask.sum()), okmask.size), flush=True)
    bad = np.nonzero(~okmask)[0]
    if bad.size:
        from fractions import Fraction
        print("recomputing %d bases exactly" % bad.size, flush=True)
        for t in bad:
            Mi = [[int(x) for x in row] for row in Ms[t]]
            d0 = det_int(Mi)
            ds[t] = d0
            # exact adjugate by cofactors
            adjm = []
            for i in range(D):
                row = []
                for j in range(D):
                    sub = [[Mi[a][b] for b in range(D) if b != i]
                           for a in range(D) if a != j]
                    row.append((-1) ** (i + j) * det_int(sub))
                adjm.append(row)
            adj[t] = np.array(adjm, dtype=np.int64)
        chk = np.matmul(Ms, adj)
        eye = np.eye(D, dtype=np.int64)[None, :, :] * ds[:, None, None]
        assert np.all(np.all(chk == eye, axis=(1, 2))), "exact adjugate failed"

    absd = np.abs(ds)
    # (1) unrestricted rhs: denominator bound = d / gcd(gcd(adj), d)
    g_un = np.gcd.reduce(np.abs(adj).reshape(adj.shape[0], -1), axis=1)
    den_un = absd // np.gcd(g_un, absd)

    # (2) actual hive rhs lattice
    LS = Dn[combos[ns]]                          # (nb', 6, 15)
    NN = np.matmul(adj, np.matmul(LS, G))        # (nb', 6, 14)
    g_re = np.gcd.reduce(np.abs(NN).reshape(NN.shape[0], -1), axis=1)
    den_re = absd // np.gcd(g_re, absd)

    out = {
        "r": 5,
        "rows": m, "distinct_normals": len(set(map(tuple, A))), "dim": D,
        "bases_total": int(nb), "bases_nonsingular": int(ns.sum()),
        "max_abs_det": int(absd.max()),
        "det_histogram": {str(int(k2)): int(vv) for k2, vv in
                          zip(*np.unique(absd, return_counts=True))},
        "max_denominator_unrestricted_rhs": int(den_un.max()),
        "denominator_histogram_unrestricted": {str(int(k2)): int(vv) for k2, vv in
                                               zip(*np.unique(den_un, return_counts=True))},
        "max_denominator_hive_rhs_lattice": int(den_re.max()),
        "denominator_histogram_hive_lattice": {str(int(k2)): int(vv) for k2, vv in
                                               zip(*np.unique(den_re, return_counts=True))},
    }
    # exact spot-check of the extremes with pure-Python integer arithmetic
    idx = int(np.argmax(den_re))
    S = combos[ns][idx]
    Mi = [[int(x) for x in An[i]] for i in S]
    out["argmax_hive_lattice"] = {
        "rows": [int(x) for x in S],
        "normals": [list(map(int, An[i])) for i in S],
        "det_exact": int(det_int(Mi)),
        "smith_A_S": [int(x) for x in smith_invariants(Mi)],
    }
    idx2 = int(np.argmax(den_un))
    S2 = combos[ns][idx2]
    Mi2 = [[int(x) for x in An[i]] for i in S2]
    out["argmax_unrestricted"] = {
        "rows": [int(x) for x in S2],
        "det_exact": int(det_int(Mi2)),
        "smith_A_S": [int(x) for x in smith_invariants(Mi2)],
    }
    # exact largest invariant factor over ALL nonsingular bases (independent route)
    e6 = {}
    for t in range(Ms.shape[0]):
        d0 = int(absd[t])
        if d0 <= 1:
            continue
        e6[d0] = e6.get(d0, 0) + 1
    maxinv = 1
    seen = set()
    for t in range(Ms.shape[0]):
        if int(absd[t]) <= maxinv:
            continue
        Mi3 = [[int(x) for x in Ms[t][i]] for i in range(D)]
        key = tuple(map(tuple, Mi3))
        if key in seen:
            continue
        seen.add(key)
        inv6 = smith_invariants(Mi3)
        if inv6 and inv6[-1] > maxinv:
            maxinv = int(inv6[-1])
    out["max_largest_invariant_factor_exact_recheck"] = maxinv
    print(json.dumps(out, indent=1))
    with open("bases5_report.json", "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
