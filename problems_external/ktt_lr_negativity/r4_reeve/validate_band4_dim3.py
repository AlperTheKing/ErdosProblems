#!/usr/bin/env python3
"""
validate_band4_dim3.py -- cross-engine gate restricted to the DIM-3 stratum of
the weight band (the only stratum in which an Ehrhart coefficient can be
negative).  For N random dim-3 triples of weight W:
    band4.exe --one   vs   hive4.analyze   vs   engine A   vs   engine B
at stretch factors n = 1, 2, 3, plus hive4's own held-out check at n = 4,5.
Any mismatch is a hard failure.
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402
from validate_band4 import parts_le, band4_one, engineA, engineB, _ps  # noqa: E402


def main(W, N, seed):
    random.seed(seed)
    PT = {a: parts_le(a) for a in range(W + 1)}
    fail = 0
    done = 0
    tried = 0
    while done < N and tried < 200000:
        tried += 1
        nu = random.choice(PT[W])
        a = random.randrange(W + 1)
        lam = random.choice(PT[a])
        mu = random.choice(PT[W - a])
        b4 = band4_one(lam, mu, nu)
        kv = dict(t.split("=", 1) for t in b4.split()) if "L=" in b4 else {}
        if kv.get("dim") != "3":
            continue
        done += 1
        r = hive4.analyze(list(lam), list(mu), list(nu))
        L = [int(x) for x in kv["L"].split(",")]
        checks = {"band4_vs_hive4_L": L[:5] == r["L"][1:6],
                  "hive4_dim3": r["dim"] == 3,
                  "hive4_heldout_45": r["verified"],
                  "hive4_vol_crossroute": r["vol_crosscheck"],
                  "deg_eq_dim": r["deg_eq_dim"]}
        for n in (1, 2, 3):
            ln = [n * x for x in lam]
            mn = [n * x for x in mu]
            nn = [n * x for x in nu]
            checks["A_n%d" % n] = (engineA(ln, mn, nn) == str(r["L"][n]))
            if n <= 2:   # engine B (pure-python LR rule) is only affordable to n=2 here
                checks["B_n%d" % n] = (engineB(ln, mn, nn) == str(r["L"][n]))
        bad = [k for k, v in checks.items() if not v]
        if bad:
            fail += 1
            print("MISMATCH", lam, mu, nu, bad, "hive4 L=", r["L"], "band4=", b4)
        else:
            print("ok %-14s %-14s %-16s L(1..3)=%s V=%s poly=%s"
                  % (_ps(lam), _ps(mu), _ps(nu), r["L"][1:4],
                     r["volume_normalized"], [str(c) for c in r["poly"]]), flush=True)
    print("dim3 sample W=%d: %d dim-3 triples fully cross-checked (A+B, n=1,2,3), %d failures"
          % (W, done, fail))
    return fail


if __name__ == "__main__":
    sys.exit(1 if main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])) else 0)
