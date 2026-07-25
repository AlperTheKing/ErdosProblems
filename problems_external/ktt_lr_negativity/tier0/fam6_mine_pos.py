#!/usr/bin/env python3
"""fam6_mine_pos.py -- among records with h*_1 = 0 (c = d+1, the minimal
lattice-point family), where does the extra h*-mass sit?

TIER0 needs h*_d > 0.  With Sum h* = 2 the whole question is the POSITION j
of the single extra unit: j = d is TIER0/JACKPOT, j < d is a near miss.
Also reports min(h*_1 - h*_d) and max h*_d over everything seen.
"""
import glob
import json
import sys
from collections import Counter


def main(pats):
    files = []
    for p in pats:
        files.extend(glob.glob(p))
    tot = ok = 0
    h1zero = 0
    pos = Counter()          # (d, j) for Sum h* = 2, h*_1 = 0
    sumh = Counter()         # (d, Sum h*) for h*_1 = 0
    best_hd = (-1, None)
    best_margin = (10 ** 9, None)
    gap_hist = Counter()
    near = []
    for fn in files:
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            tot += 1
            if rec.get("status") != "OK":
                continue
            ok += 1
            d = rec["d"]
            if d is None or d < 1:
                continue
            h = rec["hstar"]
            h1, hd = h[1], h[d]
            if hd > best_hd[0]:
                best_hd = (hd, (rec["lam"], rec["mu"], rec["nu"], d, h))
            if h1 - hd < best_margin[0]:
                best_margin = (h1 - hd, (rec["lam"], rec["mu"], rec["nu"], d, h))
            gap_hist[h1 - hd] += 1
            if h1 != 0:
                continue
            h1zero += 1
            S = sum(h)
            sumh[(d, S)] += 1
            if S == 2:
                j = [i for i in range(2, d + 1) if h[i] == 1]
                if len(j) == 1:
                    pos[(d, j[0])] += 1
                    if j[0] >= d - 1 and len(near) < 40:
                        near.append((rec["lam"], rec["mu"], rec["nu"], d, h))
    print(json.dumps({
        "files": len(files), "records": tot, "ok": ok,
        "h1_zero": h1zero,
        "h1_zero_(d,Sum h*)": {"%d,%d" % k: v for k, v in sorted(sumh.items())},
        "Sumh2_extra_unit_position_(d,j)":
            {"%d,%d" % k: v for k, v in sorted(pos.items())},
        "max_hstar_d": best_hd[0], "max_hstar_d_at": best_hd[1],
        "min_h1_minus_hd": best_margin[0],
        "min_h1_minus_hd_at": best_margin[1],
        "h1_minus_hd_hist_low": {str(k): gap_hist[k]
                                 for k in sorted(gap_hist)[:8]},
        "near_j_ge_d_minus_1": near[:10],
    }, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
