#!/usr/bin/env python3
"""fam6_control.py -- UNFILTERED control arm for family 6.

The family-6 pre-filter (1 <= c <= D+1) decides TIER0 only; a triple with
c > D+1 has h*_1 > 0 but may still have h*_d > h*_1 (JACKPOT).  This arm
therefore runs the FULL mandated screen on a random sample with NO c filter
at all, purely to measure min(h*_1 - h*_d) and max h*_d on the general
population.  Sampled, not exhaustive.
"""
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PURGED = os.path.join(ROOT, "purged_region")
sys.path.insert(0, HERE)
sys.path.insert(0, PURGED)
from fam6_scan import _chunk_job                  # noqa: E402
from ladder_scan import gen                       # noqa: E402


def main(argv):
    r = int(argv[1]); Nlo = int(argv[2]); Nhi = int(argv[3])
    nsample = int(argv[4]); dst = argv[5]
    workers = int(argv[6]) if len(argv) > 6 else 16
    chunk = int(argv[7]) if len(argv) > 7 else 60
    seed = int(argv[8]) if len(argv) > 8 else 20260722
    D = (r - 1) * (r - 2) // 2
    rng = random.Random(seed)
    allt = []
    for N in range(Nlo, Nhi + 1):
        allt.extend(gen(r, N))
    print("pool %d (r=%d N=%d..%d D=%d)" % (len(allt), r, Nlo, Nhi, D),
          flush=True)
    if len(allt) > nsample:
        allt = rng.sample(allt, nsample)
    t0 = time.time()
    jobs = [(allt[s:s + chunk], D, 2 * 10 ** 9, 3000, True)
            for s in range(0, len(allt), chunk)]
    n = ok = other = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_chunk_job, j) for j in jobs]
            for fut in as_completed(futs):
                for rec in fut.result():
                    f.write(json.dumps(rec) + "\n")
                    if rec.get("status") == "OK":
                        ok += 1
                    else:
                        other += 1
                f.flush()
                n += 1
                if n % 20 == 0 or n == len(jobs):
                    print("  chunk %d/%d ok=%d other=%d %.0fs"
                          % (n, len(jobs), ok, other, time.time() - t0),
                          flush=True)
    print("DONE control r=%d sample=%d ok=%d other=%d wall=%.0fs"
          % (r, len(allt), ok, other, time.time() - t0), flush=True)


if __name__ == "__main__":
    main(sys.argv)
