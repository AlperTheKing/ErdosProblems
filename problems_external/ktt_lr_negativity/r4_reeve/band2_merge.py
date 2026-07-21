#!/usr/bin/env python3
"""band2_merge.py -- merge the 24 shard JSONs into runs/band2/manifest.json."""

import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "runs", "band2")


def main():
    files = sorted(glob.glob(os.path.join(D, "shard_*.json")))
    total = 0
    perW = {}
    dimhist = {}
    negs, audit, nonint = [], [], []
    best_a1 = best_min = None
    best_V = (Fraction(0), None)
    best_Vz = (Fraction(0), None)
    best_h2 = (0, None)
    cells = 0
    for fp in files:
        with open(fp) as f:
            s = json.load(f)
        total += s["total"]
        cells += s["cells"]
        for k, v in s["perW"].items():
            perW[k] = perW.get(k, 0) + v
        for k, v in s["dimhist"].items():
            dimhist[k] = dimhist.get(k, 0) + v
        negs.extend(s["negs"])
        audit.extend(s["audit_fail"])
        nonint.extend(s["nonint"])
        if s["best_a1"]:
            f1 = Fraction(s["best_a1"][0])
            if best_a1 is None or f1 < best_a1[0]:
                best_a1 = (f1,) + tuple(s["best_a1"][1:])
        if s["best_min"]:
            f1 = Fraction(s["best_min"][0])
            if best_min is None or f1 < best_min[0]:
                best_min = (f1,) + tuple(s["best_min"][1:])
        fV = Fraction(s["best_V"][0])
        if fV > best_V[0]:
            best_V = (fV, s["best_V"][1])
        fz = Fraction(s["best_V_h1z"][0])
        if fz > best_Vz[0]:
            best_Vz = (fz, s["best_V_h1z"][1])
        if s["best_h2"][0] > best_h2[0]:
            best_h2 = tuple(s["best_h2"])
    out = {
        "band": "W = |nu| in [15,20]",
        "exhaustive": True,
        "shards_merged": len(files),
        "cells": cells,
        "enumeration": ("EVERY triple (lam,mu,nu) of partitions with at most 4 parts "
                        "and |lam|+|mu|=|nu|=W, for W=15..20. Partitions with >4 parts "
                        "cannot occur in the r=4 cell (c(nu;lam,mu)=0 unless "
                        "l(lam),l(mu) <= l(nu) <= 4). The lam<->mu symmetry "
                        "c(nu;lam,mu)=c(nu;mu,lam) is applied, so each unordered pair "
                        "{lam,mu} is analysed once."),
        "triples_tested_unordered": total,
        "per_W": {k: perW[k] for k in sorted(perW, key=int)},
        "dim_histogram": {k: dimhist[k] for k in sorted(dimhist, key=int)},
        "audit_failures": len(audit),
        "audit_failure_list": audit[:50],
        "non_lattice_count": len(nonint),
        "non_lattice_list": nonint[:50],
        "min_a1": [str(best_a1[0])] + list(best_a1[1:]) if best_a1 else None,
        "min_coeff_any": [str(best_min[0])] + list(best_min[1:]) if best_min else None,
        "max_volume": [str(best_V[0]), best_V[1]],
        "max_volume_hstar1_zero": [str(best_Vz[0]), best_Vz[1]],
        "record_hstar2": list(best_h2),
        "n_negatives": len(negs),
        "negatives": negs,
        "engine": "hive4.py (exact: Python int / fractions.Fraction only, no float)",
        "caveat": ("An empty negative census closes this window only. It proves "
                   "nothing about the KTT conjecture and is NOT evidence for it."),
    }
    with open(os.path.join(D, "manifest.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("negatives", "audit_failure_list", "non_lattice_list")},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
