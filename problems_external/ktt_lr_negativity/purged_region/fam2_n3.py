#!/usr/bin/env python3
"""
fam2_n3.py -- exact 3-dilate ladder probe for FAMILY F2.

Under the hypothesis h*_1 = 0 (equivalently c = d+1, the ladder condition),
Stanley's identity P(n) = sum_j h*_j C(n+d-j, d) with d = c-1 gives EXACTLY

    h*_2 = P(2) - C(d+2, 2)
    h*_3 = P(3) - C(d+3, 3) - h*_2 * (d+1)

so the three exact values P(1), P(2), P(3) already pin the first three
non-trivial h* entries and give the lower bound V = sum h* >= 1 + h*_2 + h*_3.
This is arithmetic only -- no LP, no dimension oracle, no simplex test.  It is
a RANKING device; every triple it flags is then put through the full mandated
instrument.
"""
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("LR_HIVE_NODE_CAP", "3000000000")
from lpfree_screen import engineA_batch, scale  # noqa: E402

CAP = 10 ** 18


def chunk_work(rows):
    jobs = [(scale(tuple(r["lam"]), 3), scale(tuple(r["mu"]), 3),
             scale(tuple(r["nu"]), 3)) for r in rows]
    vals = engineA_batch(jobs, cap=CAP)
    out = []
    for r, v in zip(rows, vals):
        if not isinstance(v, int):
            out.append(dict(r, P3=str(v), e2=None, e3=None))
            continue
        c = r["c"]
        d = c - 1
        e2 = r["P2"] - math.comb(d + 2, 2)
        e3 = v - math.comb(d + 3, 3) - e2 * (d + 1)
        out.append(dict(r, P3=v, e2=e2, e3=e3, Vlb=1 + e2 + e3))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--chunk", type=int, default=40)
    ap.add_argument("--budget", type=float, default=600.0)
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.todo)]
    rows.sort(key=lambda r: (len(r["nu"]), sum(r["nu"])))
    chunks = [rows[i:i + args.chunk] for i in range(0, len(rows), args.chunk)]
    t0 = time.time()
    n = 0
    best = (-10 ** 9, None)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(chunk_work, c) for c in chunks]
        with open(args.out, "w") as f:
            done = 0
            for fu in as_completed(futs):
                done += 1
                try:
                    res = fu.result()
                except Exception as e:                     # noqa: BLE001
                    print("chunk failed %r" % (e,), flush=True)
                    continue
                for r in res:
                    f.write(json.dumps(r) + "\n")
                    n += 1
                    if r.get("Vlb") is not None and r["Vlb"] > best[0]:
                        best = (r["Vlb"], r)
                        print("Vlb=%d c=%d %s %s %s e2=%d e3=%d"
                              % (r["Vlb"], r["c"], r["lam"], r["mu"], r["nu"],
                                 r["e2"], r["e3"]), flush=True)
                f.flush()
                if done % 100 == 0:
                    print("%d/%d %d recs %.0fs"
                          % (done, len(chunks), n, time.time() - t0),
                          flush=True)
                if time.time() - t0 > args.budget:
                    print("BUDGET STOP %d/%d" % (done, len(chunks)), flush=True)
                    for g in futs:
                        g.cancel()
                    break
    print("done %d %.0fs" % (n, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
