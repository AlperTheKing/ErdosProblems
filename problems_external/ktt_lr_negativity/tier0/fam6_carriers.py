#!/usr/bin/env python3
"""fam6_carriers.py -- extract the only NON-TRIVIAL members of family 6:
records with h*_1 = 0 (c = d+1) and Sum h* >= 2.  Everything else in the
family is a unimodular simplex (Sum h* = 1), for which h*_d = 0 identically.

Emits a json list of {lam,mu,nu,d,hstar,topj} where topj = max{j : h*_j > 0}.
TIER0 needs topj = d.
"""
import glob
import json
import sys


def main(pats, dst):
    files = []
    for p in pats:
        files.extend(glob.glob(p))
    out = []
    seen = set()
    for fn in files:
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("status") != "OK":
                continue
            d = rec["d"]
            if d is None or d < 2:
                continue
            h = rec["hstar"]
            if h[1] != 0:
                continue
            if sum(h) < 2:
                continue
            key = (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))
            if key in seen:
                continue
            seen.add(key)
            topj = max(j for j in range(d + 1) if h[j] > 0)
            out.append({"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"],
                        "r": len(rec["nu"]), "D": rec.get("D"), "d": d,
                        "c": rec["c"], "hstar": h, "hstar_sum": sum(h),
                        "topj": topj, "gap_to_tier0": d - topj})
    out.sort(key=lambda z: (z["gap_to_tier0"], -z["hstar_sum"]))
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("carriers %d -> %s" % (len(out), dst))
    if out:
        print("best gap_to_tier0 = %d" % out[0]["gap_to_tier0"])
        for z in out[:5]:
            print(" ", z["lam"], z["mu"], z["nu"], "d=%d" % z["d"],
                  z["hstar"], "gap=%d" % z["gap_to_tier0"])


if __name__ == "__main__":
    main(sys.argv[1:-1], sys.argv[-1])
