#!/usr/bin/env python3
"""
q2_relaxed_simplex.py -- RELAXATION of the r=4 c=4 stratum.

For r=4 the rhombus matrix A is FIXED (18 rows, 15 distinct normals, entries in
{0,+-1}); only b moves with (lam,mu,nu).  Hence EVERY r=4 hive polytope is a
3-polytope whose facet normals lie in the fixed 15-element set N.

A 3-dim LATTICE polytope with c = L(1) = 4 has its 4 lattice points as its
vertices, so it is an EMPTY lattice 3-simplex; by White's theorem it is
lattice-equivalent to some T(p,q) of normalized volume q, and a_1 < 0 iff q >= 13.
So the whole Reeve mechanism inside the r=4 cell lives on:

    is there a SIMPLEX with all 4 facet normals in N, c = 4 and V >= 2 ?

Structure used: 4 normals n_1..n_4 that positively span R^3 determine the simplex
{<n_j,x> <= t_j} up to HOMOTHETY and TRANSLATION, so for each 4-subset the family
is one-parameter modulo Z^3-translation.  We enumerate the offsets t over a box
(which covers all translation classes of the small members) exhaustively.

This is a RELAXATION: b need not come from any (lam,mu,nu).  A clean negative
result here is therefore stronger than a hive census -- but it is still only a
closed window, never evidence for the KTT conjecture.
All arithmetic exact.
"""

import itertools
import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402


def hive_normals():
    H = hive4.build_hive4((3, 2, 1), (3, 2, 1), (5, 4, 2, 1))
    seen = []
    for r in H["A"]:
        if r not in seen:
            seen.append(r)
    return seen


NORMALS = hive_normals()


def _job(args):
    idxs, T = args
    S = [NORMALS[i] for i in idxs]
    # bounded <=> the 4 normals positively span R^3
    if hive4._rank(S) < 3:
        return None
    # need a strictly positive relation sum c_j n_j = 0
    rel = None
    for j in range(4):
        rest = [S[k] for k in range(4) if k != j]
        if hive4._det3(rest) == 0:
            continue
        # solve  rest^T * y = -S[j]  ->  y_k coefficients
        M = [[rest[0][a], rest[1][a], rest[2][a]] for a in range(3)]
        d = hive4._det3(M)
        if d == 0:
            continue
        rhs = [-S[j][a] for a in range(3)]
        y = hive4._solve3(M, rhs)
        if y is None:
            continue
        if all(v > 0 for v in y):
            rel = True
        break
    if not rel:
        return None
    found = defaultdict(set)      # (V,c) seen
    breaks = []
    rng = range(-T, T + 1)
    for t in itertools.product(rng, repeat=4):
        A = list(S)
        b = list(t)
        Vs = hive4.vertices(A, b)
        if len(Vs) != 4:
            continue
        if hive4._affine_rank(Vs) != 3:
            continue
        den = max(hive4.denominators(Vs))
        Vol = int(hive4.normalized_volume(A, b, Vs))
        box = hive4.bounding_box(Vs)
        c = hive4.lattice_count(A, b, 1, box)
        found[(Vol, c, den)].add(1)
        if c == 4 and Vol >= 2:
            breaks.append([list(idxs), list(t), Vol, c, den,
                           [[str(x) for x in v] for v in Vs]])
    return (tuple(idxs), sorted(found.keys()), breaks)


def main(T=4, procs=58):
    jobs = [(idxs, T) for idxs in itertools.combinations(range(len(NORMALS)), 4)]
    print(f"distinct hive normals: {len(NORMALS)} -> {len(jobs)} 4-subsets, offsets in [-{T},{T}]^4")
    allbreaks = []
    bounded = 0
    Vcs = set()
    dens = set()
    with Pool(procs) as pool:
        for res in pool.imap_unordered(_job, jobs, chunksize=4):
            if res is None:
                continue
            bounded += 1
            idxs, pairs, breaks = res
            for (V, c, d) in pairs:
                Vcs.add((V, c, d))
                dens.add(d)
            allbreaks.extend(breaks)
    print(f"bounded (positively spanning) 4-subsets: {bounded}")
    print(f"distinct (V, c, maxdenominator) triples realised: {len(Vcs)}")
    lat = sorted((V, c) for (V, c, d) in Vcs if d == 1)
    print(f"  lattice simplices (denominator 1): {sorted(set(lat))}")
    nonlat = sorted((V, c, d) for (V, c, d) in Vcs if d != 1)
    print(f"  non-lattice simplices: {nonlat[:30]}  (count {len(nonlat)})")
    print(f"c == 4 and V >= 2  (PATTERN BREAK / Reeve mechanism alive): {len(allbreaks)}")
    for bk in allbreaks[:30]:
        print("   BREAK", bk)
    out = {"T": T, "n_normals": len(NORMALS), "normals": NORMALS,
           "bounded_subsets": bounded,
           "lattice_Vc": sorted(set(lat)),
           "nonlattice_Vcd": nonlat,
           "breaks": allbreaks[:200], "n_breaks": len(allbreaks)}
    with open(os.path.join(HERE, f"q2_relaxed_simplex_T{T}.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    T = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    sys.exit(main(T))
