#!/usr/bin/env python3
"""fam10_tier0.py -- run the MANDATED tier-0 screen (exact profile -> exact
Newton interpolation -> two held-out points -> exact h*) on a list of triples,
in parallel chunks.  The screen itself is untouched; this is only a driver.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
TIER0 = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TIER0)
from tier0_screen import screen_triples          # noqa: E402


def _job(arg):
    idx, chunk, cap = arg
    try:
        recs = screen_triples([(tuple(l), tuple(m), tuple(v)) for l, m, v in chunk],
                              cap=cap)
    except Exception as ex:                       # noqa: BLE001
        recs = [{"status": "DRIVER_EXC", "err": repr(ex)[:200],
                 "lam": l, "mu": m, "nu": v, "neg": False, "NEG": False,
                 "JACKPOT": False, "TIER0": False} for l, m, v in chunk]
    return idx, recs


def main(argv):
    src, dst = argv[1], argv[2]
    csize = int(argv[3]) if len(argv) > 3 else 8
    workers = int(argv[4]) if len(argv) > 4 else 56
    cap = int(argv[5]) if len(argv) > 5 else 10 ** 15
    trips = []
    for line in open(src, encoding="utf-8"):
        r = json.loads(line)
        trips.append((r["lam"], r["mu"], r["nu"]))
    chunks = [(i, trips[s:s + csize], cap)
              for i, s in enumerate(range(0, len(trips), csize))]
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_job, c) for c in chunks]
            for fut in as_completed(futs):
                _, recs = fut.result()
                for r in recs:
                    f.write(json.dumps(r) + "\n")
                n += len(recs)
                if n % 200 < csize:
                    f.flush()
                    print("%d/%d" % (n, len(trips)), flush=True)
    print("wrote %d" % n, flush=True)


if __name__ == "__main__":
    main(sys.argv)
