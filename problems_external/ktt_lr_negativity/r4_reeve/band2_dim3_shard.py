#!/usr/bin/env python3
"""
band2_dim3_shard.py -- second exhaustive pass over the band W=|nu| in [15,20]
that DUMPS every dim-3 triple (the only stratum in which an Ehrhart negativity
can occur, since deg P = dim Q and d <= 2 forces positive coefficients).

usage: python band2_dim3_shard.py SHARD NSHARDS [WMIN WMAX]
Writes runs/band2/dim3_SHARD.jsonl : one JSON record per dim-3 triple.
"""

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4                # noqa: E402
from band2_census import P4  # noqa: E402


def main(shard, nshards, wmin=15, wmax=20):
    t0 = time.time()
    tasks = [(W, a) for W in range(wmin, wmax + 1) for a in range(0, W + 1)]
    mine = [t for i, t in enumerate(tasks) if i % nshards == shard]
    d = os.path.join(HERE, "runs", "band2")
    os.makedirs(d, exist_ok=True)
    n = 0
    tot = 0
    with open(os.path.join(d, "dim3_%02d.jsonl" % shard), "w") as f:
        for (W, a) in mine:
            for lam in P4(a):
                for mu in P4(W - a):
                    if (len(mu), mu) < (len(lam), lam):
                        continue
                    for nu in P4(W):
                        tot += 1
                        r = hive4.analyze(list(lam), list(mu), list(nu))
                        if r["dim"] != 3:
                            continue
                        n += 1
                        f.write(json.dumps({
                            "W": W, "lam": list(lam), "mu": list(mu), "nu": list(nu),
                            "c": r["c"], "V": str(r["volume_normalized"]),
                            "hstar": list(r["hstar"]),
                            "poly": [hive4._fmt_frac(c) for c in r["poly"]],
                            "a1": hive4._fmt_frac(r["poly"][1]),
                            "min_coeff": hive4._fmt_frac(r["min_coeff"]),
                            "neg": r["neg"], "L": list(r["L"]),
                            "verified": r["verified"],
                            "vol_ok": r["vol_crosscheck"],
                            "deg_ok": r["deg_eq_dim"],
                            "hstar_neg": r["hstar_neg"],
                            "max_den": r["max_denominator"]}) + "\n")
            f.flush()
    print("shard %d: %d triples, %d dim-3, %.1fs" % (shard, tot, n, time.time() - t0))
    with open(os.path.join(d, "dim3_%02d.done" % shard), "w") as g:
        g.write("%d %d %.1f\n" % (tot, n, time.time() - t0))
    return 0


if __name__ == "__main__":
    s = int(sys.argv[1]); k = int(sys.argv[2])
    wmin = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    wmax = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    sys.exit(main(s, k, wmin, wmax))
