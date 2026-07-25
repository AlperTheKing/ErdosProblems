#!/usr/bin/env python3
"""fam10_stair_screen.py -- run the mandated tier-0 screen on the MOST fractional
triples found by the staircase probe.

At r=7 the ambient degree bound D = (r-1)(r-2)/2 = 15 makes the mandated
P(0..D+2) profile unaffordable, so a REDUCED bound  dbound = dim_hi + slack  is
supplied via screen_triples(dbound=...).  This is SAFE, not a shortcut: the
screen still interpolates through n = 0..dbound and then verifies the two
held-out points n = dbound+1, dbound+2.  If dbound < deg P the held-out check
fails and the record is reported HELDOUT_MISMATCH (a SKIP, never a verdict).
Only records with status OK are used, and every OK record therefore carries an
interpolation that reproduces two points it was not fitted to.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
TIER0 = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TIER0)
sys.path.insert(0, HERE)
from tier0_screen import screen_triples          # noqa: E402


def _job(a):
    lam, mu, nu, dbound, cap = a
    try:
        rec = screen_triples([(tuple(lam), tuple(mu), tuple(nu))],
                             cap=cap, dbound=dbound)[0]
    except Exception as ex:                       # noqa: BLE001
        rec = {"status": "DRIVER_EXC", "err": repr(ex)[:200], "lam": lam,
               "mu": mu, "nu": nu, "neg": False, "NEG": False,
               "JACKPOT": False, "TIER0": False}
    rec["dbound_used"] = dbound
    return rec


def main(argv):
    src, dst = argv[1], argv[2]
    slack = int(argv[3]) if len(argv) > 3 else 2
    workers = int(argv[4]) if len(argv) > 4 else 40
    cap = int(argv[5]) if len(argv) > 5 else 10 ** 15
    jobs = []
    for line in open(src, encoding="utf-8"):
        r = json.loads(line)
        if r.get("vstatus") != "OK":
            continue
        db = min(r["D"], max(r["dim_hi"], r["dim_lo"]) + slack)
        jobs.append((r["lam"], r["mu"], r["nu"], db, cap))
    print("jobs %d" % len(jobs), flush=True)
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_job, j) for j in jobs]
            for fut in as_completed(futs):
                f.write(json.dumps(fut.result()) + "\n")
                n += 1
                if n % 25 == 0:
                    f.flush()
                    print("%d/%d" % (n, len(jobs)), flush=True)
    print("wrote %d" % n, flush=True)


if __name__ == "__main__":
    main(sys.argv)
