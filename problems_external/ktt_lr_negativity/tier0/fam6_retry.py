#!/usr/bin/env python3
"""fam6_retry.py -- re-screen every UNRESOLVED family-6 triple.
An UNRESOLVED record is a SKIP (engine spawn contention), never a verdict;
it must be resolved before the family can be called exhaustive."""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "purged_region"))
from fam6_scan import _chunk_job    # noqa: E402


def main(argv):
    trips = [(tuple(a), tuple(b), tuple(c))
             for a, b, c in json.load(open(argv[1], encoding="utf-8"))]
    dst = argv[2]
    workers = int(argv[3]) if len(argv) > 3 else 6
    chunk = int(argv[4]) if len(argv) > 4 else 20
    byD = {}
    for t in trips:
        D = (len(t[2]) - 1) * (len(t[2]) - 2) // 2
        byD.setdefault(D, []).append(t)
    jobs = []
    for D, ts in byD.items():
        for s in range(0, len(ts), chunk):
            jobs.append((ts[s:s + chunk], D, 2 * 10 ** 9, 3000, True))
    ok = other = 0
    t0 = time.time()
    left = []
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
                        left.append([rec["lam"], rec["mu"], rec["nu"]])
                f.flush()
    print("retry: ok=%d still_unresolved=%d wall=%.0fs" % (ok, other,
                                                           time.time() - t0))
    json.dump(left, open(dst + ".left.json", "w"))


if __name__ == "__main__":
    main(sys.argv)
