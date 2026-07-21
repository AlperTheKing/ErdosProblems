#!/usr/bin/env python3
"""
q2_mu_determined.py -- which edge-type coefficients mu are FORCED by the data,
and what are their exact signs?

a_1(P) = <mu, Lambda(P)> (Berline-Vergne local formula; the fit's consistency is
itself the test of this model).  mu_j is uniquely determined by a sample set iff
the unit covector e_j lies in the ROW SPACE of the sampled Lambda-matrix.  For
those j the exact rational value of mu_j is unambiguous.

A determined mu_j < 0 means: growing edges of that type drives a_1 DOWN without
bound, i.e. the Reeve/negativity mechanism is ALIVE in the r=4 normal set, and
the only remaining question is whether hive right-hand sides can realise it.
Exact arithmetic throughout.
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402
from q2_relaxed_simplex import NORMALS  # noqa: E402
from q2_localfit2 import _work, PAIRS  # noqa: E402


def rref(M, ncol):
    piv, r = [], 0
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
    return M[:r], piv


def main(nh=200, nr=500, maxpart=12, T=4, procs=48, seed0=31337):
    jobs = [(seed0 + i, nh, nr, maxpart, T) for i in range(procs)]
    recs = []
    with Pool(procs) as pool:
        for o in pool.imap_unordered(_work, jobs):
            recs.extend(o)
    hive_pairs = set()
    rows, rhs = [], []
    for tag, lam, a1, extra in recs:
        v = [0] * len(PAIRS)
        for k, val in lam.items():
            v[int(k)] += val
            if tag == "hive":
                hive_pairs.add(int(k))
        rows.append(v)
        rhs.append(Fraction(a1))
    print(f"samples {len(rows)} (hive {sum(1 for r in recs if r[0]=='hive')})")
    used = sorted({c for r in rows for c in range(len(PAIRS)) if r[c] != 0})
    n = len(used)
    aug = [[Fraction(r[c]) for c in used] + [rhs[i]] for i, r in enumerate(rows)]
    R, piv = rref([r[:] for r in aug], n)
    print(f"types used {n}, rank {len(piv)}")
    incons = [r for r in R if all(x == 0 for x in r[:n]) and r[n] != 0]
    print("inconsistent rows (model rejected if > 0):", len(incons))
    if incons:
        return 1
    # row space basis of the Lambda-part
    B, bpiv = rref([[Fraction(r[c]) for c in used] for r in rows], n)
    # e_j in rowspace?  reduce e_j against B (which is in RREF)
    part = [Fraction(0)] * n
    for k, c in enumerate(piv):
        part[c] = R[k][n]
    determined, undet = {}, []
    for j in range(n):
        v = [Fraction(0)] * n
        v[j] = Fraction(1)
        for k, c in enumerate(bpiv):
            if v[c] != 0:
                f = v[c]
                v = [a - f * b for a, b in zip(v, B[k])]
        if all(x == 0 for x in v):
            determined[used[j]] = part[j]
        else:
            undet.append(used[j])
    print(f"mu determined for {len(determined)} of {n} edge types "
          f"({len(undet)} undetermined)")
    negs = {c: v for c, v in determined.items() if v < 0}
    print(f"DETERMINED NEGATIVE mu: {len(negs)}")
    for c, v in sorted(negs.items(), key=lambda kv: kv[1]):
        i1, i2 = PAIRS[c]
        print(f"   mu = {v}   normals {NORMALS[i1]} & {NORMALS[i2]}"
              f"   {'*** OCCURS IN GENUINE HIVE POLYTOPES ***' if c in hive_pairs else '(relaxed-only so far)'}")
    print("\ndetermined nonnegative mu (sample):")
    for c, v in sorted(determined.items(), key=lambda kv: kv[1])[-8:]:
        i1, i2 = PAIRS[c]
        print(f"   mu = {v}   {NORMALS[i1]} & {NORMALS[i2]}")
    json.dump({"samples": len(rows), "types": n, "rank": len(piv),
               "determined": {str([NORMALS[PAIRS[c][0]], NORMALS[PAIRS[c][1]]]): str(v)
                              for c, v in determined.items()},
               "negative": {str([NORMALS[PAIRS[c][0]], NORMALS[PAIRS[c][1]]]): str(v)
                            for c, v in negs.items()},
               "negative_in_hive": [str([NORMALS[PAIRS[c][0]], NORMALS[PAIRS[c][1]]])
                                    for c in negs if c in hive_pairs],
               "undetermined": len(undet)},
              open(os.path.join(HERE, "q2_mu_determined.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
