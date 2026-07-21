#!/usr/bin/env python3
"""
band2_census.py -- EXHAUSTIVE r = 4 census of the weight band |nu| in [WMIN, WMAX].

Enumerates EVERY triple (lam, mu, nu) of partitions with at most 4 parts and
|lam| + |mu| = |nu| = W, for W in [WMIN, WMAX], using ONLY the symmetry
c(nu; lam, mu) = c(nu; mu, lam) (the stretched polynomial is literally the same
object for the two orders), and runs each triple through the exact hive4
Ehrhart engine.  No other filter of any kind is applied: triples with c = 0 are
also run through the engine.

Tracked:
  (i)   global minimum coefficient a_min over all P, and min a_1 specifically
  (ii)  max normalized volume V
  (iii) max V among triples with h*_1 = 0 (c = dim + 1, the "empty simplex"
        stratum where Reeve behaviour lives)
  (iv)  EVERY triple with any strictly negative coefficient

Absence of a negative coefficient proves nothing whatsoever about the KTT
conjecture and must never be reported as support for it.
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


def parts_le(N, k=4):
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


_P = {}


def P4(n):
    if n not in _P:
        _P[n] = parts_le(n, 4)
    return _P[n]


def job(arg):
    """One (W, a) cell: lam runs over partitions of a, mu over partitions of W-a."""
    W, a = arg
    lams = P4(a)
    mus = P4(W - a)
    nus = P4(W)
    total = 0
    dimhist = {}
    negs = []
    audit_fail = []
    nonint = []
    best_a1 = None      # (a1, triple, hstar, dim)
    best_min = None     # (min coeff, triple, hstar, dim)
    best_V = (Fraction(0), None)
    best_V_h1z = (Fraction(0), None)
    best_h2 = (0, None)
    for lam in lams:
        for mu in mus:
            if (len(mu), mu) < (len(lam), lam):
                continue  # lam <-> mu symmetry
            for nu in nus:
                total += 1
                r = hive4.analyze(list(lam), list(mu), list(nu))
                d = r["dim"]
                dimhist[d] = dimhist.get(d, 0) + 1
                if r["empty"]:
                    continue
                if not (r["verified"] and r["vol_crosscheck"] and r["deg_eq_dim"]):
                    audit_fail.append([lam, mu, nu])
                if r.get("max_denominator", 1) > 1:
                    nonint.append([lam, mu, nu, r["max_denominator"]])
                if r["neg"]:
                    negs.append({"lam": list(lam), "mu": list(mu), "nu": list(nu),
                                 "poly": [hive4._fmt_frac(c) for c in r["poly"]],
                                 "hstar": list(r["hstar"]), "dim": d,
                                 "V": str(r["volume_normalized"]),
                                 "L": list(r["L"])})
                Pp = r["poly"]
                mn = min(Pp)
                if best_min is None or mn < best_min[0]:
                    best_min = (mn, (lam, mu, nu), list(r["hstar"]), d)
                if len(Pp) > 1:
                    a1 = Pp[1]
                    if best_a1 is None or a1 < best_a1[0]:
                        best_a1 = (a1, (lam, mu, nu), list(r["hstar"]), d)
                V = r["volume_normalized"]
                h = r["hstar"]
                if V > best_V[0]:
                    best_V = (V, (lam, mu, nu, list(h), d))
                if len(h) > 1 and h[1] == 0 and V > best_V_h1z[0]:
                    best_V_h1z = (V, (lam, mu, nu, list(h), d))
                if len(h) > 2 and h[2] > best_h2[0]:
                    best_h2 = (h[2], (lam, mu, nu, list(h)))
    return {"W": W, "a": a, "total": total, "dimhist": dimhist, "negs": negs,
            "audit_fail": audit_fail, "nonint": nonint,
            "best_a1": (str(best_a1[0]), best_a1[1], best_a1[2], best_a1[3]) if best_a1 else None,
            "best_min": (str(best_min[0]), best_min[1], best_min[2], best_min[3]) if best_min else None,
            "best_V": (str(best_V[0]), best_V[1]),
            "best_V_h1z": (str(best_V_h1z[0]), best_V_h1z[1]),
            "best_h2": best_h2}


def main(wmin=15, wmax=20, workers=48):
    t0 = time.time()
    tasks = [(W, a) for W in range(wmin, wmax + 1) for a in range(0, W + 1)]
    total = 0
    dimhist = {}
    negs = []
    audit_fail = []
    nonint = []
    best_a1 = None
    best_min = None
    best_V = (Fraction(0), None)
    best_V_h1z = (Fraction(0), None)
    best_h2 = (0, None)
    perW = {}
    with Pool(workers) as pool:
        for res in pool.imap_unordered(job, tasks, chunksize=1):
            total += res["total"]
            perW[res["W"]] = perW.get(res["W"], 0) + res["total"]
            for k, v in res["dimhist"].items():
                dimhist[k] = dimhist.get(k, 0) + v
            negs.extend(res["negs"])
            audit_fail.extend(res["audit_fail"])
            nonint.extend(res["nonint"])
            if res["best_a1"]:
                f = Fraction(res["best_a1"][0])
                if best_a1 is None or f < best_a1[0]:
                    best_a1 = (f,) + tuple(res["best_a1"][1:])
            if res["best_min"]:
                f = Fraction(res["best_min"][0])
                if best_min is None or f < best_min[0]:
                    best_min = (f,) + tuple(res["best_min"][1:])
            fV = Fraction(res["best_V"][0])
            if fV > best_V[0]:
                best_V = (fV, res["best_V"][1])
            fVz = Fraction(res["best_V_h1z"][0])
            if fVz > best_V_h1z[0]:
                best_V_h1z = (fVz, res["best_V_h1z"][1])
            if res["best_h2"][0] > best_h2[0]:
                best_h2 = tuple(res["best_h2"])
            if negs:
                for n in res["negs"]:
                    print("*** NEGATIVE COEFFICIENT ***", n, flush=True)

    out = {
        "band": "W in [%d,%d]" % (wmin, wmax),
        "exhaustive": True,
        "enumeration": ("all (lam,mu,nu), each a partition with at most 4 parts, "
                        "|lam|+|mu|=|nu|=W; lam<->mu symmetry applied "
                        "(unordered pairs counted once)"),
        "triples_tested_unordered": total,
        "per_W": {str(k): perW[k] for k in sorted(perW)},
        "dim_histogram": {str(k): dimhist[k] for k in sorted(dimhist)},
        "audit_failures": len(audit_fail),
        "audit_failure_list": audit_fail[:50],
        "non_lattice_count": len(nonint),
        "non_lattice_list": nonint[:50],
        "min_a1": [str(best_a1[0]), best_a1[1], best_a1[2], best_a1[3]] if best_a1 else None,
        "min_coeff_any": [str(best_min[0]), best_min[1], best_min[2], best_min[3]] if best_min else None,
        "max_volume": [str(best_V[0]), best_V[1]],
        "max_volume_hstar1_zero": [str(best_V_h1z[0]), best_V_h1z[1]],
        "record_hstar2": [best_h2[0], best_h2[1]],
        "negatives": negs,
        "n_negatives": len(negs),
        "elapsed_s": round(time.time() - t0, 1),
        "engine": "hive4.py (exact, Fraction/int only)",
    }
    d = os.path.join(HERE, "runs", "band2")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "manifest.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "negatives"},
                     indent=1, default=str))
    print("NEGATIVES: %d" % len(negs))
    return 0


if __name__ == "__main__":
    wmin = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    wmax = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    wk = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    sys.exit(main(wmin, wmax, wk))
