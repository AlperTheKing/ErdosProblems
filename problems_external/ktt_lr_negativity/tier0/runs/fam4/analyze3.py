#!/usr/bin/env python3
"""Frontier report: among records that DO have an interior lattice point
(h*_d >= 1), how small can h*_1 get?  That is the true distance to JACKPOT."""
import glob, json, os, sys

dirs = sys.argv[1:] or ["out_r5", "out_r6", "out_r7"]
base = os.path.dirname(os.path.abspath(__file__))


def brief(r):
    return {"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "r": r["r"],
            "c": r.get("c"), "d": r.get("d"), "hstar": r.get("hstar"),
            "hstar_1": r.get("hstar_1"), "hstar_d": r.get("hstar_d"),
            "hstar_sum": r.get("hstar_sum")}


front = {}      # d -> best (h*_1, rec) among h*_d>=1
volmax = {}     # d -> max hstar_sum
hd_by_d = {}    # d -> max hstar_d
n_int = {}      # d -> count with h*_d>=1
for dd in dirs:
    for fn in sorted(glob.glob(os.path.join(base, dd, "*.jsonl"))):
        for line in open(fn):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("status") != "OK":
                continue
            d = r["d"]
            hs = r.get("hstar_sum")
            volmax[d] = max(volmax.get(d, 0), hs or 0)
            hd = r.get("hstar_d")
            hd_by_d[d] = max(hd_by_d.get(d, 0), hd or 0)
            h1 = r.get("hstar_1")
            if hd and hd >= 1 and h1 is not None:
                n_int[d] = n_int.get(d, 0) + 1
                cur = front.get(d)
                if cur is None or h1 < cur[0]:
                    front[d] = (h1, brief(r))

print(json.dumps({
    "max_hstar_sum_by_d": {str(k): volmax[k] for k in sorted(volmax)},
    "max_hstar_d_by_d": {str(k): hd_by_d[k] for k in sorted(hd_by_d)},
    "count_with_interior_by_d": {str(k): n_int[k] for k in sorted(n_int)},
    "min_hstar1_given_interior": {str(k): {"hstar_1": front[k][0],
                                           "triple": front[k][1]}
                                  for k in sorted(front)},
}, indent=1))
