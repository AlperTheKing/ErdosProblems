#!/usr/bin/env python3
"""
collect_dim3_band1.py -- collect EVERY dim-3 (full-dimensional) hive polytope in
the band |nu| in [wmin,wmax], r <= 4.

Rationale: an Ehrhart polynomial of a polytope of dimension <= 2 has strictly
positive coefficients (Ehrhart / Scott), so a KTT counterexample in the r = 4
cell can ONLY come from a dim-3 hive polytope.  The dim-3 stratum is therefore
the exact set that must be independently re-verified against the two LR engines.

Output: JSON list of records {lam,mu,nu,L,poly,V,hstar,min_coeff,neg}.
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
from census_band1 import P, _fmt  # noqa: E402


def work(task):
    W, a = task
    out = []
    for lam in P(a):
        for mu in P(W - a):
            for nu in P(W):
                r = hive4.analyze(list(lam), list(mu), list(nu))
                if r["dim"] != 3:
                    continue
                out.append({
                    "lam": list(lam), "mu": list(mu), "nu": list(nu),
                    "W": W, "L": r["L"], "c": r["c"],
                    "poly": [_fmt(x) for x in r["poly"]],
                    "V": _fmt(r["volume_normalized"]),
                    "hstar": r["hstar"],
                    "min_coeff": _fmt(r["min_coeff"]),
                    "neg": r["neg"],
                    "verified": r["verified"],
                    "vol_crosscheck": r.get("vol_crosscheck"),
                    "max_denominator": r.get("max_denominator"),
                    "n_vertices": r.get("n_vertices"),
                })
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--wmin", type=int, default=4)
    ap.add_argument("--wmax", type=int, default=14)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "runs", "band1", "dim3_band1.json"))
    args = ap.parse_args(argv)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tasks = [(W, a) for W in range(args.wmin, args.wmax + 1) for a in range(W + 1)]
    tasks.sort(key=lambda t: -len(P(t[0])) * len(P(t[1])) * len(P(t[0] - t[1])))
    t0 = time.time()
    recs = []
    with Pool(args.procs) as pool:
        for i, s in enumerate(pool.imap_unordered(work, tasks, chunksize=1)):
            recs.extend(s)
            print("shard %d/%d  dim3 so far %d  %.1fs" % (i + 1, len(tasks), len(recs), time.time() - t0),
                  flush=True)
    recs.sort(key=lambda r: (r["W"], r["lam"], r["mu"], r["nu"]))
    with open(args.out, "w") as f:
        json.dump(recs, f, indent=1)
    print("dim3 triples:", len(recs), "->", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
