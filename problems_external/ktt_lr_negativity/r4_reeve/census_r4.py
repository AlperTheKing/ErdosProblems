#!/usr/bin/env python3
"""
census_r4.py -- exhaustive census of the r = 4 cell.

For every N <= NMAX enumerates EVERY triple (lam, mu, nu) with
  nu  a partition of N with exactly 4 positive parts,
  lam, mu partitions with at most 4 parts, |lam| + |mu| = N,
(using the symmetry c(nu;lam,mu) = c(nu;mu,lam) to halve the work), runs the
exact hive4 analysis, and records:
  * the dim histogram
  * the extremal a_1 coefficient (the ONLY coefficient that can go negative:
    a_3 = vol > 0, a_0 = 1, and a_2 = 1 + (h*_1 - h*_3)/2 >= 0 whenever
    h*_3 <= h*_1, so a_1 is the Reeve-type coefficient)
  * every triple with a strictly negative coefficient (the KTT counterexample)
  * every triple with a non-integral vertex (max denominator > 1)
  * the record h*_2 (Reeve-likeness: for a 3-dim lattice polytope
    6*a_1 = 11 + 2 h*_1 - h*_2 + 2 h*_3, so negativity needs a big h*_2)

Absence of a negative coefficient here proves NOTHING about the KTT conjecture
in general and is not evidence for it; it only closes the enumerated window.
"""

import json
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hive4  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def parts_le(N, k):
    """All partitions of N into at most k positive parts (as tuples, desc)."""
    out = []

    def rec(rem, mx, cur):
        if rem == 0:
            out.append(tuple(cur))
            return
        if len(cur) == k:
            return
        for v in range(min(rem, mx), 0, -1):
            cur.append(v)
            rec(rem - v, v, cur)
            cur.pop()

    rec(N, N, [])
    return out


def parts_exact(N, k):
    return [p for p in parts_le(N, k) if len(p) == k]


def main(nmax=20, nmin=4, budget=None):
    t0 = time.time()
    dimhist = {}
    negs = []
    nonint = []
    best_a1 = None       # smallest a_1 seen (Fraction) with its triple
    best_h2 = (0, None)  # largest h*_2 seen
    total = 0
    audit_fail = []
    per_N = []
    cache_le = {}
    for N in range(nmin, nmax + 1):
        tN = time.time()
        nus = parts_exact(N, 4)
        cntN = 0
        for a in range(0, N + 1):
            if a not in cache_le:
                cache_le[a] = parts_le(a, 4)
            if (N - a) not in cache_le:
                cache_le[N - a] = parts_le(N - a, 4)
            for lam in cache_le[a]:
                for mu in cache_le[N - a]:
                    if (len(mu), mu) < (len(lam), lam):
                        continue  # c is symmetric in lam <-> mu
                    for nu in nus:
                        total += 1
                        cntN += 1
                        r = hive4.analyze(list(lam), list(mu), list(nu))
                        d = r["dim"]
                        dimhist[d] = dimhist.get(d, 0) + 1
                        if r["empty"]:
                            continue
                        if not (r["verified"] and r["vol_crosscheck"]
                                and r["deg_eq_dim"]):
                            audit_fail.append((lam, mu, nu))
                        if r.get("max_denominator", 1) > 1:
                            nonint.append((lam, mu, nu, r["max_denominator"]))
                        if r["neg"]:
                            negs.append((lam, mu, nu,
                                         [hive4._fmt_frac(c) for c in r["poly"]]))
                            print("*** NEGATIVE COEFFICIENT ***",
                                  lam, mu, nu,
                                  [hive4._fmt_frac(c) for c in r["poly"]])
                        P = r["poly"]
                        if len(P) > 1:
                            a1 = P[1]
                            if best_a1 is None or a1 < best_a1[0]:
                                best_a1 = (a1, (lam, mu, nu), list(r["hstar"]))
                        h = r["hstar"]
                        if len(h) > 2 and h[2] > best_h2[0]:
                            best_h2 = (h[2], (lam, mu, nu, list(h)))
        per_N.append((N, cntN, round(time.time() - tN, 1)))
        print("N=%-3d triples=%-9d cum=%-10d %.1fs  min a1 so far=%s (h*=%s)"
              % (N, cntN, total, time.time() - tN,
                 hive4._fmt_frac(best_a1[0]) if best_a1 else "-",
                 best_a1[2] if best_a1 else "-"), flush=True)
        if budget and time.time() - t0 > budget:
            print("time budget reached, stopping after N=%d" % N)
            nmax = N
            break

    print("\n=== CENSUS SUMMARY  (4 <= |nu| <= %d, nu with exactly 4 parts) ==="
          % nmax)
    print("triples enumerated (lam<=mu symmetry applied): %d" % total)
    print("dim histogram: %s" % sorted(dimhist.items()))
    print("internal audit failures: %d" % len(audit_fail))
    print("non-lattice hive polytopes (max vertex denominator > 1): %d"
          % len(nonint))
    print("record h*_2: %s at %s" % (best_h2[0], best_h2[1]))
    if best_a1:
        print("minimum linear coefficient a_1 = %s at %s (h* = %s)"
              % (hive4._fmt_frac(best_a1[0]), best_a1[1], best_a1[2]))
    print("TRIPLES WITH A STRICTLY NEGATIVE COEFFICIENT: %d" % len(negs))
    for x in negs[:40]:
        print("   ", x)
    print("elapsed %.1f s" % (time.time() - t0))

    with open(os.path.join(HERE, "census_r4.json"), "w") as f:
        json.dump({"nmin": nmin, "nmax": nmax, "total": total,
                   "dim_histogram": {str(k): v for k, v in sorted(dimhist.items())},
                   "audit_failures": len(audit_fail),
                   "non_lattice": nonint[:200], "n_non_lattice": len(nonint),
                   "record_hstar2": [best_h2[0], best_h2[1]],
                   "min_a1": [hive4._fmt_frac(best_a1[0]), best_a1[1], best_a1[2]]
                   if best_a1 else None,
                   "negatives": negs, "per_N": per_N,
                   "elapsed_s": round(time.time() - t0, 1)}, f, indent=1, default=str)
    return 0


if __name__ == "__main__":
    nm = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    bud = float(sys.argv[2]) if len(sys.argv) > 2 else None
    sys.exit(main(nm, budget=bud))
