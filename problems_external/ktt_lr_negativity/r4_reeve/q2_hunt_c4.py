#!/usr/bin/env python3
"""
q2_hunt_c4.py -- stress-test the campaign pattern  "h*_1 = 0  ==>  V = 1"  at r = 4.

h*_1 = 0  <=>  c = L(1) = dim+1 = 4  <=>  Q is a 3-dim polytope with exactly 4
lattice points.  If Q is a lattice polytope this forces Q = an EMPTY lattice
3-simplex, i.e. exactly White's T(p,q) family, whose normalized volume V = q is
unbounded -- the Reeve mechanism.  So the search reduces to:

    find an r=4 hive polytope that is a 3-SIMPLEX (4 vertices) with V >= 2,
    then test whether it is empty (c == 4).

Two-stage cheap filter (no lattice counting until the last step):
    stage 1: vertices  -> n_vertices == 4 and dim == 3       (exact Cramer)
    stage 2: normalized volume V >= 2                        (exact determinant)
    stage 3: c = L(1)                                        (exact enumeration)

Also records, over EVERY dim-3 polytope met, the necessary-screen margin
    V - 3c   ( a_1 < 0  requires  V > 3(c+i) >= 3c ),
and the exact 6a_1 = 3(c+i) - V.

All arithmetic exact.  Absence of a hit proves nothing.
"""

import json
import os
import random
import sys
import time
from fractions import Fraction
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402


def rand_partition(rng, k, maxpart):
    p = sorted((rng.randint(0, maxpart) for _ in range(k)), reverse=True)
    while p and p[-1] == 0:
        p.pop()
    return tuple(p)


def _work(args):
    seed, ntrial, maxpart = args
    rng = random.Random(seed)
    simplex_vol = Counter()      # V among 4-vertex dim-3 polytopes
    vhist = Counter()            # n_vertices histogram among dim-3
    hits = []                    # simplices with V>=2  (c reported)
    c4 = Counter()               # V distribution among c==4
    best_margin = None           # max (V - 3c)
    best_6a1 = None
    dim3 = 0
    nonlattice = []
    for _ in range(ntrial):
        # build a valid triple: pick lam, mu then nu >= a valid LR shape
        lam = rand_partition(rng, 4, maxpart)
        mu = rand_partition(rng, 4, maxpart)
        N = sum(lam) + sum(mu)
        if N == 0:
            continue
        nu = rand_partition(rng, 4, maxpart * 2)
        if sum(nu) != N:
            # repair nu to have the right weight, keeping 4 parts, weakly decr.
            nu = list(nu) + [0] * (4 - len(nu))
            d = N - sum(nu)
            if d > 0:
                nu[0] += d
            else:
                # subtract from the tail
                k = 3
                while d < 0 and k >= 0:
                    take = min(-d, nu[k] - (nu[k + 1] if k < 3 else 0))
                    nu[k] -= take
                    d += take
                    k -= 1
                if d != 0:
                    continue
            nu = tuple(x for x in nu if x > 0)
            if list(nu) != sorted(nu, reverse=True):
                continue
        H = hive4.build_hive4(lam, mu, nu)
        if not H["ok"]:
            continue
        A, b = H["A"], H["b"]
        V = hive4.vertices(A, b)
        if not V:
            continue
        if hive4._affine_rank(V) != 3:
            continue
        dim3 += 1
        vhist[len(V)] += 1
        dens = hive4.denominators(V)
        if max(dens) != 1:
            nonlattice.append([list(lam), list(mu), list(nu), max(dens)])
        Vol = int(hive4.normalized_volume(A, b, V))
        box = hive4.bounding_box(V)
        c = hive4.lattice_count(A, b, 1, box)
        if len(V) == 4:
            simplex_vol[(Vol, c)] += 1
        if c == 4:
            c4[Vol] += 1
        if len(V) == 4 and Vol >= 2:
            hits.append([list(lam), list(mu), list(nu), Vol, c,
                         "PATTERN_BREAK" if c == 4 else "c>4"])
        m = Vol - 3 * c
        if best_margin is None or m > best_margin[0]:
            best_margin = (m, [list(lam), list(mu), list(nu), c, Vol])
        # exact 6a1 via interior count = h*_3
        L = [1] + [hive4.lattice_count(A, b, n, box) for n in range(1, 4)]
        P = hive4.interpolate(L)
        s6 = 6 * P[1]
        if best_6a1 is None or s6 < best_6a1[0]:
            best_6a1 = (s6, [list(lam), list(mu), list(nu), c, Vol])
    return (dim3, vhist, simplex_vol, c4, hits, best_margin, best_6a1, nonlattice)


def main(total=400000, maxpart=25, procs=58, seed0=20260721):
    t0 = time.time()
    per = max(1, total // (procs * 8))
    jobs = [(seed0 + i, per, maxpart) for i in range(procs * 8)]
    dim3 = 0
    vhist = Counter(); simplex_vol = Counter(); c4 = Counter()
    hits = []; nonlattice = []
    bm = None; b6 = None
    with Pool(procs) as pool:
        for d, vh, sv, c4c, h, m, s, nl in pool.imap_unordered(_work, jobs):
            dim3 += d
            vhist.update(vh); simplex_vol.update(sv); c4.update(c4c)
            hits.extend(h); nonlattice.extend(nl)
            if m and (bm is None or m[0] > bm[0]):
                bm = m
            if s and (b6 is None or s[0] < b6[0]):
                b6 = s
    dt = time.time() - t0
    print(f"maxpart={maxpart}  samples~{per*len(jobs)}  dim-3 found: {dim3}  ({dt:.0f}s)")
    print("n_vertices histogram (dim-3):", dict(sorted(vhist.items())))
    print("(V,c) distribution among 4-vertex simplices:", dict(sorted(simplex_vol.items())))
    print("V distribution among c==4 polytopes    :", dict(sorted(c4.items())))
    print("4-vertex simplices with V>=2 :", len(hits), " of which c==4 (PATTERN BREAK):", sum(1 for x in hits if x[5]=="PATTERN_BREAK"))
    for h in hits[:50]:
        print("   BREAK", h)
    print("max (V - 3c) [need > 0 even to be a candidate]:", bm)
    print("min 6a1 = 3(c+i)-V  [need < 0]:", b6)
    print("non-lattice Q found:", len(nonlattice), nonlattice[:5])
    out = {"maxpart": maxpart, "samples": per * len(jobs), "seconds": dt,
           "dim3": dim3, "nvert_hist": {str(k): v for k, v in sorted(vhist.items())},
           "simplex_Vc": {str(k): v for k, v in sorted(simplex_vol.items())},
           "c4_vol": {str(k): v for k, v in sorted(c4.items())},
           "pattern_breaks": hits,
           "max_V_minus_3c": [bm[0], bm[1]] if bm else None,
           "min_6a1": [b6[0], b6[1]] if b6 else None,
           "nonlattice": nonlattice[:50]}
    with open(os.path.join(HERE, f"q2_hunt_c4_{maxpart}.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 400000
    maxpart = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    sys.exit(main(total, maxpart))
