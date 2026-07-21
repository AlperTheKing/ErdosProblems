#!/usr/bin/env python3
"""
band3_census.py -- EXHAUSTIVE r=4 hive-polytope Ehrhart census for a weight band.

Band 3 of the Reeve-dimension sweep: W = |nu| in [21, 26], fully exhaustive.

For every N in the band it enumerates EVERY triple (lam, mu, nu) with
    nu   a partition of N with EXACTLY 4 positive parts,
    lam, mu partitions with at most 4 parts, |lam| + |mu| = N,
modulo the exact symmetry c(nu; lam, mu) = c(nu; mu, lam) (each unordered pair
{lam, mu} is enumerated once).  nu with <= 3 positive parts is excluded because
c(nu; lam, mu) != 0 forces lam, mu subseteq nu, so such a triple is an r<=3
triple whose hive polytope has dim <= 1 and whose P is linear -- no dim-3
Reeve behaviour is possible there.

Every triple is run through the exact engine hive4.analyze (Fractions/ints
only; no floating point anywhere).  Recorded per band:
  (i)   global min over all P of every coefficient, and of a_1 specifically
  (ii)  max normalized volume V = 3! vol(Q)
  (iii) max V restricted to h*_1 = 0  (i.e. c = dim + 1: the "empty-simplex"
        stratum where Reeve tetrahedra live)
  (iv)  EVERY triple with any strictly negative coefficient of P
plus dim histogram, non-lattice vertices, internal audit failures (Ehrhart
interpolation verified at n=4,5 and volume cross-checked against 6*a_3).

Absence of a negative coefficient proves NOTHING about the KTT conjecture and
must never be reported as support for it; it only closes the enumerated window.
"""

import json
import os
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402


def parts_le(N, k):
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


_NUS = {}
_MUS = {}


def _nus(N):
    if N not in _NUS:
        _NUS[N] = parts_exact(N, 4)
    return _NUS[N]


def _mus(a):
    if a not in _MUS:
        _MUS[a] = parts_le(a, 4)
    return _MUS[a]


def blank():
    return {
        "total": 0,
        "dim": {},
        "min_coeff": None,     # (Fraction, triple, poly, hstar)
        "min_a1": None,        # (Fraction, triple, hstar)
        "max_V": None,         # (Fraction, triple, hstar, c)
        "max_V_h1z": None,     # (Fraction, triple, hstar, c)
        "max_h2": None,        # (int, triple, hstar)
        "negatives": [],
        "audit_fail": [],
        "nonlattice": [],
        "max_c": None,
        "min_a1_dim3": None,   # (Fraction, triple, hstar)
        "max_margin": None,    # (int, triple, hstar): h*_2 - 2h*_1 - 2h*_3 ; a_1<0 iff > 11
    }


def merge(acc, r):
    acc["total"] += r["total"]
    for k, v in r["dim"].items():
        acc["dim"][k] = acc["dim"].get(k, 0) + v
    for key, better in (("min_coeff", lambda a, b: a[0] < b[0]),
                        ("min_a1", lambda a, b: a[0] < b[0]),
                        ("max_V", lambda a, b: a[0] > b[0]),
                        ("max_V_h1z", lambda a, b: a[0] > b[0]),
                        ("max_h2", lambda a, b: a[0] > b[0]),
                        ("max_c", lambda a, b: a[0] > b[0]),
                        ("min_a1_dim3", lambda a, b: a[0] < b[0]),
                        ("max_margin", lambda a, b: a[0] > b[0])):
        if r[key] is not None and (acc[key] is None or better(r[key], acc[key])):
            acc[key] = r[key]
    acc["negatives"].extend(r["negatives"])
    acc["audit_fail"].extend(r["audit_fail"])
    acc["nonlattice"].extend(r["nonlattice"])
    return acc


def work(task):
    """task = (N, lam) : all (mu, nu) for this lam."""
    N, lam = task
    a = sum(lam)
    res = blank()
    nus = _nus(N)
    for mu in _mus(N - a):
        if (len(mu), mu) < (len(lam), lam):
            continue  # c symmetric in lam <-> mu; keep one representative
        for nu in nus:
            res["total"] += 1
            r = hive4.analyze(list(lam), list(mu), list(nu))
            d = r["dim"]
            res["dim"][d] = res["dim"].get(d, 0) + 1
            if r["empty"]:
                continue
            trip = (lam, mu, nu)
            if not (r["verified"] and r["vol_crosscheck"] and r["deg_eq_dim"]):
                res["audit_fail"].append([trip, r["verify_detail"]])
            if r.get("max_denominator", 1) > 1:
                res["nonlattice"].append([trip, r["max_denominator"]])
            P = r["poly"]
            h = list(r["hstar"])
            if r["neg"]:
                res["negatives"].append([trip, [hive4._fmt_frac(c) for c in P],
                                         h, r["L"], str(r["volume_normalized"])])
            mc = min(P)
            if res["min_coeff"] is None or mc < res["min_coeff"][0]:
                res["min_coeff"] = (mc, trip, [hive4._fmt_frac(c) for c in P], h)
            if len(P) > 1:
                if res["min_a1"] is None or P[1] < res["min_a1"][0]:
                    res["min_a1"] = (P[1], trip, h)
            V = r["volume_normalized"]
            if res["max_V"] is None or V > res["max_V"][0]:
                res["max_V"] = (V, trip, h, r["c"])
            if len(h) > 1 and h[1] == 0:
                if res["max_V_h1z"] is None or V > res["max_V_h1z"][0]:
                    res["max_V_h1z"] = (V, trip, h, r["c"])
            if len(h) > 2:
                if res["max_h2"] is None or h[2] > res["max_h2"][0]:
                    res["max_h2"] = (h[2], trip, h)
            if res["max_c"] is None or r["c"] > res["max_c"][0]:
                res["max_c"] = (r["c"], trip, h)
            if d == 3:
                # for a 3-dim lattice polytope: 6*a_1 = 11 + 2h*_1 - h*_2 + 2h*_3,
                # so a_1 < 0  <=>  margin := h*_2 - 2h*_1 - 2h*_3 > 11.
                margin = h[2] - 2 * h[1] - 2 * h[3]
                if res["max_margin"] is None or margin > res["max_margin"][0]:
                    res["max_margin"] = (margin, trip, h)
                if res["min_a1_dim3"] is None or P[1] < res["min_a1_dim3"][0]:
                    res["min_a1_dim3"] = (P[1], trip, h)
    return res


def fmt(x):
    if x is None:
        return None
    return hive4._fmt_frac(x)


def jsonify(entry):
    if entry is None:
        return None
    out = []
    for x in entry:
        if isinstance(x, Fraction):
            out.append(hive4._fmt_frac(x))
        elif isinstance(x, tuple) and len(x) == 3 and all(isinstance(y, tuple) for y in x):
            out.append([list(y) for y in x])
        else:
            out.append(x)
    return out


def main():
    nmin = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 26
    nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    outdir = os.path.join(HERE, "runs", "band3")
    os.makedirs(outdir, exist_ok=True)

    t0 = time.time()
    acc = blank()
    per_N = []
    pool = Pool(nproc)
    for N in range(nmin, nmax + 1):
        tN = time.time()
        tasks = []
        for a in range(0, N + 1):
            for lam in parts_le(a, 4):
                tasks.append((N, lam))
        # parts_le(0,4) == [()], so lam = () (the empty partition) is included
        seen = set()
        ded = []
        for t in tasks:
            if t in seen:
                continue
            seen.add(t)
            ded.append(t)
        tasks = ded
        accN = blank()
        for r in pool.imap_unordered(work, tasks, chunksize=2):
            merge(accN, r)
        merge(acc, accN)
        per_N.append({"N": N, "triples": accN["total"],
                      "seconds": round(time.time() - tN, 1),
                      "dim": {str(k): v for k, v in sorted(accN["dim"].items())},
                      "min_a1": fmt(accN["min_a1"][0]) if accN["min_a1"] else None,
                      "max_V": fmt(accN["max_V"][0]) if accN["max_V"] else None,
                      "max_V_hstar1_zero": fmt(accN["max_V_h1z"][0]) if accN["max_V_h1z"] else None,
                      "negatives": len(accN["negatives"])})
        print("N=%-3d triples=%-10d cum=%-11d %.1fs  min a1=%-8s maxV=%-6s maxV(h*1=0)=%-6s NEG=%d"
              % (N, accN["total"], acc["total"], time.time() - tN,
                 fmt(accN["min_a1"][0]) if accN["min_a1"] else "-",
                 fmt(accN["max_V"][0]) if accN["max_V"] else "-",
                 fmt(accN["max_V_h1z"][0]) if accN["max_V_h1z"] else "-",
                 len(accN["negatives"])), flush=True)

    pool.close()
    pool.join()
    elapsed = round(time.time() - t0, 1)
    man = {
        "band": "W=|nu| in [%d,%d]" % (nmin, nmax),
        "exhaustive": True,
        "enumeration": ("all (lam,mu,nu): nu partition of N with exactly 4 parts; "
                        "lam,mu partitions with at most 4 parts, |lam|+|mu|=N; "
                        "unordered {lam,mu} counted once (c symmetric)"),
        "engine": "hive4.py exact (Fraction/int only), Ehrhart interpolated from L(0..3), "
                  "verified at n=4 and n=5, volume cross-checked as 6*a_3",
        "triples_tested": acc["total"],
        "dim_histogram": {str(k): v for k, v in sorted(acc["dim"].items())},
        "audit_failures": len(acc["audit_fail"]),
        "audit_failure_detail": acc["audit_fail"][:20],
        "non_lattice_polytopes": len(acc["nonlattice"]),
        "non_lattice_detail": acc["nonlattice"][:20],
        "min_coefficient_over_band": jsonify(acc["min_coeff"]),
        "min_a1": jsonify(acc["min_a1"]),
        "max_volume": jsonify(acc["max_V"]),
        "max_volume_at_hstar1_zero": jsonify(acc["max_V_h1z"]),
        "max_hstar2": jsonify(acc["max_h2"]),
        "max_c": jsonify(acc["max_c"]),
        "min_a1_dim3": jsonify(acc["min_a1_dim3"]),
        "max_negativity_margin_dim3": jsonify(acc["max_margin"]),
        "margin_identity": "for dim Q = 3: 6*a_1 = 11 + 2h*_1 - h*_2 + 2h*_3; a_1 < 0 iff h*_2 - 2h*_1 - 2h*_3 > 11",
        "negatives": acc["negatives"],
        "n_negatives": len(acc["negatives"]),
        "per_N": per_N,
        "elapsed_s": elapsed,
        "caveat": ("An empty census proves nothing about the KTT conjecture and is "
                   "not evidence for it; it only closes this enumerated window."),
    }
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1, default=str)
    print("\n=== BAND 3 SUMMARY (exhaustive, W in [%d,%d]) ===" % (nmin, nmax))
    print("triples tested: %d" % acc["total"])
    print("dim histogram: %s" % sorted(acc["dim"].items()))
    print("audit failures: %d ; non-lattice: %d" % (len(acc["audit_fail"]), len(acc["nonlattice"])))
    print("min coefficient: %s at %s poly=%s h*=%s" % tuple(jsonify(acc["min_coeff"]) or [None]*4))
    print("min a_1: %s at %s h*=%s" % tuple(jsonify(acc["min_a1"]) or [None]*3))
    print("max V: %s at %s h*=%s c=%s" % tuple(jsonify(acc["max_V"]) or [None]*4))
    print("max V (h*_1=0): %s at %s h*=%s c=%s" % tuple(jsonify(acc["max_V_h1z"]) or [None]*4))
    print("max h*_2: %s at %s h*=%s" % tuple(jsonify(acc["max_h2"]) or [None]*3))
    print("min a_1 (dim 3 only): %s at %s h*=%s" % tuple(jsonify(acc["min_a1_dim3"]) or [None]*3))
    print("max margin h*_2-2h*_1-2h*_3 (dim 3; need >11 for a_1<0): %s at %s h*=%s"
          % tuple(jsonify(acc["max_margin"]) or [None]*3))
    print("NEGATIVE-COEFFICIENT TRIPLES: %d" % len(acc["negatives"]))
    for x in acc["negatives"][:50]:
        print("   ", x)
    print("elapsed %.1f s -> %s" % (elapsed, os.path.join(outdir, "manifest.json")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
