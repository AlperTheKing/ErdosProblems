#!/usr/bin/env python3
"""
band2_shard.py -- one independent shard of the exhaustive band-2 census
(W = |nu| in [15,20]).  No multiprocessing: each shard is its own OS process
writing its own JSON, so nothing can deadlock and partial results survive.

usage:  python band2_shard.py SHARD NSHARDS [WMIN WMAX]
"""

import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4                    # noqa: E402
from band2_census import P4, job  # noqa: E402


def main(shard, nshards, wmin=15, wmax=20):
    t0 = time.time()
    tasks = [(W, a) for W in range(wmin, wmax + 1) for a in range(0, W + 1)]
    mine = [t for i, t in enumerate(tasks) if i % nshards == shard]
    d = os.path.join(HERE, "runs", "band2")
    os.makedirs(d, exist_ok=True)
    logp = os.path.join(d, "shard_%02d.log" % shard)
    agg = {"total": 0, "dimhist": {}, "negs": [], "audit_fail": [], "nonint": [],
           "best_a1": None, "best_min": None,
           "best_V": (Fraction(0), None), "best_V_h1z": (Fraction(0), None),
           "best_h2": (0, None), "perW": {}}
    with open(logp, "w") as lg:
        for (W, a) in mine:
            r = job((W, a))
            agg["total"] += r["total"]
            agg["perW"][W] = agg["perW"].get(W, 0) + r["total"]
            for k, v in r["dimhist"].items():
                agg["dimhist"][k] = agg["dimhist"].get(k, 0) + v
            agg["negs"].extend(r["negs"])
            agg["audit_fail"].extend(r["audit_fail"])
            agg["nonint"].extend(r["nonint"])
            if r["best_a1"]:
                f = Fraction(r["best_a1"][0])
                if agg["best_a1"] is None or f < agg["best_a1"][0]:
                    agg["best_a1"] = (f,) + tuple(r["best_a1"][1:])
            if r["best_min"]:
                f = Fraction(r["best_min"][0])
                if agg["best_min"] is None or f < agg["best_min"][0]:
                    agg["best_min"] = (f,) + tuple(r["best_min"][1:])
            fV = Fraction(r["best_V"][0])
            if fV > agg["best_V"][0]:
                agg["best_V"] = (fV, r["best_V"][1])
            fz = Fraction(r["best_V_h1z"][0])
            if fz > agg["best_V_h1z"][0]:
                agg["best_V_h1z"] = (fz, r["best_V_h1z"][1])
            if r["best_h2"][0] > agg["best_h2"][0]:
                agg["best_h2"] = tuple(r["best_h2"])
            lg.write("W=%d a=%d triples=%d cum=%d negs=%d %.1fs\n"
                     % (W, a, r["total"], agg["total"], len(agg["negs"]),
                        time.time() - t0))
            lg.flush()
    out = {"shard": shard, "nshards": nshards, "wmin": wmin, "wmax": wmax,
           "cells": len(mine), "total": agg["total"],
           "perW": {str(k): v for k, v in sorted(agg["perW"].items())},
           "dimhist": {str(k): v for k, v in sorted(agg["dimhist"].items())},
           "negs": agg["negs"], "audit_fail": agg["audit_fail"],
           "nonint": agg["nonint"],
           "best_a1": [str(agg["best_a1"][0])] + list(agg["best_a1"][1:]) if agg["best_a1"] else None,
           "best_min": [str(agg["best_min"][0])] + list(agg["best_min"][1:]) if agg["best_min"] else None,
           "best_V": [str(agg["best_V"][0]), agg["best_V"][1]],
           "best_V_h1z": [str(agg["best_V_h1z"][0]), agg["best_V_h1z"][1]],
           "best_h2": list(agg["best_h2"]),
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(d, "shard_%02d.json" % shard), "w") as f:
        json.dump(out, f, default=str)
    print("shard %d done: %d triples, %d negatives, %.1fs"
          % (shard, agg["total"], len(agg["negs"]), time.time() - t0))
    return 0


if __name__ == "__main__":
    s = int(sys.argv[1]); n = int(sys.argv[2])
    wmin = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    wmax = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    sys.exit(main(s, n, wmin, wmax))
