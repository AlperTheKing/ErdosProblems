#!/usr/bin/env python3
"""
census_band1.py -- EXHAUSTIVE r=4 hive-polytope census over the weight band
                   W = |nu| in [4,14]  (band1 of the Reeve-dimension sweep).

Every valid r<=4 triple (lam, mu, nu) -- all three partitions with at most 4
parts, |lam|+|mu|=|nu|=W -- is run through the mandated engine
hive4.analyze (which is NOT modified here; this file only drives it).

No sampling anywhere.  All arithmetic is exact (Python int / Fraction).

Tracked, as required by the run protocol:
  (i)   global minimum coefficient a_min over all P  (and min a_1 separately)
  (ii)  maximum normalized volume V
  (iii) maximum V among triples with h*_1 = 0  (i.e. c = dim+1)
  (iv)  EVERY triple with ANY negative coefficient  -> hits

Usage:  python census_band1.py [--wmin 4] [--wmax 14] [--procs N] [--out DIR]
"""

import argparse
import json
import os
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hive4  # noqa: E402

MAXPARTS = 4


def parts_atmost(n, k=MAXPARTS):
    """All partitions of n into at most k parts, as tuples (weakly decreasing)."""
    res = []

    def rec(rem, maxp, cur):
        if rem == 0:
            res.append(tuple(cur))
            return
        if len(cur) == k:
            return
        for x in range(min(rem, maxp), 0, -1):
            cur.append(x)
            rec(rem - x, x, cur)
            cur.pop()

    rec(n, n, [])
    return res


_PCACHE = {}


def P(n):
    if n not in _PCACHE:
        _PCACHE[n] = parts_atmost(n)
    return _PCACHE[n]


def _fmt(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def _key(t):
    return ";".join(",".join(map(str, p)) if p else "0" for p in t)


def work(task):
    """One shard: W, a = |lam|.  Returns an aggregate dict for the shard."""
    W, a = task
    agg = {
        "W": W, "a": a, "n": 0, "n_empty": 0, "n_nonempty": 0,
        "dimhist": {}, "chist_le": 0,
        "min_coeff": None, "min_coeff_at": None,
        "min_a1": None, "min_a1_at": None,
        "max_V": None, "max_V_at": None,
        "max_V_h1z": None, "max_V_h1z_at": None,
        "max_den": 1,
        "hits": [], "interp_fail": [], "volxcheck_fail": [], "degdim_fail": [],
        "hstar_neg": [],
        "n_h1zero": 0, "n_dim3": 0,
    }
    NUS = P(W)
    LAMS = P(a)
    MUS = P(W - a)
    for lam in LAMS:
        for mu in MUS:
            for nu in NUS:
                agg["n"] += 1
                r = hive4.analyze(list(lam), list(mu), list(nu))
                if r["c"] == 0:
                    agg["n_empty"] += 1
                    continue
                agg["n_nonempty"] += 1
                d = r["dim"]
                agg["dimhist"][d] = agg["dimhist"].get(d, 0) + 1
                if d == 3:
                    agg["n_dim3"] += 1
                trip = (lam, mu, nu)
                mc = Fraction(r["min_coeff"])
                if agg["min_coeff"] is None or mc < agg["min_coeff"]:
                    agg["min_coeff"] = mc
                    agg["min_coeff_at"] = trip
                poly = r["poly"]
                a1 = Fraction(poly[1]) if len(poly) > 1 else Fraction(0)
                if agg["min_a1"] is None or a1 < agg["min_a1"]:
                    agg["min_a1"] = a1
                    agg["min_a1_at"] = trip
                V = Fraction(r["volume_normalized"])
                if agg["max_V"] is None or V > agg["max_V"]:
                    agg["max_V"] = V
                    agg["max_V_at"] = trip
                hs = r["hstar"]
                h1 = hs[1] if len(hs) > 1 else 0
                if h1 == 0:
                    agg["n_h1zero"] += 1
                    if agg["max_V_h1z"] is None or V > agg["max_V_h1z"]:
                        agg["max_V_h1z"] = V
                        agg["max_V_h1z_at"] = trip
                if r.get("max_denominator", 1) > agg["max_den"]:
                    agg["max_den"] = r["max_denominator"]
                if r["neg"]:
                    agg["hits"].append({
                        "lam": list(lam), "mu": list(mu), "nu": list(nu),
                        "dim": d, "c": r["c"], "L": r["L"],
                        "poly": [_fmt(x) for x in poly],
                        "hstar": hs, "V": _fmt(V),
                        "min_coeff": _fmt(mc),
                        "neg_indices": r["neg_indices"],
                        "verified": r["verified"],
                    })
                if not r.get("verified", True):
                    agg["interp_fail"].append(_key(trip))
                if not r.get("vol_crosscheck", True):
                    agg["volxcheck_fail"].append(_key(trip))
                if not r.get("deg_eq_dim", True):
                    agg["degdim_fail"].append(_key(trip))
                if r.get("hstar_neg", False):
                    agg["hstar_neg"].append(_key(trip))
    # serialise Fractions
    for k in ("min_coeff", "min_a1", "max_V", "max_V_h1z"):
        if agg[k] is not None:
            agg[k] = _fmt(agg[k])
    for k in ("min_coeff_at", "min_a1_at", "max_V_at", "max_V_h1z_at"):
        if agg[k] is not None:
            agg[k] = _key(agg[k])
    agg["dimhist"] = {str(k): v for k, v in agg["dimhist"].items()}
    return agg


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--wmin", type=int, default=4)
    ap.add_argument("--wmax", type=int, default=14)
    ap.add_argument("--procs", type=int, default=max(1, (os.cpu_count() or 8) - 2))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "runs", "band1"))
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    tasks = [(W, a) for W in range(args.wmin, args.wmax + 1) for a in range(W + 1)]
    # biggest shards first
    tasks.sort(key=lambda t: -len(P(t[0])) * len(P(t[1])) * len(P(t[0] - t[1])))

    t0 = time.time()
    shards = []
    if args.procs <= 1:
        for i, t in enumerate(tasks):
            shards.append(work(t))
            print("shard %d/%d W=%d a=%d n=%d  %.1fs"
                  % (i + 1, len(tasks), t[0], t[1], shards[-1]["n"], time.time() - t0),
                  flush=True)
    else:
        with Pool(args.procs) as pool:
            for i, s in enumerate(pool.imap_unordered(work, tasks, chunksize=1)):
                shards.append(s)
                print("shard %d/%d W=%d a=%d n=%d  %.1fs"
                      % (i + 1, len(tasks), s["W"], s["a"], s["n"], time.time() - t0),
                      flush=True)
    tasks = [(s["W"], s["a"]) for s in shards]
    el = time.time() - t0

    tot = {
        "band": "|nu| in [%d,%d]" % (args.wmin, args.wmax),
        "exhaustive": True,
        "triplesTested": 0, "n_empty": 0, "n_nonempty": 0,
        "n_dim3": 0, "n_hstar1_zero": 0,
        "dimhist": {}, "max_denominator": 1,
        "min_coeff": None, "min_coeff_at": None,
        "min_a1": None, "min_a1_at": None,
        "max_V": None, "max_V_at": None,
        "max_V_hstar1_zero": None, "max_V_hstar1_zero_at": None,
        "hits": [], "interp_fail": [], "volxcheck_fail": [], "degdim_fail": [],
        "hstar_neg": [],
        "per_W": {},
    }
    perW = {}
    for s, t in zip(shards, tasks):
        W = s["W"]
        pw = perW.setdefault(W, {"n": 0, "n_nonempty": 0, "n_dim3": 0,
                                 "min_coeff": None, "min_a1": None,
                                 "max_V": None, "max_V_h1z": None,
                                 "hits": 0})
        pw["n"] += s["n"]
        pw["n_nonempty"] += s["n_nonempty"]
        pw["n_dim3"] += s["n_dim3"]
        pw["hits"] += len(s["hits"])
        tot["triplesTested"] += s["n"]
        tot["n_empty"] += s["n_empty"]
        tot["n_nonempty"] += s["n_nonempty"]
        tot["n_dim3"] += s["n_dim3"]
        tot["n_hstar1_zero"] += s["n_h1zero"]
        tot["max_denominator"] = max(tot["max_denominator"], s["max_den"])
        for k, v in s["dimhist"].items():
            tot["dimhist"][k] = tot["dimhist"].get(k, 0) + v
        tot["hits"].extend(s["hits"])
        tot["interp_fail"].extend(s["interp_fail"])
        tot["volxcheck_fail"].extend(s["volxcheck_fail"])
        tot["degdim_fail"].extend(s["degdim_fail"])
        tot["hstar_neg"].extend(s["hstar_neg"])
        for src, dst, better in (("min_coeff", "min_coeff", "lt"),
                                 ("min_a1", "min_a1", "lt"),
                                 ("max_V", "max_V", "gt"),
                                 ("max_V_h1z", "max_V_hstar1_zero", "gt")):
            v = s[src]
            if v is None:
                continue
            v = Fraction(v)
            cur = tot[dst]
            cur = None if cur is None else Fraction(cur)
            if cur is None or (v < cur if better == "lt" else v > cur):
                tot[dst] = _fmt(v)
                tot[dst + "_at"] = s[src + "_at"]
            cw = pw[src]
            cw = None if cw is None else Fraction(cw)
            if cw is None or (v < cw if better == "lt" else v > cw):
                pw[src] = _fmt(v)
    tot["per_W"] = {str(k): perW[k] for k in sorted(perW)}
    tot["elapsed_sec"] = round(el, 2)
    tot["engine"] = "hive4.py analyze() (unmodified)"
    with open(os.path.join(args.out, "census_band1.json"), "w") as f:
        json.dump(tot, f, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in tot.items() if k != "per_W"}, indent=1, sort_keys=True))
    print("per_W:", json.dumps(tot["per_W"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
