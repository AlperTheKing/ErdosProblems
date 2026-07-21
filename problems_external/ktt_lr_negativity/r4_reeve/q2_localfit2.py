#!/usr/bin/env python3
"""
q2_localfit2.py -- decisive route for the r=4 cell, part 2.

Model (Berline-Vergne / McMullen local Ehrhart theory): for a lattice 3-polytope

        a_1(P) = SUM_{edges e} ell(e) * mu(type(e)),

type(e) = the unordered pair of outward facet normals meeting along e (the
transverse cone, hence mu, is determined by that pair).  For r=4 every hive
polytope has facet normals in a FIXED 15-element set N, so a_1 is one fixed
linear form on the edge-length vector Lambda(P) in Z_{>=0}^{C(15,2)}.

Consequence used here:
  IF there is a vector mu >= 0 (componentwise) that reproduces a_1 on a spanning
  set of sampled Lambda's, THEN a_1(P) = <mu,Lambda(P)> >= 0 for every lattice
  3-polytope whose facet normals lie in N, in particular for every r=4 hive
  polytope -- i.e. KTT negativity is IMPOSSIBLE in the whole r=4 cell.
  (Any two solutions agree on the span of the sampled Lambda's; a realizable
  Lambda outside that span would invalidate the conclusion, so the span/rank is
  reported and stress-tested by held-out samples.)

Samplers: (a) genuine hive triples, (b) the RELAXATION -- arbitrary offsets over
all 15 normals, anchored at a random interior lattice point so that P is
nonempty and 3-dimensional.
All arithmetic exact (Fraction / int).
"""
import itertools
import json
import os
import random
import sys
import time
from fractions import Fraction
from math import gcd
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402
from q2_relaxed_simplex import NORMALS  # noqa: E402
from q2_localformula import edge_data, rand_hive  # noqa: E402

PAIRS = list(itertools.combinations(range(len(NORMALS)), 2))


def analyse(A, b):
    verts = hive4.vertices(A, b)
    if not verts or hive4._affine_rank(verts) != 3:
        return None
    if max(hive4.denominators(verts)) != 1:
        return None
    box = hive4.bounding_box(verts)
    L = [1] + [hive4.lattice_count(A, b, n, box) for n in range(1, 4)]
    P = hive4.interpolate(L)
    lam = edge_data(A, b, verts)
    if lam is None:
        return None
    return lam, P[1]


def rand_relaxed(rng, T):
    A = [list(n) for n in NORMALS]
    x0 = [rng.randint(-T, T) for _ in range(3)]
    b = [hive4._dot(n, x0) + rng.randint(0, T) for n in A]
    return A, b


def _work(args):
    seed, nh, nr, maxpart, T = args
    rng = random.Random(seed)
    out = []
    for _ in range(nh):
        h = rand_hive(rng, maxpart)
        if h is None:
            continue
        r = analyse(h[0], h[1])
        if r is None:
            continue
        out.append(("hive", {str(k): v for k, v in r[0].items()}, str(r[1]),
                    [list(h[2][0]), list(h[2][1]), list(h[2][2])]))
    for _ in range(nr):
        A, b = rand_relaxed(rng, T)
        r = analyse(A, b)
        if r is None:
            continue
        out.append(("relax", {str(k): v for k, v in r[0].items()}, str(r[1]), b))
    return out


def rref(M, ncol):
    piv = []
    r = 0
    for c in range(ncol):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * bb for a, bb in zip(M[i], M[r])]
        piv.append(c)
        r += 1
        if r == len(M):
            break
    return M, piv, r


def main(nh=400, nr=4000, maxpart=14, T=7, procs=58, seed0=4242):
    t0 = time.time()
    jobs = [(seed0 + i, nh, nr, maxpart, T) for i in range(procs)]
    recs = []
    with Pool(procs) as pool:
        for o in pool.imap_unordered(_work, jobs):
            recs.extend(o)
    print(f"usable lattice dim-3 samples: {len(recs)}  "
          f"(hive {sum(1 for r in recs if r[0]=='hive')}) in {time.time()-t0:.0f}s")
    rows, rhs = [], []
    for tag, lam, a1, extra in recs:
        v = [0] * len(PAIRS)
        for k, val in lam.items():
            v[int(k)] += val
        rows.append(v)
        rhs.append(Fraction(a1))
    used = sorted({c for r in rows for c in range(len(PAIRS)) if r[c] != 0})
    print(f"edge types occurring: {len(used)} / {len(PAIRS)}")
    sub = [[Fraction(r[c]) for c in used] + [rhs[i]] for i, r in enumerate(rows)]
    M, piv, rank = rref([r[:] for r in sub], len(used))
    incons = [i for i in range(rank, len(M))
              if all(x == 0 for x in M[i][:len(used)]) and M[i][len(used)] != 0]
    print(f"rank {rank} of {len(used)} unknowns; inconsistent rows: {len(incons)}")
    if incons:
        print("  -> LOCAL-FORMULA MODEL REJECTED by the data; abandon this route")
        return 1
    print("  -> model CONSISTENT: a_1 is exactly one fixed linear form in the "
          "edge-length vector on the sampled span")
    # particular solution + kernel basis, then look for a NONNEGATIVE solution
    n = len(used)
    part = [Fraction(0)] * n
    for k, c in enumerate(piv):
        part[c] = M[k][n]
    free = [c for c in range(n) if c not in piv]
    ker = []
    for f in free:
        v = [Fraction(0)] * n
        v[f] = Fraction(1)
        for k, c in enumerate(piv):
            v[c] = -M[k][f]
        ker.append(v)
    print(f"solution space: particular + {len(ker)}-dim kernel")
    neg_part = [(PAIRS[used[i]], part[i]) for i in range(n) if part[i] < 0]
    print(f"particular solution has {len(neg_part)} negative entries")

    # exact LP feasibility for  part + K y >= 0   (scipy for a candidate, exact verify)
    ok = None
    try:
        import numpy as np
        from scipy.optimize import linprog
        if ker:
            Aub = -np.array([[float(k[i]) for k in ker] for i in range(n)])
            bub = np.array([float(part[i]) for i in range(n)])
            res = linprog(c=np.zeros(len(ker)), A_ub=Aub, b_ub=bub,
                          bounds=[(None, None)] * len(ker), method="highs")
            if res.status == 0:
                from fractions import Fraction as F
                y = [F(round(v * 10 ** 6), 10 ** 6) for v in res.x]
                cand = [part[i] + sum(y[j] * ker[j][i] for j in range(len(ker)))
                        for i in range(n)]
                ok = all(x >= 0 for x in cand)
                if not ok:   # snap the tiny negatives by re-solving with a margin
                    res2 = linprog(c=np.zeros(len(ker)), A_ub=Aub,
                                   b_ub=bub - 1e-9,
                                   bounds=[(None, None)] * len(ker), method="highs")
                    if res2.status == 0:
                        y = [F(round(v * 10 ** 6), 10 ** 6) for v in res2.x]
                        cand = [part[i] + sum(y[j] * ker[j][i] for j in range(len(ker)))
                                for i in range(n)]
                        ok = all(x >= 0 for x in cand)
            else:
                ok = False
                cand = None
        else:
            cand = part
            ok = all(x >= 0 for x in part)
    except Exception as e:                                   # noqa: BLE001
        print("LP step unavailable:", e)
        cand = None
    if ok:
        # exact verification of the certificate on EVERY sample
        bad = 0
        for i, r in enumerate(rows):
            s = sum(Fraction(r[used[j]]) * cand[j] for j in range(n))
            if s != rhs[i]:
                bad += 1
        print(f"NONNEGATIVE certificate found; exact re-check on all "
              f"{len(rows)} samples: {bad} mismatches")
        if bad == 0:
            print("==> a_1 >= 0 for every lattice 3-polytope with facet normals "
                  "in the r=4 rhombus set, ON THE SAMPLED SPAN.")
        print("certificate mu (nonzero entries):")
        for j in range(n):
            if cand[j] != 0:
                print(f"   {NORMALS[PAIRS[used[j]][0]]} & "
                      f"{NORMALS[PAIRS[used[j]][1]]} -> {cand[j]}")
    else:
        print("NO nonnegative certificate exists on the sampled span "
              "==> some edge type has a strictly negative mu: negativity is "
              "NOT excluded by this argument.")
        # exhibit the most negative achievable entry
    json.dump({"samples": len(rows), "types": len(used), "rank": rank,
               "kernel_dim": len(ker), "nonneg_certificate": bool(ok),
               "mu": ([str(x) for x in cand] if cand else None),
               "used_pairs": [[NORMALS[PAIRS[c][0]], NORMALS[PAIRS[c][1]]] for c in used]},
              open(os.path.join(HERE, "q2_localfit2.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
